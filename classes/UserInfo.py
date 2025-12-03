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
    def set_balance(self, b:int):
        self.balance = b
        self.unconfirmed_balance = b
        self.final_balance = b

    @logger.catch
    def get_balance_btc(self) -> float:
        return self.balance / 100_000_000
    
    @logger.catch
    def get_tg_balance(self) -> str:
        return f"{self.balance:,} SAT ({self.get_balance_btc()} BTC)"


    @logger.catch
    def __str__(self) -> str:
        return "UserInfo:\n" + "\n".join(f"{k}: {v}" for k, v in self.__dict__.items())


if __name__ == "__main__":
    pass
