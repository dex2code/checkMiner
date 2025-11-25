from classes.Manager import manager

from loguru import logger


async def operate_info(user: str) -> None:
    user_name = manager.user_list[user].get_user_name()

    logger.info(f"Updating info for user {user_name}...")
    logger.debug(f"{manager.user_list[user].info}")
    info_flag = manager.user_list[user].info_flag
    old_balance = manager.user_list[user].info.final_balance
    try:
        await manager.user_list[user].update_info()
    
    except Exception as e:
        logger.exception(f"Cannot update info for user {user_name}: {e} ({info_flag=})")
        if not info_flag:
            manager.user_list[user].set_info_flag(v=True)
            # Inform Balance API Error
    
    else:
        logger.info(f"Successfully updated info for user {user_name} ({info_flag=})")
        logger.debug(f"{manager.user_list[user].info}")

        new_balance = manager.user_list[user].info.final_balance

        if info_flag:
            manager.user_list[user].set_info_flag(v=False)
            # inform Balance API Ok with current balance

        if old_balance != new_balance:
            logger.warning(f"Balance changed for user {user_name}: {old_balance:,} -> {new_balance:,}")
            # Inform balance change
        else:
            logger.info(f"Balance for user {user_name} is the same: {new_balance:,}")

    return None


if __name__ == "__main__":
    pass
