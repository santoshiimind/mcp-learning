# MCP Learning

A step-by-step hands-on guide to learning **Model Context Protocol (MCP)** by building real projects in Python.

## What is MCP?

Model Context Protocol (MCP) is an open standard by Anthropic that lets AI models like Claude connect to external tools, data sources, and services in a standardized way.

> Think of it like a USB standard — one universal plug for AI + tools.

## Architecture

```
MCP Client (Claude Desktop)  <── JSON-RPC 2.0 over stdio ──>  MCP Server (Python script)
```

## 3 Core Primitives

| Primitive | Purpose | Example |
|-----------|---------|---------|
| **Tools** | AI calls these to DO things | `get_weather(city)` |
| **Resources** | AI reads these to KNOW things | `notes://all` |
| **Prompts** | Reusable AI prompt templates | `daily_briefing(city)` |

---

## Project Structure

```
MCP/
├── step1_hello_world/      # Tools only
├── step2_resources/        # Tools + Resources
├── step3_prompts/          # Tools + Resources + Prompts
├── step4_real_project/     # Full real-world project
└── summary/                # Learning notes
```

---

## Step by Step

### Step 1 — Hello World (Tools)
A simple calculator MCP server with `add` and `multiply` tools.

```python
@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b
```

### Step 2 — Resources
Expose notes data via URI-based resources.

```python
@mcp.resource("notes://all")
def get_all_notes() -> str:
    """Returns a summary list of all notes."""
    ...

@mcp.resource("notes://{note_id}")
def get_note(note_id: str) -> str:
    """Returns a specific note by ID."""
    ...
```

### Step 3 — Prompts
Reusable prompt templates that guide the AI.

```python
@mcp.prompt()
def summarize_notes() -> list[PromptMessage]:
    """Prompt the AI to summarize all notes."""
    ...
```

### Step 4 — Real Project (Weather + Notes)
A full MCP server with:
- Live weather via [Open-Meteo API](https://open-meteo.com/) (free, no API key)
- Persistent notes stored in `notes.json`
- All 3 primitives: Tools + Resources + Prompts

**Tools:**
- `get_weather(city)` — Live weather for any city
- `add_note(title, body)` — Create a note
- `update_note(id, title, body)` — Edit a note
- `delete_note(id)` — Delete a note

**Resources:**
- `notes://all` — List all notes
- `notes://{id}` — Read a specific note
- `weather://{city}` — Weather as a resource

**Prompts:**
- `daily_briefing(city)` — Morning briefing with weather + notes
- `summarize_notes()` — Summarize all notes

---

## Getting Started

### 1. Install dependencies
```bash
pip install mcp httpx
```

### 2. Run the server (any step)
```bash
cd MCP/step4_real_project
python client.py
```

### 3. Connect to Claude Desktop
Add this to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "weather-notes": {
      "command": "python",
      "args": ["path/to/MCP/step4_real_project/server.py"]
    }
  }
}
```
Then restart Claude Desktop and look for the hammer icon in the chat input.

---

## How Claude Desktop Communicates with MCP

1. Claude Desktop reads `claude_desktop_config.json`
2. Spawns `python server.py` as a subprocess
3. Sends JSON-RPC 2.0 messages via **stdin**
4. Server processes and responds via **stdout**
5. Claude uses the response to answer the user

---

## Tech Stack
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [httpx](https://www.python-httpx.org/) — HTTP client
- [Open-Meteo](https://open-meteo.com/) — Free weather API

---

## Learning Date
18 March 2026
