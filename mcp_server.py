import json
import uuid
import time
import os
import requests
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from rag import retrieve

app = FastAPI(title="MCP Server JSON-RPC")

API_KEY = "super-secret-key"
SESSIONS = {}

EXTERNAL_ANUNCIOS_URL = os.getenv(
    "ANUNCIOS_API_URL",
    "http://localhost:8000/api/anuncios"
)
TIMEOUT = 10


# ---------------- CORE ----------------

def validate_api_key(x_api_key: str):
    if x_api_key != API_KEY:
        raise HTTPException(401, "Invalid API Key")


def validate_session(session_id: str):
    if session_id not in SESSIONS:
        raise HTTPException(401, "Invalid session")


# ---------------- TOOLS ----------------

TOOLS = {
    "rag_search": {
        "description": "Search knowledge base using RAG",
        "args": {"query": "string", "k": "int"},
    },
    "get_ads": {
        "description": "Fetch car ads from external REST API",
        "args": {"take": "int"},
    },
}


# ---------------- JSON-RPC HANDLERS ----------------

def rpc_initialize(params):
    session_id = str(uuid.uuid4())
    SESSIONS[session_id] = {"created_at": time.time()}
    return {"sessionId": session_id, "tools": TOOLS}


def rpc_list_tools(params):
    return TOOLS


def rpc_call_tool(params):
    name = params["name"]
    args = params.get("arguments", {})

    if name == "rag_search":
        return retrieve(args.get("query"), args.get("k", 2))

    if name == "get_ads":
        resp = requests.get(
            EXTERNAL_ANUNCIOS_URL,
            params={"take": args.get("take", 5)},
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json()

    raise HTTPException(404, f"Tool not found: {name}")


# ---------------- STREAMABLE JSON-RPC ----------------

@app.post("/rpc")
async def rpc_endpoint(
    request: Request,
    x_api_key: str = Header(..., alias="x-api-key"),
    session_id: str | None = Header(None, alias="session-id"),
):
    validate_api_key(x_api_key)

    payload = await request.json()

    method = payload.get("method")
    params = payload.get("params", {})
    rpc_id = payload.get("id")

    if method != "initialize":
        if not session_id:
            raise HTTPException(401, "Missing session-id")
        validate_session(session_id)

    def stream():
        try:
            if method == "initialize":
                result = rpc_initialize(params)
            elif method == "tools/list":
                result = rpc_list_tools(params)
            elif method == "tools/call":
                result = rpc_call_tool(params)
            else:
                raise Exception("Unknown method")

            response = {
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": result,
            }

        except Exception as e:
            response = {
                "jsonrpc": "2.0",
                "id": rpc_id,
                "error": {"message": str(e)},
            }

        yield json.dumps(response)

    return StreamingResponse(stream(), media_type="application/json")
