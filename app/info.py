from classes.Manager import manager

from loguru import logger


async def operate_info(user: str) -> None:
    user_name = manager.user_list[user].get_user_name()

    logger.info(f"Updating info for user {user_name}...")
    logger.debug(f"{manager.user_list[user].info}")
    info_flag = manager.user_list[user].info_flag
    old_balance_sat = manager.user_list[user].info.balance
    old_balance_btc = manager.user_list[user].info.get_balance_btc()

    if not await manager.user_list[user].update_info():
        logger.error(f"Cannot update info for user {user_name} ({info_flag=})")
        if not info_flag:
            manager.user_list[user].set_info_flag(v=True)
            await manager.user_list[user].tg_balance_api_error()
    
    else:
        logger.info(f"Successfully updated info for user {user_name} ({info_flag=})")
        logger.debug(f"{manager.user_list[user].info}")

        new_balance_sat = manager.user_list[user].info.balance
        new_balance_btc = manager.user_list[user].info.get_balance_btc()

        if info_flag:
            manager.user_list[user].set_info_flag(v=False)
            await manager.user_list[user].tg_balance_api_alive()

        if old_balance_sat != new_balance_sat:
            logger.warning(f"Balance changed for user {user_name}: {old_balance_sat:,} SAT ({old_balance_btc} BTC) -> {new_balance_sat:,} SAT ({new_balance_btc} BTC)")
            await manager.user_list[user].tg_balance_changed()
        else:
            logger.info(f"Balance for user {user_name} is the same: {new_balance_sat:,} SAT ({new_balance_btc} BTC)")

    return None


if __name__ == "__main__":
    pass
