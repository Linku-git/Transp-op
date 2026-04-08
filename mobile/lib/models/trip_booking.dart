class TripBooking {
  final DateTime date;
  final String shiftId;
  final String shiftLabel;
  final String pickupPointId;
  final String pickupPointName;
  final double? pickupLat;
  final double? pickupLng;

  const TripBooking({
    required this.date,
    required this.shiftId,
    required this.shiftLabel,
    required this.pickupPointId,
    required this.pickupPointName,
    this.pickupLat,
    this.pickupLng,
  });

  Map<String, dynamic> toJson() => {
        'date': '${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}',
        'shift_id': shiftId,
        'pickup_point_id': pickupPointId,
        if (pickupLat != null) 'pickup_lat': pickupLat,
        if (pickupLng != null) 'pickup_lng': pickupLng,
      };
}

class Shift {
  final String id;
  final String label;
  final String entryTime;
  final String exitTime;

  const Shift({
    required this.id,
    required this.label,
    required this.entryTime,
    required this.exitTime,
  });

  factory Shift.fromJson(Map<String, dynamic> json) {
    return Shift(
      id: json['id'] as String,
      label: json['label'] as String? ?? json['shift_type'] as String? ?? 'Poste',
      entryTime: json['entry_time'] as String? ?? '',
      exitTime: json['exit_time'] as String? ?? '',
    );
  }
}

class PickupPoint {
  final String id;
  final String name;
  final double lat;
  final double lng;
  final double? walkingMinutes;

  const PickupPoint({
    required this.id,
    required this.name,
    required this.lat,
    required this.lng,
    this.walkingMinutes,
  });

  factory PickupPoint.fromJson(Map<String, dynamic> json) {
    return PickupPoint(
      id: json['id'] as String,
      name: json['name'] as String,
      lat: (json['lat'] as num).toDouble(),
      lng: (json['lng'] as num).toDouble(),
      walkingMinutes: (json['walking_minutes'] as num?)?.toDouble(),
    );
  }
}

class BookingConfirmation {
  final String tripId;
  final String message;

  const BookingConfirmation({required this.tripId, required this.message});

  factory BookingConfirmation.fromJson(Map<String, dynamic> json) {
    return BookingConfirmation(
      tripId: json['trip_id'] as String? ?? json['id'] as String? ?? '',
      message: json['message'] as String? ?? 'Réservation confirmée',
    );
  }
}
