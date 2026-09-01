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

from ._basis import INHALTSSEITEN, LuviqTestCase, erzeuge_produkt

_JSONLD = re.compile(
    r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>', re.DOTALL
)

#: Die Seiten, die ein FAQPage-Schema tragen (``kontakt.html`` und
#: ``liefergebiet.html``). Die Startseite steht bewusst nicht darin: ihr
#: Schema wurde entfernt, weil die Fragen dort nirgends sichtbar waren (siehe
#: Kommentar in ``index.html``). Kommt eine Seite dazu, gehört sie hier hinein
#: – dann prüft der Test auch dort, dass jede Frage sichtbar auf der Seite steht.
FAQ_SEITEN = ('/kontakt/', '/liefergebiet/')


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
        ``Produkt.aktualisiert_am`` – sie wird nicht erfunden."""
        inhalt = self.hole(self.produkt.get_absolute_url()).content.decode()
        produktknoten = [k for k in schema_knoten(inhalt) if k.get('@type') == 'Product']
        self.assertEqual(len(produktknoten), 1)
        self.assertEqual(
            produktknoten[0]['dateModified'][:10],
            self.produkt.aktualisiert_am.date().isoformat(),
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
        über die Kurzfassung nie erreichen."""
        text = self.hole('/llms.txt').content.decode()
        for pfad in INHALTSSEITEN:
            if pfad == '/impressum/':
                continue  # steht unter "Rechtliches", per reverse() erzeugt
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

    def test_die_kurzfassung_behauptet_nichts_anderes_als_die_agb(self):
        """Verhindert genau den Fehler, den dieser Bereich verhindern soll: die
        Kurzfassung nennt Zahlungsarten, die auf der Seite nicht gelten."""
        text = self.hole('/llms.txt').content.decode()
        agb = sichtbarer_text(self.hole('/agb/').content.decode())
        self.assertIn('PayPal oder Vorab-Ueberweisung', text)
        self.assertIn('PayPal oder Vorab-Überweisung', agb)
