#!/usr/bin/env python3
"""
Script de validación de variables de entorno
Verifica que todas las variables necesarias estén definidas
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Variables requeridas
REQUIRED_VARS = [
    'SECRET_KEY',
    'DB_HOST',
    'DB_PORT',
    'DB_NAME',
    'DB_USER',
    'DB_PASSWORD',
    'SPLYNX_BASE_URL',
    'SPLYNX_USER',
    'SPLYNX_PASSWORD',
    'GESTION_REAL_USERNAME',
    'GESTION_REAL_PASSWORD',
    'EVOLUTION_API_BASE_URL',
    'EVOLUTION_API_KEY',
    'EVOLUTION_INSTANCE_NAME',
]

# Variables opcionales (con valores por defecto)
OPTIONAL_VARS = [
    'SPLYNX_SSL_VERIFY',
    'GESTION_REAL_LOGIN_URL',
    'GESTION_REAL_CASOS_URL',
    'DEVICE_ANALYSIS_API_URL',
    'SESSION_COOKIE_SECURE',
]


def validate_env():
    """Valida que todas las variables requeridas estén definidas"""
    missing = []
    warnings = []

    print("=" * 70)
    print("VALIDACIÓN DE VARIABLES DE ENTORNO")
    print("=" * 70)

    # Verificar variables requeridas
    print("\n✓ Variables Requeridas:")
    for var in REQUIRED_VARS:
        value = os.getenv(var)
        if not value:
            missing.append(var)
            print(f"  ❌ {var}: NO DEFINIDA")
        else:
            # Ocultar valor sensible
            display_value = value if len(value) < 20 else f"{value[:10]}...{value[-5:]}"
            if 'PASSWORD' in var or 'KEY' in var or 'SECRET' in var:
                display_value = "***********"
            print(f"  ✅ {var}: {display_value}")

    # Verificar variables opcionales
    print("\n✓ Variables Opcionales:")
    for var in OPTIONAL_VARS:
        value = os.getenv(var)
        if not value:
            warnings.append(var)
            print(f"  ⚠️  {var}: NO DEFINIDA (usando valor por defecto)")
        else:
            print(f"  ✅ {var}: {value}")

    # Resultado
    print("\n" + "=" * 70)
    if missing:
        print("❌ VALIDACIÓN FALLIDA")
        print(f"\nVariables faltantes ({len(missing)}):")
        for var in missing:
            print(f"  - {var}")
        print("\nPor favor, configura estas variables en el archivo .env")
        return False
    else:
        print("✅ VALIDACIÓN EXITOSA")
        if warnings:
            print(f"\n⚠️  Hay {len(warnings)} variables opcionales sin definir (se usarán valores por defecto)")
        return True


if __name__ == '__main__':
    success = validate_env()
    sys.exit(0 if success else 1)
