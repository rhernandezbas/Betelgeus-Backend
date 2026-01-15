"""
Migración para crear los 3 tipos de horarios para cada operador:
- work: Horario laboral general
- assignment: Horario para asignación de tickets
- alert: Horario para alertas de WhatsApp
"""

from app import create_app
from app.utils.config import db
from sqlalchemy import text

app = create_app()

# Mapeo de operadores
OPERATORS = {
    'Gabriel Romero': 10,
    'Luis Sarco': 27,
    'Cesareo Suarez': 37,
    'Yaini Al': 38
}

# Horarios de TRABAJO (work)
WORK_SCHEDULES = {
    'Luis Sarco': {'start': '10:00', 'end': '18:00', 'days': [0, 1, 2, 3, 4]},  # Lun-Vie 10am-6pm
    'Cesareo Suarez': {'start': '08:00', 'end': '16:00', 'days': [0, 1, 2, 3, 4]},  # Lun-Vie 8am-4pm
    'Yaini Al': {'start': '16:00', 'end': '00:00', 'days': [0, 1, 2, 3, 4]},  # Lun-Vie 4pm-12am
    'Gabriel Romero': {'start': '08:00', 'end': '17:00', 'days': [0, 1, 2, 3, 4]}  # Lun-Vie 8am-5pm
}

# Horarios de ASIGNACIÓN (assignment)
ASSIGNMENT_SCHEDULES = {
    'Gabriel Romero': {'start': '08:00', 'end': '16:00', 'days': [0, 1, 2, 3, 4]},  # Lun-Vie 8am-4pm
    'Luis Sarco': {'start': '10:00', 'end': '17:00', 'days': [0, 1, 2, 3, 4]},  # Lun-Vie 10am-5pm
    'Cesareo Suarez': {'start': '08:00', 'end': '14:00', 'days': [0, 1, 2, 3, 4]},  # Lun-Vie 8am-2pm
    'Yaini Al': {'start': '16:00', 'end': '23:00', 'days': [0, 1, 2, 3, 4]}  # Lun-Vie 4pm-11pm
}

# Horarios de ALERTAS (alert)
ALERT_SCHEDULES = {
    'Gabriel Romero': {'start': '08:00', 'end': '17:00', 'days': [0, 1, 2, 3, 4]},  # Lun-Vie 8am-5pm
    'Luis Sarco': {'start': '10:00', 'end': '18:00', 'days': [0, 1, 2, 3, 4]},  # Lun-Vie 10am-6pm
    'Cesareo Suarez': {'start': '08:00', 'end': '15:00', 'days': [0, 1, 2, 3, 4]},  # Lun-Vie 8am-3pm
    'Yaini Al': {'start': '16:00', 'end': '00:00', 'days': [0, 1, 2, 3, 4]}  # Lun-Vie 4pm-12am
}

def create_schedules():
    with app.app_context():
        # Primero, eliminar todos los horarios existentes
        print("🗑️  Eliminando horarios existentes...")
        db.session.execute(text("DELETE FROM operator_schedule"))
        db.session.commit()
        print("✅ Horarios existentes eliminados")
        
        schedules_created = 0
        
        # Crear horarios de TRABAJO
        print("\n📅 Creando horarios de TRABAJO...")
        for name, person_id in OPERATORS.items():
            if name in WORK_SCHEDULES:
                schedule = WORK_SCHEDULES[name]
                for day in schedule['days']:
                    db.session.execute(text("""
                        INSERT INTO operator_schedule 
                        (person_id, day_of_week, start_time, end_time, schedule_type, is_active)
                        VALUES (:person_id, :day, :start, :end, 'work', 1)
                    """), {
                        'person_id': person_id,
                        'day': day,
                        'start': schedule['start'],
                        'end': schedule['end']
                    })
                    schedules_created += 1
                print(f"  ✓ {name} (ID: {person_id}): {schedule['start']}-{schedule['end']}")
        
        # Crear horarios de ASIGNACIÓN
        print("\n🎯 Creando horarios de ASIGNACIÓN...")
        for name, person_id in OPERATORS.items():
            if name in ASSIGNMENT_SCHEDULES:
                schedule = ASSIGNMENT_SCHEDULES[name]
                for day in schedule['days']:
                    db.session.execute(text("""
                        INSERT INTO operator_schedule 
                        (person_id, day_of_week, start_time, end_time, schedule_type, is_active)
                        VALUES (:person_id, :day, :start, :end, 'assignment', 1)
                    """), {
                        'person_id': person_id,
                        'day': day,
                        'start': schedule['start'],
                        'end': schedule['end']
                    })
                    schedules_created += 1
                print(f"  ✓ {name} (ID: {person_id}): {schedule['start']}-{schedule['end']}")
        
        # Crear horarios de ALERTAS
        print("\n🔔 Creando horarios de ALERTAS...")
        for name, person_id in OPERATORS.items():
            if name in ALERT_SCHEDULES:
                schedule = ALERT_SCHEDULES[name]
                for day in schedule['days']:
                    db.session.execute(text("""
                        INSERT INTO operator_schedule 
                        (person_id, day_of_week, start_time, end_time, schedule_type, is_active)
                        VALUES (:person_id, :day, :start, :end, 'alert', 1)
                    """), {
                        'person_id': person_id,
                        'day': day,
                        'start': schedule['start'],
                        'end': schedule['end']
                    })
                    schedules_created += 1
                print(f"  ✓ {name} (ID: {person_id}): {schedule['start']}-{schedule['end']}")
        
        db.session.commit()
        
        # Verificar resultados
        print("\n📊 Resumen de horarios creados:")
        result = db.session.execute(text("""
            SELECT schedule_type, COUNT(*) as count 
            FROM operator_schedule 
            GROUP BY schedule_type
        """))
        for row in result:
            print(f"  - {row[0]}: {row[1]} horarios")
        
        print(f"\n✅ Total: {schedules_created} horarios creados exitosamente")

if __name__ == '__main__':
    create_schedules()
