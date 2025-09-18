import json
from flask import send_file
from config import BASE_PATH
from controllers import _Controller


class NFTConfigController(_Controller):
    def call(self, nft_name) -> dict:
        if "json" in nft_name:
            with open(f"{BASE_PATH}nft/{nft_name}", "r") as f:
                return json.load(f)
        else:
            return send_file(f"{BASE_PATH}nft/{nft_name}", mimetype="image/gif")
