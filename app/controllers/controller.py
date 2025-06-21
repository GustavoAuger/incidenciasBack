from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from sqlalchemy.orm import Session
from db.session import get_db  
from app.models import Usuario
from app.models import Incidencia
from app.auth import create_access_token  # Importa el create_access_token
from app.services.user_service import UserService
from app.services.incidencia_service import IncidenciaService
from app.services.external_service import ExternalService
from app.services.transportista_service import TransportistaService
from app.models.models import GuiaRequest # Importa el nuevo modelo

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

@router.get("/getGuias")
async def get_bodegas(db: Session = Depends(get_db)):
    success = _externalService.get_guias(db)
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

@router.post("/getIncidencias")
async  def get_incidencias(body: dict, db: Session = Depends(get_db)):
    success = _incidenciaService.get_incidencias(body, db)
    return success

@router.post("/getDetallesIncidencia")
async  def get_incidencias(body: dict, db: Session = Depends(get_db)):
    success = _incidenciaService.get_detalle_incidencias(body, db)
    print(success)
    return success

@router.post("/getSkusByGuia") # Cambiamos a POST
def get_skus_by_guia_from_body(body: dict, db: Session = Depends(get_db)):
    skus = _externalService.get_skus_by_guia(body, db)
    if not skus:
        raise HTTPException(status_code=404, detail="SKUs not found for the given guide number")
    return skus

@router.get("/getMails")
async def get_emails(db: Session = Depends(get_db)):
    return _userService.get_emails(db)

@router.get("/getIdBodegaUser")
async def get_IdBodegaUser(db: Session = Depends(get_db)):
    return _userService.get_IdBodegaUser(db)


@router.post("/actualizarDetalle")
async def actualizar_detalle(body: dict, db: Session = Depends(get_db)):
    return _incidenciaService.actualizar_detalle(body, db)

@router.post("/correo")
async def enviar_correo(body: dict, db: Session = Depends(get_db)):
    return _incidenciaService.correo(body, db)

@router.post("/upload-image")
async def upload_image(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    return _incidenciaService.subir_imagen(file, db)