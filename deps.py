from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Literal

# Типы пользователей
UserRole = Literal["client", "moderator", "employee_pvz"]

# Используем стандартный Bearer
security = HTTPBearer()

# Хранилище токенов
from auth import token_store

def get_current_user_role(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserRole:
    token = credentials.credentials
    role = token_store.get(token)
    if not role:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return role

def require_role(required_role: UserRole):
    def dependency(role: UserRole = Depends(get_current_user_role)):
        if role != required_role:
            raise HTTPException(status_code=403, detail="Forbidden")
        return role
    return dependency
