import os
import sys
import chainlit as cl
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from main import ChatbotWithMemory

# ==============================
# Load environment variables
# ==============================
_HERE = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_HERE, ".env"))


# ==============================
# MCP Configuration
# ==============================
MCP_CONFIG = {
    "weather": {
        "command": sys.executable,
        "args": [os.path.join(_HERE, "mcp_server.py")],
        "transport": "stdio",
    }
}


# ==============================
# On Chat Start - runs when user opens the app
# ==============================
@cl.on_chat_start
async def on_chat_start():
    # Start MCP client — spawns mcp_server.py as a subprocess
    client = MultiServerMCPClient(MCP_CONFIG)

    # Discover tools from the MCP server
    tools = await client.get_tools()

    # Inject tools into the chatbot
    chatbot = ChatbotWithMemory(tools=tools)
    cl.user_session.set("chatbot", chatbot)

    # Welcome message
    await cl.Message(
        content=(
            "👋 **Welcome to the AI Chatbot (MCP-powered)!**\n\n"
            f"Tools loaded via MCP: `{[t.name for t in tools]}`\n\n"
            "- 🌤️ **Current Weather** — *What's the weather in Tokyo?*\n"
            "- 🕐 **Hourly Forecast** — *Give me the hourly forecast for London for the next 12 hours.*\n"
            "- 📅 **Daily Forecast** — *What's the 7-day forecast for New York?*\n"
            "- 🌫️ **Air Quality** — *What is the AQI in Delhi?*\n"
            "- 📍 **Geocoding** — *Where are the coordinates of Paris?*\n"
            "- 💬 **General Questions** — Ask me anything!\n\n"
            "**Commands:** `/clear` | `/model <name>`"
        )
    ).send()


# ==============================
# On Message - runs every time user sends a message
# ==============================
@cl.on_message
async def on_message(message: cl.Message):
    # Get the chatbot from user session
    chatbot: ChatbotWithMemory = cl.user_session.get("chatbot")
    user_input = message.content.strip()

    # ==============================
    # Handle Commands
    # ==============================
    if user_input.lower() == "/clear":
        chatbot.clear_memory()
        await cl.Message(content="🗑️ Memory cleared!").send()
        return

    elif user_input.lower().startswith("/model"):
        parts = user_input.split()
        if len(parts) > 1:
            chatbot.change_model(parts[1])
            await cl.Message(content=f"🤖 Model changed to: `{parts[1]}`").send()
        else:
            await cl.Message(content="⚠️ Usage: `/model <model_name>`").send()
        return

    # ==============================
    # Show typing indicator while processing
    # ==============================
    async with cl.Step(name="Thinking...") as step:
        step.input = user_input
        response = await chatbot.chat(user_input)
        step.output = response

    # ==============================
    # Send the final response
    # ==============================
    await cl.Message(content=response).send()


# ==============================
# On Chat End - runs when user closes the app
# ==============================
@cl.on_chat_end
async def on_chat_end():
    print("User session ended.")