from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.auth import create_access_token  
from passlib.context import CryptContext
from app.models import TipoIncidencia
from app.models import EstadoIncidencia
from app.models import Incidencia
import bcrypt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class IncidenciaRepository:
    
    
    def get_tipo_incidencia(self, db: Session):
        incidencias = db.query(TipoIncidencia).all()
        return incidencias

    def get_estado_incidencia(self, db: Session):
        estado = db.query(EstadoIncidencia).all()
        return estado
    
    def create_incidencia(self, body: dict, db: Session):

        nueva_incidencia = Incidencia(
            origen=body.get('id_bodega'),
            ots=body.get('ots'),
            fecha_recepcion=body.get("fecha"),
            observaciones=body.get("observaciones"),
            id_estado=body.get("id_estado"),
            id_usuario=body.get("id_usuario"),
            id_transportista=body.get("id_transportista")
        )

        try:
            db.add(nueva_incidencia)
            db.commit()
            db.refresh(nueva_incidencia)
            return True
        except Exception as e:
            db.rollback()
            print(f"Error creando incidencia: {e}")
            return False
