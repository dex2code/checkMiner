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

    try:
        await manager.user_list[user].update_workers()
    
    except Exception as e:
        logger.exception(f"Cannot update workers for user {user_name}: {e} ({workers_flag=})")
        if not workers_flag:
            manager.user_list[user].set_workers_flag(v=True)
            # Inform Workers API Error

    else:
        logger.info(f"Successfully updated workers for user {user_name} ({workers_flag=})")
        logger.debug(f"{manager.user_list[user].workers}")

        new_number_workers = manager.user_list[user].workers.workers

        if workers_flag:
            manager.user_list[user].set_workers_flag(v=False)
            # Inform Workers API OK with current number of workers

        if old_number_workers != new_number_workers:
            logger.warning(f"Number of workers for user {user_name} changed: {old_number_workers} -> {new_number_workers}")
            # Inform number of workers changed
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
                    # Inform Hashrate 1m LOW

            else:
                logger.info(f"1m hashrate for user {user_name} is OK: {cur_hashrate1m_str} >= {tr_hashrate1m_str} ({flag_hashrate1m=})")

                if flag_hashrate1m:
                    manager.user_list[user].set_hashrate1m_flag(v=False)
                    # Inform Hashrate 1m OK

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
                    # Inform hashrate 5m is LOW

            else:
                logger.info(f"5m hashrate for user {user_name} is OK: {cur_hashrate5m_str} >= {tr_hashrate5m_str} ({flag_hashrate5m=})")

                if manager.user_list[user].hashrate5m_flag:
                    manager.user_list[user].set_hashrate5m_flag(v=False)
                    # Inform hashrate 5m is OK

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
                    # Inform hashrate 1hr is LOW

            else:
                logger.info(f"1hr hashrate for user {user_name} is OK: {cur_hashrate1hr_str} >= {tr_hashrate1hr_str} ({flag_hashrate1hr=})")

                if manager.user_list[user].hashrate1hr_flag:
                    manager.user_list[user].set_hashrate1hr_flag(v=False)
                    # Inform hashrate 1h is OK

        except Exception as e:
            flag_hashrate1hr = manager.user_list[user].hashrate1hr_flag
            logger.exception(f"Cannot compare hashrate1hr for user {user_name}: {e}")
        
        else:
            flag_hashrate1hr = manager.user_list[user].hashrate1hr_flag
            logger.info(f"Successfully measured hashrate1hr ({flag_hashrate1hr=})")

    return None


if __name__ == "__main__":
    pass