from app.repositories.transportista_repository import TransportistaRepository
from app.models import Transportista

import jwt
import datetime


class TransportistaService:
    def __init__(self):
        self.repository = TransportistaRepository()

    def get_transportistas(self, db):
        return self.repository.get_transportistas(db)
    
    def get_e_transportistas(self, db):
        return self.repository.get_e_transportistas(db)
