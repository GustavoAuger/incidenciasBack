from app.repositories.user_repository import UserRepository
from app.models import Usuario

import jwt
import datetime


class UserService:
    def __init__(self):
        self.repository = UserRepository()
        self.bodegas_url = "https://680fe31d27f2fdac240fb759.mockapi.io/ged_id_bodega/bodega"

    def validate_user_password(self, body, db):
        return self.repository.validate_user_password(body, db)

    def get_users(self, db):
        return self.repository.get_users(db)
  
    def create_user(self, body, db):
        return self.repository.create_user(body, db)

    def modify_user(self, body, db):
        return self.repository.modify_user(body, db)