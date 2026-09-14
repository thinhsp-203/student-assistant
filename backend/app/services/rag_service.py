from typing import AsyncGenerator, List, Dict, Any, Optional
import json

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_classic.chains.history_aware_retriever import create_history_aware_retriever

from app.services.chroma_service import ChromaService
from app.services.student_service import StudentService
from app.core.config import settings
from app.services.prompt_templates import SYSTEM_PROMPT


def _source_payload(document: Any) -> Dict[str, Any]:
    metadata = dict(getattr(document, "metadata", {}) or {})
    content = getattr(document, "page_content", "") or ""
    source_name = metadata.get("source") or metadata.get("title") or "Tài liệu không xác định"
    metadata.setdefault("title", source_name)
    return {
        "content": content[:500],
        "metadata": metadata,
    }

class RAGService:
    def __init__(self, chroma_service: ChromaService, student_service: StudentService):
        self.chroma_service = chroma_service
        self.student_service = student_service
        
        self.llm = ChatGoogleGenerativeAI(
            model=settings.LLM_MODEL,
            temperature=0.2,
            google_api_key=settings.GOOGLE_API_KEY,
        )

    async def astream_answer(self, question: str, chat_history: Optional[List[Dict[str, str]]] = None, student_id: Optional[str] = None) -> AsyncGenerator[Dict[str, Any], None]:
        try:
            # 1. Get student context if provided
            student_context = ""
            if student_id:
                student_context = await self.student_service.get_student_context(student_id)

            # Build history objects
            history_messages = []
            if chat_history:
                for msg in chat_history:
                    if msg.get("role") == "user":
                        history_messages.append(HumanMessage(content=msg.get("content", "")))
                    else:
                        history_messages.append(AIMessage(content=msg.get("content", "")))

            # 2. Build retriever
            retriever = self.chroma_service.get_retriever(k=settings.RETRIEVAL_TOP_K)

            # 3. History-aware retriever
            contextualize_q_system_prompt = (
                "Cho đoạn hội thoại trước đó và câu hỏi mới nhất của người dùng. "
                "Có thể câu hỏi mới tham chiếu đến ngữ cảnh trong hội thoại trước đó. "
                "Hãy viết lại câu hỏi thành một câu hỏi độc lập có thể hiểu được mà không cần đoạn hội thoại trước đó. "
                "KHÔNG trả lời câu hỏi, chỉ định dạng lại nếu cần và nếu không, hãy giữ nguyên."
            )
            contextualize_q_prompt = ChatPromptTemplate.from_messages([
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ])
            history_aware_retriever = create_history_aware_retriever(
                self.llm, retriever, contextualize_q_prompt
            )

            # 4. Create QA chain
            qa_system_prompt = SYSTEM_PROMPT
            if student_context:
                qa_system_prompt += f"\n\n{student_context}"

            qa_prompt = ChatPromptTemplate.from_messages([
                ("system", qa_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ])
            question_answer_chain = create_stuff_documents_chain(self.llm, qa_prompt)

            # 5. Full RAG chain
            rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

            # 6 & 7. Stream the response
            sources = []
            sources_sent = False
            answer_emitted = False
            async for chunk in rag_chain.astream({"input": question, "chat_history": history_messages}):
                if "context" in chunk:
                    sources = [_source_payload(doc) for doc in chunk["context"]]
                    if sources and not sources_sent:
                        yield {"sources": sources}
                        sources_sent = True
                if "answer" in chunk:
                    answer_emitted = True
                    yield {"answer": chunk["answer"], "sources": sources}
            
            if not sources and not answer_emitted:
                yield {
                    "answer": (
                        "Tôi chưa tìm thấy tài liệu phù hợp để trả lời chắc chắn câu hỏi này. "
                        "Vui lòng cung cấp thêm ngữ cảnh hoặc liên hệ phòng đào tạo."
                    )
                }
            # 8. Done chunk
            yield {"done": True}

        except Exception as e:
            yield {"error": str(e), "done": True}
