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
        try:
            # Crear la incidencia principal
            nueva_incidencia = Incidencia(
                origen=body['incidencia'].get('id_bodega'),
                destino=body['incidencia'].get('destino_id_local'),
                ots=body['incidencia'].get('ots'),
                fecha_recepcion=body['incidencia'].get("fecha"),
                observaciones=body['incidencia'].get("observaciones"),
                id_estado=body['incidencia'].get("id_estado"),
                id_usuario=body['incidencia'].get("id_usuario"),
                id_transportista=body['incidencia'].get("id_transportista"),
                id_tipo_incidencia=body['incidencia'].get("id_tipo_incidencia")
            )

            # Agregar y obtener el ID de la incidencia
            db.add(nueva_incidencia)
            db.flush()  # Esto asigna el ID pero no hace commit aún
            id_incidencia = nueva_incidencia.id

            # Procesar cada detalle
            for detalle in body['detalles']:
                nuevo_detalle = Detalle(
                    id_incidencia=id_incidencia,
                    tipo_de_diferencia=detalle.get("tipoDiferencia"),
                    sku_producto=detalle.get("sku"),
                    nro_bulto=detalle.get("numBulto"),
                    peso_origen=detalle.get("pesoOrigen"),
                    peso_recepcion=detalle.get("pesoRecepcion"),
                    cantidad=detalle.get("cantidad"),
                    id_guia=detalle.get("numGuia")
                )
                db.add(nuevo_detalle)

            # Si todo salió bien, hacer commit de la transacción
            db.commit()
            return id_incidencia

        except Exception as e:
            # Si algo salió mal, hacer rollback
            db.rollback()
            print(f"Error creando incidencia y detalles: {e}")
            raise HTTPException(status_code=500, detail=str(e))
#no borrar esto pues es cuando cargaba imagen, se usara despues como referencia para la ruta
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

    def get_detalle_incidencias(self, body: dict, db: Session):
        id_incidencia = body.get('id_incidencia')
        if not id_incidencia:
            raise HTTPException(
                status_code=400,
                detail="Se requiere el parámetro 'id_incidencia'"
            )
            
        detalles = db.query(Detalle).filter(Detalle.id_incidencia == id_incidencia).all()
        if not detalles:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontraron detalles para la incidencia con ID {id_incidencia}"
            )
        
        # Transformar los datos al formato esperado por el frontend
        detalles_formateados = []
        for detalle in detalles:
            detalles_formateados.append({
                "id": detalle.id,
                "idIncidencia": detalle.id_incidencia,
                "sku": detalle.sku_producto,
                "numBulto": detalle.nro_bulto,
                "pesoOrigen": float(detalle.peso_origen),  # Convertir Decimal a float
                "pesoRecepcion": float(detalle.peso_recepcion),  # Convertir Decimal a float
                "cantidad": detalle.cantidad,
                "numGuia": detalle.id_guia,
                "tipoDiferencia": detalle.tipo_de_diferencia,
                "descripcion": ""  # Agregar este campo si lo necesitas
            })
        
        return detalles_formateados