import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  // En emulador Android, 10.0.2.2 apunta al localhost de la máquina de desarrollo.
  // Cambiar a la IP local de tu servidor en red física si pruebas en dispositivo real.
  static const String baseUrl = 'http://10.0.2.2:5000/api';

  String? _token;

  void setToken(String? token) {
    _token = token;
  }

  Map<String, String> _getHeaders() {
    final headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
    if (_token != null) {
      headers['Authorization'] = 'Bearer $_token';
    }
    return headers;
  }

  // --- MÉTODOS DE AUTENTICACIÓN ---

  Future<Map<String, dynamic>> registrar({
    required String nombre,
    required String correo,
    required String telefono,
    required String password,
    required String tipoCliente,
    String? ciudad,
    String? nitCi,
    String? razonSocial,
  }) async {
    final url = Uri.parse('$baseUrl/auth/registro');
    final cuerpo = {
      'nombre': nombre,
      'correo': correo,
      'telefono': telefono,
      'password': password,
      'tipo_cliente': tipoCliente,
      'ciudad': ciudad,
      'nit_ci': nitCi,
      'razon_social': razonSocial,
    };

    try {
      final respuesta = await http.post(
        url,
        headers: _getHeaders(),
        body: json.encode(cuerpo),
      );
      return json.decode(respuesta.body) as Map<String, dynamic>;
    } catch (e) {
      return {'error': 'Error de conexión: $e'};
    }
  }

  Future<Map<String, dynamic>> solicitarOtp(String telefono) async {
    final url = Uri.parse('$baseUrl/auth/solicitar-otp');
    try {
      final respuesta = await http.post(
        url,
        headers: _getHeaders(),
        body: json.encode({'telefono': telefono}),
      );
      return json.decode(respuesta.body) as Map<String, dynamic>;
    } catch (e) {
      return {'error': 'Error de conexión: $e'};
    }
  }

  Future<Map<String, dynamic>> verificarOtp(String telefono, String codigo) async {
    final url = Uri.parse('$baseUrl/auth/verificar-otp');
    try {
      final respuesta = await http.post(
        url,
        headers: _getHeaders(),
        body: json.encode({'telefono': telefono, 'codigo': codigo}),
      );
      return json.decode(respuesta.body) as Map<String, dynamic>;
    } catch (e) {
      return {'error': 'Error de conexión: $e'};
    }
  }

  Future<Map<String, dynamic>> loginConTelefono(String telefono, String password) async {
    final url = Uri.parse('$baseUrl/auth/login-telefono');
    try {
      final respuesta = await http.post(
        url,
        headers: _getHeaders(),
        body: json.encode({'telefono': telefono, 'password': password}),
      );
      return json.decode(respuesta.body) as Map<String, dynamic>;
    } catch (e) {
      return {'error': 'Error de conexión: $e'};
    }
  }

  Future<Map<String, dynamic>> loginConGoogle({
    required String correo,
    required String nombre,
    required String googleId,
  }) async {
    final url = Uri.parse('$baseUrl/auth/google');
    final cuerpo = {
      'correo': correo,
      'nombre': nombre,
      'google_id': googleId,
    };
    try {
      final respuesta = await http.post(
        url,
        headers: _getHeaders(),
        body: json.encode(cuerpo),
      );
      return json.decode(respuesta.body) as Map<String, dynamic>;
    } catch (e) {
      return {'error': 'Error de conexión: $e'};
    }
  }

  // --- MÉTODOS DE PEDIDOS ---

  Future<Map<String, dynamic>> obtenerMisPedidos() async {
    final url = Uri.parse('$baseUrl/pedidos/mis-pedidos');
    try {
      final respuesta = await http.get(
        url,
        headers: _getHeaders(),
      );
      return json.decode(respuesta.body) as Map<String, dynamic>;
    } catch (e) {
      return {'error': 'Error de conexión: $e'};
    }
  }

  Future<Map<String, dynamic>> obtenerTrackingPedido(int pedidoId) async {
    final url = Uri.parse('$baseUrl/pedidos/$pedidoId/tracking');
    try {
      final respuesta = await http.get(
        url,
        headers: _getHeaders(),
      );
      return json.decode(respuesta.body) as Map<String, dynamic>;
    } catch (e) {
      return {'error': 'Error de conexión: $e'};
    }
  }
}
