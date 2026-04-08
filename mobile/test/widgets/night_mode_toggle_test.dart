import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:transpop_mobile/widgets/night_mode_toggle.dart';
import 'package:transpop_mobile/services/night_mode_service.dart';

void main() {
  group('NightModeToggle', () {
    testWidgets('renders mode nuit label', (tester) async {
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            nightModeProvider.overrideWith(
              (ref) => _StubNightModeNotifier(),
            ),
          ],
          child: const MaterialApp(
            home: Scaffold(body: NightModeToggle()),
          ),
        ),
      );

      expect(find.text('Mode nuit'), findsOneWidget);
    });
  });
}

class _StubNightModeNotifier extends StateNotifier<NightModeState>
    implements NightModeNotifier {
  _StubNightModeNotifier()
      : super(const NightModeState(
            isActive: false, preference: NightModePreference.auto));

  @override
  Future<void> setPreference(NightModePreference pref) async {
    state = state.copyWith(preference: pref);
  }

  @override
  void toggle() {
    state = state.copyWith(isActive: !state.isActive);
  }
}
