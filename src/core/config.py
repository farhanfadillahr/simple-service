import os
from typing import List

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

ENV: str = ""

class Settings(BaseSettings):
    # base
    ENV: str = os.getenv("ENV", "dev")
    API: str = ""

    PROJECT_NAME: str = "fast-api-webhook"
    PROJECT_ROOT: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    VERSION: str = "0.0.1"
    
    DB_ENGINE_MAPPER: dict = {
        "postgresql": "postgresql",
        "mysql": "mysql+aiomysql",
    }

    # date
    DATETIME_FORMAT: str = "%Y-%m-%dT%H:%M:%S"
    DATE_FORMAT: str = "%Y-%m-%d"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    # Supabase
    supabase_url: str
    supabase_key: str
    supabase_table_name: str = "master"
    
    # Duitku Payment Gateway
    duitku_base_url: str = "https://api-sandbox.duitku.com/api/merchant/createInvoice"
    duitku_api_key: str
    duitku_merchant_code: str
    
    model_config = SettingsConfigDict(
        env_file=".env",
        ignore_extra=True,
    )
        


class TestConfigs(Settings):
    ENV: str = "test"


configs = Settings()

if ENV == "prod":
    pass
elif ENV == "stage":
    pass
elif ENV == "test":
    setting = TestConfigs()
