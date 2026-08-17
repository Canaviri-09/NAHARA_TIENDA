import 'package:flutter/material.dart';

class OrderStatusTracker extends StatelessWidget {
  final String estadoActual;

  const OrderStatusTracker({
    super.key,
    required this.estadoActual,
  });

  // Lista ordenada de los estados para calcular el progreso
  static const List<Map<String, dynamic>> _etapas = [
    {
      'estado': 'Pendiente',
      'titulo': 'Pedido Pendiente',
      'descripcion': 'Tu pedido ha sido registrado y está a la espera de confirmación de pago.',
      'icono': Icons.receipt_long_outlined,
    },
    {
      'estado': 'Pagado',
      'titulo': 'Pago Verificado',
      'descripcion': 'El pago fue verificado correctamente y tu nota de venta fue emitida.',
      'icono': Icons.payment_outlined,
    },
    {
      'estado': 'Despachado',
      'titulo': 'Pedido Despachado',
      'descripcion': 'Tu pedido fue embalado y entregado a la transportadora interdepartamental.',
      'icono': Icons.inventory_2_outlined,
    },
    {
      'estado': 'En Tránsito',
      'titulo': 'En Tránsito',
      'descripcion': 'El paquete se encuentra en viaje hacia tu ciudad de destino.',
      'icono': Icons.local_shipping_outlined,
    },
    {
      'estado': 'Entregado',
      'titulo': 'Entregado',
      'descripcion': 'El paquete fue recibido con éxito. ¡Gracias por tu compra!',
      'icono': Icons.done_all_outlined,
    },
  ];

  @override
  Widget build(BuildContext context) {
    // Si el pedido fue rechazado, mostramos una tarjeta de alerta especial
    if (estadoActual == 'Rechazado') {
      return Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.red.shade50,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.red.shade200),
        ),
        child: Row(
          children: [
            Icon(Icons.cancel_outlined, color: Colors.red.shade700, size: 32),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Pedido Cancelado / Rechazado',
                    style: TextStyle(
                      color: Colors.red.shade900,
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Este pedido ha sido marcado como cancelado. Si tienes dudas, ponte en contacto con soporte.',
                    style: TextStyle(
                      color: Colors.red.shade700,
                      fontSize: 14,
                    ),
                  ),
                ],
              ),
            )
          ],
        ),
      );
    }

    // Obtener el índice del estado actual en nuestra lista
    int indiceActual = _etapas.indexWhere(
      (element) => element['estado'].toString().toLowerCase() == estadoActual.toLowerCase()
    );
    if (indiceActual == -1) {
      // Por defecto, si no se encuentra (o es un estado nuevo) asumimos Pendiente (0)
      indiceActual = 0;
    }

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Estado de Envío',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Color(0xFF1E293B), // Slate 800
              ),
            ),
            const SizedBox(height: 24),
            ListView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: _etapas.length,
              itemBuilder: (context, index) {
                final etapa = _etapas[index];
                final bool estaCompletado = index < indiceActual;
                final bool esActivo = index == indiceActual;
                final bool esPendiente = index > indiceActual;

                // Definir colores según el estado
                final Color colorLinea = estaCompletado ? const Color(0xFF10B981) : Colors.grey.shade300; // Esmeralda para completado
                final Color colorIcono = esActivo
                    ? const Color(0xFF3B82F6) // Azul para activo actual
                    : (estaCompletado ? const Color(0xFF10B981) : Colors.grey.shade400);
                
                final Color colorFondoCirculo = esActivo
                    ? const Color(0xFFEFF6FF)
                    : (estaCompletado ? const Color(0xFFECFDF5) : Colors.grey.shade100);

                final Color colorBordeCirculo = esActivo
                    ? const Color(0xFF3B82F6)
                    : (estaCompletado ? const Color(0xFF10B981) : Colors.grey.shade300);

                return IntrinsicHeight(
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      // Línea y círculo con icono
                      Column(
                        children: [
                          Container(
                            width: 44,
                            height: 44,
                            decoration: BoxDecoration(
                              color: colorFondoCirculo,
                              shape: BoxShape.circle,
                              border: Border.all(
                                color: colorBordeCirculo,
                                width: esActivo ? 2.5 : 1.5,
                              ),
                              boxShadow: esActivo
                                  ? [
                                      BoxShadow(
                                        color: const Color(0xFF3B82F6).withOpacity(0.2),
                                        blurRadius: 8,
                                        spreadRadius: 2,
                                      )
                                    ]
                                  : null,
                            ),
                            child: Icon(
                              etapa['icono'] as IconData,
                              color: colorIcono,
                              size: 20,
                            ),
                          ),
                          // Línea conectora
                          if (index < _etapas.length - 1)
                            Expanded(
                              child: Container(
                                width: 3,
                                color: colorLinea,
                              ),
                            ),
                        ],
                      ),
                      const SizedBox(width: 16),
                      // Textos informativos
                      Expanded(
                        child: Padding(
                          padding: const EdgeInsets.only(bottom: 24.0),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                etapa['titulo'] as String,
                                style: TextStyle(
                                  fontSize: 16,
                                  fontWeight: esActivo ? FontWeight.bold : FontWeight.w600,
                                  color: esActivo 
                                      ? const Color(0xFF1E3A8A) // Azul marino oscuro
                                      : (esPendiente ? Colors.grey.shade500 : const Color(0xFF334155)),
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                etapa['descripcion'] as String,
                                style: TextStyle(
                                  fontSize: 13,
                                  height: 1.4,
                                  color: esActivo 
                                      ? const Color(0xFF475569) 
                                      : (esPendiente ? Colors.grey.shade400 : Colors.grey.shade600),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}
