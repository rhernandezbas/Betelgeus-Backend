"""Add AUTO_UNASSIGN_AFTER_SHIFT_ENABLED system config flag

Revision ID: d4e5f6a7b8c9
Revises: 9caedbea016e
Create Date: 2026-03-10 18:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'd4e5f6a7b8c9'
down_revision = '9caedbea016e'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        INSERT INTO system_config (`key`, value, value_type, description, category, updated_at, updated_by)
        VALUES (
            'AUTO_UNASSIGN_AFTER_SHIFT_ENABLED',
            'false',
            'bool',
            'Habilita la desasignación automática de tickets 1 hora después del fin de turno del operador',
            'schedules',
            NOW(),
            'migration'
        )
        ON DUPLICATE KEY UPDATE `key` = `key`
    """)


def downgrade():
    op.execute("DELETE FROM system_config WHERE key = 'AUTO_UNASSIGN_AFTER_SHIFT_ENABLED'")
