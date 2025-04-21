import pytest

@pytest.mark.asyncio
async def test_intake_endpoints(client, conn):
    # Создаём точку самовывоза
    row = await conn.fetchrow(
        "INSERT INTO pickup_points (name, address) VALUES ('Точка', 'Адрес') RETURNING id"
    )
    pickup_point_id = row["id"]

    # Создание приёмки
    response = await client.post(f"/intakes/create/{pickup_point_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "in_progress"

    # Попытка создать вторую приёмку — должна быть ошибка
    response = await client.post(f"/intakes/create/{pickup_point_id}")
    assert response.status_code == 400
    assert "ещё не закрыта" in response.json()["detail"]

    # Закрытие приёмки
    intake_id = data["id"]
    response = await client.post(f"/intakes/close/{intake_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "Intake closed"
@pytest.mark.asyncio
async def test_pickup_point_endpoints(client):
    # Создание новой точки самовывоза
    response = await client.post("/pickup_points/create", json={"name": "ПВЗ 1", "address": "ул. Тестовая 1"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "ПВЗ 1"

    # Получение всех точек
    response = await client.get("/pickup_points/")
    assert response.status_code == 200
    points = response.json()
    assert len(points) == 1
    assert points[0]["address"] == "ул. Тестовая 1"


@pytest.mark.asyncio
async def test_items_endpoints(client, conn):
    # Вставка ПВЗ и приёмки
    pp = await conn.fetchrow("INSERT INTO pickup_points (name, address) VALUES ('Test', 'Addr') RETURNING id")
    intake = await conn.fetchrow("INSERT INTO intakes (status, pickup_point_id) VALUES ('in_progress', $1) RETURNING id", pp["id"])

    # Создание item
    response = await client.post(f"/items/create", json={
        "name": "Товар 1",
        "intake_id": intake["id"]
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Товар 1"
    assert data["intake_id"] == intake["id"]

    # Получение всех items
    response = await client.get("/items/")
    assert response.status_code == 200
    items = response.json()
    assert any(item["name"] == "Товар 1" for item in items)

