class UserModel {
  final int id;
  final String nombre;
  final String correo;
  final String? telefono;
  final String rol;
  final String? estadoAprobacionB2b; // 'Pendiente' | 'Aprobado' | 'Rechazado' | null

  UserModel({
    required this.id,
    required this.nombre,
    required this.correo,
    this.telefono,
    required this.rol,
    this.estadoAprobacionB2b,
  });

  bool get esMayorista => rol.contains('Mayorista');
  bool get estaAprobadoMayorista => esMayorista && estadoAprobacionB2b == 'Aprobado';
  bool get esPendienteAprobacion => esMayorista && estadoAprobacionB2b == 'Pendiente';

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'] as int,
      nombre: json['nombre'] as String,
      correo: json['correo'] as String,
      telefono: json['telefono'] as String?,
      rol: json['rol'] as String,
      estadoAprobacionB2b: json['estado_aprobacion_b2b'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'nombre': nombre,
      'correo': correo,
      'telefono': telefono,
      'rol': rol,
      'estado_aprobacion_b2b': estadoAprobacionB2b,
    };
  }
}
