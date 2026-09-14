from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
import json

from app.schemas.chat import ChatRequest
from app.services.rag_service import RAGService
from app.dependencies import get_rag_service

router = APIRouter()

@router.post("/completions")
async def chat_completions(request: ChatRequest, rag_service: RAGService = Depends(get_rag_service)):
    
    history_dicts = [{"role": m.role, "content": m.content} for m in request.history] if request.history else []
    
    async def event_generator():
        async for chunk in rag_service.astream_answer(request.message, history_dicts, request.student_id):
            if "error" in chunk:
                yield f"data: {json.dumps({'error': chunk['error']}, ensure_ascii=False)}\n\n"
            if chunk.get("done"):
                yield "data: [DONE]\n\n"
            elif "answer" in chunk or "sources" in chunk:
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
