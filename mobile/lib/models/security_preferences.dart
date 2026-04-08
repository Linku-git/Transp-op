class SecurityPreferences {
  int safetyRating;
  List<String> vulnerableTimeSlots;
  List<ConcernZone> concernZones;
  String? nightConcerns;
  double maxNightWalkingDistanceMeters;

  SecurityPreferences({
    this.safetyRating = 3,
    List<String>? vulnerableTimeSlots,
    List<ConcernZone>? concernZones,
    this.nightConcerns,
    this.maxNightWalkingDistanceMeters = 300,
  })  : vulnerableTimeSlots = vulnerableTimeSlots ?? [],
        concernZones = concernZones ?? [];

  Map<String, dynamic> toJson() {
    return {
      'safety_rating': safetyRating,
      'vulnerable_time_slots': vulnerableTimeSlots,
      'concern_zones': concernZones.map((z) => z.toJson()).toList(),
      'night_concerns': nightConcerns,
      'max_night_walking_distance_meters': maxNightWalkingDistanceMeters.round(),
    };
  }
}

class ConcernZone {
  final double lat;
  final double lng;
  final String? description;

  const ConcernZone({
    required this.lat,
    required this.lng,
    this.description,
  });

  Map<String, dynamic> toJson() => {
        'lat': lat,
        'lng': lng,
        if (description != null) 'description': description,
      };
}

class TimeSlot {
  final String key;
  final String label;

  const TimeSlot({required this.key, required this.label});

  static const List<TimeSlot> all = [
    TimeSlot(key: '05h-07h', label: '05h - 07h'),
    TimeSlot(key: '07h-09h', label: '07h - 09h'),
    TimeSlot(key: '12h-14h', label: '12h - 14h'),
    TimeSlot(key: '17h-19h', label: '17h - 19h'),
    TimeSlot(key: '19h-22h', label: '19h - 22h'),
    TimeSlot(key: '22h-05h', label: '22h - 05h'),
  ];
}
