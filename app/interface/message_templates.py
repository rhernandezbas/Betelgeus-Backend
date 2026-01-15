"""
Interface para gestionar plantillas de mensajes de WhatsApp
"""

from typing import List, Optional, Dict, Any
from app.models.models import MessageTemplate
from app.extensions import db
from app.utils.logger import get_logger

logger = get_logger(__name__)


class MessageTemplateInterface:
    """Interfaz para operaciones CRUD de plantillas de mensajes"""
    
    @staticmethod
    def get_all_templates() -> List[MessageTemplate]:
        """Obtener todas las plantillas de mensajes"""
        try:
            return MessageTemplate.query.all()
        except Exception as e:
            logger.error(f"Error obteniendo plantillas: {e}")
            return []
    
    @staticmethod
    def get_template_by_key(template_key: str) -> Optional[MessageTemplate]:
        """Obtener plantilla por su clave única"""
        try:
            return MessageTemplate.query.filter_by(template_key=template_key).first()
        except Exception as e:
            logger.error(f"Error obteniendo plantilla {template_key}: {e}")
            return None
    
    @staticmethod
    def get_template_by_id(template_id: int) -> Optional[MessageTemplate]:
        """Obtener plantilla por ID"""
        try:
            return MessageTemplate.query.get(template_id)
        except Exception as e:
            logger.error(f"Error obteniendo plantilla ID {template_id}: {e}")
            return None
    
    @staticmethod
    def create_template(data: Dict[str, Any]) -> Optional[MessageTemplate]:
        """Crear nueva plantilla de mensaje"""
        try:
            template = MessageTemplate(
                template_key=data['template_key'],
                template_name=data['template_name'],
                template_content=data['template_content'],
                description=data.get('description'),
                variables=data.get('variables', []),
                is_active=data.get('is_active', True),
                updated_by=data.get('updated_by', 'system')
            )
            db.session.add(template)
            db.session.commit()
            logger.info(f"✅ Plantilla creada: {template.template_key}")
            return template
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creando plantilla: {e}")
            return None
    
    @staticmethod
    def update_template(template_id: int, data: Dict[str, Any]) -> Optional[MessageTemplate]:
        """Actualizar plantilla existente"""
        try:
            template = MessageTemplate.query.get(template_id)
            if not template:
                return None
            
            if 'template_name' in data:
                template.template_name = data['template_name']
            if 'template_content' in data:
                template.template_content = data['template_content']
            if 'description' in data:
                template.description = data['description']
            if 'variables' in data:
                template.variables = data['variables']
            if 'is_active' in data:
                template.is_active = data['is_active']
            if 'updated_by' in data:
                template.updated_by = data['updated_by']
            
            db.session.commit()
            logger.info(f"✅ Plantilla actualizada: {template.template_key}")
            return template
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error actualizando plantilla: {e}")
            return None
    
    @staticmethod
    def delete_template(template_id: int) -> bool:
        """Eliminar plantilla"""
        try:
            template = MessageTemplate.query.get(template_id)
            if not template:
                return False
            
            db.session.delete(template)
            db.session.commit()
            logger.info(f"✅ Plantilla eliminada: {template.template_key}")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error eliminando plantilla: {e}")
            return False
    
    @staticmethod
    def get_active_templates() -> List[MessageTemplate]:
        """Obtener solo plantillas activas"""
        try:
            return MessageTemplate.query.filter_by(is_active=True).all()
        except Exception as e:
            logger.error(f"Error obteniendo plantillas activas: {e}")
            return []
    
    @staticmethod
    def render_template(template_key: str, variables: Dict[str, Any]) -> Optional[str]:
        """
        Renderizar plantilla con variables
        
        Args:
            template_key: Clave de la plantilla
            variables: Diccionario con valores de variables
            
        Returns:
            str: Mensaje renderizado o None si error
        """
        try:
            template = MessageTemplateInterface.get_template_by_key(template_key)
            if not template or not template.is_active:
                return None
            
            message = template.template_content
            
            # Reemplazar variables en el formato {variable_name}
            for key, value in variables.items():
                placeholder = f"{{{key}}}"
                message = message.replace(placeholder, str(value))
            
            return message
        except Exception as e:
            logger.error(f"Error renderizando plantilla {template_key}: {e}")
            return None
