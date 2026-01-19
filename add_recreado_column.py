#!/usr/bin/env python3
"""Script para agregar la columna 'recreado' a la tabla tickets_detection"""

from app import create_app
from app.utils.config import db
from sqlalchemy import text

def add_recreado_column():
    app = create_app()
    with app.app_context():
        try:
            # Verificar si la columna ya existe
            result = db.session.execute(text(
                "SELECT COUNT(*) FROM information_schema.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() "
                "AND TABLE_NAME = 'tickets_detection' "
                "AND COLUMN_NAME = 'recreado'"
            ))
            exists = result.scalar() > 0
            
            if exists:
                print("✅ La columna 'recreado' ya existe en la tabla tickets_detection")
                return
            
            # Agregar la columna
            db.session.execute(text(
                "ALTER TABLE tickets_detection "
                "ADD COLUMN recreado INT DEFAULT 0 COMMENT 'Contador de veces que se ha recreado el ticket'"
            ))
            db.session.commit()
            print("✅ Columna 'recreado' agregada exitosamente a la tabla tickets_detection")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al agregar columna 'recreado': {e}")
            raise

if __name__ == '__main__':
    add_recreado_column()
