import 'package:flutter/material.dart';
import 'package:nahara_flutter/models/order_model.dart';
import 'package:nahara_flutter/services/api_service.dart';

class OrderProvider extends ChangeNotifier {
  final ApiService _apiService = ApiService();

  List<OrderModel> _orders = [];
  OrderModel? _selectedOrderTracking;
  bool _isLoadingOrders = false;
  bool _isLoadingTracking = false;
  String? _errorMessage;

  List<OrderModel> get orders => _orders;
  OrderModel? get selectedOrderTracking => _selectedOrderTracking;
  bool get isLoadingOrders => _isLoadingOrders;
  bool get isLoadingTracking => _isLoadingTracking;
  String? get errorMessage => _errorMessage;

  void clearTracking() {
    _selectedOrderTracking = null;
    notifyListeners();
  }

  // --- OBTENER LISTA DE PEDIDOS ---
  Future<void> fetchOrders() async {
    _isLoadingOrders = true;
    _errorMessage = null;
    notifyListeners();

    final res = await _apiService.obtenerMisPedidos();

    _isLoadingOrders = false;

    if (res.containsKey('error')) {
      _errorMessage = res['error'];
    } else if (res['success'] == true) {
      final list = res['pedidos'] as List;
      _orders = list.map((json) => OrderModel.fromJson(json as Map<String, dynamic>)).toList();
    } else {
      _errorMessage = 'Ocurrió un error al obtener la lista de pedidos.';
    }

    notifyListeners();
  }

  // --- OBTENER TRACKING DETALLADO DE UN PEDIDO ---
  Future<void> fetchOrderTracking(int pedidoId) async {
    _isLoadingTracking = true;
    _errorMessage = null;
    notifyListeners();

    final res = await _apiService.obtenerTrackingPedido(pedidoId);

    _isLoadingTracking = false;

    if (res.containsKey('error')) {
      _errorMessage = res['error'];
    } else if (res['success'] == true) {
      _selectedOrderTracking = OrderModel.fromJson(res['tracking']);
    } else {
      _errorMessage = 'Ocurrió un error al obtener el seguimiento del pedido.';
    }

    notifyListeners();
  }
}
