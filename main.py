from fastapi import FastAPI
import db, auth, utils
from routers import pickup_points, intakes, items

app = FastAPI()

app.include_router(auth.router)
app.include_router(pickup_points.router)
app.include_router(intakes.router)
app.include_router(items.router)

@app.on_event("startup")
async def startup():
    await db.connect_to_db()
    await utils.init_db(db.db_pool)

@app.on_event("shutdown")
async def shutdown():
    await db.close_db()
