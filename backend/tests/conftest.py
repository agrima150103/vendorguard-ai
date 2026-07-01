"""
Shared pytest fixtures for VendorGuard API tests.

Each test uses a separate SQLite database inside pytest's temporary directory.
This avoids Windows file-locking errors caused by manually deleting an active
SQLite database.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app


@pytest.fixture()
def client(tmp_path):
    """
    Return a FastAPI test client backed by a unique temporary database.

    TestClient is used as a context manager so FastAPI startup and shutdown
    complete before pytest cleans the temporary directory.
    """

    test_database = tmp_path / "vendorguard_test.db"

    original_db_path = settings.db_path
    settings.db_path = str(test_database)

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        settings.db_path = original_db_path