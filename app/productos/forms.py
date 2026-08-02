from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, DecimalField, IntegerField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class ProductoForm(FlaskForm):
    nombre = StringField("Nombre del producto", validators=[DataRequired(), Length(max=150)])
    sku = StringField("SKU / Código", validators=[DataRequired(), Length(max=50)])
    descripcion = TextAreaField("Descripción", validators=[Optional()])

    categoria_id = SelectField("Categoría", coerce=int, validators=[DataRequired()])
    subcategoria_id = SelectField("Subcategoría", coerce=int, validators=[Optional()])

    precio_publico = DecimalField("Precio Público (Bs.)", places=2, validators=[DataRequired(), NumberRange(min=0)])
    precio_minorista = DecimalField("Precio Minorista (Bs.)", places=2, validators=[DataRequired(), NumberRange(min=0)])
    precio_mayorista = DecimalField("Precio Mayorista / Por Docena (Bs.)", places=2, validators=[DataRequired(), NumberRange(min=0)])

    stock = IntegerField("Stock", validators=[DataRequired(), NumberRange(min=0)])

    # Visibilidad: si está desmarcado, solo el personal interno lo ve (como "Inactivo")
    activo = BooleanField("Activo (visible para clientes)", default=True)

    # Banderas de estado combinables. "Nuevo" no está aquí: se calcula
    # solo durante los primeros 30 días desde la creación del producto.
    es_destacado = BooleanField("Destacado")
    en_oferta = BooleanField("En oferta")
    porcentaje_descuento = DecimalField(
        "% de descuento", places=2, validators=[Optional(), NumberRange(min=0, max=95)]
    )

    submit = SubmitField("Guardar producto")
