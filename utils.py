from models import CREATE_USERS_TABLE, CREATE_PICKUP_POINTS_TABLE, CREATE_INTAKES_TABLE, CREATE_ITEMS_TABLE
import asyncpg

async def init_db(pool: asyncpg.Pool):
    async with pool.acquire() as conn:
        await conn.execute(CREATE_USERS_TABLE)
        await conn.execute(CREATE_PICKUP_POINTS_TABLE)
        await conn.execute(CREATE_INTAKES_TABLE)
        await conn.execute(CREATE_ITEMS_TABLE)
