from datetime import datetime
from flask_login import UserMixin
from app.extensions import db


class Rol(db.Model):
    """Roles del sistema.

    Personal interno: Gerente, Administrador, Empleado/Vendedor.
    Clientes externos: Cliente Publico, Cliente Minorista, Cliente Mayorista.
    Se usa una sola tabla de roles para simplificar `role_required` en ambos
    tipos de usuario (autenticación unificada vía Flask-Login).
    """
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    es_personal_interno = db.Column(db.Boolean, default=False, nullable=False)

    usuarios = db.relationship("Usuario", backref="rol", lazy=True)

    def __repr__(self):
        return f"<Rol {self.nombre}>"


class Usuario(db.Model, UserMixin):
    """Usuario unificado: personal interno (login con contraseña) y clientes
    externos (login sin contraseña vía OTP). El campo `password` es NULL
    para clientes externos.
    """
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    correo = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=True)  # NULL para clientes externos (OTP)
    telefono = db.Column(db.String(30), nullable=True)

    rol_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    activo = db.Column(db.Boolean, default=True, nullable=False)

    # Datos B2B (solo aplican a Cliente Minorista / Cliente Mayorista)
    nit_ci = db.Column(db.String(30), nullable=True)
    razon_social = db.Column(db.String(150), nullable=True)
    ciudad = db.Column(db.String(100), nullable=True)
    nivel_b2b_solicitado = db.Column(db.String(20), nullable=True)  # Minorista | Mayorista
    estado_aprobacion_b2b = db.Column(db.String(20), nullable=True)  # Pendiente | Aprobado | Rechazado

    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def tiene_rol(self, *nombres_rol):
        return self.rol is not None and self.rol.nombre in nombres_rol

    def es_cliente_externo(self):
        return self.rol is not None and not self.rol.es_personal_interno

    def __repr__(self):
        return f"<Usuario {self.correo}>"


class TokenOTP(db.Model):
    """Código de un solo uso enviado por correo para el login sin
    contraseña de los clientes externos.
    """
    __tablename__ = "tokens_otp"

    id = db.Column(db.Integer, primary_key=True)
    correo = db.Column(db.String(150), nullable=False, index=True)
    codigo = db.Column(db.String(6), nullable=False)
    expira_en = db.Column(db.DateTime, nullable=False)
    usado = db.Column(db.Boolean, default=False, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


# ---------------------------------------------------------------------------
# Categorías y Subcategorías (Fase 3)
# ---------------------------------------------------------------------------
class Categoria(db.Model):
    __tablename__ = "categorias"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    activo = db.Column(db.Boolean, default=True, nullable=False)

    subcategorias = db.relationship("Subcategoria", backref="categoria", lazy=True)
    productos = db.relationship("Producto", backref="categoria", lazy=True)

    def __repr__(self):
        return f"<Categoria {self.nombre}>"


class Subcategoria(db.Model):
    __tablename__ = "subcategorias"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categorias.id"), nullable=False)
    activo = db.Column(db.Boolean, default=True, nullable=False)

    productos = db.relationship("Producto", backref="subcategoria", lazy=True)

    __table_args__ = (db.UniqueConstraint("nombre", "categoria_id", name="uq_subcategoria_por_categoria"),)

    def __repr__(self):
        return f"<Subcategoria {self.nombre}>"


# ---------------------------------------------------------------------------
# Productos, tallas/stock y galería de fotos (Fase 3)
# ---------------------------------------------------------------------------
ESTADOS_PRODUCTO = ["Activo", "Inactivo", "En Oferta", "Seccion WOW"]
TALLAS_CALZADO = list(range(33, 46))  # 33 a 45


class Producto(db.Model):
    __tablename__ = "productos"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    sku = db.Column(db.String(50), unique=True, nullable=False, index=True)
    descripcion = db.Column(db.Text, nullable=True)

    categoria_id = db.Column(db.Integer, db.ForeignKey("categorias.id"), nullable=False)
    subcategoria_id = db.Column(db.Integer, db.ForeignKey("subcategorias.id"), nullable=True)

    # Matriz de precios multinivel (Bs.)
    precio_publico = db.Column(db.Numeric(10, 2), nullable=False)
    precio_minorista = db.Column(db.Numeric(10, 2), nullable=False)
    precio_mayorista = db.Column(db.Numeric(10, 2), nullable=False)

    estado = db.Column(db.String(20), default="Activo", nullable=False)

    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    creado_por_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)

    tallas = db.relationship(
        "ProductoTalla", backref="producto", lazy=True, cascade="all, delete-orphan",
        order_by="ProductoTalla.talla",
    )
    imagenes = db.relationship(
        "ProductoImagen", backref="producto", lazy=True, cascade="all, delete-orphan",
        order_by="ProductoImagen.orden",
    )

    @property
    def stock_total(self):
        return sum(t.stock for t in self.tallas)

    @property
    def imagen_principal(self):
        for img in self.imagenes:
            if img.es_principal:
                return img
        return self.imagenes[0] if self.imagenes else None

    def __repr__(self):
        return f"<Producto {self.sku} - {self.nombre}>"


class ProductoTalla(db.Model):
    """Desglose de stock por talla/número de calzado (33 a 45)."""
    __tablename__ = "producto_tallas"

    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey("productos.id"), nullable=False)
    talla = db.Column(db.Integer, nullable=False)
    stock = db.Column(db.Integer, default=0, nullable=False)

    __table_args__ = (db.UniqueConstraint("producto_id", "talla", name="uq_talla_por_producto"),)


class ProductoImagen(db.Model):
    """Foto del calzado; se permite carga múltiple con orden y una imagen
    marcada como principal (portada de la tarjeta/PDP)."""
    __tablename__ = "producto_imagenes"

    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey("productos.id"), nullable=False)
    ruta_archivo = db.Column(db.String(255), nullable=False)
    orden = db.Column(db.Integer, default=0, nullable=False)
    es_principal = db.Column(db.Boolean, default=False, nullable=False)


# ---------------------------------------------------------------------------
# Configuración de pago QR institucional (Fase 4)
# ---------------------------------------------------------------------------
class ConfiguracionPagoQR(db.Model):
    """Fila única con el QR institucional vigente para transferencias."""
    __tablename__ = "configuracion_pago_qr"

    id = db.Column(db.Integer, primary_key=True)
    ruta_imagen_qr = db.Column(db.String(255), nullable=True)
    nombre_beneficiario = db.Column(db.String(150), nullable=True)
    numero_cuenta = db.Column(db.String(50), nullable=True)
    banco = db.Column(db.String(100), nullable=True)


# ---------------------------------------------------------------------------
# Pedidos y checkout (Fase 4)
# ---------------------------------------------------------------------------
TIPOS_TARIFA = ["Menudeo", "Minorista", "Docena"]
ESTADOS_PEDIDO = ["Pendiente de verificación", "Pagado", "En preparación", "Entregado", "Rechazado"]
ENTREGAS = ["Envio", "Retiro en tienda"]


class ConfiguracionEmpresa(db.Model):
    """Datos institucionales usados en el encabezado de la Nota de Venta
    (formato AUDY): nombre comercial, dirección, NIT y celular."""
    __tablename__ = "configuracion_empresa"

    id = db.Column(db.Integer, primary_key=True)
    nombre_comercial = db.Column(db.String(100), default="NAHARA", nullable=False)
    direccion = db.Column(db.String(255), nullable=True)
    nit = db.Column(db.String(30), nullable=True)
    celular = db.Column(db.String(30), nullable=True)
    ciudad = db.Column(db.String(100), nullable=True)


class Pedido(db.Model):
    __tablename__ = "pedidos"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)

    tipo_tarifa = db.Column(db.String(20), nullable=False)  # Menudeo | Minorista | Docena
    tipo_entrega = db.Column(db.String(20), nullable=False, default="Retiro en tienda")
    direccion_envio = db.Column(db.String(255), nullable=True)
    nota = db.Column(db.Text, nullable=True)

    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    total = db.Column(db.Numeric(10, 2), nullable=False)

    comprobante_pago = db.Column(db.String(255), nullable=True)
    metodo_pago = db.Column(db.String(30), default="QR/Transferencia", nullable=False)
    estado = db.Column(db.String(30), default="Pendiente de verificación", nullable=False)

    numero_nota = db.Column(db.Integer, unique=True, nullable=True)
    verificado_por_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)
    fecha_verificacion = db.Column(db.DateTime, nullable=True)

    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    usuario = db.relationship("Usuario", foreign_keys=[usuario_id], backref="pedidos", lazy=True)
    verificado_por = db.relationship("Usuario", foreign_keys=[verificado_por_id], lazy=True)
    items = db.relationship("ItemPedido", backref="pedido", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Pedido #{self.id} - {self.estado}>"


class ItemPedido(db.Model):
    __tablename__ = "items_pedido"

    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedidos.id"), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey("productos.id"), nullable=False)

    nombre_producto = db.Column(db.String(150), nullable=False)  # copia histórica
    talla = db.Column(db.Integer, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    tipo_tarifa = db.Column(db.String(20), nullable=False, default="Menudeo")  # Menudeo | Minorista | Docena

    producto = db.relationship("Producto", lazy=True)
