from unittest.mock import Mock
from query.application.use_cases.answer_natural_language_query import (
    AnswerNaturalLanguageQueryUseCase,
)
from query.domain.entities import ClassifiedQuery, QueryIntent, QueryAnswer


def test_orchestration():
    mock_classifier = Mock()
    mock_executor = Mock()

    question = "Who is connected to Alice?"
    classified = ClassifiedQuery(
        QueryIntent.NEIGHBORS_WITHIN_HOPS, {"entity_name": "Alice"}, 0.9
    )
    answer = QueryAnswer(
        QueryIntent.NEIGHBORS_WITHIN_HOPS, {"nodes": []}, "Explanation"
    )

    mock_classifier.classify.return_value = classified
    mock_executor.execute.return_value = answer

    use_case = AnswerNaturalLanguageQueryUseCase(mock_classifier, mock_executor)
    result = use_case.execute(question)

    assert result == answer
    mock_classifier.classify.assert_called_once_with(question)
    mock_executor.execute.assert_called_once_with(classified)
