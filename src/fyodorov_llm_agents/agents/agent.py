import os
import re
import requests
import queue
import threading
import json
import yaml
from pydantic import BaseModel
from openai import OpenAI as oai
from litellm import completion
from fyodorov_llm_agents.tools.tool import Tool

MAX_NAME_LENGTH = 80
MAX_DESCRIPTION_LENGTH = 280
VALID_CHARACTERS_REGEX = r'^[a-zA-Z0-9\s.,!?:;\'"-]+$'

class Agent(BaseModel):
    provider_id: str = None
    api_key: str = None
    tools: [Tool] = []
    rag: [] = []
    model: str = "gpt-3.5-turbo"
    name: str = "My Agent"
    description: str = "My Agent Description"
    prompt: str = "My Prompt"
    prompt_size: int = 10000

    class Config:
        arbitrary_types_allowed = True

    def validate(self):
        Agent.validate_name(self.name)
        Agent.validate_description(self.description)
        Agent.validate_prompt(self.prompt, self.prompt_size)

    @staticmethod
    def validate_name(name: str) -> str:
        if not name:
            raise ValueError('Name is required')
        if len(name) > MAX_NAME_LENGTH:
            raise ValueError('Name exceeds maximum length')
        if not re.match(VALID_CHARACTERS_REGEX, name):
            raise ValueError('Name contains invalid characters')
        return name

    @staticmethod
    def validate_description(description: str) -> str:
        if not description:
            raise ValueError('Description is required')
        if len(description) > MAX_DESCRIPTION_LENGTH:
            raise ValueError('Description exceeds maximum length')
        if not re.match(VALID_CHARACTERS_REGEX, description):
            raise ValueError('Description contains invalid characters')
        return description

    @staticmethod
    def validate_prompt(prompt: str, prompt_size: int) -> str:
        if not prompt:
            raise ValueError('Prompt is required')
        if len(prompt) > prompt_size:
            raise ValueError('Prompt exceeds maximum length')
        return prompt

    def to_dict(self) -> dict:
        return {
            'provider_id': self.provider_id,
            'model': self.model,
            'name': self.name,
            'description': self.description,
            'prompt': self.prompt,
            'prompt_size': self.prompt_size,
            'tools': self.tools,
            'rag': self.rag,
        }

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

    def invoke(self, prompt: str = "", input: str = "", temperature: float = 0.0, depth: int = 0) -> str:
        res = self.call(prompt, input, temperature)
        print("llm response:", res)
        if len(self.tools) > 0:
            print("Checking for tool usage in llm response...")
            tool_used, new_prompt = self.check_res_for_tools(res)
            print("tool used in llm response:", tool_used)
            if tool_used:
                print("tool used in llm response:", res)
                prompt += new_prompt
                return self.invoke(prompt, input)
            print("Checking for tool calls in llm response...")
            tool_called, new_prompt = self.check_res_for_calls(res)
            print("tool called in llm response:", tool_called)
            if tool_called:
                print("tool called in llm response:", res)
                print(f"new prompt: {new_prompt}")
                prompt += new_prompt
                return self.invoke(prompt, input)
        return res

    def streaming_call(self, result_queue):
        try:
            # Simulate defining multiple functions that the model can choose to call
            functions = [
                {
                    "name": "get_current_weather",
                    "description": "Get the current weather for a location",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {"type": "string"},
                            "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
                        },
                        "required": ["location"]
                    }
                },
                {
                    "name": "get_n_day_weather_forecast",
                    "description": "Get a weather forecast for a number of days",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {"type": "string"},
                            "num_days": {"type": "integer"},
                            "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
                        },
                        "required": ["location", "num_days"]
                    }
                }
            ]

            # Example request that could potentially trigger multiple function calls
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": "What's the weather today and the forecast for the next 4 days in San Francisco?"}
                ],
                functions=functions
            )

            # Process the response assuming it might include multiple tool calls
            if response.choices and len(response.choices) > 0:
                result_queue.put(f"array length of choices greater than 0")
                result_queue.put(f"response choices: {response.choices}")
                result_queue.put(f"response choice 1: {response.choices[0]}")
                if response.choices[0].finish_reason == 'function_call':
                    result_queue.put(f"response choice 1 finish reason: {response.choices[0].finish_reason}")
                    result_queue.put(f"response choice 1 function call: {response.choices[0].message.function_call}")
                    function_calls = {
                        "function_name": response.choices[0].message.function_call.name,
                        "function_args": response.choices[0].message.function_call.arguments
                    }
                    result_queue.put(json.dumps(function_calls))
                else:
                    answer = response.choices[0].message.content
                    result_queue.put(f"No function calls detected: {answer}")
            else:
                result_queue.put(f"response id: {response.id}")
                result_queue.put(f"response choices: {response.choices}")
                result_queue.put(f"response first choice: {response.choices[0]}")
                result_queue.put(f"response first choice finish reason: {response.choices[0].finish_reason}")
                result_queue.put(f"Invalid response format: {response}")
            
            result_queue.put(None)  # Signal the end of streaming
        except Exception as e:
            result_queue.put(str(e))
            result_queue.put(None)

    async def invoke_async(self, prompt: str = "", input: str = "", temperature: float = 0.0, depth: int = 0):
        result_queue = queue.Queue()
        thread = threading.Thread(target=self.streaming_call, args=(result_queue,))
        thread.start()

        while True:
            result = result_queue.get()
            try:
                result = json.loads(result)
            except Exception as e:
                print("Error parsing result to json:", str(e))
                continue
            if result is None:  # End of stream
                print("End of stream")
                break
            elif isinstance(result, dict) and "function_name" in result:
                print(f"Calling function: {result}")
                tool = next((t for t in self.tools if t.name_for_ai == result["function_name"]), None)
                if tool:
                    print(f"Found tool: {tool}")
                    res = tool.call(result["function_args"])
                    print(f"Result from tool: {res}")
                    yield res.encode()
                else:
                    print(f"Tool not found: {result['function_name']}")
                    yield result.encode()
            else:
                print(f"Result from stream: {result}")
                print(f"type of result: {type(result)}")
                yield result.encode()

    def call_with_fn_calling(self, prompt: str = "", input: str = ""):
        # Set environmental variable
        messages: [] = [
            {"content": prompt, "role": "system"},
            { "content": input, "role": "user"},
        ]
        response = completion(model=self.model, messages=messages, max_retries=0, api_key=self.api_key)
        print(f"Response: {response}")
        answer = response.choices[0].message.content
        print(f"Answer: {answer}")
        return {
            "answer": answer
        }

    @staticmethod
    def from_yaml(yaml_str: str):
        """Instantiate Agent from YAML."""
        if not yaml_str:
            raise ValueError('YAML string is required')
        agent_dict = yaml.safe_load(yaml_str)
        agent = Agent(**agent_dict)
        agent.validate()
        return agent
    
    def add_tool(self, tool: Tool):
        self.tools.append(tool)

    def check_res_for_tools(self, prompt) -> (bool, str):
        tool_used = False
        new_prompt = '''
        Here's how to call a tool (example between ``):`
        Thought:I need to use the Klarna Shopping API to search for t shirts.
        Action: requests_get
        Action Input: https://www.klarna.com/us/shopping/public/openai/v0/products?q=t%20shirts
        `
        The response will be in JSON format:`
        Observation: {"products":[{"name":"Lacoste Men's Pack of Plain T-Shirts","url":"https://www.klarna.com/us/shopping/pl/cl10001/3202043025/Clothing/Lacoste-Men-s-Pack-of-Plain-T-Shirts/?utm_source=openai","price":"$26.60","attributes":["Material:Cotton","Target Group:Man","Color:White,Black"]},{"name":"Hanes Men's Ultimate 6pk. Crewneck T-Shirts","url":"https://www.klarna.com/us/shopping/pl/cl10001/3201808270/Clothing/Hanes-Men-s-Ultimate-6pk.-Crewneck-T-Shirts/?utm_source=openai","price":"$13.82","attributes":["Material:Cotton","Target Group:Man","Color:White"]},{"name":"Nike Boy's Jordan Stretch T-shirts","url":"https://www.klarna.com/us/shopping/pl/cl359/3201863202/Children-s-Clothing/Nike-Boy-s-Jordan-Stretch-T-shirts/?utm_source=openai","price":"$14.99","attributes":["Material:Cotton","Color:White,Green","Model:Boy","Size (Small-Large):S,XL,L,M"]},{"name":"Polo Classic Fit Cotton V-Neck T-Shirts 3-Pack","url":"https://www.klarna.com/us/shopping/pl/cl10001/3203028500/Clothing/Polo-Classic-Fit-Cotton-V-Neck-T-Shirts-3-Pack/?utm_source=openai","price":"$29.95","attributes":["Material:Cotton","Target Group:Man","Color:White,Blue,Black"]},{"name":"adidas Comfort T-shirts Men's 3-pack","url":"https://www.klarna.com/us/shopping/pl/cl10001/3202640533/Clothing/adidas-Comfort-T-shirts-Men-s-3-pack/?utm_source=openai","price":"$14.99","attributes":["Material:Cotton","Target Group:Man","Color:White,Black","Neckline:Round"]}]}
        `'''
        for tool in self.tools:
            if f"Action: {tool.name_for_ai}" in prompt:
                print("[check_res_for_tools] tool use found:", tool.name_for_ai)
                new_prompt += f"OpenAPI Spec ({tool.name_for_ai}): {tool.get_api_spec()}\n"
                tool_used = True
        return (tool_used, new_prompt if tool_used else '')

    def check_res_for_calls(self, prompt) -> (bool, str):
        tool_called = False
        new_prompt = ''
        if re.search("Action: requests_get", prompt):
            print("[check_res_for_calls] tool called found")
            tool_called = True
            reqs = re.findall(r"Action Input: (https?:\/\/.*?)$(?:|\n)", prompt, re.MULTILINE)
            print("[check_res_for_calls] reqs:", reqs)
            for url_string in reqs:
                print("[check_res_for_calls] calling url:", url_string)
                res = requests.get(url_string)
                if res.status_code != 200:
                    raise ValueError(f"Error fetching {url}: {res.status_code}")
                json = res.json()
                new_prompt += f"Observation: {str(json)}"
        return (tool_called, new_prompt)

    def get_tools_for_prompt(self) -> str:
        print("[get_tools_for_prompt] tools", self.tools)
        prompt = '''Tools are available below. To call a tool, return a message in the following format (between ``):`
        Thought: I need to check the Klarna Shopping API to see if it has information on available t shirts.
        Action: KlarnaProducts
        Action Input: None
        Observation: Usage Guide: Use the Klarna plugin to get relevant product suggestions for any shopping or researching purpose. The query to be sent should not include stopwords like articles, prepositions and determinants. The api works best when searching for words that are related to products, like their name, brand, model or category. Links will always be returned and should be shown to the user.
        `
        '''
        for tool in self.tools:
            prompt += tool.get_prompt() + "\n\n"
        return prompt