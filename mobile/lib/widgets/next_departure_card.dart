import 'dart:async';
import 'package:flutter/material.dart';
import '../config/colors.dart';
import '../models/departure.dart';

class NextDepartureCard extends StatefulWidget {
  final Departure departure;
  final VoidCallback? onViewMap;

  const NextDepartureCard({
    super.key,
    required this.departure,
    this.onViewMap,
  });

  @override
  State<NextDepartureCard> createState() => _NextDepartureCardState();
}

class _NextDepartureCardState extends State<NextDepartureCard> {
  Timer? _timer;
  late Duration _remaining;

  @override
  void initState() {
    super.initState();
    _remaining = widget.departure.timeRemaining;
    _timer = Timer.periodic(const Duration(seconds: 1), (_) {
      if (!mounted) return;
      setState(() {
        _remaining = widget.departure.timeRemaining;
      });
    });
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  Color get _countdownColor {
    final minutes = _remaining.inMinutes;
    if (_remaining.isNegative) return AppColors.error;
    if (minutes < 2) return AppColors.error;
    if (minutes < 5) return AppColors.warning;
    return AppColors.success;
  }

  String get _countdownText {
    if (_remaining.isNegative) return 'Parti';
    final hours = _remaining.inHours;
    final mins = _remaining.inMinutes.remainder(60);
    final secs = _remaining.inSeconds.remainder(60);
    if (hours > 0) return '${hours}h ${mins}min';
    if (mins > 0) return '${mins}min ${secs.toString().padLeft(2, '0')}s';
    return '${secs}s';
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final dep = widget.departure;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Row(
              children: [
                Icon(
                  Icons.directions_bus,
                  color: theme.colorScheme.primary,
                  size: 20,
                ),
                const SizedBox(width: 8),
                Text(
                  'PROCHAIN DÉPART',
                  style: theme.textTheme.labelSmall?.copyWith(
                    fontWeight: FontWeight.w700,
                    letterSpacing: 1,
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Countdown
            Row(
              crossAxisAlignment: CrossAxisAlignment.baseline,
              textBaseline: TextBaseline.alphabetic,
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 6,
                  ),
                  decoration: BoxDecoration(
                    color: _countdownColor.withValues(alpha: 0.12),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    _countdownText,
                    style: theme.textTheme.headlineMedium?.copyWith(
                      fontWeight: FontWeight.w700,
                      color: _countdownColor,
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Text(
                  'Départ à ${_formatTime(dep.departureTime)}',
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Details
            _DetailRow(
              icon: Icons.place,
              label: dep.pickupPointName,
              trailing: dep.walkingMinutes != null
                  ? '${dep.walkingMinutes!.round()} min à pied'
                  : null,
            ),
            const SizedBox(height: 8),
            _DetailRow(
              icon: Icons.route,
              label: dep.routeName,
            ),
            const SizedBox(height: 8),
            _DetailRow(
              icon: Icons.directions_bus_filled,
              label: dep.vehicleType,
              trailing: dep.driverName,
            ),

            if (widget.onViewMap != null) ...[
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                child: OutlinedButton.icon(
                  onPressed: widget.onViewMap,
                  icon: const Icon(Icons.map, size: 18),
                  label: const Text('Voir sur la carte'),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  String _formatTime(DateTime time) {
    return '${time.hour.toString().padLeft(2, '0')}:${time.minute.toString().padLeft(2, '0')}';
  }
}

class _DetailRow extends StatelessWidget {
  final IconData icon;
  final String label;
  final String? trailing;

  const _DetailRow({
    required this.icon,
    required this.label,
    this.trailing,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Row(
      children: [
        Icon(icon, size: 16, color: theme.colorScheme.onSurfaceVariant),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            label,
            style: theme.textTheme.bodyMedium,
          ),
        ),
        if (trailing != null)
          Text(
            trailing!,
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
      ],
    );
  }
}
