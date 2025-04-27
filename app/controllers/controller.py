from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from db.session import get_db  
from app.models import Usuario
from app.auth import create_access_token  # Importa el create_access_token
router = APIRouter()

from app.auth import create_access_token  # Importa el create_access_token

@router.post("/validateLogin")
async def validate_user_password(body: dict, db: Session = Depends(get_db)):
    username = body.get("username")
    password = body.get("password")

    user = db.query(Usuario).filter(Usuario.email == username).first()

    if not user:
        raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")

    # Comparación directa SIN encriptación
    if user.contrasena != password:
        raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")

    # Crear token con el id_usuario
    token_data = {"sub": str(user.id)}
    access_token = create_access_token(data=token_data)

    return {"access_token": access_token, "id_rol": user.id_rol}
