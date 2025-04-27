from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from db.session import get_db  
from app.models import Usuario 
from passlib.context import CryptContext


router = APIRouter()
# Configuración de encriptación de contraseñas
#pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Función para verificar la contraseña
#def verify_password(plain_password, hashed_password):
  #  return pwd_context.verify(plain_password, hashed_password)

@router.post("/validateLogin")
async def validate_user_password(body: dict, db: Session = Depends(get_db)):
    username = body.get("username")  # El 'username' es el 'email' del usuario
    password = body.get("password")

    # Buscar al usuario por email (username)
    user = db.query(Usuario).filter(Usuario.email == username).first()

    if not user:
        raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")

    # Comparar la contraseña en texto plano
    if user.contrasena != password:
        raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")

    
    return {"message": "Login exitoso"}