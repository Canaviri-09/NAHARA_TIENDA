import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:nahara_flutter/providers/auth_provider.dart';
import 'package:nahara_flutter/widgets/custom_button.dart';
import 'package:nahara_flutter/widgets/custom_text_field.dart';
import 'package:nahara_flutter/screens/auth/otp_verification_screen.dart';
import 'package:nahara_flutter/screens/orders/order_list_screen.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nombreController = TextEditingController();
  final _correoController = TextEditingController();
  final _telefonoController = TextEditingController();
  final _passwordController = TextEditingController();
  
  // Campos B2B / Mayorista
  final _nitCiController = TextEditingController();
  final _razonSocialController = TextEditingController();
  final _ciudadController = TextEditingController();

  String _tipoCliente = 'Publico'; // 'Publico' | 'Mayorista'

  @override
  void dispose() {
    _nombreController.dispose();
    _correoController.dispose();
    _telefonoController.dispose();
    _passwordController.dispose();
    _nitCiController.dispose();
    _razonSocialController.dispose();
    _ciudadController.dispose();
    super.dispose();
  }

  void _submit() async {
    if (!_formKey.currentState!.validate()) return;

    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    
    // 1. Registrar usuario en el backend
    final exitoRegistro = await authProvider.register(
      nombre: _nombreController.text,
      correo: _correoController.text,
      telefono: _telefonoController.text,
      password: _passwordController.text,
      tipoCliente: _tipoCliente,
      ciudad: _tipoCliente == 'Mayorista' ? _ciudadController.text : null,
      nitCi: _tipoCliente == 'Mayorista' ? _nitCiController.text : null,
      razonSocial: _tipoCliente == 'Mayorista' ? _razonSocialController.text : null,
    );

    if (exitoRegistro) {
      if (_tipoCliente == 'Mayorista') {
        // Al ser mayorista B2B, la cuenta requiere aprobación de administración.
        // Mostramos un diálogo y regresamos o permitimos validación.
        _mostrarDialogoMayorista();
      } else {
        // Enviar OTP telefónico para confirmación de cuenta de WhatsApp
        final exitoOtp = await authProvider.requestOtp(_telefonoController.text);
        if (exitoOtp && mounted) {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (_) => OtpVerificationScreen(telefono: _telefonoController.text),
            ),
          );
        }
      }
    }
  }

  void _mostrarDialogoMayorista() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Row(
          children: [
            Icon(Icons.info_outline, color: Color(0xFF1E3A8A)),
            SizedBox(width: 10),
            Text('Registro Recibido'),
          ],
        ),
        content: const Text(
          'Tu solicitud de cuenta Mayorista ha sido enviada. El administrador revisará tu información (NIT/CI y Razón Social) y habilitará tu acceso en las próximas horas.',
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(ctx);
              // Limpiar formulario o regresar a login
              Navigator.pop(context);
            },
            child: const Text('Entendido', style: TextStyle(color: Color(0xFF1E3A8A), fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
  }

  void _loginConGoogle() async {
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final exito = await authProvider.loginWithGoogle();
    if (exito && mounted) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => const OrderListScreen()),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final authProvider = Provider.watch<AuthProvider>(context);

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: const Text('Crear Cuenta', style: TextStyle(color: Color(0xFF1E293B), fontWeight: FontWeight.bold)),
        backgroundColor: Colors.white,
        elevation: 0,
        iconTheme: const IconThemeData(color: Color(0xFF1E293B)),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Únete a NAHARA',
                  style: TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF1E3A8A),
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Regístrate para comprar las mejores mochilas del mercado.',
                  style: TextStyle(fontSize: 14, color: Colors.grey.shade600),
                ),
                const SizedBox(height: 24),

                // Selector de Rol (Público vs Mayorista)
                Container(
                  padding: const EdgeInsets.all(4),
                  decoration: BoxDecoration(
                    color: Colors.grey.shade100,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Row(
                    children: [
                      Expanded(
                        child: GestureDetector(
                          onTap: () => setState(() => _tipoCliente = 'Publico'),
                          child: Container(
                            padding: const EdgeInsets.symmetric(vertical: 12),
                            decoration: BoxDecoration(
                              color: _tipoCliente == 'Publico' ? Colors.white : Colors.transparent,
                              borderRadius: BorderRadius.circular(10),
                              boxShadow: _tipoCliente == 'Publico'
                                  ? [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 4, offset: const Offset(0, 2))]
                                  : null,
                            ),
                            alignment: Alignment.center,
                            child: Text(
                              'Público General',
                              style: TextStyle(
                                fontWeight: FontWeight.bold,
                                color: _tipoCliente == 'Publico' ? const Color(0xFF1E3A8A) : Colors.grey.shade600,
                              ),
                            ),
                          ),
                        ),
                      ),
                      Expanded(
                        child: GestureDetector(
                          onTap: () => setState(() => _tipoCliente = 'Mayorista'),
                          child: Container(
                            padding: const EdgeInsets.symmetric(vertical: 12),
                            decoration: BoxDecoration(
                              color: _tipoCliente == 'Mayorista' ? Colors.white : Colors.transparent,
                              borderRadius: BorderRadius.circular(10),
                              boxShadow: _tipoCliente == 'Mayorista'
                                  ? [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 4, offset: const Offset(0, 2))]
                                  : null,
                            ),
                            alignment: Alignment.center,
                            child: Text(
                              'Mayorista (B2B)',
                              style: TextStyle(
                                fontWeight: FontWeight.bold,
                                color: _tipoCliente == 'Mayorista' ? const Color(0xFF1E3A8A) : Colors.grey.shade600,
                              ),
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),

                // Campos comunes
                CustomTextField(
                  controller: _nombreController,
                  labelText: 'Nombre Completo',
                  prefixIcon: Icons.person_outline,
                  validator: (val) => val == null || val.trim().isEmpty ? 'Ingresa tu nombre' : null,
                ),
                const SizedBox(height: 16),
                CustomTextField(
                  controller: _correoController,
                  labelText: 'Correo Electrónico',
                  keyboardType: TextInputType.emailAddress,
                  prefixIcon: Icons.email_outlined,
                  validator: (val) {
                    if (val == null || val.trim().isEmpty) return 'Ingresa tu correo';
                    if (!RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$').hasMatch(val)) {
                      return 'Correo electrónico no válido';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 16),
                CustomTextField(
                  controller: _telefonoController,
                  labelText: 'Teléfono / WhatsApp',
                  keyboardType: TextInputType.phone,
                  prefixIcon: Icons.phone_outlined,
                  validator: (val) {
                    if (val == null || val.trim().isEmpty) return 'Ingresa tu teléfono';
                    if (val.trim().length < 8) return 'Teléfono muy corto';
                    return null;
                  },
                ),
                const SizedBox(height: 16),
                CustomTextField(
                  controller: _passwordController,
                  labelText: 'Contraseña',
                  isPassword: true,
                  prefixIcon: Icons.lock_outline,
                  validator: (val) => val == null || val.length < 6 ? 'Mínimo 6 caracteres' : null,
                ),
                const SizedBox(height: 16),

                // Campos Condicionales de Mayorista B2B
                if (_tipoCliente == 'Mayorista') ...[
                  const Divider(height: 32),
                  const Text(
                    'Información de Mayorista',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF1E3A8A)),
                  ),
                  const SizedBox(height: 16),
                  CustomTextField(
                    controller: _nitCiController,
                    labelText: 'NIT / CI',
                    prefixIcon: Icons.badge_outlined,
                    validator: (val) => val == null || val.trim().isEmpty ? 'NIT o CI obligatorio para mayorista' : null,
                  ),
                  const SizedBox(height: 16),
                  CustomTextField(
                    controller: _razonSocialController,
                    labelText: 'Razón Social / Nombre Comercial',
                    prefixIcon: Icons.business_outlined,
                    validator: (val) => val == null || val.trim().isEmpty ? 'Razón social obligatoria para mayorista' : null,
                  ),
                  const SizedBox(height: 16),
                  CustomTextField(
                    controller: _ciudadController,
                    labelText: 'Ciudad',
                    prefixIcon: Icons.location_city_outlined,
                    validator: (val) => val == null || val.trim().isEmpty ? 'Especifica tu ciudad' : null,
                  ),
                  const SizedBox(height: 16),
                ],

                // Mensaje de Error
                if (authProvider.errorMessage != null) ...[
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.red.shade50,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      authProvider.errorMessage!,
                      style: TextStyle(color: Colors.red.shade700, fontSize: 13, fontWeight: FontWeight.w500),
                    ),
                  ),
                  const SizedBox(height: 16),
                ],

                // Botón de Envío
                CustomButton(
                  text: _tipoCliente == 'Mayorista' ? 'Solicitar Cuenta Mayorista' : 'Registrarse y Validar Teléfono',
                  onPressed: _submit,
                  isLoading: authProvider.isLoading,
                ),
                const SizedBox(height: 20),

                // Separador o "Registrarse con Google"
                const Row(
                  children: [
                    Expanded(child: Divider()),
                    Padding(
                      padding: EdgeInsets.symmetric(horizontal: 16.0),
                      child: Text('o', style: TextStyle(color: Colors.grey)),
                    ),
                    Expanded(child: Divider()),
                  ],
                ),
                const SizedBox(height: 20),

                // Botón Google Sign-In
                OutlinedButton(
                  onPressed: authProvider.isLoading ? null : _loginConGoogle,
                  style: OutlinedButton.styleFrom(
                    minimumSize: const Size(double.infinity, 52),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    side: BorderSide(color: Colors.grey.shade300),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Image.network(
                        'https://upload.wikimedia.org/wikipedia/commons/c/c1/Google_%22G%22_logo.svg',
                        height: 20,
                        width: 20,
                        errorBuilder: (_, __, ___) => const Icon(Icons.g_mobiledata, color: Colors.blue, size: 28),
                      ),
                      const SizedBox(width: 12),
                      const Text(
                        'Registrarse con Google',
                        style: TextStyle(
                          color: Color(0xFF1E293B),
                          fontWeight: FontWeight.bold,
                          fontSize: 15,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
