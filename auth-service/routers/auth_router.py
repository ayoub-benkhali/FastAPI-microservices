from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import UserCreate
from auth import hash_password

from schemas import UserLogin

from auth import ( verify_password , create_access_token )

router = APIRouter()

# routes pour registration
@router.post("/register")
def register( user: UserCreate , db: Session = Depends(get_db) ):
    
    new_user = User (
        username=user.username,
        email=user.email,
        hashed_password=hash_password( user.password )
    )

    db.add(new_user)
    db.commit()

    return { "message": "Utilisateur créé" }

# route pour le login
@router.post("/login")
def login( user: UserLogin, db: Session = Depends(get_db)):

    db_user = db.query(User).filter(
        User.email == user.email ).first()

    if not db_user:

        return { "message": "Email incorrect"  }

    if not verify_password( user.password , db_user.hashed_password ):

        return { "message": "Mot de passe incorrect" }

    token = create_access_token (
        {"sub": db_user.email}
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }