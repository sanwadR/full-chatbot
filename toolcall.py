import os
import requests
from dotenv import load_dotenv
from typing import Annotated
from typing_extensions import TypedDict

from langchain_groq import ChatGroq
from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
    BaseMessage,
    ToolMessage,
)
from langchain_core.tools import tool

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver


# ==============================
# Load environment variables
# ==============================
load_dotenv()


# ==============================
# Weather Tool
# ==============================
@tool
def get_weather(city: str) -> str:
    """
    Get current weather for a city.
    """
    try:
        # Get coordinates
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        geo_response = requests.get(geo_url).json()

        if "results" not in geo_response:
            return f"Could not find location: {city}"

        lat = geo_response["results"][0]["latitude"]
        lon = geo_response["results"][0]["longitude"]

        # Get weather
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&current_weather=true"
        )
        weather_response = requests.get(weather_url).json()

        temp = weather_response["current_weather"]["temperature"]
        wind = weather_response["current_weather"]["windspeed"]

        return (
            f"The current temperature in {city} is {temp}°C "
            f"with wind speed {wind} km/h."
        )

    except Exception as e:
        return f"Weather error: {str(e)}"


# ==============================
# Graph State
# ==============================
class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


# ==============================
# Chatbot with LangGraph
# ==============================
class ChatbotWithMemory:
    def __init__(self, model_name="llama-3.3-70b-versatile", temperature=0.7):
        self.model_name = model_name
        self.temperature = temperature
        self.session_id = "default"
        self.memory = MemorySaver()
        self._build_graph()

    def _build_graph(self):

        # Initialize Groq LLM
        self.llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name=self.model_name,
            temperature=self.temperature,
        )

        # Register tools
        self.tools = {"get_weather": get_weather}
        self.llm_with_tools = self.llm.bind_tools(list(self.tools.values()))

        # System prompt
        self.system_message = SystemMessage(
            content=(
                "You are a helpful AI assistant. "
                "If the user asks about weather, you must use the get_weather tool."
            )
        )

        # ==============================
        # LLM Node
        # ==============================
        def llm_node(state: State):
            print("[LLM Node] Calling LLM...")
            messages = [self.system_message] + state["messages"]
            response = self.llm_with_tools.invoke(messages)
            if response.tool_calls:
                print(f"[LLM Node] LLM wants to call tools: {[tc['name'] for tc in response.tool_calls]}")
            else:
                print("[LLM Node] LLM returned a final response.")
            return {"messages": [response]}

        # ==============================
        # Tool Node
        # ==============================
        def tool_node(state: State):
            last_message = state["messages"][-1]
            tool_messages = []

            for tool_call in last_message.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                print(f"[Tool Node] Calling tool: '{tool_name}' with args: {tool_args}")

                result = self.tools[tool_name].invoke(tool_args)
                print(f"[Tool Node] Tool '{tool_name}' returned: {result}")

                tool_messages.append(
                    ToolMessage(
                        content=result,
                        tool_call_id=tool_call["id"],
                    )
                )

            return {"messages": tool_messages}

        # ==============================
        # Conditional Edge
        # ==============================
        def should_continue(state: State):
            last_message = state["messages"][-1]
            if last_message.tool_calls:
                print("[Router] Routing to tool_node.")
                return "tool_node"
            print("[Router] No tool calls. Ending.")
            return END

        # ==============================
        # Build Graph
        # ==============================
        graph = StateGraph(State)

        graph.add_node("llm_node", llm_node)
        graph.add_node("tool_node", tool_node)

        graph.add_edge(START, "llm_node")

        graph.add_conditional_edges(
            "llm_node",
            should_continue,
        )

        graph.add_edge("tool_node", "llm_node")

        self.graph = graph.compile(checkpointer=self.memory)

    # ==============================
    # Chat Function
    # ==============================
    def chat(self, user_input):
        try:
            config = {"configurable": {"thread_id": self.session_id}}

            response = self.graph.invoke(
                {"messages": [HumanMessage(content=user_input)]},
                config=config,
            )

            return response["messages"][-1].content

        except Exception as e:
            return f"Error: {str(e)}"

    # ==============================
    # Clear Memory
    # ==============================
    def clear_memory(self):
        self.session_id = os.urandom(8).hex()
        print("Conversation memory cleared!")

    # ==============================
    # Change Model
    # ==============================
    def change_model(self, model_name, temperature=0.7):
        self.model_name = model_name
        self.temperature = temperature
        self._build_graph()
        print(f"Model changed to: {model_name}")


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