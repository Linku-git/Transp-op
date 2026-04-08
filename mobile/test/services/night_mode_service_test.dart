import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/services/night_mode_service.dart';

void main() {
  group('NightModeState', () {
    test('initial state', () {
      const state = NightModeState();
      expect(state.isActive, false);
      expect(state.preference, NightModePreference.auto);
    });

    test('copyWith updates correctly', () {
      const state = NightModeState();
      final updated = state.copyWith(isActive: true, preference: NightModePreference.manual);
      expect(updated.isActive, true);
      expect(updated.preference, NightModePreference.manual);
    });
  });

  group('NightModePreference', () {
    test('all values exist', () {
      expect(NightModePreference.values.length, 3);
      expect(NightModePreference.values, contains(NightModePreference.auto));
      expect(NightModePreference.values, contains(NightModePreference.manual));
      expect(NightModePreference.values, contains(NightModePreference.off));
    });
  });
}
