import 'package:flutter/material.dart';

class StaleDataBadge extends StatelessWidget {
  final String? label;

  const StaleDataBadge({super.key, this.label});

  @override
  Widget build(BuildContext context) {
    if (label == null) return const SizedBox.shrink();

    final theme = Theme.of(context);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: Colors.orange.shade50,
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: Colors.orange.shade200, width: 0.5),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.access_time, size: 12, color: Colors.orange.shade700),
          const SizedBox(width: 4),
          Text(
            label!,
            style: theme.textTheme.labelSmall?.copyWith(
              color: Colors.orange.shade700,
              fontSize: 10,
            ),
          ),
        ],
      ),
    );
  }
}
