from fastapi import HTTPException
from starlette import status

import db

async def create_intake(pickup_point_id: int):
    async with db.db_pool.acquire() as conn:
        # Проверка: есть ли незакрытая приёмка
        existing_intake = await conn.fetchrow(
            """
            SELECT id FROM intakes
            WHERE pickup_point_id = $1 AND status = 'in_progress'
            """,
            pickup_point_id
        )

        if existing_intake:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Невозможно создать новую приёмку: предыдущая приёмка ещё не закрыта."
            )

        # Создание новой приёмки
        row = await conn.fetchrow(
            """
            INSERT INTO intakes (status, pickup_point_id)
            VALUES ('in_progress', $1)
            RETURNING id, status, pickup_point_id, created_at
            """,
            pickup_point_id
        )
        return dict(row)

async def close_intake(pickup_point_id: int):
    async with db.db_pool.acquire() as conn:
        # Закрываем последнюю приёмку со статусом 'in_progress' для этого pickup_point
        result = await conn.execute(
            """
            UPDATE intakes
            SET status = 'close'
            WHERE id = (
                SELECT id FROM intakes
                WHERE pickup_point_id = $1 AND status = 'in_progress'
                ORDER BY created_at DESC
                LIMIT 1
            )
            """,
            pickup_point_id
        )

        if result == "UPDATE 0":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нет открытых приёмок для данного пункта выдачи."
            )

        return {"status": "Intake closed"}

