from pydantic import BaseModel


class AskQuestionRequestDTO(BaseModel):
    question: str


class AskQuestionResponseDTO(BaseModel):
    intent: str
    result: dict
    explanation: str
