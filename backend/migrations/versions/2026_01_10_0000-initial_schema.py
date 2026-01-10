"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-01-10 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('username', sa.String(50), nullable=False, unique=True),
        sa.Column('email', sa.String(100), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(100), nullable=False),
        sa.Column('role', sa.Enum('admin', 'evaluator', name='userrole'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, onupdate=sa.text('NOW()'))
    )
    op.create_index('ix_users_username', 'users', ['username'])
    op.create_index('ix_users_email', 'users', ['email'])

    # Projects table
    op.create_table(
        'projects',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('stage', sa.String(20), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('evaluation_template', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, onupdate=sa.text('NOW()'))
    )

    # Companies table
    op.create_table(
        'companies',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('business_number', sa.String(20), nullable=True, unique=True),
        sa.Column('ceo_name', sa.String(50), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('contact_email', sa.String(100), nullable=True),
        sa.Column('contact_phone', sa.String(20), nullable=True),
        sa.Column('documents_path', sa.Text(), nullable=True),
        sa.Column('ocr_data', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('ocr_confidence', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()'))
    )
    op.create_index('ix_companies_project', 'companies', ['project_id'])
    op.create_index('ix_companies_business_number', 'companies', ['business_number'])

    # Evaluations table
    op.create_table(
        'evaluations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('evaluator_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('scores_data', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('overall_comment', sa.Text(), nullable=True),
        sa.Column('total_score', sa.Float(), nullable=True),
        sa.Column('weighted_score', sa.Float(), nullable=True),
        sa.Column('is_submitted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('submitted_at', sa.DateTime(), nullable=True),
        sa.Column('signature_data', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, onupdate=sa.text('NOW()'))
    )
    op.create_index('ix_evaluations_company', 'evaluations', ['company_id'])
    op.create_index('ix_evaluations_evaluator', 'evaluations', ['evaluator_id'])
    op.create_index('ix_evaluations_submitted', 'evaluations', ['is_submitted'])
    # Unique constraint for company-evaluator pair
    op.create_unique_constraint('uq_evaluations_company_evaluator', 'evaluations', ['company_id', 'evaluator_id'])

    # Audit logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('username', sa.String(50), nullable=False),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('resource', sa.String(100), nullable=True),
        sa.Column('details', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('status', sa.String(20), nullable=False, server_default='SUCCESS'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()'))
    )
    op.create_index('ix_audit_logs_user', 'audit_logs', ['user_id'])
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('ix_audit_logs_created', 'audit_logs', ['created_at'], postgresql_ops={'created_at': 'DESC'})


def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('evaluations')
    op.drop_table('companies')
    op.drop_table('projects')
    op.drop_table('users')
    op.execute('DROP TYPE userrole')
