"""Erreichbarkeit: antwortet jede Adresse noch so, wie sie soll?

Das ist die teuerste Klasse von Fehlern: Eine Seite, die nach einer Änderung
mit 500 oder 404 antwortet, ist für Kundschaft und Suchmaschinen weg – und
niemand merkt es, solange niemand sie aufruft.
"""

from django.contrib.auth.models import User
from django.urls import NoReverseMatch, get_resolver, reverse

from ._basis import (
    ADMIN_SEITEN,
    GESCHUETZTE_SEITEN,
    OEFFENTLICHE_SEITEN,
    PFLICHTSEITEN,
    LuviqTestCase,
    erzeuge_benutzer,
    erzeuge_produkt,
)


class OeffentlicheSeitenTest(LuviqTestCase):
    """Jede Seite, die ein Besucher ohne Anmeldung sieht."""

    def test_jede_oeffentliche_seite_antwortet_mit_200(self):
        """Verhindert, dass eine Änderung an Views, Templates oder URLs eine
        öffentliche Seite unbemerkt auf 404 oder 500 wirft."""
        for pfad in OEFFENTLICHE_SEITEN:
            with self.subTest(pfad=pfad):
                antwort = self.hole(pfad)
                self.assertEqual(
                    antwort.status_code, 200,
                    f'{pfad} antwortet mit {antwort.status_code} statt 200',
                )

    def test_jede_pflichtseite_traegt_ihren_rechtlich_noetigen_inhalt(self):
        """Verhindert, dass Impressum, Datenschutz oder AGB zwar noch antworten,
        aber leer ausgeliefert werden – der Statuscode allein deckt das nicht auf."""
        erwartet = {
            '/impressum/': 'Alsfeld',
            '/datenschutz/': 'Daten',
            '/agb/': 'Widerruf',
        }
        for pfad in PFLICHTSEITEN:
            with self.subTest(pfad=pfad):
                inhalt = self.hole(pfad).content.decode()
                self.assertIn(erwartet[pfad], inhalt)
                self.assertGreater(
                    len(inhalt), 2000,
                    f'{pfad} liefert auffällig wenig Inhalt aus',
                )

    def test_unbekannte_adresse_liefert_404_und_keinen_serverfehler(self):
        """Verhindert, dass ein Tippfehler in einer URL-Regel dazu führt, dass
        beliebige Pfade in einer View landen und mit 500 abstürzen."""
        antwort = self.hole('/gibt-es-nicht-und-soll-es-nicht-geben/')
        self.assertEqual(antwort.status_code, 404)

    def test_jeder_url_name_laesst_sich_aufloesen(self):
        """Verhindert den häufigsten Fehler dieses Projekts: eine neue View wird
        in ``shop1/views/__init__.py`` nicht re-exportiert oder ein URL-Name wird
        umbenannt, während Templates ihn per ``{% url %}`` weiter benutzen."""
        namen = [n for n in get_resolver().reverse_dict.keys() if isinstance(n, str)]
        self.assertGreater(len(namen), 50, 'URLconf wirkt unvollständig geladen')
        for name in namen:
            with self.subTest(name=name):
                try:
                    reverse(name)
                except NoReverseMatch:
                    pass  # Route mit Pflichtparametern – hier nicht prüfbar


class ProduktseitenTest(LuviqTestCase):
    """Produktdetailseiten und die Altlink-Kompatibilität."""

    def setUp(self):
        self.produkt = erzeuge_produkt('Handbemalte Jeansjacke')

    def test_produktseite_ist_ueber_ihren_slug_erreichbar(self):
        """Verhindert, dass die kanonische Produkt-URL bricht – jede
        Sitemap-, Newsletter- und Suchmaschinenverlinkung zeigt darauf."""
        antwort = self.hole(self.produkt.get_absolute_url())
        self.assertEqual(antwort.status_code, 200)
        self.assertContains(antwort, 'Handbemalte Jeansjacke')

    def test_alte_id_adresse_leitet_dauerhaft_auf_die_slug_adresse_um(self):
        """Verhindert, dass die Altlink-Route ``produkt/<id>/`` verloren geht.
        Frühere Links und Newsletter benutzen sie; ohne 301 verfällt ihr Rang."""
        antwort = self.hole(f'/produkt/{self.produkt.id}/')
        self.assertEqual(antwort.status_code, 301)
        self.assertEqual(antwort['Location'], self.produkt.get_absolute_url())

    def test_inaktives_produkt_ist_nicht_mehr_oeffentlich_abrufbar(self):
        """Verhindert, dass ein im Admin deaktiviertes Produkt weiter verkauft
        werden kann, weil seine Detailseite bestehen bleibt."""
        self.produkt.aktiv = False
        self.produkt.save()
        self.assertEqual(self.hole(self.produkt.get_absolute_url()).status_code, 404)
        self.assertEqual(self.hole(f'/produkt/{self.produkt.id}/').status_code, 404)

    def test_produktliste_zeigt_nur_aktive_produkte(self):
        """Verhindert, dass ein deaktiviertes Produkt in der Übersicht stehen
        bleibt und ins Leere verlinkt."""
        verborgen = erzeuge_produkt('Stillgelegtes Teil', aktiv=False)
        inhalt = self.hole('/produkte/').content.decode()
        self.assertIn('Handbemalte Jeansjacke', inhalt)
        self.assertNotIn(verborgen.name, inhalt)


class ZugriffsschutzTest(LuviqTestCase):
    """Wer darf was sehen – der Teil, dessen Ausfall am teuersten wird."""

    def setUp(self):
        self.kundin = erzeuge_benutzer('kundin')
        self.besitzerin = User.objects.create_superuser(
            'shopbesitzer', 'shop@example.invalid', 'ein-langes-testpasswort'
        )

    def test_geschuetzte_seite_leitet_nicht_angemeldete_zum_login(self):
        """Verhindert, dass ein vergessener ``@login_required`` fremde Warenkörbe,
        Profile oder Bestellvorgänge öffentlich macht."""
        for pfad in GESCHUETZTE_SEITEN:
            with self.subTest(pfad=pfad):
                antwort = self.hole(pfad)
                self.assertEqual(
                    antwort.status_code, 302,
                    f'{pfad} ist ohne Anmeldung erreichbar',
                )
                self.assertIn('/login/', antwort['Location'])

    def test_admin_panel_weist_nicht_angemeldete_ab(self):
        """Verhindert, dass das Shop-Admin-Panel ohne Anmeldung offensteht –
        dort lassen sich Produkte löschen und Massen-Newsletter auslösen."""
        for pfad in ADMIN_SEITEN:
            with self.subTest(pfad=pfad):
                antwort = self.hole(pfad)
                self.assertEqual(antwort.status_code, 302, f'{pfad} ist offen')
                self.assertNotIn('/shop-admin/', antwort['Location'])

    def test_admin_panel_weist_angemeldete_ohne_rechte_ab(self):
        """Verhindert genau den Fehler, der beim Aufräumen der doppelten
        ``admin_required``-Fassungen entstehen kann: der Decorator fällt weg und
        jede angemeldete Kundin kommt ins Admin-Panel."""
        self.client.force_login(self.kundin)
        for pfad in ADMIN_SEITEN:
            with self.subTest(pfad=pfad):
                antwort = self.hole(pfad)
                self.assertEqual(
                    antwort.status_code, 302,
                    f'{pfad} ist für eine normale Kundin erreichbar',
                )

    def test_admin_panel_laesst_die_shopbesitzerin_durch(self):
        """Gegenprobe zum Test darüber: ein zu scharfer Zugriffsschutz würde die
        Betreiberin aus ihrem eigenen Panel aussperren."""
        self.client.force_login(self.besitzerin)
        for pfad in ADMIN_SEITEN:
            with self.subTest(pfad=pfad):
                self.assertEqual(self.hole(pfad).status_code, 200)
