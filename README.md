# 🤖 LangGraph Chatbot with Groq API

> A fully functional chatbot built with **LangGraph** that uses **Groq API** and maintains full conversation context/memory.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🧠 **Context Memory** | Remembers entire conversation history across sessions |
| 🔄 **Model Flexibility** | Easily switch between different Groq models on the fly |
| 🏗️ **LangGraph Architecture** | Modern, scalable architecture using state graphs |
| ⌨️ **Interactive Commands** | Clear history, view history, change models dynamically |

---

## 🚀 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/sanwadR/full-chatbot.git
cd full-chatbot
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Key

Edit the `.env` file and add your Groq API key:

```env
GROQ_API_KEY=your_actual_groq_api_key_here
```

> 📌 Get your free Groq API key from: [https://console.groq.com/](https://console.groq.com/)

### 5. Run the Chatbot

```bash
python chatbot.py
```

---

## 📊 Available Models

| Model | Notes |
|---|---|
| `llama3-8b-8192` | Default |
| `llama3-70b-8192` | More powerful |
| `llama-3.3-70b-versatile` | Latest Llama |
| `mixtral-8x7b-32768` | Large context |
| `gemma2-9b-it` | Google Gemma |

---

## ⌨️ Commands

| Command | Description |
|---|---|
| `/clear` | Clear conversation history |
| `/history` | Show conversation history |
| `/model <name>` | Switch model |
| `/quit` | Exit the chatbot |

---

## 📁 Project Structure

```
full-chatbot/
├── chatbot.py        # Main chatbot implementation
├── .env              # Environment variables (API keys)
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

---

## 🔧 How It Works

1. **LangGraph** — Framework for building state-based LLM applications
2. **ChatGroq** — Groq API integration for fast LLM inference
3. **MemorySaver** — LangGraph built-in checkpointer for conversation memory
4. **StateGraph** — Manages the chatbot processing flow

---

## 📦 Requirements

```
langchain-groq
langchain-core
langgraph
python-dotenv
typing-extensions
```
