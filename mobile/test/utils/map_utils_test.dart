import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/config/colors.dart';
import 'package:transpop_mobile/utils/map_utils.dart';

void main() {
  group('MapUtils.etaColor', () {
    test('green for <=90 seconds', () {
      expect(MapUtils.etaColor(90), AppColors.success);
      expect(MapUtils.etaColor(30), AppColors.success);
    });

    test('orange for 91-180 seconds', () {
      expect(MapUtils.etaColor(91), AppColors.warning);
      expect(MapUtils.etaColor(180), AppColors.warning);
    });

    test('red for >180 seconds', () {
      expect(MapUtils.etaColor(181), AppColors.error);
      expect(MapUtils.etaColor(600), AppColors.error);
    });

    test('outline for null', () {
      expect(MapUtils.etaColor(null), AppColors.outline);
    });
  });

  group('MapUtils.formatEta', () {
    test('returns Arrivé for 0', () {
      expect(MapUtils.formatEta(0), 'Arrivé');
    });

    test('returns seconds for <60', () {
      expect(MapUtils.formatEta(45), '45s');
    });

    test('returns minutes and seconds for >=60', () {
      expect(MapUtils.formatEta(125), '2min 05s');
    });

    test('returns -- for null', () {
      expect(MapUtils.formatEta(null), '--');
    });

    test('returns Arrivé for negative', () {
      expect(MapUtils.formatEta(-5), 'Arrivé');
    });
  });

  group('MapUtils.formatEtaShort', () {
    test('returns 0s for 0', () {
      expect(MapUtils.formatEtaShort(0), '0s');
    });

    test('returns seconds for <60', () {
      expect(MapUtils.formatEtaShort(30), '30s');
    });

    test('returns min:sec for >=60', () {
      expect(MapUtils.formatEtaShort(125), '2:05');
    });
  });
}
