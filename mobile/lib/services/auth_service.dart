import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../config/api_config.dart';
import '../models/auth_token.dart';
import '../models/user.dart';
import 'api_client.dart';

class AuthService {
  final ApiClient _apiClient;
  final FlutterSecureStorage _storage;

  AuthService({
    required ApiClient apiClient,
    FlutterSecureStorage? storage,
  })  : _apiClient = apiClient,
        _storage = storage ?? const FlutterSecureStorage();

  Dio get _dio => _apiClient.dio;

  Future<User> login(String email, String password) async {
    final response = await _dio.post(
      ApiConfig.loginPath,
      data: {'email': email, 'password': password},
    );

    final token = AuthToken.fromJson(response.data);
    await _storeTokens(token);

    return getProfile();
  }

  Future<User> getProfile() async {
    final response = await _dio.get(ApiConfig.profilePath);
    final user = User.fromJson(response.data);
    await _storage.write(key: 'user_id', value: user.id);
    return user;
  }

  Future<bool> tryRefresh() async {
    final refreshToken = await _storage.read(key: ApiConfig.refreshTokenKey);
    if (refreshToken == null) return false;

    try {
      final response = await _dio.post(
        ApiConfig.refreshPath,
        data: {'refresh_token': refreshToken},
      );

      final token = AuthToken.fromJson(response.data);
      await _storeTokens(token);
      return true;
    } on DioException {
      return false;
    }
  }

  Future<void> logout() async {
    try {
      await _dio.post(ApiConfig.logoutPath);
    } on DioException {
      // Ignore server errors during logout
    } finally {
      await clearSession();
    }
  }

  Future<void> clearSession() async {
    await _storage.delete(key: ApiConfig.accessTokenKey);
    await _storage.delete(key: ApiConfig.refreshTokenKey);
    await _storage.delete(key: 'user_id');
    await _storage.delete(key: 'biometric_enabled');
  }

  Future<bool> hasStoredSession() async {
    final token = await _storage.read(key: ApiConfig.refreshTokenKey);
    return token != null;
  }

  Future<bool> isBiometricEnabled() async {
    final value = await _storage.read(key: 'biometric_enabled');
    return value == 'true';
  }

  Future<void> setBiometricEnabled(bool enabled) async {
    await _storage.write(
      key: 'biometric_enabled',
      value: enabled.toString(),
    );
  }

  Future<void> _storeTokens(AuthToken token) async {
    await _storage.write(key: ApiConfig.accessTokenKey, value: token.accessToken);
    await _storage.write(key: ApiConfig.refreshTokenKey, value: token.refreshToken);
  }
}
