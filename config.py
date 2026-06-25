# 📁 ESTRUCTURA RECOMENDADA
# ├── app.py
# ├── models.py
# ├── config.py
# └── requirements.txt

# =========================
# config.py
# =========================

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'super-secret-key'

    # Corrección para Render/Heroku: postgres:// a postgresql://
    uri = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:123456@localhost:5433/App_Combustible")
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_DATABASE_URI = uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static/uploads")

    # 🔥 OPTIMIZACIÓN EXCLUSIVA PARA NEON TECH
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 4,             # Neon gratis permite pocas conexiones concurrentes. 4 es ideal.
        "max_overflow": 2,          # Permite superar el límite brevemente si hay picos.
        "pool_recycle": 280,        # Neon cierra conexiones inactivas a los 5 min (300s). Las reciclamos a los 4.6 min.
        "pool_timeout": 15,         # Tiempo máximo de espera por una conexión libre antes de dar timeout.
        "pool_pre_ping": True,      # Verifica si la conexión sigue viva antes de lanzar el query.
    }
