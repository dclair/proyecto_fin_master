from django.core.management.base import BaseCommand
from gamification.models import Badge

class Command(BaseCommand):
    help = 'Crea las medallas base para el sistema de Gamificación'

    def handle(self, *args, **kwargs):
        badges_data = [
            {
                'name': 'Voz Holística',
                'code_name': 'voz-holistica',
                'description': 'Has iluminado a la comunidad. Otorgada por recibir 50 likes en total.',
                'icon': 'fas fa-leaf text-success'
            },
            {
                'name': 'Maestro Facilitador',
                'code_name': 'maestro-facilitador',
                'description': 'Líder en naturopatía. Otorgada por organizar 3 eventos con alta asistencia.',
                'icon': 'fas fa-sun text-warning'
            },
            {
                'name': 'Guía de Luz',
                'code_name': 'guia-de-luz',
                'description': 'Excelencia reconocida. Otorgada por conseguir 5 valoraciones con promedio de excelencia (mayor a 4.5 estrellas).',
                'icon': 'fas fa-star-of-life text-info'
            }
        ]

        count = 0
        for data in badges_data:
            badge, created = Badge.objects.get_or_create(code_name=data['code_name'], defaults=data)
            if created:
                count += 1
                self.stdout.write(self.style.SUCCESS(f'Medalla creada: {badge.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'La medalla {badge.name} ya existía.'))

        self.stdout.write(self.style.SUCCESS(f'Proceso completado. Se crearon {count} medallas.'))
