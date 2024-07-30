"""Asynchronous Python client for AndrewsArnold."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

import aiohttp
from aiohttp.hdrs import METH_POST
from aioresponses import CallbackResult, aioresponses
import pytest
from yarl import URL

from aioandrewsarnold.exceptions import (
    AndrewsArnoldAuthenticationError,
    AndrewsArnoldConnectionError,
    AndrewsArnoldError,
)
from aioandrewsarnold.andrewsarnold import AndrewsArnoldClient
from tests import load_fixture

from .const import ANDREWS_ARNOLD_URL, HEADERS

if TYPE_CHECKING:
    from syrupy import SnapshotAssertion


async def test_authentication_error(
    responses: aioresponses,
    client: AndrewsArnoldClient,
    snapshot: SnapshotAssertion,
) -> None:
    """Test retrieving quotas but not authorized."""

    url = URL(ANDREWS_ARNOLD_URL).joinpath("broadband/quota")
    responses.post(
        url,
        status=200,
        body=load_fixture("authentication_error.json"),
    )

    with pytest.raises(AndrewsArnoldAuthenticationError):
        assert await client.get_quotas() == snapshot


async def test_putting_in_own_session(
    responses: aioresponses,
) -> None:
    """Test putting in own session."""
    responses.post(
        f"{ANDREWS_ARNOLD_URL}/broadband/quota",
        status=200,
        body=load_fixture("broadband_quota.json"),
    )
    async with aiohttp.ClientSession() as session:
        client = AndrewsArnoldClient(session=session)
        await client.get_quotas()
        assert client.session is not None
        assert not client.session.closed
        await client.close()
        assert not client.session.closed


async def test_creating_own_session(
    responses: aioresponses,
) -> None:
    """Test creating own session."""
    responses.post(
        f"{ANDREWS_ARNOLD_URL}/broadband/quota",
        status=200,
        body=load_fixture("broadband_quota.json"),
    )
    client = AndrewsArnoldClient(control_login="XXX", control_password="XXX")
    await client.get_quotas()
    assert client.session is not None
    assert not client.session.closed
    await client.close()
    assert client.session.closed


async def test_unexpected_server_response(
    responses: aioresponses,
    client: AndrewsArnoldClient,
) -> None:
    """Test handling unexpected response."""
    responses.post(
        f"{ANDREWS_ARNOLD_URL}/broadband/quota",
        status=200,
        headers={"Content-Type": "plain/text"},
        body="Yes",
    )
    with pytest.raises(AndrewsArnoldError):
        assert await client.get_quotas()


async def test_timeout(
    responses: aioresponses,
) -> None:
    """Test request timeout."""

    # Faking a timeout by sleeping
    async def response_handler(_: str, **_kwargs: Any) -> CallbackResult:
        """Response handler for this test."""
        await asyncio.sleep(2)
        return CallbackResult(body="Goodmorning!")

    url = URL(ANDREWS_ARNOLD_URL).joinpath("broadband/quota")
    responses.post(
        url,
        callback=response_handler,
    )
    async with AndrewsArnoldClient(request_timeout=1) as client:
        with pytest.raises(AndrewsArnoldConnectionError):
            assert await client.get_quotas()


async def test_quotas(
    responses: aioresponses,
    client: AndrewsArnoldClient,
    snapshot: SnapshotAssertion,
) -> None:
    """Test retrieving quotas."""

    url = URL(ANDREWS_ARNOLD_URL).joinpath("broadband/quota")
    responses.post(
        url,
        status=200,
        body=load_fixture("broadband_quota.json"),
    )
    assert await client.get_quotas() == snapshot

    responses.assert_called_once_with(
        f"{ANDREWS_ARNOLD_URL}/broadband/quota",
        METH_POST,
        headers=HEADERS,
        params=None,
        json={"control_login": "test", "control_password": "test"},
    )
