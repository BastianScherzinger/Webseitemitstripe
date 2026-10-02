"""Sichtbarkeit in KI-Antworten.

Der Grundsatz dieses Bereichs: **ein Schema, das etwas anderes behauptet als
die Seite, ist schlimmer als keines.** Die Tests vergleichen deshalb nicht nur,
ob JSON-LD vorhanden und gültig ist, sondern ob seine Aussagen im sichtbaren
Text derselben Seite wiederzufinden sind.
"""

import json
import re
from datetime import date
from html.parser import HTMLParser
from urllib.parse import urlsplit
from xml.etree import ElementTree

from django.test import override_settings
from django.utils import timezone

from ._basis import INDEXIERBARE_SEITEN, INHALTSSEITEN, LuviqTestCase, erzeuge_produkt, ohne_kaufweg

_JSONLD = re.compile(
    r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>', re.DOTALL
)

#: Die Seiten, die ein FAQPage-Schema tragen (``kontakt.html``,
#: ``liefergebiet.html`` und die drei Wissensbeiträge, deren
#: Zwischenüberschriften Fragen sind). Die Startseite steht bewusst nicht
#: darin: ihr Schema wurde entfernt, weil die Fragen dort nirgends sichtbar
#: waren (siehe Kommentar in ``index.html``); die Wissensübersicht hat kein
#: FAQ. Kommt eine Seite dazu, gehört sie hier hinein – dann prüft der Test
#: auch dort, dass jede Frage sichtbar auf der Seite steht.
FAQ_SEITEN = (
    '/kontakt/', '/liefergebiet/',
    '/wissen/pflege-handbemalte-kleidung/',
    '/wissen/upcycling-mode-second-hand-vintage/',
    '/wissen/groesse-bei-einzelstuecken/',
    '/wissen/bestellen-und-bezahlen/',
    '/wissen/widerruf-und-ruecksendung/',
    '/wissen/konto-und-daten/',
)
# Ohne Verkauf leiten die Kaufweg-Beiträge um (siehe _basis.KAUFWEG_WISSENSSEITEN).
FAQ_SEITEN = tuple(ohne_kaufweg(FAQ_SEITEN))


class _Textleser(HTMLParser):
    """Zieht den sichtbaren Text aus einem Dokument."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self._stumm = 0
        self.stuecke = []

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self._stumm += 1

    def handle_endtag(self, tag):
        if tag in ('script', 'style') and self._stumm:
            self._stumm -= 1

    def handle_data(self, daten):
        if not self._stumm:
            self.stuecke.append(daten)


def sichtbarer_text(html):
    leser = _Textleser()
    leser.feed(html)
    return ' '.join(' '.join(leser.stuecke).split())


class _Ueberschriftenleser(HTMLParser):
    """Sammelt den Text jeder Überschrift ``<h1>`` bis ``<h6>``."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self._offen = None
        self.ueberschriften = []

    def handle_starttag(self, tag, attrs):
        if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            self._offen = [tag, '']

    def handle_endtag(self, tag):
        if self._offen and tag == self._offen[0]:
            self.ueberschriften.append(' '.join(self._offen[1].split()))
            self._offen = None

    def handle_data(self, daten):
        if self._offen:
            self._offen[1] += daten


def ueberschriften(html):
    """Alle sichtbaren Überschriftentexte einer Seite, Leerraum normalisiert."""
    leser = _Ueberschriftenleser()
    leser.feed(html)
    return leser.ueberschriften


def kennung(knoten):
    """``@id`` eines Knotens ohne Schema und Host – ``#luisa`` statt ``https://testserver/#luisa``."""
    return knoten['@id'].split('://', 1)[-1].split('/', 1)[-1]


def schema_knoten(html):
    """Alle JSON-LD-Knoten einer Seite, @graph aufgelöst."""
    knoten = []
    for block in _JSONLD.findall(html):
        daten = json.loads(block)
        knoten.extend(daten['@graph'] if isinstance(daten, dict) and '@graph' in daten
                      else daten if isinstance(daten, list) else [daten])
    return knoten


class StrukturierteDatenTest(LuviqTestCase):
    """JSON-LD – gültig, widerspruchsfrei, deckungsgleich mit der Seite."""

    def setUp(self):
        self.produkt = erzeuge_produkt('Bemalte Bomberjacke')

    def test_jedes_json_ld_ist_gueltiges_json(self):
        """Verhindert, dass ein Anführungszeichen aus einem Produktnamen oder
        einem Kommentar den ganzen Block zerschiesst. Ein ungültiger Block wird
        von Suchmaschinen und Antwortmaschinen vollständig verworfen."""
        for pfad in INHALTSSEITEN + [self.produkt.get_absolute_url()]:
            with self.subTest(pfad=pfad):
                inhalt = self.hole(pfad).content.decode()
                bloecke = _JSONLD.findall(inhalt)
                self.assertTrue(bloecke, f'{pfad} hat kein JSON-LD')
                for nummer, block in enumerate(bloecke):
                    try:
                        json.loads(block)
                    except json.JSONDecodeError as fehler:
                        self.fail(f'{pfad}, Block {nummer}: {fehler}')

    def test_es_gibt_nur_eine_organisationskennung(self):
        """Verhindert konkurrierende Unternehmensangaben. Vor diesem Lauf gab
        es drei: ``#organization`` seitenweit, ``#organisation`` auf
        /ueber_uns/ und einen Knoten ganz ohne Kennung im Impressum. Für
        Suchmaschinen sind das drei verschiedene Firmen."""
        kennungen = set()
        for pfad in INHALTSSEITEN:
            inhalt = self.hole(pfad).content.decode()
            for knoten in schema_knoten(inhalt):
                typen = knoten.get('@type', '')
                typen = typen if isinstance(typen, list) else [typen]
                if {'Organization', 'LocalBusiness', 'ClothingStore'} & set(typen):
                    self.assertIn(
                        '@id', knoten,
                        f'{pfad}: Unternehmensknoten ohne @id',
                    )
                    kennungen.add(knoten['@id'].split('://', 1)[-1].split('/', 1)[-1])
        self.assertEqual(
            kennungen, {'#organization'},
            f'Mehrere Unternehmenskennungen im Umlauf: {sorted(kennungen)}',
        )

    def test_das_schema_behauptet_keine_oeffnungszeiten(self):
        """Verhindert die Rückkehr eines widerlegten Versprechens: das Schema
        gab Mo–So 00:00–23:59 an, während /liefergebiet/ sichtbar sagt, es gebe
        'keinen Laden zum Reinschauen'. Öffnungszeiten gehören erst wieder
        hinein, wenn es einen Ladenbetrieb gibt."""
        for pfad in INHALTSSEITEN:
            with self.subTest(pfad=pfad):
                for knoten in schema_knoten(self.hole(pfad).content.decode()):
                    self.assertNotIn('openingHoursSpecification', knoten)

    def test_das_schema_verspricht_keine_suche_die_es_nicht_gibt(self):
        """Verhindert die Rückkehr der ``SearchAction`` auf ``/produkte/?q=``.
        Die Produktansicht wertet keinen Suchparameter aus – ein Schema, das
        eine Suche ankündigt, führt Antwortmaschinen ins Leere."""
        for knoten in schema_knoten(self.hole('/').content.decode()):
            self.assertNotIn('potentialAction', knoten)

    def test_die_brotkrume_nennt_die_sichtbaren_beschriftungen(self):
        """Verhindert den Fall, den dieser Lauf vorgefunden hat: die Seite
        zeigte 'Orbit' und 'Objekte', das Schema meldete 'Home' und
        'Produkte'.

        Der Test schlägt auch an, wenn die Produktseite gar keine Brotkrume
        mehr ausliefert oder eine leere – sonst wäre er ohne einen einzigen
        Vergleich grün."""
        inhalt = self.hole(self.produkt.get_absolute_url()).content.decode()
        text = sichtbarer_text(inhalt)
        brotkrumen = [k for k in schema_knoten(inhalt) if k.get('@type') == 'BreadcrumbList']
        self.assertEqual(
            len(brotkrumen), 1,
            f'Die Produktseite hat {len(brotkrumen)} BreadcrumbList-Knoten statt einem',
        )
        eintraege = brotkrumen[0].get('itemListElement', [])
        self.assertGreaterEqual(len(eintraege), 2, 'Brotkrume ohne Stationen')
        for eintrag in eintraege:
            with self.subTest(name=eintrag.get('name')):
                self.assertTrue(eintrag.get('name'), 'Station ohne Namen')
                self.assertIn(
                    eintrag['name'], text,
                    f'Die Brotkrume nennt "{eintrag["name"]}", '
                    f'auf der Seite steht das nicht',
                )

    def test_jede_frage_im_schema_steht_auch_auf_der_seite(self):
        """Verhindert erfundene Fragen und Antworten im FAQ-Schema. Google
        entfernt solche Seiten aus den Ergebnissen, Antwortmaschinen zitieren
        etwas, das niemand nachlesen kann.

        Zusätzlich muss das FAQ-Schema genau auf den Seiten liegen, die es
        tragen sollen (``FAQ_SEITEN``): fällt es dort weg, wäre der Test sonst
        ohne einen einzigen Vergleich grün; taucht es auf einer neuen Seite
        auf, gehört die Seite bewusst in die Liste aufgenommen – samt Abgleich
        mit ihrem sichtbaren Text."""
        gefunden = set()
        for pfad in INHALTSSEITEN:
            inhalt = self.hole(pfad).content.decode()
            text = sichtbarer_text(inhalt)
            for knoten in schema_knoten(inhalt):
                if knoten.get('@type') != 'FAQPage':
                    continue
                gefunden.add(pfad)
                fragen = knoten.get('mainEntity', [])
                self.assertTrue(fragen, f'{pfad}: FAQPage ohne eine einzige Frage')
                for frage in fragen:
                    with self.subTest(pfad=pfad, frage=frage['name'][:40]):
                        self.assertIn(frage['name'], text)
                        antwort = ' '.join(frage['acceptedAnswer']['text'].split())
                        self.assertIn(antwort, text)
        self.assertEqual(
            gefunden, set(FAQ_SEITEN),
            f'FAQ-Schema gefunden auf {sorted(gefunden)}, erwartet auf {sorted(FAQ_SEITEN)}',
        )

    def test_die_produktseite_nennt_ihr_aenderungsdatum(self):
        """Verhindert, dass Antwortmaschinen und Suchmaschinen die Aktualität
        eines Angebots nicht einschätzen können. Die Angabe stammt aus
        ``Produkt.aktualisiert_am`` – sie wird nicht erfunden.

        Der Vergleich rechnet den Zeitstempel in die Zeitzone der Seite um
        (``TIME_ZONE``, Europe/Berlin), weil das Template ihn so rendert.
        ``aktualisiert_am`` selbst ist UTC; ohne die Umrechnung war der Test
        täglich zwischen 22:00 und 24:00 UTC rot, weil in Berlin schon der
        nächste Tag angebrochen war."""
        inhalt = self.hole(self.produkt.get_absolute_url()).content.decode()
        produktknoten = [k for k in schema_knoten(inhalt) if k.get('@type') == 'Product']
        self.assertEqual(len(produktknoten), 1)
        self.assertEqual(
            produktknoten[0]['dateModified'][:10],
            timezone.localtime(self.produkt.aktualisiert_am).date().isoformat(),
        )

    def test_jede_seite_traegt_einen_webpage_knoten_mit_aenderungsdatum(self):
        """Verhindert drei Fehler auf einmal: (a) eine Inhaltsseite ohne
        ``WebPage``-Knoten – Antwortmaschinen können ihre Aktualität dann
        nicht einschätzen (Befund GE18); (b) ein ``dateModified``, das kein
        Datum ist oder in der Zukunft liegt – ein Tippfehler im Register
        ``shop1/seiten_stand.py``; (c) ein Schema-Datum, das vom ``lastmod``
        derselben Adresse in der Sitemap abweicht – beide kommen aus einem
        Register, und genau das sichert dieser Vergleich.

        Der ``name`` des Knotens muss auf der Seite sichtbar sein (er ist die
        Menübeschriftung), sonst behauptet das Schema einen Titel, den
        niemand liest."""
        sitemap = ElementTree.fromstring(self.hole('/sitemap.xml').content)
        ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        lastmod_je_pfad = {
            urlsplit(e.find('sm:loc', ns).text).path or '/': e.find('sm:lastmod', ns).text
            for e in sitemap.findall('sm:url', ns)
        }
        for pfad in INHALTSSEITEN:
            with self.subTest(pfad=pfad):
                inhalt = self.hole(pfad).content.decode()
                seiten = [k for k in schema_knoten(inhalt) if k.get('@type') == 'WebPage']
                self.assertEqual(len(seiten), 1, f'{pfad}: {len(seiten)} WebPage-Knoten statt einem')
                seite = seiten[0]
                self.assertEqual(urlsplit(seite['url']).path, pfad)
                self.assertEqual(kennung(seite['isPartOf']), '#website')
                self.assertTrue(seite.get('name'), f'{pfad}: WebPage ohne name')
                self.assertIn(seite['name'], sichtbarer_text(inhalt), f'{pfad}: name "{seite["name"]}" steht nicht auf der Seite')
                stand = seite.get('dateModified', '')
                self.assertRegex(stand, r'^\d{4}-\d{2}-\d{2}$', f'{pfad}: dateModified "{stand}"')
                self.assertLessEqual(date.fromisoformat(stand), date.today())
                if pfad in lastmod_je_pfad:
                    self.assertEqual(
                        stand, lastmod_je_pfad[pfad],
                        f'{pfad}: Schema sagt {stand}, Sitemap sagt {lastmod_je_pfad[pfad]}',
                    )

    def test_speakable_zeigt_auf_titel_und_beschreibung_die_es_gibt(self):
        """Verhindert ein ``speakable``, das ins Leere zeigt (PJ13): die beiden
        XPath-Ziele müssen auf jeder Inhaltsseite genau einmal und nicht leer
        vorhanden sein – sonst hat ein Sprachassistent nichts vorzulesen."""
        for pfad in INHALTSSEITEN:
            with self.subTest(pfad=pfad):
                inhalt = self.hole(pfad).content.decode()
                seite = [k for k in schema_knoten(inhalt) if k.get('@type') == 'WebPage'][0]
                sprechbar = seite.get('speakable', {})
                self.assertEqual(sprechbar.get('@type'), 'SpeakableSpecification')
                self.assertEqual(sprechbar.get('xpath'), [
                    '/html/head/title', "/html/head/meta[@name='description']/@content",
                ])
                self.assertEqual(len(re.findall(r'<title>\s*\S', inhalt)), 1, pfad)
                self.assertEqual(len(re.findall(r'<meta name="description" content="[^"]+"', inhalt)), 1, pfad)

    def test_die_person_hinter_der_seite_steht_genau_einmal_im_graphen(self):
        """Verhindert zwei Personen, wo es eine gibt: vor diesem Lauf war die
        Gründerin als namenloser Knoten in ``founder`` eingebettet und auf
        /ueber_uns/ ein zweites Mal mit Kennung angelegt; ``author`` fehlte
        ganz (Befund GE16). Jetzt gibt es genau eine Kennung, und ``founder``
        wie ``author`` sind Verweise darauf – ein eingebetteter Knoten an einer
        dieser Stellen wäre die Rückkehr des Fehlers."""
        for pfad in INHALTSSEITEN:
            with self.subTest(pfad=pfad):
                knoten = schema_knoten(self.hole(pfad).content.decode())
                personen = [k for k in knoten if k.get('@type') == 'Person']
                self.assertTrue(personen, f'{pfad}: kein Person-Knoten')
                for person in personen:
                    self.assertIn('@id', person, f'{pfad}: Person ohne @id')
                kennungen = {kennung(p) for p in personen}
                self.assertEqual(len(kennungen), 1, f'{pfad}: mehrere Personen {sorted(kennungen)}')
                person_id = kennungen.pop()

                verweise = {'founder': 0, 'author': 0}
                for k in knoten:
                    for rolle in verweise:
                        if rolle not in k:
                            continue
                        wert = k[rolle]
                        self.assertEqual(
                            set(wert), {'@id'},
                            f'{pfad}: {rolle} bettet einen Knoten ein statt zu verweisen',
                        )
                        self.assertEqual(kennung(wert), person_id)
                        verweise[rolle] += 1
                self.assertGreaterEqual(verweise['founder'], 1, f'{pfad}: kein founder-Verweis')
                self.assertGreaterEqual(verweise['author'], 1, f'{pfad}: kein author-Verweis')

    def test_jede_unterseite_traegt_eine_brotkrume_mit_erreichbaren_stationen(self):
        """Verhindert den Zustand vor Schritt 18 – sieben von neun Seiten ohne
        ``BreadcrumbList`` (Befund GE12) – und zwei Folgefehler: eine Station,
        deren Adresse ins 404 führt, und einen Namen, der nirgends auf der
        Seite sichtbar ist. Die Startseite darf keine Brotkrume tragen: ein
        Pfad mit einer Station ist keiner."""
        unterseiten = [p for p in INHALTSSEITEN if p != '/'] + [self.produkt.get_absolute_url()]
        for pfad in unterseiten:
            with self.subTest(pfad=pfad):
                inhalt = self.hole(pfad).content.decode()
                text = sichtbarer_text(inhalt)
                listen = [k for k in schema_knoten(inhalt) if k.get('@type') == 'BreadcrumbList']
                self.assertEqual(len(listen), 1, f'{pfad}: {len(listen)} BreadcrumbList-Knoten')
                stationen = listen[0].get('itemListElement', [])
                self.assertGreaterEqual(len(stationen), 2, f'{pfad}: Brotkrume mit weniger als zwei Stationen')
                self.assertEqual([s['position'] for s in stationen], list(range(1, len(stationen) + 1)))
                for station in stationen:
                    self.assertIn(station['name'], text, f'{pfad}: "{station["name"]}" steht nicht auf der Seite')
                    ziel = urlsplit(station['item']).path
                    self.assertEqual(self.hole(ziel).status_code, 200, f'{pfad}: Station {ziel} antwortet nicht')
                self.assertEqual(urlsplit(stationen[-1]['item']).path, pfad, 'Letzte Station ist nicht die Seite selbst')
        startseite = [k for k in schema_knoten(self.hole('/').content.decode()) if k.get('@type') == 'BreadcrumbList']
        self.assertEqual(startseite, [], 'Die Startseite trägt eine Brotkrume')

    def test_jede_faq_frage_ist_eine_sichtbare_ueberschrift(self):
        """Verhindert, dass eine Frage im FAQ-Schema nur irgendwo im Fliesstext
        vorkommt oder leicht anders lautet als auf der Seite. Google verlangt
        für ``FAQPage``, dass Frage und Antwort sichtbar sind; die Frage muss
        deshalb **wortgleich** als Überschrift stehen – nicht als Teil eines
        Satzes. Der schwächere Test oben (``assertIn`` im Gesamttext) würde
        eine Frage durchwinken, die in einem Absatz zitiert wird."""
        for pfad in FAQ_SEITEN:
            inhalt = self.hole(pfad).content.decode()
            titel = ueberschriften(inhalt)
            fragen = [
                frage['name']
                for knoten in schema_knoten(inhalt) if knoten.get('@type') == 'FAQPage'
                for frage in knoten.get('mainEntity', [])
            ]
            self.assertTrue(fragen, f'{pfad}: FAQPage ohne Fragen')
            for frage in fragen:
                with self.subTest(pfad=pfad, frage=frage[:40]):
                    self.assertIn(
                        ' '.join(frage.split()), titel,
                        f'{pfad}: "{frage}" steht nicht wortgleich als Überschrift auf der Seite',
                    )


class AntwortCrawlerTest(LuviqTestCase):
    """robots.txt und llms.txt – die zwei Dateien, die Antwortmaschinen lesen."""

    def test_jeder_antwort_crawler_darf_die_inhaltsseiten_lesen(self):
        """Verhindert, dass die Seite in KI-Antworten nicht mehr auftauchen
        kann, weil ein Crawler pauschal ausgesperrt wurde."""
        from ..views.legal import ANTWORT_CRAWLER

        robots = self.hole('/robots.txt').content.decode()
        for bot in ANTWORT_CRAWLER:
            with self.subTest(bot=bot):
                self.assertIn(f'User-agent: {bot}', robots)
        for zeile in robots.splitlines():
            self.assertNotEqual(zeile.strip(), 'Disallow: /')

    def test_auch_antwort_crawler_bleiben_aus_den_privaten_bereichen(self):
        """Gegenprobe: eine ausdrückliche Erlaubnis darf nicht dazu führen,
        dass Warenkorb, Bezahlvorgang und Admin-Panel plötzlich offenstehen."""
        robots = self.hole('/robots.txt').content.decode()
        for block in robots.split('\n\n'):
            if not block.startswith('User-agent:'):
                continue
            with self.subTest(block=block.splitlines()[0]):
                for pfad in ('/shop-admin/', '/checkout/', '/profil/', '/reset/'):
                    self.assertIn(f'Disallow: {pfad}', block)

    def test_robots_verweist_auf_die_kurzfassung(self):
        """Verhindert, dass llms.txt zwar existiert, aber von niemandem
        gefunden wird."""
        self.assertIn('/llms.txt', self.hole('/robots.txt').content.decode())

    def test_die_kurzfassung_wird_als_text_ausgeliefert(self):
        """Verhindert, dass llms.txt als HTML oder als Download ankommt."""
        antwort = self.hole('/llms.txt')
        self.assertEqual(antwort.status_code, 200)
        self.assertTrue(antwort['Content-Type'].startswith('text/plain'))

    def test_die_kurzfassung_beginnt_mit_einer_zitierfaehigen_antwort(self):
        """Verhindert eine llms.txt ohne den einen Absatz, aus dem eine
        Antwortmaschine zitieren kann: wer ist das, was gibt es dort, wo."""
        text = self.hole('/llms.txt').content.decode()
        self.assertTrue(text.startswith('# Luviq Universe'))
        einleitung = ' '.join(
            z.lstrip('> ') for z in text.splitlines() if z.startswith('>')
        )
        self.assertGreater(len(einleitung), 150)
        for begriff in ('Alsfeld', 'Luisa Brehler', 'Einzelstueck'):
            with self.subTest(begriff=begriff):
                self.assertIn(begriff, einleitung)

    def test_die_kurzfassung_verweist_auf_alle_hauptseiten(self):
        """Verhindert, dass eine neue Seite gebaut wird, die Antwortmaschinen
        über die Kurzfassung nie erreichen. Seiten mit ``noindex`` (Impressum,
        nicht freigegebene Wissensbeiträge) gehören nicht hinein – das prüft
        ``test_seo.WissensfreigabeTest`` in beide Richtungen."""
        text = self.hole('/llms.txt').content.decode()
        self.assertIn('/impressum/', text)  # steht unter "Rechtliches"
        for pfad in INDEXIERBARE_SEITEN:
            with self.subTest(pfad=pfad):
                self.assertIn(pfad, text)

    def test_die_kurzfassung_fuehrt_nur_verfuegbare_einzelstuecke(self):
        """Verhindert, dass eine Antwortmaschine ein Stück empfiehlt, das nicht
        mehr zu haben ist – bei Einzelstücken ist das der Regelfall."""
        verfuegbar = erzeuge_produkt('Bemalte Bomberjacke')
        vergriffen = erzeuge_produkt('Bereits verkauftes Teil', aktiv=False)
        text = self.hole('/llms.txt').content.decode()
        self.assertIn(verfuegbar.get_absolute_url(), text)
        self.assertNotIn(vergriffen.get_absolute_url(), text)

    def test_jede_adresse_in_der_kurzfassung_antwortet(self):
        """Verhindert tote Verweise in der Datei, die Antwortmaschinen als
        Wegweiser benutzen."""
        erzeuge_produkt('Bemalte Bomberjacke')
        text = self.hole('/llms.txt').content.decode()
        pfade = {p for p in re.findall(r'\]\(https?://testserver([^)]*)\)', text)}
        self.assertGreaterEqual(len(pfade), 8)
        for pfad in pfade:
            with self.subTest(pfad=pfad):
                self.assertEqual(self.hole(pfad).status_code, 200)

    @override_settings(VERKAUF_AKTIV=True)  # prüft den Shop hinter dem Verkaufsschalter
    def test_die_kurzfassung_behauptet_nichts_anderes_als_die_agb(self):
        """Verhindert genau den Fehler, den dieser Bereich verhindern soll: die
        Kurzfassung nennt Zahlungsarten, die auf der Seite nicht gelten."""
        text = self.hole('/llms.txt').content.decode()
        agb = sichtbarer_text(self.hole('/agb/').content.decode())
        self.assertIn('PayPal oder Vorab-Ueberweisung', text)
        self.assertIn('PayPal oder Vorab-Überweisung', agb)


class SchemaBildAdressenTest(LuviqTestCase):
    """EIG07: das Schema baut keine Bildadresse von Hand am Static-Manifest vorbei.

    ``ManifestStaticFilesStorage`` hängt einen Inhalts-Hash an jede Datei
    (``logo-luviq.<hash>.jpeg``). Eine von Hand getippte ``/static/…``-Adresse
    zeigte nach dem nächsten Deploy ins Leere oder auf eine alte Fassung."""

    def test_das_logo_im_schema_traegt_den_manifest_hash(self):
        knoten = schema_knoten(self.hole('/').content.decode())
        betrieb = next(k for k in knoten if k.get('@id', '').endswith('/#organization')
                       and 'logo' in k)
        for adresse in (betrieb['logo']['url'], betrieb['image']):
            with self.subTest(adresse=adresse):
                self.assertRegex(urlsplit(adresse).path,
                                 r'^/static/shop1/images/logo-luviq\.[0-9a-f]{12}\.jpeg$')

    def test_keine_vorlage_tippt_eine_static_adresse_ins_schema(self):
        from pathlib import Path
        from django.conf import settings

        vorlagen = list(Path(settings.BASE_DIR, 'shop1', 'templates').rglob('*.html'))
        vorlagen.append(Path(settings.BASE_DIR, 'templates', 'base.html'))
        for vorlage in vorlagen:
            quelle = vorlage.read_text(encoding='utf-8')
            for block in _JSONLD.findall(quelle):
                with self.subTest(vorlage=vorlage.name):
                    self.assertNotIn('"/static/', block)
                    self.assertNotIn('/static/shop1/', block.replace("{% static 'shop1/", ''))


class UnaufgeloestePlatzhalterTest(LuviqTestCase):
    """EIG01: in llms.txt und llms-full.txt steht keine ungefüllte Vorlagenvariable
    und kein Python-``None`` – in beiden Zuständen des Verkaufsschalters."""

    def _pruefe(self):
        erzeuge_produkt('Bemalter Hoodie')
        for pfad in ('/llms.txt', '/llms-full.txt'):
            text = self.hole(pfad).content.decode()
            with self.subTest(pfad=pfad):
                self.assertNotRegex(text, r'\{\{|\{%|%\(|None|True|False')

    def test_ohne_verkauf(self):
        self._pruefe()

    @override_settings(VERKAUF_AKTIV=True)  # prüft den Shop hinter dem Verkaufsschalter
    def test_mit_verkauf(self):
        self._pruefe()


class BelegteKleidungsartenTest(LuviqTestCase):
    """EIG79: Schema und llms.txt nennen nur Kleidungsarten, die es im Bestand gibt
    (Hoodies, Hose, Jacke) – keine Shirts."""

    @override_settings(VERKAUF_AKTIV=True)  # Katalog und Fließtext stehen nur mit Verkauf
    def test_weder_schema_noch_llms_txt_versprechen_shirts(self):
        erzeuge_produkt('Bemalter Hoodie')
        self.assertNotIn('Shirts', self.hole('/llms.txt').content.decode())
        self.assertNotIn('Shirts', self.hole('/llms-full.txt').content.decode().split('## Volltext', 1)[0])
        self.assertNotIn('Vintage-Shirts', self.hole('/').content.decode())
        self.assertIn('Vintage-Hoodies', self.hole('/').content.decode())


class ArchivSchemaTest(LuviqTestCase):
    """Die Stücke stehen auf ``/produkte/`` als Knoten der obersten Ebene (GE13).

    Ein Product-Knoten, der nur verschachtelt in ``hasPart`` steckt, sieht für
    jeden, der die Knoten des Graphen liest, aus wie gar keiner. Ohne Verkauf
    trägt er kein ``offers``: ein Angebot ohne Verkauf wäre falsch."""

    def setUp(self):
        self.stuecke = [erzeuge_produkt('Bemalte Bomberjacke'), erzeuge_produkt('Bemalte Hose')]

    def _knoten(self):
        return schema_knoten(self.hole('/produkte/').content.decode())

    def test_jedes_stueck_ist_ein_product_knoten_der_obersten_ebene(self):
        produkte = [k for k in self._knoten() if k.get('@type') == 'Product']
        self.assertEqual(len(produkte), len(self.stuecke))
        pfade = [urlsplit(k['url']).path for k in produkte]
        for stueck in self.stuecke:
            with self.subTest(stueck=stueck.name):
                self.assertIn(stueck.get_absolute_url(), pfade)

    def test_die_sammlung_verweist_per_id_auf_die_knoten(self):
        knoten = self._knoten()
        ids = {k['@id'] for k in knoten if '@id' in k}
        sammlung = next(k for k in knoten if k.get('@type') == 'CollectionPage')
        verweise = [t['@id'] for t in sammlung['hasPart']]
        self.assertEqual(len(verweise), len(self.stuecke))
        for ziel in verweise:
            with self.subTest(ziel=ziel):
                self.assertIn(ziel, ids)

    def test_die_ids_stimmen_mit_denen_der_stueckseiten_ueberein(self):
        """Gleiche @id wie auf der Stückseite: JSON-LD führt beide zusammen."""
        stueck = self.stuecke[0]
        auf_uebersicht = {k['@id'] for k in self._knoten() if k.get('@type') == 'Product'}
        auf_stueckseite = {k['@id'] for k in schema_knoten(
            self.hole(stueck.get_absolute_url()).content.decode()) if k.get('@type') == 'Product'}
        self.assertTrue(auf_stueckseite <= auf_uebersicht)

    def test_ohne_verkauf_traegt_kein_stueck_ein_angebot(self):
        for k in self._knoten():
            with self.subTest(knoten=k.get('@id')):
                self.assertNotIn('offers', k)

    @override_settings(VERKAUF_AKTIV=True)  # prüft den Shop hinter dem Verkaufsschalter
    def test_mit_verkauf_tragen_die_stuecke_ein_angebot(self):
        for k in self._knoten():
            if k.get('@type') == 'Product':
                with self.subTest(knoten=k['@id']):
                    self.assertEqual(k['offers']['@type'], 'Offer')


class LlmsVolltextTest(LuviqTestCase):
    """``/llms-full.txt`` (GE31, VL08): die Kurzfassung plus der Text der Seiten.

    Der Volltext darf nichts sagen, was die Seite nicht sagt – er wird deshalb
    aus den ausgelieferten Seiten gelesen, nicht noch einmal getippt."""

    def test_der_volltext_wird_als_text_ausgeliefert(self):
        antwort = self.hole('/llms-full.txt')
        self.assertEqual(antwort.status_code, 200)
        self.assertTrue(antwort['Content-Type'].startswith('text/plain'))

    def test_der_volltext_beginnt_mit_der_kurzfassung(self):
        """Dieselbe Quelle wie ``llms.txt``: wer eine ändert, ändert beide."""
        kurz = self.hole('/llms.txt').content.decode().rstrip('\n')
        voll = self.hole('/llms-full.txt').content.decode()
        self.assertTrue(voll.startswith(kurz))
        self.assertIn('## Volltext der Seiten', voll)

    def test_der_volltext_ist_ein_volltext(self):
        """GE31 verlangt mehr als 500 Wörter, sonst gilt er als zu knapp."""
        erzeuge_produkt('Bemalte Bomberjacke')
        voll = self.hole('/llms-full.txt').content.decode()
        self.assertGreater(len(voll.split()), 500)

    def test_der_volltext_enthaelt_den_text_der_seiten_wortgleich(self):
        """Ein Satz aus ``/ueber_uns/`` und einer aus dem Archiv stehen
        unverändert im Volltext."""
        erzeuge_produkt('Bemalte Bomberjacke')
        voll = self.hole('/llms-full.txt').content.decode()
        for pfad in ('/ueber_uns/', '/produkte/'):
            haupt = self.hole(pfad).content.decode().split('<main', 1)[1]
            erster = next(
                a for a in re.findall(r'<p[^>]*>(.*?)</p>', haupt, re.DOTALL)
                if len(re.sub(r'<[^>]+>', '', a).split()) >= 15
            )
            satz = ' '.join(re.sub(r'<[^>]+>', ' ', erster).split())[:80]
            with self.subTest(pfad=pfad):
                self.assertIn(satz, voll)
            self.assertIn(f'Adresse: https://testserver{pfad}', voll)

    def test_der_volltext_fuehrt_nur_aktive_stuecke(self):
        aktiv = erzeuge_produkt('Bemalte Bomberjacke')
        weg = erzeuge_produkt('Bereits verkauftes Teil', aktiv=False)
        voll = self.hole('/llms-full.txt').content.decode()
        self.assertIn(aktiv.get_absolute_url(), voll)
        self.assertNotIn(weg.get_absolute_url(), voll)
        self.assertIn('Bemalte Bomberjacke', voll)

    def test_der_volltext_nennt_ohne_verkauf_keine_preise_und_keine_kaufwege(self):
        """Verkaufsschalter aus: dieselbe Zurückhaltung wie in ``llms.txt``."""
        erzeuge_produkt('Bemalte Bomberjacke')
        voll = self.hole('/llms-full.txt').content.decode()
        for verboten in (' EUR', '€', 'UStG', 'PayPal', 'Vorab-Überweisung', '/agb/',
                         '/warenkorb/', '/checkout/'):
            with self.subTest(verboten=verboten):
                self.assertNotIn(verboten, voll)

    def test_der_volltext_laesst_noindex_seiten_aus(self):
        """Nicht freigegebene Wissensbeiträge und noindex-Seiten gehören weder
        in die Sitemap noch hierher. Seit 02.10.2026 sind Pflege, Upcycling und
        Grösse freigegeben; die Kaufweg-Beiträge bleiben ohne Verkauf draussen."""
        voll = self.hole('/llms-full.txt').content.decode()
        for pfad in ('/wissen/bestellen-und-bezahlen/', '/kontakt/danke/', '/login/', '/register/'):
            with self.subTest(pfad=pfad):
                self.assertNotIn(pfad, voll)
        self.assertIn('/wissen/pflege-handbemalte-kleidung/', voll)

    def test_der_volltext_enthaelt_kein_formular_und_keine_navigation(self):
        voll = self.hole('/llms-full.txt').content.decode()
        for fremd in ('<form', '<input', '<script', 'csrfmiddlewaretoken', 'Zum Inhalt springen'):
            with self.subTest(fremd=fremd):
                self.assertNotIn(fremd, voll)

    def test_robots_und_kurzfassung_verweisen_auf_den_volltext(self):
        self.assertIn('/llms-full.txt', self.hole('/robots.txt').content.decode())
        self.assertIn('Volltext: https://testserver/llms-full.txt',
                      self.hole('/llms.txt').content.decode())

    def test_eine_nicht_lesbare_seite_kippt_die_datei_nicht(self):
        """Fällt eine View aus, fehlt nur ihr Abschnitt."""
        from unittest import mock

        with mock.patch('shop1.views.shop.ueber_uns', side_effect=RuntimeError('kaputt')), \
                self.assertLogs('shop1', level='ERROR'):
            antwort = self.hole('/llms-full.txt')
        self.assertEqual(antwort.status_code, 200)
        text = antwort.content.decode()
        self.assertNotIn('/ueber_uns/', text.split('## Volltext der Seiten', 1)[1])
        self.assertIn('### Archiv', text)

    @override_settings(VERKAUF_AKTIV=True)  # prüft den Shop hinter dem Verkaufsschalter
    def test_mit_verkauf_folgt_der_volltext_der_kurzfassung(self):
        erzeuge_produkt('Bemalte Bomberjacke')
        kurz = self.hole('/llms.txt').content.decode().rstrip('\n')
        voll = self.hole('/llms-full.txt').content.decode()
        self.assertTrue(voll.startswith(kurz))
        self.assertIn('### Alle Unikate', voll)


class VolltextLeserTest(LuviqTestCase):
    """Der Leser hinter ``llms-full.txt`` (``shop1/llms_volltext.py``)."""

    def test_nur_der_inhalt_von_main_zaehlt(self):
        from ..llms_volltext import haupttext

        html = (
            '<html><body><nav><a href="/">Start</a></nav>'
            '<main><h1>Titel</h1><p>Erster Absatz.</p>'
            '<form><label>Name</label><input name="x"></form>'
            '<script>var x = 1;</script>'
            '<p aria-hidden="true">versteckt</p>'
            '<ul><li>eins</li><li>zwei</li></ul>'
            '<p><span>Nº 001</span><span>vergeben</span></p>'
            '</main><footer>Fuß</footer></body></html>'
        )
        zeilen = haupttext(html)
        self.assertEqual(zeilen, ['#### Titel', 'Erster Absatz.', '- eins', '- zwei',
                                  'Nº 001 vergeben'])

    def test_ohne_main_kommt_nichts(self):
        from ..llms_volltext import haupttext

        self.assertEqual(haupttext('<html><body><p>Text</p></body></html>'), [])


class RatgeberSchemaTest(LuviqTestCase):
    """``Article`` auf den Wissensbeiträgen (GE15).

    Ein Ratgebertext ohne Autor und ohne Datum ist für eine Antwortmaschine
    eine Aussage ohne Herkunft. Der ``Article``-Knoten liefert beides – und
    fällt damit unter denselben Grundsatz wie alles andere hier: Er darf nur
    behaupten, was auf der Seite selbst steht.
    """

    def _beitraege(self):
        from django.urls import reverse

        from ..views.wissen import WISSEN_BEITRAEGE, nur_mit_verkauf_ausgeblendet

        # Ohne Verkauf leiten die Kaufweg-Beiträge auf /wissen/ um und stehen
        # nicht in der Übersicht; ihr Schema prüft test_verkauf mit Verkauf.
        return [(reverse(b['url_name']), slug, b)
                for slug, b in WISSEN_BEITRAEGE.items()
                if not nur_mit_verkauf_ausgeblendet(b)]

    @staticmethod
    def _artikel(knoten):
        return [k for k in knoten
                if 'Article' in (k.get('@type') if isinstance(k.get('@type'), list)
                                 else [k.get('@type')])]

    def test_jeder_wissensbeitrag_traegt_genau_einen_article(self):
        """Ohne diesen Test bliebe der Knoten auf den Beiträgen aus, die
        später dazukommen – der Einbau hängt an einem ``include``, das man
        beim Anlegen einer Vorlage leicht vergisst."""
        for pfad, slug, _ in self._beitraege():
            with self.subTest(pfad=pfad):
                artikel = self._artikel(schema_knoten(self.hole(pfad).content.decode()))
                self.assertEqual(len(artikel), 1, f'{slug}: {len(artikel)} Article-Knoten')

    def test_die_ueberschrift_des_article_steht_als_h1_auf_der_seite(self):
        """Der Grundsatz dieses Moduls, angewandt auf die ``headline``: ein
        Beitrag, der im Schema anders heisst als in seiner Überschrift, führt
        eine Antwortmaschine in die Irre."""
        for pfad, slug, beitrag in self._beitraege():
            with self.subTest(pfad=pfad):
                inhalt = self.hole(pfad).content.decode()
                artikel = self._artikel(schema_knoten(inhalt))[0]
                self.assertEqual(artikel['headline'], beitrag['titel'])
                self.assertIn(beitrag['titel'], ueberschriften(inhalt))

    def test_der_article_nennt_autorin_und_beide_daten(self):
        """``author`` verweist auf dieselbe Person wie der Rest der Seite
        (``#luisa``) – ohne Autor fehlt das E-E-A-T-Signal. Und das
        Erscheinungsdatum darf nicht nach dem Änderungsdatum liegen: das wäre
        ein Beitrag, der geändert wurde, bevor es ihn gab."""
        from ..seiten_stand import SEITEN_STAND

        for pfad, slug, beitrag in self._beitraege():
            with self.subTest(pfad=pfad):
                artikel = self._artikel(schema_knoten(self.hole(pfad).content.decode()))[0]
                self.assertEqual(kennung(artikel['author']), '#luisa')
                self.assertEqual(kennung(artikel['publisher']), '#organization')
                self.assertEqual(artikel['datePublished'], beitrag['veroeffentlicht'])
                self.assertEqual(artikel['dateModified'], SEITEN_STAND[beitrag['url_name']])
                self.assertLessEqual(
                    date.fromisoformat(artikel['datePublished']),
                    date.fromisoformat(artikel['dateModified']),
                    f'{slug}: veröffentlicht nach der letzten Änderung',
                )

    def test_die_uebersicht_gibt_sich_nicht_als_beitrag_aus(self):
        """``/wissen/`` ist das Verzeichnis des Bereichs, kein Ratgebertext.
        Ein ``Article`` dort behauptete einen Beitrag, den es nicht gibt –
        dieselbe Regel wie bei den Öffnungszeiten und der SearchAction."""
        knoten = schema_knoten(self.hole('/wissen/').content.decode())
        self.assertEqual(self._artikel(knoten), [])
        for k in knoten:
            self.assertNotIn(k.get('@type'), ('BlogPosting', 'CollectionPage'))

    def test_die_liste_der_uebersicht_nennt_die_sichtbaren_beitraege(self):
        """Die ``ItemList`` ist der ehrliche Ersatz: sie darf genau die
        Beiträge nennen, die weiter unten auf derselben Seite verlinkt sind –
        in derselben Reihenfolge und mit denselben Titeln."""
        inhalt = self.hole('/wissen/').content.decode()
        listen = [k for k in schema_knoten(inhalt) if k.get('@type') == 'ItemList']
        self.assertEqual(len(listen), 1)
        eintraege = listen[0]['itemListElement']
        erwartet = [b['titel'] for _, _, b in self._beitraege()]
        self.assertEqual([e['name'] for e in eintraege], erwartet)
        self.assertEqual(listen[0]['numberOfItems'], len(erwartet))
        for eintrag in eintraege:
            with self.subTest(name=eintrag['name']):
                self.assertIn(eintrag['name'], sichtbarer_text(inhalt))
                pfad = urlsplit(eintrag['url']).path
                self.assertIn(f'href="{pfad}"', inhalt)
                self.assertEqual(self.hole(pfad).status_code, 200)
