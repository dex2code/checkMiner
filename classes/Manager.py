from classes.Config import app_config
from classes.UserInfo import UserInfo
from classes.WorkersInfo import WorkersInfo
from classes.User import User

from loguru import logger


class Manager():
    @logger.catch
    def __init__(self) -> None:
        self.user_list: dict[str, User] = {}

        for pool_user in app_config.pool_users:
            self.user_list[pool_user] = User(
                address=pool_user,
                memo=app_config.pool_users[pool_user].memo,
                daily_statistics=app_config.pool_users[pool_user].daily_statistics,
                info=UserInfo(
                    address=pool_user
                ),
                workers=WorkersInfo(),
                hashrate1m_treshold_str=app_config.pool_users[pool_user].hashrate1m_treshold,
                hashrate5m_treshold_str=app_config.pool_users[pool_user].hashrate5m_treshold,
                hashrate1hr_treshold_str=app_config.pool_users[pool_user].hashrate1hr_treshold
            )
    
    @logger.catch
    def get_tg_list_users(self) -> str:
        return "\n".join(f"👛 {k[:5]} ... {k[-6:]} ({self.user_list[k].memo})" for k in self.user_list)


manager = Manager()


if __name__ == "__main__":
    pass
