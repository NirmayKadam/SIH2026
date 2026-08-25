from query.application.ports.intent_classifier_port import IntentClassifierPort
from query.application.ports.query_executor_port import QueryExecutorPort
from query.domain.entities import QueryAnswer


class AnswerNaturalLanguageQueryUseCase:
    def __init__(self, classifier: IntentClassifierPort, executor: QueryExecutorPort) -> None:
        self._classifier = classifier
        self._executor = executor

    def execute(self, question: str) -> QueryAnswer:
        classified = self._classifier.classify(question)
        return self._executor.execute(classified)
