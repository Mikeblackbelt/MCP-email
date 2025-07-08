from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
import mail
from mcp.server import Server
import mcp.types as types
import prompts
import asyncio

PROMPTS = prompts.PROMPTS

# Initialize FastMCP server
mcp = FastMCP("EmailWriter")

# Register the list_prompts function directly
def list_prompts() -> list[types.Prompt]:
    return list(PROMPTS.values())

@mcp.get_prompt
def get_prompt(
    name: str, arguments: dict[str, str] | None = None
) -> types.GetPromptResult:
    if name not in PROMPTS:
        raise ValueError(f"Prompt not found: {name}")

    if name == "describeEmail":
        content = arguments.get("content") if arguments else ""
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Please summarize the following email content:\n\n{content}"
                    )
                )
            ]
        )
    
    if name == "describeMany":
        data = arguments.get("data") if arguments else ""
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Please summarize the following emails, and return the most important information:\n{data}"
                    )
                )
            ]
        )

    raise ValueError("Prompt implementation not found")

@mcp.tool("dscribeEmail")
def describe_all():
    data = asyncio.run([mail.parse_email(mail.fetch_mail_by_id(email_id)) for email_id in mail.email_ids])
    return get_prompt(
        name="describeMany",
        arguments={"data": str(data)}
    )

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')