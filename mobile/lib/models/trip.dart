class Trip {
  final String id;
  final DateTime date;
  final String shiftLabel;
  final String pickupPointName;
  final String routeName;
  final String vehicleType;
  final TripStatus status;
  final DateTime departureTime;
  final DateTime? arrivalTime;
  final double? co2SavedKg;
  final double? distanceKm;
  final double? durationMinutes;
  final double? pickupLat;
  final double? pickupLng;
  final double? siteLat;
  final double? siteLng;

  const Trip({
    required this.id,
    required this.date,
    required this.shiftLabel,
    required this.pickupPointName,
    required this.routeName,
    required this.vehicleType,
    required this.status,
    required this.departureTime,
    this.arrivalTime,
    this.co2SavedKg,
    this.distanceKm,
    this.durationMinutes,
    this.pickupLat,
    this.pickupLng,
    this.siteLat,
    this.siteLng,
  });

  bool get canModify {
    if (status != TripStatus.booked && status != TripStatus.confirmed) {
      return false;
    }
    return departureTime.difference(DateTime.now()).inMinutes > 30;
  }

  bool get canCancel => canModify;

  bool get isUpcoming =>
      status == TripStatus.booked ||
      status == TripStatus.confirmed ||
      status == TripStatus.inProgress;

  factory Trip.fromJson(Map<String, dynamic> json) {
    return Trip(
      id: json['id'] as String,
      date: DateTime.parse(json['date'] as String),
      shiftLabel: json['shift_label'] as String? ?? '',
      pickupPointName: json['pickup_point_name'] as String? ?? '',
      routeName: json['route_name'] as String? ?? '',
      vehicleType: json['vehicle_type'] as String? ?? '',
      status: TripStatus.fromString(json['status'] as String? ?? 'booked'),
      departureTime: DateTime.parse(json['departure_time'] as String),
      arrivalTime: json['arrival_time'] != null
          ? DateTime.parse(json['arrival_time'] as String)
          : null,
      co2SavedKg: (json['co2_saved_kg'] as num?)?.toDouble(),
      distanceKm: (json['distance_km'] as num?)?.toDouble(),
      durationMinutes: (json['duration_minutes'] as num?)?.toDouble(),
      pickupLat: (json['pickup_lat'] as num?)?.toDouble(),
      pickupLng: (json['pickup_lng'] as num?)?.toDouble(),
      siteLat: (json['site_lat'] as num?)?.toDouble(),
      siteLng: (json['site_lng'] as num?)?.toDouble(),
    );
  }
}

enum TripStatus {
  booked,
  confirmed,
  inProgress,
  completed,
  cancelled;

  String get label => switch (this) {
        booked => 'Réservé',
        confirmed => 'Confirmé',
        inProgress => 'En cours',
        completed => 'Terminé',
        cancelled => 'Annulé',
      };

  static TripStatus fromString(String value) => switch (value) {
        'booked' => TripStatus.booked,
        'confirmed' => TripStatus.confirmed,
        'in_progress' => TripStatus.inProgress,
        'completed' => TripStatus.completed,
        'cancelled' => TripStatus.cancelled,
        _ => TripStatus.booked,
      };
}

class TripStats {
  final int totalTrips;
  final double totalCo2SavedKg;
  final double totalDistanceKm;

  const TripStats({
    this.totalTrips = 0,
    this.totalCo2SavedKg = 0,
    this.totalDistanceKm = 0,
  });

  factory TripStats.fromTrips(List<Trip> trips) {
    return TripStats(
      totalTrips: trips.length,
      totalCo2SavedKg: trips.fold(0.0, (sum, t) => sum + (t.co2SavedKg ?? 0)),
      totalDistanceKm: trips.fold(0.0, (sum, t) => sum + (t.distanceKm ?? 0)),
    );
  }
}
