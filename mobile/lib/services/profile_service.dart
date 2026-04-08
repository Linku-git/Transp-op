import '../models/user_profile.dart';
import 'api_client.dart';

class ProfileService {
  final ApiClient _apiClient;

  ProfileService({required ApiClient apiClient}) : _apiClient = apiClient;

  Future<UserProfile> getProfile() async {
    final response = await _apiClient.dio.get('/employees/me');
    return UserProfile.fromJson(response.data);
  }

  Future<void> updateProfile({
    String? phone,
    bool? isPmr,
    double? pickupLat,
    double? pickupLng,
    String? pickupAddress,
  }) async {
    await _apiClient.dio.patch(
      '/employees/me',
      data: <String, dynamic>{
        if (phone != null) 'phone': phone,
        if (isPmr != null) 'is_pmr': isPmr,
        if (pickupLat != null) 'pickup_lat': pickupLat,
        if (pickupLng != null) 'pickup_lng': pickupLng,
        if (pickupAddress != null) 'pickup_address': pickupAddress,
      },
    );
  }

  Future<void> updatePreferences({
    String? transportMode,
    double? maxWalkingDistance,
    bool? volunteerDriver,
    int? carpoolSeats,
  }) async {
    await _apiClient.dio.patch(
      '/employees/me/preferences',
      data: <String, dynamic>{
        if (transportMode != null) 'current_transport_mode': transportMode,
        if (maxWalkingDistance != null)
          'max_walking_distance_meters': maxWalkingDistance.round(),
        if (volunteerDriver != null) 'volunteer_driver': volunteerDriver,
        if (carpoolSeats != null) 'carpool_seats': carpoolSeats,
      },
    );
  }

  Future<void> updateNotificationPreferences(NotificationPreferences prefs) async {
    await _apiClient.dio.patch(
      '/employees/me/notification-preferences',
      data: prefs.toJson(),
    );
  }
}
