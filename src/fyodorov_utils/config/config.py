from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    JWT_SECRET: str = os.getenv("JWT_SECRET")
    SUPABASE_URL: str = os.getenv("SUPABASE_PROJECT_URL")
    SUPABASE_KEY: str = os.getenv("SUPABASE_API_KEY")
