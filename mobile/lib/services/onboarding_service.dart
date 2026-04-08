import '../models/transport_preferences.dart';
import '../models/security_preferences.dart';
import 'api_client.dart';

class OnboardingService {
  final ApiClient _apiClient;

  OnboardingService({required ApiClient apiClient}) : _apiClient = apiClient;

  Future<void> savePreferences({
    required TransportPreferences transport,
    required SecurityPreferences security,
  }) async {
    await _apiClient.dio.patch(
      '/employees/me/preferences',
      data: {
        ...transport.toJson(),
        ...security.toJson(),
        'onboarding_completed': true,
      },
    );
  }
}
