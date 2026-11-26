from pathlib import Path
import uuid

from django.conf import settings
from django.core.management.base import BaseCommand
from support.services import collection


class Command(BaseCommand):
    help = 'Загружает базу знаний в ChromaDB'

    def handle(self, *args, **options):
        kb_path = Path(settings.BASE_DIR) / 'support' / 'knowledge_base.txt'
        with open(kb_path, encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]

        documents = []
        metadatas = []
        ids = []
        for i, line in enumerate(lines):
            documents.append(line)
            metadatas.append({'source': 'knowledge_base.txt', 'line': i + 1})
            ids.append(f'doc_{uuid.uuid4().hex[:8]}')

        collection.add(documents=documents, metadatas=metadatas, ids=ids)
        self.stdout.write(self.style.SUCCESS(f'Загружено {len(documents)} документов.'))
