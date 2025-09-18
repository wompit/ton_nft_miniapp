from flask import url_for
from controllers import _Controller
from models import User
from utils import UserStatus


class WalletConnectController(_Controller):
    def _call(self) -> dict:
        user = User.get_or_none(telegram_id=self.request_data["user_data[id]"])
        wallet = self.request_data["address"]
        mode = self.get_mode(wallet)

        # user = False
        # mode = "default"
        url = url_for("main.buy_page", mode=mode)
        if user:
            status = user.status
            if status == UserStatus.ACTIVE or self.check_nft_ownership(
                user.wallet_address
            ):
                url = url_for(
                    "main.final", nft_address=user.extra_data["nft"]["address"]
                )
            elif status == UserStatus.NEED_TO_PAY:
                url = url_for("main.buy_page", mode=mode)
            elif status == UserStatus.WAITING_FOR_PAYMENT:
                url = url_for("main.wait_page")
            elif status == UserStatus.PAYMENT_RECEIVED:
                url = url_for("main.mint_nft")
            elif status == UserStatus.WAITING_FOR_NFT:
                url = url_for("main.wait_nft")

        return dict(url=url)
