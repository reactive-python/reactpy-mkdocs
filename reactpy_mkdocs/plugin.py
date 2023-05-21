import asyncio
import threading
from pathlib import Path
from shutil import copyfile
from typing import Callable, Literal

from mkdocs.config import Config
from mkdocs.config.base import Config
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.livereload import LiveReloadServer
from mkdocs.plugins import BasePlugin
from reactpy.backend import starlette as reactpy_starlette

from reactpy_mkdocs.reactpy_frame import reactpy_frame

JS_BUNDLE = Path(__file__).parent / "static" / "reactpy-mkdocs.mjs"
JS_BASE_URL_TEMPLATE = "const BASE_URL = {};"
ORIGINAL_JS_BASE_URL = JS_BASE_URL_TEMPLATE.format("document.location.origin")


class ReactPyPluginConfig(Config):
    dev_host: str = "localhost"
    dev_port: int = 5000


class ReactPyPlugin(BasePlugin[ReactPyPluginConfig]):
    """Plugin for MkDocs that allows embedding ReactPy components in Markdown files"""

    serving: bool = False

    def on_startup(
        self, command: Literal["build", "gh-deploy", "serve"], dirty: bool
    ) -> None:
        self.serving = command == "serve"

    def on_config(self, config: MkDocsConfig) -> Config | None:
        config.extra_javascript.append("reactpy/reactpy-mkdocs.js")

    def on_post_build(self, config: MkDocsConfig):
        reacpy_site_dir = Path(config.site_dir) / "reactpy"
        reacpy_site_dir.mkdir(exist_ok=True)
        reactpy_mkdocs_js = reacpy_site_dir / "reactpy-mkdocs.js"
        copyfile(JS_BUNDLE, reactpy_mkdocs_js)

        if self.serving:
            dev_base_url = f"http://{self.config.dev_host}:{self.config.dev_port}"
            reactpy_dev_base_url = JS_BASE_URL_TEMPLATE.format(f"'{dev_base_url}'")
            reactpy_mkdocs_js.write_text(
                reactpy_mkdocs_js.read_text().replace(
                    ORIGINAL_JS_BASE_URL, reactpy_dev_base_url
                )
            )

    def on_serve(
        self,
        server: LiveReloadServer,
        config: MkDocsConfig,
        builder: Callable[[], None],
    ):
        run_reactpy_server_in_thread(self.config.dev_host, self.config.dev_port)
        return server


def run_reactpy_server_in_thread(host: str, port: int) -> None:
    app = reactpy_starlette.create_development_app()
    opts = reactpy_starlette.Options(cors=True)
    reactpy_starlette.configure(app, reactpy_frame, opts)

    def target():
        asyncio.run(reactpy_starlette.serve_development_app(app, host=host, port=port))

    thread = threading.Thread(target=target, daemon=True)
    thread.start()
