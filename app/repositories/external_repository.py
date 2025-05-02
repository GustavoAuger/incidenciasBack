from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.auth import create_access_token  
from passlib.context import CryptContext
from sqlalchemy.orm import joinedload
import requests
import bcrypt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class ExternalRepository:
    def __init__(self):
        self.bodegas_url = "https://680fe31d27f2fdac240fb759.mockapi.io/ged_id_bodega/bodega"
    
    def get_bodegas(self, db: Session):
        response = requests.get(self.bodegas_url)
        bodegas = response.json()
        result = []
        for bodega in bodegas:
            result.append({
                "id": bodega["id"],
                "nombre": bodega["nombre_bodega"],
            })

        return result #retornamos la lista ! :D