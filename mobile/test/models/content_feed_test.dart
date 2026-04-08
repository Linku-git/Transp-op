import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/models/content_feed.dart';

void main() {
  group('FeedContent', () {
    test('fromJson parses all fields correctly', () {
      final json = {
        'id': 'c-123',
        'title': 'Formation sécurité',
        'body': '<p>Contenu de la formation</p>',
        'content_type': 'training',
        'media_url': 'https://example.com/image.jpg',
        'published_at': '2026-04-08T10:00:00Z',
        'expires_at': '2026-05-01T00:00:00Z',
        'delivered': true,
        'viewed': true,
        'completed': false,
      };

      final item = FeedContent.fromJson(json);
      expect(item.id, 'c-123');
      expect(item.title, 'Formation sécurité');
      expect(item.contentType, 'training');
      expect(item.mediaUrl, 'https://example.com/image.jpg');
      expect(item.delivered, true);
      expect(item.viewed, true);
      expect(item.completed, false);
    });

    test('fromJson handles missing optional fields', () {
      final json = {
        'id': '1',
        'title': 'Test',
      };

      final item = FeedContent.fromJson(json);
      expect(item.body, isNull);
      expect(item.contentType, 'news');
      expect(item.mediaUrl, isNull);
      expect(item.publishedAt, isNull);
      expect(item.delivered, false);
      expect(item.viewed, false);
      expect(item.completed, false);
    });

    test('snippet strips HTML tags', () {
      final item = FeedContent(
        id: '1',
        title: 'Test',
        body: '<p>Hello <strong>world</strong></p>',
        contentType: 'news',
      );
      expect(item.snippet, 'Hello world');
    });

    test('snippet truncates long text', () {
      final longBody = '<p>${'A' * 200}</p>';
      final item = FeedContent(
        id: '1',
        title: 'Test',
        body: longBody,
        contentType: 'news',
      );
      expect(item.snippet.length, lessThanOrEqualTo(123)); // 120 + "..."
      expect(item.snippet.endsWith('...'), true);
    });

    test('isNew returns true when not delivered', () {
      final item = FeedContent(
        id: '1',
        title: 'Test',
        contentType: 'news',
        delivered: false,
        viewed: false,
      );
      expect(item.isNew, true);
    });

    test('isNew returns false when delivered', () {
      final item = FeedContent(
        id: '1',
        title: 'Test',
        contentType: 'news',
        delivered: true,
        viewed: false,
      );
      expect(item.isNew, false);
    });

    test('typeLabel returns correct French labels', () {
      expect(
        FeedContent(id: '1', title: 'T', contentType: 'news').typeLabel,
        'Actualité',
      );
      expect(
        FeedContent(id: '1', title: 'T', contentType: 'training').typeLabel,
        'Formation',
      );
      expect(
        FeedContent(id: '1', title: 'T', contentType: 'safety').typeLabel,
        'Sécurité',
      );
      expect(
        FeedContent(id: '1', title: 'T', contentType: 'survey').typeLabel,
        'Sondage',
      );
    });

    test('toJson round-trips correctly', () {
      final item = FeedContent(
        id: 'x',
        title: 'Round trip',
        body: '<p>body</p>',
        contentType: 'safety',
        delivered: true,
        viewed: true,
        completed: true,
      );
      final json = item.toJson();
      final restored = FeedContent.fromJson(json);
      expect(restored.id, item.id);
      expect(restored.title, item.title);
      expect(restored.contentType, item.contentType);
      expect(restored.delivered, item.delivered);
    });
  });
}
