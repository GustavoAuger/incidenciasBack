from app.repositories.incidencia_repository import IncidenciaRepository
from app.models import Incidencia
import jwt
import httpx

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

    def get_detalle_incidencias(self, body, db):
        return self.repository.get_detalle_incidencias(body, db)
        
    def actualizar_detalle(self, body, db):
        return self.repository.actualizar_detalle(body, db)

    def correo(self, body, db):
        incidencia = Incidencia(
            id=body.get("id"),  # <-- simulado para pruebas postman
            origen=body.get("origen"),
            destino=body.get("destino"),
            fecha_recepcion=body.get("fecha_recepcion"),
            observaciones=body.get("observaciones")
        )

        return self.repository.enviar_correo_bodega(incidencia, db)