#!/usr/bin/env node

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { readFileSync } from "fs";
import { homedir } from "os";

const MAX_RESULTS = 5;
const FETCH_TIMEOUT_MS = 10_000;
const MAX_CALLS_PER_MINUTE = 5;
const MAX_RESPONSE_BYTES = 20 * 1024 * 1024; // 20 MB cap
const SG_API_URL = "https://sourcegraph.com/.api/search/stream";

// --- Token Resolution ---
// Priority: 1) env var  2) ~/.config/switchboard/secrets.env file
function resolveToken() {
  const envToken = (process.env.SOURCEGRAPH_TOKEN || "").trim();
  // Switchboard may pass literal "${SOURCEGRAPH_TOKEN}" — reject that
  if (envToken && !envToken.startsWith("$") && envToken.startsWith("sgp_")) {
    return envToken;
  }
  try {
    const secrets = readFileSync(`${homedir()}/.config/switchboard/secrets.env`, "utf-8");
    const match = secrets.match(/SOURCEGRAPH_TOKEN=(sgp_[^\s]+)/);
    if (match) return match[1].trim();
  } catch (_) { /* file not found — acceptable */ }
  return "";
}
const SG_TOKEN = resolveToken();

// --- Client-side Rate Limiter ---
const callTimestamps = [];
function checkRateLimit() {
  const now = Date.now();
  while (callTimestamps.length > 0 && callTimestamps[0] < now - 60_000) {
    callTimestamps.shift();
  }
  if (callTimestamps.length >= MAX_CALLS_PER_MINUTE) {
    const waitSec = Math.ceil((callTimestamps[0] + 60_000 - now) / 1000);
    throw new Error(`Client-side rate limit: max ${MAX_CALLS_PER_MINUTE} calls/min. Retry in ${waitSec}s.`);
  }
  callTimestamps.push(now);
}

// --- Sourcegraph Stream Search ---
async function searchSourcegraph(query) {
  const url = `${SG_API_URL}?q=${encodeURIComponent(query + ` count:${MAX_RESULTS}`)}&display=${MAX_RESULTS}`;

  const headers = {
    "Accept": "text/event-stream",
    "User-Agent": "switchboard-sourcegraph-bridge/1.0",
  };
  if (SG_TOKEN) {
    headers["Authorization"] = `token ${SG_TOKEN}`;
  }

  // Fetch with AbortController timeout to prevent zombie processes
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);
  let response;
  try {
    response = await fetch(url, { headers, signal: controller.signal });
  } catch (err) {
    clearTimeout(timeout);
    if (err.name === "AbortError") {
      throw new Error(`Sourcegraph API request timed out after ${FETCH_TIMEOUT_MS / 1000}s`);
    }
    throw err;
  }
  clearTimeout(timeout);

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`Sourcegraph API error ${response.status}: ${body.slice(0, 200)}`);
  }

  // Bounded stream reader (cap at 20MB)
  const decoder = new TextDecoder("utf-8");
  let text = "";
  let byteCount = 0;
  for await (const chunk of response.body) {
    byteCount += chunk.byteLength;
    if (byteCount > MAX_RESPONSE_BYTES) {
      console.warn(`[sourcegraph-mcp] Response exceeded 20MB limit. Truncating.`);
      text += decoder.decode(chunk, { stream: false });
      break;
    }
    text += decoder.decode(chunk, { stream: true });
  }
  text += decoder.decode(); // Flush decoder

  const results = [];

  // Parse SSE events
  const events = text.split("\nevent: ");
  for (const event of events) {
    if (event.startsWith("matches") || event.includes('"type":"content"')) {
      const dataLine = event.split("\ndata: ").slice(1).join("\ndata: ");
      if (!dataLine) continue;
      try {
        const parsed = JSON.parse(dataLine);
        if (Array.isArray(parsed)) {
          for (const match of parsed) {
            if (results.length >= MAX_RESULTS) break;
            results.push({
              repo: match.repository || "unknown",
              file: match.path || match.name || "unknown",
              lineMatches: (match.lineMatches || match.chunkMatches || [])
                .slice(0, 3)
                .map(lm => ({
                  line: lm.lineNumber ?? lm.contentStart?.line ?? 0,
                  preview: (lm.preview || lm.content || "").slice(0, 200),
                })),
            });
          }
        }
      } catch (e) {
        console.error(`[sourcegraph-mcp] SSE parse error: ${e.message}. Data: ${dataLine.slice(0, 100)}`);
      }
    }
  }

  return results;
}

// --- MCP Server Setup ---
const server = new McpServer({
  name: "sourcegraph-mcp",
  version: "1.0.0",
});

server.tool(
  "search_code",
  "Search code across millions of open-source repositories on Sourcegraph. Use specific queries with repo filters for best results. Returns max 5 results.",
  {
    query: z.string().max(2000).describe(
      "Sourcegraph search query. MUST be specific. Good: 'useEffect cleanup WebSocket repo:vercel/next.js'. Bad: 'useEffect'."
    ),
  },
  async ({ query }) => {
    try {
      checkRateLimit();
      const results = await searchSourcegraph(query);
      if (results.length === 0) {
        return {
          content: [{ type: "text", text: "No results found. Try a more specific query or different repo filter." }],
        };
      }
      const formatted = results
        .map(
          (r, i) =>
            `[${i + 1}] ${r.repo} — ${r.file}\n${r.lineMatches.map((lm) => `  L${lm.line}: ${lm.preview}`).join("\n")}`
        )
        .join("\n\n");
      return {
        content: [{ type: "text", text: `Found ${results.length} result(s):\n\n${formatted}` }],
      };
    } catch (error) {
      return {
        content: [{ type: "text", text: `Error: ${error.message}` }],
        isError: true,
      };
    }
  }
);

// --- Start Server ---
const transport = new StdioServerTransport();
await server.connect(transport);
