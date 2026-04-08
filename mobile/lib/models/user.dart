class User {
  final String id;
  final String email;
  final String? firstName;
  final String? lastName;
  final String roleId;
  final String tenantId;
  final bool mfaEnabled;
  final bool isActive;

  const User({
    required this.id,
    required this.email,
    this.firstName,
    this.lastName,
    required this.roleId,
    required this.tenantId,
    this.mfaEnabled = false,
    this.isActive = true,
  });

  String get displayName {
    if (firstName != null && lastName != null) {
      return '$firstName $lastName';
    }
    if (firstName != null) return firstName!;
    if (lastName != null) return lastName!;
    return email;
  }

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] as String,
      email: json['email'] as String,
      firstName: json['first_name'] as String?,
      lastName: json['last_name'] as String?,
      roleId: json['role_id'] as String,
      tenantId: json['tenant_id'] as String,
      mfaEnabled: json['mfa_enabled'] as bool? ?? false,
      isActive: json['is_active'] as bool? ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'first_name': firstName,
      'last_name': lastName,
      'role_id': roleId,
      'tenant_id': tenantId,
      'mfa_enabled': mfaEnabled,
      'is_active': isActive,
    };
  }
}
