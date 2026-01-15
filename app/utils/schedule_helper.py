"""
Helper para obtener horarios de operadores desde la base de datos
"""

from typing import List, Dict, Optional
from datetime import datetime
import pytz
from app.models.models import OperatorSchedule
from app.utils.logger import get_logger

logger = get_logger(__name__)

class ScheduleHelper:
    """Helper para trabajar con horarios de operadores desde la BD"""
    
    @staticmethod
    def get_operator_schedules(person_id: int, schedule_type: str, day_of_week: Optional[int] = None) -> List[Dict]:
        """
        Obtiene los horarios de un operador desde la BD
        
        Args:
            person_id: ID del operador
            schedule_type: Tipo de horario ('work', 'assignment', 'alert')
            day_of_week: Día de la semana (0=Lunes, 6=Domingo). Si es None, obtiene todos los días
            
        Returns:
            Lista de horarios en formato [{"start": "HH:MM", "end": "HH:MM"}]
        """
        try:
            query = OperatorSchedule.query.filter_by(
                person_id=person_id,
                schedule_type=schedule_type,
                is_active=True
            )
            
            if day_of_week is not None:
                query = query.filter_by(day_of_week=day_of_week)
            
            schedules = query.all()
            
            return [
                {
                    "start": schedule.start_time,
                    "end": schedule.end_time,
                    "day": schedule.day_of_week
                }
                for schedule in schedules
            ]
        except Exception as e:
            logger.error(f"Error obteniendo horarios de BD para person_id {person_id}: {e}")
            return []
    
    @staticmethod
    def is_operator_available(person_id: int, schedule_type: str = 'assignment', 
                             current_time: Optional[datetime] = None) -> bool:
        """
        Verifica si un operador está disponible según sus horarios de BD
        
        Args:
            person_id: ID del operador
            schedule_type: Tipo de horario a verificar ('work', 'assignment', 'alert')
            current_time: Hora actual (si es None, usa la hora actual de Argentina)
            
        Returns:
            bool: True si el operador está disponible, False si no
        """
        if current_time is None:
            tz_argentina = pytz.timezone('America/Argentina/Buenos_Aires')
            current_time = datetime.now(tz_argentina)
        
        day_of_week = current_time.weekday()  # 0=Lunes, 6=Domingo
        current_hour = current_time.hour
        current_minute = current_time.minute
        current_time_minutes = current_hour * 60 + current_minute
        
        # Obtener horarios del operador para el día actual
        schedules = ScheduleHelper.get_operator_schedules(person_id, schedule_type, day_of_week)
        
        if not schedules:
            logger.debug(f"No hay horarios de tipo '{schedule_type}' para person_id {person_id} el día {day_of_week}")
            return False
        
        # Verificar si la hora actual está dentro de algún horario
        for schedule in schedules:
            start_time = schedule["start"]
            end_time = schedule["end"]
            
            # Convertir a minutos
            start_hour, start_min = map(int, start_time.split(':'))
            end_hour, end_min = map(int, end_time.split(':'))
            
            start_minutes = start_hour * 60 + start_min
            end_minutes = end_hour * 60 + end_min
            
            # Manejar horarios que cruzan medianoche (ej: 16:00 - 00:00)
            if end_minutes == 0:  # 00:00 = medianoche
                end_minutes = 24 * 60  # 1440 minutos
            
            if start_minutes <= current_time_minutes < end_minutes:
                logger.debug(f"Operador {person_id} disponible: {start_time}-{end_time}")
                return True
        
        logger.debug(f"Operador {person_id} NO disponible en horario {schedule_type}")
        return False
    
    @staticmethod
    def get_available_operators(operator_ids: List[int], schedule_type: str = 'assignment',
                               current_time: Optional[datetime] = None) -> List[int]:
        """
        Obtiene lista de operadores disponibles según sus horarios de BD
        
        Args:
            operator_ids: Lista de IDs de operadores a verificar
            schedule_type: Tipo de horario a verificar ('work', 'assignment', 'alert')
            current_time: Hora actual (si es None, usa la hora actual de Argentina)
            
        Returns:
            Lista de IDs de operadores disponibles
        """
        available = []
        
        for person_id in operator_ids:
            if ScheduleHelper.is_operator_available(person_id, schedule_type, current_time):
                available.append(person_id)
        
        return available
    
    @staticmethod
    def get_schedule_end_time(person_id: int, schedule_type: str = 'work',
                             day_of_week: Optional[int] = None) -> Optional[str]:
        """
        Obtiene la hora de fin del último turno del operador
        
        Args:
            person_id: ID del operador
            schedule_type: Tipo de horario ('work', 'assignment', 'alert')
            day_of_week: Día de la semana (si es None, usa el día actual)
            
        Returns:
            Hora de fin en formato "HH:MM" o None si no hay horarios
        """
        if day_of_week is None:
            tz_argentina = pytz.timezone('America/Argentina/Buenos_Aires')
            day_of_week = datetime.now(tz_argentina).weekday()
        
        schedules = ScheduleHelper.get_operator_schedules(person_id, schedule_type, day_of_week)
        
        if not schedules:
            return None
        
        # Obtener el horario con la hora de fin más tardía
        latest_end = max(schedules, key=lambda s: s["end"])
        return latest_end["end"]
    
    @staticmethod
    def get_all_operators_with_schedules(schedule_type: str = 'assignment') -> List[int]:
        """
        Obtiene lista de todos los operadores que tienen horarios configurados
        
        Args:
            schedule_type: Tipo de horario ('work', 'assignment', 'alert')
            
        Returns:
            Lista de person_ids que tienen horarios configurados
        """
        try:
            schedules = OperatorSchedule.query.filter_by(
                schedule_type=schedule_type,
                is_active=True
            ).distinct(OperatorSchedule.person_id).all()
            
            return list(set(schedule.person_id for schedule in schedules))
        except Exception as e:
            logger.error(f"Error obteniendo operadores con horarios: {e}")
            return []
