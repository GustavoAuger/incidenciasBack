from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, Date, Numeric, TIMESTAMP, JSON
from sqlalchemy.orm import relationship
from db.session import Base

# Tabla ROL
class Rol(Base):
    __tablename__ = "rol"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)

    usuarios = relationship("Usuario", back_populates="rol") # Relación inversa

# Tabla USUARIO
class Usuario(Base):
    __tablename__ = "usuario"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, nullable=False)  # Agregamos el campo email
    nombre = Column(String(100), nullable=False)
    id_rol = Column(Integer, ForeignKey("rol.id", ondelete="RESTRICT"), nullable=False)
    contrasena = Column(Text, nullable=False)
    id_bodega = Column(Integer, nullable=True)
    estado = Column(Boolean, default=True)

    rol = relationship("Rol", back_populates="usuarios") # Relación hacia Rol
    
# Tabla TRANSPORTISTA
class Transportista(Base):
    __tablename__ = "transportista"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    contacto = Column(String(100))

# Tabla TIPO_INCIDENCIA
class TipoIncidencia(Base):
    __tablename__ = "tipo_incidencia"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)

# Tabla ESTADO_INCIDENCIA
class EstadoIncidencia(Base):
    __tablename__ = "estado_incidencia"

    id = Column(Integer, primary_key=True, index=True)
    tipo_estado = Column(String(20), nullable=False)

# Tabla INCIDENCIA
class Incidencia(Base):
    __tablename__ = "incidencia"

    id = Column(Integer, primary_key=True, index=True)
    fecha_emision = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")
    origen = Column(String(100))
    ots = Column(String(50))
    fecha_recepcion = Column(Date)
    observaciones = Column(Text)
    id_estado = Column(Integer, ForeignKey("estado_incidencia.id", ondelete="RESTRICT"), nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuario.id", ondelete="SET NULL"), nullable=False)
    id_transportista = Column(Integer, ForeignKey("transportista.id", ondelete="SET NULL"))

# Tabla ESTADO_TRANSPORTISTA
class EstadoTransportista(Base):
    __tablename__ = "estado_transportista"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(20), nullable=False)

# Tabla RECLAMO_TRANSPORTISTA
class ReclamoTransportista(Base):
    __tablename__ = "reclamo_transportista"

    id = Column(Integer, primary_key=True, index=True)
    id_incidencia = Column(Integer, ForeignKey("incidencia.id", ondelete="CASCADE"), nullable=False)
    monto_pagado = Column(Numeric(10, 2))
    fdr = Column(Text)
    fecha_reclamo = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")
    observacion = Column(Text)
    id_estado = Column(Integer, ForeignKey("estado_transportista.id", ondelete="RESTRICT"), nullable=False)

# Tabla DETALLE
class Detalle(Base):
    __tablename__ = "detalle"

    id = Column(Integer, primary_key=True, index=True)
    id_incidencia = Column(Integer, ForeignKey("incidencia.id", ondelete="CASCADE"), nullable=False)
    id_tipo_incidencia = Column(Integer, ForeignKey("tipo_incidencia.id", ondelete="RESTRICT"), nullable=False)
    sku_producto = Column(String(50), nullable=False)
    nro_bulto = Column(Integer, nullable=False)
    peso_origen = Column(Numeric(10, 2), nullable=False)
    peso_recepcion = Column(Numeric(10, 2), nullable=False)
    cantidad = Column(Integer, nullable=False)
    id_guia = Column(String(50), nullable=False)
    ruta_storage = Column(Text, nullable=True) 

# Tabla REPORTE
class Reporte(Base):
    __tablename__ = "reporte"

    id = Column(Integer, primary_key=True, index=True)
    fecha_generacion = Column(TIMESTAMP(timezone=True), server_default="NOW()")
    datos = Column(JSON, nullable=False)
    tipo_reporte = Column(String(30), nullable=False)
