"""IndexNow: geänderte Adressen sofort an die teilnehmenden Suchmaschinen melden.

IndexNow (indexnow.org) ist ein offenes Protokoll von Bing, Yandex, Seznam
und anderen: statt auf den nächsten Besuch des Crawlers zu warten, meldet die
Seite eine geänderte Adresse selbst. Für diesen Shop zählt das bei jedem
Stück, weil es ein Einzelstück ist – ist es verkauft, setzt ``paypal_capture``
es auf inaktiv, und die Produktseite soll nicht tagelang weiter im Index
stehen. Google nimmt an IndexNow nicht teil; dort bleibt es bei der Sitemap.

Aus, solange ``INDEXNOW_KEY`` leer ist (Vorgabe) oder ``DEBUG`` an ist. Der
Schlüssel ist frei wählbar (8–128 Zeichen aus Buchstaben, Ziffern und
Bindestrich) und wird unter ``SCHLUESSEL_PFAD`` ausgeliefert; über diese
Datei prüft die Suchmaschine, dass die Meldung von der Seite selbst kommt.

Gemeldet wird ausserhalb der Anfrage in einem Pool mit einem Platz – ein
langsamer oder ausgefallener Endpunkt verzögert keine Seite und keinen
Kaufabschluss. Ein Fehlschlag landet nur im Protokoll: die Sitemap bleibt
der Rückweg.
"""

import logging
import re
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlsplit

import requests
from django.conf import settings

_log = logging.getLogger('shop1')

#: Gemeinsamer Endpunkt; er reicht die Meldung an alle Teilnehmer weiter.
ENDPUNKT = 'https://api.indexnow.org/indexnow'
#: Adresse der Schlüsseldatei (Route ``indexnow_schluessel`` in ``urls.py``).
SCHLUESSEL_PFAD = '/indexnow-schluessel.txt'
_GUELTIG = re.compile(r'^[A-Za-z0-9-]{8,128}$')
_POOL = ThreadPoolExecutor(max_workers=1, thread_name_prefix='indexnow')


def schluessel():
    """Der gesetzte Schlüssel – oder ``''``, wenn keiner oder ein ungültiger gesetzt ist."""
    wert = getattr(settings, 'INDEXNOW_KEY', '')
    return wert if _GUELTIG.match(wert) else ''


def nutzlast(pfade):
    """Die Meldung nach indexnow.org/documentation: Host, Schlüssel, Ort der
    Schlüsseldatei und die vollständigen Adressen, jede nur einmal."""
    basis = settings.SITE_URL.rstrip('/')
    return {
        'host': urlsplit(basis).hostname,
        'key': schluessel(),
        'keyLocation': basis + SCHLUESSEL_PFAD,
        'urlList': [basis + pfad for pfad in dict.fromkeys(pfade)],
    }


def _senden(daten):
    try:
        antwort = requests.post(ENDPUNKT, json=daten, timeout=10)
    except requests.RequestException as fehler:
        _log.warning('IndexNow nicht erreichbar: %s', fehler)
        return
    # 200 und 202 heissen angenommen; 403 = Schlüsseldatei passt nicht,
    # 422 = Adresse gehört nicht zum Host.
    if antwort.status_code >= 300:
        _log.warning('IndexNow lehnt die Meldung ab: %s %s',
                     antwort.status_code, antwort.text[:200])


def melden(pfade):
    """Meldet die Pfade (``/produkt/…/``) im Hintergrund; ``True``, wenn gemeldet wird."""
    if not pfade or not schluessel() or settings.DEBUG:
        return False
    _POOL.submit(_senden, nutzlast(pfade))
    return True
