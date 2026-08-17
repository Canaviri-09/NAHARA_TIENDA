import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:nahara_flutter/providers/auth_provider.dart';
import 'package:nahara_flutter/widgets/custom_button.dart';
import 'package:nahara_flutter/screens/orders/order_list_screen.dart';

class OtpVerificationScreen extends StatefulWidget {
  final String telefono;

  const OtpVerificationScreen({super.key, required this.telefono});

  @override
  State<OtpVerificationScreen> createState() => _OtpVerificationScreenState();
}

class _OtpVerificationScreenState extends State<OtpVerificationScreen> {
  final List<TextEditingController> _controllers = List.generate(6, (_) => TextEditingController());
  final List<FocusNode> _focusNodes = List.generate(6, (_) => FocusNode());

  @override
  void dispose() {
    for (var controller in _controllers) {
      controller.dispose();
    }
    for (var focusNode in _focusNodes) {
      focusNode.dispose();
    }
    super.dispose();
  }

  String _getOtpCode() {
    return _controllers.map((c) => c.text).join();
  }

  void _verify() async {
    final codigo = _getOtpCode();
    if (codigo.length < 6) return;

    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final exito = await authProvider.verifyOtp(widget.telefono, codigo);

    if (exito && mounted) {
      Navigator.pushAndRemoveUntil(
        context,
        MaterialPageRoute(builder: (_) => const OrderListScreen()),
        (route) => false,
      );
    }
  }

  void _reenviarOtp() async {
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final exito = await authProvider.requestOtp(widget.telefono);
    if (exito && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Código OTP reenviado con éxito.')),
      );
      // Limpiar y resetear foco
      for (var controller in _controllers) {
        controller.clear();
      }
      _focusNodes[0].requestFocus();
    }
  }

  @override
  Widget build(BuildContext context) {
    final authProvider = Provider.watch<AuthProvider>(context);

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: const Text('Verificar Cuenta', style: TextStyle(color: Color(0xFF1E293B), fontWeight: FontWeight.bold)),
        backgroundColor: Colors.white,
        elevation: 0,
        iconTheme: const IconThemeData(color: Color(0xFF1E293B)),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 32.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              const Icon(
                Icons.security_outlined,
                size: 80,
                color: Color(0xFF1E3A8A),
              ),
              const SizedBox(height: 24),
              const Text(
                'Código de Verificación',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF1E293B),
                ),
              ),
              const SizedBox(height: 12),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16.0),
                child: Text(
                  'Hemos enviado un código OTP de 6 dígitos al WhatsApp / Móvil del número:\n+${widget.telefono}',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey.shade600,
                    height: 1.5,
                  ),
                ),
              ),
              const SizedBox(height: 36),

              // Inputs de 6 celdas
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: List.generate(6, (index) {
                  return SizedBox(
                    width: 48,
                    height: 56,
                    child: TextFormField(
                      controller: _controllers[index],
                      focusNode: _focusNodes[index],
                      keyboardType: TextInputType.number,
                      textAlign: TextAlign.center,
                      maxLength: 1,
                      style: const TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF1E293B),
                      ),
                      decoration: InputDecoration(
                        counterText: '',
                        filled: true,
                        fillColor: Colors.grey.shade50,
                        contentPadding: EdgeInsets.zero,
                        enabledBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                          borderSide: BorderSide(color: Colors.grey.shade200, width: 1.5),
                        ),
                        focusedBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                          borderSide: const BorderSide(color: Color(0xFF3B82F6), width: 2.5),
                        ),
                      ),
                      onChanged: (value) {
                        if (value.isNotEmpty) {
                          if (index < 5) {
                            _focusNodes[index + 1].requestFocus();
                          } else {
                            _focusNodes[index].unfocus();
                          }
                        } else {
                          if (index > 0) {
                            _focusNodes[index - 1].requestFocus();
                          }
                        }
                        setState(() {}); // Actualiza estado para habilitar botón
                      },
                    ),
                  );
                }),
              ),
              const SizedBox(height: 32),

              // Mensaje de Error del Servidor
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
                    textAlign: TextAlign.center,
                    style: TextStyle(color: Colors.red.shade700, fontSize: 13, fontWeight: FontWeight.w500),
                  ),
                ),
                const SizedBox(height: 24),
              ],

              // Botón Verificar
              CustomButton(
                text: 'Confirmar Código',
                onPressed: _getOtpCode().length == 6 ? _verify : null,
                isLoading: authProvider.isLoading,
              ),
              const SizedBox(height: 24),

              // Botón de reenvío
              TextButton(
                onPressed: authProvider.isLoading ? null : _reenviarOtp,
                child: const Text(
                  '¿No recibiste el código? Reenviar OTP',
                  style: TextStyle(
                    color: Color(0xFF3B82F6),
                    fontWeight: FontWeight.bold,
                    fontSize: 14,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
