import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:transpop_mobile/models/content_feed.dart';
import 'package:transpop_mobile/providers/content_feed_provider.dart';

void main() {
  group('ContentFeedScreen', () {
    testWidgets('ContentFeedState filters items by type', (tester) async {
      final state = ContentFeedState(
        items: [
          FeedContent(id: '1', title: 'News 1', contentType: 'news'),
          FeedContent(id: '2', title: 'Training 1', contentType: 'training'),
          FeedContent(id: '3', title: 'Safety 1', contentType: 'safety'),
          FeedContent(id: '4', title: 'News 2', contentType: 'news'),
        ],
        selectedType: 'news',
      );

      expect(state.filteredItems.length, 2);
      expect(state.filteredItems.every((i) => i.contentType == 'news'), true);
    });

    testWidgets('ContentFeedState returns all when type is all',
        (tester) async {
      final state = ContentFeedState(
        items: [
          FeedContent(id: '1', title: 'News 1', contentType: 'news'),
          FeedContent(id: '2', title: 'Training 1', contentType: 'training'),
        ],
        selectedType: 'all',
      );

      expect(state.filteredItems.length, 2);
    });

    testWidgets('ContentFeedState copyWith preserves values', (tester) async {
      const state = ContentFeedState(
        isLoading: true,
        selectedType: 'training',
      );
      final updated = state.copyWith(isLoading: false);

      expect(updated.isLoading, false);
      expect(updated.selectedType, 'training');
    });

    testWidgets('ContentFeedState offline flag', (tester) async {
      final state = ContentFeedState(
        items: [FeedContent(id: '1', title: 'Cached', contentType: 'news')],
        isOffline: true,
      );

      expect(state.isOffline, true);
      expect(state.items.length, 1);
    });
  });
}
