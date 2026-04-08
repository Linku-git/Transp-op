class VehiclePosition {
  final String vehicleId;
  final double lat;
  final double lng;
  final double? heading;
  final double? speed;
  final DateTime timestamp;
  final int? etaSeconds;

  const VehiclePosition({
    required this.vehicleId,
    required this.lat,
    required this.lng,
    this.heading,
    this.speed,
    required this.timestamp,
    this.etaSeconds,
  });

  factory VehiclePosition.fromJson(Map<String, dynamic> json) {
    return VehiclePosition(
      vehicleId: json['vehicle_id'] as String,
      lat: (json['lat'] as num).toDouble(),
      lng: (json['lng'] as num).toDouble(),
      heading: (json['heading'] as num?)?.toDouble(),
      speed: (json['speed'] as num?)?.toDouble(),
      timestamp: json['timestamp'] != null
          ? DateTime.parse(json['timestamp'] as String)
          : DateTime.now(),
      etaSeconds: json['eta_seconds'] as int?,
    );
  }
}

class TrackingInfo {
  final String vehicleId;
  final String vehicleType;
  final String routeName;
  final String? driverName;
  final String gatheringPointName;
  final double gatheringPointLat;
  final double gatheringPointLng;
  final double? employeeLat;
  final double? employeeLng;

  const TrackingInfo({
    required this.vehicleId,
    required this.vehicleType,
    required this.routeName,
    this.driverName,
    required this.gatheringPointName,
    required this.gatheringPointLat,
    required this.gatheringPointLng,
    this.employeeLat,
    this.employeeLng,
  });

  factory TrackingInfo.fromJson(Map<String, dynamic> json) {
    return TrackingInfo(
      vehicleId: json['vehicle_id'] as String,
      vehicleType: json['vehicle_type'] as String,
      routeName: json['route_name'] as String? ?? '',
      driverName: json['driver_name'] as String?,
      gatheringPointName: json['gathering_point_name'] as String,
      gatheringPointLat: (json['gathering_point_lat'] as num).toDouble(),
      gatheringPointLng: (json['gathering_point_lng'] as num).toDouble(),
      employeeLat: (json['employee_lat'] as num?)?.toDouble(),
      employeeLng: (json['employee_lng'] as num?)?.toDouble(),
    );
  }
}
