from app.repositories.reclamo_repository import ReclamoRepository
from app.models.models import ReclamoTransportista as ReclamoTransportistaModel
from app.models.models import ReclamoTransportistaCreate, ReclamoTransportistaResponse

class ReclamoService:
    def __init__(self):
        self.reclamo_repository = ReclamoRepository()

    def get_estados_reclamo(self, db):
        return self.reclamo_repository.get_estados_reclamo(db)
    
    def get_reclamos(self, db):
        return self.reclamo_repository.get_reclamos(db)
    
    def create_reclamo_transportista(self, reclamo: ReclamoTransportistaCreate, db):
        try:
            
            # Crear una instancia del modelo de SQLAlchemy
            db_reclamo = ReclamoTransportistaModel(
                id_incidencia=reclamo.id_incidencia,
                monto_pagado=reclamo.monto_pagado or 0,
                fdr=reclamo.fdr,
                fecha_reclamo=reclamo.fecha_reclamo,
                observacion=reclamo.observacion,
                id_estado=reclamo.id_estado
            )
            
            # Guardar en la base de datos
            result = self.reclamo_repository.create_reclamo_transportista(db_reclamo, db)
            
            # Convertir el resultado a un diccionario para la respuesta
            response_dict = {
                'id': result.id,
                'id_incidencia': result.id_incidencia,
                'monto_pagado': float(result.monto_pagado) if result.monto_pagado is not None else 0,
                'fdr': result.fdr,
                'fecha_reclamo': result.fecha_reclamo.isoformat() if result.fecha_reclamo else None,
                'observacion': result.observacion,
                'id_estado': result.id_estado
            }
            
            return response_dict
            
        except Exception as e:
            print(f"Error en el servicio al crear reclamo: {str(e)}")
            raise e
    
    def update_reclamo_transportista(self, reclamo: ReclamoTransportistaResponse, db):
        # Convertir el modelo Pydantic a un diccionario
        reclamo_dict = reclamo.dict()
        # Crear una instancia del modelo de SQLAlchemy
        db_reclamo = ReclamoTransportistaModel(**reclamo_dict)
        # Actualizar en la base de datos
        return self.reclamo_repository.update_reclamo_transportista(db_reclamo, db)