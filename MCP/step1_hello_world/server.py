from mcp.server.fastmcp import FastMCP

# Create the MCP server with a name
mcp = FastMCP("Calculator")


# --- TOOLS ---
# Tools are functions the AI can call to DO something

@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b


@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers together."""
    return a * b


if __name__ == "__main__":
    # Run the server using stdio transport (standard for MCP)
    mcp.run(transport="stdio")
