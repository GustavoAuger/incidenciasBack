from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from db.session import get_db  
from app.models import Usuario
from app.models import Incidencia
from app.auth import create_access_token  # Importa el create_access_token
from app.services.user_service import UserService
from app.services.incidencia_service import IncidenciaService
from app.services.external_service import ExternalService
from app.services.transportista_service import TransportistaService

router = APIRouter()
_userService = UserService()
_externalService = ExternalService()
_incidenciaService = IncidenciaService()
_trasportistaService = TransportistaService()


@router.post("/validateLogin")
async def validate_user_password(body: dict, db: Session = Depends(get_db)):
    return _userService.validate_user_password(body, db)


@router.get("/getUsers")
async def get_users(db: Session = Depends(get_db)):
    return _userService.get_users(db)

@router.post("/createUser")
async  def create_user(body: dict, db: Session = Depends(get_db)):
    success = _userService.create_user(body, db)
    return success

@router.post("/modifyUser")
async def create_user(body: dict, db: Session = Depends(get_db)):
    success = _userService.modify_user(body, db)
    return success

@router.get("/getRol")
async def create_user(db: Session = Depends(get_db)):
    success = _userService.get_rol(db)
    return success

@router.get("/getBodegas")
async def get_bodegas(db: Session = Depends(get_db)):
    success = _externalService.get_bodegas(db)
    return success

@router.get("/getProductos")
async def get_bodegas(db: Session = Depends(get_db)):
    success = _externalService.get_productos(db)
    return success

@router.get("/getTipoincidencias")
async def get_tipo_incidencia(db: Session = Depends(get_db)):
    success = _incidenciaService.get_tipo_incidencia(db)
    return success

@router.get("/getEstadoincidencias")
async def get_tipo_incidencia(db: Session = Depends(get_db)):
    success = _incidenciaService.get_estado_incidencia(db)
    return success

@router.post("/createIncidencia")
async  def create_user(body: dict, db: Session = Depends(get_db)):
    success = _incidenciaService.create_incidencia(body, db)
    return success

@router.get("/getTransportistas")
async def get_transportistas(db: Session = Depends(get_db)):
    success = _trasportistaService.get_transportistas(db)
    return success

@router.get("/getEstadosTransportista")
async def get_e_ransportistas(db: Session = Depends(get_db)):
    success = _trasportistaService.get_e_transportistas(db)
    return success

@router.post("/createDetalle")
async  def create_user(body: dict, db: Session = Depends(get_db)):
    success = _incidenciaService.create_detalle(body, db)
    return success

@router.get("/getIncidencias")
async  def create_user(db: Session = Depends(get_db)):
    success = _incidenciaService.get_incidencias(db)
    return success

