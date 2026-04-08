enum NotificationType {
  rtiAlert,
  routeChange,
  weather,
  content,
  emergency;

  String get label => switch (this) {
        rtiAlert => 'Transport',
        routeChange => 'Itinéraire',
        weather => 'Météo',
        content => 'Contenu',
        emergency => 'Urgence',
      };

  String get icon => switch (this) {
        rtiAlert => 'directions_bus',
        routeChange => 'map',
        weather => 'cloud',
        content => 'article',
        emergency => 'shield',
      };

  static NotificationType fromString(String value) => switch (value) {
        'rti_alert' => NotificationType.rtiAlert,
        'route_change' => NotificationType.routeChange,
        'weather' => NotificationType.weather,
        'content' => NotificationType.content,
        'emergency' => NotificationType.emergency,
        _ => NotificationType.content,
      };

  String get targetRoute => switch (this) {
        rtiAlert => '/tracking',
        routeChange => '/trips',
        weather => '/home',
        content => '/content',
        emergency => '/emergency',
      };
}

class NotificationItem {
  final String id;
  final NotificationType type;
  final String title;
  final String body;
  final DateTime receivedAt;
  final bool isRead;
  final Map<String, dynamic>? data;

  const NotificationItem({
    required this.id,
    required this.type,
    required this.title,
    required this.body,
    required this.receivedAt,
    this.isRead = false,
    this.data,
  });

  String? get targetRoute {
    final contentId = data?['content_id'] as String?;
    final tripId = data?['trip_id'] as String?;

    if (type == NotificationType.content && contentId != null) {
      return '/content/$contentId';
    }
    if (type == NotificationType.rtiAlert && tripId != null) {
      return '/tracking';
    }
    return type.targetRoute;
  }

  NotificationItem copyWith({bool? isRead}) {
    return NotificationItem(
      id: id,
      type: type,
      title: title,
      body: body,
      receivedAt: receivedAt,
      isRead: isRead ?? this.isRead,
      data: data,
    );
  }

  factory NotificationItem.fromJson(Map<String, dynamic> json) {
    return NotificationItem(
      id: json['id'] as String? ?? DateTime.now().millisecondsSinceEpoch.toString(),
      type: NotificationType.fromString(json['type'] as String? ?? 'content'),
      title: json['title'] as String? ?? '',
      body: json['body'] as String? ?? '',
      receivedAt: json['received_at'] != null
          ? DateTime.parse(json['received_at'] as String)
          : DateTime.now(),
      isRead: json['is_read'] as bool? ?? false,
      data: json['data'] as Map<String, dynamic>?,
    );
  }

  factory NotificationItem.fromFCM(Map<String, dynamic> message) {
    final notification = message['notification'] as Map<String, dynamic>? ?? {};
    final data = message['data'] as Map<String, dynamic>? ?? {};

    return NotificationItem(
      id: data['notification_id'] as String? ?? DateTime.now().millisecondsSinceEpoch.toString(),
      type: NotificationType.fromString(data['type'] as String? ?? 'content'),
      title: notification['title'] as String? ?? data['title'] as String? ?? '',
      body: notification['body'] as String? ?? data['body'] as String? ?? '',
      receivedAt: DateTime.now(),
      data: data,
    );
  }
}
