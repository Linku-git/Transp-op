import 'package:flutter/material.dart';

import '../../models/content_feed.dart';

class ContentCard extends StatelessWidget {
  final FeedContent item;
  final VoidCallback? onTap;

  const ContentCard({super.key, required this.item, this.onTap});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Card(
      clipBehavior: Clip.antiAlias,
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Thumbnail
              if (item.mediaUrl != null)
                ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: Image.network(
                    item.mediaUrl!,
                    width: 72,
                    height: 72,
                    fit: BoxFit.cover,
                    errorBuilder: (_, __, ___) => Container(
                      width: 72,
                      height: 72,
                      decoration: BoxDecoration(
                        color: theme.colorScheme.surfaceContainerHigh,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Icon(
                        Icons.image_outlined,
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                  ),
                )
              else
                Container(
                  width: 72,
                  height: 72,
                  decoration: BoxDecoration(
                    color: _typeColor(theme).withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(_typeIcon, color: _typeColor(theme), size: 28),
                ),
              const SizedBox(width: 12),

              // Content
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Top row: type badge + new indicator
                    Row(
                      children: [
                        _TypeBadge(type: item.contentType),
                        const Spacer(),
                        if (item.isNew)
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 6,
                              vertical: 2,
                            ),
                            decoration: BoxDecoration(
                              color: theme.colorScheme.primary,
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: Text(
                              'NEW',
                              style: theme.textTheme.labelSmall?.copyWith(
                                color: theme.colorScheme.onPrimary,
                                fontWeight: FontWeight.w700,
                                fontSize: 9,
                                letterSpacing: 0.5,
                              ),
                            ),
                          ),
                        if (item.completed)
                          Icon(
                            Icons.check_circle,
                            size: 18,
                            color: theme.colorScheme.primary,
                          ),
                      ],
                    ),
                    const SizedBox(height: 6),

                    // Title
                    Text(
                      item.title,
                      style: theme.textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 4),

                    // Snippet
                    if (item.snippet.isNotEmpty)
                      Text(
                        item.snippet,
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: theme.colorScheme.onSurfaceVariant,
                        ),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                    const SizedBox(height: 6),

                    // Date
                    if (item.publishedAt != null)
                      Text(
                        _formatDate(item.publishedAt!),
                        style: theme.textTheme.labelSmall?.copyWith(
                          color: theme.colorScheme.onSurfaceVariant
                              .withValues(alpha: 0.7),
                        ),
                      ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  IconData get _typeIcon => switch (item.contentType) {
    'training' => Icons.school_outlined,
    'safety' => Icons.shield_outlined,
    'survey' => Icons.poll_outlined,
    _ => Icons.newspaper_outlined,
  };

  Color _typeColor(ThemeData theme) => switch (item.contentType) {
    'training' => Colors.purple,
    'safety' => Colors.orange,
    'survey' => Colors.teal,
    _ => theme.colorScheme.primary,
  };

  static const _months = [
    'jan.', 'fév.', 'mars', 'avr.', 'mai', 'juin',
    'juil.', 'août', 'sept.', 'oct.', 'nov.', 'déc.',
  ];

  String _formatDate(DateTime date) {
    return '${date.day} ${_months[date.month - 1]} ${date.year}';
  }
}

class _TypeBadge extends StatelessWidget {
  final String type;
  const _TypeBadge({required this.type});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final (label, color) = switch (type) {
      'training' => ('Formation', Colors.purple),
      'safety' => ('Sécurité', Colors.orange),
      'survey' => ('Sondage', Colors.teal),
      _ => ('Actualité', theme.colorScheme.primary),
    };

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        label,
        style: theme.textTheme.labelSmall?.copyWith(
          color: color,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
}
