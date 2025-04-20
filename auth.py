from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, EmailStr
from typing import Literal
import secrets
import db

router = APIRouter()

# Типы пользователей
UserRole = Literal["client", "moderator", "employee_pvz"]

# In-memory хранилище токенов (можно заменить на Redis)
token_store = {}

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    role: UserRole

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    token: str

@router.post("/register", response_model=TokenResponse)
async def register_user(data: RegisterRequest):
    async with db.db_pool.acquire() as conn:
        existing = await conn.fetchrow("SELECT id FROM users WHERE email = $1", data.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        await conn.execute(
            "INSERT INTO users (email, password, role) VALUES ($1, $2, $3)",
            data.email, data.password, data.role
        )

        token = secrets.token_hex(16)
        token_store[token] = data.role
        return TokenResponse(token=token)

@router.post("/login", response_model=TokenResponse)
async def login_user(data: LoginRequest):
    async with db.db_pool.acquire() as conn:
        user = await conn.fetchrow("SELECT * FROM users WHERE email = $1 AND password = $2", data.email, data.password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = secrets.token_hex(16)
        token_store[token] = user["role"]
        return TokenResponse(token=token)

@router.get("/dummyLogin", response_model=TokenResponse)
async def dummy_login(role: UserRole):
    token = secrets.token_hex(16)
    token_store[token] = role
    return TokenResponse(token=token)

# 🔐 Получение токена из заголовка Authorization
def get_token_from_header(authorization: str = Header(...)) -> str:
    print("Authorization header received:", authorization)
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")
    return authorization.removeprefix("Bearer ").strip()

# ✅ Используем get_token_from_header как Depends в get_current_user_role
def get_current_user_role(token: str = Depends(get_token_from_header)) -> UserRole:
    role = token_store.get(token)
    if not role:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return role
