_WERBUNG_MODELS = frozenset({'werbung', 'werbungstat'})


class WerbungRouter:
    """
    Leitet alle Werbung- und WerbungStat-Queries zur 'pystore'-Datenbank.
    Wenn PYSTORE_DATABASE_URL nicht gesetzt ist, ist 'pystore' == 'default'.
    """

    def db_for_read(self, model, **hints):
        if model._meta.model_name in _WERBUNG_MODELS:
            return 'pystore'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.model_name in _WERBUNG_MODELS:
            return 'pystore'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db == 'pystore':
            return False  # pystore-DB wird vom pystore-Projekt verwaltet
        if model_name in _WERBUNG_MODELS:
            return False
        return None
