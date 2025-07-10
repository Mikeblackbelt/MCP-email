from mcp.server.fastmcp import FastMCP

mcp = FastMCP("TestTool")

@mcp.tool("hello")
def say_hello():
    return {"message": "Hello from MCP"}

if __name__ == "__main__":
    import sys
    print("Launching server...", file=sys.stderr)
    mcp.run(transport='stdio')
