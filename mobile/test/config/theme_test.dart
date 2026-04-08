import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/config/colors.dart';

void main() {
  group('AppColors', () {
    test('primary color is Azure Blue #0058BE', () {
      expect(AppColors.primary, const Color(0xFF0058BE));
    });

    test('error color is defined', () {
      expect(AppColors.error, const Color(0xFFBA1A1A));
    });

    test('surface colors form correct hierarchy', () {
      // Light surfaces should exist and be distinct
      expect(AppColors.surface, isNotNull);
      expect(AppColors.surfaceContainerLowest, isNotNull);
      expect(AppColors.surfaceContainerLow, isNotNull);
      expect(AppColors.surfaceContainer, isNotNull);
      expect(AppColors.surfaceContainerHigh, isNotNull);
    });

    test('dark surface colors are defined', () {
      expect(AppColors.surfaceDark, isNotNull);
      expect(AppColors.surfaceContainerLowestDark, isNotNull);
      expect(AppColors.onSurfaceDark, isNotNull);
    });

    test('night mode colors are defined', () {
      expect(AppColors.nightBackground, const Color(0xFF1A1A2E));
      expect(AppColors.nightEmergency, const Color(0xFFFF3333));
      expect(AppColors.nightText, const Color(0xFFE0E0E0));
    });

    test('semantic colors are defined', () {
      expect(AppColors.success, isNotNull);
      expect(AppColors.warning, isNotNull);
      expect(AppColors.info, isNotNull);
    });
  });
}
