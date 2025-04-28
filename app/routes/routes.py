from fastapi import APIRouter
from app.controllers.controller import router as controller_router 

api_router = APIRouter()

# Incluye las rutas del controlador
api_router.include_router(controller_router)