from pydantic_settings import BaseSettings
import os

print(f"Loading settings from .env file")
print(f"Working directory: {os.getcwd()}")
with open('.env', 'r') as file:
    print(f"ENV file name: {file.name}")
    env_contents = file.read()
    print(f"ENV file contents: {env_contents}")

print(f"JWT secret: {os.getenv('JWT_SECRET')}")
print(f"Supabase project URL: {os.getenv('SUPABASE_PROJECT_URL')}")
print(f"Supabase API key: {os.getenv('SUPABASE_API_KEY')}")

class Settings(BaseSettings):
    JWT_SECRET: str = os.getenv("JWT_SECRET")
    SUPABASE_URL: str = os.getenv("SUPABASE_PROJECT_URL")
    SUPABASE_KEY: str = os.getenv("SUPABASE_API_KEY")
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
