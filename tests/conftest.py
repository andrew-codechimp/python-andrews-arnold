"""Asynchronous Python client for AndrewsArnold."""

from typing import AsyncGenerator, Generator

import aiohttp
from aioresponses import aioresponses
import pytest

from aioandrewsarnold import AndrewsArnoldClient
from syrupy import SnapshotAssertion

from .syrupy import AndrewsArnoldSnapshotExtension


@pytest.fixture(name="snapshot")
def snapshot_assertion(snapshot: SnapshotAssertion) -> SnapshotAssertion:
    """Return snapshot assertion fixture with the AndrewsArnold extension."""
    return snapshot.use_extension(AndrewsArnoldSnapshotExtension)


@pytest.fixture(name="client")
async def client() -> AsyncGenerator[AndrewsArnoldClient, None]:
    """Return a AndrewsArnold client."""
    async with aiohttp.ClientSession() as session, AndrewsArnoldClient(
        control_login="test",
        control_password="test",
        session=session,
    ) as andrews_arnold_client:
        yield andrews_arnold_client


@pytest.fixture(name="responses")
def aioresponses_fixture() -> Generator[aioresponses, None, None]:
    """Return aioresponses fixture."""
    with aioresponses() as mocked_responses:
        yield mocked_responses
