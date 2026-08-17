import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:nahara_flutter/providers/auth_provider.dart';
import 'package:nahara_flutter/providers/order_provider.dart';
import 'package:nahara_flutter/screens/orders/order_tracking_screen.dart';

class OrderListScreen extends StatefulWidget {
  const OrderListScreen({super.key});

  @override
  State<OrderListScreen> createState() => _OrderListScreenState();
}

class _OrderListScreenState extends State<OrderListScreen> {
  @override
  void initState() {
    super.initState();
    // Cargar los pedidos al iniciar la pantalla
    WidgetsBinding.instance.addPostFrameCallback((_) {
      Provider.of<OrderProvider>(context, listen: false).fetchOrders();
    });
  }

  Color _obtenerColorEstado(String estado) {
    switch (estado.toLowerCase()) {
      case 'pendiente':
        return Colors.orange;
      case 'pagado':
        return Colors.blue;
      case 'despachado':
        return Colors.purple;
      case 'en tránsito':
      case 'en transito':
        return Colors.indigo;
      case 'entregado':
        return Colors.green;
      case 'rechazado':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    final orderProvider = Provider.watch<OrderProvider>(context);
    final authProvider = Provider.read<AuthProvider>(context);
    final user = authProvider.currentUser;

    return Scaffold(
      backgroundColor: Colors.grey.shade50,
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Mis Pedidos',
              style: TextStyle(color: Color(0xFF1E293B), fontWeight: FontWeight.bold, fontSize: 20),
            ),
            if (user != null)
              Text(
                'Hola, ${user.nombre}',
                style: TextStyle(color: Colors.grey.shade600, fontSize: 13, fontWeight: FontWeight.normal),
              ),
          ],
        ),
        backgroundColor: Colors.white,
        elevation: 0.5,
        actions: [
          IconButton(
            icon: const Icon(Icons.logout, color: Color(0xFFE11D48)),
            tooltip: 'Cerrar Sesión',
            onPressed: () async {
              await authProvider.logout();
              if (mounted) {
                // Redirigir al inicio o pantalla de login (en este caso sacamos del stack)
                Navigator.of(context).popUntil((route) => route.isFirst);
              }
            },
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: orderProvider.fetchOrders,
        color: const Color(0xFF1E3A8A),
        child: _buildBody(orderProvider),
      ),
    );
  }

  Widget _buildBody(OrderProvider provider) {
    if (provider.isLoadingOrders) {
      return const Center(
        child: CircularProgressIndicator(color: Color(0xFF1E3A8A)),
      );
    }

    if (provider.errorMessage != null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error_outline, size: 64, color: Colors.red),
              const SizedBox(height: 16),
              Text(
                provider.errorMessage!,
                textAlign: TextAlign.center,
                style: const TextStyle(fontSize: 16, color: Color(0xFF475569)),
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: provider.fetchOrders,
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF1E3A8A),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                ),
                child: const Text('Reintentar', style: TextStyle(color: Colors.white)),
              ),
            ],
          ),
        ),
      );
    }

    if (provider.orders.isEmpty) {
      return ListView(
        children: [
          SizedBox(height: MediaQuery.of(context).size.height * 0.25),
          const Center(
            child: Column(
              children: [
                Icon(Icons.shopping_bag_outlined, size: 80, color: Colors.grey),
                SizedBox(height: 16),
                Text(
                  'No tienes ningún pedido registrado',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF475569)),
                ),
                SizedBox(height: 8),
                Text(
                  'Tus compras aparecerán aquí automáticamente.',
                  style: TextStyle(fontSize: 14, color: Colors.grey),
                ),
              ],
            ),
          ),
        ],
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: provider.orders.length,
      itemBuilder: (context, index) {
        final order = provider.orders[index];
        final Color estadoColor = _obtenerColorEstado(order.estado);

        return Card(
          margin: const EdgeInsets.only(bottom: 12),
          elevation: 1.5,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          child: InkWell(
            borderRadius: BorderRadius.circular(12),
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => OrderTrackingScreen(pedidoId: order.idPedido),
                ),
              );
            },
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.between,
                    children: [
                      Text(
                        'Pedido #${order.idPedido}',
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF1E293B),
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: estadoColor.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(20),
                          border: Border.all(color: estadoColor.withOpacity(0.5)),
                        ),
                        child: Text(
                          order.estado,
                          style: TextStyle(
                            color: estadoColor,
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Fecha: ${order.fechaCreacion}',
                    style: TextStyle(fontSize: 13, color: Colors.grey.shade600),
                  ),
                  const SizedBox(height: 12),
                  const Divider(),
                  const SizedBox(height: 8),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.between,
                    children: [
                      Text(
                        '${order.itemsCount} artículo(s)',
                        style: TextStyle(fontSize: 14, color: Colors.grey.shade700),
                      ),
                      Text(
                        'Total: Bs. ${order.total.toStringAsFixed(2)}',
                        style: const TextStyle(
                          fontSize: 15,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF1E3A8A),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }
}
