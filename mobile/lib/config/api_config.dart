class ApiConfig {
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'https://transpop.replit.app/api/v1',
  );

  static const String accessTokenKey = 'access_token';
  static const String refreshTokenKey = 'refresh_token';

  static const Duration connectTimeout = Duration(seconds: 15);
  static const Duration receiveTimeout = Duration(seconds: 30);

  // Auth endpoints
  static const String loginPath = '/auth/login';
  static const String refreshPath = '/auth/refresh';
  static const String logoutPath = '/auth/logout';
  static const String profilePath = '/auth/me';

  // Mobile-specific
  static const String offlineManifestPath = '/mobile/offline-manifest';
}
