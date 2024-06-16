"""empty message

Revision ID: 084b523aff5e
Revises: 1407a74d1252
Create Date: 2024-06-16 06:30:17.425325

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '084b523aff5e'
down_revision = '1407a74d1252'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('vendor',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('vendor_name', sa.String(length=255), nullable=True),
    sa.Column('registered_name', sa.String(length=255), nullable=True),
    sa.Column('tin', sa.String(length=255), nullable=True),
    sa.Column('business_style', sa.String(length=255), nullable=True),
    sa.Column('address', sa.String(length=255), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('admin_vendor',
    sa.Column('vendor_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['vendor_id'], ['vendor.id'], ),
    sa.PrimaryKeyConstraint('vendor_id', 'user_id')
    )
    op.create_table('purchase_order',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('record_date', sa.String(), nullable=True),
    sa.Column('purchase_order_number', sa.String(), nullable=True),
    sa.Column('vendor_id', sa.Integer(), nullable=False),
    sa.Column('notes', sa.String(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('submitted', sa.String(), nullable=True),
    sa.Column('cancelled', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['vendor_id'], ['vendor.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_vendor',
    sa.Column('vendor_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['vendor_id'], ['vendor.id'], ),
    sa.PrimaryKeyConstraint('vendor_id', 'user_id')
    )
    op.create_table('admin_purchase_order',
    sa.Column('purchase_order_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['purchase_order_id'], ['purchase_order.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('purchase_order_id', 'user_id')
    )
    op.create_table('purchase_order_detail',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('purchase_request_number', sa.String(), nullable=True),
    sa.Column('grouping', sa.String(), nullable=True),
    sa.Column('purchase_order_id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Float(), nullable=True),
    sa.Column('measure_id', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('unit_price', sa.Float(), nullable=True),
    sa.Column('side_note', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['measure_id'], ['measure.id'], ),
    sa.ForeignKeyConstraint(['purchase_order_id'], ['purchase_order.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_purchase_order',
    sa.Column('purchase_order_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['purchase_order_id'], ['purchase_order.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('purchase_order_id', 'user_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_purchase_order')
    op.drop_table('purchase_order_detail')
    op.drop_table('admin_purchase_order')
    op.drop_table('user_vendor')
    op.drop_table('purchase_order')
    op.drop_table('admin_vendor')
    op.drop_table('vendor')
    # ### end Alembic commands ###