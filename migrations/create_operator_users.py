"""
Crear cuentas de usuario para los 4 operadores
"""

import sys
sys.path.insert(0, '/app')
from app import create_app
from app.utils.config import db
from app.models.models import User
from werkzeug.security import generate_password_hash

app = create_app()

OPERATORS = [
    {
        'username': 'gabriel',
        'password': 'gabriel123',
        'full_name': 'Gabriel Romero',
        'person_id': 10,
        'email': 'gabriel@splynx.com'
    },
    {
        'username': 'luis',
        'password': 'luis123',
        'full_name': 'Luis Sarco',
        'person_id': 27,
        'email': 'luis@splynx.com'
    },
    {
        'username': 'cesareo',
        'password': 'cesareo123',
        'full_name': 'Cesareo Suarez',
        'person_id': 37,
        'email': 'cesareo@splynx.com'
    },
    {
        'username': 'yaini',
        'password': 'yaini123',
        'full_name': 'Yaini Al',
        'person_id': 38,
        'email': 'yaini@splynx.com'
    }
]

def create_operator_users():
    with app.app_context():
        print('👥 Creando cuentas de usuario para operadores...\n')
        
        for op_data in OPERATORS:
            # Verificar si el usuario ya existe
            existing_user = User.query.filter_by(username=op_data['username']).first()
            
            if existing_user:
                print(f"⚠️  Usuario '{op_data['username']}' ya existe, actualizando...")
                existing_user.full_name = op_data['full_name']
                existing_user.person_id = op_data['person_id']
                existing_user.email = op_data['email']
                existing_user.role = 'operator'
                existing_user.is_active = True
                print(f"   ✓ Actualizado: {op_data['full_name']} (person_id: {op_data['person_id']})")
            else:
                # Crear nuevo usuario
                new_user = User(
                    username=op_data['username'],
                    password_hash=generate_password_hash(op_data['password']),
                    full_name=op_data['full_name'],
                    email=op_data['email'],
                    role='operator',
                    person_id=op_data['person_id'],
                    is_active=True,
                    created_by='system'
                )
                db.session.add(new_user)
                print(f"✅ Creado: {op_data['full_name']} (username: {op_data['username']}, person_id: {op_data['person_id']})")
        
        db.session.commit()
        
        print('\n📊 Resumen de usuarios operadores:')
        operators = User.query.filter_by(role='operator').all()
        for user in operators:
            status = '🟢' if user.is_active else '🔴'
            print(f"  {status} {user.full_name} (@{user.username}) - person_id: {user.person_id}")
        
        print(f'\n✅ Total: {len(operators)} usuarios operadores en el sistema')
        print('\n🔑 Credenciales de acceso:')
        for op_data in OPERATORS:
            print(f"  - Usuario: {op_data['username']} | Contraseña: {op_data['password']}")

if __name__ == '__main__':
    create_operator_users()
