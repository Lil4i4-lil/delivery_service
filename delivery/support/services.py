import os
from pathlib import Path

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from django.conf import settings


def _create_chroma_client():
    """
    dev -> PersistentClient (локальная папка, без сервиса chroma)
    prod -> HttpClient (контейнер chroma в docker-compose)
    """
    app_env = os.getenv('APP_ENV', 'dev')

    if app_env == 'prod':
        return chromadb.HttpClient(
            host=os.getenv('CHROMA_HOST', 'chroma'),
            port=int(os.getenv('CHROMA_PORT', '8000')),
            settings=Settings(anonymized_telemetry=False),
        )

    data_path = Path(settings.BASE_DIR) / 'chroma_data'
    return chromadb.PersistentClient(
        path=str(data_path),
        settings=Settings(anonymized_telemetry=False),
    )


chroma_client = _create_chroma_client()

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name='all-MiniLM-L6-v2',
)

collection = chroma_client.get_or_create_collection(
    name='support_knowledge_base',
    embedding_function=embedding_fn,  # type: ignore[arg-type]
)
