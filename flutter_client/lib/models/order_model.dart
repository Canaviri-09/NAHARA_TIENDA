class OrderModel {
  final int idPedido;
  final String estado; // Pendiente | Pagado | Despachado | En Tránsito | Entregado | Rechazado
  final String? empresaTransporte;
  final String? numeroGuia;
  final String? numeroGuiaFotoUrl;
  final String fechaCreacion;
  final String tipoEntrega;
  final String? direccionEnvio;
  final double costoEnvio;
  final double subtotal;
  final double total;
  final List<OrderItemModel> items;

  OrderModel({
    required this.idPedido,
    required this.estado,
    this.empresaTransporte,
    this.numeroGuia,
    this.numeroGuiaFotoUrl,
    required this.fechaCreacion,
    required this.tipoEntrega,
    this.direccionEnvio,
    required this.costoEnvio,
    required this.subtotal,
    required this.total,
    required this.items,
  });

  factory OrderModel.fromJson(Map<String, dynamic> json) {
    var itemsList = json['items'] as List? ?? [];
    List<OrderItemModel> parsedItems = itemsList
        .map((itemJson) => OrderItemModel.fromJson(itemJson as Map<String, dynamic>))
        .toList();

    return OrderModel(
      idPedido: json['id_pedido'] as int,
      estado: json['estado'] as String,
      empresaTransporte: json['empresa_transporte'] as String?,
      numeroGuia: json['numero_guia'] as String?,
      numeroGuiaFotoUrl: json['numero_guia_foto_url'] as String?,
      fechaCreacion: json['fecha_creacion'] as String,
      tipoEntrega: json['tipo_entrega'] as String,
      direccionEnvio: json['direccion_envio'] as String?,
      costoEnvio: (json['costo_envio'] as num).toDouble(),
      subtotal: (json['subtotal'] as num).toDouble(),
      total: (json['total'] as num).toDouble(),
      items: parsedItems,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id_pedido': idPedido,
      'estado': estado,
      'empresa_transporte': empresaTransporte,
      'numero_guia': numeroGuia,
      'numero_guia_foto_url': numeroGuiaFotoUrl,
      'fecha_creacion': fechaCreacion,
      'tipo_entrega': tipoEntrega,
      'direccion_envio': direccionEnvio,
      'costo_envio': costoEnvio,
      'subtotal': subtotal,
      'total': total,
      'items': items.map((item) => item.toJson()).toList(),
    };
  }
}

class OrderItemModel {
  final String nombre;
  final int cantidad;
  final double precioUnitario;
  final double subtotal;

  OrderItemModel({
    required this.nombre,
    required this.cantidad,
    required this.precioUnitario,
    required this.subtotal,
  });

  factory OrderItemModel.fromJson(Map<String, dynamic> json) {
    return OrderItemModel(
      nombre: json['nombre'] as String,
      cantidad: json['cantidad'] as int,
      precioUnitario: (json['precio_unitario'] as num).toDouble(),
      subtotal: (json['subtotal'] as num).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'nombre': nombre,
      'cantidad': cantidad,
      'precio_unitario': precioUnitario,
      'subtotal': subtotal,
    };
  }
}
