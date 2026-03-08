import os
import sys
import asyncio
from dotenv import load_dotenv
from typing import Annotated
from typing_extensions import TypedDict

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage, ToolMessage
from langchain_core.tools import BaseTool

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()


class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


class ChatbotWithMemory:
    def __init__(self, model_name="Qwen/Qwen2.5-72B-Instruct", temperature=0.7, tools: list[BaseTool] = None):
        self.model_name = model_name
        self.temperature = temperature
        self.session_id = "default"
        self.memory = MemorySaver()
        self._build_graph(tools or [])

    def _build_graph(self, tools: list[BaseTool]):
        self.llm = ChatOpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=os.getenv("HUGGINGFACE_API_KEY"),
            model=self.model_name,
            temperature=self.temperature,
        )

        # Build a lookup dict from the injected MCP tools
        self.tools = {t.name: t for t in tools}
        self.llm_with_tools = self.llm.bind_tools(tools) if tools else self.llm

        self.system_message = SystemMessage(
            content=(
                "You are a helpful AI assistant with access to weather and air quality tools.\n"
                "Available tools:\n"
                "- get_weather_by_city(city): current weather by city name\n"
                "- get_weather_by_coordinates(lat, lon): current weather by coordinates\n"
                "- get_hourly_forecast(city, hours): hourly forecast up to 48 hours\n"
                "- get_daily_forecast(city, days): daily forecast up to 8 days\n"
                "- get_air_pollution(city): AQI and pollutant levels\n"
                "- geocode_city(city): resolve a city to lat/lon\n"
                "Always use the appropriate tool when the user asks about weather, forecasts, or air quality."
            )
        )

        def llm_node(state: State):
            messages = [self.system_message] + state["messages"]
            print(f"[LLM] Sending {len(messages)} messages to model...")
            response = self.llm_with_tools.invoke(messages)
            if response.tool_calls:
                print(f"[LLM] Model requested tool calls: {[tc['name'] for tc in response.tool_calls]}")
            else:
                print("[LLM] Model returned a final response (no tool calls).")
            return {"messages": [response]}

        async def tool_node(state: State):
            last_message = state["messages"][-1]
            tool_messages = []
            for tool_call in last_message.tool_calls:
                print(f"[TOOL CALL] {tool_call['name']}({tool_call['args']})")
                raw = await self.tools[tool_call["name"]].ainvoke(tool_call["args"])
                # MCP returns [{'type': 'text', 'text': '...'}] — extract plain string
                if isinstance(raw, list):
                    result = "\n".join(
                        block["text"] for block in raw
                        if isinstance(block, dict) and block.get("type") == "text"
                    )
                else:
                    result = str(raw)
                print(f"[TOOL RESULT] {tool_call['name']} \u2192 {result[:200]}")
                tool_messages.append(
                    ToolMessage(content=result, tool_call_id=tool_call["id"])
                )
            return {"messages": tool_messages}

        def should_continue(state: State):
            last = state["messages"][-1]
            return "tool_node" if last.tool_calls else END

        graph = StateGraph(State)
        graph.add_node("llm_node", llm_node)
        graph.add_node("tool_node", tool_node)
        graph.add_edge(START, "llm_node")
        graph.add_conditional_edges("llm_node", should_continue)
        graph.add_edge("tool_node", "llm_node")
        self.graph = graph.compile(checkpointer=self.memory)

    async def chat(self, user_input: str) -> str:
        config = {"configurable": {"thread_id": self.session_id}}
        response = await self.graph.ainvoke(
            {"messages": [HumanMessage(content=user_input)]}, config=config
        )
        return response["messages"][-1].content

    def clear_memory(self):
        self.session_id = os.urandom(8).hex()

    def change_model(self, model_name: str):
        self.model_name = model_name
        # Rebuild graph with the same tools after model change
        current_tools = list(self.tools.values())
        self._build_graph(current_tools)


# ==============================
# Main CLI
# ==============================
async def main():
    # Import here to avoid circular at module level
    from langchain_mcp_adapters.client import MultiServerMCPClient

    _HERE = os.path.dirname(os.path.abspath(__file__))

    MCP_CONFIG = {
        "weather": {
            "command": sys.executable,
            "args": [os.path.join(_HERE, "mcp_server.py")],
            "transport": "stdio",
        }
    }

    print("=" * 60)
    print("LangGraph + HuggingFace Chatbot with Function Calling")
    print("=" * 60)
    print("Loading MCP tools...", end=" ", flush=True)
    client = MultiServerMCPClient(MCP_CONFIG)
    tools = await client.get_tools()
    print(f"OK — {[t.name for t in tools]}")
    print("Commands: /clear | /model <name> | /quit")
    print("=" * 60)

    chatbot = ChatbotWithMemory(tools=tools)

    while True:
        user_input = input("\nYou: ").strip()

        if not user_input:
            continue

        if user_input.lower() == "/quit":
            print("Goodbye!")
            break

        elif user_input.lower() == "/clear":
            chatbot.clear_memory()
            print("Memory cleared.")
            continue

        elif user_input.lower().startswith("/model"):
            parts = user_input.split()
            if len(parts) > 1:
                chatbot.change_model(parts[1])
                print(f"Model changed to: {parts[1]}")
            else:
                print("Usage: /model <model_name>")
            continue

        response = await chatbot.chat(user_input)
        print(f"\nBot: {response}")


if __name__ == "__main__":
    asyncio.run(main())