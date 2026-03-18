import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    # Point to our server script
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            # 1. Initialize the connection
            await session.initialize()
            print("Connected to MCP server!\n")

            # 2. List all available tools
            tools = await session.list_tools()
            print("Available tools:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")
            print()

            # 3. Call the 'add' tool
            result = await session.call_tool("add", {"a": 10, "b": 25})
            print(f"add(10, 25) = {result.content[0].text}")

            # 4. Call the 'multiply' tool
            result = await session.call_tool("multiply", {"a": 6, "b": 7})
            print(f"multiply(6, 7) = {result.content[0].text}")


if __name__ == "__main__":
    asyncio.run(main())
