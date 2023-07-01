from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .models import DataSet


@receiver(pre_delete, sender=DataSet)
def date_set_delete(sender, instance, **kwargs):
    if instance.file:
        instance.file.delete()
