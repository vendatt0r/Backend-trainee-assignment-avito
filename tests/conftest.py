import asyncio
import pytest
from httpx import AsyncClient
from main import app

@pytest.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client  # Важно: yield client, а не c
