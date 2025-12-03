from classes.Config import app_config
from classes.UserInfo import UserInfo
from classes.WorkersInfo import WorkersInfo
from app.tools import convert_hashrate
from app.telegram import send_message

from loguru import logger
from pydantic import BaseModel, Field
import httpx


class User(BaseModel):
    address: str
    memo: str
    daily_statistics: bool

    info: UserInfo
    info_flag: bool = Field(default=False)

    workers: WorkersInfo
    workers_flag: bool = Field(default=False)

    hashrate1m_flag: bool = Field(default=True)
    hashrate5m_flag: bool = Field(default=True)
    hashrate1hr_flag: bool = Field(default=True)

    hashrate1m_treshold_str: str = Field(pattern=r'^\d+(\.\d+)?[KMGT]$')
    hashrate5m_treshold_str: str = Field(pattern=r'^\d+(\.\d+)?[KMGT]$')
    hashrate1hr_treshold_str: str = Field(pattern=r'^\d+(\.\d+)?[KMGT]$')


    @logger.catch
    def get_user_name(self) -> str:
        return f"{self.address} ({self.memo})"

    @logger.catch
    def get_tg_user_name(self) -> str:
        return f"👛 {self.address[:5]} ... {self.address[-6:]} ({self.memo})"


    @logger.catch
    def set_info_flag(self, v: bool) -> None:
        self.info_flag = v
        logger.info(f"Set: {self.info_flag=} for user {self.get_user_name()}")

    @logger.catch
    def set_workers_flag(self, v: bool) -> None:
        self.workers_flag = v
        logger.info(f"Set: {self.workers_flag=} for user {self.get_user_name()}")


    @logger.catch
    def set_hashrate1m_flag(self, v: bool) -> None:
        self.hashrate1m_flag = v
        logger.info(f"Set: {self.hashrate1m_flag=} for user {self.get_user_name()}")

    @logger.catch
    def set_hashrate5m_flag(self, v: bool) -> None:
        self.hashrate5m_flag = v
        logger.info(f"Set: {self.hashrate5m_flag=} for user {self.get_user_name()}")

    @logger.catch
    def set_hashrate1hr_flag(self, v: bool) -> None:
        self.hashrate1hr_flag = v
        logger.info(f"Set: {self.hashrate1hr_flag=} for user {self.get_user_name()}")


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
    async def tg_daily_statistics(self) -> None:
        await send_message(
            t=f"🕑 Daily info for {self.get_tg_user_name()}:\n🛠 Hashrate 1d: {self.workers.hashrate1d}\n💰 Balance: {self.info.get_tg_balance()}"
        )


    @logger.catch
    async def update_info(self) -> bool:
        try:
            api_url = app_config.balance_api.format(
                wallet_address=self.address
            )
        except BaseException as e:
            logger.error(f"Cannot prepare URL for Balance API: {e}")
            return False

        logger.info(f"Requesting {api_url}...")

        try:
            async with httpx.AsyncClient() as httpx_client:
                r = await httpx_client.get(
                    url=api_url,
                    follow_redirects=True
                )
                r.raise_for_status()
        except httpx.HTTPError as e:
            logger.error(f"Cannot request Balance API URL ({api_url}): {e}")
            return False

        logger.info(f"Successfully requested Balance API with {r.status_code=} for user {self.get_user_name()}")
        logger.debug(f"{r.text=}")

        try:
            r_json = r.json()
            r_model = UserInfo(**r_json)
            if self.address != r_model.address:
                raise Exception(f"Expected {self.address=} from Balance API but {r_model.address=} received")
            self.info = r_model
        except BaseException as e:
            logger.error(f"Cannot operate Balance API data: {e}")
            return False

        return True

    @logger.catch
    async def operate_info(self) -> None:
        user_name = self.get_user_name()

        logger.info(f"Updating info for user {user_name}...")
        logger.debug(f"{self.info}")

        old_balance_sat = self.info.balance
        old_balance_btc = self.info.get_balance_btc()

        if not await self.update_info():
            logger.error(f"Cannot update info for user {user_name} ({self.info_flag=})")
            if not self.info_flag:
                self.set_info_flag(v=True)
                self.info.set_balance(b=-1)
                await self.tg_balance_api_error()
            return None
    
        logger.info(f"Successfully updated info for user {user_name} ({self.info_flag=})")
        logger.debug(f"{self.info}")

        new_balance_sat = self.info.balance
        new_balance_btc = self.info.get_balance_btc()

        if self.info_flag:
            self.set_info_flag(v=False)
            await self.tg_balance_api_alive()

        if old_balance_sat != new_balance_sat:
            logger.warning(f"Balance changed for user {user_name}: {old_balance_sat:,} SAT ({old_balance_btc} BTC) -> {new_balance_sat:,} SAT ({new_balance_btc} BTC)")
            await self.tg_balance_changed()
        else:
            logger.info(f"Balance for user {user_name} is the same: {new_balance_sat:,} SAT ({new_balance_btc} BTC)")

        return None


    @logger.catch
    async def update_workers(self) -> bool:
        try:
            api_url = app_config.pool_api.format(
                wallet_address=self.address
            )
        except BaseException as e:
            logger.error(f"Cannot prepare URL for Pool API: {e}")
            return False

        logger.info(f"Requesting {api_url}...")

        try:
            async with httpx.AsyncClient() as httpx_client:
                r = await httpx_client.get(
                    url=api_url,
                    follow_redirects=True
                )
                r.raise_for_status()
        except httpx.HTTPError as e:
            logger.error(f"Cannot request Pool API URL ({api_url}): {e}")
            return False

        logger.info(f"Successfully requested Pool API with {r.status_code=} for for user {self.get_user_name()}")
        logger.debug(f"{r.text=}")

        try:
            r_json = r.json()
            r_model = WorkersInfo(**r_json)
            self.workers = r_model
        except BaseException as e:
            logger.error(f"Cannot operate Pool API data: {e}")
            return False

        return True

    async def operate_workers(self) -> None:
        old_number_workers = self.workers.workers

        logger.info(f"Updating workers for user {self.get_user_name()} ({self.workers_flag=})")
        logger.debug(f"{self.workers}")

        if not await self.update_workers():
            logger.error(f"Cannot update workers for user {self.get_user_name()} ({self.workers_flag=})")
            if not self.workers_flag:
                self.set_workers_flag(v=True)
                self.set_hashrate1m_flag(v=True)
                self.set_hashrate5m_flag(v=True)
                self.set_hashrate1hr_flag(v=True)
                await self.tg_pool_api_error()
            return None

        logger.info(f"Successfully updated workers for user {self.get_user_name()} ({self.workers_flag=})")
        logger.debug(f"{self.workers}")

        new_number_workers = self.workers.workers

        if self.workers_flag:
            self.set_workers_flag(v=False)
            await self.tg_pool_api_alive()

        if old_number_workers != new_number_workers:
            logger.warning(f"Number of workers for user {self.get_user_name()} changed: {old_number_workers} -> {new_number_workers}")
            await self.tg_workers_changed()
        else:
            logger.info(f"Number of workers for user {self.get_user_name()} is the same: {new_number_workers}")


        cur_hashrate1m_str = self.workers.hashrate1m
        cur_hashrate1m_int = convert_hashrate(cur_hashrate1m_str)
        tr_hashrate1m_str = self.hashrate1m_treshold_str
        tr_hashrate1m_int = convert_hashrate(tr_hashrate1m_str)
        logger.debug(f"{cur_hashrate1m_str=}, {cur_hashrate1m_int=}, {tr_hashrate1m_str=}, {tr_hashrate1m_int=}")

        if cur_hashrate1m_int < tr_hashrate1m_int:
            logger.warning(f"1m hashrate for user {self.get_user_name()} is lower than expected: {cur_hashrate1m_str} < {tr_hashrate1m_str} ({self.hashrate1m_flag=})")
            if not self.hashrate1m_flag:
                self.set_hashrate1m_flag(v=True)
                await self.tg_hashrate1m_low()
        else:
            logger.info(f"1m hashrate for user {self.get_user_name()} is OK: {cur_hashrate1m_str} >= {tr_hashrate1m_str} ({self.hashrate1m_flag=})")
            if self.hashrate1m_flag:
                self.set_hashrate1m_flag(v=False)
                await self.tg_hashrate1m_ok()
        logger.info(f"Successfully measured hashrate1m ({self.hashrate1m_flag=})")


        logger.debug(f"{self.workers.hashrate5m=}, {self.hashrate1hr_treshold_str}")
        cur_hashrate5m_str = self.workers.hashrate5m
        cur_hashrate5m_int = convert_hashrate(cur_hashrate5m_str)
        tr_hashrate5m_str = self.hashrate5m_treshold_str
        tr_hashrate5m_int = convert_hashrate(tr_hashrate5m_str)
        logger.debug(f"{cur_hashrate5m_str=}, {cur_hashrate5m_int=}, {tr_hashrate5m_str=}, {tr_hashrate5m_int=}")

        if cur_hashrate5m_int < tr_hashrate5m_int:
            logger.warning(f"5m hashrate for user {self.get_user_name()} is lower than expected: {cur_hashrate5m_str} < {tr_hashrate5m_str} ({self.hashrate5m_flag=})")
            if not self.hashrate5m_flag:
                self.set_hashrate5m_flag(v=True)
                await self.tg_hashrate5m_low()
        else:
            logger.info(f"5m hashrate for user {self.get_user_name()} is OK: {cur_hashrate5m_str} >= {tr_hashrate5m_str} ({self.hashrate5m_flag=})")
            if self.hashrate5m_flag:
                self.set_hashrate5m_flag(v=False)
                await self.tg_hashrate5m_ok()
        logger.info(f"Successfully measured hashrate5m ({self.hashrate5m_flag=})")


        cur_hashrate1hr_str = self.workers.hashrate1hr
        cur_hashrate1hr_int = convert_hashrate(cur_hashrate1hr_str)
        tr_hashrate1hr_str = self.hashrate1hr_treshold_str
        tr_hashrate1hr_int = convert_hashrate(tr_hashrate1hr_str)
        logger.debug(f"{cur_hashrate1hr_str=}, {cur_hashrate1hr_int=}, {tr_hashrate1hr_str=}, {tr_hashrate1hr_int=}")

        if cur_hashrate1hr_int < tr_hashrate1hr_int:
            logger.warning(f"1hr hashrate for user {self.get_user_name()} is lower than expected: {cur_hashrate1hr_str} < {tr_hashrate1hr_str} ({self.hashrate1hr_flag=})")
            if not self.hashrate1hr_flag:
                self.set_hashrate1hr_flag(v=True)
                await self.tg_hashrate1hr_low()
        else:
            logger.info(f"1hr hashrate for user {self.get_user_name()} is OK: {cur_hashrate1hr_str} >= {tr_hashrate1hr_str} ({self.hashrate1hr_flag=})")
            if self.hashrate1hr_flag:
                self.set_hashrate1hr_flag(v=False)
                await self.tg_hashrate1hr_ok()
        logger.info(f"Successfully measured hashrate1hr ({self.hashrate1hr_flag=})")

        return None


    @logger.catch
    def __str__(self) -> str:
        return "User:\n" + "\n".join(f"{k}: {v}" for k, v in self.__dict__.items())


if __name__ == "__main__":
    pass
