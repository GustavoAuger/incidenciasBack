from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.auth import create_access_token  
from passlib.context import CryptContext
from app.models import Transportista
from app.models import EstadoTransportista
import requests
import bcrypt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class TransportistaRepository:
    
    def get_transportistas(self, db):
        transportista = db.query(Transportista).all()
        return transportista
    
    def get_e_transportistas(self, db):
        estado = db.query(EstadoTransportista).all()
        return estado