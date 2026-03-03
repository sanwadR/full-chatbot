from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from typing import Annotated
from typing_extensions import TypedDict
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define the graph state
class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


class ChatbotWithMemory:
    def __init__(self, model_name="llama3-8b-8192", temperature=0.7):
        """
        Initialize the chatbot with Groq LLM and LangGraph memory

        Args:
            model_name (str): The Groq model to use (default: llama3-8b-8192)
                             Other options: llama3-70b-8192, gemma2-9b-it, etc.
            temperature (float): Controls randomness (0.0 to 1.0)
        """
        self.model_name = model_name
        self.temperature = temperature
        self.session_id = "default"
        self.memory = MemorySaver()
        self._build_graph()

    def _build_graph(self):
        """Build or rebuild the LangGraph state graph"""
        self.llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name=self.model_name,
            temperature=self.temperature
        )

        self.system_message = SystemMessage(
            content="You are a helpful AI assistant. Use the conversation history to provide contextual responses."
        )

        def chatbot_node(state: State):
            messages = [self.system_message] + state["messages"]
            response = self.llm.invoke(messages)
            return {"messages": [response]}

        graph = StateGraph(State)
        graph.add_node("chatbot", chatbot_node)
        graph.add_edge(START, "chatbot")
        graph.add_edge("chatbot", END)

        self.graph = graph.compile(checkpointer=self.memory)

    def chat(self, user_input):
        """
        Send a message to the chatbot and get a response

        Args:
            user_input (str): The user's message

        Returns:
            str: The chatbot's response
        """
        try:
            config = {"configurable": {"thread_id": self.session_id}}
            response = self.graph.invoke(
                {"messages": [HumanMessage(content=user_input)]},
                config=config
            )
            return response["messages"][-1].content
        except Exception as e:
            return f"Error: {str(e)}"

    def clear_memory(self):
        """Clear the conversation history by starting a new session"""
        self.session_id = os.urandom(8).hex()
        print("Conversation memory cleared!")

    def get_conversation_history(self):
        """Get the current conversation history"""
        config = {"configurable": {"thread_id": self.session_id}}
        state = self.graph.get_state(config)
        if state and state.values.get("messages"):
            messages = state.values["messages"]
            return "\n".join([f"{msg.type.upper()}: {msg.content}" for msg in messages])
        return "No conversation history yet."

    def change_model(self, model_name, temperature=0.7):
        """
        Change the LLM model on the fly

        Args:
            model_name (str): New model name
            temperature (float): New temperature setting
        """
        self.model_name = model_name
        self.temperature = temperature
        self._build_graph()
        print(f"Model changed to: {model_name}")


def main():
    """Main function to run the chatbot"""
    print("=" * 60)
    print("🤖 LangChain Chatbot with Groq API")
    print("=" * 60)
    print("\nAvailable Commands:")
    print("  /clear  - Clear conversation history")
    print("  /history - Show conversation history")
    print("  /model <name> - Change model (e.g., /model mixtral-8x7b-32768)")
    print("  /quit   - Exit the chatbot")
    print("=" * 60)
    
    # Initialize chatbot with default model
    chatbot = ChatbotWithMemory(model_name="llama-3.3-70b-versatile", temperature=0.7)
    
    print("\n✅ Chatbot initialized! Type your message below.\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if not user_input:
            continue
        
        # Handle commands
        if user_input.lower() == "/quit":
            print("\n👋 Goodbye!")
            break
        elif user_input.lower() == "/clear":
            chatbot.clear_memory()
            continue
        elif user_input.lower() == "/history":
            history = chatbot.get_conversation_history()
            print("\n📜 Conversation History:")
            print(history)
            print()
            continue
        elif user_input.lower().startswith("/model"):
            parts = user_input.split()
            if len(parts) > 1:
                new_model = parts[1]
                chatbot.change_model(new_model)
            else:
                print("Usage: /model <model_name>")
            continue
        
        # Get chatbot response
        response = chatbot.chat(user_input)
        print(f"\nBot: {response}\n")


if __name__ == "__main__":
    main()