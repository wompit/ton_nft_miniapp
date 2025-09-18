from controllers import _Controller


class CardPageController(_Controller):
    need_to_render = True

    def _call(self, mode) -> tuple:
        return "index.html", dict(mode=mode)
