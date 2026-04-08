class AuthToken {
  final String accessToken;
  final String refreshToken;
  final String tokenType;

  const AuthToken({
    required this.accessToken,
    required this.refreshToken,
    this.tokenType = 'bearer',
  });

  factory AuthToken.fromJson(Map<String, dynamic> json) {
    return AuthToken(
      accessToken: json['access_token'] as String,
      refreshToken: json['refresh_token'] as String,
      tokenType: json['token_type'] as String? ?? 'bearer',
    );
  }
}
