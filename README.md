# IA Agent com LangGraph, MCP, RAG e Observabilidade

Este projeto demonstra como construir um **agente de IA produtivo**
usando:

-   **LangGraph** para orquestração de estados.
-   **Ollama + Mistral** como LLM local.
-   **MCP (Model Context Protocol)** para descoberta e execução de
    ferramentas.
-   **RAG com FAISS + SentenceTransformers**.
-   **FastAPI** como MCP Server.
-   **LangSmith / Langfuse** para observabilidade.

O objetivo é sair do modelo de chatbot e entrar em **engenharia de
agentes**, onde a IA planeja, decide, executa ações reais e valida
resultados.

------------------------------------------------------------------------

## Visão Geral

O agente executa o seguinte fluxo:

1.  **Perception** -- entende a intenção do usuário.\
2.  **Planner** -- cria um plano curto de ação.\
3.  **Tool Discovery** -- escolhe ferramentas via MCP.\
4.  **Executor** -- executa RAG ou chama APIs externas.\
5.  **Validator** -- valida se a resposta resolve o pedido.\
6.  **Retry / End** -- controla convergência.

------------------------------------------------------------------------

## Estrutura do Projeto

    .
    ├── agent.py
    ├── mcp_client.py
    ├── mcp_server.py
    ├── rag.py
    └── requirements.txt

------------------------------------------------------------------------

## Pré-requisitos

-   Python 3.10+
-   Ollama instalado
-   Modelo Mistral

``` bash
ollama pull mistral
```

------------------------------------------------------------------------

## Instalação

``` bash
python -m venv venv
source venv/bin/activate

pip install langchain langgraph langchain-ollama fastapi uvicorn faiss-cpu sentence-transformers requests
```

------------------------------------------------------------------------

## Subindo o MCP Server

``` bash
uvicorn mcp_server:app --reload --port 9001
```

------------------------------------------------------------------------

## Executando o Agente

``` bash
python agent.py
```

------------------------------------------------------------------------

## RAG

-   Chunking
-   Embeddings
-   Indexação FAISS
-   Busca semântica

------------------------------------------------------------------------

## MCP

-   Handshake
-   tools/list
-   tools/call via JSON-RPC

------------------------------------------------------------------------

## Observabilidade com LangSmith

``` bash
export LANGSMITH_TRACING=true
export LANGSMITH_ENDPOINT=https://api.smith.langchain.com
export LANGSMITH_API_KEY=<SUA_KEY>
export LANGSMITH_PROJECT="IA-Agents"
```

------------------------------------------------------------------------

## Arquitetura

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

    ExternalAPI[(API Anúncios)]
```

------------------------------------------------------------------------