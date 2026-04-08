class TransportPreferences {
  String? currentMode;
  bool interestedInCompanyTransport;
  bool hasPrivateCar;
  bool volunteerDriver;
  int carpoolSeats;
  double maxWalkingDistanceMeters;
  double? pickupLat;
  double? pickupLng;
  String? pickupName;

  TransportPreferences({
    this.currentMode,
    this.interestedInCompanyTransport = true,
    this.hasPrivateCar = false,
    this.volunteerDriver = false,
    this.carpoolSeats = 0,
    this.maxWalkingDistanceMeters = 500,
    this.pickupLat,
    this.pickupLng,
    this.pickupName,
  });

  Map<String, dynamic> toJson() {
    return {
      'current_transport_mode': currentMode,
      'opt_in_company_transport': interestedInCompanyTransport,
      'has_private_car': hasPrivateCar,
      'volunteer_driver': volunteerDriver,
      'carpool_seats': carpoolSeats,
      'max_walking_distance_meters': maxWalkingDistanceMeters.round(),
      if (pickupLat != null) 'pickup_lat': pickupLat,
      if (pickupLng != null) 'pickup_lng': pickupLng,
      if (pickupName != null) 'pickup_name': pickupName,
    };
  }
}

class TransportMode {
  final String key;
  final String label;
  final String icon;

  const TransportMode({
    required this.key,
    required this.label,
    required this.icon,
  });

  static const List<TransportMode> all = [
    TransportMode(key: 'voiture', label: 'Voiture', icon: 'directions_car'),
    TransportMode(key: 'transport_commun', label: 'Transport en commun', icon: 'directions_bus'),
    TransportMode(key: 'covoiturage', label: 'Covoiturage', icon: 'people'),
    TransportMode(key: 'taxi', label: 'Taxi / VTC', icon: 'local_taxi'),
    TransportMode(key: 'deux_roues', label: 'Deux-roues', icon: 'two_wheeler'),
    TransportMode(key: 'marche', label: 'Marche', icon: 'directions_walk'),
    TransportMode(key: 'velo', label: 'Vélo', icon: 'pedal_bike'),
    TransportMode(key: 'autre', label: 'Autre', icon: 'more_horiz'),
  ];
}
