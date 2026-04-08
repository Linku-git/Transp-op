import 'package:flutter/material.dart';

class ContentTabs extends StatelessWidget {
  final String selectedType;
  final ValueChanged<String> onTypeChanged;

  const ContentTabs({
    super.key,
    required this.selectedType,
    required this.onTypeChanged,
  });

  static const _tabs = [
    ('all', 'Tout', Icons.apps_outlined),
    ('news', 'Actualités', Icons.newspaper_outlined),
    ('training', 'Formation', Icons.school_outlined),
    ('safety', 'Sécurité', Icons.shield_outlined),
    ('survey', 'Sondages', Icons.poll_outlined),
  ];

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return SizedBox(
      height: 40,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        itemCount: _tabs.length,
        separatorBuilder: (_, __) => const SizedBox(width: 8),
        itemBuilder: (context, index) {
          final (type, label, icon) = _tabs[index];
          final isSelected = selectedType == type;

          return FilterChip(
            selected: isSelected,
            onSelected: (_) => onTypeChanged(type),
            avatar: Icon(icon, size: 16),
            label: Text(label),
            labelStyle: theme.textTheme.labelMedium?.copyWith(
              fontWeight: isSelected ? FontWeight.w600 : FontWeight.w400,
            ),
            showCheckmark: false,
            padding: const EdgeInsets.symmetric(horizontal: 4),
            materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
          );
        },
      ),
    );
  }
}
