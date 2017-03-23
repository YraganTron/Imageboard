import datetime

from django.core.management.base import BaseCommand
from django.dispatch import Signal
from django.utils import timezone

from imageboard.models import MySession, Session

from imageboard.signals.signals import count_usr

usr_hour = Signal(providing_args=[])


class Command(BaseCommand):

    def handle(self, *args, **options):
        now = timezone.now()
        two_hour = now - datetime.timedelta(hours=2)
        MySession.objects.filter(expire_date__range=(two_hour, now)).delete()
        Session.objects.filter(expire_date__range=(two_hour, now)).delete()

        usr_hour.connect(count_usr)
        usr_hour.send(sender=self.__class__)
        usr_hour.disconnect(count_usr)

        self.stdout.write('Succes')
