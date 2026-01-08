"""
Scheduler para tareas programadas
Ejecuta el flujo completo de tickets cada 10 minutos
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import threading
from datetime import datetime
import pytz


def run_all_flow_job(app):
    """Ejecuta el flujo completo de tickets (download CSV + create tickets)"""
    from app.routes.thread_functions import thread_download_csv, thread_create_tickets
    
    # Obtener hora actual en Argentina
    tz_argentina = pytz.timezone('America/Argentina/Buenos_Aires')
    now = datetime.now(tz_argentina)
    
    print(f"\n{'='*60}")
    print(f"🕐 CRON JOB INICIADO - {now.strftime('%Y-%m-%d %H:%M:%S')} (Argentina)")
    print(f"{'='*60}")
    
    try:
        # Primer paso: Descargar CSV
        print("📥 Paso 1/2: Descargando CSV...")
        hilo1 = threading.Thread(target=thread_download_csv)
        hilo1.start()
        hilo1.join()  # Esperar a que termine
        print("✅ CSV descargado exitosamente")
        
        # Segundo paso: Crear tickets
        print("🎫 Paso 2/2: Creando tickets...")
        thread_create_tickets(app)
        print("✅ Tickets creados exitosamente")
        
        print(f"{'='*60}")
        print(f"✅ CRON JOB COMPLETADO - {datetime.now(tz_argentina).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"❌ Error en cron job: {str(e)}")
        print(f"{'='*60}\n")


def init_scheduler(app):
    """Inicializa el scheduler con la tarea programada"""
    scheduler = BackgroundScheduler(timezone='America/Argentina/Buenos_Aires')
    
    # Agregar job que se ejecuta cada 10 minutos
    scheduler.add_job(
        func=lambda: run_all_flow_job(app),
        trigger=IntervalTrigger(minutes=10),
        id='all_flow_job',
        name='Ejecutar all_flow cada 10 minutos',
        replace_existing=True
    )
    
    # Iniciar el scheduler
    scheduler.start()
    
    print("\n" + "="*60)
    print("⏰ SCHEDULER INICIADO")
    print("📋 Tarea: Ejecutar all_flow cada 10 minutos")
    print("🌎 Zona horaria: America/Argentina/Buenos_Aires")
    print("="*60 + "\n")
    
    return scheduler
