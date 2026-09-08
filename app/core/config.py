from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    internal_service_token: str = "dev-internal-token"
    llm_api_key: str = ""
    trained_policy_path: str = "data/trained_policy.pkl"
    bedrock_model_id: str = "us.meta.llama3-1-8b-instruct-v1:0"
    aws_region: str = "us-east-1"
    topics_path: str = "data/topics.json"

    model_config = SettingsConfigDict(env_prefix="AI_")


@lru_cache
def get_settings() -> Settings:
    return Settings()