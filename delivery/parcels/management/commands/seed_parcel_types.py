from django.core.management.base import BaseCommand

from parcels.models import ParcelType


class Command(BaseCommand):
    help = 'Создаёт три типа посылки, если их ещё нет'

    def handle(self, *args, **options):
        for name in ('clothes', 'electronics', 'other'):
            obj, created = ParcelType.objects.get_or_create(name=name)
            status = 'created' if created else 'exists'
            self.stdout.write(f'{name}: {status}')
        self.stdout.write(self.style.SUCCESS('Готово.'))
