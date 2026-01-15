#!/usr/bin/env python3
"""
Script para actualizar schedule_type de 'work' a 'assignment'
"""
from app import create_app
from app.utils.config import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        # Actualizar 'work' a 'assignment'
        print("Actualizando schedule_type de 'work' a 'assignment'...")
        result = db.session.execute(text("""
            UPDATE operator_schedule 
            SET schedule_type = 'assignment' 
            WHERE schedule_type = 'work'
        """))
        db.session.commit()
        print(f"✅ {result.rowcount} registros actualizados de 'work' a 'assignment'")
        
        # Verificar los tipos actuales
        print("\nVerificando tipos de horarios en la base de datos...")
        result = db.session.execute(text("""
            SELECT schedule_type, COUNT(*) as count 
            FROM operator_schedule 
            GROUP BY schedule_type
        """))
        for row in result:
            print(f"  - {row[0]}: {row[1]} registros")
        
        print("\n🎉 Migración completada exitosamente!")
        
    except Exception as e:
        print(f"❌ Error en migración: {e}")
        db.session.rollback()
