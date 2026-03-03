# 🤖 LangGraph Chatbot with Groq API

> A fully functional chatbot built with **LangGraph** that uses **Groq API** and maintains full conversation context/memory.

---

## ✨ Features

| Feature                       | Description                                            |
| ----------------------------- | ------------------------------------------------------ |
| 🧠 **Context Memory**         | Remembers entire conversation history across sessions  |
| 🔄 **Model Flexibility**      | Easily switch between different Groq models on the fly |
| 🏗️ **LangGraph Architecture** | Modern, scalable architecture using state graphs       |
| ⌨️ **Interactive Commands**   | Clear history, view history, change models dynamically |

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
venv\Scripts\activate      # Windows
source venv/bin/activate   # macOS/Linux
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

```
llama3-8b-8192          (default)
llama3-70b-8192
llama-3.3-70b-versatile
mixtral-8x7b-32768
gemma-7b-it
gemma2-9b-it
```

---

## ⌨️ Commands

| Command         | Description                                     |
| --------------- | ----------------------------------------------- |
| `/clear`        | Clear conversation history                      |
| `/history`      | Show conversation history                       |
| `/model <name>` | Switch model (e.g. `/model mixtral-8x7b-32768`) |
| `/quit`         | Exit the chatbot                                |

---

## 💬 Example Usage

```
You: Hello! What's your name?
Bot: Hello! I'm an AI assistant powered by LangGraph...

You: What's 25 + 17?
Bot: 25 + 17 equals 42.

You: What was the math problem I just asked?
Bot: You asked me to calculate 25 + 17...

You: /model mixtral-8x7b-32768
Model changed to: mixtral-8x7b-32768

You: /quit
👋 Goodbye!
```

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

The chatbot uses the following components:

1. **LangGraph** — Framework for building state-based LLM applications
2. **ChatGroq** — Groq API integration for fast LLM inference
3. **MemorySaver** — LangGraph's built-in checkpointer for conversation memory
4. **StateGraph** — Manages the chatbot's processing flow

> 💡 The architecture allows you to switch models or even LLM providers with minimal code changes!

---

## 📦 Requirements

```
langchain-groq
langchain-core
langgraph
python-dotenv
typing-extensions
```

---

<div align="center">

Built with ❤️ using **LangGraph** and **Groq API**

</div>
      }

      body {
        font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.6;
        color: #333;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
        padding: 20px;
      }

      .container {
        max-width: 900px;
        margin: 0 auto;
        background: white;
        border-radius: 10px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
        padding: 40px;
      }

      h1 {
        color: #667eea;
        margin-bottom: 10px;
        font-size: 2.5em;
      }

      .subtitle {
        color: #666;
        margin-bottom: 30px;
        font-size: 1.1em;
      }

      h2 {
        color: #667eea;
        margin-top: 35px;
        margin-bottom: 15px;
        font-size: 1.8em;
        border-bottom: 2px solid #667eea;
        padding-bottom: 10px;
      }

      h3 {
        color: #764ba2;
        margin-top: 20px;
        margin-bottom: 10px;
        font-size: 1.3em;
      }

      .features {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 20px;
        margin: 20px 0;
      }

      .feature-card {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 15px;
        border-radius: 5px;
      }

      .feature-card strong {
        color: #667eea;
      }

      code {
        background: #f5f5f5;
        padding: 2px 6px;
        border-radius: 3px;
        font-family: "Courier New", monospace;
        color: #d63384;
      }

      pre {
        background: #1e1e1e;
        color: #d4d4d4;
        padding: 15px;
        border-radius: 5px;
        overflow-x: auto;
        margin: 15px 0;
        font-family: "Courier New", monospace;
        font-size: 0.9em;
        line-height: 1.5;
      }

      pre code {
        background: none;
        padding: 0;
        color: inherit;
      }

      ul,
      ol {
        margin: 15px 0 15px 25px;
      }

      li {
        margin-bottom: 8px;
      }

      .command {
        background: #e8f4f8;
        padding: 10px;
        border-left: 4px solid #667eea;
        margin: 10px 0;
        border-radius: 3px;
        font-family: "Courier New", monospace;
      }

      .model-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 10px;
        margin: 15px 0;
      }

      .model-item {
        background: #f0f4ff;
        padding: 10px 15px;
        border-radius: 5px;
        border: 1px solid #667eea;
        font-family: "Courier New", monospace;
        font-size: 0.9em;
      }

      .command-list {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 5px;
        margin: 15px 0;
      }

      .command-list table {
        width: 100%;
        border-collapse: collapse;
      }

      .command-list th,
      .command-list td {
        text-align: left;
        padding: 10px;
        border-bottom: 1px solid #ddd;
      }

      .command-list th {
        background: #667eea;
        color: white;
        font-weight: bold;
      }

      .command-list tr:hover {
        background: #e8f0ff;
      }

      .highlight {
        background: #fff3cd;
        padding: 15px;
        border-radius: 5px;
        margin: 15px 0;
        border-left: 4px solid #ffc107;
      }

      .footer {
        margin-top: 40px;
        padding-top: 20px;
        border-top: 2px solid #eee;
        text-align: center;
        color: #666;
        font-size: 0.9em;
      }

      a {
        color: #667eea;
        text-decoration: none;
      }

      a:hover {
        text-decoration: underline;
      }
    </style>

  </head>
  <body>
    <div class="container">
      <h1>🤖 LangGraph Chatbot with Groq API</h1>
      <p class="subtitle">
        A fully functional chatbot built with LangGraph that uses Groq API and
        maintains conversation context/memory.
      </p>

      <h2>✨ Features</h2>
      <div class="features">
        <div class="feature-card">
          <strong>✅ Context Memory</strong>
          <p>Remembers entire conversation history across sessions</p>
        </div>
        <div class="feature-card">
          <strong>✅ Model Flexibility</strong>
          <p>Easily switch between different Groq models on the fly</p>
        </div>
        <div class="feature-card">
          <strong>✅ LangGraph Architecture</strong>
          <p>Modern, scalable architecture using state graphs</p>
        </div>
        <div class="feature-card">
          <strong>✅ Interactive Commands</strong>
          <p>Clear history, view history, change models dynamically</p>
        </div>
      </div>

      <h2>🚀 Setup Instructions</h2>

      <h3>1. Install Dependencies</h3>
      <p>Run the following command to install all required packages:</p>
      <div class="command">pip install -r requirements.txt</div>

      <h3>2. Configure API Key</h3>
      <p>Edit the <code>.env</code> file and add your Groq API key:</p>
      <pre><code>GROQ_API_KEY=your_actual_groq_api_key_here</code></pre>
      <div class="highlight">
        📌 Get your free Groq API key from:
        <a href="https://console.groq.com/" target="_blank"
          >https://console.groq.com/</a
        >
      </div>

      <h3>3. Run the Chatbot</h3>
      <div class="command">python chatbot.py</div>

      <h2>📊 Available Models</h2>
      <p>You can use any of these Groq models:</p>
      <div class="model-grid">
        <div class="model-item">llama3-8b-8192</div>
        <div class="model-item">llama3-70b-8192</div>
        <div class="model-item">mixtral-8x7b-32768</div>
        <div class="model-item">gemma-7b-it</div>
        <div class="model-item">gemma2-9b-it</div>
        <div class="model-item">llama-3.3-70b-versatile</div>
      </div>

      <h2>⌨️ Commands</h2>
      <div class="command-list">
        <table>
          <thead>
            <tr>
              <th>Command</th>
              <th>Description</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><code>/clear</code></td>
              <td>Clear conversation history</td>
            </tr>
            <tr>
              <td><code>/history</code></td>
              <td>Show conversation history</td>
            </tr>
            <tr>
              <td><code>/model &lt;name&gt;</code></td>
              <td>Change model (e.g., /model mixtral-8x7b-32768)</td>
            </tr>
            <tr>
              <td><code>/quit</code></td>
              <td>Exit the chatbot</td>
            </tr>
          </tbody>
        </table>
      </div>

      <h2>💬 Example Usage</h2>
      <pre><code>You: Hello! What's your name?

Bot: Hello! I'm an AI assistant powered by LangGraph...

You: What's 25 + 17?
Bot: 25 + 17 equals 42.

You: What was the math problem I just asked?
Bot: You asked me to calculate 25 + 17...

You: /model mixtral-8x7b-32768
Model changed to: mixtral-8x7b-32768

You: /quit
👋 Goodbye!</code></pre>

      <h2>📁 Project Structure</h2>
      <ul>
        <li><code>chatbot.py</code> - Main chatbot implementation</li>
        <li><code>.env</code> - Environment variables (API keys)</li>
        <li><code>requirements.txt</code> - Python dependencies</li>
        <li><code>README.html</code> - This documentation</li>
      </ul>

      <h2>🔧 How It Works</h2>
      <p>The chatbot uses the following components:</p>
      <ol>
        <li>
          <strong>LangGraph</strong> - Framework for building state-based LLM
          applications
        </li>
        <li>
          <strong>ChatGroq</strong> - Groq API integration for fast LLM
          inference
        </li>
        <li>
          <strong>MemorySaver</strong> - LangGraph's built-in checkpointer for
          conversation memory
        </li>
        <li>
          <strong>StateGraph</strong> - Manages the chatbot's processing flow
        </li>
      </ol>

      <div class="highlight">
        💡 The architecture allows you to switch models or even LLM providers
        with minimal code changes!
      </div>

      <div class="footer">
        <p>Built with ❤️ using LangGraph and Groq API</p>
        <p>
          Repository:
          <a href="https://github.com/sanwadR/full-chatbot" target="_blank"
            >https://github.com/sanwadR/full-chatbot</a
          >
        </p>
      </div>
    </div>

  </body>
</html>
