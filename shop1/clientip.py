"""Die Adresse des Besuchers hinter dem Railway-Proxy (EIG105).

Der **letzte** Eintrag in ``X-Forwarded-For`` ist der, den der einzige Proxy vor
Gunicorn (``DOCUMENTATION.md`` § 1) selbst gesehen hat. Den ersten kann der
Absender frei setzen: Wer ihn verwendet, lässt sich eine beliebige Adresse
unterschieben – bei der Drosselung wie bei der Besucherzählung. Ohne Proxy-Kopf
(lokal) gilt ``REMOTE_ADDR``.
"""


def client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if xff.strip():
        return xff.split(',')[-1].strip()
    return request.META.get('REMOTE_ADDR', '')
