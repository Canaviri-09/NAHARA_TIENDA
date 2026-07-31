# PROMPT DE INICIALIZACIÓN: PROYECTO E-COMMERCE Y PANEL DE CONTROL INTEGRADO "NAHARA"

## 1. OBJETIVO CLARO
Desarrolla el backend (API REST Modular) y el frontend integrado mediante vistas/plantillas para el proyecto **"NAHARA"** (Sistema de E-Commerce y Panel de Control Administrativo Interno). 
El sistema gestionará ventas de calzado a nivel público (B2C Menudeo), minoristas B2B (ventas por cuarta docena) y mayoristas B2B (ventas por docena o mas de una docena), incluyendo pasarela de pago por QR/transferencia, generación automática de Notas de Venta en PDF (formato estandarizado) y reportes de ventas e ingresos.

---

## 2. ESPECIFICACIONES TÉCNICAS Y ARQUITECTURA
* **Lenguaje y Framework:** Python con Flask (API REST Modular).
* **Arquitectura:** Flask Blueprints. Cada módulo debe tener su propio subdirectorio con su `__init__.py`, `routes.py`, `models.py` y carpeta interna de vistas `templates/` (patrón de vistas modulares).
* **Base de Datos (CONFIRMADO):** PostgreSQL desde el día 1 (Docker local o servicio administrado como Supabase/Render). **NUNCA SQLite**, ni siquiera en desarrollo, para evitar incompatibilidades de tipos de datos, llaves foráneas y JSON al migrar a la nube. Flask-SQLAlchemy con la cadena de conexión leída de la variable de entorno `DATABASE_URL` en `config.py`, de modo que cambie automáticamente entre entorno local y nube.
* **Seguridad y Control de Acceso (CONFIRMADO):** Flask-Login basado en sesiones/cookies (`HttpOnly`, `SameSite`) — no JWT, por ser un sistema de vistas HTML integradas (Blueprints + Bootstrap):
  - **Personal interno** (Gerente, Administrador, Empleado/Vendedor): inicia sesión con correo/usuario y contraseña hasheada (`werkzeug.security` o `bcrypt`).
  - **Clientes Externos** (Público, Minorista, Mayorista): inician sesión mediante token OTP de 6 dígitos enviado por correo; al validarse, se ejecuta `login_user()` igual que el personal interno.
  - Control de acceso mediante decoradores personalizados por rol (ej. `requiere_rol('GERENTE')`, `cliente_aprobado_b2b`).
  - **Gerente & Administrador:** Control total del sistema, aprobación de cuentas B2B, gestión de personal.
  - **Empleado / Vendedor:** CRUD de productos, 3 niveles de precios, carga de fotografías, gestión de pedidos, cambio de estados, emisión de Notas de Venta (PDF) y generación de reportes.
  - **Cliente Externo (Público, Minorista, Mayorista):** Registro OTP sin contraseña, compras web, subida de comprobante QR y consulta de su historial. Sin acceso de modificación o edición en la web.
* **Frontend:** HTML5 estandarizado con Bootstrap básico.
  - **REGLA DE DISEÑO:** Mantener el diseño **limpio y ordenado** como el archivo borrador HTML subido, respetando los colores, tipografía, estructura y componentes de las referencias visuales del borrador subido.
  - **Internacionalización (CONFIRMADO):** El selector regional del header (idioma/moneda) NO debe estar hardcodeado solo a español/bolivianos; debe construirse como una lista configurable de idiomas y monedas (aunque por defecto arranque con ES/BOB).
* **Librerías Adicionales:** 
  - `ReportLab` o `WeasyPrint` para la generación dinámica de la **Nota de Venta en PDF** (siguiendo estrictamente la plantilla AUDY/NAHARA).
  - Manejo de exportación a Excel para el módulo de reportes con fecha y hora incluida.

---

## 3. ESTRUCTURA DE CARPETAS OBJETIVO

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

## 4. CONTEXTO Y ARCHIVOS ADJUNTOS DE REFERENCIA
Para garantizar la precisión en el desarrollo, debes leer y basarte en los siguientes archivos adjuntos:

Definicion_del_proyecto_NAHARA.txt: Contiene la especificación completa del sistema, los 3 niveles de precio (Público, Minorista, Docena), los flujos de uso, los actores y la estructura de la Nota de Venta en PDF.

Diseño_Borrador.html: Referencia para el maquetado visual del frontend. Conservar la paleta de colores, botones, cajas de entrada e imágenes, aplicando Bootstrap de forma simple sin iconos.

Archivos de Referencia de Código (Proyecto Anterior): Tomar como guía de estilo de código, buenas prácticas de desarrollo modular, manejo de seguridad y gestión de base de datos.

## 5. REGLAS DE EJECUCIÓN PASO A PASO
Análisis Preliminar: Lee detalladamente la especificación funcional completa (Definicion_del_proyecto_NAHARA.txt), el HTML borrador de referencia y los archivos de código del proyecto anterior.

Plan de Implementación: Crea de forma obligatoria un archivo PLAN_DE_IMPLEMENTACION.md desglosando las fases de desarrollo incremental. NO comiences a programar rutas ni vistas hasta que congele y apruebe este plan en la terminal contigo.

Desarrollo Incremental y Modular: Desarrolla módulo por módulo. No programes múltiples módulos en paralelo. El orden será:

Fase 1: Configuración base (run.py, config.py, app/__init__.py) y modelos base.

Fase 2: Autenticación OTP y Gestión de Usuarios/Personal con matriz de roles.

Fase 3: Módulo de Productos (CRUD, subida de imágenes, 3 niveles de precios).

Fase 4: Tienda, Catálogo, Carrito con Auto-descuento por docena y Checkout QR.

Fase 5: Gestión de Pedidos, Verificación QR, Notificaciones y Generación de PDF (Nota de Venta).

Fase 6: Módulo de Reportes de Ventas e Ingresos (Gerente/Empleados).

Control de Dependencias: No instales paquetes ni dependencias externas en requirements.txt sin pedir aprobación previa explícita en la terminal.

Reglas de Negocio Clave:

Si un usuario introduce 12 o más unidades de un mismo calzado al carrito, el sistema debe recalcular dinámicamente el precio al Precio Mayorista / Por Docena.

Los Clientes Externos NO pueden modificar precios ni la estructura del sitio.

Mantener el diseño limpio, ordenado y SIN ICONOS utilizando únicamente componentes básicos de Bootstrap.