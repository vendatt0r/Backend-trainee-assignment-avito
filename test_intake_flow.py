import pytest
import httpx

BASE_URL = "http://localhost:8080"  # Убедись, что сервер стартует на этом порту


@pytest.mark.asyncio
async def test_full_flow():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # 1. Аутентификация
        mod_resp = await client.get("/dummyLogin", params={"role": "moderator"})
        emp_resp = await client.get("/dummyLogin", params={"role": "employee_pvz"})

        headers_mod = {"Authorization": f"Bearer {mod_resp.json()['token']}"}
        headers_emp = {"Authorization": f"Bearer {emp_resp.json()['token']}"}

        # 2. Создание ПВЗ
        pp_resp = await client.post("/pickup-points/",
                                    json={"city": "Москва"},
                                    headers=headers_mod
                                    )
        pp_id = pp_resp.json()["id"]

        # 3. Создание приёмки
        intake_resp = await client.post("/intakes/",
                                        json={"pickup_point_id": pp_id},
                                        headers=headers_emp
                                        )
        intake_id = intake_resp.json()["id"]

        # 4. Добавление товаров с проверкой
        for i in range(50):
            item_resp = await client.post("/items/",
                                          json={
                                              "type": "электроника",
                                              "pickup_point_id": pp_id,
                                              "intake_id": intake_id  # Явно указываем intake_id
                                          },
                                          headers=headers_emp
                                          )
            assert item_resp.status_code == 200, (
                f"Ошибка при создании товара {i + 1}: {item_resp.status_code}\n"
                f"Ответ: {item_resp.text}"
            )

        # 5. Закрытие приёмки с проверкой тела ответа
        close_resp = await client.post(
            f"/intakes/{pp_id}/close",
            headers=headers_emp,
            json={"status": "closed"}  # Добавляем параметры если требуется
        )

        # Детальный анализ ошибки
        if close_resp.status_code != 200:
            print(f"Ошибка закрытия приёмки. Ответ сервера: {close_resp.text}")
            print(f"Текущий статус приёмки: {intake_resp.json()}")
            print(f"Добавленные товары: {i + 1} шт")

        assert close_resp.status_code == 200, (
            f"Не удалось закрыть приёмку. Статус: {close_resp.status_code}\n"
            f"Причина: {close_resp.text}"
        )
