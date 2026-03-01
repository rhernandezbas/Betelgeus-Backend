"""
Hooks Routes - Endpoints para webhooks entrantes de tickets.
Recibe payloads desde Suricata y los persiste en BD.
Normaliza los nombres de campos del webhook (con espacios) a snake_case del modelo.
"""

from flask import Blueprint, request, jsonify
from app.interface.webhook_interface import HookNuevoTicketInterface, HookCierreTicketInterface
from app.utils.logger import get_logger

logger = get_logger(__name__)

hooks_bp = Blueprint('hooks', __name__, url_prefix='/api/hooks')

# Mapeo: campo del webhook (como viene de Suricata) → campo del modelo
NUEVO_TICKET_FIELD_MAP = {
    'Nombre de la empresa': 'nombre_empresa',
    'Numero de ticket': 'numero_ticket',
    'Fecha_creado': 'fecha_creado',
    'Departamento creacion del ticket': 'departamento',
    'Canal por el que entro el ticket': 'canal_entrada',
    'Motivo de contacto': 'motivo_contacto',
    'Numero de  cliente': 'numero_cliente',
    'Numero de  Whatsapp': 'numero_whatsapp',
    'Nombre y apellido del usuario': 'nombre_usuario',
}

CIERRE_TICKET_FIELD_MAP = {
    'Nombre de la empresa': 'nombre_empresa',
    'Numero de ticket': 'numero_ticket',
    'Fecha_creado': 'fecha_creado',
    'Departamento creacion del ticket': 'departamento',
    'Canal por el que entro el ticket': 'canal_entrada',
    'Motivo de contacto': 'motivo_contacto',
    'Numero de  cliente': 'numero_cliente',
    'Numero de  Whatsapp': 'numero_whatsapp',
    'Nombre y apellido del usuario': 'nombre_usuario',
    'fc': 'fecha_cerrado',
    'Asignado': 'asignado',
    'Descripciondelcierre': 'descripcion_cierre',
    'Motivo': 'motivo',
}


def normalize_payload(raw_data: dict, field_map: dict) -> dict:
    """Normaliza un payload del webhook usando el mapeo de campos.
    Acepta tanto los nombres originales (con espacios) como los ya normalizados (snake_case).
    """
    normalized = {}
    # Primero mapear campos conocidos del webhook
    for webhook_field, model_field in field_map.items():
        if webhook_field in raw_data:
            normalized[model_field] = raw_data[webhook_field]

    # Luego, si ya vienen en snake_case (por si cambian el formato), agregar sin sobreescribir
    for model_field in field_map.values():
        if model_field not in normalized and model_field in raw_data:
            normalized[model_field] = raw_data[model_field]

    return normalized


@hooks_bp.route('/nuevo-ticket', methods=['POST'])
def nuevo_ticket():
    """Recibe payload de nuevo ticket y lo guarda en BD."""
    data = request.get_json(silent=True)
    logger.info(f"[WEBHOOK nuevo-ticket] Content-Type: {request.content_type} | Payload: {data}")
    if data is None:
        logger.warning(f"[WEBHOOK nuevo-ticket] Body JSON vacío o Content-Type incorrecto. Raw body: {request.get_data(as_text=True)[:500]}")
        return jsonify({'error': 'Body JSON requerido'}), 400

    # Normalizar campos del webhook a snake_case
    normalized = normalize_payload(data, NUEVO_TICKET_FIELD_MAP)
    logger.info(f"[WEBHOOK nuevo-ticket] Normalizado: {normalized}")

    # Validar campos requeridos
    numero_ticket = normalized.get('numero_ticket')
    if numero_ticket is None:
        logger.warning(f"[WEBHOOK nuevo-ticket] Falta numero_ticket. Payload original: {data}")
        return jsonify({'error': 'Campo numero_ticket es requerido'}), 400
    try:
        normalized['numero_ticket'] = int(numero_ticket)
    except (ValueError, TypeError):
        logger.warning(f"[WEBHOOK nuevo-ticket] numero_ticket no numérico: {numero_ticket}")
        return jsonify({'error': 'Campo numero_ticket debe ser numérico'}), 400

    if not normalized.get('numero_cliente'):
        logger.warning(f"[WEBHOOK nuevo-ticket] Falta numero_cliente. Payload original: {data}")
        return jsonify({'error': 'Campo numero_cliente es requerido'}), 400

    record = HookNuevoTicketInterface.create(normalized)
    if record is None:
        return jsonify({'error': 'Error al guardar el registro'}), 500

    logger.info(f"[WEBHOOK nuevo-ticket] Guardado OK: id={record.id}, numero_ticket={numero_ticket}")
    return jsonify({'ok': True, 'id': record.id}), 200


@hooks_bp.route('/cierre-ticket', methods=['POST'])
def cierre_ticket():
    """Recibe payload de cierre de ticket y lo guarda en BD."""
    data = request.get_json(silent=True)
    logger.info(f"[WEBHOOK cierre-ticket] Content-Type: {request.content_type} | Payload: {data}")
    if data is None:
        logger.warning(f"[WEBHOOK cierre-ticket] Body JSON vacío o Content-Type incorrecto. Raw body: {request.get_data(as_text=True)[:500]}")
        return jsonify({'error': 'Body JSON requerido'}), 400

    # Normalizar campos del webhook a snake_case
    normalized = normalize_payload(data, CIERRE_TICKET_FIELD_MAP)
    logger.info(f"[WEBHOOK cierre-ticket] Normalizado: {normalized}")

    # Validar campos requeridos
    numero_ticket = normalized.get('numero_ticket')
    if numero_ticket is None:
        logger.warning(f"[WEBHOOK cierre-ticket] Falta numero_ticket. Payload original: {data}")
        return jsonify({'error': 'Campo numero_ticket es requerido'}), 400
    try:
        normalized['numero_ticket'] = int(numero_ticket)
    except (ValueError, TypeError):
        logger.warning(f"[WEBHOOK cierre-ticket] numero_ticket no numérico: {numero_ticket}")
        return jsonify({'error': 'Campo numero_ticket debe ser numérico'}), 400

    record = HookCierreTicketInterface.create(normalized)
    if record is None:
        return jsonify({'error': 'Error al guardar el registro'}), 500

    logger.info(f"[WEBHOOK cierre-ticket] Guardado OK: id={record.id}, numero_ticket={normalized.get('numero_ticket')}")
    return jsonify({'ok': True, 'id': record.id}), 200
