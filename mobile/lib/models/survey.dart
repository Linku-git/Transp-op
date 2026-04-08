/// Survey models for Session 73.

class SurveyData {
  final String id;
  final String title;
  final String? description;
  final List<SurveyQuestion> questions;
  final int responseCount;
  final bool isAnonymous;
  final bool isActive;

  const SurveyData({
    required this.id,
    required this.title,
    this.description,
    required this.questions,
    this.responseCount = 0,
    this.isAnonymous = false,
    this.isActive = true,
  });

  factory SurveyData.fromJson(Map<String, dynamic> json) {
    final questionsJson = json['questions'] as List? ?? [];
    return SurveyData(
      id: json['id'] as String,
      title: json['title'] as String,
      description: json['description'] as String?,
      questions: questionsJson
          .map((q) => SurveyQuestion.fromJson(q as Map<String, dynamic>))
          .toList(),
      responseCount: json['response_count'] as int? ?? 0,
      isAnonymous: json['is_anonymous'] as bool? ?? false,
      isActive: json['is_active'] as bool? ?? true,
    );
  }

  int get requiredCount => questions.where((q) => q.required).length;
}

class SurveyQuestion {
  final String id;
  final String text;
  final String questionType;
  final List<SurveyOption> options;
  final bool required;
  final int? minValue;
  final int? maxValue;

  const SurveyQuestion({
    required this.id,
    required this.text,
    required this.questionType,
    this.options = const [],
    this.required = true,
    this.minValue,
    this.maxValue,
  });

  factory SurveyQuestion.fromJson(Map<String, dynamic> json) {
    final optionsJson = json['options'] as List? ?? [];
    return SurveyQuestion(
      id: json['id'] as String,
      text: json['text'] as String,
      questionType: json['question_type'] as String,
      options: optionsJson
          .map((o) => SurveyOption.fromJson(o as Map<String, dynamic>))
          .toList(),
      required: json['required'] as bool? ?? true,
      minValue: json['min_value'] as int?,
      maxValue: json['max_value'] as int?,
    );
  }
}

class SurveyOption {
  final String text;
  final String? value;

  const SurveyOption({required this.text, this.value});

  String get effectiveValue => value ?? text;

  factory SurveyOption.fromJson(Map<String, dynamic> json) {
    return SurveyOption(
      text: json['text'] as String,
      value: json['value'] as String?,
    );
  }
}

class SurveyAnswer {
  final String questionId;
  final dynamic value;

  const SurveyAnswer({required this.questionId, required this.value});

  Map<String, dynamic> toJson() => {
    'question_id': questionId,
    'value': value,
  };
}
