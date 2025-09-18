import asyncio
import os
import base64
import json

from datetime import datetime
from config import BASE_PATH, TON_WALLET_ADDRESS, ZOOBLE_ADDRESS, ZOOBLE_AMOUNT
from controllers import _Controller
from models import User
from pytoniq import begin_cell
from utils import UserStatus, PRE_SALE


class SubmitController(_Controller):
    def _call(self) -> dict:
        telegram_data = json.loads(self.request_data["user_data"])
        wallet_data = json.loads(self.request_data["account"])

        photo = self.request.files["photo"]
        photo_path = os.path.join(BASE_PATH, f"photos/{photo.filename}")
        photo.save(photo_path)

        User.get_or_create(
            telegram_id=telegram_data["id"],
            defaults=dict(
                name=self.request_data["name"],
                wallet_address=wallet_data["address"],
                date_of_birth=datetime.strptime(self.request_data["date_of_birth"], '%d.%m.%Y'),
                race=self.request_data["race"],
                planet=self.request_data["planet"],
                sex=self.request_data["sex"],
                position=self.request_data["position"],
                image_path=photo_path,
                status=UserStatus.NEED_TO_PAY,
                extra_data={"telegram_data": telegram_data, "wallet_data": wallet_data},
            ),
        )
        telegram_id = telegram_data["id"]
        mode = self.get_mode(wallet_data["address"])
        if mode == "default":
            jetton_payload = self.create_usdt_payload(
                telegram_id, wallet_data["address"]
            )
        else:
            jetton_payload = {"mode": mode}
        self.log.info("Jetton payload: %s", jetton_payload)
        # jetton_payload = self.create_usdt_payload('test', 'UQAV3RvNzkoG6AlbP3t52gczRuccYIH2MQaEJ89E4YKi7_k_')
        return jetton_payload

    def create_usdt_payload(self, telegram_id, user_address):
        forward_payload = (
            begin_cell()
            .store_uint(0, 32)  # TextComment op-code
            .store_snake_string(str(telegram_id))
            .end_cell()
        )
        transfer_cell = (
            begin_cell()
            .store_uint(0xF8A7EA5, 32)  # Jetton Transfer op-code
            .store_uint(0, 64)  # query_id
            .store_coins(int(ZOOBLE_AMOUNT))  # Jetton amount to transfer in nanojetton
            .store_address(TON_WALLET_ADDRESS)  # Destination address
            .store_address(TON_WALLET_ADDRESS)  # Response address
            .store_bit(0)  # Custom payload is None
            .store_coins(1)  # Ton forward amount in nanoton
            .store_bit(1)  # Store forward_payload as a reference
            .store_ref(forward_payload)  # Forward payload
            .end_cell()
        )

        jetton_payload = {
            "to_address": TON_WALLET_ADDRESS,
            "from_address": user_address,
            "amount": ZOOBLE_AMOUNT,
            "comment": telegram_id,
            "jetton_address": asyncio.run(
                self.get_jetton_address(user_address, ZOOBLE_ADDRESS)
            ),
            "payload": base64.urlsafe_b64encode(transfer_cell.to_boc()).decode(),
        }

        return jetton_payload

    async def get_jetton_address(self, from_address, jetton_master):
        client = await self._get_client()
        return (
            (
                await client.run_get_method(
                    address=jetton_master,
                    method="get_wallet_address",
                    stack=[
                        begin_cell()
                        .store_address(from_address)
                        .end_cell()
                        .begin_parse()
                    ],
                )
            )[0]
            .load_address()
            .to_str()
        )
