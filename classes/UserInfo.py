from pydantic import BaseModel, Field
from loguru import logger


class UserInfo(BaseModel):
    address: str
    total_received: int = Field(default=-1)
    total_sent: int = Field(default=-1)
    balance: int = Field(default=-1)
    unconfirmed_balance: int = Field(default=-1)
    final_balance: int = Field(default=-1)
    n_tx: int = Field(default=-1)
    unconfirmed_n_tx: int = Field(default=-1)
    final_n_tx: int = Field(default=-1)

    @logger.catch
    def __str__(self) -> str:
        return "UserInfo:" + "\n".join(f"{k}: {v}" for k, v in self.__dict__.items())


if __name__ == "__main__":
    pass
