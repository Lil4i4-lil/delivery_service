from rest_framework import serializers


class SupportQuestionSerializer(serializers.Serializer):
    """Сериализатор для запроса к LLM"""

    question = serializers.CharField(max_length=1000)
