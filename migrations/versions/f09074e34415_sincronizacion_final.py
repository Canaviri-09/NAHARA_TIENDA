"""Sincronizacion final
Revision ID: f09074e34415
Revises: 
Create Date: 2026-08-13 17:01:51.925123
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f09074e34415'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 1. Update configuracion_empresa and add new columns safely
    # First add margen_ganancia_mayorista as nullable
    op.add_column('configuracion_empresa', sa.Column('margen_ganancia_mayorista', sa.Numeric(precision=10, scale=2), nullable=True))
    # Populate the values
    op.execute("UPDATE configuracion_empresa SET margen_ganancia_mayorista = 12.50 WHERE margen_ganancia_mayorista IS NULL")
    # Make it nullable=False
    op.alter_column('configuracion_empresa', 'margen_ganancia_mayorista', nullable=False)
    
    # Add other columns to configuracion_empresa
    op.add_column('configuracion_empresa', sa.Column('tipo_cambio_usd', sa.Numeric(precision=10, scale=4), nullable=True))
    op.add_column('configuracion_empresa', sa.Column('tipo_cambio_actualizado', sa.DateTime(), nullable=True))

    # 2. Update items_pedido safely
    # Add nivel_precio as nullable
    op.add_column('items_pedido', sa.Column('nivel_precio', sa.String(length=20), nullable=True))
    # Map tipo_tarifa to nivel_precio
    op.execute("UPDATE items_pedido SET nivel_precio = CASE WHEN tipo_tarifa = 'Docena' THEN 'Mayorista' WHEN tipo_tarifa = 'Menudeo' THEN 'Minorista' ELSE COALESCE(tipo_tarifa, 'Minorista') END")
    # Make it nullable=False
    op.alter_column('items_pedido', 'nivel_precio', nullable=False)
    # Drop tipo_tarifa
    op.drop_column('items_pedido', 'tipo_tarifa')
    # Add other columns
    op.add_column('items_pedido', sa.Column('precio_unitario_usd', sa.Numeric(precision=10, scale=2), nullable=True))
    op.add_column('items_pedido', sa.Column('precio_compra_unitario_usd', sa.Numeric(precision=10, scale=2), nullable=True))

    # 3. Update pedidos safely
    # Add nivel_precio as nullable
    op.add_column('pedidos', sa.Column('nivel_precio', sa.String(length=20), nullable=True))
    # Map tipo_tarifa to nivel_precio
    op.execute("UPDATE pedidos SET nivel_precio = CASE WHEN tipo_tarifa = 'Docena' THEN 'Mayorista' WHEN tipo_tarifa = 'Menudeo' THEN 'Minorista' ELSE COALESCE(tipo_tarifa, 'Minorista') END")
    # Make it nullable=False
    op.alter_column('pedidos', 'nivel_precio', nullable=False)
    # Drop tipo_tarifa
    op.drop_column('pedidos', 'tipo_tarifa')
    # Add other columns
    op.add_column('pedidos', sa.Column('metodo_envio_nombre', sa.String(length=100), nullable=True))
    op.add_column('pedidos', sa.Column('costo_envio', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0.00'))
    op.alter_column('pedidos', 'costo_envio', server_default=None)
    op.add_column('pedidos', sa.Column('tipo_cambio_aplicado', sa.Numeric(precision=10, scale=4), nullable=True))

    # 4. Update productos safely
    # Populate existing rows before altering nullable constraints
    op.execute("UPDATE productos SET precio_compra_usd = 0.00 WHERE precio_compra_usd IS NULL")
    op.execute("UPDATE productos SET precio_minorista_usd = COALESCE(precio_minorista, 0.00) WHERE precio_minorista_usd IS NULL")
    op.execute("UPDATE productos SET precio_mayorista_usd = COALESCE(precio_mayorista, 0.00) WHERE precio_mayorista_usd IS NULL")
    op.execute("UPDATE productos SET precio_franquicia_usd = COALESCE(precio_publico, 0.00) WHERE precio_franquicia_usd IS NULL")
    op.execute("UPDATE productos SET precio_asesora_libre_usd = COALESCE(precio_publico, 0.00) WHERE precio_asesora_libre_usd IS NULL")
    op.execute("UPDATE productos SET minorista_habilitado = TRUE WHERE minorista_habilitado IS NULL")
    op.execute("UPDATE productos SET mayorista_habilitado = TRUE WHERE mayorista_habilitado IS NULL")
    op.execute("UPDATE productos SET franquicia_habilitado = TRUE WHERE franquicia_habilitado IS NULL")
    op.execute("UPDATE productos SET asesora_libre_habilitado = TRUE WHERE asesora_libre_habilitado IS NULL")

    with op.batch_alter_table('productos', schema=None) as batch_op:
        batch_op.alter_column('precio_compra_usd',
               existing_type=sa.NUMERIC(precision=10, scale=2),
               nullable=False)
        batch_op.alter_column('tipo_cambio_al_comprar',
               existing_type=sa.NUMERIC(precision=10, scale=2),
               type_=sa.Numeric(precision=10, scale=4),
               existing_nullable=True)
        batch_op.alter_column('precio_minorista_usd',
               existing_type=sa.NUMERIC(precision=10, scale=2),
               nullable=False)
        batch_op.alter_column('precio_mayorista_usd',
               existing_type=sa.NUMERIC(precision=10, scale=2),
               nullable=False)
        batch_op.alter_column('precio_franquicia_usd',
               existing_type=sa.NUMERIC(precision=10, scale=2),
               nullable=False)
        batch_op.alter_column('precio_asesora_libre_usd',
               existing_type=sa.NUMERIC(precision=10, scale=2),
               nullable=False)
        batch_op.alter_column('minorista_habilitado',
               existing_type=sa.BOOLEAN(),
               nullable=False,
               existing_server_default=sa.text('true'))
        batch_op.alter_column('mayorista_habilitado',
               existing_type=sa.BOOLEAN(),
               nullable=False,
               existing_server_default=sa.text('true'))
        batch_op.alter_column('franquicia_habilitado',
               existing_type=sa.BOOLEAN(),
               nullable=False,
               existing_server_default=sa.text('true'))
        batch_op.alter_column('asesora_libre_habilitado',
               existing_type=sa.BOOLEAN(),
               nullable=False,
               existing_server_default=sa.text('true'))
        batch_op.drop_column('precio_minorista')
        batch_op.drop_column('precio_mayorista')
        batch_op.drop_column('precio_publico')


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('productos', schema=None) as batch_op:
        batch_op.add_column(sa.Column('precio_publico', sa.NUMERIC(precision=10, scale=2), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('precio_mayorista', sa.NUMERIC(precision=10, scale=2), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('precio_minorista', sa.NUMERIC(precision=10, scale=2), autoincrement=False, nullable=False))
        batch_op.alter_column('asesora_libre_habilitado',
               existing_type=sa.BOOLEAN(),
               nullable=True,
               existing_server_default=sa.text('true'))
        batch_op.alter_column('franquicia_habilitado',
               existing_type=sa.BOOLEAN(),
               nullable=True,
               existing_server_default=sa.text('true'))
        batch_op.alter_column('mayorista_habilitado',
               existing_type=sa.BOOLEAN(),
               nullable=True,
               existing_server_default=sa.text('true'))
        batch_op.alter_column('minorista_habilitado',
               existing_type=sa.BOOLEAN(),
               nullable=True,
               existing_server_default=sa.text('true'))
        batch_op.alter_column('precio_asesora_libre_usd',
               existing_type=sa.NUMERIC(precision=10, scale=2),
               nullable=True)
        batch_op.alter_column('precio_franquicia_usd',
               existing_type=sa.NUMERIC(precision=10, scale=2),
               nullable=True)
        batch_op.alter_column('precio_mayorista_usd',
               existing_type=sa.NUMERIC(precision=10, scale=2),
               nullable=True)
        batch_op.alter_column('precio_minorista_usd',
               existing_type=sa.NUMERIC(precision=10, scale=2),
               nullable=True)
        batch_op.alter_column('tipo_cambio_al_comprar',
               existing_type=sa.Numeric(precision=10, scale=4),
               type_=sa.NUMERIC(precision=10, scale=2),
               existing_nullable=True)
        batch_op.alter_column('precio_compra_usd',
               existing_type=sa.NUMERIC(precision=10, scale=2),
               nullable=True)

    with op.batch_alter_table('pedidos', schema=None) as batch_op:
        batch_op.add_column(sa.Column('tipo_tarifa', sa.VARCHAR(length=20), autoincrement=False, nullable=False))
        batch_op.drop_column('tipo_cambio_aplicado')
        batch_op.drop_column('costo_envio')
        batch_op.drop_column('metodo_envio_nombre')
        batch_op.drop_column('nivel_precio')

    with op.batch_alter_table('items_pedido', schema=None) as batch_op:
        batch_op.add_column(sa.Column('tipo_tarifa', sa.VARCHAR(length=20), autoincrement=False, nullable=False))
        batch_op.drop_column('nivel_precio')
        batch_op.drop_column('precio_compra_unitario_usd')
        batch_op.drop_column('precio_unitario_usd')

    with op.batch_alter_table('configuracion_empresa', schema=None) as batch_op:
        batch_op.drop_column('tipo_cambio_actualizado')
        batch_op.drop_column('tipo_cambio_usd')
        batch_op.drop_column('margen_ganancia_mayorista')

    # ### end Alembic commands ###
