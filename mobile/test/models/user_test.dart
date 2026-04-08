import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/models/user.dart';

void main() {
  group('User', () {
    test('fromJson parses correctly', () {
      final json = {
        'id': '123e4567-e89b-12d3-a456-426614174000',
        'email': 'test@transpop.dev',
        'first_name': 'Jean',
        'last_name': 'Dupont',
        'role_id': '223e4567-e89b-12d3-a456-426614174000',
        'tenant_id': '323e4567-e89b-12d3-a456-426614174000',
        'mfa_enabled': false,
        'is_active': true,
      };

      final user = User.fromJson(json);

      expect(user.id, '123e4567-e89b-12d3-a456-426614174000');
      expect(user.email, 'test@transpop.dev');
      expect(user.firstName, 'Jean');
      expect(user.lastName, 'Dupont');
      expect(user.mfaEnabled, false);
      expect(user.isActive, true);
    });

    test('fromJson handles null optional fields', () {
      final json = {
        'id': '123',
        'email': 'test@transpop.dev',
        'first_name': null,
        'last_name': null,
        'role_id': '223',
        'tenant_id': '323',
      };

      final user = User.fromJson(json);
      expect(user.firstName, isNull);
      expect(user.lastName, isNull);
      expect(user.mfaEnabled, false);
      expect(user.isActive, true);
    });

    test('displayName returns full name when both set', () {
      final user = User(
        id: '1',
        email: 'test@test.com',
        firstName: 'Jean',
        lastName: 'Dupont',
        roleId: '2',
        tenantId: '3',
      );
      expect(user.displayName, 'Jean Dupont');
    });

    test('displayName returns email when no name', () {
      final user = User(
        id: '1',
        email: 'test@test.com',
        roleId: '2',
        tenantId: '3',
      );
      expect(user.displayName, 'test@test.com');
    });

    test('toJson produces correct map', () {
      final user = User(
        id: '1',
        email: 'test@test.com',
        firstName: 'Jean',
        lastName: 'Dupont',
        roleId: '2',
        tenantId: '3',
        mfaEnabled: true,
        isActive: true,
      );

      final json = user.toJson();
      expect(json['id'], '1');
      expect(json['email'], 'test@test.com');
      expect(json['first_name'], 'Jean');
      expect(json['mfa_enabled'], true);
    });
  });
}
