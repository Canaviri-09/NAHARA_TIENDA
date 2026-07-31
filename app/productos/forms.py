from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, DecimalField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

from app.models_all import ESTADOS_PRODUCTO


class ProductoForm(FlaskForm):
    nombre = StringField("Nombre del producto", validators=[DataRequired(), Length(max=150)])
    sku = StringField("SKU / Código", validators=[DataRequired(), Length(max=50)])
    descripcion = TextAreaField("Descripción", validators=[Optional()])

    categoria_id = SelectField("Categoría", coerce=int, validators=[DataRequired()])
    subcategoria_id = SelectField("Subcategoría", coerce=int, validators=[Optional()])

    precio_publico = DecimalField("Precio Público / Par (Bs.)", places=2, validators=[DataRequired(), NumberRange(min=0)])
    precio_minorista = DecimalField("Precio Minorista (Bs.)", places=2, validators=[DataRequired(), NumberRange(min=0)])
    precio_mayorista = DecimalField("Precio Mayorista / Por Docena (Bs.)", places=2, validators=[DataRequired(), NumberRange(min=0)])

    estado = SelectField("Estado", choices=[(e, e) for e in ESTADOS_PRODUCTO], validators=[DataRequired()])

    submit = SubmitField("Guardar producto")
