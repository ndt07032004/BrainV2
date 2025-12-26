"""
RAG Engine built on top of existing ChromaDB and embedding logic.

This wraps the previous `ChatbotService` idea into a simpler interface
that uses LLMManager for answer generation when needed.
"""

from __future__ import annotations

import warnings
from typing import List

from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain.chains import RetrievalQA

from src.helper import download_hugging_face_embeddings
from src.prompt import system_prompt
from config import settings
from utils.logger import get_logger

# Suppress deprecation warnings
warnings.filterwarnings("ignore", message=".*Convert_system_message_to_human will be deprecated.*")
warnings.filterwarnings("ignore", category=UserWarning, module="langchain_google_genai")

logger = get_logger(__name__)


class RAGEngine:
    def __init__(self):
        logger.info("--- Initializing RAG Engine ---")
        self.embeddings = download_hugging_face_embeddings()
        self.retriever = self._load_vector_db()
        self.rag_chain = self._create_rag_chain()
        logger.info("--- RAG Engine is ready ---")

    def _load_vector_db(self):
        logger.info(f"Loading ChromaDB from: {settings.PERSIST_DIRECTORY} ...")
        vectordb = Chroma(
            persist_directory=settings.PERSIST_DIRECTORY,
            embedding_function=self.embeddings,
        )
        retriever = vectordb.as_retriever(search_kwargs={"k": 5})
        return retriever

    def _create_rag_chain(self):
        logger.info(f"Configuring LLM for RAG: {settings.LLM_MODEL_NAME} ...")

        # Reuse original Google GenAI LLM for now; can later refactor to use LLMManager directly.
        from langchain_google_genai import ChatGoogleGenerativeAI

        chat_model = ChatGoogleGenerativeAI(
            model=settings.LLM_MODEL_NAME,
            temperature=0.7,
            max_output_tokens=512,
            google_api_key=settings.GOOGLE_API_KEY,
            convert_system_message_to_human=True,
        )

        template = f"""{system_prompt}

Dựa vào thông tin ngữ cảnh được cung cấp dưới đây để trả lời câu hỏi.
Nếu không tìm thấy thông tin trong ngữ cảnh, hãy nói rằng bạn không biết.

Ngữ cảnh:
{{context}}

Câu hỏi:
{{question}}

Câu trả lời hữu ích:"""

        prompt = ChatPromptTemplate.from_template(template)

        rag_chain = RetrievalQA.from_chain_type(
            llm=chat_model,
            retriever=self.retriever,
            chain_type="stuff",
            chain_type_kwargs={"prompt": prompt},
        )
        logger.info("RAG chain created successfully.")
        return rag_chain

    def get_answer(self, question: str) -> str:
        logger.info(f"RAG question: {question}")
        try:
            response = self.rag_chain.invoke({"query": question})
            answer = response.get("result", "").strip()
            if not answer:
                answer = "Xin lỗi, tôi không tìm thấy câu trả lời phù hợp trong dữ liệu."
            return answer
        except Exception as e:
            logger.error(f"Error while running RAG: {e}", exc_info=True)
            return "Đã xảy ra lỗi khi truy vấn RAG, vui lòng thử lại."


rag_engine = RAGEngine()


