"""
Device Analysis API Routes - Análisis completo de dispositivos con IA y feedback
"""

from flask import Blueprint, jsonify, request
from app.models.models import DeviceAnalysis
from app.utils.config import db
from app.utils.logger import get_logger
from app.utils.constants import DEVICE_ANALYSIS_API_URL
from datetime import datetime
import requests
import time

logger = get_logger(__name__)

device_analysis_bp = Blueprint('device_analysis', __name__, url_prefix='/api/device-analysis')


def get_client_ip():
    """Get client IP address from request."""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0]
    return request.remote_addr


@device_analysis_bp.route('/analyze-complete', methods=['POST'])
def analyze_device_complete():
    """
    Análisis completo de dispositivo (ping, frecuencias, site survey, métricas, LLM)
    Guarda la consulta y respuesta en base de datos
    """
    try:
        data = request.get_json() or {}
        device_ip = data.get('ip_address') or request.args.get('ip_address')
        ssh_username = data.get('ssh_username') or request.args.get('ssh_username')
        ssh_password = data.get('ssh_password') or request.args.get('ssh_password')
        
        if not device_ip:
            return jsonify({
                'success': False,
                'error': 'IP address is required'
            }), 400
        
        # Preparar parámetros para el endpoint real
        params = {'ip_address': device_ip}
        if ssh_username:
            params['ssh_username'] = ssh_username
        if ssh_password:
            params['ssh_password'] = ssh_password
        
        # Llamar al endpoint real de análisis
        start_time = time.time()
        try:
            response = requests.post(
                f"{DEVICE_ANALYSIS_API_URL}/api/v1/analyze-device-complete",
                params=params,
                timeout=120
            )
            execution_time = int((time.time() - start_time) * 1000)
            
            response_data = response.json()
            success = response.status_code == 200 and response_data.get('success', False)
            
        except Exception as api_error:
            execution_time = int((time.time() - start_time) * 1000)
            logger.error(f"Error calling analyze-device-complete API: {api_error}")
            response_data = {'error': str(api_error)}
            success = False
        
        # Extraer datos relevantes
        device_name = None
        device_model = None
        llm_summary = None
        ping_data = None
        metrics_data = None
        site_survey_data = None
        error_message = None
        
        if success:
            device_info = response_data.get('device', {})
            device_name = device_info.get('name')
            device_model = device_info.get('model')
            
            analysis = response_data.get('analysis', {})
            llm_summary = analysis.get('llm_summary')
            ping_data = analysis.get('ping')
            metrics_data = analysis.get('metrics')
            site_survey_data = analysis.get('site_survey')
        else:
            error_message = response_data.get('detail') or response_data.get('error') or 'Unknown error'
        
        # Guardar en base de datos
        analysis_record = DeviceAnalysis(
            device_ip=device_ip,
            device_name=device_name,
            device_model=device_model,
            analysis_type='complete',
            query_params=params,
            api_response=response_data,
            llm_summary=llm_summary,
            ping_data=ping_data,
            metrics_data=metrics_data,
            site_survey_data=site_survey_data,
            success=success,
            error_message=error_message,
            execution_time_ms=execution_time,
            requested_by=data.get('requested_by', 'unknown'),
            requested_by_role=data.get('requested_by_role', 'unknown'),
            ip_address=get_client_ip()
        )
        
        db.session.add(analysis_record)
        db.session.commit()
        
        # Retornar respuesta con ID del registro
        result = response_data.copy()
        result['analysis_id'] = analysis_record.id
        result['execution_time_ms'] = execution_time
        
        return jsonify(result), response.status_code if 'response' in locals() else 200
        
    except Exception as e:
        logger.error(f"Error in analyze_device_complete: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@device_analysis_bp.route('/metrics', methods=['GET'])
def get_device_metrics():
    """
    Obtiene solo métricas del dispositivo (sin análisis LLM)
    Guarda la consulta y respuesta en base de datos
    """
    try:
        device_ip = request.args.get('ip_address')
        
        if not device_ip:
            return jsonify({
                'success': False,
                'error': 'IP address is required'
            }), 400
        
        # Preparar parámetros
        params = {'ip_address': device_ip}
        
        # Llamar al endpoint real de métricas
        start_time = time.time()
        try:
            response = requests.get(
                f"{DEVICE_ANALYSIS_API_URL}/api/v1/device-metrics",
                params=params,
                timeout=60
            )
            execution_time = int((time.time() - start_time) * 1000)
            
            response_data = response.json()
            success = response.status_code == 200
            
        except Exception as api_error:
            execution_time = int((time.time() - start_time) * 1000)
            logger.error(f"Error calling device-metrics API: {api_error}")
            response_data = {'error': str(api_error)}
            success = False
        
        # Extraer datos relevantes
        device_name = None
        device_model = None
        metrics_data = None
        error_message = None
        
        if success:
            device_name = response_data.get('device_name')
            device_model = response_data.get('device_model')
            metrics_data = response_data
        else:
            error_message = response_data.get('detail') or response_data.get('error') or 'Unknown error'
        
        # Obtener info del usuario desde headers o query params
        requested_by = request.args.get('requested_by', 'unknown')
        requested_by_role = request.args.get('requested_by_role', 'unknown')
        
        # Guardar en base de datos
        analysis_record = DeviceAnalysis(
            device_ip=device_ip,
            device_name=device_name,
            device_model=device_model,
            analysis_type='metrics',
            query_params=params,
            api_response=response_data,
            metrics_data=metrics_data,
            success=success,
            error_message=error_message,
            execution_time_ms=execution_time,
            requested_by=requested_by,
            requested_by_role=requested_by_role,
            ip_address=get_client_ip()
        )
        
        db.session.add(analysis_record)
        db.session.commit()
        
        # Retornar respuesta con ID del registro
        result = response_data.copy()
        result['analysis_id'] = analysis_record.id
        result['execution_time_ms'] = execution_time
        
        return jsonify(result), response.status_code if 'response' in locals() else 200
        
    except Exception as e:
        logger.error(f"Error in get_device_metrics: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@device_analysis_bp.route('/feedback/<int:analysis_id>', methods=['POST'])
def submit_feedback(analysis_id):
    """
    Enviar feedback sobre un análisis
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        rating = data.get('rating')
        comment = data.get('comment', '')
        
        if not rating or rating not in ['helpful', 'not_helpful', 'incorrect']:
            return jsonify({
                'success': False,
                'error': 'Valid rating is required (helpful, not_helpful, incorrect)'
            }), 400
        
        # Buscar el análisis
        analysis = DeviceAnalysis.query.get(analysis_id)
        
        if not analysis:
            return jsonify({
                'success': False,
                'error': 'Analysis not found'
            }), 404
        
        # Actualizar feedback
        analysis.feedback_rating = rating
        analysis.feedback_comment = comment
        analysis.feedback_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Feedback submitted successfully',
            'analysis': analysis.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@device_analysis_bp.route('/history', methods=['GET'])
def get_analysis_history():
    """
    Obtener historial de análisis con filtros opcionales
    """
    try:
        # Parámetros de filtro
        device_ip = request.args.get('device_ip')
        analysis_type = request.args.get('analysis_type')
        requested_by = request.args.get('requested_by')
        success_only = request.args.get('success_only', 'false').lower() == 'true'
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        
        # Construir query
        query = DeviceAnalysis.query
        
        if device_ip:
            query = query.filter(DeviceAnalysis.device_ip == device_ip)
        
        if analysis_type:
            query = query.filter(DeviceAnalysis.analysis_type == analysis_type)
        
        if requested_by:
            query = query.filter(DeviceAnalysis.requested_by == requested_by)
        
        if success_only:
            query = query.filter(DeviceAnalysis.success == True)
        
        # Ordenar por fecha descendente
        query = query.order_by(DeviceAnalysis.requested_at.desc())
        
        # Contar total
        total = query.count()
        
        # Aplicar paginación
        analyses = query.limit(limit).offset(offset).all()
        
        return jsonify({
            'success': True,
            'total': total,
            'limit': limit,
            'offset': offset,
            'analyses': [a.to_dict() for a in analyses]
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting analysis history: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@device_analysis_bp.route('/stats', methods=['GET'])
def get_analysis_stats():
    """
    Obtener estadísticas de análisis
    """
    try:
        # Estadísticas generales
        total_analyses = DeviceAnalysis.query.count()
        successful_analyses = DeviceAnalysis.query.filter(DeviceAnalysis.success == True).count()
        failed_analyses = DeviceAnalysis.query.filter(DeviceAnalysis.success == False).count()
        
        # Feedback stats
        with_feedback = DeviceAnalysis.query.filter(DeviceAnalysis.feedback_rating.isnot(None)).count()
        helpful_count = DeviceAnalysis.query.filter(DeviceAnalysis.feedback_rating == 'helpful').count()
        not_helpful_count = DeviceAnalysis.query.filter(DeviceAnalysis.feedback_rating == 'not_helpful').count()
        incorrect_count = DeviceAnalysis.query.filter(DeviceAnalysis.feedback_rating == 'incorrect').count()
        
        # Por tipo de análisis
        complete_count = DeviceAnalysis.query.filter(DeviceAnalysis.analysis_type == 'complete').count()
        metrics_count = DeviceAnalysis.query.filter(DeviceAnalysis.analysis_type == 'metrics').count()
        
        # Tiempo promedio de ejecución
        avg_execution_time = db.session.query(
            db.func.avg(DeviceAnalysis.execution_time_ms)
        ).filter(DeviceAnalysis.success == True).scalar() or 0
        
        return jsonify({
            'success': True,
            'stats': {
                'total_analyses': total_analyses,
                'successful_analyses': successful_analyses,
                'failed_analyses': failed_analyses,
                'success_rate': round((successful_analyses / total_analyses * 100) if total_analyses > 0 else 0, 2),
                'feedback': {
                    'total_with_feedback': with_feedback,
                    'helpful': helpful_count,
                    'not_helpful': not_helpful_count,
                    'incorrect': incorrect_count,
                    'feedback_rate': round((with_feedback / total_analyses * 100) if total_analyses > 0 else 0, 2)
                },
                'by_type': {
                    'complete': complete_count,
                    'metrics': metrics_count
                },
                'avg_execution_time_ms': round(avg_execution_time, 2)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting analysis stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
