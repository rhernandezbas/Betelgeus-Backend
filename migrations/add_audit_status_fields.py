"""
Migration script to add audit_status, audit_reviewed_at, audit_reviewed_by columns
"""

import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

def add_audit_status_fields():
    """Add audit status tracking fields to tickets_detection table"""
    
    connection = pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'splynx_tickets'),
        port=int(os.getenv('DB_PORT', 3306))
    )
    
    try:
        with connection.cursor() as cursor:
            # Agregar columna audit_status
            print("Agregando columna audit_status...")
            try:
                cursor.execute("""
                    ALTER TABLE tickets_detection 
                    ADD COLUMN audit_status VARCHAR(20) DEFAULT 'pending' 
                    COMMENT 'Estado de auditoría: pending/approved/rejected'
                    AFTER audit_requested_by
                """)
                print("✅ Columna audit_status agregada")
            except pymysql.err.OperationalError as e:
                if "Duplicate column name" in str(e):
                    print("⚠️  Columna audit_status ya existe")
                else:
                    raise
            
            # Agregar columna audit_reviewed_at
            print("Agregando columna audit_reviewed_at...")
            try:
                cursor.execute("""
                    ALTER TABLE tickets_detection 
                    ADD COLUMN audit_reviewed_at DATETIME NULL 
                    COMMENT 'Fecha de revisión por admin'
                    AFTER audit_status
                """)
                print("✅ Columna audit_reviewed_at agregada")
            except pymysql.err.OperationalError as e:
                if "Duplicate column name" in str(e):
                    print("⚠️  Columna audit_reviewed_at ya existe")
                else:
                    raise
            
            # Agregar columna audit_reviewed_by
            print("Agregando columna audit_reviewed_by...")
            try:
                cursor.execute("""
                    ALTER TABLE tickets_detection 
                    ADD COLUMN audit_reviewed_by INT NULL 
                    COMMENT 'Admin user ID que revisó'
                    AFTER audit_reviewed_at
                """)
                print("✅ Columna audit_reviewed_by agregada")
            except pymysql.err.OperationalError as e:
                if "Duplicate column name" in str(e):
                    print("⚠️  Columna audit_reviewed_by ya existe")
                else:
                    raise
            
            connection.commit()
            print("✅ Todas las columnas agregadas exitosamente")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        connection.rollback()
        raise
    finally:
        connection.close()

if __name__ == "__main__":
    print("🔧 Iniciando migración: agregar campos de estado de auditoría")
    add_audit_status_fields()
    print("✅ Migración completada")
