from app.config import app_config
from classes.UserInfo import UserInfo
from classes.WorkersInfo import WorkersInfo
from app.telegram import send_message

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

    hashrate1m_flag: bool = Field(default=True)
    hashrate5m_flag: bool = Field(default=True)
    hashrate1hr_flag: bool = Field(default=True)


    @logger.catch
    def get_user_name(self) -> str:
        return f"{self.address} ({self.memo})"

    @logger.catch
    def get_tg_user_name(self) -> str:
        return f"👛 {self.address[:5]} ... {self.address[-6:]} ({self.memo})"


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
    async def update_info(self) -> bool:
        try:
            api_url = app_config.balance_api.format(
                wallet_address=self.address
            )

        except Exception as e:
            logger.error(f"Cannot prepare balance api: {e}")
            return False

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
            logger.error(f"HTTP request error: {e}")
            return False

        except Exception as e:
            logger.error(f"HTTP unknown error: {e}")
            return False

        else:
            logger.info(f"Successfully requested balance API with {r.status_code=} for address {self.address} ({self.memo})")
            logger.debug(f"{r.text=}")

        try:
            r_json = r.json()
            r_model = UserInfo(**r_json)

            if self.address != r_model.address:
                raise Exception(f"Expected {self.address=} from balance API but {r_model.address=} received")
            
            self.info = r_model

        except Exception as e:
            logger.error(f"Cannot operate balance data: {e}")
            return False

        return True


    @logger.catch
    async def update_workers(self) -> bool:
        try:
            api_url = app_config.pool_api.format(
                wallet_address=self.address
            )

        except Exception as e:
            logger.error(f"Cannot prepare pool api: {e}")
            return False

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
            logger.error(f"HTTP request error: {e}")
            return False

        except Exception as e:
            logger.error(f"HTTP unknown error: {e}")
            return False

        else:
            logger.info(f"Successfully requested pool API with {r.status_code=} for address {self.address} ({self.memo})")
            logger.debug(f"{r.text=}")

        try:
            r_json = r.json()
            self.workers = WorkersInfo(**r_json)

        except Exception as e:
            logger.error(f"Cannot operate pool data: {e}")
            return False

        return True


    @logger.catch
    async def tg_balance_api_error(self) -> None:
        await send_message(
            t=f"{self.get_tg_user_name()}:\n🔴 Balance API Error!"
        )

    @logger.catch
    async def tg_balance_api_alive(self) -> None:
        await send_message(
            t=f"{self.get_tg_user_name()}:\n🟢 Balance API Alive!"
        )

    @logger.catch
    async def tg_balance_changed(self) -> None:
        await send_message(
            t=f"{self.get_tg_user_name()}:\n💸 Balance: {self.info.get_tg_balance()}"
        )


    @logger.catch
    async def tg_pool_api_error(self) -> None:
        await send_message(
            t=f"{self.get_tg_user_name()}:\n🔴 Pool API Error!"
        )

    @logger.catch
    async def tg_pool_api_alive(self) -> None:
        await send_message(
            t=f"{self.get_tg_user_name()}:\n🟢 Pool API Alive!"
        )

    @logger.catch
    async def tg_workers_changed(self) -> None:
        await send_message(
            t=f"{self.get_tg_user_name()}:\n👷 Workers: {self.workers.workers}"
        )


    @logger.catch
    async def tg_hashrate1m_low(self) -> None:
        await send_message(
            t=f"{self.get_tg_user_name()}:\n🔴 Hashrate 1m LOW: {self.workers.hashrate1m}"
        )

    @logger.catch
    async def tg_hashrate1m_ok(self) -> None:
        await send_message(
            t=f"{self.get_tg_user_name()}:\n🟢 Hashrate 1m OK: {self.workers.hashrate1m}"
        )


    @logger.catch
    async def tg_hashrate5m_low(self) -> None:
        await send_message(
            t=f"{self.get_tg_user_name()}:\n🔴 Hashrate 5m LOW: {self.workers.hashrate5m}"
        )

    @logger.catch
    async def tg_hashrate5m_ok(self) -> None:
        await send_message(
            t=f"{self.get_tg_user_name()}:\n🟢 Hashrate 5m OK: {self.workers.hashrate5m}"
        )


    @logger.catch
    async def tg_hashrate1hr_low(self) -> None:
        await send_message(
            t=f"{self.get_tg_user_name()}:\n🔴 Hashrate 1hr LOW: {self.workers.hashrate1hr}"
        )

    @logger.catch
    async def tg_hashrate1hr_ok(self) -> None:
        await send_message(
            t=f"{self.get_tg_user_name()}:\n🟢 Hashrate 1hr OK: {self.workers.hashrate1hr}"
        )


    @logger.catch
    def __str__(self) -> str:
        return "User:\n" + "\n".join(f"{k}: {v}" for k, v in self.__dict__.items())


if __name__ == "__main__":
    pass
