from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    """
        Settings for all env variable configuration, consume with .env file schema
    """

    API_KEY: str
    VERIFY_TOKEN: str
    ACCESS_TOKEN: str
    APP_ID: str
    APP_SECRET:str
    RECIPIENT_WAID: str
    VERSION: str
    PHONE_NUMBER_ID: str

    OPENAI_KEY:str

    class Config:
        env_file = ".env"

settings = Settings()
