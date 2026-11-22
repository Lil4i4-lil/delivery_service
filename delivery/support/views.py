import os

from openai import OpenAI
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

        # 1. Поиск в ChromaDB
        results = collection.query(
            query_texts=[question],
            n_results=2,
            include=["documents", "metadatas"],
        )
        retrieved_docs = results.get('documents', [[]])[0]
        context = "\n".join(retrieved_docs) if retrieved_docs else "Контекст не найден."

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

        try:
            response = client.chat.completions.create(
                model=f"gpt://{os.environ['YANDEX_FOLDER_ID']}/{os.environ.get('YANDEX_MODEL', 'yandexgpt-lite/latest')}",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                max_tokens=1000,
            )
            answer = response.choices[0].message.content
        except Exception as exc:
            return Response(
                {"detail": f"Ошибка при обращении к LLM: {exc}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response({
            "answer": answer,
            "sources": [meta.get('source') for meta in results.get('metadatas', [[]])[0]],
        })