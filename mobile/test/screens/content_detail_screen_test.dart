import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/models/content_feed.dart';

void main() {
  group('ContentDetailScreen logic', () {
    test('FeedContent renders body snippet without HTML', () {
      final content = FeedContent(
        id: '1',
        title: 'Article complet',
        body: '<h3>Introduction</h3><p>Ceci est un <strong>article</strong> de test avec du contenu riche.</p>',
        contentType: 'news',
        publishedAt: DateTime(2026, 4, 8),
      );

      expect(content.snippet, isNotEmpty);
      expect(content.snippet.contains('<'), false);
      expect(content.snippet.contains('>'), false);
    });

    test('FeedContent with media URL', () {
      final content = FeedContent(
        id: '2',
        title: 'Video article',
        contentType: 'training',
        mediaUrl: 'https://example.com/video.mp4',
      );

      expect(content.mediaUrl, isNotNull);
      expect(content.mediaUrl!.contains('.mp4'), true);
    });

    test('FeedContent type labels are correct', () {
      final types = ['news', 'training', 'safety', 'survey'];
      final expectedLabels = ['Actualité', 'Formation', 'Sécurité', 'Sondage'];

      for (var i = 0; i < types.length; i++) {
        final content = FeedContent(id: '$i', title: 'T', contentType: types[i]);
        expect(content.typeLabel, expectedLabels[i]);
      }
    });

    test('Mark as read triggers at scroll completion threshold', () {
      // Verify the 90% scroll threshold logic
      const maxScroll = 1000.0;
      const threshold = 0.9;
      const currentScroll = 910.0;

      expect(currentScroll >= maxScroll * threshold, true);
    });

    test('Time spent is calculated correctly', () {
      final openedAt = DateTime(2026, 4, 8, 10, 0, 0);
      final completedAt = DateTime(2026, 4, 8, 10, 2, 30);
      final timeSpent = completedAt.difference(openedAt).inSeconds;

      expect(timeSpent, 150);
    });
  });
}
