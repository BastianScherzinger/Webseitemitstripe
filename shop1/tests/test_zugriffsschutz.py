"""Zugriffsschutz auf **allen** Routen des Shop-Admin-Panels
(``shop1/admin_views.py``).

Die Routen werden nicht von Hand aufgezählt, sondern aus dem URL-Verzeichnis
gesammelt: alles unter ``shop-admin/``. Eine neue Admin-Route ist damit
automatisch mitgeprüft; ``ADMIN_SEITEN`` in ``_basis.py`` (fünf Adressen
ohne Parameter) bleibt für die Seitentests bestehen.

Je Route wird behauptet: nicht angemeldet → Umleitung; angemeldet, aber
ohne Rechte → Umleitung und keine Änderung an den Daten; Superuser →
Zugang; der Decorator sitzt am Funktionsobjekt.
"""

import os
from decimal import Decimal
from unittest import mock

from django.contrib.auth.models import User
from django.urls import URLPattern, URLResolver, get_resolver, reverse

from .. import admin_views
from ..models import Comment, Order, Produkt, Subscriber, Werbung
from ._basis import LuviqTestCase, erzeuge_benutzer, erzeuge_produkt

_NEWSLETTER = 'shop1.utils.send_newsletter_email'
_CLOUDINARY = 'shop1.admin_views._upload_werbung_bild'


def admin_routen():
    """Alle Routen unter ``shop-admin/`` als ``(name, pfadmuster, view, parameter)``."""
    gefunden = []

    def sammle(muster, praefix, konverter):
        for eintrag in muster:
            if isinstance(eintrag, URLResolver):
                if eintrag.namespace:      # Django-Admin: fremder Code
                    continue
                sammle(eintrag.url_patterns, praefix + str(eintrag.pattern),
                       {**konverter, **eintrag.pattern.converters})
            elif isinstance(eintrag, URLPattern):
                pfad = praefix + str(eintrag.pattern)
                if pfad.startswith('shop-admin/'):
                    parameter = {**konverter, **eintrag.pattern.converters}
                    gefunden.append((eintrag.name, pfad, eintrag.callback, tuple(parameter)))

    sammle(get_resolver().url_patterns, '', {})
    return gefunden


def _leer(request, *args, **kwargs):
    """Platzhalter-View, um die Wrapper-Codeobjekte der Decorators zu gewinnen."""


#: Codeobjekte der beiden Wrapper aus ``admin_views``. Jede damit dekorierte
#: View trägt genau eines davon als ``__code__`` – so lässt sich am
#: Funktionsobjekt prüfen, ob der Decorator sitzt, ohne die View aufzurufen.
_ADMIN_WRAPPER = admin_views.admin_required(_leer).__code__
_PRODUKT_WRAPPER = admin_views.product_manager_required(_leer).__code__


class AdminRoutenTest(LuviqTestCase):
    """Vier Konten: anonym, Kundin, Mitarbeiterin (``is_staff``), Superuser."""

    def setUp(self):
        self.kundin = erzeuge_benutzer('kundin')
        self.mitarbeiterin = erzeuge_benutzer('mitarbeiterin', is_staff=True)
        self.besitzerin = User.objects.create_superuser(
            'shopbesitzer', 'shop@example.invalid', 'ein-langes-testpasswort'
        )
        self.produkt = erzeuge_produkt('Bemalte Jacke', preis=Decimal('80.00'))
        self.bestellung = Order.objects.create(
            user=self.kundin, vorname='Erika', nachname='Musterfrau',
            email='erika@example.invalid', adresse='Grünberger Str. 16',
            stadt='Alsfeld', postleitzahl='36304', land='Deutschland',
            gesamt_betrag=Decimal('80.00'),
        )
        self.werbung = Werbung.objects.create(
            titel='Testkampagne', link='https://luviq.example/kampagne', budget=Decimal('10.00'),
        )
        self.routen = admin_routen()

    # ── Helfer ────────────────────────────────────────────────────────────

    def adresse(self, name, parameter):
        """Baut die Adresse einer Route mit vorhandenen Datensätzen."""
        werte = {
            'user_id': self.kundin.id,
            'produkt_id': self.produkt.id,
            'order_id': self.bestellung.id,
            'werbung_id': self.werbung.id,
        }
        fehlend = set(parameter) - set(werte)
        self.assertFalse(fehlend, f'Route {name}: kein Beispielwert für {fehlend} – oben ergänzen')
        return reverse(name, kwargs={p: werte[p] for p in parameter})

    def datenstand(self):
        """Alles, was eine Admin-Route verändern könnte – muss für Unbefugte gleich bleiben."""
        self.produkt.refresh_from_db()
        self.werbung.refresh_from_db()
        return {
            'produkte': Produkt.objects.count(),
            'produkt_aktiv': self.produkt.aktiv,
            'newsletter_gesendet': self.produkt.newsletter_gesendet,
            'bestellungen': Order.objects.count(),
            'benutzer': User.objects.count(),
            'werbungen': Werbung.objects.count(),
            'werbung_aktiv': self.werbung.aktiv,
        }

    def abgewiesen(self, wer):
        """GET und POST auf jede Route: Umleitung weg vom Panel, Datenstand unverändert."""
        vorher = self.datenstand()
        with mock.patch(_NEWSLETTER) as newsletter, mock.patch(_CLOUDINARY):
            for name, pfad, _, parameter in self.routen:
                adresse = self.adresse(name, parameter)
                for aufruf in (self.hole, self.sende):
                    with self.subTest(route=name, methode=aufruf.__name__):
                        antwort = aufruf(adresse)
                        self.assertEqual(antwort.status_code, 302, f'{pfad} ist für {wer} erreichbar')
                        self.assertNotIn('/shop-admin/', antwort['Location'])
        newsletter.assert_not_called()
        self.assertEqual(self.datenstand(), vorher)

    # ── Tests ─────────────────────────────────────────────────────────────

    def test_die_sammlung_findet_alle_admin_routen(self):
        """Verhindert, dass diese Datei grün bleibt, obwohl sie nichts prüft:
        die Sammlung muss die Admin-Routen tatsächlich finden, und jede
        View aus ``admin_views`` muss unter ``shop-admin/`` liegen – eine
        Admin-View an einer anderen Adresse entginge allen Tests hier."""
        self.assertGreater(len(self.routen), 20, 'Sammlung hat nicht gegriffen')

        namen = {name for name, *_ in self.routen}
        self.assertTrue({'admin_resend_newsletter', 'admin_user_delete', 'admin_order_delete',
                         'admin_produkt_toggle', 'admin_werbung_delete'} <= namen)

        def alle_routen(muster, praefix=''):
            for eintrag in muster:
                if isinstance(eintrag, URLResolver):
                    yield from alle_routen(eintrag.url_patterns, praefix + str(eintrag.pattern))
                elif isinstance(eintrag, URLPattern):
                    yield praefix + str(eintrag.pattern), eintrag.callback

        verirrt = [
            pfad for pfad, view in alle_routen(get_resolver().url_patterns)
            if getattr(view, '__module__', '') == admin_views.__name__ and not pfad.startswith('shop-admin/')
        ]
        self.assertEqual(verirrt, [], 'Admin-Views ausserhalb von shop-admin/')

    def test_der_zugriffsschutz_sitzt_an_jeder_admin_view_als_decorator(self):
        """Verhindert, dass eine neue Admin-View ohne ``@admin_required`` oder
        ``@product_manager_required`` angelegt wird – geprüft am
        Funktionsobjekt, unabhängig davon, wie die View auf einen Aufruf
        reagiert."""
        for name, pfad, view, _ in self.routen:
            with self.subTest(route=name):
                self.assertTrue(hasattr(view, '__wrapped__'), f'{pfad}: kein Decorator')
                self.assertIn(view.__code__, (_ADMIN_WRAPPER, _PRODUKT_WRAPPER),
                              f'{pfad}: weder admin_required noch product_manager_required')

    def test_nicht_angemeldete_werden_von_jeder_admin_route_umgeleitet(self):
        """Verhindert, dass eine Admin-Route ohne Anmeldung offensteht – dort
        werden Benutzer und Bestellungen gelöscht und Newsletter an alle
        Abonnenten ausgelöst."""
        self.abgewiesen('Unangemeldete')

    def test_angemeldete_ohne_rechte_kommen_auf_keine_admin_route(self):
        """Verhindert den in der Praxis übersehenen Fall: ``@login_required``
        genügt nicht, eine gewöhnliche Kundin ist angemeldet und darf
        trotzdem nichts – weder sehen noch per POST auslösen."""
        self.client.force_login(self.kundin)
        self.abgewiesen('eine Kundin')

    def test_mitarbeiterinnen_erreichen_nur_die_produktverwaltung(self):
        """Verhindert, dass ``is_staff`` mehr öffnet als die Produktverwaltung:
        Benutzer, Bestellungen, Statistik und Werbung bleiben der
        Shopbesitzerin vorbehalten (``admin_required``)."""
        self.client.force_login(self.mitarbeiterin)
        with mock.patch(_NEWSLETTER), mock.patch(_CLOUDINARY):
            for name, pfad, view, parameter in self.routen:
                with self.subTest(route=name):
                    antwort = self.hole(self.adresse(name, parameter))
                    if view.__code__ is _PRODUKT_WRAPPER:
                        self.assertIn(antwort.status_code, (200, 302))
                        if antwort.status_code == 302:
                            self.assertIn('/shop-admin/', antwort['Location'])
                    else:
                        self.assertEqual(antwort.status_code, 302, f'{pfad} ist für Mitarbeiterinnen offen')
                        self.assertNotIn('/shop-admin/', antwort['Location'])

    def test_die_shopbesitzerin_erreicht_jede_admin_route(self):
        """Gegenprobe: ein zu scharfer Schutz sperrte die Betreiberin aus ihrem
        eigenen Panel. Jede Route antwortet ihr mit einer Seite oder leitet
        innerhalb des Panels weiter – nie zur Startseite mit
        „keine Berechtigung"."""
        self.client.force_login(self.besitzerin)
        with mock.patch(_NEWSLETTER), mock.patch(_CLOUDINARY):
            for name, pfad, _, parameter in self.routen:
                with self.subTest(route=name):
                    antwort = self.hole(self.adresse(name, parameter))
                    self.assertIn(antwort.status_code, (200, 302), f'{pfad}: {antwort.status_code}')
                    if antwort.status_code == 302:
                        self.assertIn('/shop-admin/', antwort['Location'], f'{pfad} weist die Besitzerin ab')

    def test_der_eingetragene_admin_benutzername_gilt_auch_ohne_superuser(self):
        """Verhindert, dass die zweite Hälfte der Admin-Definition wegfällt:
        ``ADMIN_USERNAME`` aus der Umgebung öffnet das Panel auch ohne
        ``is_superuser`` – so meldet sich die Betreiberin im Betrieb an."""
        luisa = erzeuge_benutzer('luisa')
        self.client.force_login(luisa)
        with mock.patch.dict(os.environ, {'ADMIN_USERNAME': 'luisa'}):
            self.assertEqual(self.hole('/shop-admin/stats/').status_code, 200)
        with mock.patch.dict(os.environ, {'ADMIN_USERNAME': 'jemand-anderes'}):
            self.assertEqual(self.hole('/shop-admin/stats/').status_code, 302)


class ZustandsaenderungNurPerPostTest(LuviqTestCase):
    """Zustandsändernde Adressen reagieren nur auf POST (Beim Kunden Nr. 10, EIG85).

    Früher hielt diese Klasse die GET-Lücke aus ``01-BEFUND.md`` 6.1 (2) als
    Ist-Zustand fest („``GetLueckeHeutigerStandTest``“): ein Kommentar wurde durch
    den blossen Aufruf seiner Lösch-Adresse gelöscht, ein Produkt durch den
    Aufruf der Toggle-Adresse umgeschaltet, ein Newsletter durch den Aufruf der
    Resend-Adresse verschickt. GET ist von der CSRF-Prüfung ausgenommen; ein
    ``<img src="…/delete/">`` auf einer fremden Seite genügte. Seit der Umstellung
    (POST-Pflicht, ``<form>`` mit CSRF-Token statt ``<a>``) ist das Soll
    festgehalten: GET verändert **nichts**, POST tut es.
    """

    def setUp(self):
        self.besitzerin = User.objects.create_superuser(
            'shopbesitzer', 'shop@example.invalid', 'ein-langes-testpasswort'
        )
        self.produkt = erzeuge_produkt('Bemalte Jacke')

    def test_ein_get_aufruf_loescht_keinen_kommentar_ein_post_schon(self):
        kundin = erzeuge_benutzer('kundin')
        kommentar = Comment.objects.create(user=kundin, text='Tolle Jacke!')
        self.client.force_login(kundin)

        antwort = self.hole(f'/comment/{kommentar.id}/delete/')
        self.assertEqual(antwort.status_code, 302)
        self.assertTrue(Comment.objects.filter(pk=kommentar.pk).exists())

        antwort = self.sende(f'/comment/{kommentar.id}/delete/')
        self.assertEqual(antwort.status_code, 302)
        self.assertFalse(Comment.objects.filter(pk=kommentar.pk).exists())

    def test_ein_get_aufruf_schaltet_kein_produkt_um_ein_post_schon(self):
        self.client.force_login(self.besitzerin)

        self.hole(f'/shop-admin/produkte/{self.produkt.id}/toggle/')
        self.produkt.refresh_from_db()
        self.assertTrue(self.produkt.aktiv)

        self.sende(f'/shop-admin/produkte/{self.produkt.id}/toggle/')
        self.produkt.refresh_from_db()
        self.assertFalse(self.produkt.aktiv)

    def test_ein_get_aufruf_verschickt_keinen_newsletter_und_setzt_nichts_zurueck(self):
        Subscriber.objects.create(email='abo@example.invalid', bestaetigt=True)
        # Unbestaetigte Adressen bekommen nichts (Double-Opt-in, 17.09.2026).
        Subscriber.objects.create(email='offen@example.invalid')
        self.client.force_login(self.besitzerin)

        with mock.patch(_NEWSLETTER) as newsletter:
            self.hole(f'/shop-admin/produkte/{self.produkt.id}/resend-newsletter/')
            self.hole(f'/shop-admin/produkte/{self.produkt.id}/resend-newsletter/')
        newsletter.assert_not_called()
        self.produkt.refresh_from_db()
        self.assertFalse(self.produkt.newsletter_gesendet)

        with mock.patch(_NEWSLETTER) as newsletter:
            self.sende(f'/shop-admin/produkte/{self.produkt.id}/resend-newsletter/')
            self.sende(f'/shop-admin/produkte/{self.produkt.id}/resend-newsletter/')
        self.assertEqual(newsletter.call_count, 2)
        empfaenger = [s.email for s in newsletter.call_args.args[1]]
        self.assertEqual(empfaenger, ['abo@example.invalid'])
        self.produkt.refresh_from_db()
        self.assertTrue(self.produkt.newsletter_gesendet)

        # Zurücksetzen: ebenfalls nur per POST.
        self.hole(f'/shop-admin/produkte/{self.produkt.id}/reset-newsletter/')
        self.produkt.refresh_from_db()
        self.assertTrue(self.produkt.newsletter_gesendet)
        self.sende(f'/shop-admin/produkte/{self.produkt.id}/reset-newsletter/')
        self.produkt.refresh_from_db()
        self.assertFalse(self.produkt.newsletter_gesendet)

    def test_ein_get_aufruf_veraendert_keinen_gaestebuch_like_ein_post_schon(self):
        kundin = erzeuge_benutzer('kundin')
        kommentar = Comment.objects.create(user=kundin, text='Tolle Jacke!')
        self.client.force_login(kundin)

        self.hole(f'/comment/{kommentar.id}/like/')
        self.assertEqual(kommentar.likes.count(), 0)

        self.sende(f'/comment/{kommentar.id}/like/')
        self.assertEqual(kommentar.likes.count(), 1)

    def test_die_seiten_bieten_formulare_mit_csrf_token_statt_links_an(self):
        """Verhindert, dass ein Template wieder einen ``<a href>`` auf eine
        zustandsändernde Adresse setzt – dann liefe der Knopf ins Leere (GET
        verändert nichts mehr) oder jemand baut die Lücke wieder ein."""
        kundin = erzeuge_benutzer('kundin')
        kommentar = Comment.objects.create(user=kundin, text='Tolle Jacke!')
        self.client.force_login(kundin)
        seite = self.hole('/gaestebuch/').content.decode()
        self.assertNotIn(f'href="/comment/{kommentar.id}/like/"', seite)
        self.assertNotIn(f'href="/comment/{kommentar.id}/delete/"', seite)
        self.assertIn(f'action="/comment/{kommentar.id}/like/"', seite)
        self.assertIn(f'action="/comment/{kommentar.id}/delete/"', seite)
        self.assertIn('csrfmiddlewaretoken', seite)

        self.client.force_login(self.besitzerin)
        seite = self.hole('/shop-admin/produkte/').content.decode()
        for name in ('toggle', 'resend-newsletter'):
            adresse = f'/shop-admin/produkte/{self.produkt.id}/{name}/'
            self.assertNotIn(f'href="{adresse}"', seite)
            self.assertIn(f'action="{adresse}"', seite)

    def test_ein_post_ohne_csrf_token_wird_abgewiesen(self):
        """Gegenprobe zur Umstellung: der POST ist nur dann ein Schutz, wenn
        Django das Token auch prüft. Ein Client, der die Prüfung nicht
        umgeht, bekommt 403."""
        from django.test import Client
        kundin = erzeuge_benutzer('kundin')
        kommentar = Comment.objects.create(user=kundin, text='Tolle Jacke!')
        strenger = Client(enforce_csrf_checks=True)
        strenger.force_login(kundin)
        antwort = strenger.post(f'/comment/{kommentar.id}/delete/', secure=True)
        self.assertEqual(antwort.status_code, 403)
        self.assertTrue(Comment.objects.filter(pk=kommentar.pk).exists())


class GaestebuchMeldungTest(LuviqTestCase):
    """Die Erfolgsmeldung nach einem Beitrag ist öffentlich sichtbar. Sie trug
    bis 02.10.2026 den Bildsprachen-Rest „im Orbit“ der früheren Linie."""

    def test_die_meldung_nach_einem_beitrag_ist_klartext_ohne_orbit(self):
        from django.contrib.messages import get_messages

        kundin = erzeuge_benutzer('kundin')
        self.client.force_login(kundin)
        antwort = self.sende('/comment/add/', {'text': 'Schöne Stücke!'})
        self.assertEqual(antwort.status_code, 302)
        self.assertTrue(Comment.objects.filter(user=kundin, text='Schöne Stücke!').exists())
        meldungen = [str(m) for m in get_messages(antwort.wsgi_request)]
        self.assertEqual(meldungen, ['Dein Beitrag wurde veröffentlicht.'])
        self.assertNotIn('Orbit', ' '.join(meldungen))
