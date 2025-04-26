from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config.settings import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
from sqlalchemy.orm import Session

# Cadena de conexión para PostgreSQL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency para FastAPI (abrir/cerrar sesión)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
