from django.apps import AppConfig


class Shop1Config(AppConfig):
    name = 'shop1'
    verbose_name = 'Shop'
    
    def ready(self):
        """Registriere Signals wenn die App bereit ist"""
        import shop1.signals  # noqa
