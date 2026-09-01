"""Sitemap, robots.txt und die Angaben im Kopf jeder Seite.

Diese Dateien sind handgeschriebene Views (``shop1/views/legal.py``), keine
Django-Sitemap. Sie laufen deshalb nicht automatisch mit, wenn eine Route
dazukommt oder verschwindet – genau das prüfen die Tests hier.
"""

import re
from xml.etree import ElementTree

from ._basis import (
    INHALTSSEITEN,
    OEFFENTLICHE_SEITEN,
    LuviqTestCase,
    erzeuge_produkt,
)

_LOC = re.compile(r'<loc>(.*?)</loc>')
_TITEL = re.compile(r'<title>(.*?)</title>', re.DOTALL)
_CANONICAL = re.compile(r'<link[^>]+rel="canonical"[^>]+href="([^"]+)"')
_DESCRIPTION = re.compile(r'<meta\s+name="description"\s+content="([^"]*)"')


class SitemapTest(LuviqTestCase):
    """Die Sitemap ist die Liste, die Google abarbeitet."""

    def setUp(self):
        self.produkt = erzeuge_produkt('Bemalte Bomberjacke')

    def _adressen(self):
        xml = self.hole('/sitemap.xml').content.decode()
        return xml, _LOC.findall(xml)

    def test_sitemap_ist_wohlgeformtes_xml(self):
        """Verhindert, dass ein unmaskiertes Zeichen in einem Produktnamen die
        gesamte Sitemap unlesbar macht – Google verwirft sie dann komplett."""
        roh = self.hole('/sitemap.xml').content
        ElementTree.fromstring(roh)  # wirft bei kaputtem XML

    def test_jede_adresse_der_sitemap_antwortet_mit_200(self):
        """Verhindert die häufigste Sitemap-Fehlermeldung der Search Console:
        eine gelistete Adresse, die 404 liefert. Passiert, sobald eine Route
        umbenannt wird und die handgeschriebene Sitemap davon nichts erfährt."""
        _, adressen = self._adressen()
        self.assertGreaterEqual(len(adressen), 8, 'Sitemap wirkt unvollständig')
        for adresse in adressen:
            pfad = adresse.split('testserver', 1)[-1] or '/'
            with self.subTest(adresse=adresse):
                self.assertEqual(
                    self.hole(pfad).status_code, 200,
                    f'{pfad} steht in der Sitemap, antwortet aber nicht mit 200',
                )

    def test_sitemap_nennt_jede_oeffentlich_indexierbare_seite(self):
        """Verhindert, dass eine neue Seite gebaut, aber nie eingetragen wird –
        sie bleibt dann für Suchmaschinen praktisch unsichtbar."""
        _, adressen = self._adressen()
        pfade = {a.split('testserver', 1)[-1] or '/' for a in adressen}
        pflicht = {
            '/', '/produkte/', '/gaestebuch/', '/ueber_uns/',
            '/liefergebiet/', '/kontakt/', '/datenschutz/', '/agb/',
        }
        self.assertTrue(
            pflicht.issubset(pfade),
            f'In der Sitemap fehlen: {sorted(pflicht - pfade)}',
        )

    def test_keine_adresse_der_sitemap_ist_auf_noindex_gesetzt(self):
        """Verhindert das widersprüchliche Signal, das dieser Lauf vorgefunden
        hat: ``/impressum/`` stand in der Sitemap und setzte zugleich
        ``noindex``. Die Search Console meldet das als Fehler."""
        _, adressen = self._adressen()
        for adresse in adressen:
            pfad = adresse.split('testserver', 1)[-1] or '/'
            with self.subTest(pfad=pfad):
                inhalt = self.hole(pfad).content.decode()
                treffer = re.findall(r'<meta\s+name="robots"\s+content="([^"]*)"', inhalt)
                self.assertTrue(treffer, f'{pfad} hat keine robots-Angabe')
                self.assertNotIn(
                    'noindex', treffer[0],
                    f'{pfad} steht in der Sitemap, verbietet aber die Aufnahme',
                )

    def test_sitemap_fuehrt_aktive_produkte_mit_lastmod(self):
        """Verhindert, dass Produktseiten aus der Sitemap fallen oder ohne
        Änderungsdatum stehen – ohne ``lastmod`` crawlt Google seltener neu."""
        xml, adressen = self._adressen()
        pfade = {a.split('testserver', 1)[-1] for a in adressen}
        self.assertIn(self.produkt.get_absolute_url(), pfade)
        self.assertIn('<lastmod>', xml)

    def test_sitemap_fuehrt_keine_inaktiven_produkte(self):
        """Verhindert, dass ein deaktiviertes Produkt Suchmaschinen weiter auf
        eine 404-Seite schickt."""
        verborgen = erzeuge_produkt('Eingelagertes Teil', aktiv=False)
        _, adressen = self._adressen()
        self.assertNotIn(
            verborgen.get_absolute_url(),
            {a.split('testserver', 1)[-1] for a in adressen},
        )

    def test_keine_adresse_der_sitemap_ist_in_robots_gesperrt(self):
        """Verhindert das widersprüchliche Signal 'bitte crawlen' in der Sitemap
        gegen 'nicht crawlen' in der robots.txt – Google meldet das als Fehler."""
        _, adressen = self._adressen()
        robots = self.hole('/robots.txt').content.decode()
        gesperrt = [z.split(':', 1)[1].strip()
                    for z in robots.splitlines() if z.startswith('Disallow:')]
        for adresse in adressen:
            pfad = adresse.split('testserver', 1)[-1] or '/'
            for regel in gesperrt:
                with self.subTest(pfad=pfad, regel=regel):
                    self.assertFalse(
                        pfad.startswith(regel),
                        f'{pfad} steht in der Sitemap, ist aber per "{regel}" gesperrt',
                    )


class RobotsTest(LuviqTestCase):
    """robots.txt – die Datei, mit der man sich am schnellsten selbst aussperrt."""

    def setUp(self):
        self.inhalt = self.hole('/robots.txt').content.decode()

    def test_robots_verweist_auf_die_sitemap(self):
        """Verhindert, dass der Sitemap-Verweis beim Bearbeiten verlorengeht;
        er ist der Weg, auf dem Crawler die Sitemap ohne Anmeldung finden."""
        self.assertIn('Sitemap:', self.inhalt)
        self.assertIn('/sitemap.xml', self.inhalt)

    def test_robots_sperrt_die_privaten_bereiche(self):
        """Verhindert, dass Warenkorb, Bezahlvorgang, Profil oder das
        Admin-Panel in den Suchindex geraten."""
        for pfad in ('/shop-admin/', '/warenkorb/', '/checkout/',
                     '/payment/', '/profil/', '/reset/'):
            with self.subTest(pfad=pfad):
                self.assertIn(f'Disallow: {pfad}', self.inhalt)

    def test_robots_sperrt_die_seite_nicht_komplett(self):
        """Verhindert den teuersten Ein-Zeilen-Fehler im ganzen Projekt:
        ein 'Disallow: /' nimmt die Seite vollständig aus dem Index."""
        for zeile in self.inhalt.splitlines():
            self.assertNotEqual(zeile.strip(), 'Disallow: /')

    def test_robots_sperrt_keinen_antwort_crawler_aus(self):
        """Verhindert, dass die Seite in KI-Antworten nicht mehr zitiert werden
        kann, weil ein Crawler wie GPTBot oder PerplexityBot gesperrt wurde."""
        for bot in ('GPTBot', 'OAI-SearchBot', 'PerplexityBot',
                    'ClaudeBot', 'Google-Extended'):
            with self.subTest(bot=bot):
                block = re.search(
                    rf'User-agent:\s*{bot}\s*\n(.*?)(?:\n\s*\n|\Z)',
                    self.inhalt, re.IGNORECASE | re.DOTALL,
                )
                if block:
                    self.assertNotIn('Disallow: /\n', block.group(1) + '\n')


class VerweiseTest(LuviqTestCase):
    """Adressen, die aus dem Projekt heraus gesetzt werden."""

    def test_die_favicon_routen_zeigen_auf_eine_vorhandene_datei(self):
        """Verhindert den Zustand, den dieser Lauf vorgefunden hat: beide
        Routen leiteten auf ``/static/shop1/favicon.ico`` bzw. ``.png`` – keine
        der beiden Dateien existiert, jeder Browser holte sich eine 404."""
        from django.contrib.staticfiles import finders

        for pfad in ('/favicon.ico', '/favicon.png'):
            with self.subTest(pfad=pfad):
                antwort = self.hole(pfad)
                self.assertEqual(antwort.status_code, 301)
                ziel = antwort['Location']
                self.assertTrue(ziel.startswith('/static/'))
                self.assertIsNotNone(
                    finders.find(ziel[len('/static/'):]),
                    f'{pfad} verweist auf {ziel}, diese Datei gibt es nicht',
                )

    def test_der_newsletter_verlinkt_das_produkt_richtig(self):
        """Verhindert den Fehler, den dieser Lauf vorgefunden hat: der
        Newsletter baute ``/produkte/<id>/`` zusammen – diese Route gibt es
        nicht. Jeder verschickte Newsletter-Button führte auf eine 404."""
        from unittest import mock

        from ..models import Subscriber
        from ..utils import send_newsletter_email

        produkt = erzeuge_produkt('Bemalte Bomberjacke')
        abonnentin = Subscriber(email='leserin@example.invalid')
        with mock.patch('shop1.utils.send_brevo_email') as versand:
            send_newsletter_email(produkt, [abonnentin])

        html = versand.call_args.args[1]
        self.assertIn(produkt.get_absolute_url(), html)
        self.assertNotIn(f'/produkte/{produkt.id}/', html)
        pfad = produkt.get_absolute_url()
        self.assertEqual(self.hole(pfad).status_code, 200)


class SeitenkopfTest(LuviqTestCase):
    """Titel, Beschreibung und canonical – was in der Trefferliste steht."""

    def test_jede_seite_hat_genau_einen_titel(self):
        """Verhindert, dass ein Template-Block doppelt gesetzt wird und die
        Seite zwei ``<title>`` ausliefert – Suchmaschinen wählen dann selbst."""
        for pfad in OEFFENTLICHE_SEITEN:
            with self.subTest(pfad=pfad):
                titel = _TITEL.findall(self.hole(pfad).content.decode())
                self.assertEqual(len(titel), 1, f'{pfad} hat {len(titel)} Titel')
                self.assertTrue(titel[0].strip(), f'{pfad} hat einen leeren Titel')

    def test_jede_seite_hat_ein_canonical_auf_sich_selbst(self):
        """Verhindert, dass eine Seite auf eine fremde Adresse kanonisiert und
        damit ihre eigene Auffindbarkeit an eine andere Seite abtritt."""
        for pfad in OEFFENTLICHE_SEITEN:
            with self.subTest(pfad=pfad):
                treffer = _CANONICAL.findall(self.hole(pfad).content.decode())
                self.assertEqual(len(treffer), 1, f'{pfad} hat {len(treffer)} canonical')
                self.assertTrue(
                    treffer[0].endswith(pfad),
                    f'{pfad} kanonisiert auf {treffer[0]}',
                )

    def test_jede_seite_hat_eine_nicht_leere_beschreibung(self):
        """Verhindert, dass eine Seite ohne ``meta description`` ausgeliefert
        wird – Google erfindet dann einen Textausschnitt."""
        for pfad in OEFFENTLICHE_SEITEN:
            with self.subTest(pfad=pfad):
                treffer = _DESCRIPTION.findall(self.hole(pfad).content.decode())
                self.assertEqual(len(treffer), 1, f'{pfad} hat {len(treffer)} Beschreibungen')
                self.assertGreater(len(treffer[0].strip()), 40, f'{pfad}: Beschreibung zu kurz')

    def test_keine_zwei_seiten_teilen_sich_titel_oder_beschreibung(self):
        """Verhindert, dass Seiten in der Trefferliste ununterscheidbar werden.
        Vor diesem Lauf erbten Impressum, Datenschutz, AGB, Warenkorb und alle
        Konto-Seiten wörtlich die Beschreibung der Startseite."""
        titel, beschreibungen = {}, {}
        for pfad in OEFFENTLICHE_SEITEN:
            inhalt = self.hole(pfad).content.decode()
            titel.setdefault(_TITEL.findall(inhalt)[0].strip(), []).append(pfad)
            beschreibungen.setdefault(
                _DESCRIPTION.findall(inhalt)[0].strip(), []).append(pfad)

        for name, sammlung in (('Titel', titel), ('Beschreibung', beschreibungen)):
            for wert, pfade in sammlung.items():
                with self.subTest(art=name, wert=wert[:50]):
                    self.assertEqual(
                        len(pfade), 1,
                        f'Gleiche {name} auf {pfade}: "{wert[:80]}"',
                    )

    def test_titel_und_beschreibung_halten_die_anzeigelaenge_ein(self):
        """Verhindert Titel und Beschreibungen, die Google mitten im Wort
        abschneidet oder als zu dünn verwirft."""
        for pfad in OEFFENTLICHE_SEITEN:
            inhalt = self.hole(pfad).content.decode()
            with self.subTest(pfad=pfad, teil='Titel'):
                laenge = len(_TITEL.findall(inhalt)[0].strip())
                self.assertTrue(25 <= laenge <= 70, f'{pfad}: Titel {laenge} Zeichen')
            with self.subTest(pfad=pfad, teil='Beschreibung'):
                laenge = len(_DESCRIPTION.findall(inhalt)[0].strip())
                self.assertTrue(50 <= laenge <= 200, f'{pfad}: Beschreibung {laenge} Zeichen')

    def test_jede_seite_hat_genau_eine_h1(self):
        """Verhindert eine kaputte Überschriftenstruktur: keine oder mehrere
        ``h1`` machen es Suchmaschinen und Screenreadern unmöglich zu erkennen,
        worum es auf der Seite geht.

        Geprüft werden nur die Inhaltsseiten: die Anmelde- und Passwortseiten
        sind in robots.txt gesperrt und tragen bauartbedingt keine ``h1``."""
        for pfad in INHALTSSEITEN:
            with self.subTest(pfad=pfad):
                anzahl = len(re.findall(r'<h1[\s>]', self.hole(pfad).content.decode()))
                self.assertEqual(anzahl, 1, f'{pfad} hat {anzahl} h1-Überschriften')
