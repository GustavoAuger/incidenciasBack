from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from db.session import get_db  
from app.models import Usuario
from app.auth import create_access_token  # Importa el create_access_token

from app.services.user_service import UserService
_userService = UserService()

router = APIRouter()


@router.post("/validateLogin")
async def validate_user_password(body: dict, db: Session = Depends(get_db)):
    return _userService.validate_user_password(body, db)


@router.get("/getUsers")
async def get_users(db: Session = Depends(get_db)):
    return _userService.get_users(db)
