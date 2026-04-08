import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/connectivity_provider.dart';
import '../services/connectivity_service.dart';

class OfflineBanner extends ConsumerWidget {
  const OfflineBanner({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final connectivityAsync = ref.watch(connectivityStateProvider);

    return connectivityAsync.when(
      data: (state) {
        if (state == ConnectivityState.online) return const SizedBox.shrink();

        final isOffline = state == ConnectivityState.offline;
        return Container(
          width: double.infinity,
          padding: const EdgeInsets.symmetric(vertical: 6, horizontal: 12),
          color: isOffline ? Colors.grey.shade800 : Colors.orange.shade700,
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                isOffline ? Icons.cloud_off : Icons.signal_wifi_statusbar_connected_no_internet_4,
                size: 14,
                color: Colors.white,
              ),
              const SizedBox(width: 6),
              Text(
                isOffline
                    ? 'Vous êtes hors ligne. Données en cache affichées.'
                    : 'Connexion instable. Certaines données peuvent être obsolètes.',
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 11,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
        );
      },
      loading: () => const SizedBox.shrink(),
      error: (_, _) => const SizedBox.shrink(),
    );
  }
}
