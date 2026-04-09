import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/utils/accessibility_helper.dart';

void main() {
  group('Touch Targets', () {
    test('minimum touch target is 48dp', () {
      expect(kMinTouchTarget, 48.0);
    });

    test('valid touch target passes', () {
      expect(meetsMinTouchTarget(48, 48), true);
    });

    test('large touch target passes', () {
      expect(meetsMinTouchTarget(56, 56), true);
    });

    test('small touch target fails', () {
      expect(meetsMinTouchTarget(32, 32), false);
    });

    test('narrow touch target fails', () {
      expect(meetsMinTouchTarget(48, 30), false);
    });
  });

  group('Semantic Labels', () {
    test('back button label', () {
      expect(SemanticLabels.backButton, 'Retour');
    });

    test('close button label', () {
      expect(SemanticLabels.closeButton, 'Fermer');
    });

    test('loading indicator label', () {
      expect(SemanticLabels.loadingIndicator, 'Chargement en cours');
    });

    test('all labels are non-empty', () {
      final labels = [
        SemanticLabels.backButton,
        SemanticLabels.closeButton,
        SemanticLabels.menuButton,
        SemanticLabels.searchField,
        SemanticLabels.refreshButton,
        SemanticLabels.deleteButton,
        SemanticLabels.editButton,
        SemanticLabels.submitButton,
        SemanticLabels.cancelButton,
        SemanticLabels.loadingIndicator,
        SemanticLabels.errorMessage,
        SemanticLabels.successMessage,
      ];
      for (final label in labels) {
        expect(label.isNotEmpty, true);
      }
    });
  });

  group('Contrast Ratios', () {
    test('primary text passes AA', () {
      expect(
        ContrastRatios.passesAA(ContrastRatios.primaryTextOnSurface),
        true,
      );
    });

    test('secondary text passes AA', () {
      expect(
        ContrastRatios.passesAA(ContrastRatios.secondaryTextOnSurface),
        true,
      );
    });

    test('primary on white passes AA', () {
      expect(
        ContrastRatios.passesAA(ContrastRatios.primaryOnWhite),
        true,
      );
    });

    test('error on white passes AA', () {
      expect(
        ContrastRatios.passesAA(ContrastRatios.errorOnWhite),
        true,
      );
    });

    test('insufficient contrast fails AA', () {
      expect(ContrastRatios.passesAA(3.0), false);
    });

    test('large text has lower threshold', () {
      expect(ContrastRatios.passesAA(3.5, isLargeText: true), true);
    });
  });

  group('Mobile A11y Audit', () {
    test('all screens audited', () {
      expect(mobileA11yAudit.length, greaterThanOrEqualTo(10));
    });

    test('all screens pass voiceover', () {
      for (final entry in mobileA11yAudit.entries) {
        expect(entry.value['voiceover'], 'PASS',
            reason: '${entry.key} voiceover should PASS');
      }
    });

    test('all screens pass talkback', () {
      for (final entry in mobileA11yAudit.entries) {
        expect(entry.value['talkback'], 'PASS',
            reason: '${entry.key} talkback should PASS');
      }
    });

    test('all screens pass touch targets', () {
      for (final entry in mobileA11yAudit.entries) {
        expect(entry.value['touch_targets'], 'PASS',
            reason: '${entry.key} touch_targets should PASS');
      }
    });
  });
}
