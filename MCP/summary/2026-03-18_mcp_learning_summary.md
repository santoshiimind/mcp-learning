# MCP Learning Summary
**Date:** 18 March 2026

---

## What is MCP?
Model Context Protocol (MCP) is an open standard by Anthropic that lets AI models
like Claude connect to external tools, data sources, and services in a standardized way.

> Think of it like a USB standard — one universal plug for AI + tools.

---

## Architecture
```
MCP Client (Claude Desktop)  <──JSON-RPC 2.0 over stdio──>  MCP Server (your Python script)
```

Claude Desktop spawns your Python script as a child process and communicates
by sending JSON messages through stdin/stdout.

---

## 3 Core Primitives

| Primitive | Purpose | REST Equivalent |
|-----------|---------|-----------------|
| Tools     | AI calls these to DO things | POST / PUT / DELETE |
| Resources | AI reads these to KNOW things | GET |
| Prompts   | Reusable prompt templates for the AI | Saved workflows |

---

## What Was Built (Step by Step)

### Step 1 — Hello World (Tools)
- File: `step1_hello_world/server.py`
- Built a calculator MCP server with `add` and `multiply` tools
- Learned: `@mcp.tool()` decorator, `FastMCP`, `mcp.run(transport="stdio")`

### Step 2 — Resources
- File: `step2_resources/server.py`
- Exposed notes data via `notes://all` and `notes://{note_id}` URIs
- Learned: `@mcp.resource("uri")`, dynamic URI parameters, Resources vs Tools

### Step 3 — Prompts
- File: `step3_prompts/server.py`
- Added `summarize_notes()` and `note_action_guide(action)` prompts
- Learned: `@mcp.prompt()`, `PromptMessage`, `TextContent`, prompt arguments

### Step 4 — Real Project (Weather + Notes)
- File: `step4_real_project/server.py`
- Built a full MCP server with:
  - Live weather via Open-Meteo API (free, no API key)
  - Persistent notes stored in notes.json
  - All 3 primitives: Tools + Resources + Prompts
- Tools: `get_weather`, `add_note`, `update_note`, `delete_note`
- Resources: `notes://all`, `notes://{id}`, `weather://{city}`
- Prompts: `daily_briefing(city)`, `summarize_notes()`

### Step 5 — Connected to Claude Desktop
- Edited: `C:/Users/SANTOSH/AppData/Roaming/Claude/claude_desktop_config.json`
- Added `weather-notes` server config with Python path and server script path
- Verified via MCP logs at: `C:/Users/SANTOSH/AppData/Roaming/Claude/logs/mcp-server-weather-notes.log`

---

## How Claude Desktop Communicates with MCP

1. Claude Desktop reads `claude_desktop_config.json`
2. Spawns `python.exe server.py` as a subprocess
3. Sends JSON-RPC 2.0 messages via stdin
4. Server processes and responds via stdout
5. Claude uses the response to answer the user

---

## Key Code Patterns

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ServerName")

@mcp.tool()
def my_tool(param: str) -> str:
    """Tool description shown to AI."""
    return "result"

@mcp.resource("data://{id}")
def my_resource(id: str) -> str:
    """Resource description."""
    return "data"

@mcp.prompt()
def my_prompt(arg: str) -> list[PromptMessage]:
    """Prompt description."""
    return [PromptMessage(role="user", content=TextContent(type="text", text=arg))]

mcp.run(transport="stdio")
```

---

## Packages Used
- `mcp` — MCP Python SDK
- `httpx` — HTTP client for weather API calls

---

## Project Structure
```
MCP/
├── step1_hello_world/      Tools only
├── step2_resources/        Tools + Resources
├── step3_prompts/          Tools + Resources + Prompts
├── step4_real_project/     Full real project
│   ├── server.py
│   ├── client.py
│   └── notes.json
└── summary/
    └── 2026-03-18_mcp_learning_summary.md
```
