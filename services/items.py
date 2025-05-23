from fastapi import HTTPException
from starlette import status

import db

async def create_item(item_type: str, pickup_point_id: int):
    async with db.db_pool.acquire() as conn:
        # Найти последнюю открытую приёмку
        intake = await conn.fetchrow("""
            SELECT id FROM intakes
            WHERE pickup_point_id = $1 AND status = 'in_progress'
            ORDER BY created_at DESC
            LIMIT 1
        """, pickup_point_id)

        if not intake:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нет активной приёмки для этого ПВЗ"
            )

        intake_id = intake["id"]

        # Добавить товар к найденной приёмке
        await conn.execute(
            "INSERT INTO items (type, intake_id) VALUES ($1, $2)",
            item_type, intake_id
        )
        return {"status": "Item added to intake", "intake_id": intake_id}

async def delete_last_item_from_open_intake(pickup_point_id: int):
    async with db.db_pool.acquire() as conn:
        # 1. Найти активную (незакрытую) приёмку
        intake = await conn.fetchrow("""
            SELECT id FROM intakes
            WHERE pickup_point_id = $1 AND status = 'in_progress'
            ORDER BY created_at DESC
            LIMIT 1
        """, pickup_point_id)

        if not intake:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Нет активной приёмки для этого ПВЗ"
            )

        intake_id = intake['id']

        # 2. Найти последний добавленный товар (по ID или по времени)
        item = await conn.fetchrow("""
            SELECT id FROM items
            WHERE intake_id = $1
            ORDER BY id DESC  -- ID инкрементируется => соответствует LIFO
            LIMIT 1
        """, intake_id)

        if not item:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нет товаров для удаления"
            )

        item_id = item['id']

        # 3. Удалить товар
        await conn.execute("DELETE FROM items WHERE id = $1", item_id)

        return {"status": f"Удалён товар с id={item_id}"}
