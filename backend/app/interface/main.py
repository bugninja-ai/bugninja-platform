import asyncio
import os

from bugninja import BugninjaClient, BugninjaConfig, BugninjaTask  # type: ignore
from rich import print as rich_print

BACPREP_NAVIGATION_PROMPT = """
Go to app.bacprep.ro/en, login to the platform via email authentication with the 
provided credentials and edit the name of the user based on the provided information. 
If successful log out and close the browser.
""".strip()


async def run_traversal() -> None:

    client = BugninjaClient(config=BugninjaConfig())

    task = BugninjaTask(
        description=BACPREP_NAVIGATION_PROMPT,
        max_steps=150,
        allowed_domains=["app.bacprep.ro"],
        secrets={
            "credential_email": os.getenv("BACPREP_MAIL_1"),
            "credential_password": os.getenv("BACPREP_LOGIN_PASSWORD_1"),
            "new_username": "kiskutya",
        },
    )
    result = await client.run_task(task)

    if result.success:
        rich_print(f"Task completed in {result.steps_completed} steps")
    else:
        rich_print(f"Task failed: {result.error.message}")

    rich_print(result)


if __name__ == "__main__":
    asyncio.run(run_traversal())
