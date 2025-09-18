from controllers import _Controller
from config import NFT_COLLECTION_ADDRESS


class FinalPageController(_Controller):
    need_to_render = True

    def _call(self, nft_address) -> tuple:
        return "final.html", dict(
            passport_url=f"https://getgems.io/collection/{NFT_COLLECTION_ADDRESS}/{nft_address}"
        )
