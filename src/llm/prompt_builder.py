from pathlib import Path


class PromptBuilder:

    def __init__(self):

        self.system_prompt = Path(
            "../prompts/system_prompt.txt"
        ).read_text(
            encoding="utf-8"
        )

    def build(
        self,
        issue,
        project_context="",
        comments=""
    ):

        return f"""
{self.system_prompt}

----------------------------------------
ISSUE
----------------------------------------

Title:
{issue.title}

Description:
{issue.body}

----------------------------------------
COMMENTS
----------------------------------------

{comments}

----------------------------------------
PROJECT CONTEXT
----------------------------------------

{project_context}

----------------------------------------
TASK
----------------------------------------

Analyze the issue and propose the required code changes.
Return detailed implementation instructions.
"""
