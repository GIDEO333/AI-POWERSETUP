#!/usr/bin/env python3
"""
GLM Claude Proxy v1.0
Translates Anthropic Messages API → z.ai GLM OpenAI-compatible API

Usage:
  OPENAI_API_KEY=<z.ai key> python3 glm_claude_proxy.py

Then set:
  export ANTHROPIC_BASE_URL=http://localhost:9099
  export ANTHROPIC_API_KEY=dummy
  claude
"""

import json
import os
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer

import litellm

# Suppress LiteLLM noise
logging.getLogger("LiteLLM").setLevel(logging.WARNING)

PORT = int(os.environ.get("PROXY_PORT", "9099"))
API_KEY = os.environ.get("OPENAI_API_KEY", "")
API_BASE = os.environ.get("OPENAI_API_BASE", "https://api.z.ai/api/coding/paas/v4")
MODEL = os.environ.get("GLM_MODEL", "openai/glm-4.7")


def anthropic_to_openai_messages(anthropic_messages, system_prompt=None):
    """Convert Anthropic message format to OpenAI format."""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    for msg in anthropic_messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        # Content can be a string or a list of content blocks
        if isinstance(content, list):
            text_parts = []
            for block in content:
                if isinstance(block, dict):
                    if block.get("type") == "text":
                        text_parts.append(block.get("text", ""))
                    elif block.get("type") == "tool_result":
                        text_parts.append(str(block.get("content", "")))
                else:
                    text_parts.append(str(block))
            content = "\n".join(text_parts)
        messages.append({"role": role, "content": content})
    return messages


def call_glm(messages, max_tokens=4096, stream=False, temperature=0.6):
    """Forward request to z.ai GLM via LiteLLM."""
    response = litellm.completion(
        model=MODEL,
        messages=messages,
        max_tokens=max_tokens,
        api_key=API_KEY,
        api_base=API_BASE,
        temperature=temperature,
        stream=stream,
        num_retries=0,
        timeout=120,
    )
    return response


def build_anthropic_response(glm_response, model_name="glm-4.7"):
    """Convert LiteLLM response to Anthropic Messages API format."""
    choice = glm_response.choices[0]
    msg = choice.message
    text = msg.content or ""
    # GLM flash sometimes puts content in reasoning_content
    if not text and hasattr(msg, "reasoning_content") and msg.reasoning_content:
        text = msg.reasoning_content
    if not text and hasattr(msg, "model_extra"):
        text = (msg.model_extra or {}).get("reasoning_content", "")

    usage = glm_response.usage
    return {
        "id": f"msg_{glm_response.id or 'glm'}",
        "type": "message",
        "role": "assistant",
        "model": model_name,
        "content": [{"type": "text", "text": text}],
        "stop_reason": "end_turn",
        "stop_sequence": None,
        "usage": {
            "input_tokens": usage.prompt_tokens if usage else 0,
            "output_tokens": usage.completion_tokens if usage else 0,
        },
    }


class ProxyHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"[GLM Proxy] {format % args}")

    def send_json(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        # Health check
        if self.path == "/health":
            self.send_json(200, {"status": "ok", "model": MODEL, "backend": API_BASE})
        else:
            self.send_json(404, {"error": "Not found"})

    def do_POST(self):
        if self.path not in ("/v1/messages", "/v1/messages/"):
            self.send_json(404, {"error": f"Unknown endpoint: {self.path}"})
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)

        try:
            req = json.loads(body)
        except json.JSONDecodeError:
            self.send_json(400, {"error": "Invalid JSON"})
            return

        try:
            system = req.get("system", None)
            if isinstance(system, list):
                system = "\n".join(b.get("text", "") for b in system if isinstance(b, dict))

            messages = anthropic_to_openai_messages(req.get("messages", []), system)
            max_tokens = req.get("max_tokens", 4096)
            temperature = req.get("temperature", 0.6)
            stream = req.get("stream", False)

            if stream:
                # Streaming response
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()

                glm_stream = call_glm(messages, max_tokens, stream=True, temperature=temperature)

                # Send SSE opening event
                self.wfile.write(b'event: message_start\ndata: {"type":"message_start","message":{"id":"msg_stream","type":"message","role":"assistant","content":[],"model":"glm-4.7","stop_reason":null,"usage":{"input_tokens":0,"output_tokens":0}}}\n\n')
                self.wfile.write(b'event: content_block_start\ndata: {"type":"content_block_start","index":0,"content_block":{"type":"text","text":""}}\n\n')
                self.wfile.flush()

                for chunk in glm_stream:
                    delta = chunk.choices[0].delta if chunk.choices else None
                    if delta and delta.content:
                        payload = json.dumps({
                            "type": "content_block_delta",
                            "index": 0,
                            "delta": {"type": "text_delta", "text": delta.content}
                        })
                        self.wfile.write(f"event: content_block_delta\ndata: {payload}\n\n".encode())
                        self.wfile.flush()

                self.wfile.write(b'event: content_block_stop\ndata: {"type":"content_block_stop","index":0}\n\n')
                self.wfile.write(b'event: message_delta\ndata: {"type":"message_delta","delta":{"stop_reason":"end_turn","stop_sequence":null},"usage":{"output_tokens":0}}\n\n')
                self.wfile.write(b'event: message_stop\ndata: {"type":"message_stop"}\n\n')
                self.wfile.flush()
            else:
                glm_response = call_glm(messages, max_tokens, temperature=temperature)
                anthropic_resp = build_anthropic_response(glm_response)
                self.send_json(200, anthropic_resp)

        except Exception as e:
            print(f"[GLM Proxy ERROR] {e}")
            self.send_json(500, {
                "type": "error",
                "error": {"type": "api_error", "message": str(e)}
            })


if __name__ == "__main__":
    if not API_KEY:
        print("❌ ERROR: OPENAI_API_KEY not set. Export your z.ai API key first.")
        exit(1)

    print(f"🚀 GLM Claude Proxy starting on port {PORT}")
    print(f"   Model  : {MODEL}")
    print(f"   Backend: {API_BASE}")
    print(f"\n   Set these in your shell:")
    print(f"   export ANTHROPIC_BASE_URL=http://localhost:{PORT}")
    print(f"   export ANTHROPIC_API_KEY=dummy")
    print(f"   claude\n")

    server = HTTPServer(("localhost", PORT), ProxyHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[GLM Proxy] Stopped.")
