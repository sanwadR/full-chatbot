import os
import chainlit as cl
from dotenv import load_dotenv
from main import ChatbotWithMemory

# ==============================
# Load environment variables
# ==============================
load_dotenv()


# ==============================
# On Chat Start - runs when user opens the app
# ==============================
@cl.on_chat_start
async def on_chat_start():
    # Create a new chatbot instance for this user session
    chatbot = ChatbotWithMemory()

    # Store chatbot in user session so it persists
    cl.user_session.set("chatbot", chatbot)

    # Welcome message
    await cl.Message(
        content=(
            "👋 **Welcome to the AI Chatbot!**\n\n"
            "I can help you with:\n"
            "- 🌤️ **Weather** — Ask me weather of any city!\n"
            "- 💬 **General Questions** — Ask me anything!\n\n"
            "**Commands:**\n"
            "- `/clear` — Clear conversation memory\n"
            "- `/model <name>` — Change AI model\n"
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
        await cl.Message(content="🗑️ **Memory cleared!** Starting fresh conversation.").send()
        return

    elif user_input.lower().startswith("/model"):
        parts = user_input.split()
        if len(parts) > 1:
            model_name = parts[1]
            chatbot.change_model(model_name)
            await cl.Message(content=f"🤖 **Model changed to:** `{model_name}`").send()
        else:
            await cl.Message(content="⚠️ **Usage:** `/model <model_name>`\n\nExample: `/model llama-3.3-70b-versatile`").send()
        return

    # ==============================
    # Show typing indicator while processing
    # ==============================
    async with cl.Step(name="Thinking...") as step:
        step.input = user_input

        # Get response from chatbot
        response = chatbot.chat(user_input)

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