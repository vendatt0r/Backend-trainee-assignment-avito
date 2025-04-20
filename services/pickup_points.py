from datetime import datetime

from fastapi import HTTPException, status
import db

ALLOWED_CITIES = ["Москва", "Санкт-Петербург", "Казань"]

async def create_pickup_point(city: str):
    if city not in ALLOWED_CITIES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"ПВЗ можно создать только в городах: {', '.join(ALLOWED_CITIES)}"
        )

    async with db.db_pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO pickup_points (city)
            VALUES ($1)
            RETURNING id, city, created_at
            """,
            city
        )
        return dict(row)  # {'id': ..., 'city': ..., 'created_at': ...}

async def get_pickup_points_filtered(from_date: datetime, to_date: datetime, limit: int, offset: int):
    async with db.db_pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT DISTINCT pp.id, pp.city, pp.created_at
            FROM pickup_points pp
            JOIN intakes i ON pp.id = i.pickup_point_id
            WHERE i.created_at BETWEEN $1 AND $2
            ORDER BY pp.id
            LIMIT $3 OFFSET $4
            """,
            from_date, to_date, limit, offset
        )
        return [dict(row) for row in rows]

