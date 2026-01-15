"""
Agregar columna is_closed a tickets_detection y ticket_response_metrics
"""

import sys
sys.path.insert(0, '/app')
from app import create_app
from app.utils.config import db
from sqlalchemy import text

app = create_app()

def add_is_closed_columns():
    with app.app_context():
        print('📝 Agregando columnas is_closed a las tablas...\n')
        
        try:
            # 1. Agregar is_closed a tickets_detection
            print('1️⃣ Tabla: tickets_detection')
            result = db.session.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'tickets_detection' 
                AND COLUMN_NAME = 'is_closed'
            """))
            exists = result.scalar() > 0
            
            if exists:
                print('   ⚠️  La columna is_closed ya existe en tickets_detection')
            else:
                db.session.execute(text("""
                    ALTER TABLE tickets_detection 
                    ADD COLUMN is_closed TINYINT(1) DEFAULT 0
                """))
                db.session.commit()
                print('   ✅ Columna is_closed agregada a tickets_detection')
            
            # Actualizar is_closed basado en closed_at existente
            print('   🔄 Actualizando is_closed basado en closed_at...')
            result = db.session.execute(text("""
                UPDATE tickets_detection 
                SET is_closed = 1 
                WHERE closed_at IS NOT NULL
            """))
            db.session.commit()
            print(f'   ✅ {result.rowcount} registros actualizados con is_closed=1\n')
            
            # 2. Agregar is_closed a ticket_response_metrics
            print('2️⃣ Tabla: ticket_response_metrics')
            result = db.session.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'ticket_response_metrics' 
                AND COLUMN_NAME = 'is_closed'
            """))
            exists = result.scalar() > 0
            
            if exists:
                print('   ⚠️  La columna is_closed ya existe en ticket_response_metrics')
            else:
                db.session.execute(text("""
                    ALTER TABLE ticket_response_metrics 
                    ADD COLUMN is_closed TINYINT(1) DEFAULT 0
                """))
                db.session.commit()
                print('   ✅ Columna is_closed agregada a ticket_response_metrics')
            
            # Actualizar is_closed basado en resolved_at existente
            print('   🔄 Actualizando is_closed basado en resolved_at...')
            result = db.session.execute(text("""
                UPDATE ticket_response_metrics 
                SET is_closed = 1 
                WHERE resolved_at IS NOT NULL
            """))
            db.session.commit()
            print(f'   ✅ {result.rowcount} registros actualizados con is_closed=1\n')
            
            # 3. Verificar sincronización entre tablas
            print('3️⃣ Verificando sincronización entre tablas...')
            result = db.session.execute(text("""
                SELECT 
                    td.Ticket_ID,
                    td.is_closed as td_is_closed,
                    trm.is_closed as trm_is_closed
                FROM tickets_detection td
                LEFT JOIN ticket_response_metrics trm ON td.Ticket_ID = trm.ticket_id
                WHERE td.is_closed != COALESCE(trm.is_closed, 0)
                LIMIT 5
            """))
            
            inconsistencias = result.fetchall()
            if inconsistencias:
                print(f'   ⚠️  {len(inconsistencias)} inconsistencias encontradas entre tablas')
                for inc in inconsistencias:
                    print(f'      Ticket {inc[0]}: tickets_detection={inc[1]}, ticket_response_metrics={inc[2]}')
            else:
                print('   ✅ Tablas sincronizadas correctamente')
            
            print('\n✅ Migración completada exitosamente')
            
        except Exception as e:
            print(f'❌ Error: {e}')
            db.session.rollback()

if __name__ == '__main__':
    add_is_closed_columns()
