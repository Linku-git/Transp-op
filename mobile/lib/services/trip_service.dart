import '../models/trip_booking.dart';
import 'api_client.dart';

class TripService {
  final ApiClient _apiClient;

  TripService({required ApiClient apiClient}) : _apiClient = apiClient;

  Future<List<Shift>> getSiteShifts(String siteId) async {
    final response = await _apiClient.dio.get(
      '/horaires-travail',
      queryParameters: {'site_id': siteId},
    );
    final data = response.data['data'] as List? ?? response.data as List? ?? [];
    return data.map((item) => Shift.fromJson(item)).toList();
  }

  Future<List<PickupPoint>> getNearbyPickupPoints({
    required double lat,
    required double lng,
    double radiusMeters = 2000,
  }) async {
    final response = await _apiClient.dio.get(
      '/points-arret',
      queryParameters: {'lat': lat, 'lng': lng, 'radius': radiusMeters},
    );
    final data = response.data['data'] as List? ?? response.data as List? ?? [];
    return data.map((item) => PickupPoint.fromJson(item)).toList();
  }

  Future<BookingConfirmation> bookTrip(TripBooking booking) async {
    final response = await _apiClient.dio.post(
      '/trips/book',
      data: booking.toJson(),
    );
    return BookingConfirmation.fromJson(response.data);
  }
}
