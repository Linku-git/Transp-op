import 'dart:async';
import 'package:flutter/material.dart';
import '../utils/map_utils.dart';

class VehicleArrivalCard extends StatefulWidget {
  final int? etaSeconds;
  final String vehicleType;
  final String routeName;
  final String? driverName;
  final String gatheringPointName;
  final VoidCallback? onViewFullMap;

  const VehicleArrivalCard({
    super.key,
    this.etaSeconds,
    required this.vehicleType,
    required this.routeName,
    this.driverName,
    required this.gatheringPointName,
    this.onViewFullMap,
  });

  @override
  State<VehicleArrivalCard> createState() => _VehicleArrivalCardState();
}

class _VehicleArrivalCardState extends State<VehicleArrivalCard> {
  Timer? _timer;
  late int _currentEta;

  @override
  void initState() {
    super.initState();
    _currentEta = widget.etaSeconds ?? 0;
    _timer = Timer.periodic(const Duration(seconds: 1), (_) {
      if (!mounted) return;
      setState(() {
        if (_currentEta > 0) _currentEta--;
      });
    });
  }

  @override
  void didUpdateWidget(VehicleArrivalCard old) {
    super.didUpdateWidget(old);
    if (widget.etaSeconds != null && widget.etaSeconds != old.etaSeconds) {
      _currentEta = widget.etaSeconds!;
    }
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final color = MapUtils.etaColor(_currentEta);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // ETA countdown
            Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                  decoration: BoxDecoration(
                    color: color.withValues(alpha: 0.12),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    MapUtils.formatEta(_currentEta),
                    style: theme.textTheme.headlineMedium?.copyWith(
                      fontWeight: FontWeight.w700,
                      color: color,
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        _currentEta <= 0 ? 'Véhicule arrivé' : 'Avant arrivée',
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: theme.colorScheme.onSurfaceVariant,
                        ),
                      ),
                      Text(
                        widget.gatheringPointName,
                        style: theme.textTheme.titleSmall?.copyWith(
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Vehicle info
            Row(
              children: [
                Icon(Icons.directions_bus, size: 16, color: theme.colorScheme.onSurfaceVariant),
                const SizedBox(width: 6),
                Text(widget.vehicleType, style: theme.textTheme.bodyMedium),
                const SizedBox(width: 16),
                Icon(Icons.route, size: 16, color: theme.colorScheme.onSurfaceVariant),
                const SizedBox(width: 6),
                Expanded(
                  child: Text(widget.routeName, style: theme.textTheme.bodyMedium, overflow: TextOverflow.ellipsis),
                ),
              ],
            ),
            if (widget.driverName != null) ...[
              const SizedBox(height: 6),
              Row(
                children: [
                  Icon(Icons.person, size: 16, color: theme.colorScheme.onSurfaceVariant),
                  const SizedBox(width: 6),
                  Text(widget.driverName!, style: theme.textTheme.bodyMedium),
                ],
              ),
            ],

            if (widget.onViewFullMap != null) ...[
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                child: OutlinedButton.icon(
                  onPressed: widget.onViewFullMap,
                  icon: const Icon(Icons.fullscreen, size: 18),
                  label: const Text('Carte complète'),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
