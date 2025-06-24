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
        try:
            # Convertir el modelo Pydantic a diccionario, excluyendo campos no establecidos
            update_data = reclamo.dict(exclude_unset=True)
            
            # Llamar al repositorio para realizar la actualización
            updated_reclamo = self.reclamo_repository.update_reclamo(
                id=reclamo.id,
                reclamo_data=update_data,
                db=db
            )
            
            if not updated_reclamo:
                raise HTTPException(status_code=404, detail="Reclamo no encontrado")
            
            # Retornar el reclamo actualizado
            return {
                'id': updated_reclamo.id,
                'id_incidencia': updated_reclamo.id_incidencia,
                'monto_pagado': float(updated_reclamo.monto_pagado) if updated_reclamo.monto_pagado is not None else 0,
                'fdr': updated_reclamo.fdr,
                'fecha_reclamo': updated_reclamo.fecha_reclamo.isoformat() if updated_reclamo.fecha_reclamo else None,
                'observacion': updated_reclamo.observacion,
                'id_estado': updated_reclamo.id_estado
            }
                
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error al actualizar el reclamo: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error al actualizar el reclamo: {str(e)}")