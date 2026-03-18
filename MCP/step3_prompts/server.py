from mcp.server.fastmcp import FastMCP
from mcp.types import PromptMessage, TextContent

mcp = FastMCP("PromptDemo")

NOTES = {
    "1": {"title": "Meeting Notes", "body": "Discuss project timeline and deliverables."},
    "2": {"title": "Shopping List", "body": "Milk, Eggs, Bread, Butter."},
    "3": {"title": "Ideas",         "body": "Build an MCP server for weather data."},
}


# --- RESOURCES ---

@mcp.resource("notes://all")
def get_all_notes() -> str:
    """Returns a summary list of all notes."""
    return "\n".join(f"[{nid}] {n['title']}" for nid, n in NOTES.items())


@mcp.resource("notes://{note_id}")
def get_note(note_id: str) -> str:
    """Returns a specific note by ID."""
    note = NOTES.get(note_id)
    if not note:
        return f"Note '{note_id}' not found."
    return f"Title: {note['title']}\n\nBody: {note['body']}"


# --- TOOLS ---

@mcp.tool()
def add_note(title: str, body: str) -> str:
    """Add a new note."""
    new_id = str(max(int(k) for k in NOTES.keys()) + 1)
    NOTES[new_id] = {"title": title, "body": body}
    return f"Note created with ID: {new_id}"


@mcp.tool()
def delete_note(note_id: str) -> str:
    """Delete a note by ID."""
    if note_id not in NOTES:
        return f"Note '{note_id}' not found."
    del NOTES[note_id]
    return f"Note '{note_id}' deleted."


# --- PROMPTS ---
# Prompts are reusable message templates sent to the AI
# They can accept arguments to make them dynamic

@mcp.prompt()
def summarize_notes() -> list[PromptMessage]:
    """Prompt the AI to summarize all notes."""
    all_notes = "\n".join(f"[{nid}] {n['title']}: {n['body']}" for nid, n in NOTES.items())
    return [
        PromptMessage(
            role="user",
            content=TextContent(
                type="text",
                text=f"Here are all my notes:\n\n{all_notes}\n\nPlease summarize them in 2-3 sentences."
            )
        )
    ]


@mcp.prompt()
def note_action_guide(action: str) -> list[PromptMessage]:
    """Guide the AI to perform a specific action on notes (add/delete/list)."""
    return [
        PromptMessage(
            role="user",
            content=TextContent(
                type="text",
                text=(
                    f"I want to {action} a note.\n"
                    f"Available tools: add_note(title, body), delete_note(note_id).\n"
                    f"Available resources: notes://all, notes://{{note_id}}.\n"
                    f"Please help me {action} the note step by step."
                )
            )
        )
    ]


if __name__ == "__main__":
    mcp.run(transport="stdio")
