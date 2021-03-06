"""rebuilding db upon delete

Revision ID: 565fe598f344
Revises: 
Create Date: 2019-12-02 17:46:01.260517

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '565fe598f344'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('unallocated_income', sa.DECIMAL(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('budget_category',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_user', sa.Integer(), nullable=True),
    sa.Column('category_title', sa.String(length=64), nullable=True),
    sa.Column('spending_category', sa.String(length=64), nullable=True),
    sa.Column('current_balance', sa.DECIMAL(), nullable=True),
    sa.Column('status', sa.CHAR(), nullable=True),
    sa.ForeignKeyConstraint(['id_user'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_budget_category_category_title'), 'budget_category', ['category_title'], unique=False)
    op.create_index(op.f('ix_budget_category_spending_category'), 'budget_category', ['spending_category'], unique=False)
    op.create_index(op.f('ix_budget_category_status'), 'budget_category', ['status'], unique=False)
    op.create_table('budget_history',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_user', sa.Integer(), nullable=True),
    sa.Column('id_budget_category', sa.Integer(), nullable=True),
    sa.Column('start_datetime', sa.DateTime(), nullable=True),
    sa.Column('end_datetime', sa.DateTime(), nullable=True),
    sa.Column('status', sa.CHAR(), nullable=True),
    sa.Column('annual_budget', sa.DECIMAL(), nullable=True),
    sa.ForeignKeyConstraint(['id_budget_category'], ['budget_category.id'], ),
    sa.ForeignKeyConstraint(['id_user'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_budget_history_status'), 'budget_history', ['status'], unique=False)
    op.create_table('transaction',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_user', sa.Integer(), nullable=True),
    sa.Column('id_budget_category', sa.Integer(), nullable=True),
    sa.Column('date', sa.Date(), nullable=True),
    sa.Column('amount', sa.DECIMAL(), nullable=True),
    sa.Column('vendor', sa.String(length=140), nullable=True),
    sa.Column('note', sa.String(length=140), nullable=True),
    sa.Column('ttype', sa.CHAR(), nullable=True),
    sa.ForeignKeyConstraint(['id_budget_category'], ['budget_category.id'], ),
    sa.ForeignKeyConstraint(['id_user'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_transaction_amount'), 'transaction', ['amount'], unique=False)
    op.create_index(op.f('ix_transaction_date'), 'transaction', ['date'], unique=False)
    op.create_index(op.f('ix_transaction_ttype'), 'transaction', ['ttype'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_transaction_ttype'), table_name='transaction')
    op.drop_index(op.f('ix_transaction_date'), table_name='transaction')
    op.drop_index(op.f('ix_transaction_amount'), table_name='transaction')
    op.drop_table('transaction')
    op.drop_index(op.f('ix_budget_history_status'), table_name='budget_history')
    op.drop_table('budget_history')
    op.drop_index(op.f('ix_budget_category_status'), table_name='budget_category')
    op.drop_index(op.f('ix_budget_category_spending_category'), table_name='budget_category')
    op.drop_index(op.f('ix_budget_category_category_title'), table_name='budget_category')
    op.drop_table('budget_category')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    # ### end Alembic commands ###
