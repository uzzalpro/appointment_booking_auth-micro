import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import (APIKeyHeader, HTTPAuthorizationCredentials,
                              OAuth2PasswordBearer)
from app.db.models.models import UserModel, UserType
from app.db.session import get_db
from app.config import config
from sqlalchemy.orm import Session
from typing import List
from fastapi import HTTPException, status, Depends
from jose import JWTError, jwt
oauth2_scheme = APIKeyHeader(name="Authorization")

# async def get_current_user(token: str = Depends(oauth2_scheme)):
#     token = token.split(" ")[-1]
#     payload = verify_token(token)
#     if payload is None:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid token",
#         )
#     return payload

# async def get_current_user_id(token: str = Depends(oauth2_scheme)):
#     payload = await get_current_user(token)
#     user_id = payload.get("sub")
#     if user_id is None:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid token",
#         )
#     return user_id




# def verify_token(token: str):
#     try:
#         payload = jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])
#         return payload
#     except jwt.ExpiredSignatureError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Token has expired",
#         )
#     except jwt.InvalidTokenError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid token",
#         )
    

# async def get_current_user_role(token: str = Depends(oauth2_scheme)):
#     payload = await get_current_user(token)
#     user_type = payload.get("user_type")
#     if user_type is None:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid token",
#         )
#     return user_type

def verify_token(token: str):
    try:
        return jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> UserModel:
    if token.startswith("Bearer "):
        token = token.split(" ")[1]

    payload = verify_token(token)
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token: missing user ID")

    user = db.query(UserModel).filter(UserModel.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user

async def get_current_user_id(token: str = Depends(oauth2_scheme)):
    payload = await get_current_user(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    return int(user_id)

async def get_current_user_role(token: str = Depends(oauth2_scheme)):
    payload = await get_current_user(token)
    user_type = payload.get("user_type")
    if not user_type:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user_type

class RoleChecker:
    def __init__(self, allowed_roles: List[UserType]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: UserModel = Depends(get_current_user)):
        if user.user_type not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this resource"
            )
        return True

