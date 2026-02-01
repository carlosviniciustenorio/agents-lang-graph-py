import requests
import itertools
import json


class MCPClient:
    def __init__(self, base_url="http://localhost:9001/rpc", api_key="super-secret-key"):
        self.base_url = base_url
        self.api_key = api_key
        self.session_id = None
        self._ids = itertools.count(1)

    def _next_id(self):
        return next(self._ids)

    def _headers(self):
        h = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
        }
        if self.session_id:
            h["session-id"] = self.session_id
        return h

    def _rpc(self, method: str, params: dict | None = None):
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": method,
            "params": params or {},
        }

        r = requests.post(
            self.base_url,
            json=payload,
            headers=self._headers(),
            stream=True,
            timeout=30,
        )
        r.raise_for_status()

        buffer = ""
        for chunk in r.iter_content(decode_unicode=True):
            buffer += chunk

        data = json.loads(buffer)

        if "error" in data:
            raise RuntimeError(data["error"])

        return data["result"]

    # ---------- MCP ----------

    def handshake(self):
        result = self._rpc(
            "initialize",
            {
                "protocolVersion": "2025-06-18",
                "clientInfo": {"name": "agent", "version": "1.0.0"},
            },
        )
        self.session_id = result["sessionId"]
        return result

    def list_tools(self):
        if not self.session_id:
            self.handshake()
        return self._rpc("tools/list")

    def call(self, tool_name: str, args: dict):
        if not self.session_id:
            self.handshake()

        return self._rpc(
            "tools/call",
            {
                "name": tool_name,
                "arguments": args,
            },
        )
