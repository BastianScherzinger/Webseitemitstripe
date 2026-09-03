from django.conf import settings

_PYSTORE_MODELS = frozenset({'werbung', 'werbungstat', 'visitorlog'})
_NO_MIGRATE_MODELS = frozenset({'werbung', 'werbungstat'})  # von pystore-Projekt verwaltet


class WerbungRouter:
    """
    Leitet Werbung/WerbungStat/VisitorLog zur 'pystore'-Datenbank.
    Wenn PYSTORE_DATABASE_URL nicht gesetzt ist, ist 'pystore' == 'default'.
    VisitorLog wird direkt in pystore geschrieben – kein Background-Thread nötig.
    """

    def db_for_read(self, model, **hints):
        if model._meta.model_name in _PYSTORE_MODELS:
            return 'pystore'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.model_name in _PYSTORE_MODELS:
            return 'pystore'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Die Sperre gilt nur, solange die pystore-Datenbank wirklich vom
        # pystore-Projekt verwaltet wird (PYSTORE_DATABASE_URL gesetzt). Ohne
        # die Variable ist 'pystore' die eigene Datenbank; dort zu sperren
        # liesse die Tabellen lokal und im Testlauf komplett fehlen.
        if not getattr(settings, 'PYSTORE_IS_EXTERNAL', True):
            return None
        if db == 'pystore':
            return False  # pystore-DB wird vom pystore-Projekt verwaltet
        if model_name in _NO_MIGRATE_MODELS:
            return False  # Werbung-Tabellen werden vom pystore-Projekt verwaltet
        return None
