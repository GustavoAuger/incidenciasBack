from passlib.context import CryptContext
from app.models import EstadoTransportista, ReclamoTransportista as ReclamoTransportistaModel
from sqlalchemy.exc import SQLAlchemyError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class ReclamoRepository:
    def get_estados_reclamo(self, db):
        return db.query(EstadoTransportista).all()
    
    def get_reclamos(self, db):
        return db.query(ReclamoTransportistaModel).all()
    
    def create_reclamo_transportista(self, reclamo_data, db):
        try:
            # Crear una nueva instancia del modelo con los datos proporcionados
            nuevo_reclamo = ReclamoTransportistaModel(
                id_incidencia=reclamo_data.id_incidencia,
                monto_pagado=reclamo_data.monto_pagado,
                fdr=reclamo_data.fdr,
                fecha_reclamo=reclamo_data.fecha_reclamo,
                observacion=reclamo_data.observacion or None,
                id_estado=reclamo_data.id_estado
            )
            
            db.add(nuevo_reclamo)
            db.commit()
            db.refresh(nuevo_reclamo)
            return nuevo_reclamo
            
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error en la base de datos al crear reclamo: {str(e)}")
            raise e
        except Exception as e:
            db.rollback()
            print(f"Error inesperado al crear reclamo: {str(e)}")
            raise e
    
    def update_reclamo_transportista(self, reclamo_data, db):
        try:
            # Obtener el reclamo existente
            reclamo = db.query(ReclamoTransportistaModel).filter(
                ReclamoTransportistaModel.id == reclamo_data.id
            ).first()
            
            if not reclamo:
                raise ValueError("Reclamo no encontrado")
                
            # Actualizar campos
            for key, value in reclamo_data.dict().items():
                if hasattr(reclamo, key) and key != 'id':
                    setattr(reclamo, key, value)
            
            db.commit()
            db.refresh(reclamo)
            return reclamo
            
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error en la base de datos al actualizar reclamo: {str(e)}")
            raise e
        except Exception as e:
            db.rollback()
            print(f"Error inesperado al actualizar reclamo: {str(e)}")
            raise e