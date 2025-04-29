from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import Usuario
from app.models import Rol
from app.auth import create_access_token  
from sqlalchemy.orm import joinedload
import requests
import bcrypt

class UserRepository:
    def __init__(self):
        self.bodegas_url = "https://680fe31d27f2fdac240fb759.mockapi.io/ged_id_bodega/bodega"

    def validate_user_password(self, body: dict, db: Session):
        username = body.get("username")
        password = body.get("password")

        user = db.query(Usuario).filter(Usuario.email == username).first()

        if not user:
            raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")

        if user.contrasena != password:
            raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")

        token_data = {"sub": str(user.id)}
        access_token = create_access_token(data=token_data)

        return {"access_token": access_token, "id_rol": user.id_rol}
    
    def get_users(self, db: Session):
        # 1. Traemos los usuarios con su rol (/join con la tabla de rol)
        users = db.query(Usuario).options(joinedload(Usuario.rol)).all()

        # 2. Traemos las bodegas desde la MockAPI (Simulación datos de HEAD)
        response = requests.get(self.bodegas_url)
        bodegas_data = response.json()

        # 3. Creamos un lookup {id_numero: nombre_bodega}
        bodegas_lookup = {}
        for bodega in bodegas_data:
            id_local = bodega.get("id_local")
            nombre_bodega = bodega.get("nombre_bodega")
            if id_local and id_local.startswith("LO-"):
                try:
                    id_num = int(id_local.split("-")[1])  
                    bodegas_lookup[id_num] = nombre_bodega
                except ValueError:
                    pass

        # 4. Armamos el resultado
        result = []
        for user in users:
            result.append({
                "id": user.id,
                "nombre": user.nombre,
                "email": user.email,
                "id_bodega": user.id_bodega,
                "bodega": bodegas_lookup.get(user.id_bodega, "Bodega no encontrada"), # aqui se consume el lookup de acuerdo al id bodega
                "estado": user.estado,
                "rol": user.rol.nombre  
            })

        return result # 5. etornamos la lista ! :D


    def create_user(self, body: dict, db: Session):
        # Buscar el rol por nombre
        rol_nombre=body.get('rol')
        rol = db.query(Rol).filter(Rol.nombre == rol_nombre).first()
        print(rol)
        if not rol:
            return False  # No se encontró el rol


        # Hashear la contraseña
        plain_password = body.get('contrasena')
        hashed_password = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        # Crear usuario
        nuevo_usuario = Usuario(
            nombre=body.get('nombre'),
            email=body.get('email'),
            id_bodega=body.get('id_bodega'),
            id_rol=rol.id,
            contrasena=hashed_password,
        )

        try:
            db.add(nuevo_usuario)
            db.commit()
            db.refresh(nuevo_usuario)
            return True
        except Exception as e:
            db.rollback()
            print(f"Error creando usuario: {e}")
            return False

    def close_connection(self):
        self.db.close()