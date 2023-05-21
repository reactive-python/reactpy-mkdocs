import os
from threading import Thread
from typing import Any
from pathlib import Path
from playwright.sync_api import Page
import pytest
from pytest import FixtureRequest
import yaml
from mkdocs.commands.serve import serve as serve_mkdocs

WORK_DIR = Path(__file__).parent
MKDOCS_YML = WORK_DIR / "mkdocs.yml"
COMPONENTS_DIR = WORK_DIR / "components"
DOCS_DIR = WORK_DIR / "docs"
# pick a different addr than the default to avoid conflicts
MKDOCS_ADDR = "127.0.0.1:8000"


@pytest.fixture
def page(page: Page, request: FixtureRequest) -> None:
    _, _, test_module_name = request.module.__name__.rpartition(".")
    module_name = test_module_name[5:]  # strip "test_" prefix
    page.goto(f"http://{MKDOCS_ADDR}/{module_name}/index.html", timeout=5000)
    return page


@pytest.fixture(scope="session", autouse=True)
def mkdocs_server() -> None:
    _check_project_structure()
    os.chdir(WORK_DIR)
    Thread(target=lambda: serve_mkdocs(dev_addr=MKDOCS_ADDR), daemon=True).start()


def _check_project_structure():
    """check that for each component file there is a docs page and test file"""
    mkdocs_yml = _load_mkdocs_yml()
    for component_file in COMPONENTS_DIR.iterdir():
        if (
            component_file.name.startswith("_")
            or component_file.suffix != ".py"
            or component_file.stem.startswith("test_")
        ):
            continue

        component_name = component_file.stem
        docs_file = DOCS_DIR / f"{component_name}.md"
        test_file = COMPONENTS_DIR / f"test_{component_name}.py"
        nav_entry = str(docs_file.relative_to(DOCS_DIR))

        assert docs_file.exists(), f"missing {docs_file.relative_to(WORK_DIR)}"
        assert test_file.exists(), f"missing {docs_file.relative_to(WORK_DIR)}"
        assert nav_entry in mkdocs_yml["nav"], f"missing {nav_entry} in mkdocs.yml nav"


def _load_mkdocs_yml() -> Any:
    return yaml.safe_load(MKDOCS_YML.open("r"))
