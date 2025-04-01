import pytest
import pytest_asyncio
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from main import app, get_db, Base

DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope="module", autouse=True)
async def prepare_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@pytest_asyncio.fixture(scope="module")
async def db():
    async with engine.connect() as connection:
        async with connection.begin():
            session = TestingSessionLocal(bind=connection)
            yield session
            await session.close()

@pytest_asyncio.fixture(scope="module")
async def client(db):
    async def override_get_db():
        try:
            yield db
        finally:
            await db.close()

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

@pytest.mark.asyncio
async def test_token(client):
    response = await client.post("/token", json={"username": "admin"})
    data = response.json()
    assert "access_token" in data
    assert isinstance(data["access_token"], str)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_post_task(client):
    response = await client.post("/token", json={"username": "admin"})

    data = response.json()
    assert isinstance(data["access_token"], str)

    token = data["access_token"]
    headers = {
        "Authorization": f"Bearer {token}"
    }

    task_data = {
        "datetime_to_do": "2025-04-01T07:35:16.133Z",
        "task_info": "string"
    }

    response = await client.post("/tasks/create", headers=headers, json=task_data)

    assert response.status_code == 201

    response_data = response.json()
    assert isinstance(response_data, dict)
    assert "datetime_to_do" in response_data
    assert "task_info" in response_data

@pytest.mark.asyncio
async def test_create_and_get_task(client):
    response = await client.post("/token", json={"username": "admin"})
    data = response.json()
    assert isinstance(data["access_token"], str)

    token = data["access_token"]
    headers = {
        "Authorization": f"Bearer {token}"
    }

    task_data = {
        "datetime_to_do": "2025-04-01T07:35:16.133Z",
        "task_info": "slovo"
    }
    post_response = await client.post("/tasks/create", headers=headers, json=task_data)
    assert post_response.status_code == 201

    tasks_response = await client.get("/tasks", headers=headers)
    assert tasks_response.status_code == 200

    tasks = tasks_response.json()
    assert isinstance(tasks, list)
    assert any(task["task_info"] == "slovo" for task in tasks)

@pytest.mark.asyncio
async def test_create_update_and_get_task(client):
    response = await client.post("/token", json={"username": "admin"})
    data = response.json()
    assert isinstance(data["access_token"], str)

    token = data["access_token"]
    headers = {
        "Authorization": f"Bearer {token}"
    }

    task_data = {
        "datetime_to_do": "2025-04-01T07:35:16.133Z",
        "task_info": "slovo"
    }
    post_response = await client.post("/tasks/create", headers=headers, json=task_data)
    assert post_response.status_code == 201

    tasks_response = await client.get("/tasks", headers=headers)
    assert tasks_response.status_code == 200

    tasks = tasks_response.json()
    assert isinstance(tasks, list)

    task = next(task for task in tasks if task["task_info"] == "slovo")
    task_id = int(task["id"])

    assert task_id is not None

    updated_task_data = {
        "datetime_to_do": "2026-04-01T07:35:16.133Z",
        "task_info": "novoe slovo"
    }
    patch_response = await client.patch(f"/tasks/{task_id}/update", headers=headers, json=updated_task_data)
    assert patch_response.status_code == 200

    get_response = await client.get(f"/tasks/{task_id}", headers=headers)
    assert get_response.status_code == 200

    updated_task = get_response.json()
    assert updated_task["task_info"] == "novoe slovo"
