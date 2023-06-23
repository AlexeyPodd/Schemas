from django.apps import AppConfig


class MainappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mainapp'
    verbose_name = 'Schemas'

    def ready(self):
        from . import signals
