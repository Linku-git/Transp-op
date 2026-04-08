import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../utils/night_mode_helper.dart';

enum NightModePreference { auto, manual, off }

class NightModeState {
  final bool isActive;
  final NightModePreference preference;

  const NightModeState({
    this.isActive = false,
    this.preference = NightModePreference.auto,
  });

  NightModeState copyWith({bool? isActive, NightModePreference? preference}) {
    return NightModeState(
      isActive: isActive ?? this.isActive,
      preference: preference ?? this.preference,
    );
  }
}

class NightModeNotifier extends StateNotifier<NightModeState> {
  final FlutterSecureStorage _storage;
  Timer? _timer;

  NightModeNotifier({FlutterSecureStorage? storage})
      : _storage = storage ?? const FlutterSecureStorage(),
        super(const NightModeState()) {
    _initialize();
  }

  Future<void> _initialize() async {
    final pref = await _storage.read(key: 'night_mode_preference');
    final preference = switch (pref) {
      'manual' => NightModePreference.manual,
      'off' => NightModePreference.off,
      _ => NightModePreference.auto,
    };

    state = state.copyWith(preference: preference);
    _evaluate();

    // Re-evaluate every minute
    _timer = Timer.periodic(const Duration(minutes: 1), (_) => _evaluate());
  }

  void _evaluate() {
    switch (state.preference) {
      case NightModePreference.auto:
        state = state.copyWith(isActive: NightModeHelper.isNightTime());
      case NightModePreference.manual:
        // Keep current active state (user controls it)
        break;
      case NightModePreference.off:
        state = state.copyWith(isActive: false);
    }
  }

  Future<void> setPreference(NightModePreference pref) async {
    await _storage.write(key: 'night_mode_preference', value: pref.name);
    state = state.copyWith(preference: pref);
    _evaluate();
  }

  void toggle() {
    if (state.preference == NightModePreference.auto) {
      // Switch to manual mode
      state = state.copyWith(
        preference: NightModePreference.manual,
        isActive: !state.isActive,
      );
    } else {
      state = state.copyWith(isActive: !state.isActive);
    }
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }
}

final nightModeProvider =
    StateNotifierProvider<NightModeNotifier, NightModeState>((ref) {
  return NightModeNotifier();
});
