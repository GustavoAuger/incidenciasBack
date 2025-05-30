from app.repositories.external_repository import ExternalRepository
import jwt


class ExternalService:
    def __init__(self):
        self.repository = ExternalRepository()
        self.bodegas_url = "https://680fe31d27f2fdac240fb759.mockapi.io/ged_id_bodega/bodega"

    def get_bodegas(self, db):
        return self.repository.get_bodegas(db)
    
    def get_productos(self, db):
        return self.repository.get_productos(db)

    def get_guias(self, db):
        return self.repository.get_guias(db)

    def get_skus_by_guia(self, body, db):
        return self.repository.get_producto_guia(body, db)