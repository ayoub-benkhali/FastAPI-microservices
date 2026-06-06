# Hachage et vérification des mots de passe
from passlib.context import CryptContext
# Création et décodage des JWT tokens
from jose import jwt
# Gestion des dates, heures et expiration des tokens
from datetime import datetime, timedelta, timezone
# Accès aux variables d'environnement du système
import os

# SECRET_KEY depuis variable d'environnement
# can BE anything, but should be kept secret in production
SECRET_KEY = os.environ.get("3d8f5c1a9e7b2f4d6a8c0e1f3b5d7a9c2e4f6b8d0a1c3e5f7b9d1a3c5e7f9b")
# the standard algorithm for JWTs is HS256
ALGORITHM = "HS256"

# Do password hashing , unhashing and verification with passlib
# it's an dependency injection for PWD hashing and verification
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# type dict (dictionary) IS like RECORD in PL/SQL, it's a key-value pair structure
def create_access_token(data: dict):
    # copy the data to avoid mutation of the original dict
    to_encode = data.copy()
    # datetime.now(timezone.utc) au lieu de utcnow()
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode, SECRET_KEY, algorithm=ALGORITHM
                      )