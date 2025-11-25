from app.config import app_config
from classes.UserInfo import UserInfo
from classes.WorkersInfo import WorkersInfo

from loguru import logger
from pydantic import BaseModel, Field
import httpx


class User(BaseModel):
    address: str
    memo: str

    info: UserInfo
    info_flag: bool = Field(default=False)

    workers: WorkersInfo
    workers_flag: bool = Field(default=False)

    hashrate1m_flag: bool = Field(default=False)
    hashrate5m_flag: bool = Field(default=False)
    hashrate1hr_flag: bool = Field(default=False)


    @logger.catch
    def get_user_name(self) -> str:
        return f"{self.address} ({self.memo})"


    @logger.catch
    def set_info_flag(self, v: bool) -> None:
        if not isinstance(v, bool):
            raise ValueError(f"Given value is not an instance of bool!")
        self.info_flag = v
        logger.info(f"Set: {self.info_flag=}")


    @logger.catch
    def set_workers_flag(self, v: bool) -> None:
        if not isinstance(v, bool):
            raise ValueError(f"Given value is not an instance of bool!")
        self.workers_flag = v
        logger.info(f"Set: {self.workers_flag=}")


    @logger.catch
    def set_hashrate1m_flag(self, v: bool) -> None:
        if not isinstance(v, bool):
            raise ValueError(f"Given value is not instance of bool!")
        self.hashrate1m_flag = v
        logger.info(f"Set: {self.hashrate1m_flag=}")



    @logger.catch
    def set_hashrate5m_flag(self, v: bool) -> None:
        if not isinstance(v, bool):
            raise ValueError(f"Given value is not instance of bool!")
        self.hashrate5m_flag = v
        logger.info(f"Set: {self.hashrate5m_flag=}")


    @logger.catch
    def set_hashrate1hr_flag(self, v: bool) -> None:
        if not isinstance(v, bool):
            raise ValueError(f"Given value is not instance of bool!")
        self.hashrate1hr_flag = v
        logger.info(f"Set: {self.hashrate1hr_flag=}")


    @logger.catch
    async def update_info(self) -> None:
        try:
            api_url = app_config.balance_api.format(
                wallet_address=self.address
            )

        except KeyError as e:
            logger.exception(f"Cannot prepare balance api: {e}")
            raise Exception(e)

        else:
            logger.info(f"Requesting {api_url}...")

        try:
            async with httpx.AsyncClient() as httpx_client:
                r = await httpx_client.get(
                    url=api_url,
                    follow_redirects=True
                )
                if not r.is_success:
                    raise Exception(f"HTTP {r.status_code}")

        except (httpx.TimeoutException, httpx.ConnectError, httpx.ConnectTimeout, httpx.RequestError) as e:
            logger.exception(f"HTTP request error: {e}")
            raise Exception(e)

        except Exception as e:
            logger.exception(f"HTTP unknown error: {e}")
            raise Exception(e)

        else:
            logger.info(f"Successfully requested balance API with {r.status_code=} for address {self.address} ({self.memo})")
            logger.debug(f"{r.text=}")

        try:
            r_json = r.json()
            r_model = UserInfo(**r_json)

            if self.address != r_model.address:
                raise KeyError(f"Expected {self.address=} from balance API but {r_model.address=} received")
            
            self.info = r_model

        except Exception as e:
            logger.exception(f"Cannot operate balance data: {e}")
            raise Exception(e)

        return None


    @logger.catch
    async def update_workers(self) -> None:
        try:
            api_url = app_config.pool_api.format(
                wallet_address=self.address
            )

        except KeyError as e:
            logger.exception(f"Cannot prepare pool api: {e}")
            raise Exception(e)

        else:
            logger.info(f"Requesting {api_url}...")

        try:
            async with httpx.AsyncClient() as httpx_client:
                r = await httpx_client.get(
                    url=api_url,
                    follow_redirects=True
                )
                if not r.is_success:
                    raise Exception(f"HTTP {r.status_code}")

        except (httpx.TimeoutException, httpx.ConnectError, httpx.ConnectTimeout, httpx.RequestError) as e:
            logger.exception(f"HTTP request error: {e}")
            raise Exception(e)

        except Exception as e:
            logger.exception(f"HTTP unknown error: {e}")
            raise Exception(e)

        else:
            logger.info(f"Successfully requested pool API with {r.status_code=} for address {self.address} ({self.memo})")
            logger.debug(f"{r.text=}")

        try:
            r_json = r.json()
            self.workers = WorkersInfo(**r_json)

        except Exception as e:
            logger.exception(f"Cannot operate pool data: {e}")
            raise Exception(e)

        return None


if __name__ == "__main__":
    pass
