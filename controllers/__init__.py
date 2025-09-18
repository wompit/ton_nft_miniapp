import boto3
import requests
import pytz
from datetime import datetime, timedelta
from flask import Response, render_template, jsonify
from pytoniq import LiteClient

from config import TON_API_KEY, NFT_COLLECTION_ADDRESS, FILEBASE_SECRET, FILEBASE_KEY
from models import NFTPassport, User
from utils import Logger, get_request_data, PRE_SALE, fh

utc = pytz.UTC


class _Controller:
    need_to_render = False

    def __init__(self, request, is_nft=False):
        self.log = Logger(fh, self.__class__.__name__)
        self.is_nft = is_nft
        self.request = request
        try:
            self.request_data = get_request_data(self.request)
        except:
            self.request_data = {}

        self.s3 = boto3.client(
            "s3",
            endpoint_url="https://s3.filebase.com",
            aws_access_key_id=FILEBASE_KEY,
            aws_secret_access_key=FILEBASE_SECRET,
        )

    def call(self, *args, **kwargs) -> str | Response:
        result = None
        data = "base.html"
        try:
            self.log.info("Request data: %s" % self.request_data)
            data = self._call(*args, **kwargs)
            message = self.log.error_msg if self.log.error_msg else "Ok"
            result = dict(success=True, data=data, message=message, error_code=0)
        except Exception as ex:
            self.log.exception("Error during %s call" % self.__class__.__name__)
            result = dict(
                success=False,
                data=None,
                message=str(ex),
                error_code=2000,
            )
        finally:
            if self.need_to_render:
                if isinstance(data, tuple):
                    return render_template(data[0], **data[1])
                return render_template(data)
            if not data:
                result["success"] = False
            self.log.info("Result: %s" % result)
            return jsonify(result)

    def _call(self, *args, **kwargs) -> dict:
        raise NotImplementedError("_call from %s" % self.__class__.__name__)

    @staticmethod
    def get_mode(wallet):
        return PRE_SALE.get(wallet, "default")

    @staticmethod
    async def _get_client():
        client = LiteClient.from_mainnet_config(ls_i=1, trust_level=2, timeout=10)
        await client.connect()
        await client.reconnect()
        return client

    @staticmethod
    def check_nft_ownership(wallet):
        headers = {"Authorization": f"Bearer {TON_API_KEY}"}
        params = {
            "collection": NFT_COLLECTION_ADDRESS,
            "limit": 1000,
            "offset": 0,
            "indirect_ownership": "false",
        }

        url = f"https://tonapi.io/v2/accounts/{wallet}/nfts"
        res = requests.get(url, headers=headers, params=params).json()
        count = len(res.get("nft_items", []))

        user_nft = (
            NFTPassport.select()
            .join(User)
            .where(User.wallet_address == wallet)
            .order_by(NFTPassport.created.desc())
            .first()
        )
        if (
            user_nft
            and user_nft.created.replace(tzinfo=utc)
            <= datetime.now().replace(tzinfo=utc) - timedelta(minutes=5)
            and not count
        ):
            user_nft.success = False
            user_nft.save()
        return res.get("nft_items", [])

    @staticmethod
    def _get_nft_index():
        headers = {"Authorization": f"Bearer {TON_API_KEY}"}

        url = f"https://tonapi.io/v2/nfts/collections/{NFT_COLLECTION_ADDRESS}"
        res = requests.get(url, headers=headers).json()
        return res.get(
            "next_item_index",
            NFTPassport.select().where(NFTPassport.success == True).count(),
        )

    def upload_file(self, file_path, name):
        data = open(file_path, "rb")
        res = self.s3.put_object(Body=data, Bucket="ruzzia", Key=name)
        return res["ResponseMetadata"]["HTTPHeaders"]["x-amz-meta-cid"]
