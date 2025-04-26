import datetime
from sqlalchemy.orm import Session
from app.models.models import User
from db.session import SessionLocal
import bcrypt

class UserRepository:

    def __init__(self):
        self.db = SessionLocal()

    def get_all_users(self):        
        return self.db.query(User).all()
    
    
    def validate_user_password(self, user):
        if user != None:
            input_password: str = user['password']
            user_bd = self.db.query(User).filter(User.deleted_at == None).filter_by(username=user['username']).first()
            
            if user_bd:
                input_password_bytes = input_password.encode('utf-8')
                user_bd_password_bytes = user_bd.password.encode('utf-8') 
                # Compara las contraseñas
                is_match = bcrypt.checkpw(input_password_bytes, user_bd_password_bytes)
                if is_match:
                    print("Acceso autorizado")
                    return True, user_bd.is_admin
            return False
        return False
    
    def create_user(self, user):
        user_bd = self.db.query(User).filter_by(username=user.username).first()
        if user_bd is None:            
            user.password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return True
        else:
            print("El usuario ya existe")
            return False    
    
    def update_user(self, user):
        user_bd = self.db.query(User).filter_by(username=user.username).first()
        if user_bd:
            user_bd.username = user.username
            user_bd.password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            user_bd.is_admin = user.is_admin
            user_bd.deleted_at = user.deleted_at
            self.db.commit()
            return True
        else:
            print("El usuario no existe")
            return False
        
    def delete_user(self, user):
        user_bd = self.db.query(User).filter_by(username=user.username).first()
        if user_bd:
            user_bd.deleted_at = datetime.datetime.strptime(user.deleted_at, '%Y-%m-%dT%H:%M:%S.%fZ')
            self.db.commit()
            return True
        else:
            print("El usuario no existe")
            return False

    def close_connection(self):
        self.db.close()