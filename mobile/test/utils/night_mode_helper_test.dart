import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/utils/night_mode_helper.dart';

void main() {
  group('NightModeHelper', () {
    test('10pm is night time', () {
      final time = DateTime(2026, 4, 8, 22, 0);
      expect(NightModeHelper.isNightTime(time), true);
    });

    test('11pm is night time', () {
      final time = DateTime(2026, 4, 8, 23, 30);
      expect(NightModeHelper.isNightTime(time), true);
    });

    test('3am is night time', () {
      final time = DateTime(2026, 4, 8, 3, 0);
      expect(NightModeHelper.isNightTime(time), true);
    });

    test('6:30am is night time', () {
      final time = DateTime(2026, 4, 8, 6, 30);
      expect(NightModeHelper.isNightTime(time), true);
    });

    test('6:31am is day time', () {
      final time = DateTime(2026, 4, 8, 6, 31);
      expect(NightModeHelper.isNightTime(time), false);
    });

    test('noon is day time', () {
      final time = DateTime(2026, 4, 8, 12, 0);
      expect(NightModeHelper.isNightTime(time), false);
    });

    test('3pm is day time', () {
      final time = DateTime(2026, 4, 8, 15, 0);
      expect(NightModeHelper.isNightTime(time), false);
    });

    test('7:59pm is day time', () {
      final time = DateTime(2026, 4, 8, 19, 59);
      expect(NightModeHelper.isNightTime(time), false);
    });

    test('8pm is night time', () {
      final time = DateTime(2026, 4, 8, 20, 0);
      expect(NightModeHelper.isNightTime(time), true);
    });
  });
}
