"""Shared pytest fixtures for moat-research tests."""
from pathlib import Path

import pytest


@pytest.fixture
def tmp_repo(tmp_path: Path) -> Path:
    """An empty temp directory standing in for a fresh moat-research repo."""
    return tmp_path
