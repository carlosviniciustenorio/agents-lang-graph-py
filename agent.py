import json
import re
from typing import TypedDict, Optional
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END
from mcp_client import MCPClient
from langfuse.langchain import CallbackHandler


handler = CallbackHandler()
llm = ChatOllama(model="mistral", temperature=0.3, callbacks=[handler])
mcp = MCPClient()


# ---------------- STATE ----------------

class State(TypedDict):
    ask: str
    perception: Optional[str]
    plan: Optional[str]
    tool_call: Optional[str]
    result: Optional[str]
    valid: Optional[bool]
    attempts: int


# ---------------- NODES ----------------

def perception(state: State):
    prompt = f"""
Classify the user request and intention.

User: {state['ask']}
"""
    r = llm.invoke(prompt).content
    return {"perception": r}


def planner(state: State):
    prompt = f"""
Create a short actionable plan.

Perception:
{state['perception']}
"""
    r = llm.invoke(prompt).content
    return {"plan": r}


def tool_discovery(state: State):
    tools = mcp.list_tools()

    prompt = f"""
You are a tool selector.

User: {state['ask']}
Plan: {state['plan']}

Available tools:
{tools}

Rules:
- If the user asks about cars, prices, ads, vehicles, models, listings, you MUST use "get_ads".
- If the user asks about searching knowledge, use "rag_search".
- Return ONLY valid JSON.
- No markdown.
- No explanation.

Format:
{{"name": "<tool_name>", "args": {{}}}}
"""
    r = llm.invoke(prompt).content
    return {"tool_call": r}


def executor(state: State):
    raw = state["tool_call"]

    match = re.search(r"\{.*\}", raw, re.S)
    if not match:
        return {
            "result": f"Invalid tool_call: {raw}",
            "attempts": state["attempts"] + 1,
        }

    tool_call = json.loads(match.group())

    # ---- default args ----
    tool_call.setdefault("args", {})

    if tool_call["name"] == "get_ads":
        tool_call["args"].setdefault("take", 5)

    data = mcp.call(
        tool_call["name"],
        tool_call.get("args", {})
    )

    # ---- format output ----
    if tool_call["name"] == "get_ads" and isinstance(data, list):
        lines = []
        for a in data:
            modelo = a["modelo"]["descricao"]
            marca = a["modelo"]["marca"]["descricao"]
            ano = a["anoVeiculo"]
            preco = a["preco"]
            cidade = a["cidade"]

            lines.append(
                f"- {marca} {modelo} {ano} — R$ {preco:,} — {cidade}"
            )

        formatted = "\n".join(lines)

    else:
        formatted = json.dumps(data, ensure_ascii=False, indent=2)

    return {
        "result": formatted,
        "attempts": state["attempts"] + 1
    }


def validator(state: State):
    prompt = f"""
Validate if the answer satisfies the user.

User: {state['ask']}
Answer: {state['result']}

Return true or false.
"""
    r = llm.invoke(prompt).content.lower()
    return {"valid": "true" in r}


# ---------------- FLOW CONTROL ----------------

def should_continue(state: State):
    if state["valid"]:
        return "end"
    if state["attempts"] > 2:
        return "end"
    return "retry"


# ---------------- GRAPH ----------------

graph = StateGraph(State)

graph.add_node("perception", perception)
graph.add_node("planner", planner)
graph.add_node("tool_discovery", tool_discovery)
graph.add_node("executor", executor)
graph.add_node("validator", validator)

graph.set_entry_point("perception")

graph.add_edge("perception", "planner")
graph.add_edge("planner", "tool_discovery")
graph.add_edge("tool_discovery", "executor")
graph.add_edge("executor", "validator")

graph.add_conditional_edges(
    "validator",
    should_continue,
    {
        "retry": "planner",
        "end": END,
    },
)

agent = graph.compile()


# ---------------- RUN ----------------

if __name__ == "__main__":
    result = agent.invoke(
        {
            "ask": "List some cars from ads available just by your known tools",
            "attempts": 0
        },
        config={"callbacks": [handler]}
    )

    print("\nFINAL RESULT\n")
    print(result["result"])