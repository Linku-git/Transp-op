import '../models/departure.dart';
import 'api_client.dart';

class DepartureService {
  final ApiClient _apiClient;

  DepartureService({required ApiClient apiClient}) : _apiClient = apiClient;

  Future<Departure?> getNextDeparture() async {
    try {
      final response = await _apiClient.dio.get('/trips/next');
      if (response.data == null) return null;
      return Departure.fromJson(response.data);
    } catch (_) {
      return null;
    }
  }

  Future<List<ContentItem>> getLatestContent({int limit = 5}) async {
    try {
      final response = await _apiClient.dio.get(
        '/content',
        queryParameters: {'page_size': limit, 'page': 1},
      );
      final data = response.data['data'] as List? ?? [];
      return data.map((item) => ContentItem.fromJson(item)).toList();
    } catch (_) {
      return [];
    }
  }

  Future<int> getUnreadNotificationCount() async {
    try {
      final response = await _apiClient.dio.get('/notifications/unread-count');
      return response.data['count'] as int? ?? 0;
    } catch (_) {
      return 0;
    }
  }
}
