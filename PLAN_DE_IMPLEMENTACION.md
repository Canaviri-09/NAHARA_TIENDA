# PROMPT DE INICIALIZACIÓN: PROYECTO E-COMMERCE Y PANEL DE CONTROL INTEGRADO "NAHARA"

## 1. OBJETIVO CLARO
Desarrolla el backend (API REST Modular) y el frontend integrado mediante vistas/plantillas para el proyecto **"NAHARA"** (Sistema de E-Commerce y Panel de Control Administrativo Interno). 
El sistema gestionará ventas de calzado a nivel público (B2C Menudeo), minoristas B2B (ventas por cuarta docena) y mayoristas B2B (ventas por docena o mas de una docena), incluyendo pasarela de pago por QR/transferencia, generación automática de Notas de Venta en PDF (formato estandarizado) y reportes de ventas e ingresos.

## 2. ESTRUCTURA DE CARPETAS OBJETIVO

```text
app/
├── auth/          (templates/auth/, models.py, routes.py -> Login OTP, Registro B2C y B2B)
├── usuarios/      (templates/usuarios/, models.py, routes.py -> Personal interno y aprobaciones)
├── productos/     (templates/productos/, models.py, routes.py -> CRUD, fotos y 3 niveles de precios)
├── categorias/    (templates/categorias/, models.py, routes.py -> Categorías y Subcategorías)
├── cupones/       (templates/cupones/, models.py, routes.py -> Cupones y reglas de descuento)
├── tienda/        (templates/tienda/, routes.py -> Catálogo, PDP, Carrito, Auto-descuento docenas)
├── pedidos/       (templates/pedidos/, models.py, routes.py -> Checkout, Pago QR, Comprobantes)
├── notas_venta/   (templates/notas_venta/, utils_pdf.py -> Generador PDF borrador AUDY)
├── reportes/      (templates/reportes/, routes.py -> Ventas/ingresos filtrados)
├── banners/       (templates/banners/, models.py, routes.py -> Banners y avisos top)
├── sucursales/    (templates/sucursales/, models.py, routes.py -> Puntos de retiro)
└── dashboard/     (templates/dashboard/, routes.py -> Métricas y alertas iniciales)

