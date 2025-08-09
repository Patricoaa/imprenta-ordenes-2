from __future__ import annotations
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import func, CheckConstraint, UniqueConstraint, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash, check_password_hash

from .extensions import db


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Cliente(db.Model, TimestampMixin):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(db.String(255), nullable=False)
    rut: Mapped[str | None] = mapped_column(db.String(50))
    telefono: Mapped[str | None] = mapped_column(db.String(50))
    correo: Mapped[str | None] = mapped_column(db.String(255))

    ordenes: Mapped[list[Orden]] = relationship("Orden", back_populates="cliente")

    def __repr__(self) -> str:
        return f"<Cliente {self.nombre}>"


class Usuario(db.Model, TimestampMixin):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(db.String(255), nullable=False)
    rol: Mapped[str] = mapped_column(db.String(50), nullable=False, default="staff")  # admin, staff, vendedor
    email: Mapped[str] = mapped_column(db.String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(db.String(255), nullable=False)

    ordenes: Mapped[list[Orden]] = relationship("Orden", back_populates="usuario")
    pagos_registrados: Mapped[list[Pago]] = relationship("Pago", back_populates="usuario_registra")

    # Flask-Login integration
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self) -> str:
        return str(self.id)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"<Usuario {self.email}>"


class Categoria(db.Model, TimestampMixin):
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(db.String(100), unique=True, nullable=False)

    vendedores: Mapped[list[Vendedor]] = relationship("Vendedor", back_populates="categoria")


class Vendedor(db.Model, TimestampMixin):
    __tablename__ = "vendedores"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(db.String(255), nullable=False)
    rut: Mapped[str | None] = mapped_column(db.String(50))
    telefono: Mapped[str | None] = mapped_column(db.String(50))
    correo: Mapped[str | None] = mapped_column(db.String(255))
    categoria_id: Mapped[int | None] = mapped_column(ForeignKey("categorias.id"))

    categoria: Mapped[Categoria | None] = relationship("Categoria", back_populates="vendedores")
    ordenes: Mapped[list[Orden]] = relationship("Orden", back_populates="vendedor")


class Orden(db.Model, TimestampMixin):
    __tablename__ = "ordenes"

    id: Mapped[int] = mapped_column(primary_key=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), nullable=False)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    vendedor_id: Mapped[int | None] = mapped_column(ForeignKey("vendedores.id"))

    fecha: Mapped[date] = mapped_column(default=date.today, nullable=False)

    precio_neto: Mapped[Decimal] = mapped_column(db.Numeric(12, 2), default=0)
    iva: Mapped[Decimal] = mapped_column(db.Numeric(12, 2), default=0)
    precio_total: Mapped[Decimal] = mapped_column(db.Numeric(12, 2), default=0)

    estado_trabajo: Mapped[str] = mapped_column(db.String(50), default="pendiente")  # pendiente, en_proceso, listo
    estado_despacho: Mapped[str] = mapped_column(db.String(50), default="pendiente")  # pendiente, despachado
    estado_pago: Mapped[str] = mapped_column(db.String(50), default="pendiente")  # pendiente, abonado, pagado

    observaciones: Mapped[str | None] = mapped_column(db.Text())

    cliente: Mapped[Cliente] = relationship("Cliente", back_populates="ordenes")
    usuario: Mapped[Usuario] = relationship("Usuario", back_populates="ordenes")
    vendedor: Mapped[Vendedor | None] = relationship("Vendedor", back_populates="ordenes")

    pagos: Mapped[list[Pago]] = relationship("Pago", back_populates="orden", cascade="all, delete-orphan")
    attachments: Mapped[list[Attachment]] = relationship("Attachment", back_populates="orden", cascade="all, delete-orphan")
    descripciones: Mapped[list[Descripcion]] = relationship("Descripcion", back_populates="orden", cascade="all, delete-orphan")

    @hybrid_property
    def abono_calc(self) -> Decimal:
        return sum((p.monto or 0) for p in self.pagos) if self.pagos else Decimal("0")

    @abono_calc.expression
    def abono_calc(cls):  # type: ignore[no-redef]
        return (
            db.select(func.coalesce(func.sum(Pago.monto), 0))
            .where(Pago.orden_id == cls.id)
            .correlate(cls)
            .scalar_subquery()
        )

    @hybrid_property
    def saldo_calc(self) -> Decimal:
        total = Decimal(self.precio_total or 0)
        return total - Decimal(self.abono_calc or 0)

    @saldo_calc.expression
    def saldo_calc(cls):  # type: ignore[no-redef]
        return (cls.precio_total - func.coalesce(
            db.select(func.sum(Pago.monto)).where(Pago.orden_id == cls.id).correlate(cls).scalar_subquery(), 0
        ))

    @hybrid_property
    def estado_calc(self) -> str:
        if (self.saldo_calc or 0) <= 0:
            return "pagada"
        if (self.abono_calc or 0) > 0:
            return "abonada"
        return "pendiente"


class Pago(db.Model, TimestampMixin):
    __tablename__ = "pagos"

    id: Mapped[int] = mapped_column(primary_key=True)
    orden_id: Mapped[int] = mapped_column(ForeignKey("ordenes.id"), nullable=False)
    monto: Mapped[Decimal] = mapped_column(db.Numeric(12, 2), nullable=False)
    fecha: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    metodo: Mapped[str] = mapped_column(db.String(50), default="transferencia")
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))

    orden: Mapped[Orden] = relationship("Orden", back_populates="pagos")
    usuario_registra: Mapped[Usuario | None] = relationship("Usuario", back_populates="pagos_registrados")


class Attachment(db.Model, TimestampMixin):
    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(primary_key=True)
    orden_id: Mapped[int] = mapped_column(ForeignKey("ordenes.id"), nullable=False)
    filename: Mapped[str] = mapped_column(db.String(255), nullable=False)
    path: Mapped[str] = mapped_column(db.String(512), nullable=False)
    uploaded_by_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))

    orden: Mapped[Orden] = relationship("Orden", back_populates="attachments")


class Log(db.Model, TimestampMixin):
    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    accion: Mapped[str] = mapped_column(db.String(100), nullable=False)
    entidad: Mapped[str] = mapped_column(db.String(100), nullable=False)
    entidad_id: Mapped[int | None]
    mensaje: Mapped[str | None] = mapped_column(db.Text())
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))


class NotificationLog(db.Model, TimestampMixin):
    __tablename__ = "notification_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    orden_id: Mapped[int | None] = mapped_column(ForeignKey("ordenes.id"))
    destinatario: Mapped[str] = mapped_column(db.String(255), nullable=False)
    canal: Mapped[str] = mapped_column(db.String(50), nullable=False)  # email, whatsapp
    asunto: Mapped[str | None] = mapped_column(db.String(255))
    mensaje: Mapped[str | None] = mapped_column(db.Text())
    estado: Mapped[str] = mapped_column(db.String(50), default="pendiente")
    respuesta: Mapped[str | None] = mapped_column(db.Text())


class Setting(db.Model, TimestampMixin):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    clave: Mapped[str] = mapped_column(db.String(100), unique=True, nullable=False)
    valor: Mapped[str | None] = mapped_column(db.Text())


class CompanyConfig(db.Model, TimestampMixin):
    __tablename__ = "company_configs"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(db.String(255), nullable=False)
    rut: Mapped[str | None] = mapped_column(db.String(50))
    direccion: Mapped[str | None] = mapped_column(db.String(255))
    telefono: Mapped[str | None] = mapped_column(db.String(50))
    email: Mapped[str | None] = mapped_column(db.String(255))


class Descripcion(db.Model, TimestampMixin):
    __tablename__ = "descripciones"

    id: Mapped[int] = mapped_column(primary_key=True)
    orden_id: Mapped[int] = mapped_column(ForeignKey("ordenes.id"), nullable=False)
    texto: Mapped[str] = mapped_column(db.String(500), nullable=False)
    cantidad: Mapped[int] = mapped_column(db.Integer, default=1)
    precio_unitario: Mapped[Decimal] = mapped_column(db.Numeric(12, 2), default=0)
    subtotal: Mapped[Decimal] = mapped_column(db.Numeric(12, 2), default=0)

    orden: Mapped[Orden] = relationship("Orden", back_populates="descripciones")

    def recompute(self):
        self.subtotal = Decimal(self.cantidad or 0) * Decimal(self.precio_unitario or 0)