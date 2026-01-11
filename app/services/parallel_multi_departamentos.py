"""
Sistema Multi-Departamental de Creación de Tickets para Splynx
"""

import os
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Configuración de departamentos
DEPARTAMENTOS = {
    "Soporte_Tecnico": "Soporte Técnico",
    "administracion": "administracion", 
    "Facturacion": "Facturación"
}

class MultiDepartmentTicketCreator:
    def __init__(self, max_workers=5):
        """
        Inicializar el creador multi-departamental
        
        Args:
            max_workers (int): Número máximo de workers concurrentes por departamento
        """
        self.max_workers = max_workers
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.resultados_departamentos = {}
    
    def procesar_departamento(self, dept_key, dept_name):
        """Procesar tickets para un departamento específico"""
        logger.info(f"*** Procesando departamento: {dept_name} ***")
        logger.info("-" * 50)
        
        # Verificar que existe la carpeta del departamento en app/archivos
        base_dir = os.path.abspath(os.path.join(self.script_dir, '..', 'archivos'))
        dept_dir = os.path.join(base_dir, dept_key)
        if not os.path.exists(dept_dir):
            logger.error(f"❌ No existe la carpeta {dept_key}")
            return {"success": False, "error": "Carpeta no encontrada"}
        
        # Verificar que existe el archivo de clientes
        clientes_file = os.path.join(dept_dir, "clientes_extraidos.txt")
        if not os.path.exists(clientes_file):
            logger.info(f"*** Directorio: {dept_dir}")
            logger.info(f"*** Archivo de entrada: clientes_extraidos.txt en {dept_key}")
            logger.error("💡 Ejecuta primero tickets_process.py")
            return {"success": False, "error": "Archivo clientes_extraidos.txt no encontrado"}

    
    def procesar_departamentos_seleccionados(self, departamentos_a_procesar):
        """Procesar una lista de departamentos"""
        logger.info(f"*** Procesando en paralelo: {', '.join([name for _, name in departamentos_a_procesar])} ***")
        
        for dept_key, dept_name in departamentos_a_procesar:
            resultado = self.procesar_departamento(dept_key, dept_name)
            self.resultados_departamentos[dept_key] = resultado
        
        self.mostrar_resumen()
    
    def mostrar_resumen(self):
        """Mostrar resumen final de todos los departamentos procesados"""
        logger.info("=" * 60)
        logger.info("*** RESUMEN DE PROCESAMIENTO ***")
        logger.info("=" * 60)
        
        total_exitosos = 0
        total_tickets_nuevos = 0
        total_tiempo = 0
        
        for dept_key, resultado in self.resultados_departamentos.items():
            dept_name = DEPARTAMENTOS[dept_key]
            
            if resultado["success"]:
                stats = resultado["stats"]
                duration = resultado["duration"]
                new_tickets = resultado["new_tickets"]
                
                logger.info(f"*** {dept_name}: Tickets creados correctamente ***")
                logger.info(f"   - Tickets nuevos creados: {new_tickets}")
                logger.info(f"   - Total exitosos: {stats['success']}")
                logger.info(f"   - Total con Ticket ID: {stats['with_ticket_id']}")
                logger.info(f"   - Tiempo: {duration:.2f} segundos")
                
                total_exitosos += 1
                total_tickets_nuevos += new_tickets
                total_tiempo += duration
            else:
                logger.error(f"*** {dept_name}: Error en el procesamiento ***")
                logger.error(f"   - Error: {resultado['error']}")
        
        logger.info("=" * 60)
        logger.info(f"*** TOTALES GENERALES ***")
        logger.info("=" * 60)
        logger.info(f"   - Departamentos exitosos: {total_exitosos}/{len(self.resultados_departamentos)}")
        logger.info(f"   - Total tickets nuevos: {total_tickets_nuevos}")
        logger.info(f"   - Tiempo total: {total_tiempo:.2f} segundos")
        logger.info("🎉 Proceso multi-departamental completado!")