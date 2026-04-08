import 'dart:math' as math;
import 'package:flutter/material.dart';
import '../config/colors.dart';

class TransportModePieChart extends StatelessWidget {
  final Map<String, int> distribution;

  const TransportModePieChart({super.key, required this.distribution});

  static const _colors = [
    AppColors.primary,
    AppColors.success,
    AppColors.warning,
    AppColors.tertiary,
    AppColors.secondary,
    Colors.purple,
    Colors.cyan,
    Colors.pink,
  ];

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    if (distribution.isEmpty) return const SizedBox.shrink();

    final total = distribution.values.fold<int>(0, (sum, v) => sum + v);
    if (total == 0) return const SizedBox.shrink();

    final entries = distribution.entries.toList();

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'RÉPARTITION PAR MODE',
              style: theme.textTheme.labelSmall?.copyWith(
                fontWeight: FontWeight.w700,
                letterSpacing: 1,
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                SizedBox(
                  width: 120,
                  height: 120,
                  child: CustomPaint(
                    painter: _PieChartPainter(
                      data: entries.map((e) => e.value.toDouble()).toList(),
                      colors: List.generate(entries.length, (i) => _colors[i % _colors.length]),
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: entries.asMap().entries.map((entry) {
                      final idx = entry.key;
                      final e = entry.value;
                      final pct = (e.value / total * 100).round();
                      return Padding(
                        padding: const EdgeInsets.only(bottom: 6),
                        child: Row(
                          children: [
                            Container(
                              width: 10,
                              height: 10,
                              decoration: BoxDecoration(
                                color: _colors[idx % _colors.length],
                                borderRadius: BorderRadius.circular(2),
                              ),
                            ),
                            const SizedBox(width: 6),
                            Expanded(
                              child: Text(
                                _modeLabel(e.key),
                                style: theme.textTheme.bodySmall,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                            Text(
                              '$pct%',
                              style: theme.textTheme.labelSmall?.copyWith(
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ],
                        ),
                      );
                    }).toList(),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  String _modeLabel(String mode) => switch (mode) {
        'voiture' => 'Voiture',
        'transport_commun' => 'Transport en commun',
        'covoiturage' => 'Covoiturage',
        'company_transport' => 'Transport entreprise',
        'taxi' => 'Taxi',
        'marche' => 'Marche',
        'velo' => 'Vélo',
        _ => mode,
      };
}

class _PieChartPainter extends CustomPainter {
  final List<double> data;
  final List<Color> colors;

  _PieChartPainter({required this.data, required this.colors});

  @override
  void paint(Canvas canvas, Size size) {
    final total = data.fold<double>(0, (sum, v) => sum + v);
    if (total == 0) return;

    final center = Offset(size.width / 2, size.height / 2);
    final radius = math.min(size.width, size.height) / 2;
    var startAngle = -math.pi / 2;

    for (var i = 0; i < data.length; i++) {
      final sweep = (data[i] / total) * 2 * math.pi;
      final paint = Paint()
        ..color = colors[i % colors.length]
        ..style = PaintingStyle.fill;

      canvas.drawArc(
        Rect.fromCircle(center: center, radius: radius),
        startAngle,
        sweep,
        true,
        paint,
      );
      startAngle += sweep;
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}
