import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/config/api_config.dart';

void main() {
  group('ApiConfig', () {
    test('base URL has default value', () {
      expect(ApiConfig.baseUrl, isNotEmpty);
      expect(ApiConfig.baseUrl, contains('/api/v1'));
    });

    test('auth endpoints are defined', () {
      expect(ApiConfig.loginPath, '/auth/login');
      expect(ApiConfig.refreshPath, '/auth/refresh');
      expect(ApiConfig.logoutPath, '/auth/logout');
      expect(ApiConfig.profilePath, '/auth/me');
    });

    test('timeouts are reasonable', () {
      expect(ApiConfig.connectTimeout.inSeconds, greaterThan(0));
      expect(ApiConfig.receiveTimeout.inSeconds, greaterThan(0));
      expect(ApiConfig.connectTimeout.inSeconds, lessThanOrEqualTo(30));
    });

    test('token storage keys are defined', () {
      expect(ApiConfig.accessTokenKey, isNotEmpty);
      expect(ApiConfig.refreshTokenKey, isNotEmpty);
    });
  });
}
