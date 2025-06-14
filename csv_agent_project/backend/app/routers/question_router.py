from fastapi import APIRouter, HTTPException
from app.models.models import QuestionRequest, QuestionResponse
from app.services.agent_service import process_question

router = APIRouter()

@router.post("/question", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    try:
        answer = process_question(request.question)
        return QuestionResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
