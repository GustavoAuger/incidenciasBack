from sqlalchemy.orm import Session
from fastapi import UploadFile
from sqlalchemy.orm import Session
from typing import Optional
from fastapi import HTTPException
from app.auth import create_access_token  
from passlib.context import CryptContext
from app.models import TipoIncidencia
from app.models import EstadoIncidencia
from app.models import Incidencia
from app.models import Detalle
import os
from supabase import create_client, Client
from datetime import datetime
from dotenv import load_dotenv
import bcrypt

# Cargar variables del archivo .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


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
            destino=body.get('id_bodega_destino'),
            ots=body.get('ots'),
            fecha_recepcion=body.get("fecha"),
            observaciones=body.get("observaciones"),
            id_estado=body.get("id_estado"),
            id_usuario=body.get("id_usuario"),
            id_transportista=body.get("id_transportista"),
            id_tipo_incidencia=body.get("id_tipo_incidencia")
        )

        try:
            db.add(nueva_incidencia)
            db.commit()
            db.refresh(nueva_incidencia)
            return nueva_incidencia.id
        except Exception as e:
            db.rollback()
            print(f"Error creando incidencia: {e}")
            return False

    def create_detalle(self, body: dict, db: Session, file: Optional[UploadFile] = None):
        ruta_storage = None

        # Si recibimos imagen, la subimos
        if file:
            ruta_storage = upload_image_to_supabase(file)

        nuevo_detalle = Detalle(
            id_incidencia=body.get("id_incidencia"),
            tipo_de_diferencia=body.get("tipo_de_diferencia"),
            sku_producto=body.get("sku_producto"),
            nro_bulto=body.get("nro_bulto"),
            peso_origen=body.get("peso_origen"),
            peso_recepcion=body.get("peso_recepcion"),
            cantidad=body.get("cantidad"),
            id_guia=body.get("id_guia"),
            ruta_storage=ruta_storage  # Se asigna si hubo imagen
        )

        try:
            db.add(nuevo_detalle)
            db.commit()
            db.refresh(nuevo_detalle)
            return True
        except Exception as e:
            db.rollback()
            print(f"Error creando detalle: {e}")
            return False


    def upload_image_to_supabase(file, filename_prefix="detalle"): #se consume en la función de arriba si es que se carga imagen

        try:
            now = datetime.utcnow().strftime("%Y%m%d%H%M%S")
            filename = f"{filename_prefix}_{now}_{file.filename}"
            path_in_bucket = f"{filename}"

            file_bytes = file.file.read()  # Leer contenido binario
            res = supabase.storage.from_(SUPABASE_BUCKET).upload(path_in_bucket, file_bytes)

            public_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{path_in_bucket}"
            return public_url
        except Exception as e:
            print(f"Error al subir imagen a Supabase: {e}")
            return None

    def get_incidencias(self, db):
        incidencaias = db.query(Incidencia).all()
        return incidencaias