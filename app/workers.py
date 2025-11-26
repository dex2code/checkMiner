from classes.Manager import manager
from app.config import app_config
from app.tools import convert_hashrate

from loguru import logger


async def operate_workers(user: str) -> None:

    user_name = manager.user_list[user].get_user_name()
    workers_flag = manager.user_list[user].workers_flag
    old_number_workers = manager.user_list[user].workers.workers

    logger.info(f"Updating workers for user {user_name} ({workers_flag=})")
    logger.debug(f"{manager.user_list[user].workers}")

    if not await manager.user_list[user].update_workers():
        logger.error(f"Cannot update workers for user {user_name} ({workers_flag=})")
        if not workers_flag:
            manager.user_list[user].set_workers_flag(v=True)
            await manager.user_list[user].tg_pool_api_error()

    else:
        logger.info(f"Successfully updated workers for user {user_name} ({workers_flag=})")
        logger.debug(f"{manager.user_list[user].workers}")

        new_number_workers = manager.user_list[user].workers.workers

        if workers_flag:
            manager.user_list[user].set_workers_flag(v=False)
            await manager.user_list[user].tg_pool_api_alive()

        if old_number_workers != new_number_workers:
            logger.warning(f"Number of workers for user {user_name} changed: {old_number_workers} -> {new_number_workers}")
            await manager.user_list[user].tg_workers_changed()
        else:
            logger.info(f"Number of workers for user {user_name} is the same: {new_number_workers}")


        try:
            cur_hashrate1m_str = manager.user_list[user].workers.hashrate1m
            cur_hashrate1m_int = manager.user_list[user].workers.get_hashrate1m_int()
            tr_hashrate1m_str = app_config.pool_users[user].hashrate1m_treshold
            tr_hashrate1m_int = convert_hashrate(tr_hashrate1m_str)
            flag_hashrate1m = manager.user_list[user].hashrate1m_flag

            if cur_hashrate1m_int < tr_hashrate1m_int:
                logger.warning(f"1m hashrate for user {user_name} is lower than expected: {cur_hashrate1m_str} < {tr_hashrate1m_str} ({flag_hashrate1m=})")

                if not flag_hashrate1m:
                    manager.user_list[user].set_hashrate1m_flag(v=True)
                    await manager.user_list[user].tg_hashrate1m_low()

            else:
                logger.info(f"1m hashrate for user {user_name} is OK: {cur_hashrate1m_str} >= {tr_hashrate1m_str} ({flag_hashrate1m=})")

                if flag_hashrate1m:
                    manager.user_list[user].set_hashrate1m_flag(v=False)
                    await manager.user_list[user].tg_hashrate1m_ok()

        except Exception as e:
            flag_hashrate1m = manager.user_list[user].hashrate1m_flag
            logger.exception(f"Cannot compare hashrate1m for user {user_name}: {e}\n ({flag_hashrate1m=})")
        
        else:
            flag_hashrate1m = manager.user_list[user].hashrate1m_flag
            logger.info(f"Successfully measured hashrate1m ({flag_hashrate1m=})")


        try:
            cur_hashrate5m_str = manager.user_list[user].workers.hashrate5m
            cur_hashrate5m_int = manager.user_list[user].workers.get_hashrate5m_int()
            tr_hashrate5m_str = app_config.pool_users[user].hashrate5m_treshold
            tr_hashrate5m_int = convert_hashrate(tr_hashrate5m_str)
            flag_hashrate5m = manager.user_list[user].hashrate5m_flag

            if cur_hashrate5m_int < tr_hashrate5m_int:
                logger.warning(f"5m hashrate for user {user_name} is lower than expected: {cur_hashrate5m_str} < {tr_hashrate5m_str} ({flag_hashrate5m=})")

                if not manager.user_list[user].hashrate5m_flag:
                    manager.user_list[user].set_hashrate5m_flag(v=True)
                    await manager.user_list[user].tg_hashrate5m_low()

            else:
                logger.info(f"5m hashrate for user {user_name} is OK: {cur_hashrate5m_str} >= {tr_hashrate5m_str} ({flag_hashrate5m=})")

                if manager.user_list[user].hashrate5m_flag:
                    manager.user_list[user].set_hashrate5m_flag(v=False)
                    await manager.user_list[user].tg_hashrate5m_ok()

        except Exception as e:
            flag_hashrate5m = manager.user_list[user].hashrate5m_flag
            logger.exception(f"Cannot compare hashrate5m for user {user_name}: {e}")
        
        else:
            flag_hashrate5m = manager.user_list[user].hashrate5m_flag
            logger.info(f"Successfully measured hashrate5m ({flag_hashrate5m=})")


        try:
            cur_hashrate1hr_str = manager.user_list[user].workers.hashrate1hr
            cur_hashrate1hr_int = manager.user_list[user].workers.get_hashrate1hr_int()
            tr_hashrate1hr_str = app_config.pool_users[user].hashrate1hr_treshold
            tr_hashrate1hr_int = convert_hashrate(tr_hashrate1hr_str)
            flag_hashrate1hr = manager.user_list[user].hashrate1hr_flag

            if cur_hashrate1hr_int < tr_hashrate1hr_int:
                logger.warning(f"1hr hashrate for user {user_name} is lower than expected: {cur_hashrate1hr_str} < {tr_hashrate1hr_str} ({flag_hashrate1hr=})")

                if not manager.user_list[user].hashrate1hr_flag:
                    manager.user_list[user].set_hashrate1hr_flag(v=True)
                    await manager.user_list[user].tg_hashrate1hr_low()

            else:
                logger.info(f"1hr hashrate for user {user_name} is OK: {cur_hashrate1hr_str} >= {tr_hashrate1hr_str} ({flag_hashrate1hr=})")

                if manager.user_list[user].hashrate1hr_flag:
                    manager.user_list[user].set_hashrate1hr_flag(v=False)
                    await manager.user_list[user].tg_hashrate1hr_ok()

        except Exception as e:
            flag_hashrate1hr = manager.user_list[user].hashrate1hr_flag
            logger.exception(f"Cannot compare hashrate1hr for user {user_name}: {e}")
        
        else:
            flag_hashrate1hr = manager.user_list[user].hashrate1hr_flag
            logger.info(f"Successfully measured hashrate1hr ({flag_hashrate1hr=})")

    return None


if __name__ == "__main__":
    pass