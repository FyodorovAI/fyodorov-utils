from openai import OpenAI as oai
from .agent import Agent

DEFAULT_MODEL: str = "gpt-3.5-turbo"

class OpenAI(Agent):
    tools: list = []
    rag: list = []
    model: str = DEFAULT_MODEL

    def __init__(self, api_key: str, model: str = DEFAULT_MODEL) -> str:
        super().__init__(api_key)
        self.client = oai(api_key=api_key)
        self.model = model

    def call(self, prompt: str = "", input: str = "", temperature: float = 0.0):
        print(f"[OpenAI] Calling OpenAI with prompt: {prompt}, input: {input}, temperature: {temperature}")
        if temperature > 2.0 or temperature < 0.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")

        response = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": input},
            ],
            temperature=temperature,
            model=self.model,
        )

        # Process the response as needed
        print(f"Response: {response}")
        answer = response.choices[0].message.content
        print(f"Answer: {answer}")
        return str(answer)