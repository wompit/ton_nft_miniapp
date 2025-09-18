from controllers import _Controller


class StartPageController(_Controller):
    need_to_render = True

    def _call(self) -> str:
        return "base.html"
