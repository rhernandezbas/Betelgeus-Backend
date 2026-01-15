"""
Agregar columna closed_at a tickets_detection
"""

import sys
sys.path.insert(0, '/app')
from app import create_app
from app.utils.config import db
from sqlalchemy import text

app = create_app()

def add_closed_at_column():
    with app.app_context():
        print('📝 Agregando columna closed_at a tickets_detection...')
        
        try:
            # Verificar si la columna ya existe
            result = db.session.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'tickets_detection' 
                AND COLUMN_NAME = 'closed_at'
            """))
            exists = result.scalar() > 0
            
            if exists:
                print('⚠️  La columna closed_at ya existe')
            else:
                # Agregar columna
                db.session.execute(text("""
                    ALTER TABLE tickets_detection 
                    ADD COLUMN closed_at DATETIME NULL
                """))
                db.session.commit()
                print('✅ Columna closed_at agregada exitosamente')
            
            # Actualizar tickets cerrados existentes
            print('\n🔄 Actualizando tickets cerrados existentes...')
            result = db.session.execute(text("""
                UPDATE tickets_detection 
                SET closed_at = NOW() 
                WHERE Estado IN ('closed', 'Closed', 'CLOSED', 'success', 'Success', 'SUCCESS')
                AND closed_at IS NULL
            """))
            db.session.commit()
            print(f'✅ {result.rowcount} tickets actualizados con closed_at')
            
        except Exception as e:
            print(f'❌ Error: {e}')
            db.session.rollback()

if __name__ == '__main__':
    add_closed_at_column()
