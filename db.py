import asyncpg
from fastapi import FastAPI

DATABASE_URL="postgresql://postgres:123@localhost/pvz"

db_pool: asyncpg.Pool = None

async def connect_to_db():
    global db_pool
    print("[DB] Connecting to database...")
    db_pool = await asyncpg.create_pool(DATABASE_URL)
    print("[DB] Connected!")

async def close_db():
    await db_pool.close()
