from controllers import _Controller


class MintNFTController(_Controller):
    need_to_render = True

    def _call(self) -> str:
        return "mint_nft.html"
