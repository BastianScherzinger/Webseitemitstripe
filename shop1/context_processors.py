"""Kontextprozessoren: Werte, die jede Vorlage ohne eigene View-Angabe kennt.

Eingetragen in ``settings.TEMPLATES``; sie laufen bei jedem gerenderten
Template und bleiben deshalb bei einer Abfrage je Wert.
"""
import logging
import os
from django.conf import settings
from django.core.cache import cache

from .middleware import oeffentliche_basis
from .seiten_stand import seite_fuer

_log = logging.getLogger('shop1')


def csp_nonce(request):
    """Nonce der Content-Security-Policy für diese Anfrage (SI09).

    Gesetzt von ``ContentSecurityPolicyMiddleware``. Jedes Inline-``<script>``
    trägt ``nonce="{{ csp_nonce }}"`` – ohne passende Nonce blockiert der
    Browser es. Ohne die Middleware (Tests, die sie abschalten) bleibt der
    Wert leer; dann gibt es auch keine Richtlinie, die etwas blockiert.
    """
    return {'csp_nonce': getattr(request, 'csp_nonce', '')}


def oeffentliche_adresse(request):
    """Die öffentliche Adresse dieser Seite für canonical, hreflang und og:url.

    Mit gesetztem CANONICAL_HOST immer unter diesem Host (siehe
    middleware.oeffentliche_basis), sonst wie bisher unter dem Host der
    Anfrage. Nur der Pfad, **ohne Query** (seit 23.10.2026): keine öffentliche
    Seite zeigt je Query einen anderen Inhalt – die Query belegt höchstens ein
    Formular vor (``/motiv-anfragen/?richtung=tier``). Mit Query im canonical
    standen die sechs Vorbelegungen der Motivanfrage als eigene, fast gleiche
    Seiten im Index (Website-Check 22.10.2026: doppelte Titel, doppelter Text).
    """
    return {'seiten_url': oeffentliche_basis(request) + request.path}


def feed_beworben(request):
    """Ob base.html den Feed per ``rel=alternate`` bewirbt (EIG128).

    Nur mit mindestens einem freigegebenen Wissensbeitrag – derselben Menge,
    die der Feed selbst ausgibt. Ein leerer Feed bleibt unter ``/feed/``
    erreichbar, wird aber nicht in jedem Seitenkopf angekündigt. Reines
    Nachschlagen im Register, kein Datenbankzugriff.
    """
    from .views.wissen import uebersicht_indexierbar
    return {'feed_beworben': uebersicht_indexierbar()}


def shop_owner_check(request):
    """Inhaberkennung, Warenkorbzähler, aktive Werbung und Seitenstand.

    Werbe-Impressionen werden hier bewusst nicht gezählt, sondern nur in
    der View ``startseite``.
    """
    is_shop_owner = False
    if request.user.is_authenticated:
        admin_username = os.getenv('ADMIN_USERNAME', 'shopbesitzer')
        if request.user.username == admin_username or request.user.is_superuser:
            is_shop_owner = True

    # Warenkorb-Zähler im Kopf jeder Seite. Läuft bei jedem Abruf eines
    # angemeldeten Nutzers – deshalb eine einzige SUM-Abfrage über die Posten
    # statt Warenkorb laden und die Posten in Python aufsummieren (zwei
    # Abfragen plus Objektaufbau). Ohne Warenkorb oder ohne Posten ergibt
    # SUM NULL, daraus wird 0 – wie bisher.
    cart_count = 0
    if request.user.is_authenticated:
        try:
            from django.db.models import Sum
            from .models import CartItem
            cart_count = CartItem.objects.filter(
                cart__user=request.user
            ).aggregate(summe=Sum('menge'))['summe'] or 0
        except Exception:
            _log.exception('Warenkorb-Zählung im Context Processor fehlgeschlagen')

    # Aktive Werbung aus Cache
    werbung_aktiv = []
    _skip = ('/static/', '/shop-admin/', '/admin/', '/media/', '/favicon')
    if not any(request.path.startswith(s) for s in _skip):
        try:
            cache_key = 'werbung_aktiv_list'
            werbung_aktiv = cache.get(cache_key)
            if werbung_aktiv is None:
                from .models import Werbung
                werbung_aktiv = [w for w in Werbung.objects.filter(aktiv=True) if w.ist_aktiv]
                cache.set(cache_key, werbung_aktiv, 60)
        except Exception:
            _log.exception('Aktive Werbung konnte nicht geladen werden')

    # Stand der aktuellen Seite für den WebPage-Knoten in base.html: reines
    # Nachschlagen im Register, kein Datenbankzugriff. resolver_match fehlt
    # bei Fehlerseiten, url_name bei namenlosen Routen – beides ergibt None,
    # und base.html lässt name/dateModified dann weg.
    treffer = getattr(request, 'resolver_match', None)
    seite = seite_fuer(treffer.url_name if treffer else None)

    return {
        'is_shop_owner': is_shop_owner,
        'cart_count': cart_count,
        'werbung_aktiv': werbung_aktiv,
        'GOOGLE_REVIEW_URL': getattr(settings, 'GOOGLE_REVIEW_URL', ''),
        'seite': seite,
    }


def anbieterin(request):
    """Anbieterin und Herkunft für Impressum, Kontakt, Schema (``luviq_daten``).

    Reine Konstanten, keine Abfrage – deshalb auf jeder Seite, auch im Panel."""
    from . import luviq_daten
    return {'anbieterin': luviq_daten.ANBIETERIN, 'herkunft': luviq_daten.HERKUNFT,
            # USt-IdNr. erst, wenn sie da ist (settings.UST_IDNR, Impressum).
            'ust_idnr': getattr(settings, 'UST_IDNR', ''),
            'lucid_nr': getattr(settings, 'LUCID_REGISTRIERNUMMER', ''),
            'rechtstexte': rechtstexte_vorhanden(),
            # Absolute Adresse für Rechtstexte („online unter https://…/vertrag-widerrufen/“);
            # in Mails setzt mails.vertragsunterlagen() die Live-Adresse ein.
            'rechts_basis': oeffentliche_basis(request),
            # „Vertrag widerrufen“ (§ 356a BGB) muss während jeder laufenden Widerrufsfrist
            # sichtbar sein – auch wenn der Verkauf später wieder aus ist.
            'widerruf_knopf': widerruf_knopf_zeigen(),
            # Rechtstexte nennen nur Zahlungsarten, die der Bestellweg wirklich anbietet
            # (Überweisung nur mit hinterlegter IBAN, views/checkout._bank_konfiguriert).
            'ueberweisung_moeglich': bool(os.getenv('BANK_IBAN', '').strip()),
            'pflege': luviq_daten.PFLEGE,
            # Einwilligungs-Banner nur, wenn ein nicht notwendiger Dienst eingestellt ist.
            'einwilligung': ({'dienst': settings.EINWILLIGUNG_DIENST,
                              'skript': getattr(settings, 'EINWILLIGUNG_SKRIPT', ''),
                              'ga': getattr(settings, 'GA_MESSUNG_ID', '')}
                             if getattr(settings, 'EINWILLIGUNG_DIENST', '') else None)}


def rechtstexte_vorhanden():
    """Welche Generator-Ablagen (legal/generator/*.html) schon Text tragen.

    Ändert sich nur mit einem neuen Stand, deshalb einmal je Prozess gelesen."""
    global _RECHTSTEXTE
    if _RECHTSTEXTE is None:
        from .startsperre import generator_text_fehlt
        _RECHTSTEXTE = {name: not generator_text_fehlt(name)
                        for name in ('impressum', 'datenschutz', 'agb', 'widerruf')}
    return _RECHTSTEXTE


_RECHTSTEXTE = None

#: So lange nach der letzten Bestellung bleibt „Vertrag widerrufen“ im Fuß, auch ohne
#: laufenden Verkauf: 14 Tage Frist ab Erhalt plus großzügig Versand, Zustellung und
#: Überweisungsdauer. Bei fehlender Belehrung liefe die Frist bis 12 Monate + 14 Tage
#: (§ 356 Abs. 3 BGB); die Belehrung ist vorhanden, deshalb genügt dieser Puffer.
WIDERRUF_NACHLAUF_TAGE = 90


def widerruf_knopf_zeigen():
    """True bei laufendem Verkauf oder wenn die letzte Bestellung weniger als
    ``WIDERRUF_NACHLAUF_TAGE`` alt ist (eine Abfrage, 10 Minuten zwischengespeichert)."""
    from .verkauf import verkauf_aktiv
    if verkauf_aktiv():
        return True
    wert = cache.get('widerruf_knopf')
    if wert is None:
        from datetime import timedelta
        from django.utils import timezone
        from .models import Order
        try:
            grenze = timezone.now() - timedelta(days=WIDERRUF_NACHLAUF_TAGE)
            wert = Order.objects.filter(erstellt_am__gte=grenze).exists()
        except Exception:
            _log.exception('widerruf_knopf: Abfrage gescheitert')
            wert = True
        cache.set('widerruf_knopf', wert, 600)
    return wert


def luviq(request):
    """Laufband, Drop-Kasten und Schalter des Looks „Nachtausgabe".

    Werte aus ``shop1/luviq_daten.py``, nie aus einer Vorlage. Eine
    Datenbankabfrage (nächste freie Archivnummer), nur für öffentliche Seiten."""
    if request.path.startswith(('/shop-admin/', '/admin/', '/static/', '/media/')):
        from . import luviq_daten
        return {'motivanfrage_aktiv': settings.MOTIVANFRAGE_AKTIV, 'profile_urls': luviq_daten.PROFILE,
                'profile_person_urls': luviq_daten.PROFILE_PERSON, **_rahmen()}
    from . import luviq_daten
    try:
        drop = luviq_daten.drop_kontext()
    except Exception:
        _log.exception('Drop-Angaben konnten nicht gelesen werden')
        drop = None
    return {
        'drop': drop,
        'motivanfrage_aktiv': settings.MOTIVANFRAGE_AKTIV,
        'instagram_url': luviq_daten.INSTAGRAM,
        'instagram_name': luviq_daten.INSTAGRAM_NAME,
        # sameAs des Schemas: nur belegte Profile, eine Quelle (luviq_daten.PROFILE).
        'profile_urls': luviq_daten.PROFILE,
        'profile_person_urls': luviq_daten.PROFILE_PERSON,
        # Luisas Erfahrungswert „2 bis 5 Tage“ (nie als Zusage): jede Seite, die ihn
        # nennt, liest ihn von hier, nicht aus eigener Abschrift.
        'dauer': luviq_daten.DAUER,
        # Antwortzeit auf Nachrichten (bestätigt 02.10.2026), eine Quelle.
        'antwort': luviq_daten.ANTWORT,
        # Versand, Übergabe, Herkunftssatz (P1): eine Quelle; leerer ABHOLUNG-Text = keine Erwähnung.
        'versand': luviq_daten.VERSAND,
        'abholung': luviq_daten.ABHOLUNG,
        'herkunft_satz': luviq_daten.HERKUNFT_SATZ,
        # Runde 3 (30.10.2026): Versand im Preis, kein Umtausch, Auftragsarbeit ohne Widerruf.
        'versand_preissatz': luviq_daten.VERSAND_PREISSATZ,
        'umtausch_satz': luviq_daten.UMTAUSCH_SATZ,
        'auftrag_widerruf_satz': luviq_daten.AUFTRAG_WIDERRUF_SATZ,
        'luisa_foto': luisa_foto(),
        'versand_werktage_min': _werktage()[0],
        'versand_werktage_max': _werktage()[1],
        **_rahmen(),
    }


def _werktage():
    """``VERSAND['werktage']`` (z. B. „1-2“) als Zahlenpaar für das Schema; „3“ wird (3, 3)."""
    from . import luviq_daten
    teile = [t for t in str(luviq_daten.VERSAND.get('werktage', '')).replace('–', '-').split('-') if t.strip()]
    try:
        zahlen = [int(t) for t in teile]
    except ValueError:
        zahlen = []
    if not zahlen:
        return 1, 2
    return min(zahlen), max(zahlen)


def luisa_foto():
    """Luisas Brustbild als ``produktbilder.Bild`` (``None`` ohne Foto oder ohne Datei).

    Eine Quelle (``luviq_daten.LUISA_FOTO``) für Kontakt, Luisa-Seite und das ``image`` des
    Person-Knotens in ``base.html``."""
    from . import luviq_daten, produktbilder
    foto = luviq_daten.LUISA_FOTO
    if not foto:
        return None
    breite, hoehe = foto['masse']
    spec = f"{foto['muster']}@{','.join(str(b) for b in foto['breiten'])}#{breite}x{hoehe}"
    return produktbilder.bild_aus(None, spec, breite, hoehe, foto['alt'])


def _rahmen():
    """Ankündigungszeile, Navigation, Fußgruppen und Handy-Leiste (Paket P2).

    Reine Konstanten und der Verkaufsschalter, keine Abfrage. Die Ankündigung
    nennt den abgestimmten Öffnungssatz wörtlich (``verkauf.oeffnungs_satz``)."""
    from . import luviq_daten, verkauf
    aktiv = verkauf.verkauf_aktiv()
    motiv = settings.MOTIVANFRAGE_AKTIV
    satz, knopf, route, anker = luviq_daten.leiste(aktiv, getattr(settings, 'VERKAUF_FRUEHESTENS', None))
    return {
        'hinweis': luviq_daten.hinweis(aktiv, verkauf.oeffnungs_satz()),
        'navigation': luviq_daten.navigation(aktiv, motiv),
        'fuss_gruppen': luviq_daten.fuss(aktiv, motiv),
        'leiste': {'satz': satz, 'knopf': knopf, 'route': route, 'anker': anker},
        'leiste_aus': sorted(luviq_daten.LEISTE_AUS),
    }
