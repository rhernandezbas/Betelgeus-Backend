import logging
import sys
import os
from logging.handlers import RotatingFileHandler


_loggers = {}


def setup_logger(name: str, log_file: str = None, level=logging.INFO) -> logging.Logger:
    """
    Configura y retorna un logger con rotación de archivos.
    
    Args:
        name: Nombre del logger (usualmente __name__ del módulo)
        log_file: Ruta del archivo de log (opcional, si no se provee solo usa stdout)
        level: Nivel de logging (default: INFO)
    
    Returns:
        logging.Logger: Logger configurado
    """
    if name in _loggers:
        return _loggers[name]
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False
    
    if logger.handlers:
        return logger
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    logger.addHandler(console_handler)
    
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        logger.addHandler(file_handler)
    
    _loggers[name] = logger
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Obtiene un logger configurado para el módulo.
    
    Args:
        name: Nombre del logger (usualmente __name__ del módulo)
    
    Returns:
        logging.Logger: Logger configurado
    """
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
    log_file = os.path.join(log_dir, 'app_splynx.log')
    return setup_logger(name, log_file=log_file)
