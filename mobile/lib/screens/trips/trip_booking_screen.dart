import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../config/colors.dart';
import '../../providers/trip_booking_provider.dart';
import '../../widgets/date_picker_strip.dart';
import '../../widgets/shift_selector.dart';
import '../../widgets/pickup_point_picker.dart';
import '../../widgets/booking_summary_card.dart';

class TripBookingScreen extends ConsumerWidget {
  const TripBookingScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(tripBookingProvider);
    final notifier = ref.read(tripBookingProvider.notifier);
    final theme = Theme.of(context);

    ref.listen<TripBookingState>(tripBookingProvider, (prev, next) {
      if (next.confirmation != null && prev?.confirmation == null) {
        _showConfirmation(context, next.confirmation!.message);
      }
    });

    return Scaffold(
      appBar: AppBar(
        title: const Text('Réserver un trajet'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Date picker
            Text(
              'DATE',
              style: theme.textTheme.labelSmall?.copyWith(
                fontWeight: FontWeight.w700,
                letterSpacing: 1,
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 8),
            DatePickerStrip(
              selectedDate: state.selectedDate,
              onDateSelected: notifier.selectDate,
            ),
            const SizedBox(height: 24),

            // Shift selector
            Text(
              'HORAIRE',
              style: theme.textTheme.labelSmall?.copyWith(
                fontWeight: FontWeight.w700,
                letterSpacing: 1,
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 8),
            ShiftSelector(
              shifts: state.shifts,
              selectedShiftId: state.selectedShiftId,
              onShiftSelected: notifier.selectShift,
              isLoading: state.isLoadingShifts,
            ),
            const SizedBox(height: 24),

            // Pickup point
            PickupPointPicker(
              selectedPoint: state.activePickupPoint,
              availablePoints: state.availablePickupPoints,
              onPointSelected: notifier.selectPickupPoint,
            ),
            const SizedBox(height: 24),

            // Summary
            if (state.selectedShift != null)
              BookingSummaryCard(
                date: state.selectedDate,
                shift: state.selectedShift,
                pickupPoint: state.activePickupPoint,
              ),

            // Error
            if (state.error != null) ...[
              const SizedBox(height: 12),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: theme.colorScheme.errorContainer,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  state.error!,
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onErrorContainer,
                  ),
                ),
              ),
            ],

            // Cancellation policy
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: AppColors.warningContainer.withValues(alpha: 0.3),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Icon(
                    Icons.info_outline,
                    size: 16,
                    color: AppColors.warning,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Annulation possible jusqu\'à 30 minutes avant le départ.',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.onSurface,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // Confirm button
            SizedBox(
              width: double.infinity,
              height: 52,
              child: ElevatedButton(
                onPressed: state.canConfirm
                    ? () async {
                        final success = await notifier.confirmBooking();
                        if (success && context.mounted) {
                          context.pop();
                        }
                      }
                    : null,
                child: state.isSubmitting
                    ? const SizedBox(
                        width: 22,
                        height: 22,
                        child: CircularProgressIndicator(
                          strokeWidth: 2.5,
                          color: Colors.white,
                        ),
                      )
                    : const Text(
                        'Confirmer la réservation',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
              ),
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }

  void _showConfirmation(BuildContext context, String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            const Icon(Icons.check_circle, color: Colors.white),
            const SizedBox(width: 8),
            Text(message),
          ],
        ),
        backgroundColor: AppColors.success,
        behavior: SnackBarBehavior.floating,
      ),
    );
  }
}
