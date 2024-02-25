from pydantic import BaseModel, EmailStr, HttpUrl
from typing import TypeVar
import re
from typing import Literal
import requests
import yaml

APIUrlTypes = Literal['openapi']

MAX_NAME_LENGTH = 80
MAX_DESCRIPTION_LENGTH = 1000
VALID_CHARACTERS_REGEX = r'^[a-zA-Z0-9\s.,!?:;\'"-_]+$'

class Tool(BaseModel):
    name_for_human: str
    name_for_ai: str
    description_for_human: str
    description_for_ai: str
    api_type: APIUrlTypes
    api_url: HttpUrl
    logo_url: HttpUrl
    contact_email: str
    legal_info_url: str
    public: bool = False
    user_id: str = None

    class Config:
        arbitrary_types_allowed = True

    def validate(self) -> bool:
        try:
            Tool.validate_name_for_human(self.name_for_human)
            Tool.validate_name_for_ai(self.name_for_ai)
            Tool.validate_description_for_human(self.description_for_human)
            Tool.validate_description_for_ai(self.description_for_ai)
        except ValueError as e:
            print("Tool model validation error:", e)
            return False
        else:
            return True

    def to_dict(self) -> dict:
        return {
            'name_for_human': self.name_for_human,
            'name_for_ai': self.name_for_ai,
            'description_for_human': self.description_for_human,
            'description_for_ai': self.description_for_ai,
            'api_type': self.api_type,
            'api_url': str(self.api_url),
            'logo_url': str(self.logo_url),
            'contact_email': str(self.contact_email),
            'legal_info_url': str(self.legal_info_url)
        }

    def to_plugin(self) -> dict:
        return {
            'name_for_model': self.name_for_ai,
            'name_for_human': self.name_for_human,
            'description_for_model': self.description_for_ai,
            'description_for_human': self.description_for_human,
            'auth': {
                'type': 'user_http',
                'authorization_type': 'bearer'
            },
            'api': {
                'type': self.api_type,
                'url': str(self.api_url),
                'has_user_authentication': False
            },
            'logo_url': str(self.logo_url),
            'contact_email': str(self.contact_email),
            'legal_info_url': str(self.legal_info_url)
        }

    @staticmethod
    def from_plugin(url: str):
        """Instantiate Tool from plugin."""
        if not url:
            raise ValueError('Plugin URL is required')
        if not re.match(r"^https?:\/\/.+\.well-known\/.+\.json$", url):
            raise ValueError('URL to load plugin is not a valid plugin URL')
        try:
            res = requests.get(url)
            if res.status_code != 200:
                raise ValueError(f"Error fetching plugin json from {url}: {res.status_code}")
            json = res.json()
            return Tool.from_plugin_json(json)
        except Exception as e:
            print(f"Error creating tool from plugin: {e}")
            raise

    @staticmethod
    def from_plugin_json(json: dict):
        """Instantiate Tool from plugin json."""
        if not json:
            raise ValueError('Plugin JSON is required')
        tool_dict = {
            'name_for_human': json['name_for_human'],
            'name_for_ai': json['name_for_model'],
            'description_for_human': json['description_for_human'],
            'description_for_ai': json['description_for_model'],
            'api_type': json['api']['type'],
            'api_url': HttpUrl(json['api']['url']),
            'logo_url': HttpUrl(json['logo_url']),
            'contact_email': json['contact_email'],
            'legal_info_url': json['legal_info_url'],
        }
        tool = Tool(**tool_dict)
        tool.validate()
        return tool

    @staticmethod
    def from_yaml(yaml_str: str):
        """Instantiate Tool from YAML."""
        if not yaml_str:
            raise ValueError('YAML string is required')
        tool_dict = yaml.safe_load(yaml_str)
        tool = Tool.from_plugin_json(tool_dict)
        tool.validate()
        return tool

    @staticmethod
    def validate_name_for_human(name_for_human: str) -> str:
        if not name_for_human:
            raise ValueError('Name for human is required')
        if len(name_for_human) > MAX_NAME_LENGTH:
            raise ValueError('Name for human exceeds maximum length')
        if not re.match(VALID_CHARACTERS_REGEX, name_for_human):
            raise ValueError('Name for human contains invalid characters')
        return name_for_human

    @staticmethod
    def validate_name_for_ai(name_for_ai: str) -> str:
        if not name_for_ai:
            raise ValueError('Name for AI is required')
        if len(name_for_ai) > MAX_NAME_LENGTH:
            raise ValueError('Name for AI exceeds maximum length')
        if not re.match(VALID_CHARACTERS_REGEX, name_for_ai):
            raise ValueError('Name for AI contains invalid characters')
        if name_for_ai != name_for_ai.lower():
            raise ValueError('Name for AI must be lowercase')
        if re.match(r' ', name_for_ai):
            raise ValueError('Name for AI must not contain spaces')
        return name_for_ai

    @staticmethod
    def validate_description_for_human(description_for_human: str) -> str:
        if not description_for_human:
            raise ValueError('Description for human is required')
        if len(description_for_human) > MAX_DESCRIPTION_LENGTH:
            raise ValueError('Description for human exceeds maximum length')
        if not re.match(VALID_CHARACTERS_REGEX, description_for_human):
            raise ValueError('Description for human contains invalid characters')
        return description_for_human

    @staticmethod
    def validate_description_for_ai(description_for_ai: str) -> str:
        if not description_for_ai:
            raise ValueError('Description for AI is required')
        if len(description_for_ai) > MAX_DESCRIPTION_LENGTH:
            raise ValueError('Description for AI exceeds maximum length')
        if not re.match(VALID_CHARACTERS_REGEX, description_for_ai):
            raise ValueError('Description for AI contains invalid characters')
        return description_for_ai

    def get_prompt(self) -> str:
        prompt = f"tool: {self.name_for_ai}\ndescription: {self.description_for_ai}"
        return prompt

    def get_api_spec(self) -> dict:
        print(f"Fetching API spec from {self.api_url}")
        res = requests.get(self.api_url)
        print(f"API spec fetched from {self.api_url}: {res.status_code}")
        print(f"res: {res}")
        if res.status_code != 200:
            raise ValueError(f"Error fetching API spec from {self.api_url}: {res.status_code}")
        spec = {}
        url = str(self.api_url)
        if url.endswith('.json'):
            # Your code here
            spec = res.json()
        elif url.endswith('.yaml') or url.endswith('.yml'):
            spec = yaml.safe_load(res.text)
        return spec
