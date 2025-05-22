from typing import Optional

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    POSTGRES_DSN: Optional[PostgresDsn] = None
    SECRET_KEY: str


config = Config()
