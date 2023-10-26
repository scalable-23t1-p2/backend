import os as OS
from pydantic import BaseSettings
from dotenv import load_dotenv

class AuthConfig(BaseSettings):
    load_dotenv()
    print("hi")
    print(OS.getenv("JWT_SECRET"))
    print(type(OS.getenv("JWT_SECRET")))

    JWT_ALG: str = "HS256"
    JWT_SECRET: str = OS.getenv("JWT_SECRET")
    JWT_EXP: int = 5  # minutes

    REFRESH_TOKEN_KEY: str = "refreshToken"
    REFRESH_TOKEN_EXP: int = 60 * 60 * 24 * 21  # 21 days

    SECURE_COOKIES: bool = True

auth_config = AuthConfig()