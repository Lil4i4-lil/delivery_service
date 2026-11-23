from django.core.management.base import BaseCommand

from parcels.tasks import calculate_delivery_costs


class Command(BaseCommand):
    """Команда для запуска перерасчета стоимости посылки"""

    help = 'Рассчитать стоимость доставки для необработанных посылок (вне расписания)'

    def handle(self, *args, **options):
        self.stdout.write('Запуск расчёта стоимости доставки...')
        updated = calculate_delivery_costs()
        self.stdout.write(self.style.SUCCESS(f'Готово. Обновлено посылок: {updated}'))
