import os
import time

from openai import OpenAI
from loguru import logger
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from .serializers import SupportQuestionSerializer
from .services import collection


class SupportAskView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = SupportQuestionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        question = serializer.validated_data['question']

        rag_logger = logger.bind(component="support", question=question)
        rag_logger.info("RAG request received")
        started_at = time.monotonic()

        # 1. Поиск в ChromaDB
        results = collection.query(
            query_texts=[question],
            n_results=2,
            include=["documents", "metadatas"],
        )
        retrieved_docs = results.get('documents', [[]])[0]
        context = "\n".join(retrieved_docs) if retrieved_docs else "Контекст не найден."

        rag_logger.debug(
            "Извлечение данных из ChromaDB: docs_count={count}, has_context={has_context}",
            count=len(retrieved_docs),
            has_context=bool(retrieved_docs),
        )
        rag_logger.debug("Извлеченные документы: {docs}", docs=retrieved_docs)

        if not retrieved_docs:
            rag_logger.warning(
                "В ChromaDB не найдено документов по этому вопросу, "
                "LLM будет вызвана с пустым контекстом"
            )

        # 2. Вызов YandexGPT через OpenAI-совместимый API
        client = OpenAI(
            api_key=os.environ["YANDEX_API_KEY"],
            base_url="https://llm.api.cloud.yandex.net/v1",
            timeout=120.0,
        )

        system_prompt = (
            "Ты — служба поддержки сервиса международной доставки. "
            "Отвечай на вопрос пользователя, используя ТОЛЬКО предоставленный контекст. "
            "Если ответа в контексте нет, скажи, что не можешь помочь."
        )
        user_prompt = f"Контекст:\n{context}\n\nВопрос: {question}"

        model_name = os.environ.get('YANDEX_MODEL', 'yandexgpt-lite/latest')
        rag_logger.info("Вызов LLM, model={model}", model=model_name)
        llm_started_at = time.monotonic()

        try:
            response = client.chat.completions.create(
                model=f"gpt://{os.environ['YANDEX_FOLDER_ID']}/{model_name}",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                max_tokens=1000,
            )
            answer = response.choices[0].message.content

            llm_duration = time.monotonic() - llm_started_at
            usage = getattr(response, "usage", None)
            rag_logger.info(
                "LLM ответ получен: duration_s={duration:.2f}, "
                "prompt_tokens={pt}, completion_tokens={ct}",
                duration=llm_duration,
                pt=getattr(usage, "prompt_tokens", None),
                ct=getattr(usage, "completion_tokens", None),
            )
            rag_logger.debug("LLM ответ: {answer}", answer=answer)
        except Exception as exc:
            llm_duration = time.monotonic() - llm_started_at
            rag_logger.error(
                "LLM вызвало ошибку после {duration:.2f}s: {exc}",
                duration=llm_duration,
                exc=exc,
            )
            return Response(
                {"detail": f"Ошибка при обращении к LLM: {exc}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        total_duration = time.monotonic() - started_at
        rag_logger.info(
            "RAG запрос завершен: total_duration_s={duration:.2f}",
            duration=total_duration,
        )

        return Response({
            "answer": answer
        })
