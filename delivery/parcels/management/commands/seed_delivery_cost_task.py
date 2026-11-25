from django.core.management.base import BaseCommand
from django_celery_beat.models import CrontabSchedule, PeriodicTask


class Command(BaseCommand):
    help = 'Создаёт PeriodicTask для расчёта стоимости доставки'

    def handle(self, *args, **options):
        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute='*/5',
            hour='*',
            day_of_week='*',
            day_of_month='*',
            month_of_year='*',
        )
        task, created = PeriodicTask.objects.get_or_create(
            name='calculate-delivery-costs',
            defaults={
                'task': 'parcels.tasks.calculate_delivery_costs',
                'crontab': schedule,
                'enabled': True,
            },
        )
        self.stdout.write(self.style.SUCCESS(f'PeriodicTask: {"created" if created else "exists"}'))
