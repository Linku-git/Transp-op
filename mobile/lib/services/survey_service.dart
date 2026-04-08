import 'package:hive_flutter/hive_flutter.dart';

import '../models/survey.dart';
import 'api_client.dart';

class SurveyService {
  final ApiClient _apiClient;
  static const String _queueBoxName = 'survey_offline_queue';

  SurveyService({required ApiClient apiClient}) : _apiClient = apiClient;

  /// Fetch survey by ID.
  Future<SurveyData> getSurvey(String surveyId) async {
    final response = await _apiClient.dio.get('/surveys/$surveyId');
    return SurveyData.fromJson(response.data);
  }

  /// Submit survey response.
  Future<void> submitResponse({
    required String surveyId,
    String? employeeId,
    required List<SurveyAnswer> answers,
  }) async {
    await _apiClient.dio.post(
      '/surveys/$surveyId/respond',
      data: {
        if (employeeId != null) 'employee_id': employeeId,
        'responses': answers.map((a) => a.toJson()).toList(),
      },
    );
  }

  /// Queue response for offline submission.
  Future<void> queueOfflineResponse({
    required String surveyId,
    String? employeeId,
    required List<SurveyAnswer> answers,
  }) async {
    try {
      final box = await Hive.openBox(_queueBoxName);
      final queue = (box.get('pending') as List?)?.cast<Map>() ?? [];
      queue.add({
        'survey_id': surveyId,
        'employee_id': employeeId,
        'answers': answers.map((a) => a.toJson()).toList(),
        'queued_at': DateTime.now().toIso8601String(),
      });
      await box.put('pending', queue);
    } catch (_) {
      // Non-critical
    }
  }

  /// Submit all queued responses.
  Future<int> submitQueuedResponses() async {
    try {
      final box = await Hive.openBox(_queueBoxName);
      final queue = (box.get('pending') as List?)?.cast<Map>() ?? [];
      if (queue.isEmpty) return 0;

      int submitted = 0;
      final remaining = <Map>[];

      for (final item in queue) {
        try {
          final answers = (item['answers'] as List)
              .map((a) => SurveyAnswer(
                    questionId: a['question_id'] as String,
                    value: a['value'],
                  ))
              .toList();
          await submitResponse(
            surveyId: item['survey_id'] as String,
            employeeId: item['employee_id'] as String?,
            answers: answers,
          );
          submitted++;
        } catch (_) {
          remaining.add(item);
        }
      }

      await box.put('pending', remaining);
      return submitted;
    } catch (_) {
      return 0;
    }
  }

  /// Get count of queued responses.
  Future<int> getQueuedCount() async {
    try {
      final box = await Hive.openBox(_queueBoxName);
      final queue = box.get('pending') as List?;
      return queue?.length ?? 0;
    } catch (_) {
      return 0;
    }
  }
}
