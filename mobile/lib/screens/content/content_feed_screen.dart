import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../providers/content_feed_provider.dart';
import '../../widgets/content/content_card.dart';
import '../../widgets/content/content_tabs.dart';
import '../../widgets/content/offline_indicator.dart';
import '../../widgets/loading_indicator.dart';

class ContentFeedScreen extends ConsumerStatefulWidget {
  const ContentFeedScreen({super.key});

  @override
  ConsumerState<ContentFeedScreen> createState() => _ContentFeedScreenState();
}

class _ContentFeedScreenState extends ConsumerState<ContentFeedScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() => ref.read(contentFeedProvider.notifier).load());
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(contentFeedProvider);
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Contenu'),
        centerTitle: false,
      ),
      body: Column(
        children: [
          // Offline indicator
          if (state.isOffline) const OfflineIndicator(),

          // Tabs
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 8),
            child: ContentTabs(
              selectedType: state.selectedType,
              onTypeChanged: (type) {
                ref.read(contentFeedProvider.notifier).setType(type);
              },
            ),
          ),

          // Content list
          Expanded(
            child: _buildBody(state, theme),
          ),
        ],
      ),
    );
  }

  Widget _buildBody(ContentFeedState state, ThemeData theme) {
    if (state.isLoading) {
      return const LoadingIndicator(message: 'Chargement du contenu...');
    }

    if (state.error != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.error_outline,
              size: 48,
              color: theme.colorScheme.error,
            ),
            const SizedBox(height: 12),
            Text(
              state.error!,
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 16),
            FilledButton.tonal(
              onPressed: () => ref.read(contentFeedProvider.notifier).load(),
              child: const Text('Réessayer'),
            ),
          ],
        ),
      );
    }

    final items = state.filteredItems;

    if (items.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.article_outlined,
              size: 48,
              color: theme.colorScheme.onSurfaceVariant.withValues(alpha: 0.4),
            ),
            const SizedBox(height: 12),
            Text(
              'Aucun contenu disponible',
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: () => ref.read(contentFeedProvider.notifier).refresh(),
      child: ListView.builder(
        padding: const EdgeInsets.only(top: 4, bottom: 16),
        itemCount: items.length,
        itemBuilder: (context, index) {
          final item = items[index];
          return ContentCard(
            item: item,
            onTap: () => context.push('/content/${item.id}'),
          );
        },
      ),
    );
  }
}
