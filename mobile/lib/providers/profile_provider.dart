import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/user_profile.dart';
import '../services/profile_service.dart';
import '../utils/api_error.dart';
import 'auth_provider.dart';

final profileServiceProvider = Provider<ProfileService>((ref) {
  return ProfileService(apiClient: ref.watch(apiClientProvider));
});

class ProfileState {
  final UserProfile? profile;
  final bool isLoading;
  final bool isSaving;
  final String? error;
  final String? saveSuccess;

  const ProfileState({
    this.profile,
    this.isLoading = false,
    this.isSaving = false,
    this.error,
    this.saveSuccess,
  });

  ProfileState copyWith({
    UserProfile? profile,
    bool? isLoading,
    bool? isSaving,
    String? error,
    String? saveSuccess,
    bool clearMessages = false,
  }) {
    return ProfileState(
      profile: profile ?? this.profile,
      isLoading: isLoading ?? this.isLoading,
      isSaving: isSaving ?? this.isSaving,
      error: clearMessages ? null : error,
      saveSuccess: clearMessages ? null : saveSuccess,
    );
  }
}

class ProfileNotifier extends StateNotifier<ProfileState> {
  final ProfileService _service;

  ProfileNotifier(this._service) : super(const ProfileState());

  Future<void> load() async {
    state = state.copyWith(isLoading: true, clearMessages: true);
    try {
      final profile = await _service.getProfile();
      state = ProfileState(profile: profile);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: extractApiError(e, 'Erreur de chargement du profil'),
      );
    }
  }

  Future<bool> updateProfile({
    String? phone,
    bool? isPmr,
    double? pickupLat,
    double? pickupLng,
    String? pickupAddress,
  }) async {
    state = state.copyWith(isSaving: true, clearMessages: true);
    try {
      await _service.updateProfile(
        phone: phone,
        isPmr: isPmr,
        pickupLat: pickupLat,
        pickupLng: pickupLng,
        pickupAddress: pickupAddress,
      );
      await load();
      state = state.copyWith(saveSuccess: 'Profil mis à jour');
      return true;
    } catch (e) {
      state = state.copyWith(
        isSaving: false,
        error: extractApiError(e, 'Erreur de sauvegarde'),
      );
      return false;
    }
  }

  Future<bool> updatePreferences({
    String? transportMode,
    double? maxWalkingDistance,
    bool? volunteerDriver,
    int? carpoolSeats,
  }) async {
    state = state.copyWith(isSaving: true, clearMessages: true);
    try {
      await _service.updatePreferences(
        transportMode: transportMode,
        maxWalkingDistance: maxWalkingDistance,
        volunteerDriver: volunteerDriver,
        carpoolSeats: carpoolSeats,
      );
      await load();
      state = state.copyWith(saveSuccess: 'Préférences mises à jour');
      return true;
    } catch (e) {
      state = state.copyWith(
        isSaving: false,
        error: extractApiError(e, 'Erreur de sauvegarde'),
      );
      return false;
    }
  }
}

final profileProvider = StateNotifierProvider<ProfileNotifier, ProfileState>((ref) {
  return ProfileNotifier(ref.watch(profileServiceProvider));
});
