from mcp.server import Server
import mcp.types as types

# Define available prompts
PROMPTS = {
    "describeEmails":types.Prompt(
        name="describeEmail",
        description="Summarize a given email",
        arguments=[
            types.PromptArgument(
                name="content",
                description="content of the email",
                required=True
            )
        ],
    ),
    "describeMany": types.Prompt(
        name="describeMany",
        description="Summarize multiple emails",
        arguments=[
            types.PromptArgument(
                name="data",
                description="List of email data to summarize",
                required=True
            )
        ]
    )
}

