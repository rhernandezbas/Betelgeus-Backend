"""Views"""

import threading
from flask import jsonify, current_app
from app.routes import blueprint
from app.routes.thread_functions import thread_process_webhooks, thread_create_tickets, thread_assign_unassigned_tickets, thread_alert_overdue_tickets, thread_end_of_shift_notifications, thread_auto_unassign_after_shift
from app.utils.logger import get_logger

logger = get_logger(__name__)


@blueprint.route("/", methods=["GET"])
def health_check():
    """Health check endpoint para Docker y monitoreo"""
    logger.info("🏥 Health check endpoint llamado")
    return jsonify({
        "status": "healthy",
        "service": "splynx-tickets",
        "message": "Application is running"
    }), 200


@blueprint.route("/api/tickets/create", methods=["POST"])
def create_tickets():
    """"""
    app = current_app._get_current_object()  # Obtiene el objeto real de la aplicación
    hilo = threading.Thread(target=thread_create_tickets, args=(app,))
    hilo.start()
    return jsonify({
        "success": True,
    }), 200


@blueprint.route("/api/tickets/process_webhooks", methods=["POST"])
def process_webhooks():
    """Procesa webhooks pendientes y crea tickets en Splynx"""
    try:
        app = current_app._get_current_object()
        hilo = threading.Thread(target=thread_process_webhooks, args=(app,))
        hilo.start()
        return jsonify({
            "success": True,
            "message": "Procesamiento de webhooks iniciado"
        }), 200
    except Exception as e:
        logger.error(f"Error en process_webhooks: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@blueprint.route("/api/tickets/assign_unassigned", methods=["POST"])
def assign_unassigned():
    """Asigna tickets no asignados del grupo de Soporte Técnico usando round-robin"""
    try:
        hilo = threading.Thread(target=thread_assign_unassigned_tickets, args=(current_app._get_current_object(),))
        hilo.start()
        return jsonify({
            "success": True,
            "message": "Asignación de tickets no asignados iniciada"
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@blueprint.route("/api/tickets/alert_overdue", methods=["POST"])
def alert_overdue_tickets():
    """Alerta sobre tickets asignados que superen 45 minutos sin respuesta"""
    try:
        hilo = threading.Thread(target=thread_alert_overdue_tickets, args=(current_app._get_current_object(),))
        hilo.start()
        return jsonify({
            "success": True,
            "message": "Verificación de tickets vencidos iniciada"
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@blueprint.route("/api/tickets/end_of_shift_notifications", methods=["POST"])
def end_of_shift_notifications():
    """Envía notificaciones de resumen 1 hora antes del fin de turno"""
    try:
        hilo = threading.Thread(target=thread_end_of_shift_notifications, args=(current_app._get_current_object(),))
        hilo.start()
        return jsonify({
            "success": True,
            "message": "Verificación de notificaciones de fin de turno iniciada"
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@blueprint.route("/api/system/pause", methods=["POST"])
def pause_system():
    """Pausa el sistema - detiene asignación automática y procesos"""
    try:
        from flask import request
        from app.utils.system_control import SystemControl
        
        data = request.get_json() or {}
        reason = data.get("reason", "Pausa manual")
        paused_by = data.get("paused_by", "manual")
        
        state = SystemControl.pause(reason=reason, paused_by=paused_by)
        
        return jsonify({
            "success": True,
            "message": "Sistema pausado exitosamente",
            "state": state
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@blueprint.route("/api/system/resume", methods=["POST"])
def resume_system():
    """Reanuda el sistema - reactiva asignación automática y procesos"""
    try:
        from flask import request
        from app.utils.system_control import SystemControl
        
        data = request.get_json() or {}
        resumed_by = data.get("resumed_by", "manual")
        
        state = SystemControl.resume(resumed_by=resumed_by)
        
        return jsonify({
            "success": True,
            "message": "Sistema reanudado exitosamente",
            "state": state
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@blueprint.route("/api/system/status", methods=["GET"])
def system_status():
    """Obtiene el estado actual del sistema"""
    try:
        from app.utils.system_control import SystemControl
        
        status = SystemControl.get_status()
        
        return jsonify({
            "success": True,
            "status": status
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@blueprint.route("/api/tickets/auto_unassign_after_shift", methods=["POST"])
def auto_unassign_after_shift():
    """Desasigna tickets automáticamente 1 hora después del fin de turno"""
    try:
        from app.utils.config_helper import ConfigHelper
        if not ConfigHelper.is_auto_unassign_enabled():
            return jsonify({
                "success": True,
                "message": "Desasignación automática deshabilitada (AUTO_UNASSIGN_AFTER_SHIFT_ENABLED=false)",
                "skipped": True
            }), 200

        hilo = threading.Thread(target=thread_auto_unassign_after_shift, args=(current_app._get_current_object(),))
        hilo.start()
        return jsonify({
            "success": True,
            "message": "Verificación de desasignación automática iniciada"
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@blueprint.route("/api/tickets/sync_status", methods=["POST"])
def sync_tickets_status_endpoint():
    """Sincroniza el estado de tickets abiertos con Splynx"""
    try:
        from app.utils.sync_tickets_status import sync_tickets_status
        
        app = current_app._get_current_object()
        
        def run_sync():
            with app.app_context():
                result = sync_tickets_status()
                logger.info(f"Sincronización completada: {result}")
        
        hilo = threading.Thread(target=run_sync)
        hilo.start()
        
        return jsonify({
            "success": True,
            "message": "Sincronización de estado de tickets iniciada"
        }), 200
    except Exception as e:
        logger.error(f"Error en endpoint sync_status: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@blueprint.route("/api/tickets/import_existing", methods=["POST"])
def import_existing_tickets():
    """Importa tickets existentes del grupo 4 de Splynx a la BD"""
    try:
        from app.utils.import_existing_tickets import import_existing_tickets_from_splynx
        
        app = current_app._get_current_object()
        
        def run_import():
            with app.app_context():
                result = import_existing_tickets_from_splynx()
                logger.info(f"Importación completada: {result}")
        
        hilo = threading.Thread(target=run_import)
        hilo.start()
        
        return jsonify({
            "success": True,
            "message": "Importación de tickets existentes iniciada"
        }), 200
    except Exception as e:
        logger.error(f"Error en endpoint import_existing: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
