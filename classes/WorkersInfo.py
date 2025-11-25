from app.tools import convert_hashrate

from pydantic import BaseModel, Field
from loguru import logger


class WorkersInfo(BaseModel):
    hashrate1m: str = Field(default="")
    hashrate5m: str = Field(default="")
    hashrate1hr: str = Field(default="")
    hashrate1d: str = Field(default="")
    hashrate7d: str = Field(default="")
    lastshare: int = Field(default=0)
    workers: int = Field(default=-1)
    shares: int = Field(default=0)
    bestshare: float = Field(default=0.0)
    bestever: int = Field(default=0)
    authorised: int = Field(default=0)

    @logger.catch
    def get_hashrate1m_int(self) -> int:
        try:
            return convert_hashrate(
                s = self.hashrate1m
            )
        except ValueError as e:
            logger.exception(f"{e}")
            raise ValueError(e)


    @logger.catch
    def get_hashrate5m_int(self) -> int:
        try:
            return convert_hashrate(
                s = self.hashrate5m
            )
        except ValueError as e:
            logger.exception(f"{e}")
            raise ValueError(e)


    @logger.catch
    def get_hashrate1hr_int(self) -> int:
        try:
            return convert_hashrate(
                s = self.hashrate1hr
            )
        except ValueError as e:
            logger.exception(f"{e}")
            raise ValueError(e)


    @logger.catch
    def __str__(self) -> str:
        return "WorkersInfo:" + "\n".join(f"{k}: {v}" for k, v in self.__dict__.items())


if __name__ == "__main__":
    pass