/// Content feed models for Session 70.
class FeedContent {
  final String id;
  final String title;
  final String? body;
  final String contentType;
  final String? mediaUrl;
  final DateTime? publishedAt;
  final DateTime? expiresAt;
  final bool delivered;
  final bool viewed;
  final bool completed;

  const FeedContent({
    required this.id,
    required this.title,
    this.body,
    required this.contentType,
    this.mediaUrl,
    this.publishedAt,
    this.expiresAt,
    this.delivered = false,
    this.viewed = false,
    this.completed = false,
  });

  /// Short snippet from body (strip HTML tags).
  String get snippet {
    if (body == null || body!.isEmpty) return '';
    final stripped = body!.replaceAll(RegExp(r'<[^>]*>'), '');
    return stripped.length > 120 ? '${stripped.substring(0, 120)}...' : stripped;
  }

  bool get isNew => !delivered && !viewed;

  String get typeLabel => switch (contentType) {
    'training' => 'Formation',
    'safety' => 'Sécurité',
    'survey' => 'Sondage',
    _ => 'Actualité',
  };

  factory FeedContent.fromJson(Map<String, dynamic> json) {
    return FeedContent(
      id: json['id'] as String,
      title: json['title'] as String,
      body: json['body'] as String?,
      contentType: json['content_type'] as String? ?? 'news',
      mediaUrl: json['media_url'] as String?,
      publishedAt: json['published_at'] != null
          ? DateTime.parse(json['published_at'] as String)
          : null,
      expiresAt: json['expires_at'] != null
          ? DateTime.parse(json['expires_at'] as String)
          : null,
      delivered: json['delivered'] as bool? ?? false,
      viewed: json['viewed'] as bool? ?? false,
      completed: json['completed'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'title': title,
    'body': body,
    'content_type': contentType,
    'media_url': mediaUrl,
    'published_at': publishedAt?.toIso8601String(),
    'expires_at': expiresAt?.toIso8601String(),
    'delivered': delivered,
    'viewed': viewed,
    'completed': completed,
  };
}
