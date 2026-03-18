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
            print("Connected!\n")

            # 1. List all prompts
            prompts = await session.list_prompts()
            print("Available prompts:")
            for p in prompts.prompts:
                args = [a.name for a in p.arguments] if p.arguments else []
                print(f"  - {p.name}({', '.join(args)}): {p.description}")
            print()

            # 2. Get the 'summarize_notes' prompt (no arguments)
            result = await session.get_prompt("summarize_notes", {})
            print("Prompt: summarize_notes")
            print("-" * 40)
            print(result.messages[0].content.text)
            print()

            # 3. Get the 'note_action_guide' prompt (with an argument)
            result = await session.get_prompt("note_action_guide", {"action": "delete"})
            print("Prompt: note_action_guide(action='delete')")
            print("-" * 40)
            print(result.messages[0].content.text)
            print()

            # --- Review: all 3 primitives working together ---
            print("=" * 40)
            print("All 3 MCP Primitives in action:")
            print("=" * 40)

            # Tool
            tool_result = await session.call_tool("add_note", {
                "title": "Step 3 Done",
                "body": "I learned Tools, Resources, and Prompts!"
            })
            print(f"[Tool]     add_note     => {tool_result.content[0].text}")

            # Resource
            res_result = await session.read_resource("notes://all")
            note_count = len(res_result.contents[0].text.strip().split("\n"))
            print(f"[Resource] notes://all   => {note_count} notes found")

            # Prompt
            prompt_result = await session.get_prompt("summarize_notes", {})
            preview = prompt_result.messages[0].content.text[:60]
            print(f"[Prompt]   summarize_notes => '{preview}...'")


if __name__ == "__main__":
    asyncio.run(main())
