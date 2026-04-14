"""add_url_results

Revision ID: 0002
Revises: 0001
Create Date: 2026-04-13 12:01:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '0002'
down_revision: Union[str, None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table('url_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('scan_id', sa.Integer(), nullable=False),
        sa.Column('original_url', sa.String(length=2048), nullable=False),
        sa.Column('normalized_url', sa.String(length=2048), nullable=True),
        sa.Column('is_shortener', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('heuristic_score', sa.Float(), nullable=False),
        sa.Column('vt_score', sa.Float(), nullable=False),
        sa.Column('final_score', sa.Float(), nullable=False),
        sa.Column('vt_malicious', sa.Integer(), nullable=False),
        sa.Column('vt_suspicious', sa.Integer(), nullable=False),
        sa.Column('vt_harmless', sa.Integer(), nullable=False),
        sa.Column('vt_total', sa.Integer(), nullable=False),
        sa.Column('vt_error', sa.String(length=256), nullable=True),
        sa.Column('heuristic_flags', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('dynamic_score', sa.Float(), nullable=True),
        sa.Column('redirect_chain', sa.JSON(), nullable=True),
        sa.Column('dom_has_login_form', sa.Boolean(), nullable=True),
        sa.Column('ssl_valid', sa.Boolean(), nullable=True),
        sa.Column('playwright_screenshot_path', sa.String(length=1024), nullable=True),
        sa.ForeignKeyConstraint(['scan_id'], ['scans.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_url_results_id'), 'url_results', ['id'], unique=False)
    op.create_index(op.f('ix_url_results_scan_id'), 'url_results', ['scan_id'], unique=False)
    op.create_index(op.f('ix_url_results_final_score'), 'url_results', ['final_score'], unique=False)

def downgrade() -> None:
    op.drop_table('url_results')
