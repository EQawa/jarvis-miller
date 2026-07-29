import logging

from ollama import chat  # ty:ignore[unresolved-import]

from src.config.settings import OLLAMA_MODEL


class OllamaClient:

    def __init__(
        self,
        model: str = OLLAMA_MODEL
    ):

        self.model = model

    def generate(
        self,
        prompt: str,
        temperature: float = 0.2
    ) -> str:

        try:

            response = chat(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                options={
                    "temperature": temperature
                }
            )

            return response["message"]["content"]

        except Exception as e:

            logging.exception(
                "Ollama request failed"
            )

            raise e

    def chat(
        self,
        messages: list,
        temperature: float = 0.2
    ) -> str:

        try:

            response = chat(
                model=self.model,
                messages=messages,
                options={
                    "temperature": temperature
                }
            )

            return response["message"]["content"]

        except Exception as e:

            logging.exception(
                "Ollama chat failed"
            )

            raise e

    def is_available(self) -> bool:

        try:

            chat(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": "ping"
                    }
                ]
            )

            return True

        except Exception:

            return False