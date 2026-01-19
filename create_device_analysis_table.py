#!/usr/bin/env python3
"""Script para crear la tabla device_analysis en la base de datos"""

from app import create_app
from app.utils.config import db
from app.models.models import DeviceAnalysis

def create_table():
    app = create_app()
    with app.app_context():
        # Crear solo la tabla device_analysis
        DeviceAnalysis.__table__.create(db.engine, checkfirst=True)
        print("✅ Tabla device_analysis creada exitosamente")

if __name__ == '__main__':
    create_table()
