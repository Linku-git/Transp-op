import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/utils/api_error.dart';

void main() {
  group('extractApiError', () {
    test('extracts string detail from DioException', () {
      final error = DioException(
        requestOptions: RequestOptions(path: '/test'),
        response: Response(
          requestOptions: RequestOptions(path: '/test'),
          statusCode: 401,
          data: {'detail': 'Invalid email or password'},
        ),
      );

      expect(extractApiError(error), 'Invalid email or password');
    });

    test('extracts Pydantic v2 array detail', () {
      final error = DioException(
        requestOptions: RequestOptions(path: '/test'),
        response: Response(
          requestOptions: RequestOptions(path: '/test'),
          statusCode: 422,
          data: {
            'detail': [
              {'type': 'value_error', 'loc': ['body', 'email'], 'msg': 'Invalid email format'},
              {'type': 'value_error', 'loc': ['body', 'password'], 'msg': 'Too short'},
            ]
          },
        ),
      );

      final result = extractApiError(error);
      expect(result, contains('Invalid email format'));
      expect(result, contains('Too short'));
    });

    test('returns fallback for connection timeout', () {
      final error = DioException(
        requestOptions: RequestOptions(path: '/test'),
        type: DioExceptionType.connectionTimeout,
      );

      expect(extractApiError(error), contains('Connexion'));
    });

    test('returns fallback for connection error', () {
      final error = DioException(
        requestOptions: RequestOptions(path: '/test'),
        type: DioExceptionType.connectionError,
      );

      expect(extractApiError(error), contains('serveur'));
    });

    test('returns custom fallback when provided', () {
      expect(extractApiError(42, 'Custom error'), 'Custom error');
    });

    test('returns string directly', () {
      expect(extractApiError('Direct error'), 'Direct error');
    });

    test('returns default fallback for unknown type', () {
      expect(extractApiError(null), 'Une erreur est survenue');
    });
  });
}
