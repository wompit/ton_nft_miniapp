from flask import url_for

from controllers import _Controller
from models import User
from utils import UserStatus


class NFTCheckController(_Controller):
    def _call(self) -> str | None:
        user = User.get(telegram_id=self.request_data["id"])
        if self.check_nft_ownership(user.wallet_address):
            user.status = UserStatus.ACTIVE
            user.save(only=[User.status])
            return url_for("main.final", nft_address=user.extra_data["nft"]["address"])
