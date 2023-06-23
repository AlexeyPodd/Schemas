from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .models import DataSet, DataType


@receiver(pre_delete, sender=DataSet)
def date_set_delete(sender, instance, **kwargs):
    if instance.file:
        instance.file.delete()


@receiver(pre_delete, sender=DataType)
def date_set_delete(sender, instance, **kwargs):
    if instance.source_file:
        instance.source_file.delete()
