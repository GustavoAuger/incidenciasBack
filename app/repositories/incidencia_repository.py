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
#importanciones para correo
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders



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
    
    def enviar_correo_bodega(self, id_bodega: str) -> dict:
        try:
            # Obtener información de la bodega
            response = requests.get(f"{self.bodegas_url}/{id_bodega}")
            if response.status_code != 200:
                raise HTTPException(status_code=404, detail="Bodega no encontrada")
                
            bodega = response.json()
            correo_destino = bodega.get('correo')
            nombre_bodega = bodega.get('nombre_bodega')
            
            if not correo_destino:
                raise HTTPException(status_code=400, detail="La bodega no tiene correo registrado")
            
            # Configuración del servidor SMTP
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            sender_email = os.getenv("EMAIL_USER")
            sender_password = os.getenv("EMAIL_PASSWORD")
            
            if not sender_email or not sender_password:
                raise HTTPException(status_code=500, detail="Configuración de correo no disponible")
            
            # Crear mensaje
            message = MIMEMultipart()
            message["From"] = sender_email
            message["To"] = correo_destino
            message["Subject"] = f"Nueva Incidencia Registrada - {nombre_bodega}"
            
            body = f"Se ha registrado una nueva incidencia para la bodega {nombre_bodega}."
            message.attach(MIMEText(body, "plain"))
            
            # Enviar correo
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(message)
            
            return {"message": "Correo enviado exitosamente"}
            
        except HTTPException as he:
            raise he
        except Exception as e:
            print(f"Error enviando correo: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    def create_incidencia(self, body: dict, db: Session):
        try:
            # Crear la incidencia principal
            nueva_incidencia = Incidencia(
                origen=body['incidencia'].get('id_bodega'),
                destino=body['incidencia'].get('destino_id_bodega'),
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
            # Enviar correo a la bodega de origen
            try:
                # llamamos directamente a la funcion
                resultado = self.enviar_correo_bodega(body['incidencia'].get('id_bodega'))

                # para ver si lo hizo
                if resultado.get('message') == "Correo enviado exitosamente":
                    print("Correo enviado exitosamente.")
                else:
                    print(f"Error al enviar correo: {resultado.get('message')}")

            except Exception as e:
                print(f"Error enviando correo: {e}")

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
                "id_bodega": bodega["id_bodega"]
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
                {"nombre_bodega": f"ID {origen_id}", "id_bodega": "N/A"}
            )
            destino_data = bodegas_map.get(
                destino_id, 
                {"nombre_bodega": f"ID {destino_id}", "id_bodega": "N/A"}
            )
       
            result.append({
                "id": incidencia.id,
                "fecha_recepcion": incidencia.fecha_recepcion,
                "id_estado": incidencia.id_estado,
                "tipo_estado": incidencia.estado.tipo_estado,
                "transportista": incidencia.transportista.nombre,
                "origen_id_local": origen_data["id_bodega"],
                "destino": destino_data["nombre_bodega"],
                "destino_id_bodega": destino_data["id_bodega"],
                "ots": incidencia.ots,
                "fecha_emision": incidencia.fecha_emision,
                "observaciones": incidencia.observaciones,
                "id_usuario": incidencia.id_usuario,
                "id_tipo_incidencia": incidencia.id_tipo_incidencia,
                "valorizado": incidencia.valorizado,
                "total_item": incidencia.total_item
            })

        return result

    def get_detalle_incidencias(self, body: dict, db: Session):
        id_incidencia = body.get('id_incidencia')
        if not id_incidencia:
            raise HTTPException(
                status_code=400,
                detail="Se requiere el parámetro 'id_incidencia'"
            )
            
        detalles = db.query(Detalle).filter(Detalle.id_incidencia == id_incidencia, Detalle.estado == True).all()
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

    
    def actualizar_detalle(self, body: dict, db: Session):
        id_incidencia = body.get('incidencia')
        detallex = body.get('detalles')
        try:
            # Obtener todos los detalles actuales de la incidencia
            detalles_actuales = db.query(Detalle).filter(Detalle.id_incidencia == id_incidencia, Detalle.estado == True).all()
             # Crear un set de IDs actuales en la base de datos
            ids_actuales = {detalle.id for detalle in detalles_actuales}
            # Crear un set de IDs que vienen en el body
            ids_nuevos = {detalle.get("id") for detalle in body['detalles'] if detalle.get("id")}
            # Encontrar los IDs que deben ser eliminados (soft delete)
            ids_a_eliminar = ids_actuales - ids_nuevos
            # Eliminar los detalles marcados como eliminados (si los hay)
            if ids_a_eliminar: # aplicamos soft delete
                db.query(Detalle).filter(Detalle.id.in_(ids_a_eliminar)).update({Detalle.estado: False}, synchronize_session=False)
            for detalle in body['detalles']:
                # signfica que es nuevo
                if not detalle.get("id"):

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
                    print(nuevo_detalle)
                    db.add(nuevo_detalle)
                else:
                    print(detalle)
            #si todo salió bien, hacer commit a la bd
            db.commit()
            print(id_incidencia)
            print(detallex)
        except Exception as e:
            # Si algo salió mal, hacer rollback
            db.rollback()
            print(f"Error creando detalle: {e}")
            return False

        return id_incidencia