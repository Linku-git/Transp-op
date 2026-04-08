import 'package:flutter/material.dart';
import '../models/trip_booking.dart';

class ShiftSelector extends StatelessWidget {
  final List<Shift> shifts;
  final String? selectedShiftId;
  final ValueChanged<Shift> onShiftSelected;
  final bool isLoading;

  const ShiftSelector({
    super.key,
    required this.shifts,
    this.selectedShiftId,
    required this.onShiftSelected,
    this.isLoading = false,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    if (isLoading) {
      return const Padding(
        padding: EdgeInsets.symmetric(vertical: 16),
        child: Center(child: CircularProgressIndicator(strokeWidth: 2)),
      );
    }

    if (shifts.isEmpty) {
      return Padding(
        padding: const EdgeInsets.symmetric(vertical: 16),
        child: Text(
          'Aucun horaire disponible',
          style: theme.textTheme.bodyMedium?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
      );
    }

    return Column(
      children: shifts.map((shift) {
        final isSelected = shift.id == selectedShiftId;
        return Padding(
          padding: const EdgeInsets.only(bottom: 8),
          child: Card(
            color: isSelected
                ? theme.colorScheme.primary.withValues(alpha: 0.08)
                : null,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
              side: isSelected
                  ? BorderSide(color: theme.colorScheme.primary, width: 1.5)
                  : BorderSide.none,
            ),
            child: InkWell(
              onTap: () => onShiftSelected(shift),
              borderRadius: BorderRadius.circular(12),
              child: Padding(
                padding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 14,
                ),
                child: Row(
                  children: [
                    Icon(
                      isSelected
                          ? Icons.radio_button_checked
                          : Icons.radio_button_off,
                      color: isSelected
                          ? theme.colorScheme.primary
                          : theme.colorScheme.outline,
                      size: 20,
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            shift.label,
                            style: theme.textTheme.titleSmall?.copyWith(
                              fontWeight:
                                  isSelected ? FontWeight.w600 : FontWeight.w500,
                            ),
                          ),
                          if (shift.entryTime.isNotEmpty) ...[
                            const SizedBox(height: 2),
                            Text(
                              '${shift.entryTime} — ${shift.exitTime}',
                              style: theme.textTheme.bodySmall?.copyWith(
                                color: theme.colorScheme.onSurfaceVariant,
                              ),
                            ),
                          ],
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        );
      }).toList(),
    );
  }
}
