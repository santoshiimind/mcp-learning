from mcp.server.fastmcp import FastMCP

mcp = FastMCP("NotesApp")

# Simulated in-memory "database" of notes
NOTES = {
    "1": {"title": "Meeting Notes", "body": "Discuss project timeline and deliverables."},
    "2": {"title": "Shopping List", "body": "Milk, Eggs, Bread, Butter."},
    "3": {"title": "Ideas",         "body": "Build an MCP server for weather data."},
}


# --- RESOURCES ---
# Resources expose data the AI can READ (like GET endpoints in REST)

@mcp.resource("notes://all")
def get_all_notes() -> str:
    """Returns a summary list of all notes."""
    lines = []
    for note_id, note in NOTES.items():
        lines.append(f"[{note_id}] {note['title']}")
    return "\n".join(lines)


@mcp.resource("notes://{note_id}")
def get_note(note_id: str) -> str:
    """Returns the full content of a specific note by ID."""
    note = NOTES.get(note_id)
    if not note:
        return f"Note '{note_id}' not found."
    return f"Title: {note['title']}\n\nBody: {note['body']}"


# --- TOOLS ---
# Tools can MODIFY data (like POST/PUT/DELETE in REST)

@mcp.tool()
def add_note(title: str, body: str) -> str:
    """Add a new note."""
    new_id = str(max(int(k) for k in NOTES.keys()) + 1)
    NOTES[new_id] = {"title": title, "body": body}
    return f"Note created with ID: {new_id}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
