"""
Query REST boundary — the "agentic querying" layer from the problem statement:

  POST /api/query/ask   {"question": "who is connected to Ravi within 2 hops?"}
"""
from fastapi import APIRouter, Depends

from query.application.use_cases.answer_natural_language_query import (
    AnswerNaturalLanguageQueryUseCase,
)
from query.interface.rest.schemas import AskQuestionRequestDTO, AskQuestionResponseDTO

router = APIRouter(prefix="/api/query", tags=["query"])


def get_use_case() -> AnswerNaturalLanguageQueryUseCase:
    raise NotImplementedError("Dependency not wired — see api_gateway/di_container.py")


@router.post("/ask", response_model=AskQuestionResponseDTO)
def ask_question(
    body: AskQuestionRequestDTO,
    use_case: AnswerNaturalLanguageQueryUseCase = Depends(get_use_case),
) -> AskQuestionResponseDTO:
    answer = use_case.execute(body.question)
    return AskQuestionResponseDTO(
        intent=answer.intent.value, result=answer.result, explanation=answer.explanation
    )
