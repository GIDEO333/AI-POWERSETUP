# Sourcegraph MCP — Agent Instructions

## When to USE this tool
- Refactoring besar: perlu tahu "bagaimana project besar lain melakukannya"
- Mengimplementasikan library baru yang belum familiar
- Debugging edge case yang sangat spesifik, butuh bukti dari codebase lain
- Mencari contoh pattern tertentu di repo terkenal (e.g., "how does Next.js handle X")

## When NOT to use
- Sudah tahu cara implementasinya → langsung coding
- Searching di project lokal → pakai `grep_search` atau `find_by_name`
# Sourcegraph MCP Bridge - Agent Instructions

This server provides the `search_code` tool, exposing the full power of the Sourcegraph Code Search engine.

### Core Directive for AI Agents
When tasked with finding implementation examples, debugging architecture, or looking up proprietary usage patterns, you MUST use the Sourcegraph MCP. Do not hallucinate code when you can search across open-source truth instead.

### Query Construction Masterclass
Sourcegraph queries are highly semantic text strings, not structured JSON. You must construct the string expertly:

1. **Always Anchor Repository Scopes**
   To prevent searching billions of lines of code and timing out, you MUST scope searches:
   `repo:^github\.com/owner/name$` (Use `^` and `$` to prevent partial matches like `owner/name-fork`).
2. **Combine Multiple Scopes (OR logic)**
   To search Next.js and React simultaneously:
   `repo:^github\.com/(vercel/next\.js|facebook/react)$`
3. **Targeting File Extensions**
   Use either `lang:` (e.g. `lang:python`) or `file:` regex (e.g. `file:\.test\.tsx$`).
4. **Targeting File Exclusion**
   Use `NOT` or preceding hyphens: `-file:\.md$` or `-repo:foo`.
5. **Exact Match Keywords**
   Enclose keywords in quotes if they contain special characters: `"for await (const chunk"`

### Example Golden Queries
- **Find Server-Sent Events implementation in OpenAI SDK:**
  `repo:^github\.com/openai/openai-node$ "for await" chunk TextDecoder lang:typescript`
- **Find how Prisma handles SQLite migrations:**
  `repo:^github\.com/prisma/prisma$ file:migration sqlite boolean`

### Limitations
- **Results Capped:** The tool forces a hard cap of 5 top matches. Therefore, your queries must be highly specific to be useful. Focus your query narrowly (e.g., specific files, precise terms).

## Anti-Bloat Rules (WAJIB DIPATUHI)
1. SELALU gunakan query spesifik dengan `repo:` filter
2. Hasil SUDAH dibatasi otomatis ke 5 matches oleh bridge
3. Baca file satu-per-satu, JANGAN minta seluruh repo
4. Jika 0 results, perbaiki query, JANGAN ulangi query yang sama
5. Maksimal 3 panggilan search per sesi kerja

## Query Examples
❌ `search_code("useEffect")`
✅ `search_code("useEffect cleanup WebSocket disconnect repo:vercel/next.js")`

❌ `search_code("database connection")`
✅ `search_code("pg.Pool idleTimeoutMillis repo:expressjs/express")`
