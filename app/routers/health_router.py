from fastapi import APIRouter, Depends, HTTPException, status

from app.config import config
from app.dependencies.auth import get_current_user_id

health_router = APIRouter(
    prefix=f'{config.API_PREFIX}/health',
    tags=['Health Check']
)


@health_router.get('', status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "ok", "message": f"Auth Service {config.PROJECT_VERSION} is running"}

@health_router.get('/auth', status_code=status.HTTP_200_OK)
async def health_check_auth(user_id: int = Depends(get_current_user_id)):
    return{"message": "You are authenticated", "user": user_id}