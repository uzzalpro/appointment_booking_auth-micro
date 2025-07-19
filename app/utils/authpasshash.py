from passlib.context import CryptContext
import bcrypt
from jose import jwt
from app.config import config
# # Password hashing
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# def hash_password(password: str) -> str:
#     """Hash a password using bcrypt."""
#     return pwd_context.hash(password)

# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     """Verify a password against its hashed version."""
#     return pwd_context.verify(plain_password, hashed_password)

from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.config import config
# SECRET_KEY = "KJOIDjjjdkap*&^*"  # Load from env in production
# ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
# token_blacklist = set()

# class TokenBlacklist(BaseModel):
#     token: str

def create_jwt_token(data: dict):
    """
    Create a JWT token using the provided data.
    """
    return jwt.encode(data, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    # Using bcrypt directly to avoid passlib warning
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


# @router.post("/logout")
# def logout(token: str = Depends(OAuth2PasswordBearer(tokenUrl="login"))):
#     token_blacklist.add(token)
#     return {"message": "Successfully logged out"}