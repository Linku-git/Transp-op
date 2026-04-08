import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/trip_booking.dart';
import '../services/trip_service.dart';
import '../utils/api_error.dart';
import 'auth_provider.dart';

final tripServiceProvider = Provider<TripService>((ref) {
  return TripService(apiClient: ref.watch(apiClientProvider));
});

class TripBookingState {
  final DateTime selectedDate;
  final List<Shift> shifts;
  final String? selectedShiftId;
  final PickupPoint? defaultPickupPoint;
  final PickupPoint? selectedPickupPoint;
  final List<PickupPoint> availablePickupPoints;
  final bool isLoadingShifts;
  final bool isSubmitting;
  final BookingConfirmation? confirmation;
  final String? error;

  TripBookingState({
    DateTime? selectedDate,
    this.shifts = const [],
    this.selectedShiftId,
    this.defaultPickupPoint,
    this.selectedPickupPoint,
    this.availablePickupPoints = const [],
    this.isLoadingShifts = false,
    this.isSubmitting = false,
    this.confirmation,
    this.error,
  }) : selectedDate = selectedDate ?? DateTime.now();

  Shift? get selectedShift =>
      selectedShiftId == null ? null : shifts.cast<Shift?>().firstWhere(
            (s) => s?.id == selectedShiftId,
            orElse: () => null,
          );

  PickupPoint? get activePickupPoint => selectedPickupPoint ?? defaultPickupPoint;

  bool get canConfirm =>
      selectedShiftId != null && activePickupPoint != null && !isSubmitting;

  TripBookingState copyWith({
    DateTime? selectedDate,
    List<Shift>? shifts,
    String? selectedShiftId,
    PickupPoint? defaultPickupPoint,
    PickupPoint? selectedPickupPoint,
    List<PickupPoint>? availablePickupPoints,
    bool? isLoadingShifts,
    bool? isSubmitting,
    BookingConfirmation? confirmation,
    String? error,
    bool clearShiftId = false,
    bool clearConfirmation = false,
  }) {
    return TripBookingState(
      selectedDate: selectedDate ?? this.selectedDate,
      shifts: shifts ?? this.shifts,
      selectedShiftId: clearShiftId ? null : (selectedShiftId ?? this.selectedShiftId),
      defaultPickupPoint: defaultPickupPoint ?? this.defaultPickupPoint,
      selectedPickupPoint: selectedPickupPoint ?? this.selectedPickupPoint,
      availablePickupPoints: availablePickupPoints ?? this.availablePickupPoints,
      isLoadingShifts: isLoadingShifts ?? this.isLoadingShifts,
      isSubmitting: isSubmitting ?? this.isSubmitting,
      confirmation: clearConfirmation ? null : (confirmation ?? this.confirmation),
      error: error,
    );
  }
}

class TripBookingNotifier extends StateNotifier<TripBookingState> {
  final TripService _service;

  TripBookingNotifier(this._service) : super(TripBookingState());

  Future<void> loadShifts(String siteId) async {
    state = state.copyWith(isLoadingShifts: true, error: null);
    try {
      final shifts = await _service.getSiteShifts(siteId);
      state = state.copyWith(shifts: shifts, isLoadingShifts: false);
    } catch (e) {
      state = state.copyWith(
        isLoadingShifts: false,
        error: extractApiError(e, 'Erreur de chargement des horaires'),
      );
    }
  }

  void selectDate(DateTime date) {
    state = state.copyWith(selectedDate: date);
  }

  void selectShift(Shift shift) {
    state = state.copyWith(selectedShiftId: shift.id);
  }

  void selectPickupPoint(PickupPoint point) {
    state = state.copyWith(selectedPickupPoint: point);
  }

  void setDefaultPickupPoint(PickupPoint point) {
    state = state.copyWith(defaultPickupPoint: point);
  }

  Future<bool> confirmBooking() async {
    final shift = state.selectedShift;
    final pickup = state.activePickupPoint;
    if (shift == null || pickup == null) return false;

    state = state.copyWith(isSubmitting: true, error: null);
    try {
      final booking = TripBooking(
        date: state.selectedDate,
        shiftId: shift.id,
        shiftLabel: shift.label,
        pickupPointId: pickup.id,
        pickupPointName: pickup.name,
        pickupLat: pickup.lat,
        pickupLng: pickup.lng,
      );
      final confirmation = await _service.bookTrip(booking);
      state = state.copyWith(isSubmitting: false, confirmation: confirmation);
      return true;
    } catch (e) {
      state = state.copyWith(
        isSubmitting: false,
        error: extractApiError(e, 'Erreur lors de la réservation'),
      );
      return false;
    }
  }
}

final tripBookingProvider =
    StateNotifierProvider<TripBookingNotifier, TripBookingState>((ref) {
  return TripBookingNotifier(ref.watch(tripServiceProvider));
});
