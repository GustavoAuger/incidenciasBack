from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.auth import create_access_token  
from passlib.context import CryptContext
from sqlalchemy.orm import joinedload
import requests
import bcrypt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class ExternalRepository:
    def __init__(self):
        self.bodegas_url = "https://680fe31d27f2fdac240fb759.mockapi.io/ged_id_bodega/bodega"
        self.producto_url = "https://680fe31d27f2fdac240fb759.mockapi.io/ged_id_bodega/productos"
        self.guia_url = "https://672258a92108960b9cc41077.mockapi.io/api/guias/guia" 
        self.movimientos_url = "https://672258a92108960b9cc41077.mockapi.io/api/guias/movimientos"  
    
    def get_bodegas(self, db: Session):
        response = requests.get(self.bodegas_url)
        bodegas = response.json()
        result = []
        for bodega in bodegas:
            result.append({
                "id_bodega": bodega["id_bodega"],
                "id": bodega["id"],
                "nombre": bodega["nombre_bodega"],
            })

        return result #retornamos la lista ! :D
    
    def get_productos(self, db: Session):
        response = requests.get(self.producto_url)
        productos = response.json()
        return productos
    
    def get_guias(self, db: Session):
        response = requests.get(self.guia_url)
        guias = response.json()
        return guias

    def get_producto_guia(self, body: dict, db: Session):
    #Obtiene los SKUs para un número de guía específico desde la mock API
        guia_numero = body.get('guia_numero')
        if not guia_numero:
            return []

        try:
            response = requests.get(self.guia_url)
            response.raise_for_status()
            guias = response.json()

            guia = next((g for g in guias if str(g.get('numguia')) == str(guia_numero)), None)

            if guia and 'sku_total' in guia:
                return guia['sku_total'] if isinstance(guia['sku_total'], list) else []
            return []

        except requests.exceptions.RequestException as e:
            print(f"Error al obtener guía {guia_numero} desde la mock API: {e}")
            return []

    def post_movimientos(self, body: dict, db: Session):
        try:
            response = requests.post(self.movimientos_url, json=body)
            print(f"Respuesta del servidor: {response.status_code}")
            # si recive un 200 o 201 es exitoso retorna true    
            return response.status_code in [200, 201]
        except requests.exceptions.RequestException as e:
            print(f"Error en la petición: {str(e)}")
            return False