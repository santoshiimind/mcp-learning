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

            # 1. List all available resources
            resources = await session.list_resources()
            print("Available resources:")
            for r in resources.resources:
                print(f"  - {r.uri}  =>  {r.description}")
            print()

            # 2. Read the "notes://all" resource
            result = await session.read_resource("notes://all")
            print("All notes (notes://all):")
            print(result.contents[0].text)
            print()

            # 3. Read a specific note by ID
            result = await session.read_resource("notes://2")
            print("Note #2 (notes://2):")
            print(result.contents[0].text)
            print()

            # 4. Use a Tool to add a new note
            result = await session.call_tool("add_note", {
                "title": "MCP Learning",
                "body": "Resources expose data. Tools perform actions."
            })
            print("Tool result:", result.content[0].text)
            print()

            # 5. Read all notes again to see the new one
            result = await session.read_resource("notes://all")
            print("All notes after adding:")
            print(result.contents[0].text)


if __name__ == "__main__":
    asyncio.run(main())
