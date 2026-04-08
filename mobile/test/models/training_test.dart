import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/models/training.dart';

void main() {
  group('TrainingContent', () {
    test('fromJson parses all fields', () {
      final json = {
        'id': 't-1',
        'title': 'Formation sécurité',
        'body': '<p>Contenu de la formation</p>',
        'media_url': 'https://example.com/video.mp4',
        'media_type': 'video',
        'passing_score': 80,
        'published_at': '2026-04-08T10:00:00Z',
        'questions': [
          {
            'id': 'q1',
            'text': 'Quelle est la bonne pratique ?',
            'options': [
              {'text': 'Option A'},
              {'text': 'Option B'},
              {'text': 'Option C'},
            ],
            'correct_index': 1,
          },
        ],
      };

      final training = TrainingContent.fromJson(json);
      expect(training.id, 't-1');
      expect(training.title, 'Formation sécurité');
      expect(training.mediaUrl, 'https://example.com/video.mp4');
      expect(training.mediaType, MediaType.video);
      expect(training.passingScore, 80);
      expect(training.questions.length, 1);
      expect(training.hasMedia, true);
      expect(training.hasQuiz, true);
    });

    test('hasMedia returns false without url', () {
      final training = TrainingContent(id: '1', title: 'Test');
      expect(training.hasMedia, false);
    });

    test('hasQuiz returns false without questions', () {
      final training = TrainingContent(id: '1', title: 'Test');
      expect(training.hasQuiz, false);
    });
  });

  group('QuizQuestion', () {
    test('fromJson parses options', () {
      final json = {
        'id': 'q1',
        'text': 'Question test',
        'options': [
          {'text': 'A'},
          {'text': 'B'},
        ],
        'correct_index': 0,
      };

      final q = QuizQuestion.fromJson(json);
      expect(q.text, 'Question test');
      expect(q.options.length, 2);
      expect(q.correctIndex, 0);
    });
  });

  group('MediaType', () {
    test('fromString parses audio', () {
      expect(MediaType.fromString('audio'), MediaType.audio);
    });

    test('fromString defaults to video', () {
      expect(MediaType.fromString('unknown'), MediaType.video);
    });

    test('labels are in French', () {
      expect(MediaType.video.label, 'Vidéo');
      expect(MediaType.audio.label, 'Audio');
    });
  });

  group('QuizResult', () {
    test('calculates score correctly', () {
      const result = QuizResult(
        totalQuestions: 5,
        correctAnswers: 4,
        passingScore: 70,
      );
      expect(result.scorePercent, 80.0);
      expect(result.passed, true);
      expect(result.scoreLabel, '80%');
    });

    test('fails when below passing score', () {
      const result = QuizResult(
        totalQuestions: 5,
        correctAnswers: 2,
        passingScore: 70,
      );
      expect(result.scorePercent, 40.0);
      expect(result.passed, false);
    });

    test('handles zero questions', () {
      const result = QuizResult(
        totalQuestions: 0,
        correctAnswers: 0,
        passingScore: 70,
      );
      expect(result.scorePercent, 0);
      expect(result.passed, false);
    });

    test('passes at exact threshold', () {
      const result = QuizResult(
        totalQuestions: 10,
        correctAnswers: 7,
        passingScore: 70,
      );
      expect(result.scorePercent, 70.0);
      expect(result.passed, true);
    });
  });
}
