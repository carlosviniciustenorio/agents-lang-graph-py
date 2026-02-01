# IA Agent com LangGraph, MCP, RAG e Observabilidade

Este projeto demonstra como construir um **agente de IA produtivo**
usando:

-   **LangGraph** para orquestração de estados.
-   **Ollama + Mistral** como LLM local.
-   **MCP (Model Context Protocol)** para descoberta e execução de
    ferramentas.
-   **RAG com FAISS + SentenceTransformers**.
-   **FastAPI** como MCP Server.
-   **Langfuse** para observabilidade local.

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

pip install langchain langgraph langchain-ollama fastapi uvicorn faiss-cpu sentence-transformers requests langfuse
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

-   Chunking de documentos\
-   Geração de embeddings\
-   Indexação com FAISS\
-   Busca semântica antes do LLM

------------------------------------------------------------------------

## MCP

-   Handshake com o servidor\
-   tools/list para descoberta\
-   tools/call via JSON-RPC

------------------------------------------------------------------------

## Observabilidade com Langfuse (Local)

O projeto já usa o `CallbackHandler` do Langfuse no agente.

### 1️⃣ Subindo o Langfuse local

A forma mais simples é via Docker:

``` bash
git clone https://github.com/langfuse/langfuse.git
cd langfuse
docker compose up -d
```

Acesse:

``` text
http://localhost:3000
```

Crie um projeto e gere:

-   Public Key\
-   Secret Key

------------------------------------------------------------------------

### 2️⃣ Configurando variáveis de ambiente

No seu projeto:

``` bash
export LANGFUSE_PUBLIC_KEY=pk_...
export LANGFUSE_SECRET_KEY=sk_...
export LANGFUSE_HOST=http://localhost:3000
```

------------------------------------------------------------------------

### 3️⃣ Executando com tracing

Com tudo configurado:

``` bash
python agent.py
```

Você poderá ver no Langfuse:

-   Cada nó do LangGraph\
-   Prompts e respostas\
-   Latência\
-   Erros e retries

Langfuse transforma o agente em um sistema **debugável e observável**.

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