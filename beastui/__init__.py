__version__ = '0.19.0-dev.2'


def _install_runtime_ui_patches():
    from .engine import BeastUI
    from .platform_surfaces_v2 import install
    install(BeastUI)


_install_runtime_ui_patches()
