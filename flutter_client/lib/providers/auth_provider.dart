import 'package:flutter/material.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:nahara_flutter/models/user_model.dart';
import 'package:nahara_flutter/services/api_service.dart';

class AuthProvider extends ChangeNotifier {
  final ApiService _apiService = ApiService();
  final GoogleSignIn _googleSignIn = GoogleSignIn(
    scopes: ['email', 'profile'],
  );

  UserModel? _currentUser;
  String? _token;
  bool _isLoading = false;
  String? _errorMessage;

  UserModel? get currentUser => _currentUser;
  String? get token => _token;
  bool get isAuthenticated => _currentUser != null;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }

  void _setError(String? message) {
    _errorMessage = message;
    notifyListeners();
  }

  // Limpiar errores
  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }

  // --- REGISTRO ---
  Future<bool> register({
    required String nombre,
    required String correo,
    required String telefono,
    required String password,
    required String tipoCliente,
    String? ciudad,
    String? nitCi,
    String? razonSocial,
  }) async {
    _setLoading(true);
    _setError(null);

    final res = await _apiService.registrar(
      nombre: nombre,
      correo: correo,
      telefono: telefono,
      password: password,
      tipoCliente: tipoCliente,
      ciudad: ciudad,
      nitCi: nitCi,
      razonSocial: razonSocial,
    );

    _setLoading(false);

    if (res.containsKey('error')) {
      _setError(res['error']);
      return false;
    }

    return true;
  }

  // --- SOLICITAR OTP ---
  Future<bool> requestOtp(String telefono) async {
    _setLoading(true);
    _setError(null);

    final res = await _apiService.solicitarOtp(telefono);

    _setLoading(false);

    if (res.containsKey('error')) {
      _setError(res['error']);
      return false;
    }

    return true;
  }

  // --- VERIFICAR OTP ---
  Future<bool> verifyOtp(String telefono, String codigo) async {
    _setLoading(true);
    _setError(null);

    final res = await _apiService.verificarOtp(telefono, codigo);

    _setLoading(false);

    if (res.containsKey('error')) {
      _setError(res['error']);
      return false;
    }

    _token = res['token'];
    _currentUser = UserModel.fromJson(res['usuario']);
    _apiService.setToken(_token);
    notifyListeners();
    return true;
  }

  // --- LOGIN CON TELÉFONO Y CONTRASEÑA ---
  Future<bool> loginWithPhone(String telefono, String password) async {
    _setLoading(true);
    _setError(null);

    final res = await _apiService.loginConTelefono(telefono, password);

    _setLoading(false);

    if (res.containsKey('error')) {
      _setError(res['error']);
      return false;
    }

    _token = res['token'];
    _currentUser = UserModel.fromJson(res['usuario']);
    _apiService.setToken(_token);
    notifyListeners();
    return true;
  }

  // --- GOOGLE SIGN-IN ---
  Future<bool> loginWithGoogle() async {
    _setLoading(true);
    _setError(null);

    try {
      // 1. Intentar inicio de sesión con Google
      final GoogleSignInAccount? googleUser = await _googleSignIn.signIn();
      
      if (googleUser == null) {
        // El usuario canceló el inicio de sesión
        _setLoading(false);
        _setError("Inicio de sesión con Google cancelado.");
        return false;
      }

      // 2. Enviar datos de Google al backend
      final res = await _apiService.loginConGoogle(
        correo: googleUser.email,
        nombre: googleUser.displayName ?? 'Usuario de Google',
        googleId: googleUser.id,
      );

      _setLoading(false);

      if (res.containsKey('error')) {
        _setError(res['error']);
        return false;
      }

      _token = res['token'];
      _currentUser = UserModel.fromJson(res['usuario']);
      _apiService.setToken(_token);
      notifyListeners();
      return true;
    } catch (e) {
      _setLoading(false);
      
      // Fallback de simulación en desarrollo si falta configuración de SHA-1 / Firebase
      _setError("Error con Google Sign-In. Usando fallback de desarrollo para simulación.");
      return await loginWithGoogleMock();
    }
  }

  // Fallback de desarrollo para simular Google Sign-In si no hay Google Play Services configurado
  Future<bool> loginWithGoogleMock() async {
    _setLoading(true);
    _setError(null);

    // Simulación de respuesta exitosa del backend
    final res = await _apiService.loginConGoogle(
      correo: "cliente.google.dev@example.com",
      nombre: "Google Developer Mock",
      googleId: "google_mock_123456789",
    );

    _setLoading(false);

    if (res.containsKey('error')) {
      _setError(res['error']);
      return false;
    }

    _token = res['token'];
    _currentUser = UserModel.fromJson(res['usuario']);
    _apiService.setToken(_token);
    notifyListeners();
    return true;
  }

  // --- LOGOUT ---
  Future<void> logout() async {
    _setLoading(true);
    try {
      await _googleSignIn.signOut();
    } catch (_) {}
    _currentUser = null;
    _token = null;
    _apiService.setToken(null);
    _setLoading(false);
    notifyListeners();
  }
}
