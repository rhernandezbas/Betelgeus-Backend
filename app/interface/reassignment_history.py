"""
Interface para el historial de reasignaciones de tickets
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

from app.utils.config import db
from app.models.models import TicketReassignmentHistory
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ReassignmentHistoryInterface:
    """Interface para gestionar el historial de reasignaciones"""
    
    @staticmethod
    def create(data: Dict[str, Any]) -> Optional[TicketReassignmentHistory]:
        """
        Crea un registro de reasignación en el historial
        
        Args:
            data: Diccionario con los datos de la reasignación
                - ticket_id: ID del ticket
                - from_operator_id: ID del operador anterior (opcional)
                - from_operator_name: Nombre del operador anterior (opcional)
                - to_operator_id: ID del nuevo operador (opcional)
                - to_operator_name: Nombre del nuevo operador (opcional)
                - reason: Razón de la reasignación
                - reassignment_type: Tipo de reasignación
                - created_by: Usuario que realizó la acción
        
        Returns:
            Registro creado o None si hay error
        """
        try:
            history = TicketReassignmentHistory(
                ticket_id=data.get('ticket_id'),
                from_operator_id=data.get('from_operator_id'),
                from_operator_name=data.get('from_operator_name'),
                to_operator_id=data.get('to_operator_id'),
                to_operator_name=data.get('to_operator_name'),
                reason=data.get('reason', ''),
                reassignment_type=data.get('reassignment_type', 'manual'),
                created_by=data.get('created_by', 'system')
            )
            
            db.session.add(history)
            db.session.commit()
            
            logger.info(f"✅ Historial de reasignación creado: Ticket {data.get('ticket_id')} de {data.get('from_operator_name', 'Sin asignar')} a {data.get('to_operator_name', 'Sin asignar')}")
            return history
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"❌ Error creando historial de reasignación: {str(e)}")
            return None
    
    @staticmethod
    def get_by_ticket(ticket_id: str) -> List[TicketReassignmentHistory]:
        """
        Obtiene el historial de reasignaciones de un ticket específico
        
        Args:
            ticket_id: ID del ticket
            
        Returns:
            Lista de registros de historial
        """
        try:
            return TicketReassignmentHistory.query.filter_by(
                ticket_id=ticket_id
            ).order_by(TicketReassignmentHistory.created_at.desc()).all()
        except SQLAlchemyError as e:
            logger.error(f"❌ Error obteniendo historial del ticket {ticket_id}: {str(e)}")
            return []
    
    @staticmethod
    def get_recent(limit: int = 100) -> List[TicketReassignmentHistory]:
        """
        Obtiene los registros más recientes del historial
        
        Args:
            limit: Número máximo de registros a retornar
            
        Returns:
            Lista de registros de historial
        """
        try:
            return TicketReassignmentHistory.query.order_by(
                TicketReassignmentHistory.created_at.desc()
            ).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"❌ Error obteniendo historial reciente: {str(e)}")
            return []
    
    @staticmethod
    def get_by_operator(operator_id: int, limit: int = 50) -> List[TicketReassignmentHistory]:
        """
        Obtiene el historial de reasignaciones relacionadas con un operador
        
        Args:
            operator_id: ID del operador
            limit: Número máximo de registros
            
        Returns:
            Lista de registros de historial
        """
        try:
            return TicketReassignmentHistory.query.filter(
                (TicketReassignmentHistory.from_operator_id == operator_id) |
                (TicketReassignmentHistory.to_operator_id == operator_id)
            ).order_by(TicketReassignmentHistory.created_at.desc()).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"❌ Error obteniendo historial del operador {operator_id}: {str(e)}")
            return []
    
    @staticmethod
    def to_dict(history: TicketReassignmentHistory) -> Dict[str, Any]:
        """
        Convierte un registro de historial a diccionario
        
        Args:
            history: Registro de historial
            
        Returns:
            Diccionario con los datos
        """
        return {
            'id': history.id,
            'ticket_id': history.ticket_id,
            'from_operator_id': history.from_operator_id,
            'from_operator_name': history.from_operator_name or 'Sin asignar',
            'to_operator_id': history.to_operator_id,
            'to_operator_name': history.to_operator_name or 'Sin asignar',
            'reason': history.reason,
            'reassignment_type': history.reassignment_type,
            'created_at': history.created_at.isoformat() if history.created_at else None,
            'created_by': history.created_by
        }
