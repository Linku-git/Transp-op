import '../models/trip.dart';
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

  Future<List<Trip>> getUpcomingTrips() async {
    final response = await _apiClient.dio.get('/trips/upcoming');
    final data = response.data['data'] as List? ?? response.data as List? ?? [];
    return data.map((item) => Trip.fromJson(item)).toList();
  }

  Future<List<Trip>> getPastTrips({int page = 1, int pageSize = 20}) async {
    final response = await _apiClient.dio.get(
      '/trips/my',
      queryParameters: {'page': page, 'page_size': pageSize, 'status': 'completed,cancelled'},
    );
    final data = response.data['data'] as List? ?? response.data as List? ?? [];
    return data.map((item) => Trip.fromJson(item)).toList();
  }

  Future<Trip> getTripDetail(String tripId) async {
    final response = await _apiClient.dio.get('/trips/$tripId');
    return Trip.fromJson(response.data);
  }

  Future<void> cancelTrip(String tripId) async {
    await _apiClient.dio.delete('/trips/$tripId');
  }

  Future<Trip> modifyTrip(String tripId, {String? shiftId, String? pickupPointId}) async {
    final response = await _apiClient.dio.put(
      '/trips/$tripId',
      data: <String, dynamic>{
        if (shiftId != null) 'shift_id': shiftId,
        if (pickupPointId != null) 'pickup_point_id': pickupPointId,
      },
    );
    return Trip.fromJson(response.data);
  }
}
