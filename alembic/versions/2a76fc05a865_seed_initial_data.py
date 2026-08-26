"""seed_initial_data

Revision ID: 2a76fc05a865
Revises: 5a76099fd413
Create Date: 2026-08-26 20:56:08.070232

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import uuid
from app.services.auth import get_password_hash
from app.config import settings

# revision identifiers, used by Alembic.
revision: str = '2a76fc05a865'
down_revision: Union[str, Sequence[str], None] = '5a76099fd413'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # define tables for bulk insert
    boards_table = sa.table('boards',
        sa.column('name', sa.String),
        sa.column('description', sa.String),
        sa.column('display_order', sa.Integer)
    )
    
    op.bulk_insert(boards_table, [
        {'name': 'Site Hakkında', 'description': 'Kurallar, İletişim, Duyurular', 'display_order': 1},
        {'name': 'Sakin', 'description': 'Grup hakkında yorumlar.', 'display_order': 2},
        {'name': 'HAYAT - 2008', 'description': 'Albüm hakkında yorumlar', 'display_order': 3},
        {'name': 'Müzik', 'description': 'Yerli Müzisyenler, Yabancı Müzisyenler, Amatör Müzik', 'display_order': 4},
        {'name': 'Kültür - Sanat', 'description': 'Edebiyat, Felsefe, Sinema & Tiyatro', 'display_order': 5},
        {'name': 'Genel', 'description': 'Kategori dışı konular...', 'display_order': 6},
    ])

    users_table = sa.table('users',
        sa.column('id', sa.Uuid),
        sa.column('username', sa.String),
        sa.column('email', sa.String),
        sa.column('password_hash', sa.String),
        sa.column('is_admin', sa.Boolean),
        sa.column('is_banned', sa.Boolean)
    )
    
    op.bulk_insert(users_table, [
        {
            'id': uuid.uuid4(),
            'username': settings.ADMIN_USERNAME,
            'email': settings.ADMIN_EMAIL,
            'password_hash': get_password_hash(settings.ADMIN_PASSWORD),
            'is_admin': True,
            'is_banned': False
        }
    ])

def downgrade() -> None:
    op.execute(f"DELETE FROM users WHERE username = '{settings.ADMIN_USERNAME}'")
    op.execute("DELETE FROM boards WHERE display_order IN (1, 2, 3, 4, 5, 6)")