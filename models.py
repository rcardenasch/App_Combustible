from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pytz
from flask_login import current_user
from sqlalchemy.sql import func

# Zona horaria Lima
LIMA = pytz.timezone("America/Lima")

def now_lima():
    return datetime.now(LIMA)

db = SQLAlchemy()


# -------------------------
# TABLAS RELACION
# -------------------------
user_roles = db.Table(
    'user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('usuarios.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'))
)

role_permissions = db.Table(
    'role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id')),
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id'))
)
# -------------------------
# USUARIOS
# -------------------------
class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(200))
    full_name = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=now_lima)

    roles = db.relationship('Role', secondary=user_roles, backref='usuarios')
    proyecto_id = db.Column(db.Integer, db.ForeignKey("proyectos.id"), nullable=True)
    proyectos = db.relationship("Proyecto", backref="usuarios")

    # 🔐 PASSWORD
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # 🔐 PERMISOS
    def has_permission(self, permiso):
        try:
            modulo, accion = permiso.split(".")
        except ValueError:
            return False

        for rol in self.roles:
            for p in rol.permissions:
                if p.module.name == modulo and p.action == accion:
                    return True

        return False


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

    permissions = db.relationship(
        'Permission',
        secondary=role_permissions,
        backref='roles'
    )


class Permission(db.Model):
    __tablename__ = 'permissions'
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'))
    action = db.Column(db.String(50))

    module = db.relationship("Module")

class Module(db.Model):
    __tablename__ = 'module'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

# =========================
# PROYECTOS
# =========================
class Proyecto(db.Model):
    __tablename__ = "proyectos"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    ubicacion = db.Column(db.Text)
    nombre_corto=db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)

    vehiculos = db.relationship("Vehiculo", backref="proyecto", lazy=True)
    tanques = db.relationship("Tanque", backref="proyecto", lazy=True)


# =========================
# VEHICULOS / MAQUINARIA
# =========================
class Vehiculo(db.Model):
    __tablename__ = "vehiculos"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(250), nullable=False)
    placa = db.Column(db.String(20))
    tipo = db.Column(db.String(50))  # CAMIONETA, EXCAVADORA, etc

    rendimiento_promedio = db.Column(db.Float)  # km/gal o hr/gal
    ultimo_horometro_abastecimiento = db.Column(db.Float)

    activo = db.Column(db.Boolean, default=True)

    proyecto_id = db.Column(db.Integer, db.ForeignKey("proyectos.id"))

    kardex = db.relationship("Kardex", backref="vehiculo", lazy=True)
    rendimientos = db.relationship("Rendimiento", backref="vehiculo", lazy=True)

# =========================
# OPERADORES
# =========================
class Operador(db.Model):
    __tablename__ = "operadores"

    id = db.Column(db.Integer, primary_key=True)

    nombre = db.Column(db.String(150), nullable=False)

    documento = db.Column(db.String(20))  # DNI opcional

    activo = db.Column(db.Boolean, default=True)

    proyecto_id = db.Column(db.Integer, db.ForeignKey("proyectos.id"))

    proyecto = db.relationship("Proyecto", backref="operadores")


# =========================
# TANQUES
# =========================
class Tanque(db.Model):
    __tablename__ = "tanques"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

    capacidad = db.Column(db.Float, nullable=False)
    stock_actual = db.Column(db.Float, default=0)
    stock_minimo = db.Column(db.Float, default=0)

    proyecto_id = db.Column(db.Integer, db.ForeignKey("proyectos.id"))

    kardex = db.relationship("Kardex", backref="tanque", lazy=True)


# =========================
# KARDEX (MOVIMIENTOS)
# =========================
class Kardex(db.Model):
    __tablename__ = "kardex"

    id = db.Column(db.Integer, primary_key=True)

    tipo = db.Column(db.String(20), nullable=False)  
    # ENTRADA (tanque) / SALIDA (vehículo) / OPERACION (solo horómetro)

    fecha = db.Column(db.DateTime, default=now_lima)

    # relaciones
    tanque_id = db.Column(db.Integer, db.ForeignKey("tanques.id"), nullable=True)
    vehiculo_id = db.Column(db.Integer, db.ForeignKey("vehiculos.id"), nullable=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"))

    # datos operativos
    cantidad = db.Column(db.Float, default=0)  # combustible

    horometro_inicial = db.Column(db.Float, nullable=True)
    horometro_final = db.Column(db.Float, nullable=True)

    kilometraje = db.Column(db.Float, nullable=True)

    parte_diario = db.Column(db.String(20))  # 501, 502, etc

    tanque_lleno = db.Column(db.Boolean, default=False)

    observacion = db.Column(db.Text)

    referencia = db.Column(db.Text)

    creado_en = db.Column(db.DateTime, default=now_lima)

    operador_id = db.Column(db.Integer, db.ForeignKey("operadores.id"), nullable=True)

    operador = db.relationship("Operador")
# =========================
# RENDIMIENTO (AUDITORIA)
# =========================
class Rendimiento(db.Model):
    __tablename__ = "rendimientos"

    id = db.Column(db.Integer, primary_key=True)

    vehiculo_id = db.Column(db.Integer, db.ForeignKey("vehiculos.id"))

    fecha = db.Column(db.DateTime, default=now_lima)

    horometro_abastecimiento_inicial = db.Column(db.Float)
    horometro_abastecimiento_final = db.Column(db.Float)

    consumo_total = db.Column(db.Float)
    recorrido_total = db.Column(db.Float)

    rendimiento_calculado = db.Column(db.Float)

    estado = db.Column(db.String(20))  # NORMAL, ALTO, BAJO

    tipo_control = db.Column(db.String(20))  # "PARCIAL" o "TANQUE_LLENO"

    observacion = db.Column(db.Text)



# =========================
# ALERTAS (OPCIONAL PERO PRO)
# =========================
class Alerta(db.Model):
    __tablename__ = "alertas"

    id = db.Column(db.Integer, primary_key=True)

    tipo = db.Column(db.String(50))  # STOCK_CRITICO, RENDIMIENTO_BAJO
    mensaje = db.Column(db.Text)

    fecha = db.Column(db.DateTime, default=now_lima)

    leido = db.Column(db.Boolean, default=False)

    proyecto_id = db.Column(db.Integer, db.ForeignKey("proyectos.id"), nullable=True)
    tanque_id = db.Column(db.Integer, db.ForeignKey("tanques.id"), nullable=True)
    vehiculo_id = db.Column(db.Integer, db.ForeignKey("vehiculos.id"), nullable=True)