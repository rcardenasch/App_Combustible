# =========================
# app.py
# =========================

from flask import Flask, request, redirect, url_for, render_template, flash, jsonify,send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import (db,Usuario, Role, Permission,Module,Proyecto,Vehiculo,Alerta,Operador,Kardex,Rendimiento,Tanque)

from config import Config
from functools import wraps
from flask import jsonify
import os
from werkzeug.utils import secure_filename
from flask import get_flashed_messages
import re
import json
import uuid
from sqlalchemy import cast, String,or_,func
from datetime import datetime,timedelta
from sqlalchemy import text
from openpyxl import Workbook
import io
from openpyxl.styles import PatternFill

# ------------------------
# APP
# ------------------------
app = Flask(__name__, static_folder='static')
app.config.from_object(Config)

# ------------------------
# INIT
# ------------------------
db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = None


@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Usuario, int(user_id))


# ------------------------
# CONFIG PERMISOS
# ------------------------
MODULOS = [
    "usuarios",
    "roles",
    "proyectos",
    "vehiculos",
    "operadores",
    "tanques",
    "rendimientos",
    "kardex"
]

ACCIONES = ["ver", "crear", "editar", "eliminar"]

ACCIONES_KARDEX = ["ver", "editar", "ajustar", "resetear"]


def now_utc():
    return datetime.utcnow()
# ------------------------
# SEED (MANUAL)
# ------------------------
def seed_data():
    try:
        role_admin = Role.query.filter_by(name="admin").first()
        if not role_admin:
            role_admin = Role(name="admin")
            db.session.add(role_admin)
            db.session.commit()

        admin = Usuario.query.filter_by(username="admin").first()
        if not admin:
            admin = Usuario(
                username="admin",
                email="admin@test.com",
                full_name="Administrador"
            )
            admin.set_password("admin")
            db.session.add(admin)
            db.session.commit()

        if role_admin not in admin.roles:
            admin.roles.append(role_admin)
            db.session.commit()

        for nombre_modulo in MODULOS:
            mod = Module.query.filter_by(name=nombre_modulo).first()

            if not mod:
                mod = Module(name=nombre_modulo)
                db.session.add(mod)
                db.session.commit()

            acciones_modulo = ACCIONES_KARDEX if nombre_modulo == "kardex" else ACCIONES

            for acc in acciones_modulo:
                perm = Permission.query.filter_by(
                    module_id=mod.id,
                    action=acc
                ).first()

                if not perm:
                    db.session.add(Permission(module_id=mod.id, action=acc))

        db.session.commit()

        for perm in Permission.query.all():
            if perm not in role_admin.permissions:
                role_admin.permissions.append(perm)

        db.session.commit()

        print("✅ Datos iniciales OK")

    except Exception as e:
        print("⚠️ Error en seed:", e)


# ------------------------
# SOLO TEST DE ARRANQUE (LIVIANO)
# ------------------------
#  https://tu-app.onrender.com/init para ejecutar manualmente el init (seed_data())
@app.route("/init")
def init():
    try:
        seed_data()
        return {"msg": "seed ejecutado"}, 200
    except Exception as e:
        return {"error": str(e)}, 500

# ------------------------
# CONTEXTO INICIALIZACION (SEGURO)
# ------------------------
with app.app_context():
    try:
        print("🚀 Iniciando aplicación...")

        # SOLO crear tablas
        db.create_all()

        print("✅ Tablas verificadas")

    except Exception as e:
        print("❌ Error al iniciar BD:", e)

#-- Funciones globales--
def validar_texto(valor, campo, min_len=3, max_len=150):
    if not valor:
        return f"{campo} es obligatorio"
    if len(valor) < min_len:
        return f"{campo} debe tener al menos {min_len} caracteres"
    if len(valor) > max_len:
        return f"{campo} no debe exceder {max_len} caracteres"
    return None


def validar_numero(valor, campo, tipo=float, minimo=0):
    try:
        num = tipo(valor)
        if num < minimo:
            return f"{campo} no puede ser negativo"
        return None
    except:
        return f"{campo} inválido"


def validar_email(email):
    if not email:
        return None
    regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(regex, email):
        return "Email inválido"
    return None

# =========================
# PERMISOS
# =========================
def permission_required(modulo, accion):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("login"))

            permiso = f"{modulo}.{accion}"

            if not current_user.has_permission(permiso):
                flash("No tienes permisos", "danger")
                return redirect(url_for("index"))

            return f(*args, **kwargs)
        return wrapper
    return decorator


# =========================
# RUTAS BASE
# =========================

@app.route('/')
@login_required
def index():
    #return redirect(url_for("dashboard"))
    return redirect(url_for("rendimiento_list"))
    
    

@app.route('/login', methods=['GET','POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == 'POST':
        usuario = Usuario.query.filter_by(username=request.form['username']).first()

        if usuario and usuario.check_password(request.form['password']):
            login_user(usuario)
            return redirect(url_for('index'))

        flash('Credenciales inválidas','danger')

    return render_template("login.html")

@app.route('/logout')
@login_required
def logout():
    from flask import session
    logout_user()
    session.clear()  # 🔥 borra toda la sesión
    return redirect(url_for('login'))


# =========================
# CRUD USUARIOS
# =========================
@app.route("/usuarios")
@login_required
@permission_required("usuarios","ver")
def usuarios_list():
    #print([ (p.module.name, p.action) for r in current_user.roles for p in r.permissions ])
    #return "SI FUNCIONA USUARIOS"
    return render_template(
        "usuarios.html",
        lista=Usuario.query.all(),
        roles=Role.query.all()
    )
@app.route("/usuarios/nuevo", methods=["POST"])
@login_required
@permission_required("usuarios","crear")
def usuarios_nuevo():
    try:
        # -------------------------
        # OBTENER DATOS
        # -------------------------
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        full_name = request.form.get("full_name")
        roles_ids = request.form.getlist("roles")  # 👈 importante
        proyecto_ids=request.form.getlist("proyectos")

        # -------------------------
        # VALIDACIONES
        # -------------------------
        if not username or not password:
            flash("Usuario y contraseña son obligatorios", "danger")
            return redirect(url_for("usuarios_list"))

        # Usuario único
        if Usuario.query.filter_by(username=username).first():
            flash("El username ya existe", "warning")
            return redirect(url_for("usuarios_list"))

        # Email único (opcional pero recomendado)
        if email and Usuario.query.filter_by(email=email).first():
            flash("El email ya está registrado", "warning")
            return redirect(url_for("usuarios_list"))

        # -------------------------
        # CREAR USUARIO
        # -------------------------
        nuevo_usuario = Usuario(
            username=username,
            email=email,
            full_name=full_name
        )

        # 🔐 usar tu método del modelo
        nuevo_usuario.set_password(password)

        # -------------------------
        # ASIGNAR ROLES
        # -------------------------
        if roles_ids:
            roles = Role.query.filter(Role.id.in_(roles_ids)).all()
            nuevo_usuario.roles = roles  # 👈 relación many-to-many
        # -------------------------
        # ASIGNAR Proyectos
        # -------------------------
        if proyecto_ids:
            proyectos = Proyecto.query.filter(Proyecto.id.in_(proyecto_ids)).all()
            nuevo_usuario.proyectos = proyectos 
        # -------------------------
        # GUARDAR
        # -------------------------
        db.session.add(nuevo_usuario)
        db.session.commit()

        flash("Usuario creado correctamente", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error al crear usuario: {str(e)}", "danger")

    return redirect(url_for("usuarios_list"))

@app.route("/usuarios/editar/<int:id>", methods=["POST"])
@login_required
@permission_required("usuarios","editar")
def usuarios_editar(id):
    usuario = Usuario.query.get_or_404(id)

    try:
        username = request.form.get("username")
        email = request.form.get("email")
        full_name = request.form.get("full_name")
        roles_ids = request.form.getlist("roles")
        proyectos_ids=request.form.getlist("proyectos")

        # -------------------------
        # VALIDACIONES
        # -------------------------
        if not username:
            flash("El username es obligatorio", "danger")
            return redirect(url_for("usuarios_list"))

        # Validar username único (excepto el mismo usuario)
        existe = Usuario.query.filter(Usuario.username == username, Usuario.id != id).first()
        if existe:
            flash("El username ya está en uso", "warning")
            return redirect(url_for("usuarios_list"))

        # Validar email único
        if email:
            existe_email = Usuario.query.filter(Usuario.email == email, Usuario.id != id).first()
            if existe_email:
                flash("El email ya está en uso", "warning")
                return redirect(url_for("usuarios_list"))

        # -------------------------
        # ACTUALIZAR DATOS
        # -------------------------
        usuario.username = username
        usuario.email = email
        usuario.full_name = full_name

        # -------------------------
        # ACTUALIZAR ROLES
        # -------------------------
        usuario.roles = []  # limpiar roles actuales

        if roles_ids:
            roles = Role.query.filter(Role.id.in_(roles_ids)).all()
            usuario.roles = roles
        # -------------------------
        # ACTUALIZAR proyectos
        # -------------------------
        if proyectos_ids:
            proyectos = Proyecto.query.filter(Proyecto.id.in_(proyectos_ids)).all()
            usuario.proyectos = proyectos    

        db.session.commit()
        flash("Usuario actualizado correctamente", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error al actualizar: {str(e)}", "danger")

    return redirect(url_for("usuarios_list"))

@app.route("/usuarios/eliminar/<int:id>", methods=["POST"])
@login_required
@permission_required("usuarios","eliminar")
def usuarios_eliminar(id):
    usuario = Usuario.query.get_or_404(id)

    try:
        # ⚠️ evitar eliminarse a sí mismo
        if usuario.id == current_user.id:
            flash("No puedes eliminar tu propio usuario", "warning")
            return redirect(url_for("usuarios_list"))

        db.session.delete(usuario)
        db.session.commit()

        flash("Usuario eliminado correctamente", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error al eliminar: {str(e)}", "danger")

    return redirect(url_for("usuarios_list"))

# =========================
# CRUD ROLES
# =========================

@app.route("/roles")
@login_required
@permission_required("roles", "ver")
def roles_list():
    
    permisos = Permission.query.all()

    from collections import defaultdict
    permisos_agrupados = defaultdict(list)

    for p in permisos:
        modulo = p.module.name if p.module else "Sin módulo"
        permisos_agrupados[modulo].append(p)

    return render_template(
        "roles.html",
        lista=Role.query.all(),
        permisos=permisos,  # reutilizas
        permisos_agrupados=permisos_agrupados,
        modulos=Module.query.all()
    )


@app.route("/roles/nuevo", methods=["POST"])
@login_required
@permission_required("roles", "crear")
def roles_nuevo():
    try:
        name = request.form.get("name")
        permisos_ids = request.form.getlist("permisos")

        if not name:
            flash("El nombre del rol es obligatorio", "danger")
            return redirect(url_for("roles_list"))

        if Role.query.filter_by(name=name).first():
            flash("El rol ya existe", "warning")
            return redirect(url_for("roles_list"))

        nuevo = Role(name=name)

        if permisos_ids:
            permisos = Permission.query.filter(Permission.id.in_(permisos_ids)).all()
            nuevo.permissions = permisos

        db.session.add(nuevo)
        db.session.commit()

        flash("Rol creado correctamente", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", "danger")

    return redirect(url_for("roles_list"))


@app.route("/roles/editar/<int:id>", methods=["POST"])
@login_required
@permission_required("roles", "editar")
def roles_editar(id):
    rol = Role.query.get_or_404(id)

    try:
        rol.name = request.form.get("name")
        permisos_ids = request.form.getlist("permisos")

        # actualizar permisos
        rol.permissions = []
        if permisos_ids:
            permisos = Permission.query.filter(Permission.id.in_(permisos_ids)).all()
            rol.permissions = permisos

        db.session.commit()
        flash("Rol actualizado", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", "danger")

    return redirect(url_for("roles_list"))


@app.route("/roles/eliminar/<int:id>", methods=["POST"])
@login_required
@permission_required("roles", "eliminar")
def roles_eliminar(id):
    rol = Role.query.get_or_404(id)

    try:
        db.session.delete(rol)
        db.session.commit()
        flash("Rol eliminado", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"No se pudo eliminar: {str(e)}", "danger")

    return redirect(url_for("roles_list"))


# =========================
# VEHICULOS
# =========================
@app.route("/vehiculos")
@login_required
@permission_required("vehiculos", "ver")
def vehiculos_list():
    return render_template(
        "vehiculos.html",
        lista=Vehiculo.query.all(),
        proyectos=Proyecto.query.all()
    )


@app.route("/vehiculos/nuevo", methods=["POST"])
@login_required
@permission_required("vehiculos", "crear")
def vehiculos_nuevo():

    try:
        nombre = request.form.get("nombre", "").strip()
        placa = request.form.get("placa", "").strip()
        tipo = request.form.get("tipo")
        proyecto_id = request.form.get("proyecto_id")
        rendimiento = request.form.get("rendimiento_promedio")

        if not nombre:
            flash("Debe ingresar el equipo", "danger")
            return redirect(url_for("vehiculos_list"))
        
        # Validar vehiculo único (excepto el mismo usuario)
        existe = Vehiculo.query.filter(Vehiculo.placa == placa).first()
        if existe:
            flash("La placa del vehículo ya está en uso", "warning")
            return redirect(url_for("vehiculos_list"))
        
        try:
            rendimiento = float(rendimiento) if rendimiento else None
        except:
            flash("Rendimiento inválido", "danger")
            return redirect(url_for("vehiculos_list"))
        

        nuevo = Vehiculo(
            nombre=nombre,
            placa=placa,
            tipo=tipo,
            proyecto_id=int(proyecto_id) if proyecto_id else None,
            rendimiento_promedio=rendimiento
        )

        db.session.add(nuevo)
        db.session.commit()

        flash("✅ Vehículo creado", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", "danger")

    return redirect(url_for("vehiculos_list"))


@app.route("/vehiculos/editar/<int:id>", methods=["POST"])
@login_required
@permission_required("vehiculos", "editar")
def vehiculos_editar(id):
    vehiculo = Vehiculo.query.get_or_404(id)

    try:
        nombre = request.form.get("nombre")
        placa = request.form.get("placa")
        tipo = request.form.get("tipo")
        rendimiento = request.form.get("rendimiento_promedio")
        proyecto_id=request.form.get("proyecto_id")

        # -------------------------
        # VALIDACIONES
        # -------------------------
        if not nombre:
            flash("El nombre es obligatorio", "danger")
            return redirect(url_for("vehiculos_list"))

        # -------------------------
        # ACTUALIZAR DATOS
        # -------------------------
        vehiculo.nombre = nombre
        vehiculo.placa = placa
        vehiculo.tipo = tipo
        vehiculo.rendimiento_promedio=float(rendimiento) if rendimiento else None
        vehiculo.proyecto_id=int(proyecto_id) if proyecto_id else None

        db.session.commit()
        flash("Vehiculo actualizado", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", "danger")

    return redirect(url_for("vehiculos_list"))


@app.route("/vehiculo/eliminar/<int:id>", methods=["POST"])
@login_required
@permission_required("vehiculos", "eliminar")
def vehiculos_eliminar(id):

    vehiculo = Vehiculo.query.get_or_404(id)

    try:
        db.session.delete(vehiculo)
        db.session.commit()
        flash("Vehiculo eliminado", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"No se pudo eliminar: {str(e)}", "danger")
        flash(str(e), "danger")

    return redirect(url_for("vehiculos_list"))

# =========================
# PROYECTOS
# =========================

@app.route("/proyectos")
@login_required
@permission_required("proyectos","ver")
def proyectos_list():

    lista = Proyecto.query.order_by(Proyecto.id.desc()).all()

    return render_template(
        "proyectos.html",
        lista=lista
    )

@app.route("/proyectos/nuevo", methods=["POST"])
@login_required
@permission_required("proyectos","crear")
def proyectos_nuevo():

    nombre = request.form.get("nombre")
    ubicacion = request.form.get("ubicacion")
    nombre_corto = request.form.get("nombre_corto")

    nuevo = Proyecto(
        nombre=nombre,
        ubicacion=ubicacion,
        nombre_corto=nombre_corto,
        activo=True
    )

    db.session.add(nuevo)
    db.session.commit()

    flash("Proyecto registrado correctamente", "success")

    return redirect(url_for("proyectos_list"))


@app.route("/proyectos/editar/<int:id>", methods=["POST"])
@login_required
@permission_required("proyectos","editar")
def proyectos_editar(id):

    proyecto = Proyecto.query.get_or_404(id)

    proyecto.nombre = request.form.get("nombre")
    proyecto.ubicacion = request.form.get("ubicacion")
    proyecto.nombre_corto = request.form.get("nombre_corto")
    proyecto.activo = True if request.form.get("activo") == "1" else False

    db.session.commit()

    flash("Proyecto actualizado correctamente", "success")

    return redirect(url_for("proyectos_list"))


@app.route("/proyectos/eliminar/<int:id>", methods=["POST"])
@login_required
@permission_required("proyectos","eliminar")
def proyectos_eliminar(id):

    proyecto = Proyecto.query.get_or_404(id)

    db.session.delete(proyecto)
    db.session.commit()

    flash("Proyecto eliminado correctamente", "success")

    return redirect(url_for("proyectos_list"))

# =========================
# OPERADORES
# =========================
@app.route("/operadores")
@login_required
@permission_required("operadores", "ver")
def operadores_list():
    return render_template(
        "operadores.html",
        lista=Operador.query.all(),
        proyectos=Proyecto.query.all()
    )

@app.route("/operadores/nuevo", methods=["POST"])
@login_required
@permission_required("operadores", "crear")
def operadores_nuevo():

    try:
        nombre = request.form.get("nombre", "").strip()
        documento = request.form.get("documento", "").strip()
        proyecto_id = request.form.get("proyecto_id")

        if not nombre:
            flash("Debe ingresar nombre", "danger")
            return redirect(url_for("operadores_list"))

        nuevo = Operador(
            nombre=nombre,
            documento=documento,
            proyecto_id=int(proyecto_id) if proyecto_id else None
        )

        db.session.add(nuevo)
        db.session.commit()

        flash("✅ Operador creado", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", "danger")

    return redirect(url_for("operadores_list"))


@app.route("/operadores/editar/<int:id>", methods=["POST"])
@login_required
@permission_required("operadores", "editar")
def operadores_editar(id):

    operador = Operador.query.get_or_404(id)

    try:
        nombre = request.form.get("nombre", "").strip()
        documento = request.form.get("documento", "").strip()
        proyecto_id = request.form.get("proyecto_id")

        if not nombre:
            flash("Debe ingresar nombre", "danger")
            return redirect(url_for("operadores_list"))

        operador.nombre = nombre
        operador.documento = documento
        operador.proyecto_id = int(proyecto_id) if proyecto_id else None

        db.session.commit()

        flash("Operador actualizado", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", "danger")

    return redirect(url_for("operadores_list"))


@app.route("/operadores/eliminar/<int:id>", methods=["POST"])
@login_required
@permission_required("operadores", "eliminar")
def operadores_eliminar(id):

    operador = Operador.query.get_or_404(id)

    try:
        db.session.delete(operador)
        db.session.commit()

        flash("Operador eliminado", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", "danger")

    return redirect(url_for("operadores_list"))
# =========================
# TANQUES
# =========================

@app.route("/tanques")
@login_required
@permission_required("tanques", "ver")
def tanques_list():
    return render_template(
        "tanques.html",
        lista=Tanque.query.all(),
        proyectos=Proyecto.query.all()
    )

@app.route("/tanques/nuevo", methods=["POST"])
@login_required
@permission_required("tanques", "crear")
def tanques_nuevo():

    try:
        nombre = request.form.get("nombre", "").strip()
        capacidad = request.form.get("capacidad")
        stock = request.form.get("stock_actual")
        minimo = request.form.get("stock_minimo")
        proyecto_id = request.form.get("proyecto_id")

        if not nombre:
            flash("Debe ingresar nombre", "danger")
            return redirect(url_for("tanques_list"))

        try:
            capacidad = float(capacidad)
            stock = float(stock)
            minimo = float(minimo)
        except:
            flash("Valores numéricos inválidos", "danger")
            return redirect(url_for("tanques_list"))

        nuevo = Tanque(
            nombre=nombre,
            capacidad=capacidad,
            stock_actual=stock,
            stock_minimo=minimo,
            proyecto_id=int(proyecto_id) if proyecto_id else None,
        )

        db.session.add(nuevo)
        db.session.commit()

        flash("✅ Tanque creado", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", "danger")

    return redirect(url_for("tanques_list"))


@app.route("/tanques/editar/<int:id>", methods=["POST"])
@login_required
@permission_required("tanques", "editar")
def tanques_editar(id):

    tanque = Tanque.query.get_or_404(id)

    try:
        tanque.nombre = request.form.get("nombre")
        tanque.capacidad = float(request.form.get("capacidad") or 0)
        tanque.stock_actual = float(request.form.get("stock_actual") or 0)
        tanque.stock_minimo = float(request.form.get("stock_minimo") or 0)

        db.session.commit()

        flash("Tanque actualizado", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", "danger")

    return redirect(url_for("tanques_list"))


@app.route("/tanques/eliminar/<int:id>", methods=["POST"])
@login_required
@permission_required("tanques", "eliminar")
def tanques_eliminar(id):

    tanque = Tanque.query.get_or_404(id)

    try:
        db.session.delete(tanque)
        db.session.commit()

        flash("Tanque eliminado", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", "danger")

    return redirect(url_for("tanques_list"))
#--------------------------------------------------
# KARDEX
#--------------------------------------------------
@app.route("/kardex")
@login_required
@permission_required("kardex", "ver")
def kardex_list():
    return render_template(
        "kardex.html",
        lista=Kardex.query.order_by(Kardex.fecha.desc()).all(),
        vehiculos=Vehiculo.query.all(),
        tanques=Tanque.query.all(),
        operadores=Operador.query.all()
    )

@app.route("/kardex/nuevo", methods=["POST"])
@login_required
@permission_required("kardex", "crear")
def kardex_nuevo():

    try:
        tipo = request.form.get("tipo")
        tanque_id = request.form.get("tanque_id")
        vehiculo_id = request.form.get("vehiculo_id")
        operador_id = request.form.get("operador_id")
        tanque_lleno = request.form.get("tanque_lleno") == "on"

        cantidad = request.form.get("cantidad")
        h_final = request.form.get("horometro_final")

        hace_5_seg = now_utc() - timedelta(seconds=5)

        existe = Kardex.query.filter(
            Kardex.vehiculo_id == vehiculo_id,
            Kardex.cantidad == cantidad,
            Kardex.fecha >= hace_5_seg
        ).first()

        if existe:
            flash("Movimiento duplicado detectado", "warning")
            return redirect(url_for("kardex_list"))

        # =========================
        # PARSEO SEGURO
        # =========================
        try:
            cantidad = float(cantidad) if cantidad else 0
        except:
            flash("Cantidad inválida", "danger")
            return redirect(url_for("kardex_list"))

        try:
            h_final = float(h_final) if h_final else None
        except:
            flash("Horómetro inválido", "danger")
            return redirect(url_for("kardex_list"))

        parte = request.form.get("parte_diario")
        obs = request.form.get("observacion")

        if tipo not in ["ENTRADA", "SALIDA", "OPERACION"]:
            flash("Tipo inválido", "danger")
            return redirect(url_for("kardex_list"))

        tanque = Tanque.query.get(int(tanque_id)) if tanque_id else None

        # =========================
        # VALIDACIÓN SALIDA
        # =========================
        if tipo == "SALIDA":

            if not tanque:
                flash("Debe seleccionar un tanque", "danger")
                return redirect(url_for("kardex_list"))

            if not vehiculo_id:
                flash("Debe seleccionar un vehículo", "danger")
                return redirect(url_for("kardex_list"))

            if cantidad <= 0:
                flash("Cantidad debe ser mayor a 0", "danger")
                return redirect(url_for("kardex_list"))

            if tanque.stock_actual < cantidad:
                flash(f"Stock insuficiente ({tanque.stock_actual})", "danger")
                return redirect(url_for("kardex_list"))

        # =========================
        # 🔥 ÚLTIMO HORÓMETRO REAL
        # =========================
        h_inicial = 0
        if vehiculo_id:
            vehiculo_id = int(vehiculo_id)

            ultimo = Kardex.query.filter(
                Kardex.vehiculo_id == vehiculo_id,
                Kardex.horometro_final != None
            ).order_by(Kardex.fecha.desc()).first()

            if ultimo:
                h_inicial = float(ultimo.horometro_final)

        # =========================
        # ⚠️ NORMALIZAR HORÓMETRO
        # =========================
        if tipo == "SALIDA":

            if h_final is None:
                # 🔥 CASO CLAVE: NO INGRESA HORÓMETRO
                h_final = h_inicial

            if h_final < h_inicial:
                flash("Horómetro final no puede ser menor", "danger")
                return redirect(url_for("kardex_list"))

        # =========================
        # RECORRIDO
        # =========================
        recorrido = h_final - h_inicial if h_final is not None else 0

        # =========================
        # CREAR MOVIMIENTO
        # =========================
        nuevo = Kardex(
            tipo=tipo,
            tanque_id=int(tanque_id) if tanque_id else None,
            vehiculo_id=vehiculo_id,
            usuario_id=current_user.id,
            cantidad=cantidad,
            horometro_inicial=h_inicial,
            horometro_final=h_final,
            tanque_lleno=tanque_lleno,
            parte_diario=parte,
            observacion=obs,
            operador_id=int(operador_id) if operador_id else None
        )

        db.session.add(nuevo)
        db.session.flush()  # 🔥 IMPORTANTE

        # =========================
        # STOCK
        # =========================
        if tipo == "ENTRADA":
            tanque.stock_actual += cantidad

        elif tipo == "SALIDA":
            tanque.stock_actual -= cantidad

        # =========================
        # 🚀 CONTROL TANQUE LLENO
        # =========================
        if tipo == "SALIDA" and tanque_lleno and vehiculo_id:

            anterior = Kardex.query.filter(
                Kardex.vehiculo_id == vehiculo_id,
                Kardex.tanque_lleno == True,
                Kardex.id != nuevo.id
            ).order_by(Kardex.fecha.desc()).first()

            if anterior:

                h_ini = anterior.horometro_final or 0
                h_fin = h_final or 0

                recorrido_total = h_fin - h_ini

                consumo_total = db.session.query(func.sum(Kardex.cantidad)).filter(
                    Kardex.vehiculo_id == vehiculo_id,
                    Kardex.tipo == "SALIDA",
                    Kardex.fecha > anterior.fecha,
                    Kardex.fecha <= nuevo.fecha
                ).scalar() or 0

                if consumo_total > 0 and recorrido_total > 0:
                    
                    rendimiento = consumo_total / recorrido_total

                    vehiculo = Vehiculo.query.get(vehiculo_id)
                    estado = "NORMAL"

                    if vehiculo and vehiculo.rendimiento_promedio:
                        prom = vehiculo.rendimiento_promedio

                        if rendimiento > prom * 1.2:
                            estado = "BAJO"   # 🔴 consume mucho (malo)
                        elif rendimiento < prom * 0.8:
                            estado = "ALTO"   # 🟢 consume poco (bueno)

                        if estado == "BAJO":
                            alerta = Alerta(
                                tipo="RENDIMIENTO_BAJO",
                                mensaje=f"Vehículo {vehiculo_id} bajo rendimiento",
                                vehiculo_id=vehiculo_id
                            )
                            db.session.add(alerta)

                    nuevo_rend = Rendimiento(
                        vehiculo_id=vehiculo_id,
                        consumo_total=consumo_total,
                        recorrido_total=recorrido_total,
                        rendimiento_calculado=rendimiento,
                        estado=estado,
                        tipo_control="TANQUE_LLENO",
                        observacion="Control tanque lleno",
                        horometro_abastecimiento_inicial=h_ini,
                        horometro_abastecimiento_final=h_fin
                    )

                    db.session.add(nuevo_rend)

                    

        db.session.commit()

        flash("✅ Movimiento registrado", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", "danger")

    return redirect(url_for("kardex_list"))

@app.route("/kardex/ultimo_horometro/<int:vehiculo_id>")
@login_required
def ultimo_horometro(vehiculo_id):

    ultimo = Kardex.query.filter_by(vehiculo_id=vehiculo_id)\
        .order_by(Kardex.fecha.desc()).first()

    return {
        "horometro_final": ultimo.horometro_final if ultimo else 0
    }

# =========================
# RENDIMIENTOS DASH
# =========================
@app.route("/rendimientos")
@login_required
@permission_required("rendimientos", "ver")
def rendimiento_list():

    from sqlalchemy import func

    # =========================
    # KPIs GENERALES
    # =========================
    total = db.session.query(func.count(Rendimiento.id)).scalar() or 0

    promedio = db.session.query(
        func.avg(Rendimiento.rendimiento_calculado)
    ).scalar() or 0

    total_consumo = db.session.query(
        func.sum(Rendimiento.consumo_total)
    ).scalar() or 0

    total_recorrido = db.session.query(
        func.sum(Rendimiento.recorrido_total)
    ).scalar() or 0

    bajos = db.session.query(func.count(Rendimiento.id))\
        .filter(Rendimiento.estado == "BAJO").scalar() or 0

    porcentaje_bajo = (bajos / total * 100) if total > 0 else 0

    ultimo = Rendimiento.query.order_by(Rendimiento.fecha.desc()).first()

    tanque_lleno = db.session.query(func.count(Rendimiento.id))\
        .filter(Rendimiento.tipo_control == "TANQUE_LLENO").scalar()

    # =========================
    # AGRUPACIÓN POR VEHÍCULO
    # =========================
    por_vehiculo = db.session.query(
        Vehiculo.nombre,
        func.avg(Rendimiento.rendimiento_calculado),
        func.count(Rendimiento.id)
    ).join(Vehiculo)\
     .group_by(Vehiculo.nombre).all()

    # =========================
    # AGRUPACIÓN POR PROYECTO
    # =========================
    por_proyecto = db.session.query(
        Proyecto.nombre,
        func.avg(Rendimiento.rendimiento_calculado)
    ).join(Vehiculo, Vehiculo.proyecto_id == Proyecto.id)\
     .join(Rendimiento, Rendimiento.vehiculo_id == Vehiculo.id)\
     .group_by(Proyecto.nombre).all()

    return render_template(
        "rendimientos.html",
        lista=Rendimiento.query.order_by(Rendimiento.fecha.desc()).all(),

        promedio=round(promedio, 2),
        total_consumo=round(total_consumo, 2),
        total_recorrido=round(total_recorrido, 2),
        porcentaje_bajo=round(porcentaje_bajo, 1),
        ultimo=ultimo.rendimiento_calculado if ultimo else 0,
        tanque_lleno=tanque_lleno,

        por_vehiculo=por_vehiculo,
        por_proyecto=por_proyecto
    )



@app.route("/rendimientos/calcular/<int:vehiculo_id>", methods=["POST"])
@login_required
@permission_required("rendimientos", "crear")
def calcular_rendimiento(vehiculo_id):

    try:
        registros = Kardex.query.filter_by(
            vehiculo_id=vehiculo_id,
            tipo="SALIDA"
        ).order_by(Kardex.fecha.desc()).limit(2).all()

        if len(registros) < 2:
            flash("No hay suficientes datos", "warning")
            return redirect(url_for("rendimiento_list"))

        actual, anterior = registros

        recorrido = (actual.horometro_final or 0) - (anterior.horometro_final or 0)
        consumo = actual.cantidad

        if consumo == 0:
            flash("Consumo inválido", "danger")
            return redirect(url_for("rendimiento_list"))

        rendimiento = recorrido / consumo

        vehiculo = Vehiculo.query.get(vehiculo_id)

        if rendimiento < vehiculo.rendimiento_promedio * 0.8:
            estado = "BAJO"
        elif rendimiento > vehiculo.rendimiento_promedio * 1.2:
            estado = "ALTO"
        else:
            estado = "NORMAL"

        nuevo = Rendimiento(
            vehiculo_id=vehiculo_id,
            consumo=consumo,
            recorrido=recorrido,
            rendimiento_calculado=rendimiento,
            estado=estado
        )

        db.session.add(nuevo)
        db.session.commit()

        flash(f"✅ Rendimiento calculado ({estado})", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", "danger")

    return redirect(url_for("rendimiento_list"))


@app.route("/cargas", methods=["POST"])
@permission_required("registrar","crear")
def registrar_carga():
    data = request.json

    nueva = Kardex(
        tipo="SALIDA",
        fecha=datetime.utcnow(),
        cantidad=data["cantidad"],
        tanque_id=data["tanque_id"],
        vehiculo_id=data["vehiculo_id"],
        usuario_id=current_user.id,
        horometro=data.get("horometro"),
        kilometraje=data.get("kilometraje")
    )

    db.session.add(nueva)

    # actualizar stock
    tanque = Tanque.query.get(data["tanque_id"])
    tanque.stock_actual -= data["cantidad"]

    db.session.commit()

    return {"msg": "Carga registrada"}



#====================================================================================
# Reportes
# ===================================================================================

@app.route("/reportes/rendimiento")
@login_required
@permission_required("rendimientos", "ver")
def reporte_rendimiento():

    vehiculos = Vehiculo.query.all()

    return render_template(
        "reporte_rendimientos.html",
        vehiculos=vehiculos
    )

@app.route("/reportes/rendimientos/excel")
@login_required
@permission_required("rendimientos", "ver")
def reporte_rendimientos_excel():

    tipo = request.args.get("tipo")  # semanal, mensual, anual
    fecha_str = request.args.get("fecha")

    fecha_base = datetime.strptime(fecha_str, "%Y-%m-%d")

    # =========================
    # RANGO DE FECHAS
    # =========================
    if tipo == "semanal":
        inicio = fecha_base - timedelta(days=fecha_base.weekday())
        fin = inicio + timedelta(days=6)

    elif tipo == "mensual":
        inicio = fecha_base.replace(day=1)
        if fecha_base.month == 12:
            fin = fecha_base.replace(year=fecha_base.year+1, month=1, day=1) - timedelta(days=1)
        else:
            fin = fecha_base.replace(month=fecha_base.month+1, day=1) - timedelta(days=1)

    elif tipo == "anual":
        inicio = fecha_base.replace(month=1, day=1)
        fin = fecha_base.replace(month=12, day=31)

    else:
        return "Tipo inválido", 400

    # =========================
    # DATA BASE
    # =========================
    vehiculos = Vehiculo.query.filter_by(activo=True).all()

    dias = []
    current = inicio
    while current <= fin:
        dias.append(current)
        current += timedelta(days=1)

    # =========================
    # CREAR EXCEL
    # =========================
    wb = Workbook()
    ws = wb.active
    ws.title = "Reporte"

    # HEADER
    ws["A1"] = "REPORTE DE CONSUMO DE COMBUSTIBLE"
    ws["A2"] = f"Periodo: {inicio.date()} - {fin.date()}"

    # ENCABEZADOS
    ws.cell(row=4, column=1, value="ITEM")
    ws.cell(row=4, column=2, value="EQUIPO")

    col = 3
    for d in dias:
        ws.cell(row=4, column=col, value=d.strftime("%d-%b"))
        col += 1

    ws.cell(row=4, column=col, value="TOTAL")

    # =========================
    # DATA POR VEHICULO
    # =========================
    row = 5

    for i, v in enumerate(vehiculos, start=1):

        ws.cell(row=row, column=1, value=i)
        ws.cell(row=row, column=2, value=v.nombre)

        total = 0
        col = 3

        for d in dias:

            consumo = db.session.query(func.sum(Kardex.cantidad)).filter(
                Kardex.vehiculo_id == v.id,
                Kardex.tipo == "SALIDA",
                func.date(Kardex.fecha) == d.date()
            ).scalar() or 0

            ws.cell(row=row, column=col, value=round(consumo, 2))
            total += consumo
            col += 1

        ws.cell(row=row, column=col, value=round(total, 2))

        row += 1


    fill_yellow = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")

    ws.cell(row=4, column=col).fill = fill_yellow
    
    #Congelar encabezado
    ws.freeze_panes = "C5"


    for col in ws.columns:
        max_length = 0
        col_letter = col[0].column_letter
        for cell in col:
            if cell.value:
                max_length = max(max_length, len(str(cell.value)))
        ws.column_dimensions[col_letter].width = max_length + 2

    vehiculos = Vehiculo.query.filter_by(
        proyecto_id=current_user.proyecto_id
    ).all()

    # =========================
    # EXPORTAR
    # =========================
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name=f"reporte_{tipo}.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

#==================================================================
# DASHBOARD - 
#==================================================================
@app.route("/dashboard")
@login_required
def dashboard():

    return render_template(
        "dashboard.html"
    )



if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8007, debug=True)