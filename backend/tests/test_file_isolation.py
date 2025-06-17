import asyncio
import os
from pathlib import Path

import pytest

from app.agents.tools.file_manager import FileManagerTool

USER_A = "user_a_test"
USER_B = "user_b_test"

FILE_TOOL = FileManagerTool()

pytestmark = pytest.mark.asyncio


audio = os.getenv("EDGE_WORKSPACE", "/tmp/edge_workspace")

@pytest.fixture(autouse=True)
async def _clean_workspace(tmp_path):
    # Point EDGE_WORKSPACE to a temp dir for tests
    os.environ["EDGE_WORKSPACE"] = str(tmp_path)
    yield
    # cleanup handled by tmp_path fixture

async def test_write_and_read_in_same_workspace():
    content = "hello world"
    await FILE_TOOL.run(
        mode="write",
        path="notes/hello.txt",
        content=content,
        auth_user_id=USER_A,
    )

    read_back = await FILE_TOOL.run(
        mode="read",
        path="notes/hello.txt",
        auth_user_id=USER_A,
    )
    assert read_back == content

async def test_cross_user_access_denied():
    content = "secret"
    await FILE_TOOL.run(
        mode="write",
        path="secret.txt",
        content=content,
        auth_user_id=USER_A,
    )

    with pytest.raises(FileNotFoundError):
        await FILE_TOOL.run(
            mode="read",
            path="secret.txt",
            auth_user_id=USER_B,
        )

async def test_path_traversal_blocked():
    with pytest.raises(ValueError):
        await FILE_TOOL.run(
            mode="write",
            path="../../../evil.txt",
            content="bad",
            auth_user_id=USER_A,
        ) 