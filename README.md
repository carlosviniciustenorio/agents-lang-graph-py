# AI Agent with LangGraph, MCP, RAG, and Observability 🔧

This project demonstrates how to build a **productive AI agent** using:

- **LangGraph** for state orchestration.
- **Ollama + Mistral** as a local LLM.
- **MCP (Model Context Protocol)** for tool discovery and execution.
- **RAG with FAISS + SentenceTransformers**.
- **FastAPI** as the MCP Server.
- **Langfuse** for local observability.

The goal is to move beyond chatbots into **agent engineering**, where the AI plans, decides, executes real actions, and validates results.

---

## Overview

The agent follows this flow:

1. **Perception** — understands the user's intent.
2. **Planner** — creates a short action plan.
3. **Tool Discovery** — selects tools via MCP.
4. **Executor** — runs RAG or calls external APIs.
5. **Validator** — verifies whether the response resolves the request.
6. **Retry / End** — manages convergence.

---

## Project Structure

    .
    ├── agent.py
    ├── mcp_client.py
    ├── mcp_server.py
    └── rag.py

------------------------------------------------------------------------

## Prerequisites

- Python 3.10+
- Ollama installed
- Mistral model

```bash
ollama pull mistral
```

---

## Installation

```bash
python -m venv venv
source venv/bin/activate

pip install langchain langgraph langchain-ollama fastapi uvicorn faiss-cpu sentence-transformers requests langfuse
```

---

## Starting the MCP Server

```bash
uvicorn mcp_server:app --reload --port 9001
```

---

## Running the Agent

```bash
python agent.py
```

---

## RAG

- Document chunking
- Embedding generation
- Indexing with FAISS
- Semantic search before the LLM

---

## MCP

- Handshake with the server
- `tools/list` for discovery
- `tools/call` via JSON-RPC

---

## Observability with Langfuse (Local) 🔍

The project already uses Langfuse's `CallbackHandler` in the agent.

### 1️⃣ Start Langfuse locally

The simplest way is via Docker:

```bash
git clone https://github.com/langfuse/langfuse.git
cd langfuse
docker compose up -d
```

Access:

```
http://localhost:3000
```

Create a project and generate:

- Public Key
- Secret Key

---

### 2️⃣ Set environment variables

In your project:

```bash
export LANGFUSE_PUBLIC_KEY=pk_...
export LANGFUSE_SECRET_KEY=sk_...
export LANGFUSE_HOST=http://localhost:3000
```

---

### 3️⃣ Run with tracing

With everything configured:

```bash
python agent.py
```

You’ll see in Langfuse:

- Each LangGraph node
- Prompts and responses
- Latency
- Errors and retries

Langfuse makes the agent **debuggable and observable**.

---


## Architecture

``` mermaid
flowchart TD
    User --> Agent

    subgraph Agent[LangGraph Agent]
        P[Perception]
        PL[Planner]
        TD2[Tool Discovery]
        EX[Executor]
        V[Validator]
    end

    Agent --> P
    P --> PL
    PL --> TD2
    TD2 --> EX
    EX --> V
    V -->|retry| PL
    V -->|end| User

    EX --> MCPClient

    subgraph MCP[MCP Layer]
        MCPClient --> MCPServer
    end

    MCPServer --> RAG
    MCPServer --> ExternalAPI

    subgraph RAG[RAG - FAISS]
        Index[(Vector Index)]
    end

    ExternalAPI[(External API)]
```

------------------------------------------------------------------------