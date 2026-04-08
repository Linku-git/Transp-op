import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/models/auth_token.dart';

void main() {
  group('AuthToken', () {
    test('fromJson parses correctly', () {
      final json = {
        'access_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.test',
        'refresh_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.refresh',
        'token_type': 'bearer',
      };

      final token = AuthToken.fromJson(json);

      expect(token.accessToken, startsWith('eyJ'));
      expect(token.refreshToken, startsWith('eyJ'));
      expect(token.tokenType, 'bearer');
    });

    test('fromJson defaults token_type to bearer', () {
      final json = {
        'access_token': 'abc',
        'refresh_token': 'def',
      };

      final token = AuthToken.fromJson(json);
      expect(token.tokenType, 'bearer');
    });
  });
}
