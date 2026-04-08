import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../config/colors.dart';
import '../../providers/profile_provider.dart';
import '../../widgets/loading_indicator.dart';

class EditProfileScreen extends ConsumerStatefulWidget {
  const EditProfileScreen({super.key});

  @override
  ConsumerState<EditProfileScreen> createState() => _EditProfileScreenState();
}

class _EditProfileScreenState extends ConsumerState<EditProfileScreen> {
  final _phoneController = TextEditingController();
  final _addressController = TextEditingController();
  late bool _isPmr;

  @override
  void initState() {
    super.initState();
    final profile = ref.read(profileProvider).profile;
    _phoneController.text = profile?.phone ?? '';
    _addressController.text = profile?.pickupAddress ?? '';
    _isPmr = profile?.isPmr ?? false;
  }

  @override
  void dispose() {
    _phoneController.dispose();
    _addressController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(profileProvider);
    final profile = state.profile;
    final theme = Theme.of(context);

    if (profile == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Modifier le profil')),
        body: const LoadingIndicator(),
      );
    }

    return Scaffold(
      appBar: AppBar(title: const Text('Modifier le profil')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Read-only fields
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'INFORMATIONS SIRH',
                      style: theme.textTheme.labelSmall?.copyWith(
                        fontWeight: FontWeight.w700,
                        letterSpacing: 1,
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Ces champs sont gérés par votre service RH',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.outline,
                      ),
                    ),
                    const SizedBox(height: 12),
                    _ReadOnlyField(label: 'Nom', value: profile.displayName),
                    if (profile.matricule != null)
                      _ReadOnlyField(label: 'Matricule', value: profile.matricule!),
                    if (profile.siteName != null)
                      _ReadOnlyField(label: 'Site', value: profile.siteName!),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),

            // Editable fields
            Text(
              'TÉLÉPHONE',
              style: theme.textTheme.labelSmall?.copyWith(
                fontWeight: FontWeight.w700,
                letterSpacing: 1,
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _phoneController,
              keyboardType: TextInputType.phone,
              decoration: const InputDecoration(
                hintText: '+212 6XX XX XX XX',
                prefixIcon: Icon(Icons.phone),
              ),
            ),
            const SizedBox(height: 20),

            Text(
              'ADRESSE DE RAMASSAGE',
              style: theme.textTheme.labelSmall?.copyWith(
                fontWeight: FontWeight.w700,
                letterSpacing: 1,
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _addressController,
              decoration: const InputDecoration(
                hintText: 'Adresse préférée de ramassage',
                prefixIcon: Icon(Icons.place),
              ),
            ),
            const SizedBox(height: 20),

            // PMR toggle
            Card(
              child: SwitchListTile(
                title: const Text('Personne à mobilité réduite (PMR)'),
                subtitle: Text(
                  'Véhicule accessible et assistance prioritaire',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                ),
                value: _isPmr,
                onChanged: (value) => setState(() => _isPmr = value),
                secondary: Icon(
                  Icons.accessible,
                  color: _isPmr ? AppColors.primary : theme.colorScheme.outline,
                ),
              ),
            ),

            // Error/success
            if (state.error != null) ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: theme.colorScheme.errorContainer,
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Text(state.error!, style: TextStyle(color: theme.colorScheme.onErrorContainer, fontSize: 13)),
              ),
            ],

            const SizedBox(height: 24),
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
    final success = await ref.read(profileProvider.notifier).updateProfile(
      phone: _phoneController.text.isNotEmpty ? _phoneController.text : null,
      isPmr: _isPmr,
      pickupAddress: _addressController.text.isNotEmpty ? _addressController.text : null,
    );
    if (success && mounted) context.pop();
  }
}

class _ReadOnlyField extends StatelessWidget {
  final String label;
  final String value;

  const _ReadOnlyField({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        children: [
          SizedBox(
            width: 80,
            child: Text(label, style: theme.textTheme.bodySmall?.copyWith(color: theme.colorScheme.outline)),
          ),
          Expanded(child: Text(value, style: theme.textTheme.bodyMedium)),
        ],
      ),
    );
  }
}
