import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../models/content_feed.dart';
import '../../providers/content_feed_provider.dart';
import '../../providers/auth_provider.dart';
import '../../widgets/loading_indicator.dart';

class ContentDetailScreen extends ConsumerStatefulWidget {
  final String contentId;

  const ContentDetailScreen({super.key, required this.contentId});

  @override
  ConsumerState<ContentDetailScreen> createState() =>
      _ContentDetailScreenState();
}

class _ContentDetailScreenState extends ConsumerState<ContentDetailScreen> {
  final ScrollController _scrollController = ScrollController();
  bool _markedAsRead = false;
  DateTime? _openedAt;

  @override
  void initState() {
    super.initState();
    _openedAt = DateTime.now();
    _scrollController.addListener(_onScroll);
  }

  @override
  void dispose() {
    _scrollController.removeListener(_onScroll);
    _scrollController.dispose();
    super.dispose();
  }

  void _onScroll() {
    if (_markedAsRead) return;

    final maxScroll = _scrollController.position.maxScrollExtent;
    final currentScroll = _scrollController.position.pixels;

    // Mark as read when user scrolls to ~90% of content
    if (maxScroll > 0 && currentScroll >= maxScroll * 0.9) {
      _markAsRead();
    }
  }

  Future<void> _markAsRead() async {
    if (_markedAsRead) return;
    _markedAsRead = true;

    final authState = ref.read(authProvider);
    final employeeId = authState.user?.id;
    if (employeeId == null) return;

    final service = ref.read(contentFeedServiceProvider);
    try {
      // Record view
      await service.markViewed(widget.contentId, employeeId);

      // Record completion with time spent
      final timeSpent = DateTime.now().difference(_openedAt!).inSeconds;
      await service.markCompleted(
        widget.contentId,
        employeeId,
        timeSpentSeconds: timeSpent,
      );
    } catch (_) {
      // Non-critical — engagement tracking failure shouldn't disrupt UX
    }
  }

  @override
  Widget build(BuildContext context) {
    final contentAsync = ref.watch(contentDetailProvider(widget.contentId));
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Contenu'),
      ),
      body: contentAsync.when(
        loading: () => const LoadingIndicator(message: 'Chargement...'),
        error: (e, _) => Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.error_outline, size: 48, color: theme.colorScheme.error),
              const SizedBox(height: 12),
              Text(
                'Impossible de charger le contenu',
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
              const SizedBox(height: 16),
              FilledButton.tonal(
                onPressed: () =>
                    ref.invalidate(contentDetailProvider(widget.contentId)),
                child: const Text('Réessayer'),
              ),
            ],
          ),
        ),
        data: (content) => _buildContent(content, theme),
      ),
    );
  }

  Widget _buildContent(FeedContent content, ThemeData theme) {
    return SingleChildScrollView(
      controller: _scrollController,
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Type badge
          _TypeBadge(type: content.contentType),
          const SizedBox(height: 12),

          // Title
          Text(
            content.title,
            style: theme.textTheme.headlineSmall?.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 8),

          // Date
          if (content.publishedAt != null)
            Text(
              _formatDate(content.publishedAt!),
              style: theme.textTheme.labelMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
          const SizedBox(height: 20),

          // Media
          if (content.mediaUrl != null) ...[
            ClipRRect(
              borderRadius: BorderRadius.circular(12),
              child: _buildMedia(content.mediaUrl!, theme),
            ),
            const SizedBox(height: 20),
          ],

          // Body - render HTML as styled text
          if (content.body != null && content.body!.isNotEmpty)
            _RichBodyText(html: content.body!),

          // Bottom padding for scroll completion detection
          const SizedBox(height: 40),
        ],
      ),
    );
  }

  Widget _buildMedia(String url, ThemeData theme) {
    // Video URLs - show placeholder
    if (url.contains('.mp4') || url.contains('.webm') || url.contains('youtube') || url.contains('vimeo')) {
      return Container(
        height: 200,
        decoration: BoxDecoration(
          color: theme.colorScheme.surfaceContainerHigh,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.play_circle_outline, size: 48, color: theme.colorScheme.primary),
              const SizedBox(height: 8),
              Text('Vidéo', style: theme.textTheme.labelMedium),
            ],
          ),
        ),
      );
    }

    // Image
    return Image.network(
      url,
      width: double.infinity,
      fit: BoxFit.cover,
      errorBuilder: (_, __, ___) => Container(
        height: 200,
        decoration: BoxDecoration(
          color: theme.colorScheme.surfaceContainerHigh,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Center(
          child: Icon(
            Icons.broken_image_outlined,
            size: 48,
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
      ),
    );
  }

  String _formatDate(DateTime date) {
    final months = [
      'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
      'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'
    ];
    return '${date.day} ${months[date.month - 1]} ${date.year}';
  }
}

/// Renders HTML body as simple styled text (strips tags for MVP).
class _RichBodyText extends StatelessWidget {
  final String html;
  const _RichBodyText({required this.html});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    // Simple HTML-to-text rendering for MVP
    // Split by common HTML blocks and render as paragraphs
    final blocks = html
        .replaceAll(RegExp(r'<br\s*/?>'), '\n')
        .replaceAll(RegExp(r'</?(p|div)>'), '\n')
        .replaceAll(RegExp(r'<h[1-6][^>]*>'), '\n### ')
        .replaceAll(RegExp(r'</h[1-6]>'), '\n')
        .replaceAll(RegExp(r'<li[^>]*>'), '\n• ')
        .replaceAll(RegExp(r'</li>'), '')
        .replaceAll(RegExp(r'<[^>]*>'), '')
        .replaceAll(RegExp(r'\n{3,}'), '\n\n')
        .trim();

    final paragraphs = blocks.split('\n\n').where((p) => p.trim().isNotEmpty);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: paragraphs.map((paragraph) {
        final trimmed = paragraph.trim();
        if (trimmed.startsWith('### ')) {
          return Padding(
            padding: const EdgeInsets.only(bottom: 8, top: 16),
            child: Text(
              trimmed.substring(4),
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
          );
        }
        return Padding(
          padding: const EdgeInsets.only(bottom: 12),
          child: Text(
            trimmed,
            style: theme.textTheme.bodyLarge?.copyWith(
              height: 1.6,
              color: theme.colorScheme.onSurface,
            ),
          ),
        );
      }).toList(),
    );
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
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(6),
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
