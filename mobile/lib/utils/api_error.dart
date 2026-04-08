import 'package:dio/dio.dart';

String extractApiError(dynamic error, [String fallback = 'Une erreur est survenue']) {
  if (error is DioException) {
    final data = error.response?.data;
    if (data is Map<String, dynamic>) {
      final detail = data['detail'];
      if (detail is String) return detail;
      if (detail is List) {
        return detail.map((e) => e is Map ? e['msg'] ?? '' : e.toString()).join(', ');
      }
    }
    if (error.type == DioExceptionType.connectionTimeout ||
        error.type == DioExceptionType.receiveTimeout) {
      return 'Connexion au serveur impossible. Vérifiez votre connexion.';
    }
    if (error.type == DioExceptionType.connectionError) {
      return 'Impossible de joindre le serveur.';
    }
  }
  if (error is String) return error;
  return fallback;
}
