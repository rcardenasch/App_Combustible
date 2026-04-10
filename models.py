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



db = SQLAlchemy()


# -------------------------
# TABLAS RELACION
# -------------------------
user_roles = db.Table(
    'user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'))
)

role_permissions = db.Table(
    'role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id')),
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id'))
)

# =========================
# CATEGORIA
# =========================

class Categoria(db.Model):
    __tablename__ = 'categorias'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))

    parent_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=True)

    parent = db.relationship('Categoria', remote_side=[id], backref='hijos')


class UnidadMedida(db.Model):
    __tablename__ = 'unidades_medida'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50))  # unidad, kg, caja, etc.


class Proveedor(db.Model):
    __tablename__ = 'proveedores'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150))
    telefono = db.Column(db.String(50))
    direccion = db.Column(db.String(200))


class Producto(db.Model):
    __tablename__ = 'productos'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150))
    codigo_barras = db.Column(db.String(100), unique=True, index=True)

    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'))
    unidad_id = db.Column(db.Integer, db.ForeignKey('unidades_medida.id'))

    precio_compra = db.Column(db.Float)
    precio_venta = db.Column(db.Float)
    stock = db.Column(db.Float, default=0)

    categoria = db.relationship("Categoria")
    unidad = db.relationship("UnidadMedida")
    imagen = db.Column(db.String(200))  # nombre archivo
    activo = db.Column(db.Boolean, default=True)


# =========================
# CLIENTES
# =========================

class Cliente(db.Model):
    __tablename__ = 'clientes'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150))
    documento = db.Column(db.String(20))  # DNI/RUC
    telefono = db.Column(db.String(50))
    direccion = db.Column(db.String(200))


# =========================
# VENTAS
# =========================

class Venta(db.Model):
    __tablename__ = 'ventas'

    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(LIMA)
    )
    

    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'))
    usuario_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    tipo_comprobante = db.Column(db.String(20))  # 🔥 NUEVO

    total = db.Column(db.Float)

    cliente = db.relationship("Cliente")
    usuario = db.relationship("User")

    almacen_id = db.Column(db.Integer, db.ForeignKey('almacenes.id'))
    almacen = db.relationship("Almacen")


class DetalleVenta(db.Model):
    __tablename__ = 'detalle_ventas'

    id = db.Column(db.Integer, primary_key=True)

    venta_id = db.Column(db.Integer, db.ForeignKey('ventas.id'))
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'))

    cantidad = db.Column(db.Float)
    precio = db.Column(db.Float)
    subtotal = db.Column(db.Float)

    producto = db.relationship("Producto")


# =========================
# COMPRAS
# =========================

class Compra(db.Model):
    __tablename__ = "compras"

    id = db.Column(db.Integer, primary_key=True)
    proveedor_id = db.Column(db.Integer, db.ForeignKey("proveedores.id"))
    almacen_id = db.Column(db.Integer, db.ForeignKey("almacenes.id"))
    usuario_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    total = db.Column(db.Numeric(12,2))
    fecha = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(LIMA)
    )

    proveedor = db.relationship("Proveedor")
    almacen = db.relationship("Almacen")
    usuario = db.relationship("User")

class DetalleCompra(db.Model):
    __tablename__ = 'detalle_compras'

    id = db.Column(db.Integer, primary_key=True)

    compra_id = db.Column(db.Integer, db.ForeignKey('compras.id'))
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'))

    cantidad = db.Column(db.Float)
    precio = db.Column(db.Float)
    subtotal = db.Column(db.Float)

    producto = db.relationship("Producto")


# -------------------------
# USER
# -------------------------
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(200))
    full_name = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    roles = db.relationship('Role', secondary=user_roles, backref='users')

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

#---------------------------------------------
# ALMACEN
# --------------------------------------------
class Almacen(db.Model):
    __tablename__ = 'almacenes'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    ubicacion = db.Column(db.String(200))
    activo = db.Column(db.Boolean, default=True)

class StockAlmacen(db.Model):
    __tablename__ = 'stock_almacen'

    id = db.Column(db.Integer, primary_key=True)

    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'))
    almacen_id = db.Column(db.Integer, db.ForeignKey('almacenes.id'))

    stock = db.Column(db.Float, default=0)

    producto = db.relationship("Producto")
    almacen = db.relationship("Almacen")

class KardexMovimiento(db.Model):
    __tablename__ = 'kardex_movimientos'

    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(LIMA)
    )

    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'))
    almacen_id = db.Column(db.Integer, db.ForeignKey('almacenes.id'))

    tipo_movimiento = db.Column(db.String(30))
    cantidad = db.Column(db.Float)

    stock_anterior = db.Column(db.Float)
    stock_nuevo = db.Column(db.Float)

    costo_unitario = db.Column(db.Float, default=0)

    usuario_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    observacion = db.Column(db.Text)

    compra_id = db.Column(db.Integer, db.ForeignKey('compras.id'), nullable=True)
    venta_id = db.Column(db.Integer, db.ForeignKey('ventas.id'), nullable=True)

    producto = db.relationship("Producto")
    almacen = db.relationship("Almacen")
    usuario = db.relationship("User")

class TransferenciaAlmacen(db.Model):
    __tablename__ = 'transferencias_almacen'

    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(LIMA)
    )

    almacen_origen_id = db.Column(db.Integer, db.ForeignKey('almacenes.id'))
    almacen_destino_id = db.Column(db.Integer, db.ForeignKey('almacenes.id'))

    usuario_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    observacion = db.Column(db.Text)

    origen = db.relationship("Almacen", foreign_keys=[almacen_origen_id])
    destino = db.relationship("Almacen", foreign_keys=[almacen_destino_id])
    usuario = db.relationship("User")

class TransferenciaDetalle(db.Model):
    __tablename__ = 'transferencia_detalles'

    id = db.Column(db.Integer, primary_key=True)

    transferencia_id = db.Column(db.Integer, db.ForeignKey('transferencias_almacen.id'))
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'))

    cantidad = db.Column(db.Float)
    costo_unitario = db.Column(db.Float)

    transferencia = db.relationship("TransferenciaAlmacen")
    producto = db.relationship("Producto")
#---------------------------------------------
# ALMACEN
# --------------------------------------------


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