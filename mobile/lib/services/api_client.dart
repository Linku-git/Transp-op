import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../config/api_config.dart';

class ApiClient {
  late final Dio dio;
  final FlutterSecureStorage _storage;
  bool _isRefreshing = false;

  ApiClient({FlutterSecureStorage? storage})
      : _storage = storage ?? const FlutterSecureStorage() {
    dio = Dio(BaseOptions(
      baseUrl: ApiConfig.baseUrl,
      connectTimeout: ApiConfig.connectTimeout,
      receiveTimeout: ApiConfig.receiveTimeout,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ));

    dio.interceptors.add(InterceptorsWrapper(
      onRequest: _onRequest,
      onError: _onError,
    ));
  }

  Future<void> _onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    final token = await _storage.read(key: ApiConfig.accessTokenKey);
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }

  Future<void> _onError(
    DioException error,
    ErrorInterceptorHandler handler,
  ) async {
    if (error.response?.statusCode != 401 || _isRefreshing) {
      return handler.next(error);
    }

    // Skip refresh for auth endpoints themselves
    final path = error.requestOptions.path;
    if (path.contains('/auth/login') || path.contains('/auth/refresh')) {
      return handler.next(error);
    }

    _isRefreshing = true;
    try {
      final refreshToken = await _storage.read(key: ApiConfig.refreshTokenKey);
      if (refreshToken == null) {
        await _clearTokens();
        return handler.next(error);
      }

      final response = await Dio(BaseOptions(
        baseUrl: ApiConfig.baseUrl,
        connectTimeout: ApiConfig.connectTimeout,
        receiveTimeout: ApiConfig.receiveTimeout,
      )).post(
        ApiConfig.refreshPath,
        data: {'refresh_token': refreshToken},
      );

      final newAccessToken = response.data['access_token'] as String;
      final newRefreshToken = response.data['refresh_token'] as String;

      await _storage.write(key: ApiConfig.accessTokenKey, value: newAccessToken);
      await _storage.write(key: ApiConfig.refreshTokenKey, value: newRefreshToken);

      // Retry original request with new token
      final opts = error.requestOptions;
      opts.headers['Authorization'] = 'Bearer $newAccessToken';
      final retryResponse = await dio.fetch(opts);
      return handler.resolve(retryResponse);
    } on DioException {
      await _clearTokens();
      return handler.next(error);
    } finally {
      _isRefreshing = false;
    }
  }

  Future<void> _clearTokens() async {
    await _storage.delete(key: ApiConfig.accessTokenKey);
    await _storage.delete(key: ApiConfig.refreshTokenKey);
    await _storage.delete(key: 'user_id');
  }
}
