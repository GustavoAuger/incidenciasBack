from app.repositories.incidencia_repository import IncidenciaRepository
import jwt


class IncidenciaService:
    def __init__(self):
        self.repository = IncidenciaRepository()

    def get_tipo_incidencia(self, db):
        return self.repository.get_tipo_incidencia(db)
    
    def get_estado_incidencia(self, db):
        return self.repository.get_estado_incidencia(db)

    def create_incidencia(self, body, db):
        return self.repository.create_incidencia(body, db)
    
    def create_detalle(self, body, db):
        return self.repository.create_detalle(body, db)

    def get_incidencias(self, body, db):
        return self.repository.get_incidencias(body, db)
