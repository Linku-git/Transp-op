import 'package:flutter/material.dart';
import '../config/colors.dart';
import '../services/statistics_service.dart';

class Co2TrendChart extends StatelessWidget {
  final List<Co2DataPoint> data;

  const Co2TrendChart({super.key, required this.data});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    if (data.isEmpty) return const SizedBox.shrink();

    final maxValue = data.fold<double>(0, (max, p) => p.value > max ? p.value : max);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'ÉVOLUTION CO2 ÉCONOMISÉ',
              style: theme.textTheme.labelSmall?.copyWith(
                fontWeight: FontWeight.w700,
                letterSpacing: 1,
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 16),
            SizedBox(
              height: 120,
              child: CustomPaint(
                size: Size.infinite,
                painter: _TrendLinePainter(
                  data: data,
                  maxValue: maxValue,
                  lineColor: AppColors.success,
                  fillColor: AppColors.success.withValues(alpha: 0.1),
                ),
              ),
            ),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                if (data.isNotEmpty)
                  Text(
                    _formatDate(data.first.date),
                    style: theme.textTheme.labelSmall?.copyWith(
                      color: theme.colorScheme.outline,
                      fontSize: 9,
                    ),
                  ),
                if (data.length > 1)
                  Text(
                    _formatDate(data.last.date),
                    style: theme.textTheme.labelSmall?.copyWith(
                      color: theme.colorScheme.outline,
                      fontSize: 9,
                    ),
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  String _formatDate(String date) {
    if (date.length >= 10) return '${date.substring(8, 10)}/${date.substring(5, 7)}';
    return date;
  }
}

class _TrendLinePainter extends CustomPainter {
  final List<Co2DataPoint> data;
  final double maxValue;
  final Color lineColor;
  final Color fillColor;

  _TrendLinePainter({
    required this.data,
    required this.maxValue,
    required this.lineColor,
    required this.fillColor,
  });

  @override
  void paint(Canvas canvas, Size size) {
    if (data.isEmpty || maxValue == 0) return;

    final linePaint = Paint()
      ..color = lineColor
      ..strokeWidth = 2
      ..style = PaintingStyle.stroke;

    final fillPaint = Paint()
      ..color = fillColor
      ..style = PaintingStyle.fill;

    final path = Path();
    final fillPath = Path();

    for (var i = 0; i < data.length; i++) {
      final x = data.length > 1 ? (i / (data.length - 1)) * size.width : size.width / 2;
      final y = size.height - (data[i].value / maxValue) * size.height;

      if (i == 0) {
        path.moveTo(x, y);
        fillPath.moveTo(x, size.height);
        fillPath.lineTo(x, y);
      } else {
        path.lineTo(x, y);
        fillPath.lineTo(x, y);
      }
    }

    fillPath.lineTo(size.width, size.height);
    fillPath.close();

    canvas.drawPath(fillPath, fillPaint);
    canvas.drawPath(path, linePaint);

    // Draw dots
    final dotPaint = Paint()
      ..color = lineColor
      ..style = PaintingStyle.fill;

    for (var i = 0; i < data.length; i++) {
      final x = data.length > 1 ? (i / (data.length - 1)) * size.width : size.width / 2;
      final y = size.height - (data[i].value / maxValue) * size.height;
      canvas.drawCircle(Offset(x, y), 3, dotPaint);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}
