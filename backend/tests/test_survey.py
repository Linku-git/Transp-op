"""Tests for Survey/Poll System (Session 72)."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest

from app.models.survey import Survey
from app.models.survey_response import SurveyResponse as SurveyResponseModel
from app.schemas.survey import (
    SurveyCreate,
    SurveyQuestion,
    SurveyQuestionOption,
    SurveySubmitRequest,
    AnswerItem,
    SurveyAggregationResponse,
    QuestionAggregation,
)
from app.services.survey_service import _validate_answer


SAMPLE_QUESTIONS = [
    {
        "id": "q1",
        "text": "Comment évaluez-vous le trajet ?",
        "question_type": "rating",
        "min_value": 1,
        "max_value": 5,
        "required": True,
    },
    {
        "id": "q2",
        "text": "Quel mode de transport préférez-vous ?",
        "question_type": "single_choice",
        "options": [
            {"text": "Bus", "value": "bus"},
            {"text": "Covoiturage", "value": "carpool"},
            {"text": "Navette", "value": "shuttle"},
        ],
        "required": True,
    },
    {
        "id": "q3",
        "text": "Quels jours utilisez-vous le transport ?",
        "question_type": "multiple_choice",
        "options": [
            {"text": "Lundi", "value": "mon"},
            {"text": "Mardi", "value": "tue"},
            {"text": "Mercredi", "value": "wed"},
            {"text": "Jeudi", "value": "thu"},
            {"text": "Vendredi", "value": "fri"},
        ],
        "required": False,
    },
    {
        "id": "q4",
        "text": "Commentaires libres",
        "question_type": "text",
        "required": False,
    },
    {
        "id": "q5",
        "text": "Satisfaction globale",
        "question_type": "slider",
        "min_value": 0,
        "max_value": 100,
        "required": True,
    },
]


class TestSurveyModel:
    def test_create_survey(self):
        survey = Survey(
            tenant_id=uuid.uuid4(),
            content_id=uuid.uuid4(),
            title="Enquête mobilité",
            questions=SAMPLE_QUESTIONS,
            is_anonymous=False,
            response_count=0,
        )
        assert survey.title == "Enquête mobilité"
        assert len(survey.questions) == 5
        assert survey.response_count == 0
        assert survey.is_anonymous is False

    def test_create_anonymous_survey(self):
        survey = Survey(
            tenant_id=uuid.uuid4(),
            content_id=uuid.uuid4(),
            title="Enquête anonyme",
            questions=SAMPLE_QUESTIONS,
            is_anonymous=True,
        )
        assert survey.is_anonymous is True

    def test_survey_with_all_question_types(self):
        survey = Survey(
            tenant_id=uuid.uuid4(),
            content_id=uuid.uuid4(),
            title="Toutes les questions",
            questions=SAMPLE_QUESTIONS,
        )
        types = {q["question_type"] for q in survey.questions}
        assert types == {"rating", "single_choice", "multiple_choice", "text", "slider"}


class TestSurveyResponseModel:
    def test_create_response(self):
        response = SurveyResponseModel(
            tenant_id=uuid.uuid4(),
            survey_id=uuid.uuid4(),
            employee_id=uuid.uuid4(),
            responses=[
                {"question_id": "q1", "value": 4},
                {"question_id": "q2", "value": "bus"},
            ],
            submitted_at=datetime.now(timezone.utc),
        )
        assert len(response.responses) == 2
        assert response.employee_id is not None

    def test_anonymous_response(self):
        response = SurveyResponseModel(
            tenant_id=uuid.uuid4(),
            survey_id=uuid.uuid4(),
            employee_id=None,
            responses=[{"question_id": "q1", "value": 3}],
            submitted_at=datetime.now(timezone.utc),
        )
        assert response.employee_id is None


class TestSurveySchemas:
    def test_create_schema_valid(self):
        schema = SurveyCreate(
            content_id=uuid.uuid4(),
            title="Test survey",
            questions=[
                SurveyQuestion(
                    id="q1",
                    text="Rate this",
                    question_type="rating",
                    min_value=1,
                    max_value=5,
                ),
            ],
        )
        assert schema.title == "Test survey"
        assert len(schema.questions) == 1

    def test_create_rejects_empty_title(self):
        with pytest.raises(Exception):
            SurveyCreate(
                content_id=uuid.uuid4(),
                title="",
                questions=[
                    SurveyQuestion(id="q1", text="Q", question_type="text"),
                ],
            )

    def test_create_rejects_empty_questions(self):
        with pytest.raises(Exception):
            SurveyCreate(
                content_id=uuid.uuid4(),
                title="Test",
                questions=[],
            )

    def test_create_rejects_invalid_question_type(self):
        with pytest.raises(Exception):
            SurveyQuestion(id="q1", text="Q", question_type="invalid")

    def test_submit_request_valid(self):
        request = SurveySubmitRequest(
            employee_id=uuid.uuid4(),
            responses=[
                AnswerItem(question_id="q1", value=4),
                AnswerItem(question_id="q2", value="bus"),
            ],
        )
        assert len(request.responses) == 2

    def test_submit_request_anonymous(self):
        request = SurveySubmitRequest(
            employee_id=None,
            responses=[AnswerItem(question_id="q1", value=3)],
        )
        assert request.employee_id is None


class TestResponseValidation:
    def test_valid_rating(self):
        answer = AnswerItem(question_id="q1", value=4)
        question = SAMPLE_QUESTIONS[0]
        # Should not raise
        _validate_answer(answer, question, "rating")

    def test_rating_out_of_range(self):
        answer = AnswerItem(question_id="q1", value=6)
        question = SAMPLE_QUESTIONS[0]
        with pytest.raises(ValueError, match="between 1 and 5"):
            _validate_answer(answer, question, "rating")

    def test_valid_single_choice(self):
        answer = AnswerItem(question_id="q2", value="bus")
        question = SAMPLE_QUESTIONS[1]
        _validate_answer(answer, question, "single_choice")

    def test_invalid_single_choice(self):
        answer = AnswerItem(question_id="q2", value="bicycle")
        question = SAMPLE_QUESTIONS[1]
        with pytest.raises(ValueError, match="Invalid choice"):
            _validate_answer(answer, question, "single_choice")

    def test_valid_multiple_choice(self):
        answer = AnswerItem(question_id="q3", value=["mon", "wed", "fri"])
        question = SAMPLE_QUESTIONS[2]
        _validate_answer(answer, question, "multiple_choice")

    def test_invalid_multiple_choice(self):
        answer = AnswerItem(question_id="q3", value=["mon", "sunday"])
        question = SAMPLE_QUESTIONS[2]
        with pytest.raises(ValueError, match="Invalid choice"):
            _validate_answer(answer, question, "multiple_choice")

    def test_valid_text(self):
        answer = AnswerItem(question_id="q4", value="Great service!")
        question = SAMPLE_QUESTIONS[3]
        _validate_answer(answer, question, "text")

    def test_valid_slider(self):
        answer = AnswerItem(question_id="q5", value=75)
        question = SAMPLE_QUESTIONS[4]
        _validate_answer(answer, question, "slider")

    def test_slider_out_of_range(self):
        answer = AnswerItem(question_id="q5", value=150)
        question = SAMPLE_QUESTIONS[4]
        with pytest.raises(ValueError, match="between 0 and 100"):
            _validate_answer(answer, question, "slider")

    def test_wrong_type_for_rating(self):
        answer = AnswerItem(question_id="q1", value="not a number")
        question = SAMPLE_QUESTIONS[0]
        with pytest.raises(ValueError, match="expects number"):
            _validate_answer(answer, question, "rating")

    def test_wrong_type_for_multiple_choice(self):
        answer = AnswerItem(question_id="q3", value="not a list")
        question = SAMPLE_QUESTIONS[2]
        with pytest.raises(ValueError, match="expects list"):
            _validate_answer(answer, question, "multiple_choice")


class TestAggregation:
    def test_empty_aggregation(self):
        agg = SurveyAggregationResponse(
            survey_id=uuid.uuid4(),
            total_responses=0,
            questions=[],
        )
        assert agg.total_responses == 0

    def test_question_aggregation_with_distribution(self):
        agg = QuestionAggregation(
            question_id="q2",
            question_text="Preferred transport?",
            question_type="single_choice",
            total_responses=10,
            distribution={"bus": 5, "carpool": 3, "shuttle": 2},
        )
        assert sum(agg.distribution.values()) == 10

    def test_question_aggregation_with_average(self):
        agg = QuestionAggregation(
            question_id="q1",
            question_text="Rate your trip",
            question_type="rating",
            total_responses=3,
            average=4.33,
        )
        assert agg.average == 4.33

    def test_question_aggregation_with_text_responses(self):
        agg = QuestionAggregation(
            question_id="q4",
            question_text="Comments",
            question_type="text",
            total_responses=2,
            text_responses=["Great!", "Could be better"],
        )
        assert len(agg.text_responses) == 2
