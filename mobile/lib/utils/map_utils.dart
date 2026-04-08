import 'package:flutter/material.dart';
import '../config/colors.dart';

class MapUtils {
  MapUtils._();

  static Color etaColor(int? etaSeconds) {
    if (etaSeconds == null) return AppColors.outline;
    if (etaSeconds <= 90) return AppColors.success;
    if (etaSeconds <= 180) return AppColors.warning;
    return AppColors.error;
  }

  static String formatEta(int? etaSeconds) {
    if (etaSeconds == null) return '--';
    if (etaSeconds <= 0) return 'Arrivé';
    final minutes = etaSeconds ~/ 60;
    final seconds = etaSeconds % 60;
    if (minutes > 0) {
      return '${minutes}min ${seconds.toString().padLeft(2, '0')}s';
    }
    return '${seconds}s';
  }

  static String formatEtaShort(int? etaSeconds) {
    if (etaSeconds == null) return '--';
    if (etaSeconds <= 0) return '0s';
    if (etaSeconds > 3600) return '${etaSeconds ~/ 60}min';
    final minutes = etaSeconds ~/ 60;
    final seconds = etaSeconds % 60;
    if (minutes > 0) return '$minutes:${seconds.toString().padLeft(2, '0')}';
    return '${seconds}s';
  }
}
