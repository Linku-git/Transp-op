import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../models/transport_preferences.dart';
import '../../providers/profile_provider.dart';

class PreferencesScreen extends ConsumerStatefulWidget {
  const PreferencesScreen({super.key});

  @override
  ConsumerState<PreferencesScreen> createState() => _PreferencesScreenState();
}

class _PreferencesScreenState extends ConsumerState<PreferencesScreen> {
  String? _transportMode;
  double _maxWalkingDistance = 500;
  bool _volunteerDriver = false;
  bool _rtiAlerts = true;
  bool _routeChanges = true;
  bool _contentNotifications = true;
  bool _weatherAlerts = true;
  bool _autoNightMode = true;

  @override
  void initState() {
    super.initState();
    final profile = ref.read(profileProvider).profile;
    _transportMode = profile?.transportMode;
    _volunteerDriver = false; // Would come from profile
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(profileProvider);
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(title: const Text('Préférences')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Transport mode
            _SectionHeader('MODE DE TRANSPORT'),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: TransportMode.all.map((mode) {
                final isSelected = _transportMode == mode.key;
                return ChoiceChip(
                  label: Text(mode.label),
                  selected: isSelected,
                  onSelected: (_) => setState(() => _transportMode = mode.key),
                  selectedColor: theme.colorScheme.primary.withValues(alpha: 0.15),
                );
              }).toList(),
            ),
            const SizedBox(height: 24),

            // Walking distance
            _SectionHeader('DISTANCE DE MARCHE MAXIMALE'),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: Slider(
                    value: _maxWalkingDistance,
                    min: 200,
                    max: 2000,
                    divisions: 18,
                    label: '${_maxWalkingDistance.round()} m',
                    onChanged: (v) => setState(() => _maxWalkingDistance = v),
                  ),
                ),
                SizedBox(
                  width: 64,
                  child: Text('${_maxWalkingDistance.round()} m', style: theme.textTheme.titleSmall, textAlign: TextAlign.center),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Volunteer driver
            Card(
              child: SwitchListTile(
                title: const Text('Conducteur volontaire'),
                subtitle: Text('Proposer des places de covoiturage', style: theme.textTheme.bodySmall?.copyWith(color: theme.colorScheme.onSurfaceVariant)),
                value: _volunteerDriver,
                onChanged: (v) => setState(() => _volunteerDriver = v),
              ),
            ),
            const SizedBox(height: 24),

            // Notification settings
            _SectionHeader('NOTIFICATIONS'),
            const SizedBox(height: 8),
            Card(
              child: Column(
                children: [
                  SwitchListTile(
                    title: const Text('Alertes transport'),
                    subtitle: const Text('Arrivée du véhicule'),
                    value: _rtiAlerts,
                    onChanged: (v) => setState(() => _rtiAlerts = v),
                    dense: true,
                  ),
                  SwitchListTile(
                    title: const Text('Changements d\'itinéraire'),
                    value: _routeChanges,
                    onChanged: (v) => setState(() => _routeChanges = v),
                    dense: true,
                  ),
                  SwitchListTile(
                    title: const Text('Contenu et formations'),
                    value: _contentNotifications,
                    onChanged: (v) => setState(() => _contentNotifications = v),
                    dense: true,
                  ),
                  SwitchListTile(
                    title: const Text('Alertes météo'),
                    value: _weatherAlerts,
                    onChanged: (v) => setState(() => _weatherAlerts = v),
                    dense: true,
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Night mode
            Card(
              child: SwitchListTile(
                title: const Text('Mode nuit automatique'),
                subtitle: Text('Active entre 20h et 6h30', style: theme.textTheme.bodySmall?.copyWith(color: theme.colorScheme.onSurfaceVariant)),
                value: _autoNightMode,
                onChanged: (v) => setState(() => _autoNightMode = v),
                secondary: const Icon(Icons.dark_mode),
              ),
            ),
            const SizedBox(height: 24),

            // Save button
            SizedBox(
              width: double.infinity,
              height: 52,
              child: ElevatedButton(
                onPressed: state.isSaving ? null : _save,
                child: state.isSaving
                    ? const SizedBox(width: 22, height: 22, child: CircularProgressIndicator(strokeWidth: 2.5, color: Colors.white))
                    : const Text('Enregistrer', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _save() async {
    final success = await ref.read(profileProvider.notifier).updatePreferences(
      transportMode: _transportMode,
      maxWalkingDistance: _maxWalkingDistance,
      volunteerDriver: _volunteerDriver,
    );
    if (success && mounted) context.pop();
  }
}

class _SectionHeader extends StatelessWidget {
  final String text;
  const _SectionHeader(this.text);

  @override
  Widget build(BuildContext context) {
    return Text(
      text,
      style: Theme.of(context).textTheme.labelSmall?.copyWith(
            fontWeight: FontWeight.w700,
            letterSpacing: 1,
            color: Theme.of(context).colorScheme.onSurfaceVariant,
          ),
    );
  }
}
