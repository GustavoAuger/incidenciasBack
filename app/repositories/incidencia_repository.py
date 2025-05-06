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
from app.models import Usuario
import os
from supabase import create_client, Client
from datetime import datetime
from dotenv import load_dotenv
import requests
import bcrypt
from sqlalchemy.orm import joinedload

# Cargar variables del archivo .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class IncidenciaRepository:
    def __init__(self):
        self.bodegas_url = "https://680fe31d27f2fdac240fb759.mockapi.io/ged_id_bodega/bodega"
    
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

    def get_incidencias(self, body, db):
        # Traer todas las bodegas, sus datos
        response = requests.get(self.bodegas_url)
        bodegas = response.json()  # Esto es una lista de dicts

        # Creamos de la siguiente manera: {id: {"nombre_bodega": ..., "id_local": ...}}
        bodegas_map = {
            int(bodega["id"]): {
                "nombre_bodega": bodega["nombre_bodega"],
                "id_local": bodega["id_local"]
                }
                for bodega in bodegas if str(bodega["id"]).isdigit()
        }


        user_id = body.get('id_usuario')
        usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
        id_rol=usuario.id_rol
        if(id_rol==4): #tienda
            id_bodega=usuario.id_bodega
            print(id_bodega)
        if(id_rol==2): #gestor
            incidencias = db.query(Incidencia).filter(Incidencia.id_usuario == user_id).all()
        else:
            incidencias = db.query(Incidencia).options(
                joinedload(Incidencia.transportista),
                joinedload(Incidencia.estado)
            ).all()
        print("bodegas_map keys:", bodegas_map.keys())
        
        result=[]

        for incidencia in incidencias:
            origen_id = int(incidencia.origen)
            destino_id = int(incidencia.destino)

            origen_data = bodegas_map.get(
                origen_id, 
                {"nombre_bodega": f"ID {origen_id}", "id_local": "N/A"}
            )
            destino_data = bodegas_map.get(
                destino_id, 
                {"nombre_bodega": f"ID {destino_id}", "id_local": "N/A"}
            )
       
            result.append({
                "id": incidencia.id,
                "fecha_recepcion": incidencia.fecha_recepcion,
                "id_estado": incidencia.id_estado,
                "tipo_estado": incidencia.estado.tipo_estado,
                "transportista": incidencia.transportista.nombre,
                "origen_id_local": origen_data["id_local"],
                "destino": destino_data["nombre_bodega"],
                "destino_id_local": destino_data["id_local"],
                "ots": incidencia.ots,
                "fecha_emision": incidencia.fecha_emision,
                "observaciones": incidencia.observaciones,
                "id_usuario": incidencia.id_usuario,
                "id_tipo_incidencia": incidencia.id_tipo_incidencia
            })

        return result