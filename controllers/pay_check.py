import asyncio
from flask import url_for
from datetime import datetime, timedelta

from config import TON_WALLET_ADDRESS
from controllers import _Controller
from models import User
from utils import UserStatus


class PayCheckController(_Controller):
    def _call(self) -> str | None:
        user = User.get(telegram_id=self.request_data["id"])
        mode = self.get_mode(user.wallet_address)
        if asyncio.run(self.check(user.telegram_id)):
            user.status = UserStatus.PAYMENT_RECEIVED
            user.save(only=[User.status])
            return url_for("main.mint_nft")

        if user.extra_data.get("transaction", {}).get("sending_time"):
            sending_time = datetime.strptime(
                user.extra_data["transaction"]["sending_time"], "%Y-%m-%d %H:%M:%S"
            )
            if sending_time < datetime.now() - timedelta(minutes=2):
                user.status = UserStatus.NEED_TO_PAY
                user.save(only=[User.status])
                return url_for("main.buy_page", mode=mode)

    async def check(self, telegram_id):
        user = User.get(telegram_id=telegram_id)
        comment = str(telegram_id)
        client = await self._get_client()
        transactions = await client.get_transactions(TON_WALLET_ADDRESS, count=16)
        for tr in transactions:
            try:
                body_slice = tr.in_msg.body.begin_parse()
                if len(body_slice.bits) < 32:  # Check if there are enough bits
                    continue
                op_code = body_slice.load_uint(32)
                if op_code == 0x7362D09C:
                    jetton_sender, jetton_amount, tr_comment = self._process_cell(tr)
                    if tr_comment == comment:
                        if not self.status_check(tr):
                            user.status = UserStatus.NEED_TO_PAY
                            user.save()
                            return False
                        return True
            except Exception as e:
                self.log.exception(e)
        return False

    @staticmethod
    def status_check(transaction):
        description = transaction.description
        action = description.action
        if action:
            action_success = action.success
        else:
            action_success = True

        return not all(
            (
                description.aborted,
                description.destroyed,
                description.bounce,
                action_success,
            )
        )

    def _process_cell(self, transaction):
        try:
            body_slice = transaction.in_msg.body.begin_parse()
            body_slice.load_uint(96)  # skip query_id
            jetton_amount = body_slice.load_coins()
            jetton_sender = body_slice.load_address().to_str(1, 1, 1)
            if body_slice.load_bit():
                forward_payload = body_slice.load_ref().begin_parse()
            else:
                forward_payload = body_slice

            comment = self._get_comment(forward_payload)

            return jetton_sender, jetton_amount, comment
        except Exception as e:
            self.log.exception(e)
            return None, None, None

    @staticmethod
    def _get_comment(cell) -> str | None:
        comment = None
        if len(cell.bits) >= 32:
            forward_payload_op_code = cell.load_uint(32)
            if forward_payload_op_code == 0:
                comment = cell.load_snake_string()
        return comment
