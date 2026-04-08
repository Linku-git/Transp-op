import 'package:hive_flutter/hive_flutter.dart';

import '../models/training.dart';
import '../models/content_feed.dart';
import 'api_client.dart';

class TrainingService {
  final ApiClient _apiClient;
  static const String _cacheBoxName = 'training_cache';

  TrainingService({required ApiClient apiClient}) : _apiClient = apiClient;

  /// Fetch training content with quiz questions.
  /// Uses the content API + constructs quiz from body metadata.
  Future<TrainingContent> getTraining(String contentId) async {
    final response = await _apiClient.dio.get('/content/$contentId');
    final data = response.data as Map<String, dynamic>;

    // Build training content from API response
    return TrainingContent(
      id: data['id'] as String,
      title: data['title'] as String,
      body: data['body'] as String?,
      mediaUrl: data['media_url'] as String?,
      mediaType: _inferMediaType(data['media_url'] as String?),
      questions: _extractQuestions(data),
      publishedAt: data['published_at'] != null
          ? DateTime.parse(data['published_at'] as String)
          : null,
    );
  }

  /// Submit quiz score to backend.
  Future<void> submitScore({
    required String contentId,
    required String employeeId,
    required double score,
    required int timeSpentSeconds,
  }) async {
    await _apiClient.dio.post(
      '/content/$contentId/complete',
      queryParameters: {'employee_id': employeeId},
      data: {
        'quiz_score': score,
        'time_spent_seconds': timeSpentSeconds,
      },
    );
  }

  /// Mark training as viewed.
  Future<void> markViewed(String contentId, String employeeId) async {
    await _apiClient.dio.post(
      '/content/$contentId/view',
      queryParameters: {'employee_id': employeeId},
    );
  }

  /// Cache training for offline playback.
  Future<void> cacheTraining(TrainingContent training) async {
    try {
      final box = await Hive.openBox(_cacheBoxName);
      await box.put('training_${training.id}', {
        'id': training.id,
        'title': training.title,
        'body': training.body,
        'media_url': training.mediaUrl,
        'published_at': training.publishedAt?.toIso8601String(),
      });
    } catch (_) {
      // Non-critical
    }
  }

  /// Get cached training content.
  Future<TrainingContent?> getCachedTraining(String contentId) async {
    try {
      final box = await Hive.openBox(_cacheBoxName);
      final data = box.get('training_$contentId');
      if (data == null) return null;
      final map = Map<String, dynamic>.from(data);
      return TrainingContent(
        id: map['id'] as String,
        title: map['title'] as String,
        body: map['body'] as String?,
        mediaUrl: map['media_url'] as String?,
      );
    } catch (_) {
      return null;
    }
  }

  MediaType _inferMediaType(String? url) {
    if (url == null) return MediaType.video;
    if (url.contains('.mp3') || url.contains('.wav') || url.contains('.ogg')) {
      return MediaType.audio;
    }
    return MediaType.video;
  }

  /// Extract quiz questions from content body or metadata.
  /// In production, this would parse structured quiz data from the API.
  /// For now, we support a simple JSON-encoded quiz in the body.
  List<QuizQuestion> _extractQuestions(Map<String, dynamic> data) {
    final questions = data['questions'] as List?;
    if (questions == null) return [];
    return questions
        .map((q) => QuizQuestion.fromJson(q as Map<String, dynamic>))
        .toList();
  }
}
