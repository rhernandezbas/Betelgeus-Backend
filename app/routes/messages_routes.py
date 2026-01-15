"""
Messages API Routes - Gestión de plantillas de mensajes de WhatsApp
"""

from flask import Blueprint, jsonify, request
from app.interface.message_templates import MessageTemplateInterface
from app.interface.interfaces import AuditLogInterface
from app.utils.logger import get_logger

logger = get_logger(__name__)

messages_bp = Blueprint('messages', __name__, url_prefix='/api/admin/messages')


@messages_bp.route('/templates', methods=['GET'])
def get_all_templates():
    """Obtener todas las plantillas de mensajes"""
    try:
        templates = MessageTemplateInterface.get_all_templates()
        
        return jsonify({
            'success': True,
            'templates': [{
                'id': t.id,
                'template_key': t.template_key,
                'template_name': t.template_name,
                'template_content': t.template_content,
                'description': t.description,
                'variables': t.variables,
                'is_active': t.is_active,
                'updated_at': t.updated_at.isoformat() if t.updated_at else None,
                'updated_by': t.updated_by
            } for t in templates]
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo plantillas: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@messages_bp.route('/templates/<int:template_id>', methods=['GET'])
def get_template(template_id):
    """Obtener una plantilla específica"""
    try:
        template = MessageTemplateInterface.get_template_by_id(template_id)
        
        if not template:
            return jsonify({'success': False, 'error': 'Plantilla no encontrada'}), 404
        
        return jsonify({
            'success': True,
            'template': {
                'id': template.id,
                'template_key': template.template_key,
                'template_name': template.template_name,
                'template_content': template.template_content,
                'description': template.description,
                'variables': template.variables,
                'is_active': template.is_active,
                'updated_at': template.updated_at.isoformat() if template.updated_at else None,
                'updated_by': template.updated_by
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo plantilla: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@messages_bp.route('/templates/<int:template_id>', methods=['PUT'])
def update_template(template_id):
    """Actualizar una plantilla de mensaje"""
    try:
        data = request.get_json()
        
        # Obtener plantilla actual para auditoría
        old_template = MessageTemplateInterface.get_template_by_id(template_id)
        if not old_template:
            return jsonify({'success': False, 'error': 'Plantilla no encontrada'}), 404
        
        old_value = {
            'template_content': old_template.template_content,
            'template_name': old_template.template_name,
            'is_active': old_template.is_active
        }
        
        # Actualizar plantilla
        updated_template = MessageTemplateInterface.update_template(template_id, data)
        
        if not updated_template:
            return jsonify({'success': False, 'error': 'Error actualizando plantilla'}), 500
        
        # Registrar en auditoría
        new_value = {
            'template_content': updated_template.template_content,
            'template_name': updated_template.template_name,
            'is_active': updated_template.is_active
        }
        
        AuditLogInterface.create({
            'action': 'update_message_template',
            'entity_type': 'message_template',
            'entity_id': str(template_id),
            'old_value': old_value,
            'new_value': new_value,
            'performed_by': data.get('performed_by', 'admin'),
            'ip_address': request.remote_addr,
            'notes': f"Plantilla '{updated_template.template_name}' actualizada"
        })
        
        return jsonify({
            'success': True,
            'message': 'Plantilla actualizada exitosamente',
            'template': {
                'id': updated_template.id,
                'template_key': updated_template.template_key,
                'template_name': updated_template.template_name,
                'template_content': updated_template.template_content,
                'description': updated_template.description,
                'variables': updated_template.variables,
                'is_active': updated_template.is_active
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error actualizando plantilla: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@messages_bp.route('/templates', methods=['POST'])
def create_template():
    """Crear una nueva plantilla de mensaje"""
    try:
        data = request.get_json()
        
        template = MessageTemplateInterface.create_template(data)
        
        if not template:
            return jsonify({'success': False, 'error': 'Error creando plantilla'}), 500
        
        # Registrar en auditoría
        AuditLogInterface.create({
            'action': 'create_message_template',
            'entity_type': 'message_template',
            'entity_id': str(template.id),
            'new_value': {
                'template_key': template.template_key,
                'template_name': template.template_name,
                'template_content': template.template_content
            },
            'performed_by': data.get('performed_by', 'admin'),
            'ip_address': request.remote_addr,
            'notes': f"Plantilla '{template.template_name}' creada"
        })
        
        return jsonify({
            'success': True,
            'message': 'Plantilla creada exitosamente',
            'template': {
                'id': template.id,
                'template_key': template.template_key,
                'template_name': template.template_name,
                'template_content': template.template_content
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Error creando plantilla: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@messages_bp.route('/current', methods=['GET'])
def get_current_messages():
    """Obtener los mensajes actuales hardcodeados del sistema"""
    try:
        # Mensajes actuales del sistema
        current_messages = {
            'overdue_tickets_alert': {
                'name': 'Alerta de Tickets Vencidos',
                'description': 'Mensaje enviado cuando hay tickets con más de 45 minutos sin respuesta',
                'content': """🚨 *ALERTA DE TICKETS VENCIDOS*

Hola *{operator_name}*,

Tienes *{total_tickets}* ticket(s) con más de 45 minutos sin respuesta:

{tickets_list}

⚠️ *Por favor, revisa y actualiza estos tickets lo antes posible.*""",
                'variables': ['operator_name', 'total_tickets', 'tickets_list'],
                'example': """🚨 *ALERTA DE TICKETS VENCIDOS*

Hola *Gabriel Romero*,

Tienes *2* tickets con más de 45 minutos sin respuesta:

*1. Ticket #12345*
   👤 Juan Pérez
   📝 Problema con internet
   ⏱️ 60 min

*2. Ticket #12346*
   👤 María González
   📝 Sin conexión
   ⏱️ 75 min

⚠️ *Por favor, revisa y actualiza estos tickets lo antes posible.*"""
            },
            'end_of_shift_summary': {
                'name': 'Resumen de Fin de Turno',
                'description': 'Mensaje enviado 60 minutos antes del fin de turno',
                'content': """🕐 *RESUMEN DE FIN DE TURNO*

Hola *{operator_name}*,

Tu turno termina en 60 minutos ({shift_end_time}).

📊 *Tickets pendientes: {pending_count}*

{tickets_list}

⚠️ *Por favor, intenta resolver o actualizar estos tickets antes de finalizar tu turno.*""",
                'variables': ['operator_name', 'shift_end_time', 'pending_count', 'tickets_list'],
                'example': """🕐 *RESUMEN DE FIN DE TURNO*

Hola *Gabriel Romero*,

Tu turno termina en 60 minutos (16:00).

📊 *Tickets pendientes: 3*

*1. Ticket #12345*
   👤 Juan Pérez
   📝 Problema con internet

*2. Ticket #12346*
   👤 María González
   📝 Sin conexión

⚠️ *Por favor, intenta resolver o actualizar estos tickets antes de finalizar tu turno.*"""
            },
            'ticket_assignment': {
                'name': 'Notificación de Asignación',
                'description': 'Mensaje enviado cuando se asigna un nuevo ticket',
                'content': """📋 *NUEVO TICKET ASIGNADO*

Hola *{operator_name}*,

Se te ha asignado un nuevo ticket:

*Ticket #{ticket_id}*
👤 Cliente: {customer_name}
📝 Asunto: {subject}
🕐 Creado: {created_at}

Por favor, revisa y atiende este ticket lo antes posible.""",
                'variables': ['operator_name', 'ticket_id', 'customer_name', 'subject', 'created_at'],
                'example': """📋 *NUEVO TICKET ASIGNADO*

Hola *Gabriel Romero*,

Se te ha asignado un nuevo ticket:

*Ticket #12347*
👤 Cliente: Carlos López
📝 Asunto: Consulta sobre facturación
🕐 Creado: 14/01/2026 22:00

Por favor, revisa y atiende este ticket lo antes posible."""
            }
        }
        
        return jsonify({
            'success': True,
            'messages': current_messages,
            'note': 'Estos son los mensajes actuales del sistema. Para personalizarlos, crea plantillas personalizadas.'
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo mensajes actuales: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
