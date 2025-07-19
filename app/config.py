import os
from pathlib import Path

from dotenv import load_dotenv

env_path = Path('.') / '.env.dev'
print(f"Loading .env file from: {env_path}")  # Debugging
load_dotenv(dotenv_path=env_path)

print(f"API_PREFIX from .env: {os.getenv('API_PREFIX')}")  # Debugging
class Config():
    PROJECT_NAME:str = "Auth Service"
    PROJECT_VERSION: str = "1.0.0"

    JWT_SECRET:str = os.getenv('JWT_SECRET')
    JWT_ALGORITHM:str = os.getenv('JWT_ALGORITHM')
    JWT_ACCESS_TOKEN_EXPIRES:int=os.getenv('JWT_ACCESS_TOKEN_EXPIRES')
    JWT_REFRESH_TOKEN_EXPIRES:int=os.getenv('JWT_REFRESH_TOKEN_EXPIRES')
    

    POSTGRES_USER : str = os.getenv("POSTGRES_USER","postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD","BA123456")
    POSTGRES_SERVER : str = os.getenv("POSTGRES_SERVER", "db")
    POSTGRES_PORT : int = int(os.getenv("POSTGRES_PORT", 5432)) # default postgres port is 5432
    POSTGRES_DB : str = os.getenv("POSTGRES_DB","business_automation")
    POSTGRES_SCHEMA: str = os.getenv("POSTGRES_SCHEMA", "public")
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

    CELERY = {
        "broker_url": os.getenv("BROKER_URL"),
        "redbeat_redis_url": os.getenv("REDBEAT_REDIS_URL")
    }




    API_PREFIX: str =os.getenv('API_PREFIX')
    BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
config = Config()