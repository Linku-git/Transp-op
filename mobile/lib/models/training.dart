/// Training models for Session 71.

class TrainingContent {
  final String id;
  final String title;
  final String? body;
  final String? mediaUrl;
  final MediaType mediaType;
  final List<QuizQuestion> questions;
  final int passingScore;
  final DateTime? publishedAt;

  const TrainingContent({
    required this.id,
    required this.title,
    this.body,
    this.mediaUrl,
    this.mediaType = MediaType.video,
    this.questions = const [],
    this.passingScore = 70,
    this.publishedAt,
  });

  bool get hasMedia => mediaUrl != null && mediaUrl!.isNotEmpty;
  bool get hasQuiz => questions.isNotEmpty;

  factory TrainingContent.fromJson(Map<String, dynamic> json) {
    final questionsJson = json['questions'] as List? ?? [];
    return TrainingContent(
      id: json['id'] as String,
      title: json['title'] as String,
      body: json['body'] as String?,
      mediaUrl: json['media_url'] as String?,
      mediaType: MediaType.fromString(json['media_type'] as String? ?? 'video'),
      questions: questionsJson
          .map((q) => QuizQuestion.fromJson(q as Map<String, dynamic>))
          .toList(),
      passingScore: json['passing_score'] as int? ?? 70,
      publishedAt: json['published_at'] != null
          ? DateTime.parse(json['published_at'] as String)
          : null,
    );
  }
}

enum MediaType {
  video,
  audio;

  String get label => switch (this) {
    video => 'Vidéo',
    audio => 'Audio',
  };

  static MediaType fromString(String value) => switch (value) {
    'audio' => MediaType.audio,
    _ => MediaType.video,
  };
}

class QuizQuestion {
  final String id;
  final String text;
  final List<QuizOption> options;
  final int correctIndex;

  const QuizQuestion({
    required this.id,
    required this.text,
    required this.options,
    required this.correctIndex,
  });

  factory QuizQuestion.fromJson(Map<String, dynamic> json) {
    final optionsJson = json['options'] as List? ?? [];
    return QuizQuestion(
      id: json['id'] as String? ?? '',
      text: json['text'] as String,
      options: optionsJson
          .map((o) => QuizOption.fromJson(o as Map<String, dynamic>))
          .toList(),
      correctIndex: json['correct_index'] as int? ?? 0,
    );
  }
}

class QuizOption {
  final String text;

  const QuizOption({required this.text});

  factory QuizOption.fromJson(Map<String, dynamic> json) {
    return QuizOption(text: json['text'] as String);
  }
}

class QuizResult {
  final int totalQuestions;
  final int correctAnswers;
  final int passingScore;

  const QuizResult({
    required this.totalQuestions,
    required this.correctAnswers,
    required this.passingScore,
  });

  double get scorePercent =>
      totalQuestions > 0 ? (correctAnswers / totalQuestions) * 100 : 0;

  bool get passed => scorePercent >= passingScore;

  String get scoreLabel => '${scorePercent.round()}%';
}
