import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:nahara_flutter/providers/order_provider.dart';
import 'package:nahara_flutter/widgets/order_status_tracker.dart';

class OrderTrackingScreen extends StatefulWidget {
  final int pedidoId;

  const OrderTrackingScreen({super.key, required this.pedidoId});

  @override
  State<OrderTrackingScreen> createState() => _OrderTrackingScreenState();
}

class _OrderTrackingScreenState extends State<OrderTrackingScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      Provider.of<OrderProvider>(context, listen: false).fetchOrderTracking(widget.pedidoId);
    });
  }

  // Abre la URL de la foto de la guía o factura
  Future<void> _abrirGuia(String url) async {
    final uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    } else {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('No se pudo abrir la foto de la guía.')),
        );
      }
    }
  }

  // Abre WhatsApp con el mensaje prediseñado: "Hola, tengo una consulta sobre mi pedido [ID_PEDIDO]"
  Future<void> _contactarVendedor(int pedidoId) async {
    // Número de WhatsApp de la tienda (se puede parametrizar; ej: +59170000000)
    const String telefonoVendedor = '59170000000';
    final String mensaje = 'Hola, tengo una consulta sobre mi pedido $pedidoId';
    final Uri url = Uri.parse(
      'https://wa.me/$telefonoVendedor?text=${Uri.encodeComponent(mensaje)}'
    );

    if (await canLaunchUrl(url)) {
      await launchUrl(url, mode: LaunchMode.externalApplication);
    } else {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('No se pudo abrir la aplicación de WhatsApp.')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final orderProvider = Provider.watch<OrderProvider>(context);
    final tracking = orderProvider.selectedOrderTracking;

    return Scaffold(
      backgroundColor: Colors.grey.shade50,
      appBar: AppBar(
        title: Text(
          'Seguimiento Pedido #${widget.pedidoId}',
          style: const TextStyle(color: Color(0xFF1E293B), fontWeight: FontWeight.bold, fontSize: 18),
        ),
        backgroundColor: Colors.white,
        elevation: 0.5,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Color(0xFF1E293B)),
          onPressed: () {
            orderProvider.clearTracking();
            Navigator.pop(context);
          },
        ),
      ),
      body: _buildBody(orderProvider, tracking),
    );
  }

  Widget _buildBody(OrderProvider provider, dynamic tracking) {
    if (provider.isLoadingTracking) {
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
                onPressed: () => provider.fetchOrderTracking(widget.pedidoId),
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

    if (tracking == null) {
      return const Center(
        child: Text('No se encontraron detalles para este pedido.'),
      );
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Tarjeta de información del cliente y tipo de envío
          Card(
            elevation: 1,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.location_on_outlined, color: Color(0xFF1E3A8A)),
                      const SizedBox(width: 8),
                      Text(
                        'Método de Entrega: ${tracking.tipoEntrega}',
                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: Color(0xFF1E293B)),
                      ),
                    ],
                  ),
                  if (tracking.direccionEnvio != null && tracking.direccionEnvio.isNotEmpty) ...[
                    const SizedBox(height: 8),
                    Text(
                      'Dirección: ${tracking.direccionEnvio}',
                      style: TextStyle(color: Colors.grey.shade700, fontSize: 14),
                    ),
                  ],
                  const SizedBox(height: 8),
                  Text(
                    'Registrado el: ${tracking.fechaCreacion}',
                    style: TextStyle(color: Colors.grey.shade500, fontSize: 13),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // Tarjeta de información interdepartamental (Guía)
          if (tracking.empresaTransporte != null || tracking.numeroGuia != null)
            Card(
              elevation: 1,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              color: const Color(0xFFF8FAFC),
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Detalles de Envío Nacional',
                      style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: Color(0xFF1E3A8A)),
                    ),
                    const SizedBox(height: 12),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.between,
                      children: [
                        Text('Empresa de Transporte:', style: TextStyle(color: Colors.grey.shade600, fontSize: 14)),
                        Text(
                          tracking.empresaTransporte ?? 'No especificada',
                          style: const TextStyle(fontWeight: FontWeight.w600, color: Color(0xFF1E293B)),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.between,
                      children: [
                        Text('Número de Guía / Factura:', style: TextStyle(color: Colors.grey.shade600, fontSize: 14)),
                        Text(
                          tracking.numeroGuia ?? 'Pendiente',
                          style: const TextStyle(fontWeight: FontWeight.w600, color: Color(0xFF1E293B)),
                        ),
                      ],
                    ),
                    if (tracking.numeroGuiaFotoUrl != null) ...[
                      const SizedBox(height: 16),
                      SizedBox(
                        width: double.infinity,
                        height: 48,
                        child: OutlinedButton.icon(
                          onPressed: () => _abrirGuia(tracking.numeroGuiaFotoUrl!),
                          icon: const Icon(Icons.receipt_long, color: Color(0xFF1E3A8A)),
                          label: const Text(
                            'Ver Guía de Envío / Foto',
                            style: TextStyle(color: Color(0xFF1E3A8A), fontWeight: FontWeight.bold),
                          ),
                          style: OutlinedButton.styleFrom(
                            side: const BorderSide(color: Color(0xFF1E3A8A)),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                          ),
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ),
          const SizedBox(height: 16),

          // Barra de progreso del tracking
          OrderStatusTracker(estadoActual: tracking.estado),
          const SizedBox(height: 16),

          // Tarjeta de artículos y resumen de cobro
          Card(
            elevation: 1,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: Theme(
              data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
              child: ExpansionTile(
                initiallyExpanded: false,
                title: const Text(
                  'Ver Detalle de Compra',
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: Color(0xFF1E293B)),
                ),
                children: [
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
                    child: Column(
                      children: [
                        ListView.builder(
                          shrinkWrap: true,
                          physics: const NeverScrollableScrollPhysics(),
                          itemCount: tracking.items.length,
                          itemBuilder: (context, index) {
                            final item = tracking.items[index];
                            return Padding(
                              padding: const EdgeInsets.symmetric(vertical: 4.0),
                              child: Row(
                                mainAxisAlignment: MainAxisAlignment.between,
                                children: [
                                  Expanded(
                                    child: Text(
                                      '${item.nombre} x${item.cantidad}',
                                      style: const TextStyle(fontSize: 14, color: Color(0xFF334155)),
                                    ),
                                  ),
                                  Text(
                                    'Bs. ${item.subtotal.toStringAsFixed(2)}',
                                    style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w500),
                                  ),
                                ],
                              ),
                            );
                          },
                        ),
                        const Divider(height: 24),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.between,
                          children: [
                            const Text('Subtotal:', style: TextStyle(color: Colors.grey, fontSize: 13)),
                            Text('Bs. ${tracking.subtotal.toStringAsFixed(2)}', style: const TextStyle(fontSize: 13)),
                          ],
                        ),
                        const SizedBox(height: 4),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.between,
                          children: [
                            const Text('Costo de Envío:', style: TextStyle(color: Colors.grey, fontSize: 13)),
                            Text('Bs. ${tracking.costoEnvio.toStringAsFixed(2)}', style: const TextStyle(fontSize: 13)),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.between,
                          children: [
                            const Text('Total:', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
                            Text(
                              'Bs. ${tracking.total.toStringAsFixed(2)}',
                              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: Color(0xFF1E3A8A)),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),

          // Botón Contactar Vendedor por WhatsApp
          SizedBox(
            width: double.infinity,
            height: 52,
            child: ElevatedButton.icon(
              onPressed: () => _contactarVendedor(tracking.idPedido),
              icon: Image.network(
                'https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg',
                height: 24,
                width: 24,
                errorBuilder: (_, __, ___) => const Icon(Icons.chat_bubble_outline, color: Colors.white),
              ),
              label: const Text(
                'Contactar al Vendedor por WhatsApp',
                style: TextStyle(color: Colors.white, fontSize: 15, fontWeight: FontWeight.bold),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF25D366), // Color oficial WhatsApp
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                elevation: 1,
              ),
            ),
          ),
          const SizedBox(height: 16),
        ],
      ),
    );
  }
}
