"""
Initial schema — baseline migration.

NOTE: This migration was added AFTER the database already existed
(tables were previously created by Base.metadata.create_all()).
All CREATE TABLE and CREATE INDEX operations are guarded with
existence checks so this migration is safe to run on both:
  - A fresh empty database (creates everything)
  - An existing database (skips tables that already exist)

If you are applying Alembic to an existing database for the first time,
run: alembic stamp 0001
to mark this migration as complete without re-running it.
"""

from typing import Sequence, Union
from sqlalchemy import inspect
from alembic import op
import sqlalchemy as sa

revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_tables = inspector.get_table_names()
    
    existing_indexes = {
        idx["name"]
        for table in existing_tables
        for idx in inspector.get_indexes(table)
    }

    # emails
    if "emails" not in existing_tables:
        op.create_table('emails',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('message_id', sa.String(length=512), nullable=False),
            sa.Column('sender', sa.String(length=512), nullable=False),
            sa.Column('subject', sa.String(length=1024), nullable=False),
            sa.Column('date', sa.String(length=256), nullable=True),
            sa.Column('to_address', sa.String(length=512), nullable=True),
            sa.Column('body_html', sa.Text(), nullable=True),
            sa.Column('body_text', sa.Text(), nullable=True),
            sa.Column('has_html', sa.Boolean(), nullable=False),
            sa.Column('has_attachments', sa.Boolean(), nullable=False),
            sa.Column('fetched_at', sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint('id')
        )
    
    if "ix_emails_fetched_at" not in existing_indexes:
        op.create_index(op.f('ix_emails_fetched_at'), 'emails', ['fetched_at'], unique=False)
    if "ix_emails_id" not in existing_indexes:
        op.create_index(op.f('ix_emails_id'), 'emails', ['id'], unique=False)
    if "ix_emails_message_id" not in existing_indexes:
        op.create_index(op.f('ix_emails_message_id'), 'emails', ['message_id'], unique=True)
    if "ix_emails_sender" not in existing_indexes:
        op.create_index(op.f('ix_emails_sender'), 'emails', ['sender'], unique=False)
    if "ix_emails_subject" not in existing_indexes:
        op.create_index(op.f('ix_emails_subject'), 'emails', ['subject'], unique=False)

    # attachments
    if "attachments" not in existing_tables:
        op.create_table('attachments',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('email_id', sa.Integer(), nullable=False),
            sa.Column('filename', sa.String(length=512), nullable=False),
            sa.Column('content_type', sa.String(length=256), nullable=True),
            sa.Column('size_bytes', sa.Integer(), nullable=False),
            sa.Column('sha256_hash', sa.String(length=64), nullable=True),
            sa.Column('storage_path', sa.String(length=1024), nullable=True),
            sa.ForeignKeyConstraint(['email_id'], ['emails.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
    if "ix_attachments_email_id" not in existing_indexes:
        op.create_index(op.f('ix_attachments_email_id'), 'attachments', ['email_id'], unique=False)
    if "ix_attachments_id" not in existing_indexes:
        op.create_index(op.f('ix_attachments_id'), 'attachments', ['id'], unique=False)

    # scans
    if "scans" not in existing_tables:
        op.create_table('scans',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('email_id', sa.Integer(), nullable=False),
            sa.Column('status', sa.String(length=32), nullable=False),
            sa.Column('started_at', sa.DateTime(), nullable=True),
            sa.Column('completed_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['email_id'], ['emails.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
    if "ix_scans_email_id" not in existing_indexes:
        op.create_index(op.f('ix_scans_email_id'), 'scans', ['email_id'], unique=False)
    if "ix_scans_id" not in existing_indexes:
        op.create_index(op.f('ix_scans_id'), 'scans', ['id'], unique=False)

    # verdicts
    if "verdicts" not in existing_tables:
        op.create_table('verdicts',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('scan_id', sa.Integer(), nullable=False),
            sa.Column('final_score', sa.Float(), nullable=False),
            sa.Column('classification', sa.String(length=32), nullable=False),
            sa.Column('ai_score', sa.Float(), nullable=False),
            sa.Column('ai_label', sa.String(length=64), nullable=True),
            sa.Column('url_score', sa.Float(), nullable=False),
            sa.Column('attachment_score', sa.Float(), nullable=False),
            sa.Column('breakdown', sa.JSON(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['scan_id'], ['scans.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
    if "ix_verdicts_id" not in existing_indexes:
        op.create_index(op.f('ix_verdicts_id'), 'verdicts', ['id'], unique=False)
    if "ix_verdicts_scan_id" not in existing_indexes:
        op.create_index(op.f('ix_verdicts_scan_id'), 'verdicts', ['scan_id'], unique=True)

    # fetch_state
    if "fetch_state" not in existing_tables:
        op.create_table('fetch_state',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('mailbox', sa.String(length=256), nullable=False),
            sa.Column('last_uid', sa.Integer(), nullable=False),
            sa.Column('last_fetched_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('mailbox')
        )
    if "ix_fetch_state_id" not in existing_indexes:
        op.create_index(op.f('ix_fetch_state_id'), 'fetch_state', ['id'], unique=False)

def downgrade() -> None:
    op.drop_table('verdicts')
    op.drop_table('scans')
    op.drop_table('attachments')
    op.drop_table('emails')
    op.drop_table('fetch_state')
