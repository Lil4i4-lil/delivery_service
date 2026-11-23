from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions
from django.conf import settings

CHROMA_DATA_PATH = Path(settings.BASE_DIR) / 'chroma_data'

chroma_client = chromadb.PersistentClient(path=str(CHROMA_DATA_PATH))
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name='all-MiniLM-L6-v2'
)
collection = chroma_client.get_or_create_collection(
    name='support_knowledge_base',
    embedding_function=embedding_fn,  # type: ignore[arg-type]
)
