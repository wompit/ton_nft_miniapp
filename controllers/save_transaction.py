import json
from datetime import datetime
from flask import url_for

from controllers import _Controller
from models import User
from utils import UserStatus


class SaveTransactionController(_Controller):
    def _call(self) -> dict:
        user_data = json.loads(self.request_data["user_data"])
        boc = self.request_data["boc[boc]"]

        user = User.get(telegram_id=user_data["id"])
        user.extra_data["transaction"] = {
            "boc": boc,
            "sending_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        user.status = UserStatus.WAITING_FOR_PAYMENT
        user.save()
        return dict(url=url_for("main.wait_page"))
