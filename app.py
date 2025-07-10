"""import sys
import os

# Ensure correct Python environment
expected = os.path.join(os.getcwd(), "myenv", "Scripts", "python.exe")
if sys.executable.lower() != expected.lower():
    os.execv(expected, ["python.exe", __file__])
"""
import asyncio
from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
from mcp.server import Server
import mcp.types as types
import mail
import prompts
import sys
import json

PROMPTS = prompts.PROMPTS
loop = asyncio.get_event_loop()


# Initialize servers
mcp = FastMCP("EmailWriter")
server = Server("EmailWriterServer")

# Prompt registration
def list_prompts() -> list[types.Prompt]:
    return list(PROMPTS.values())

@server.get_prompt()
def get_prompt(name: str, arguments: dict[str, str] | None = None) -> types.GetPromptResult:
    if name not in PROMPTS:
        raise ValueError(f"Prompt not found: {name}")

    content = arguments.get("content") if arguments else ""
    data = arguments.get("data") if arguments else ""

    if name == "describeEmail":
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
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Please summarize the following emails, and return ONLY the most important information from the most important emails in 5 sentences or less TOTAL. Maximum character length is 1000. DO NOT YAP.:\n{data}"
                    )
                )
            ]
        )

    raise ValueError("Prompt implementation not found")

# email processing helper
def gather_emails():
    return [mail.parse_email(mail.fetch_mail_by_id(email_id)) for email_id in mail.email_ids]

@mcp.tool("describeEmail")  # corrected tool name
def describe_all():
    try:
        data = gather_emails()
        prompt = get_prompt(
         "describeMany",
         arguments={"data": json.dumps(data, indent=2)}
        )
        return prompt.messages[1].content.text[0:1000]
    

    except Exception as e:
        print(f"Error in describe_all: {e}", file=sys.stderr)
        raise


"""Error executing tool describeEmail: An asyncio.Future, a coroutine or an awaitable is required"""

"""
@mcp.tool("describeEmail")
def describe_all():
    try:
        import mail

        async def gather_emails():
            conn, ids = mail.get_email_ids()
            return await asyncio.gather(*[
                mail.parse_email(mail.fetch_mail_by_id(conn, email_id))
                for email_id in ids
            ])

        data = asyncio.run(gather_emails())
        return get_prompt(
            "describeMany",
            arguments={"data": str(data)}
        )
    except Exception as e:
        print(f"Error in describe_all: {e}", file=sys.stderr)
        raise
"""

# Entry point
if __name__ == "__main__":
    print("Starting EmailWriter server...", file=sys.stderr)
    mcp.run(transport='stdio')
