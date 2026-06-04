from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# SECRET_KEY depuis variable d'environnement
SECRET_KEY = os.environ.get("SECRET_KEY", "change_this_in_production")
ALGORITHM = "HS256"

def create_access_token(data: dict):
    to_encode = data.copy()
    # datetime.now(timezone.utc) au lieu de utcnow()
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)