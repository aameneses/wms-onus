"""
database.py - Modelos SQLAlchemy para WMS ONUS EXPRESS v2
"""
import os
from datetime import date
from sqlalchemy import (
    create_engine, Column, Integer, String, Numeric,
    Boolean, Date, Text, ForeignKey, DateTime, func, UniqueConstraint
)
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker, Session
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

load_dotenv()


class Base(DeclarativeBase):
    pass


class Tarifa(Base):
    __tablename__ = "tarifas"
    id                = Column(Integer, primary_key=True, autoincrement=True)
    nombre            = Column(String(100), nullable=False)
    precio_pallet_dia = Column(Numeric(10, 2), nullable=False, default=0)
    precio_picking    = Column(Numeric(10, 2), nullable=False, default=0)
    precio_carga      = Column(Numeric(10, 2), nullable=False, default=0)
    precio_descarga   = Column(Numeric(10, 2), nullable=False, default=0)
    created_at        = Column(DateTime(timezone=True), server_default=func.now())
    updated_at        = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    clientes          = relationship("Cliente", back_populates="tarifa")
    detalles          = relationship("TarifaDetalle", back_populates="tarifa", cascade="all, delete")


class TarifaDetalle(Base):
    """Precios por tipo de servicio dentro de una tarifa."""
    __tablename__ = "tarifas_detalle"
    __table_args__ = (UniqueConstraint("tarifa_id", "tipo_servicio"),)
    id            = Column(Integer, primary_key=True, autoincrement=True)
    tarifa_id     = Column(Integer, ForeignKey("tarifas.id", ondelete="CASCADE"), nullable=False)
    tipo_servicio = Column(String(50), nullable=False)
    tipo_calculo  = Column(String(20), nullable=False, default="por_unidad")
    precio        = Column(Numeric(10, 2), nullable=False, default=0)
    descripcion   = Column(Text)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())
    updated_at    = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    tarifa        = relationship("Tarifa", back_populates="detalles")


class TarifaCliente(Base):
    """Tarifa personalizada negociada para un cliente específico."""
    __tablename__ = "tarifas_cliente"
    __table_args__ = (UniqueConstraint("cliente_id", "tipo_servicio"),)
    id            = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id    = Column(Integer, ForeignKey("clientes.id", ondelete="CASCADE"), nullable=False)
    tipo_servicio = Column(String(50), nullable=False)
    tipo_calculo  = Column(String(20), nullable=False, default="por_unidad")
    precio        = Column(Numeric(10, 2), nullable=False, default=0)
    descripcion   = Column(Text)
    activo        = Column(Boolean, nullable=False, default=True)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())
    updated_at    = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    cliente       = relationship("Cliente", back_populates="tarifas_personalizadas")


class Cliente(Base):
    __tablename__ = "clientes"
    id               = Column(Integer, primary_key=True, autoincrement=True)
    nombre           = Column(String(100), nullable=False)
    empresa          = Column(String(150))
    condiciones_pago = Column(String(200))
    tarifa_id        = Column(Integer, ForeignKey("tarifas.id", ondelete="SET NULL"), nullable=True)
    email            = Column(String(150))
    telefono         = Column(String(50))
    created_at       = Column(DateTime(timezone=True), server_default=func.now())
    updated_at       = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    tarifa                 = relationship("Tarifa", back_populates="clientes")
    movimientos            = relationship("Movimiento", back_populates="cliente", cascade="all, delete")
    stock                  = relationship("Stock", back_populates="cliente", cascade="all, delete")
    tarifas_personalizadas = relationship("TarifaCliente", back_populates="cliente", cascade="all, delete")


class Stock(Base):
    __tablename__ = "stock"
    id           = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id   = Column(Integer, ForeignKey("clientes.id", ondelete="CASCADE"), nullable=False)
    pallet       = Column(String(100), nullable=False)
    referencia   = Column(String(100))
    cantidad     = Column(Integer, nullable=False, default=1)
    fecha_entrada = Column(Date, nullable=False, default=date.today)
    fecha_salida  = Column(Date, nullable=True)
    activo       = Column(Boolean, nullable=False, default=True)
    observaciones = Column(Text)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())
    cliente      = relationship("Cliente", back_populates="stock")


class Movimiento(Base):
    __tablename__ = "movimientos"
    id           = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id   = Column(Integer, ForeignKey("clientes.id", ondelete="CASCADE"), nullable=False)
    tipo         = Column(String(50), nullable=False)
    cantidad     = Column(Numeric(10, 2), nullable=False, default=1)
    fecha        = Column(Date, nullable=False, default=date.today)
    observaciones = Column(Text)
    coste        = Column(Numeric(10, 2))
    created_at   = Column(DateTime(timezone=True), server_default=func.now())
    cliente      = relationship("Cliente", back_populates="movimientos")


def get_engine():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL no configurada.")
    return create_engine(
        db_url,
        poolclass=NullPool,
        echo=False,
        connect_args={"sslmode": "require", "connect_timeout": 10},
    )


def get_session() -> Session:
    engine = get_engine()
    SessionLocal = sessionmaker(bind=engine, autoflush=True, autocommit=False, expire_on_commit=False)
    return SessionLocal()
