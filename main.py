import os
from dotenv import load_dotenv
from typing import Annotated
from typing_extensions import TypedDict

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage, ToolMessage
from langchain_core.tools import BaseTool

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()


class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


class ChatbotWithMemory:
    def __init__(self, model_name="llama-3.3-70b-versatile", temperature=0.7, tools: list[BaseTool] = None):
        self.model_name = model_name
        self.temperature = temperature
        self.session_id = "default"
        self.memory = MemorySaver()
        self._build_graph(tools or [])

    def _build_graph(self, tools: list[BaseTool]):
        self.llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name=self.model_name,
            temperature=self.temperature,
        )

        # Build a lookup dict from the injected MCP tools
        self.tools = {t.name: t for t in tools}
        self.llm_with_tools = self.llm.bind_tools(tools) if tools else self.llm

        self.system_message = SystemMessage(
            content=(
                "You are a helpful AI assistant. "
                "If the user asks about weather, use the get_weather tool."
            )
        )

        def llm_node(state: State):
            messages = [self.system_message] + state["messages"]
            response = self.llm_with_tools.invoke(messages)
            return {"messages": [response]}

        async def tool_node(state: State):
            last_message = state["messages"][-1]
            tool_messages = []
            for tool_call in last_message.tool_calls:
                result = await self.tools[tool_call["name"]].ainvoke(tool_call["args"])
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
def main():
    print("=" * 60)
    print("LangGraph + Groq Chatbot with Function Calling")
    print("=" * 60)
    print("Commands:")
    print("/clear  - Clear memory")
    print("/model <name> - Change model")
    print("/quit   - Exit")
    print("=" * 60)

    chatbot = ChatbotWithMemory()

    while True:
        user_input = input("\nYou: ").strip()

        if not user_input:
            continue

        if user_input.lower() == "/quit":
            print("Goodbye!")
            break

        elif user_input.lower() == "/clear":
            chatbot.clear_memory()
            continue

        elif user_input.lower().startswith("/model"):
            parts = user_input.split()
            if len(parts) > 1:
                chatbot.change_model(parts[1])
            else:
                print("Usage: /model <model_name>")
            continue

        response = chatbot.chat(user_input)
        print(f"\nBot: {response}")


if __name__ == "__main__":
    main()