from django.core.management.base import BaseCommand
from django.dispatch import Signal

from imageboard.signals.signals import active

usr_active = Signal(providing_args=[])


class Command(BaseCommand):

    def handle(self, *args, **options):
        usr_active.connect(active)
        usr_active.send(sender=self.__class__)
        usr_active.disconnect(active)

        self.stdout.write('Succes')
