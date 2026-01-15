"""
Script de migración para actualizar assigned_to de todos los tickets
usando el campo correcto 'assign_to' de la API de Splynx
"""

from app.utils.config import db
from app.models.models import IncidentsDetection
from app.services.splynx_services import SplynxServices
import logging

logger = logging.getLogger(__name__)

def migrate_assigned_to():
    """
    Actualiza el campo assigned_to de todos los tickets abiertos
    consultando el campo correcto 'assign_to' en Splynx
    """
    try:
        splynx = SplynxServices()
        
        # Obtener todos los tickets abiertos
        open_tickets = IncidentsDetection.query.filter(
            IncidentsDetection.is_closed == False,
            IncidentsDetection.Ticket_ID.isnot(None)
        ).all()
        
        logger.info(f"🔄 Migrando assigned_to para {len(open_tickets)} tickets abiertos...")
        
        updated_count = 0
        error_count = 0
        
        for ticket in open_tickets:
            try:
                ticket_id = ticket.Ticket_ID
                if not ticket_id:
                    continue
                
                # Consultar ticket en Splynx
                splynx_ticket = splynx.get_ticket_data_status(ticket_id)
                
                if splynx_ticket:
                    # Usar el campo correcto 'assign_to'
                    assign_to = splynx_ticket.get('assign_to', None) or splynx_ticket.get('assigned_to', None)
                    
                    if assign_to:
                        new_assigned_to = int(assign_to)
                    else:
                        new_assigned_to = None
                    
                    # Actualizar si cambió
                    if ticket.assigned_to != new_assigned_to:
                        old_value = ticket.assigned_to
                        ticket.assigned_to = new_assigned_to
                        updated_count += 1
                        logger.info(f"✅ Ticket {ticket_id}: {old_value} → {new_assigned_to}")
                        
            except Exception as e:
                error_count += 1
                logger.error(f"❌ Error migrando ticket {ticket.Ticket_ID}: {e}")
                continue
        
        db.session.commit()
        logger.info(f"✅ Migración completada: {updated_count} tickets actualizados, {error_count} errores")
        
        return {
            'success': True,
            'total_checked': len(open_tickets),
            'updated_count': updated_count,
            'error_count': error_count
        }
        
    except Exception as e:
        logger.error(f"❌ Error en migración: {e}")
        db.session.rollback()
        return {
            'success': False,
            'error': str(e)
        }
