"""Vorschau der gestalteten Mails mit Beispieldaten – verschickt nichts.

    python tools/mailvorschau.py <zielordner>

Schreibt ``admin-kontakt.html``, ``admin-motiv.html`` (Mails an Luisa),
``bastian.html`` (Kopie an die Webagentur, Kontaktanfrage),
``bastian-motiv.html``, ``bastian-registrierung.html`` und
``kunde.html`` / ``kunde-newsletter.html`` (Konto bzw. Newsletter bestätigen)
– ``admin.html`` ist eine Kopie von ``admin-kontakt.html``.
Braucht eine ``.env`` wie jeder ``manage.py``-Befehl.
"""

import os
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mainweb.settings')

import django  # noqa: E402

django.setup()

from shop1 import mails  # noqa: E402

LANG = ('Hallo Luisa,\n\nich habe deine bemalten Jacken auf Instagram gesehen und bin begeistert. '
        'Gibt es die Jeansjacke mit dem Fuchs auch in Größe M? Meine Schwester hat im Mai Geburtstag, '
        'und ich würde ihr gern etwas Einzigartiges schenken – etwas mit Möwen oder Wellen, weil sie '
        'an der Ostsee wohnt.\n\nWäre das grundsätzlich möglich? Ich freue mich über eine Rückmeldung.\n\n'
        'Viele Grüße\nJürgen Übermut <script>alert("x")</script>')


def main(ziel):
    ziel = Path(ziel)
    ziel.mkdir(parents=True, exist_ok=True)
    objekt = SimpleNamespace(pk=42, _meta=SimpleNamespace(app_label='shop1', model_name='kontaktanfrage'))
    kontakt = [('Name', 'Jürgen Übermut'), ('E-Mail', 'juergen@example.invalid', 'mail'),
               ('Betreff', 'Frage zur Fuchs-Jacke in Größe M')]
    _, html, _ = mails.anfrage_an_luisa(
        art='Kontaktanfrage', betreff='Kontaktformular: Frage zur Fuchs-Jacke in Größe M', felder=kontakt,
        text='…', antwort_an='juergen@example.invalid', langtext_titel='Nachricht', langtext=LANG, objekt=objekt)
    (ziel / 'admin-kontakt.html').write_text(html, encoding='utf-8')
    (ziel / 'admin.html').write_text(html, encoding='utf-8')

    motiv_obj = SimpleNamespace(pk=7, _meta=SimpleNamespace(app_label='shop1', model_name='motivanfrage'))
    motiv = [('Richtung', 'Tier'), ('Teil', 'Hoodie'), ('Wo', 'Rücken'),
             ('Instagram', '@erika.muster', 'insta'), ('E-Mail', 'erika@example.invalid', 'mail')]
    bedeutung = 'Ein Drache für meinen Bruder, eher verspielt als böse.\nGern in Grün- und Kupfertönen.'
    _, html, _ = mails.anfrage_an_luisa(
        art='Motivanfrage', betreff='Motivanfrage: Tier auf Hoodie', felder=motiv, text='…',
        antwort_an='erika@example.invalid', langtext_titel='Was es bedeuten soll', langtext=bedeutung,
        objekt=motiv_obj, hinweis='Alle Anfragen stehen im Admin-Panel unter „Motivanfragen".')
    (ziel / 'admin-motiv.html').write_text(html, encoding='utf-8')

    gefangen = {}
    original = mails.send_brevo_email
    mails.send_brevo_email = lambda betreff, html, *a, **k: gefangen.setdefault('html', html)
    try:
        for datei, kwargs in (
            ('bastian.html', dict(art='Kontaktanfrage', name='Jürgen Übermut', felder=kontakt,
                                  antwort_an='juergen@example.invalid', langtext_titel='Nachricht',
                                  langtext=LANG, objekt=objekt, admin_mail=True)),
            ('bastian-motiv.html', dict(art='Motivanfrage', name='@erika.muster', felder=motiv,
                                        antwort_an='erika@example.invalid',
                                        langtext_titel='Was es bedeuten soll', langtext=bedeutung,
                                        objekt=motiv_obj, admin_mail=True)),
            ('bastian-registrierung.html', dict(
                art='Registrierung', name='neukundin',
                felder=[('Benutzername', 'neukundin'), ('E-Mail', 'neu@example.invalid', 'mail')],
                objekt=SimpleNamespace(pk=3, _meta=SimpleNamespace(app_label='auth', model_name='user')),
                admin_mail=None, kunden_mail='Bestätigungslink an die Adresse angestoßen')),
        ):
            gefangen.clear()
            with _env(BETREIBER_KOPIE_AN='vorschau@example.invalid'):
                mails.betreiber_kopie(**kwargs)
            (ziel / datei).write_text(gefangen['html'], encoding='utf-8')
    finally:
        mails.send_brevo_email = original

    link = mails.live_url() + '/verify/0f1e2d3c-beispiel/'
    (ziel / 'kunde.html').write_text(mails.rendern(
        'besucher.html', titel='Bitte bestätige deine E-Mail-Adresse', kopf_label='Konto',
        preheader='Ein Klick, dann ist dein Konto bei Luviq Universe bestätigt.',
        absaetze=['danke, dass du dich bei Luviq Universe registriert hast. Bitte bestätige '
                  'deine E-Mail-Adresse mit einem Klick:'],
        link=link, knopf='E-Mail bestätigen',
        nachsatz='Hast du dich nicht registriert? Dann ignoriere diese E-Mail einfach.'), encoding='utf-8')
    (ziel / 'kunde-newsletter.html').write_text(mails.rendern(
        'besucher.html', titel='Bitte bestätige deine Anmeldung', kopf_label='Newsletter',
        preheader='Ein Klick, dann bekommst du Post, wenn es Neues von Luviq gibt.',
        absaetze=['für diese Adresse wurde der Luviq-Newsletter angemeldet. Bitte bestätige '
                  'das mit einem Klick:'],
        link=mails.live_url() + '/newsletter/bestaetigen/?t=beispiel', knopf='Anmeldung bestätigen',
        nachsatz='Warst du das nicht, ignoriere diese E-Mail einfach – ohne Bestätigung '
                 'schicken wir dir nichts.'), encoding='utf-8')
    print(f'Vorschau geschrieben nach {ziel}')


class _env:
    def __init__(self, **werte):
        self.werte, self.alt = werte, {}

    def __enter__(self):
        for k, v in self.werte.items():
            self.alt[k] = os.environ.get(k)
            os.environ[k] = v

    def __exit__(self, *_):
        for k, v in self.alt.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
