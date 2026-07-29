from llm.prompt_builder import PromptBuilder
from llm.ollama_client import OllamaClient  # ty:ignore[unresolved-import]


class Agent:

    def __init__(self):

        self.ollama = OllamaClient()
        self.prompt_builder = PromptBuilder()

    def solve_issue(self, issue, repo_path):

        prompt = self.prompt_builder.build(
            issue,
            repo_path
        )

        return self.ollama.generate(
            prompt
        )