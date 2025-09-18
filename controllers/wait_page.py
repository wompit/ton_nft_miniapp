from controllers import _Controller


class WaitPageController(_Controller):
    need_to_render = True

    def _call(self) -> str:
        if self.is_nft:
            return "wait_nft.html"
        return "wait_page.html"
