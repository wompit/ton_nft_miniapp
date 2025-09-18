import asyncio
import json
from flask import url_for
from PIL import ImageFont, ImageDraw, Image

from pytoniq_core import Address
from pytoniq_tools.client import TonapiClient
from pytoniq_tools.nft import ItemStandard, CollectionStandard
from pytoniq_tools.nft.content import OffchainCommonContent
from pytoniq_tools.wallet import WalletV4R2

from config import NFT_COLLECTION_ADDRESS, TON_API_KEY, TON_WALLET_MNEMO, BASE_PATH
from controllers import _Controller
from models import User, NFTPassport
from utils import UserStatus


class GenerateNFTController(_Controller):
    def _call(self) -> str:
        self.log.info(f"Mint request - {self.request.json}")
        user = User.get(telegram_id=self.request_data["id"])
        mode = self.get_mode(user.wallet_address)
        url = url_for("main.buy_page", mode=mode)
        if user and user.status == UserStatus.PAYMENT_RECEIVED or mode != "default":
            index = self._get_nft_index()
            json_ipfs_hash, image_ipfs_hash = self.prepare_nft_image(user, mode, index)

            user.extra_data["ipfs"] = {"image": image_ipfs_hash, "json": json_ipfs_hash}

            transaction_hash, nft_address = asyncio.run(
                self.mint_nft(json_ipfs_hash, user.wallet_address, index)
            )

            user.extra_data["nft"] = {
                "transaction": transaction_hash,
                "address": nft_address,
            }

            user.status = UserStatus.WAITING_FOR_NFT
            user.save()

            url = url_for("main.wait_nft")

            NFTPassport.create(
                user=user,
                address=nft_address,
                mint_hash=transaction_hash,
                metadata_hash=json_ipfs_hash,
            )

        return url

    async def mint_nft(self, json_metadata: str, to_address: str, index: int):
        client = TonapiClient(api_key=TON_API_KEY, is_testnet=False)
        wallet, _, _, _ = WalletV4R2.from_mnemonic(TON_WALLET_MNEMO, client)
        to_address = Address(to_address)

        item = ItemStandard(
            index=index,
            collection_address=NFT_COLLECTION_ADDRESS,
        )
        body = CollectionStandard.build_mint_body(
            index=index,
            owner_address=to_address,
            content=OffchainCommonContent(
                uri=f"https://ipfs.filebase.io/ipfs/{json_metadata}"
            ),
        )

        tx_hash = await wallet.transfer(
            destination=NFT_COLLECTION_ADDRESS,
            amount=0.05,
            body=body,
        )
        return tx_hash, item.address.to_str()

    def prepare_nft_image(self, user, mode, index):
        if mode == "default":
            template_path = BASE_PATH + "static/images/light qr.png"
        else:
            template_path = BASE_PATH + f"static/images/{mode} qr.png"
        font_path = BASE_PATH + "static/images/CraftworkGrotesk-Medium.ttf"
        font = ImageFont.truetype(font_path, size=30)
        buble_font = ImageFont.truetype(
            BASE_PATH + "static/images/Perfograma.otf", size=35
        )

        template_image = Image.open(template_path)
        draw = ImageDraw.Draw(template_image)

        positions = {
            "Name": (120, 413),
            "Date of birth": (120, 520),
            "Race": (400, 520),
            "Planet": (120, 627),
            "Sex": (400, 627),
            "Position": (120, 737),
            "Index": (80, 240),
        }
        zeros = 13 - len(str(index))
        index = "ZZ-X" + "0" * zeros + str(index + 1)

        date_of_birth = user.date_of_birth.strftime("%Y-%m-%d")

        fill = (0, 0, 0) if mode != "dark" else (255, 255, 255)

        draw.text(positions["Name"], user.name, font=font, fill=fill)
        draw.text(positions["Date of birth"], date_of_birth, font=font, fill=fill)
        draw.text(positions["Race"], user.race, font=font, fill=fill)
        draw.text(positions["Planet"], user.planet, font=font, fill=fill)
        draw.text(positions["Sex"], user.sex, font=font, fill=fill)
        draw.text(positions["Position"], user.position, font=font, fill=fill)
        draw.text(positions["Index"], index, font=buble_font, fill=(255, 255, 2255))

        photo_image = Image.open(user.image_path).resize((150, 150))
        template_image.paste(
            photo_image, (template_image.width - photo_image.width - 90, 90)
        )

        # Сохранение NFT паспорта
        nft_path = f"{BASE_PATH}/nft/nft_{user.telegram_id}.png"
        template_image.save(nft_path)
        image_ipfs_hash = self.upload_file(nft_path, f"png/nft_{user.telegram_id}.png")

        nft_metadata = {
            "name": user.name,
            "description": "Ruzzia citizen passport",
            "image": f"ipfs://{image_ipfs_hash}",
            "attributes": [
                {"trait_type": "Date Of Birth", "value": date_of_birth},
                {"trait_type": "Sex", "value": user.sex},
                {"trait_type": "Race", "value": user.race},
                {"trait_type": "Planet", "value": user.planet},
                {"trait_type": "Position", "value": user.position},
            ],
        }
        self.log.info(f"NFT metabase: {nft_metadata}")
        json_path = BASE_PATH + f"nft/nft_{user.telegram_id}.json"
        with open(json_path, "w") as f:
            json.dump(nft_metadata, f)

        json_ipfs_hash = self.upload_file(
            json_path, f"json/nft_{user.telegram_id}.json"
        )
        return json_ipfs_hash, image_ipfs_hash
