class UserProfile {
  final String id;
  final String email;
  final String? firstName;
  final String? lastName;
  final String? matricule;
  final String? siteName;
  final String? shiftLabel;
  final String? phone;
  final String? transportMode;
  final bool isPmr;
  final double? pickupLat;
  final double? pickupLng;
  final String? pickupAddress;
  final ProfileStats stats;

  const UserProfile({
    required this.id,
    required this.email,
    this.firstName,
    this.lastName,
    this.matricule,
    this.siteName,
    this.shiftLabel,
    this.phone,
    this.transportMode,
    this.isPmr = false,
    this.pickupLat,
    this.pickupLng,
    this.pickupAddress,
    this.stats = const ProfileStats(),
  });

  String get displayName {
    if (firstName != null && lastName != null) return '$firstName $lastName';
    if (firstName != null) return firstName!;
    return email;
  }

  String get initials {
    final first = firstName?.isNotEmpty == true ? firstName![0] : '';
    final last = lastName?.isNotEmpty == true ? lastName![0] : '';
    if (first.isEmpty && last.isEmpty) return email[0].toUpperCase();
    return '$first$last'.toUpperCase();
  }

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      id: json['id'] as String,
      email: json['email'] as String,
      firstName: json['first_name'] as String?,
      lastName: json['last_name'] as String?,
      matricule: json['matricule'] as String?,
      siteName: json['site_name'] as String?,
      shiftLabel: json['shift_label'] as String?,
      phone: json['phone'] as String?,
      transportMode: json['current_transport_mode'] as String?,
      isPmr: json['is_pmr'] as bool? ?? false,
      pickupLat: (json['pickup_lat'] as num?)?.toDouble(),
      pickupLng: (json['pickup_lng'] as num?)?.toDouble(),
      pickupAddress: json['pickup_address'] as String?,
      stats: json['stats'] != null
          ? ProfileStats.fromJson(json['stats'] as Map<String, dynamic>)
          : const ProfileStats(),
    );
  }
}

class ProfileStats {
  final int totalTrips;
  final double co2SavedKg;
  final int trainingCompleted;

  const ProfileStats({
    this.totalTrips = 0,
    this.co2SavedKg = 0,
    this.trainingCompleted = 0,
  });

  factory ProfileStats.fromJson(Map<String, dynamic> json) {
    return ProfileStats(
      totalTrips: json['total_trips'] as int? ?? 0,
      co2SavedKg: (json['co2_saved_kg'] as num?)?.toDouble() ?? 0,
      trainingCompleted: json['training_completed'] as int? ?? 0,
    );
  }
}

class NotificationPreferences {
  bool rtiAlerts;
  bool routeChanges;
  bool contentNotifications;
  bool weatherAlerts;
  bool autoNightMode;
  int? nightModeStartHour;
  int? nightModeEndHour;

  NotificationPreferences({
    this.rtiAlerts = true,
    this.routeChanges = true,
    this.contentNotifications = true,
    this.weatherAlerts = true,
    this.autoNightMode = true,
    this.nightModeStartHour = 20,
    this.nightModeEndHour = 6,
  });

  Map<String, dynamic> toJson() => {
        'rti_alerts': rtiAlerts,
        'route_changes': routeChanges,
        'content_notifications': contentNotifications,
        'weather_alerts': weatherAlerts,
        'auto_night_mode': autoNightMode,
        'night_mode_start_hour': nightModeStartHour,
        'night_mode_end_hour': nightModeEndHour,
      };
}
