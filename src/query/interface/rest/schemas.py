from pydantic import BaseModel


from shared_kernel.interface.validators import SanitizedString

class AskQuestionRequestDTO(BaseModel):
    question: SanitizedString


class AskQuestionResponseDTO(BaseModel):
    intent: str
    result: dict
    explanation: str
