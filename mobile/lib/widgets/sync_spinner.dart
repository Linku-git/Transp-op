import 'package:flutter/material.dart';
import '../config/colors.dart';

class SyncSpinner extends StatelessWidget {
  final bool isSyncing;
  final String? label;

  const SyncSpinner({
    super.key,
    required this.isSyncing,
    this.label,
  });

  @override
  Widget build(BuildContext context) {
    if (!isSyncing) return const SizedBox.shrink();

    final theme = Theme.of(context);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: AppColors.primary.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          SizedBox(
            width: 14,
            height: 14,
            child: CircularProgressIndicator(
              strokeWidth: 2,
              color: AppColors.primary,
            ),
          ),
          const SizedBox(width: 6),
          Text(
            label ?? 'Synchronisation...',
            style: theme.textTheme.labelSmall?.copyWith(
              color: AppColors.primary,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }
}
