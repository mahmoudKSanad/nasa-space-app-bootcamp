from django.apps import AppConfig

class SpaceAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'space_app'

    def ready(self):
        import space_app.signals
