#!/usr/bin/env python3
"""
Script para aplicar migración de schedule_type
"""
from app import create_app
from app.utils.config import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        # Agregar columna schedule_type
        print("Agregando columna schedule_type...")
        db.session.execute(text("""
            ALTER TABLE operator_schedule 
            ADD COLUMN schedule_type VARCHAR(20) NOT NULL DEFAULT 'alert' AFTER end_time
        """))
        db.session.commit()
        print("✅ Columna schedule_type agregada exitosamente!")
    except Exception as e:
        if 'Duplicate column name' in str(e):
            print("✅ La columna schedule_type ya existe")
        else:
            print(f"❌ Error al agregar columna: {e}")
        db.session.rollback()

    try:
        # Actualizar registros existentes
        print("Actualizando registros existentes...")
        result = db.session.execute(text("""
            UPDATE operator_schedule 
            SET schedule_type = 'alert' 
            WHERE schedule_type IS NULL OR schedule_type = ''
        """))
        db.session.commit()
        print(f"✅ {result.rowcount} registros actualizados exitosamente!")
    except Exception as e:
        print(f"❌ Error al actualizar registros: {e}")
        db.session.rollback()

    try:
        # Crear índice
        print("Creando índice idx_schedule_type...")
        db.session.execute(text("""
            CREATE INDEX idx_schedule_type 
            ON operator_schedule(person_id, schedule_type)
        """))
        db.session.commit()
        print("✅ Índice idx_schedule_type creado exitosamente!")
    except Exception as e:
        if 'Duplicate key name' in str(e):
            print("✅ El índice idx_schedule_type ya existe")
        else:
            print(f"❌ Error al crear índice: {e}")
        db.session.rollback()

    print("\n🎉 Migración completada exitosamente!")
