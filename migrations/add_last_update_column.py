"""
Migration script to add last_update column to tickets_detection table
"""

import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

def add_last_update_column():
    """Add last_update column to tickets_detection table"""
    
    connection = pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'splynx_tickets'),
        port=int(os.getenv('DB_PORT', 3306))
    )
    
    try:
        with connection.cursor() as cursor:
            # Agregar columna last_update
            print("Agregando columna last_update...")
            cursor.execute("""
                ALTER TABLE tickets_detection 
                ADD COLUMN last_update DATETIME NULL 
                COMMENT 'Última actualización desde Splynx (updated_at)'
                AFTER is_closed
            """)
            connection.commit()
            print("✅ Columna last_update agregada exitosamente")
            
    except pymysql.err.OperationalError as e:
        if "Duplicate column name" in str(e):
            print("⚠️  Columna last_update ya existe, omitiendo...")
        else:
            print(f"❌ Error: {e}")
            connection.rollback()
            raise
    finally:
        connection.close()

if __name__ == "__main__":
    print("🔧 Iniciando migración: agregar columna last_update")
    add_last_update_column()
    print("✅ Migración completada")
