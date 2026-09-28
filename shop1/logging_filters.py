"""Filter fuer das Logging: begrenzt Fehler-Mails gegen eine Fehlerschleife.

Ohne diese Drossel wuerde eine sich staendig wiederholende Ausnahme (kaputter
Hintergrundjob, Endlosschleife) das Postfach der Betreiberin fluten - genau das
Muster, das schon einmal bei den Besuchsmails abgestellt werden musste
(``PageVisitMiddleware``, Commit e58775a).
"""

from django.core.cache import cache

#: Je Fehlerquelle (Pfad + Ausnahmetyp) hoechstens eine Mail in diesem Fenster.
_FENSTER = 600


class FehlermailDrossel:
    """``logging``-Filter fuer den ``mail_admins``-Handler."""

    def filter(self, record):
        pfad = getattr(getattr(record, 'request', None), 'path', None) or record.pathname
        art = record.exc_info[0].__name__ if record.exc_info else record.getMessage()[:80]
        schluessel = f'fehlermail:{pfad}:{art}'
        return cache.add(schluessel, 1, _FENSTER)
