import '../models/vehicle_position.dart';
import 'api_client.dart';

class VehicleTrackingService {
  final ApiClient _apiClient;

  VehicleTrackingService({required ApiClient apiClient}) : _apiClient = apiClient;

  Future<VehiclePosition?> getLatestPosition(String vehicleId) async {
    try {
      final response = await _apiClient.dio.get('/rti/vehicle/$vehicleId/position');
      return VehiclePosition.fromJson(response.data);
    } catch (_) {
      return null;
    }
  }

  Future<Map<String, dynamic>?> getTrackingInfo() async {
    try {
      final response = await _apiClient.dio.get('/rti/tracking-info');
      return response.data as Map<String, dynamic>;
    } catch (_) {
      return null;
    }
  }
}
