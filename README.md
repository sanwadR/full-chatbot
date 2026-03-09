I have now read every single file in the repository. Here is the complete, enterprise-grade technical documentation for the `sanwadR/full-chatbot` project.

---

# 📄 Technical Documentation — `full-chatbot`

**Document Title:** Software Technical Reference Document (TRD)
**Repository:** [sanwadR/full-chatbot](https://github.com/sanwadR/full-chatbot)
**Document Version:** 1.0.0
**Date:** 2026-03-09
**Author/Owner:** sanwadR
**Status:** Active / Production

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Technology Stack](#3-technology-stack)
4. [Repository Structure](#4-repository-structure)
5. [Module-by-Module Reference](#5-module-by-module-reference)
   - 5.1 [`main.py` — Core Chatbot Engine](#51-mainpy--core-chatbot-engine)
   - 5.2 [`app.py` — Chainlit Web Interface](#52-apppy--chainlit-web-interface)
   - 5.3 [`mcp_server.py` — MCP Weather/AQI Tool Server](#53-mcp_serverpy--mcp-weatheraqi-tool-server)
   - 5.4 [`dev/chatbot.py` — Legacy Prototype (Groq-based CLI)](#54-devchatbotpy--legacy-prototype-groq-based-cli)
   - 5.5 [`dev/toolcall.py` — Legacy Tool-Call Prototype](#55-devtoolcallpy--legacy-tool-call-prototype)
6. [Data Flow & Execution Lifecycle](#6-data-flow--execution-lifecycle)
7. [API & Tool Reference (MCP Tools)](#7-api--tool-reference-mcp-tools)
8. [Environment Configuration](#8-environment-configuration)
9. [Dependencies](#9-dependencies)
10. [Containerization (Docker)](#10-containerization-docker)
11. [CI/CD Pipeline](#11-cicd-pipeline)
12. [Commands Reference](#12-commands-reference)
13. [Developer Guide — Local Setup](#13-developer-guide--local-setup)
14. [Known Limitations & Notes](#14-known-limitations--notes)
15. [Glossary](#15-glossary)

---

## 1. Project Overview

`full-chatbot` is a **production-ready, context-aware AI chatbot** built with the **LangGraph** framework. It exposes a browser-based chat UI (powered by [Chainlit](https://chainlit.io)) and integrates with external tools via the **Model Context Protocol (MCP)**. The chatbot leverages the **HuggingFace Inference Router** (OpenAI-compatible API) to execute a large language model (`Qwen/Qwen2.5-72B-Instruct` by default), and uses **OpenWeatherMap APIs** to answer real-time weather and air-quality queries through structured tool-calling.

### Key Capabilities

| Capability | Description |
|---|---|
| 🧠 **Persistent Conversation Memory** | Full conversation context retained per user session via LangGraph `MemorySaver` |
| 🔧 **Function / Tool Calling** | LLM autonomously decides when and which MCP tools to invoke |
| 🌤️ **Weather Intelligence** | Real-time weather, hourly/daily forecasts, AQI from OpenWeatherMap |
| 🌐 **Web UI** | Browser-based chat interface via Chainlit |
| 🐳 **Docker Support** | Fully containerized for portable deployment |
| 🚀 **Auto-Deploy** | GitHub Actions CI/CD pipeline deploys to HuggingFace Spaces on every merge to `main` |
| ⌨️ **CLI Mode** | Standalone terminal chatbot via `main.py` |
| 🔄 **Runtime Model Switching** | Change LLM model mid-conversation with `/model <name>` command |

---

## 2. System Architecture

### High-Level Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                       │
│         Browser (Chainlit Web App on port 7860)             │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTP / WebSocket
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                        app.py                               │
│  Chainlit Event Handlers                                    │
│  - on_chat_start()   → Bootstraps chatbot + MCP tools       │
│  - on_message()      → Routes user input → ChatbotWithMemory│
│  - Command parser    → /clear, /model                       │
└────────────────────────────┬────────────────────────────────┘
                             │ Python import
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                        main.py                              │
│  ChatbotWithMemory class                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  LangGraph StateGraph                               │   │
│  │  ┌──────────┐    tool_calls?    ┌──────────────┐   │   │
│  │  │ llm_node │ ───────────────► │  tool_node   │   │   │
│  │  │(HuggingF)│ ◄─────────────── │(MCP Adapter) │   │   │
│  │  └──────────┘  tool results    └──────────────┘   │   │
│  │  MemorySaver (in-process conversation state)       │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────┘
                             │ stdio subprocess (MCP protocol)
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                     mcp_server.py                           │
│  FastMCP weather-server (subprocess via stdio)              │
│  6 Tools:                                                   │
│  - geocode_city()           - get_weather_by_city()         │
│  - get_weather_by_coordinates() - get_hourly_forecast()     │
│  - get_daily_forecast()     - get_air_pollution()           │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTPS REST
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              OpenWeatherMap API                             │
│  /geo/1.0/direct  /data/2.5/weather  /data/3.0/onecall     │
│  /data/2.5/air_pollution                                    │
└─────────────────────────────────────────────────────────────┘
```

### Data / Control Flow Summary

1. User types a message in the Chainlit browser UI.
2. `app.py` receives it via `@cl.on_message` and calls `chatbot.chat(user_input)`.
3. `ChatbotWithMemory` prepends the `SystemMessage` + full conversation history and invokes the HuggingFace-hosted LLM (`llm_node`).
4. If the LLM response contains **tool_calls**, the graph routes to `tool_node`, which calls the appropriate MCP tool via `langchain_mcp_adapters`.
5. The MCP adapter communicates with `mcp_server.py` (running as a stdio subprocess), which makes REST calls to OpenWeatherMap.
6. Tool results are wrapped in `ToolMessage` objects and fed back to `llm_node`, which produces a final natural-language response.
7. The final response is streamed back to the Chainlit UI.

---

## 3. Technology Stack

| Layer | Technology | Version/Notes |
|---|---|---|
| **Language** | Python | 3.11 (pinned in Dockerfile) |
| **LLM Framework** | LangGraph | `langgraph` (latest) |
| **LLM Provider** | HuggingFace Inference Router | `https://router.huggingface.co/v1` (OpenAI-compat.) |
| **Default Model** | `Qwen/Qwen2.5-72B-Instruct` | Configurable at runtime |
| **LLM Client** | `langchain-openai` (`ChatOpenAI`) | Used with custom `base_url` |
| **Tool Protocol** | Model Context Protocol (MCP) | `mcp` + `langchain-mcp-adapters` |
| **MCP Server** | `FastMCP` | `mcp.server.fastmcp.FastMCP` |
| **Web UI** | Chainlit | `chainlit` |
| **Weather Data** | OpenWeatherMap API v2.5 / v3.0 | Requires `OPENWEATHERMAP_API_KEY` |
| **Memory** | LangGraph `MemorySaver` | In-process, per session |
| **Config** | `python-dotenv` | `.env` file |
| **Container** | Docker | `python:3.11-slim` base |
| **CI/CD** | GitHub Actions | Deploy to HuggingFace Spaces |
| **Linting** | flake8 | max-line-length=120 |
| **Dev/Legacy LLM** | ChatGroq | Used only in `dev/` prototypes |

---

## 4. Repository Structure

```
full-chatbot/
│
├── app.py                        # Chainlit web app — entry point for UI
├── main.py                       # ChatbotWithMemory class + CLI entry point
├── mcp_server.py                 # MCP Tool Server (weather + AQI tools)
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Container build definition
├── .env                          # ⚠️ SECRET — not committed (gitignored)
├── .gitignore                    # Git ignore rules
├── README.md                     # Project quickstart guide
│
├── .github/
│   └── workflows/
│       └── ci.yml                # GitHub Actions CI/CD pipeline
│
└── dev/                          # Development / prototype files (NOT production)
    ├── chatbot.py                # v1: Groq-based chatbot, no tool-calling
    └── toolcall.py               # v2: Groq-based chatbot with single weather tool
```

> **Note:** The `.env` file, `.chainlit/` directory, `venv/`, and Python cache artifacts are all gitignored and must be created locally.

---

## 5. Module-by-Module Reference

---

### 5.1 `main.py` — Core Chatbot Engine

**File:** [`main.py`](https://github.com/sanwadR/full-chatbot/blob/main/main.py)
**Purpose:** Contains the `ChatbotWithMemory` class — the brain of the application — and a standalone CLI entry point.

#### Class: `State` (TypedDict)

```python name=main.py url=https://github.com/sanwadR/full-chatbot/blob/main/main.py#L19-L20
class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
```

Defines the LangGraph state schema. The only field is `messages`, annotated with `add_messages` so LangGraph automatically appends new messages rather than replacing the entire list.

---

#### Class: `ChatbotWithMemory`

| Attribute | Type | Description |
|---|---|---|
| `model_name` | `str` | LLM model identifier. Default: `"Qwen/Qwen2.5-72B-Instruct"` |
| `temperature` | `float` | LLM temperature (0.0–1.0). Default: `0.7` |
| `session_id` | `str` | Thread ID for conversation memory. Default: `"default"` |
| `memory` | `MemorySaver` | LangGraph in-process checkpointer |
| `llm` | `ChatOpenAI` | LLM client pointing to HuggingFace router |
| `tools` | `dict[str, BaseTool]` | Lookup dict of MCP tools by name |
| `llm_with_tools` | `ChatOpenAI` (bound) | LLM with tool schemas registered |
| `system_message` | `SystemMessage` | Prepended to every LLM invocation |
| `graph` | `CompiledStateGraph` | Compiled LangGraph with `MemorySaver` checkpointer |

---

##### Method: `__init__(model_name, temperature, tools)`

Initializes the instance and calls `_build_graph()`. Accepts an optional list of `BaseTool` objects (MCP tools injected from `app.py` or `main()`).

---

##### Method: `_build_graph(tools)`

Builds and compiles the LangGraph `StateGraph`. Contains three internal functions:

**`llm_node(state)`** — Synchronous node
- Prepends `system_message` to conversation history
- Invokes `llm_with_tools`
- Returns updated message list
- Prints diagnostics to stdout

**`tool_node(state)`** — Asynchronous node
- Reads `tool_calls` from the last LLM message
- Calls each tool via `await self.tools[name].ainvoke(args)`
- Handles MCP's `[{'type': 'text', 'text': '...'}]` response format
- Wraps results in `ToolMessage` objects

**`should_continue(state)`** — Conditional edge router
- Returns `"tool_node"` if the last message has `tool_calls`
- Returns `END` if the LLM is done

**Graph topology:**
```
START → llm_node → (conditional) → tool_node → llm_node → ... → END
```

---

##### Method: `async chat(user_input) → str`

Main conversation method. Wraps `user_input` in a `HumanMessage`, invokes the compiled graph with `thread_id=session_id`, and returns the last message's content.

---

##### Method: `clear_memory()`

Generates a new random `session_id` using `os.urandom(8).hex()`, effectively starting a blank conversation (old thread remains in MemorySaver but is abandoned).

---

##### Method: `change_model(model_name)`

Updates `self.model_name` and calls `_build_graph()` with the existing tools, seamlessly swapping the LLM mid-conversation.

---

##### Function: `async main()`

CLI entry point. Boots an `MultiServerMCPClient`, loads MCP tools, creates a `ChatbotWithMemory`, then runs an `input()` loop supporting `/quit`, `/clear`, and `/model <name>` commands.

---

### 5.2 `app.py` — Chainlit Web Interface

**File:** [`app.py`](https://github.com/sanwadR/full-chatbot/blob/main/app.py)
**Purpose:** Exposes the chatbot as a web application using the Chainlit framework.

#### Configuration: `MCP_CONFIG`

```python name=app.py url=https://github.com/sanwadR/full-chatbot/blob/main/app.py#L17-L23
MCP_CONFIG = {
    "weather": {
        "command": sys.executable,
        "args": [os.path.join(_HERE, "mcp_server.py")],
        "transport": "stdio",
    }
}
```

Instructs `MultiServerMCPClient` to launch `mcp_server.py` as a subprocess using the same Python interpreter, communicating over **stdio**. This design ensures:
- No network port conflicts
- `mcp_server.py` always finds `.env` relative to its own directory (`_HERE`)
- One MCP subprocess per Chainlit user session

---

#### Handler: `@cl.on_chat_start → on_chat_start()`

Triggered when a user opens the chat UI. Steps:
1. Creates a `MultiServerMCPClient` and calls `await client.get_tools()` to discover all 6 MCP tools.
2. Instantiates `ChatbotWithMemory(tools=tools)`.
3. Stores the chatbot in `cl.user_session` so it persists across messages.
4. Sends a formatted welcome message listing all available tool capabilities and commands.

---

#### Handler: `@cl.on_message → on_message(message)`

Triggered on every user message. Steps:
1. Retrieves the `ChatbotWithMemory` from the session store.
2. **Command routing:**
   - `/clear` → calls `chatbot.clear_memory()`, replies with confirmation
   - `/model <name>` → calls `chatbot.change_model(name)`, replies with confirmation
3. For regular messages: opens a Chainlit `Step` (displays a "Thinking..." indicator), calls `await chatbot.chat(user_input)`, then sends the response.

---

### 5.3 `mcp_server.py` — MCP Weather/AQI Tool Server

**File:** [`mcp_server.py`](https://github.com/sanwadR/full-chatbot/blob/main/mcp_server.py)
**Purpose:** Standalone MCP server process that exposes 6 weather tools over stdio. It is launched as a subprocess by `app.py` / `main.py` and communicates via the MCP protocol.

#### Initialization

```python name=mcp_server.py url=https://github.com/sanwadR/full-chatbot/blob/main/mcp_server.py#L14-L18
mcp = FastMCP("weather-server")
OWM_KEY = os.getenv("OPENWEATHERMAP_API_KEY", "").strip()
OWM_BASE = "https://api.openweathermap.org"
```

- `FastMCP("weather-server")` — registers the server with the name `weather-server`
- `OWM_KEY` — read from `.env`, used in all API calls
- All HTTP requests use `requests.get(url, timeout=10)` with a 10-second timeout

#### Internal Helper: `_log(msg)`

Writes debug/trace messages to **stderr** to avoid corrupting the MCP stdout transport channel.

#### Internal Helper: `_geocode(city) → (lat, lon, name) | None`

Calls `GET /geo/1.0/direct?q={city}&limit=1` to resolve a city name to coordinates. Returns a `(lat, lon, resolved_name)` tuple or `None` on failure. Used by tools 4, 5, and 6 to convert city names before calling coordinate-based endpoints.

---

### 5.4 `dev/chatbot.py` — Legacy Prototype (Groq-based CLI)

**File:** [`dev/chatbot.py`](https://github.com/sanwadR/full-chatbot/blob/main/dev/chatbot.py)
**Purpose:** First-generation prototype. Uses `ChatGroq` (Groq API) instead of HuggingFace. Has no tool-calling — pure conversational LLM with `MemorySaver`. Demonstrates the foundational `StateGraph` pattern.

> ⚠️ **Not used in production.** For reference and historical context only.

**Key differences from `main.py`:**
- Uses `ChatGroq` with `GROQ_API_KEY`
- Default model: `llama3-8b-8192`
- No tool nodes in the graph — single `chatbot_node` only
- `chat()` is synchronous (not `async`)
- Includes a `get_conversation_history()` method (absent in production version)

---

### 5.5 `dev/toolcall.py` — Legacy Tool-Call Prototype

**File:** [`dev/toolcall.py`](https://github.com/sanwadR/full-chatbot/blob/main/dev/toolcall.py)
**Purpose:** Second-generation prototype. Adds weather tool-calling to the Groq-based chatbot. Uses the free **Open-Meteo API** (no API key required) instead of OpenWeatherMap.

> ⚠️ **Not used in production.** Illustrates the evolution from no-tools → inline tool → MCP-based tools.

**Key differences from `main.py`:**
- Uses `ChatGroq` with `GROQ_API_KEY`
- Default model: `llama-3.3-70b-versatile`
- Single `get_weather` tool defined inline with `@tool` decorator (not MCP)
- Uses `https://geocoding-api.open-meteo.com` and `https://api.open-meteo.com` (free, no key)
- Only current weather — no forecasts or AQI

---

## 6. Data Flow & Execution Lifecycle

### Web UI Flow (via `chainlit run app.py`)

```
Browser connects
    └─► on_chat_start()
            ├─ MultiServerMCPClient spawns mcp_server.py subprocess
            ├─ client.get_tools() → [geocode_city, get_weather_by_city, ...]
            ├─ ChatbotWithMemory(tools=tools) builds LangGraph
            └─ Welcome message sent to user

User types: "What's the weather in Paris?"
    └─► on_message(message)
            ├─ chatbot.chat("What's the weather in Paris?")
            │       ├─ HumanMessage added to state
            │       ├─ llm_node: LLM invoked with system + history
            │       │       └─ LLM response has tool_call: get_weather_by_city(city="Paris")
            │       ├─ should_continue → "tool_node"
            │       ├─ tool_node: calls mcp adapter → mcp_server.py
            │       │       └─ mcp_server calls GET /data/2.5/weather?q=Paris
            │       │       └─ returns "Current weather in Paris, FR: ..."
            │       ├─ ToolMessage added to state
            │       ├─ llm_node: LLM invoked again with tool result
            │       │       └─ LLM returns final natural-language response
            │       └─ should_continue → END
            └─ Response string sent to Chainlit UI
```

### CLI Flow (via `python main.py`)

Same logic, but:
- Input/output is terminal `input()` / `print()`
- No session isolation (single `session_id = "default"`)
- Runs inside `asyncio.run(main())`

---

## 7. API & Tool Reference (MCP Tools)

All tools are registered with `@mcp.tool()` in `mcp_server.py` and exposed via the MCP protocol. All return `str`.

---

### Tool 1 — `geocode_city`

| Property | Value |
|---|---|
| **Signature** | `geocode_city(city: str) → str` |
| **Description** | Returns latitude, longitude, and resolved name for a city |
| **OWM Endpoint** | `GET /geo/1.0/direct?q={city}&limit=1&appid={key}` |
| **Example Input** | `city="Paris"` |
| **Example Output** | `"Paris: latitude=48.8566, longitude=2.3522"` |
| **Error Handling** | Returns `"Could not find location: {city}"` if API returns empty list |

---

### Tool 2 — `get_weather_by_city`

| Property | Value |
|---|---|
| **Signature** | `get_weather_by_city(city: str) → str` |
| **Description** | Current weather conditions for a city by name |
| **OWM Endpoint** | `GET /data/2.5/weather?q={city}&appid={key}&units=metric` |
| **Returns** | Condition, Temperature (°C), Feels Like, Humidity (%), Wind Speed (m/s), Visibility (km) |
| **Error Handling** | Returns API error message if `cod != 200` |

---

### Tool 3 — `get_weather_by_coordinates`

| Property | Value |
|---|---|
| **Signature** | `get_weather_by_coordinates(lat: float, lon: float) → str` |
| **Description** | Current weather conditions for a lat/lon coordinate pair |
| **OWM Endpoint** | `GET /data/2.5/weather?lat={lat}&lon={lon}&appid={key}&units=metric` |
| **Returns** | Condition, Temperature, Feels Like, Humidity, Wind Speed |
| **Error Handling** | Returns API error message if `cod != 200` |

---

### Tool 4 — `get_hourly_forecast`

| Property | Value |
|---|---|
| **Signature** | `get_hourly_forecast(city: str, hours: int = 24) → str` |
| **Description** | Hourly weather forecast for a city |
| **OWM Endpoint** | `GET /data/3.0/onecall?lat&lon&exclude=minutely,daily,alerts` |
| **Constraint** | `hours` clamped to `[1, 48]` |
| **Returns** | Tabular list: `YYYY-MM-DD HH:00 UTC | Temp°C | Description | Rain%` |
| **Prerequisite** | Internally calls `_geocode(city)` first |
| **Note** | Requires OWM **One Call API 3.0** subscription |

---

### Tool 5 — `get_daily_forecast`

| Property | Value |
|---|---|
| **Signature** | `get_daily_forecast(city: str, days: int = 7) → str` |
| **Description** | Daily weather forecast for a city |
| **OWM Endpoint** | `GET /data/3.0/onecall?lat&lon&exclude=minutely,hourly,alerts` |
| **Constraint** | `days` clamped to `[1, 8]` |
| **Returns** | Tabular list: `Date | Description | Day Temp | Min/Max | Humidity% | Rain%` |
| **Prerequisite** | Internally calls `_geocode(city)` first |
| **Note** | Requires OWM **One Call API 3.0** subscription |

---

### Tool 6 — `get_air_pollution`

| Property | Value |
|---|---|
| **Signature** | `get_air_pollution(city: str) → str` |
| **Description** | Air Quality Index (AQI) and pollutant concentrations |
| **OWM Endpoint** | `GET /data/2.5/air_pollution?lat={lat}&lon={lon}&appid={key}` |
| **Returns** | AQI label (Good/Fair/Moderate/Poor/Very Poor), CO, NO₂, O₃, PM2.5, PM10, SO₂, NH₃ (all μg/m³) |
| **AQI Scale** | 1=Good, 2=Fair, 3=Moderate, 4=Poor, 5=Very Poor |
| **Prerequisite** | Internally calls `_geocode(city)` first |

---

## 8. Environment Configuration

The application requires a `.env` file in the project root. This file is **gitignored** and must be created manually.

```ini name=.env
# HuggingFace Inference Router API Key
# Required by main.py for the production LLM
HUGGINGFACE_API_KEY=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# OpenWeatherMap API Key
# Required by mcp_server.py for all weather & AQI tools
OPENWEATHERMAP_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# (Legacy dev only) Groq API Key
# Only needed to run dev/chatbot.py or dev/toolcall.py
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

| Variable | Required By | Source |
|---|---|---|
| `HUGGINGFACE_API_KEY` | `main.py` | [HuggingFace Settings](https://huggingface.co/settings/tokens) |
| `OPENWEATHERMAP_API_KEY` | `mcp_server.py` | [OpenWeatherMap Console](https://home.openweathermap.org/api_keys) |
| `GROQ_API_KEY` | `dev/` only | [Groq Console](https://console.groq.com/) |

> ⚠️ **Security Note:** Never commit `.env` to version control. The `.gitignore` already excludes it. For GitHub Actions / HuggingFace Spaces deployment, use **GitHub Secrets** (`HF_TOKEN`) and **HuggingFace Space Secrets** for the API keys.

---

## 9. Dependencies

Full `requirements.txt`:

```pip-requirements name=requirements.txt url=https://github.com/sanwadR/full-chatbot/blob/main/requirements.txt
langchain-openai
langchain-core
langgraph
python-dotenv
typing-extensions
requests
chainlit
mcp
langchain-mcp-adapters
```

| Package | Purpose |
|---|---|
| `langchain-openai` | `ChatOpenAI` client (used with HuggingFace router) |
| `langchain-core` | Core message types (`HumanMessage`, `SystemMessage`, `ToolMessage`, `BaseTool`) |
| `langgraph` | State graph framework, `MemorySaver`, graph compilation |
| `python-dotenv` | Loads `.env` into `os.environ` |
| `typing-extensions` | `TypedDict` compatibility for Python 3.11 |
| `requests` | HTTP calls to OpenWeatherMap API (in `mcp_server.py`) |
| `chainlit` | Web UI framework — event handlers, sessions, streaming |
| `mcp` | Model Context Protocol SDK — `FastMCP`, stdio transport |
| `langchain-mcp-adapters` | Bridges MCP tools into LangChain `BaseTool` objects |

> **Note:** `langchain-groq` is **not** in `requirements.txt` — it is only used in `dev/` prototypes and must be installed separately if running those files.

---

## 10. Containerization (Docker)

```dockerfile name=Dockerfile url=https://github.com/sanwadR/full-chatbot/blob/main/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Expose Chainlit default port
EXPOSE 7860

# Run the Chainlit app
CMD ["chainlit", "run", "app.py", "--host", "0.0.0.0", "--port", "7860"]
```

| Property | Value |
|---|---|
| **Base Image** | `python:3.11-slim` |
| **Working Directory** | `/app` |
| **Exposed Port** | `7860` |
| **Entry Command** | `chainlit run app.py --host 0.0.0.0 --port 7860` |
| **Build Strategy** | Dependencies installed before copying source — leverages Docker layer caching |

### Build & Run Locally

```bash
# Build the image
docker build -t full-chatbot .

# Run with environment variables
docker run -p 7860:7860 \
  -e HUGGINGFACE_API_KEY=hf_xxx \
  -e OPENWEATHERMAP_API_KEY=owm_xxx \
  full-chatbot
```

Then open `http://localhost:7860` in your browser.

---

## 11. CI/CD Pipeline

**File:** [`.github/workflows/ci.yml`](https://github.com/sanwadR/full-chatbot/blob/main/.github/workflows/ci.yml)
**Platform:** GitHub Actions
**Target:** HuggingFace Spaces (`Sanwad/my-chatbot`)

### Triggers

| Event | Trigger Condition | Jobs Run |
|---|---|---|
| `push` to `main` | Changes to `app.py`, `main.py`, `mcp_server.py`, `requirements.txt`, or `Dockerfile` | `validate` + `deploy` |
| `pull_request` targeting `main` | Changes to those files + `chainlit.md` | `validate` only |

### Jobs

#### Job 1: `validate` — Lint & Validate

Runs on **all** triggered events (PRs and pushes).

| Step | Action |
|---|---|
| Checkout code | `actions/checkout@v4` |
| Set up Python 3.11 | `actions/setup-python@v5` |
| Install dependencies | `pip install -r requirements.txt` |
| Lint with flake8 | `flake8 app.py main.py mcp_server.py --max-line-length=120 --exit-zero` |
| Compile-check Python | `python -m py_compile app.py main.py mcp_server.py` |

> `--exit-zero` means linting warnings don't fail the build, but compile errors will.

#### Job 2: `deploy` — Deploy to HF Spaces

Runs **only** on `push` to `main` (never on PRs). Requires `validate` to pass first (`needs: validate`).

| Step | Action |
|---|---|
| Checkout code | `actions/checkout@v4` |
| Install HuggingFace Hub | `pip install huggingface_hub` |
| Configure git identity | Sets `ci-bot@github.com` as committer |
| Clone HF Space | `git clone https://user:$HF_TOKEN@huggingface.co/spaces/Sanwad/my-chatbot hf-space` |
| Copy production files | `app.py`, `main.py`, `mcp_server.py`, `requirements.txt`, `Dockerfile` |
| Commit & push | Only commits if there are changes (idempotent) |

**Required Secret:**

| Secret Name | Description |
|---|---|
| `HF_TOKEN` | HuggingFace access token with write access to the target Space |

---

## 12. Commands Reference

Available in both the **Web UI** (`app.py`) and **CLI** (`main.py`):

| Command | Description | Behavior |
|---|---|---|
| `/clear` | Clears conversation memory | Generates a new random `session_id`; LLM forgets all prior context |
| `/model <name>` | Switches the LLM model | Calls `change_model()` → rebuilds the LangGraph with the same tools |
| `/quit` | Exit the application | CLI only — exits the `asyncio` loop |

### Model Name Examples

| Model Name | Notes |
|---|---|
| `Qwen/Qwen2.5-72B-Instruct` | Default — 72B parameter Qwen model |
| `meta-llama/Llama-3.3-70B-Instruct` | Meta Llama 3.3 70B |
| `mistralai/Mixtral-8x7B-Instruct-v0.1` | Mixtral mixture-of-experts |
| Any model available on HuggingFace router | Check availability at `router.huggingface.co` |

---

## 13. Developer Guide — Local Setup

### Prerequisites

- Python 3.11+
- A HuggingFace account with an API token
- An OpenWeatherMap account with an API key (free tier supports current weather; One Call API 3.0 subscription needed for forecasts)
- Git

### Step-by-Step Setup

```bash
# 1. Clone the repository
git clone https://github.com/sanwadR/full-chatbot.git
cd full-chatbot

# 2. Create and activate a virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Install all dependencies
pip install -r requirements.txt

# 4. Create your .env file
cp .env.example .env  # (or create manually)
# Edit .env and add your keys:
# HUGGINGFACE_API_KEY=hf_...
# OPENWEATHERMAP_API_KEY=...

# 5a. Run the web UI (recommended)
chainlit run app.py
# Opens at http://localhost:8000 by default

# 5b. OR run the CLI version
python main.py
```

### Running Dev Prototypes

```bash
# Install additional dependency
pip install langchain-groq

# Add GROQ_API_KEY to .env

# Run legacy CLI chatbot (no tools)
python dev/chatbot.py

# Run legacy tool-call chatbot
python dev/toolcall.py
```

### Project-Specific Linting

```bash
pip install flake8
flake8 app.py main.py mcp_server.py --max-line-length=120
```

---

## 14. Known Limitations & Notes

| # | Limitation / Note | Detail |
|---|---|---|
| 1 | **In-memory only** | `MemorySaver` stores conversation state in RAM. Restarting the server clears all history for all users. For persistence, replace with `SqliteSaver` or `PostgresSaver`. |
| 2 | **Single session per CLI run** | The CLI `main.py` uses `session_id = "default"` — only one conversation thread. Web UI is per-user via Chainlit sessions. |
| 3 | **One Call API 3.0 required for forecasts** | `get_hourly_forecast` and `get_daily_forecast` call `/data/3.0/onecall` which requires a paid OWM subscription beyond the free tier. |
| 4 | **MCP server one-per-session** | A new `mcp_server.py` subprocess is spawned for every Chainlit user session (`on_chat_start`). Under high concurrency, this could be resource-intensive. |
| 5 | **`dev/` files not production-ready** | `dev/chatbot.py` and `dev/toolcall.py` use `GROQ_API_KEY`, not in `requirements.txt`. They are retained for educational/historical purposes. |
| 6 | **No authentication on the web UI** | Chainlit's default mode has no login. Anyone who can reach port 7860 can use the chatbot. Add Chainlit authentication for public deployments. |
| 7 | **Model availability** | The `/model` command does not validate the model name. Providing an unavailable model will cause a runtime error on the next message. |
| 8 | **`--exit-zero` in linting** | The CI flake8 step uses `--exit-zero`, meaning style warnings never fail the pipeline. |
| 9 | **Temperature not exposed via command** | The `/model` command only switches model name. Temperature cannot be changed at runtime in the current implementation. |

---

## 15. Glossary

| Term | Definition |
|---|---|
| **LangGraph** | A framework built on LangChain for constructing stateful, cyclic LLM applications using directed graphs. |
| **StateGraph** | LangGraph's core primitive — a graph where nodes process the state and edges determine routing. |
| **MemorySaver** | LangGraph's in-memory checkpointer that persists conversation state per `thread_id`. |
| **MCP (Model Context Protocol)** | An open protocol (by Anthropic) for connecting LLMs to external tools/resources over a standardized interface. |
| **FastMCP** | A high-level MCP server SDK that lets you register Python functions as tools with a decorator. |
| **stdio transport** | MCP communication mode where the client launches the server as a subprocess and communicates via stdin/stdout. |
| **Tool Calling / Function Calling** | The ability of an LLM to emit structured requests to call external functions, which are then executed and the results fed back to the LLM. |
| **`tool_calls`** | A field in an LLM's response message containing a list of function calls the model wants to make. |
| **ToolMessage** | A LangChain message type used to return the result of a tool call back to the LLM. |
| **Chainlit** | A Python framework for building production-ready chat UIs backed by LLMs, similar to Streamlit but specialized for chat. |
| **`cl.user_session`** | Chainlit's per-user in-memory store — each browser tab/user gets an isolated session. |
| **HuggingFace Spaces** | HuggingFace's hosting platform for ML demos and apps. Supports Docker-based deployments. |
| **One Call API 3.0** | OpenWeatherMap's premium API for hourly and daily forecast data (requires subscription). |
| **AQI** | Air Quality Index — a numerical scale measuring pollution levels. OWM uses 1 (Good) to 5 (Very Poor). |
| **`_HERE`** | A pattern used in both `app.py` and `mcp_server.py` — resolves the directory of the current file using `os.path.dirname(os.path.abspath(__file__))` — ensures correct `.env` resolution regardless of the working directory when the subprocess is launched. |

---

> 📁 **Repository:** [github.com/sanwadR/full-chatbot](https://github.com/sanwadR/full-chatbot)
