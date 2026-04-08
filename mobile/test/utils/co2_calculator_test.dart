import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/utils/co2_calculator.dart';

void main() {
  group('Co2Calculator', () {
    test('savedPerTripKg calculates correctly', () {
      // 10km trip: car=1200g, bus=300g, saved=900g=0.9kg
      final saved = Co2Calculator.savedPerTripKg(10.0);
      expect(saved, closeTo(0.9, 0.01));
    });

    test('savedPerTripKg returns 0 for 0 distance', () {
      expect(Co2Calculator.savedPerTripKg(0), 0);
    });

    test('totalSavedKg sums correctly', () {
      final total = Co2Calculator.totalSavedKg([10.0, 20.0]);
      // 10km=0.9kg + 20km=1.8kg = 2.7kg
      expect(total, closeTo(2.7, 0.01));
    });

    test('formatCo2 uses kg for small values', () {
      expect(Co2Calculator.formatCo2(15.3), '15.3 kg');
    });

    test('formatCo2 uses tonnes for large values', () {
      expect(Co2Calculator.formatCo2(1500), '1.5 t');
    });

    test('treesEquivalent calculates correctly', () {
      // 22 kg = 1 tree
      expect(Co2Calculator.treesEquivalent(22), 1);
      expect(Co2Calculator.treesEquivalent(44), 2);
      expect(Co2Calculator.treesEquivalent(100), 5);
    });
  });
}
