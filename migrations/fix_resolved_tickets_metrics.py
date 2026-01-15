"""
Corregir inconsistencias en ticket_response_metrics:
- Marcar como resueltos los tickets que están cerrados en tickets_detection
"""

import sys
sys.path.insert(0, '/app')
from app import create_app
from app.utils.config import db
from sqlalchemy import text
from datetime import datetime

app = create_app()

def fix_resolved_tickets():
    with app.app_context():
        print('🔧 Corrigiendo inconsistencias en métricas de tickets...\n')
        
        try:
            # Encontrar tickets marcados como vencidos sin resolver, pero cerrados en BD
            result = db.session.execute(text("""
                SELECT 
                    trm.id,
                    trm.ticket_id,
                    td.closed_at
                FROM ticket_response_metrics trm
                INNER JOIN tickets_detection td ON trm.ticket_id = td.Ticket_ID
                WHERE trm.resolved_at IS NULL
                AND td.closed_at IS NOT NULL
            """))
            
            inconsistencias = result.fetchall()
            print(f'📊 Inconsistencias encontradas: {len(inconsistencias)}\n')
            
            if len(inconsistencias) == 0:
                print('✅ No hay inconsistencias que corregir')
                return
            
            # Actualizar resolved_at para estos tickets
            for inc in inconsistencias:
                metric_id = inc[0]
                ticket_id = inc[1]
                closed_at = inc[2]
                
                db.session.execute(text("""
                    UPDATE ticket_response_metrics
                    SET resolved_at = :closed_at
                    WHERE id = :metric_id
                """), {
                    'closed_at': closed_at,
                    'metric_id': metric_id
                })
                
                print(f'✅ Ticket {ticket_id} marcado como resuelto en {closed_at}')
            
            db.session.commit()
            print(f'\n✅ {len(inconsistencias)} métricas corregidas exitosamente')
            
            # Verificar resultado
            result = db.session.execute(text("""
                SELECT COUNT(*)
                FROM ticket_response_metrics trm
                INNER JOIN tickets_detection td ON trm.ticket_id = td.Ticket_ID
                WHERE trm.resolved_at IS NULL
                AND td.closed_at IS NOT NULL
            """))
            
            remaining = result.scalar()
            print(f'📊 Inconsistencias restantes: {remaining}')
            
        except Exception as e:
            print(f'❌ Error: {e}')
            db.session.rollback()

if __name__ == '__main__':
    fix_resolved_tickets()
