"""Fix message content column type to TEXT

Revision ID: fix_message_content_type
Revises: 
Create Date: 2025-11-02

"""
from alembic import op
import sqlalchemy as sa


def upgrade():
    """Change message.content from VARCHAR(255) to TEXT."""
    # PostgreSQL
    op.execute("ALTER TABLE message ALTER COLUMN content TYPE TEXT;")
    
    # Optional: Also check reaction column if needed
    # op.execute("ALTER TABLE message ALTER COLUMN reaction TYPE TEXT;")


def downgrade():
    """Revert message.content back to VARCHAR(255)."""
    op.execute("ALTER TABLE message ALTER COLUMN content TYPE VARCHAR(255);")
