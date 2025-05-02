from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import Usuario
from app.models import Rol
from app.auth import create_access_token  
from passlib.context import CryptContext
from sqlalchemy.orm import joinedload
import requests
import bcrypt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRepository:
    def __init__(self):
        self.bodegas_url = "https://680fe31d27f2fdac240fb759.mockapi.io/ged_id_bodega/bodega"
    
    def validate_user_password(self, body: dict, db: Session):
        username = body.get("username")
        password = body.get("password")

        user = db.query(Usuario).filter(Usuario.email == username).first()

        if not user:
            raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")

        # Compara la contraseña hasheada usando bcrypt
        if not pwd_context.verify(password, user.contrasena):
            raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")

        token_data = {"sub": str(user.id)}
        access_token = create_access_token(data=token_data)

        return {"access_token": access_token, "id_rol": user.id_rol}
    
    def get_users(self, db: Session):
        # 1. Traemos los usuarios con su rol (/join con la tabla de rol) / se agrega fultro estado = true
        users = db.query(Usuario).options(joinedload(Usuario.rol)).filter(Usuario.estado == True).all()
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
                "rol": user.rol.nombre,  
                "id_rol": user.id_rol
            })

        return result # 5. retornamos la lista ! :D


    def create_user(self, body: dict, db: Session):
        # Hashear la contraseña
        plain_password = body.get('contrasena')
        hashed_password = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        # Crear usuario
        nuevo_usuario = Usuario(
            nombre=body.get('nombre'),
            email=body.get('email'),
            id_bodega=body.get('id_bodega'),
            id_rol=body.get('id_rol'),
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

    def modify_user(self, body: dict, db: Session):
        # Buscar usuario por ID
        user_id = body.get('id')
        usuario = db.query(Usuario).filter(Usuario.id == user_id).first()

        if not usuario:
            print("Usuario no encontrado")
            return False

        # Actualizar campos
        usuario.nombre = body.get('nombre')
        usuario.email = body.get('email')
        usuario.id_bodega = body.get('id_bodega')
        usuario.estado = body.get('estado')
        usuario.id_rol = body.get("id_rol")

        # Si se pasó una nueva contraseña, la actualizamos hasheada
        nueva_contra = body.get('contrasena')
        if nueva_contra:
            hashed_password = bcrypt.hashpw(nueva_contra.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            usuario.contrasena = hashed_password

        try:
            db.commit()
            db.refresh(usuario)
            return True
        except Exception as e:
            db.rollback()
            print(f"Error actualizando usuario: {e}")
            return False


    def get_rol(self, db: Session):
        rol = db.query(Rol).all()
        return rol
        
    def close_connection(self):
        self.db.close()