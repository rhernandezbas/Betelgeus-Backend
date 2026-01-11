import csv
import os
from app.utils.constants import DEPARTAMENTOS
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Mapeo de prioridades a formato Splynx
PRIORITY_MAP = {
    "baja": "low",
    "media": "medium", 
    "alta": "high",
    "urgente": "urgent"
}

def procesar_departamento(dept_key, dept_name):
    """Procesar CSV de un departamento específico"""
    logger.info(f"*** Procesando departamento: {dept_name} ***")
    logger.info("-" * 50)
    
    # Obtener directorios
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.abspath(os.path.join(script_dir, '..', 'archivos'))
    dept_dir = os.path.join(base_dir, dept_key)
    
    # Archivos de entrada y salida
    csv_file = os.path.join(dept_dir, "casos_recientes.csv")
    output_file = os.path.join(dept_dir, "clientes_extraidos.txt")
    
    logger.info(f"*** Directorio: {dept_dir}")
    logger.info(f"*** CSV de entrada: casos_recientes.csv")
    logger.info(f"*** Archivo de salida: clientes_extraidos.txt")
    
    # Verificar que existe el CSV
    if not os.path.exists(csv_file):
        logger.error(f"*** No se encontró el archivo CSV en {dept_key}")
        logger.error("*** Ejecuta primero selenium_multi_departamentos.py")
        return False
    
    try:
        # Crear archivo de salida
        with open(output_file, "w", encoding="utf-8") as f_out:
            # Escribir encabezados
            f_out.write("Cliente\tAsunto\tFecha_Creacion\tPrioridad\n")
            
            # Procesar CSV
            with open(csv_file, newline="", encoding="latin-1") as csvfile:
                reader = csv.DictReader(csvfile, delimiter=";")
                
                clientes_procesados = 0
                for fila in reader:
                    cliente = fila.get("Cliente", "").strip()
                    asunto_original = fila.get("Asunto", "").strip()
                    fecha_creacion = fila.get("Fecha Creacion", "").strip()
                    prioridad_raw = fila.get("Prioridad", "").strip().lower()
                    contrato = fila.get("Contrato", "").strip()
                    
                    # Convertir prioridad usando el mapeo
                    prioridad = PRIORITY_MAP.get(prioridad_raw, "medium")
                    
                    # Lógica para determinar el asunto basado en FO en el contrato
                    if "FO" in contrato.upper() or "FTTH" in contrato.upper():
                        asunto = "Ticket-FO"
                    else:
                        asunto = "Ticket-WIRELESS"
                    
                    if cliente:  # Solo guardar si hay cliente
                        f_out.write(f"{cliente}\t{asunto}\t{fecha_creacion}\t{prioridad}\n")
                        clientes_procesados += 1
                
                logger.info(f"*** {clientes_procesados} clientes procesados para {dept_name} ***")
                return True
                
    except Exception as e:
        logger.error(f"*** Error procesando {dept_name}: {e} ***")
        return False

def main():
    """Función principal para procesar departamentos automáticamente"""
    logger.info("*** Sistema Multi-Departamental de Procesamiento de Clientes ***")
    logger.info("=" * 65)
    logger.info("*** MODO AUTOMATICO - Sin verificaciones ***")
    
    # Procesar automáticamente solo los departamentos habilitados
    departamentos_a_procesar = [(key, name) for key, name in DEPARTAMENTOS.items()]
    
    logger.info(f"*** Procesando automaticamente: {', '.join([name for _, name in departamentos_a_procesar])} ***")
    
    # Procesar departamentos seleccionados
    resultados = {}
    for dept_key, dept_name in departamentos_a_procesar:
        success = procesar_departamento(dept_key, dept_name)
        resultados[dept_key] = success
    
    # Mostrar resumen
    logger.info("=" * 65)
    logger.info("*** RESUMEN DE PROCESAMIENTO ***")
    logger.info("=" * 65)
    
    exitosos = 0
    for dept_key, success in resultados.items():
        dept_name = DEPARTAMENTOS[dept_key]
        if success:
            logger.info(f"*** {dept_name}: Clientes extraídos correctamente ***")
            exitosos += 1
        else:
            logger.error(f"*** {dept_name}: Error en el procesamiento ***")
    
    logger.info(f"*** Total exitosos: {exitosos}/{len(resultados)} ***")
    
    if exitosos > 0:
        logger.info("*** Proceso completado! ***")
        logger.info("*** Continuando con la creación de tickets... ***")
    else:
        logger.error("*** No se procesaron departamentos exitosamente ***")

if __name__ == "__main__":
    main()
