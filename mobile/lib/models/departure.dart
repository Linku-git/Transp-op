class Departure {
  final String id;
  final DateTime departureTime;
  final String pickupPointName;
  final double? walkingMinutes;
  final String vehicleType;
  final String routeName;
  final String? driverName;

  const Departure({
    required this.id,
    required this.departureTime,
    required this.pickupPointName,
    this.walkingMinutes,
    required this.vehicleType,
    required this.routeName,
    this.driverName,
  });

  Duration get timeRemaining => departureTime.difference(DateTime.now());

  int get minutesRemaining => timeRemaining.inMinutes;

  bool get hasDeparted => timeRemaining.isNegative;

  factory Departure.fromJson(Map<String, dynamic> json) {
    return Departure(
      id: json['id'] as String,
      departureTime: DateTime.parse(json['departure_time'] as String),
      pickupPointName: json['pickup_point_name'] as String,
      walkingMinutes: (json['walking_minutes'] as num?)?.toDouble(),
      vehicleType: json['vehicle_type'] as String,
      routeName: json['route_name'] as String,
      driverName: json['driver_name'] as String?,
    );
  }
}

class ContentItem {
  final String id;
  final String title;
  final String snippet;
  final String type;
  final DateTime publishedAt;
  final String? imageUrl;
  final bool isRead;

  const ContentItem({
    required this.id,
    required this.title,
    required this.snippet,
    required this.type,
    required this.publishedAt,
    this.imageUrl,
    this.isRead = false,
  });

  factory ContentItem.fromJson(Map<String, dynamic> json) {
    return ContentItem(
      id: json['id'] as String,
      title: json['title'] as String,
      snippet: json['snippet'] as String? ?? '',
      type: json['type'] as String? ?? 'news',
      publishedAt: DateTime.parse(json['published_at'] as String),
      imageUrl: json['image_url'] as String?,
      isRead: json['is_read'] as bool? ?? false,
    );
  }
}
