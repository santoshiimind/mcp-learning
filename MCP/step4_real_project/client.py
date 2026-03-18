import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("Connected to WeatherNotes MCP Server!\n")

            # ── Discover everything ──────────────────────
            tools     = await session.list_tools()
            resources = await session.list_resources()
            prompts   = await session.list_prompts()

            print(f"Tools     ({len(tools.tools)}): {[t.name for t in tools.tools]}")
            print(f"Resources ({len(resources.resources)}): {[str(r.uri) for r in resources.resources]}")
            print(f"Prompts   ({len(prompts.prompts)}): {[p.name for p in prompts.prompts]}")
            print()

            # ── TOOLS: add some notes ────────────────────
            print("=== TOOLS ===")
            r = await session.call_tool("add_note", {"title": "Buy groceries", "body": "Milk, Eggs, Coffee"})
            print("add_note =>", r.content[0].text)

            r = await session.call_tool("add_note", {"title": "Call dentist", "body": "Book appointment for next week"})
            print("add_note =>", r.content[0].text)

            r = await session.call_tool("get_weather", {"city": "London"})
            print("\nget_weather(London) =>")
            print(r.content[0].text)
            print()

            # ── RESOURCES: read notes ────────────────────
            print("=== RESOURCES ===")
            r = await session.read_resource("notes://all")
            print("notes://all =>")
            print(r.contents[0].text)
            print()

            r = await session.read_resource("notes://1")
            print("notes://1 =>")
            print(r.contents[0].text)
            print()

            # ── PROMPTS: daily briefing ───────────────────
            print("=== PROMPTS ===")
            r = await session.get_prompt("daily_briefing", {"city": "Tokyo"})
            # Extract just the text content from the prompt message
            msg_content = r.messages[0].content
            text = msg_content.text if hasattr(msg_content, "text") else str(msg_content)
            print("daily_briefing(Tokyo) =>")
            print(text)


if __name__ == "__main__":
    asyncio.run(main())
