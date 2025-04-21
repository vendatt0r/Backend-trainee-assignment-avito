import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta

from services.pickup_points import create_pickup_point, get_pickup_points_filtered
from services.intakes import create_intake, close_intake
from services.items import create_item


@pytest.mark.asyncio
async def test_create_pickup_point_api(client: AsyncClient):  # Добавлен тип
    # Получаем токен модератора
    mod_resp = await client.get("/dummyLogin", params={"role": "moderator"})
    headers = {"Authorization": f"Bearer {mod_resp.json()['token']}"}

    # Создаем ПВЗ
    response = await client.post(
        "/pickup-points/",
        json={"city": "Москва"},
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["city"] == "Москва"




@pytest.mark.asyncio
async def test_create_intake(test_db, client):
    # Модератор создаёт ПВЗ
    mod_resp = await client.get("/dummyLogin", params={"role": "moderator"})
    headers_mod = {"Authorization": f"Bearer {mod_resp.json()['token']}"}
    pp_resp = await client.post("/pickup-points/", json={"city": "СПб"}, headers=headers_mod)
    pp_id = pp_resp.json()["id"]

    # Сотрудник ПВЗ создаёт приёмку
    emp_resp = await client.get("/dummyLogin", params={"role": "employee_pvz"})
    headers_emp = {"Authorization": f"Bearer {emp_resp.json()['token']}"}

    result = await client.post("/intakes/", json={"pickup_point_id": pp_id}, headers=headers_emp)

    assert result.status_code == 200
    result_json = result.json()
    assert "id" in result_json
    assert result_json["pickup_point_id"] == pp_id
    assert result_json["status"] == "in_progress"


@pytest.mark.asyncio
async def test_create_item(test_db, client):
    # Модератор создаёт ПВЗ
    mod_resp = await client.get("/dummyLogin", params={"role": "moderator"})
    headers_mod = {"Authorization": f"Bearer {mod_resp.json()['token']}"}
    pp_resp = await client.post("/pickup-points/", json={"city": "Казань"}, headers=headers_mod)
    pp_id = pp_resp.json()["id"]

    # Сотрудник ПВЗ создаёт приёмку
    emp_resp = await client.get("/dummyLogin", params={"role": "employee_pvz"})
    headers_emp = {"Authorization": f"Bearer {emp_resp.json()['token']}"}
    intake_resp = await client.post("/intakes/", json={"pickup_point_id": pp_id}, headers=headers_emp)
    intake_id = intake_resp.json()["id"]

    # Добавляем товар
    item_resp = await client.post("/items/", json={
        "type": "electronics",
        "pickup_point_id": pp_id,
        "intake_id": intake_id  # Указываем intake_id явно
    }, headers=headers_emp)

    assert item_resp.status_code == 200
    item_resp_json = item_resp.json()
    assert item_resp_json["status"] == "Item added to intake"
    assert "intake_id" in item_resp_json


@pytest.mark.asyncio
async def test_close_intake(test_db, client):
    # Модератор создаёт ПВЗ
    mod_resp = await client.get("/dummyLogin", params={"role": "moderator"})
    headers_mod = {"Authorization": f"Bearer {mod_resp.json()['token']}"}
    pp_resp = await client.post("/pickup-points/", json={"city": "Новосибирск"}, headers=headers_mod)
    pp_id = pp_resp.json()["id"]

    # Сотрудник ПВЗ создаёт приёмку
    emp_resp = await client.get("/dummyLogin", params={"role": "employee_pvz"})
    headers_emp = {"Authorization": f"Bearer {emp_resp.json()['token']}"}
    intake_resp = await client.post("/intakes/", json={"pickup_point_id": pp_id}, headers=headers_emp)
    intake_id = intake_resp.json()["id"]

    # Добавляем товар в приёмку
    await client.post("/items/", json={
        "type": "electronics",
        "pickup_point_id": pp_id,
        "intake_id": intake_id
    }, headers=headers_emp)

    # Закрываем приёмку
    close_resp = await client.post(f"/intakes/{intake_id}/close", json={"status": "closed"}, headers=headers_emp)

    assert close_resp.status_code == 200
    close_resp_json = close_resp.json()
    assert close_resp_json["status"] == "closed"
