from app.config import app_config
from classes.UserInfo import UserInfo
from classes.WorkersInfo import WorkersInfo
from classes.User import User

from loguru import logger


class UserManager():
    @logger.catch
    def __init__(self) -> None:
        self.user_list: dict[str, User] = {}

        for pool_user in app_config.pool_users:
            self.user_list[pool_user] = User(
                address=pool_user,
                memo=app_config.pool_users[pool_user].memo,
                info=UserInfo(
                    address=pool_user
                ),
                workers=WorkersInfo()
            )


user_manager = UserManager()


if __name__ == "__main__":
    pass