from pydantic import BaseModel, SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import urlparse
from typing import Optional


class LoggerConfig(BaseModel):
    path: str
    level: str
    rotation: str
    retention: str
    serialize: bool


class PoolUserConfig(BaseModel):
    memo: str
    hashrate1m_treshold: str = Field(pattern=r'^\d+(\.\d+)?[KMGT]$')
    hashrate5m_treshold: str = Field(pattern=r'^\d+(\.\d+)?[KMGT]$')
    hashrate1hr_treshold: str = Field(pattern=r'^\d+(\.\d+)?[KMGT]$')
    daily_statistics: bool


class AppConfig(BaseSettings):
    bot_nickname: str
    loop_sleep_seconds: int
    logger: LoggerConfig
    pool_users: dict[str, PoolUserConfig]
    pool_api: str
    balance_api: str

    TG_BOT_TOKEN: SecretStr
    TG_CHAT_ID: SecretStr

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

    def get_pool_api_host(self) -> Optional[str]:
        return urlparse(self.pool_api).hostname

    def get_balance_api_host(self) -> Optional[str]:
        return urlparse(self.balance_api).hostname


app_config = AppConfig.model_validate_json(
    json_data=open(
        file="config.json"
    ).read()
)


if __name__ == "__main__":
    pass
