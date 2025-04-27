from fastapi import FastAPI
from app.controllers.controller import router  # Importa tus routers desde app/controllers
from app.models import Usuario

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

app.include_router(router)
