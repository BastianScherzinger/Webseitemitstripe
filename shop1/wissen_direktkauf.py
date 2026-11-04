"""Texte des Beitrags „Wie bestelle und bezahle ich bei Luviq Universe?“ für den Direktkauf ohne Konto.

Stand 04.11.2026 (Zahlung per Revolut-Zahlungslink). Gilt nur, wenn ``verkauf.direktkauf_aktiv()`` wahr ist; sonst bleibt
``wissen/bestellen.html`` bei seinem bisherigen Text (Konto, Warenkorb, PayPal).

Eine Quelle, zwei Orte: Dieselbe Liste speist das FAQ-Schema im ``<head>`` und die sichtbaren
Abschnitte (``<h2>`` = Frage, erster Absatz = Antwort). So laufen beide nicht auseinander
(``test_geo`` verlangt Wortgleichheit). Jede Sachangabe stammt aus ``views/direktkauf.py``,
``luviq_daten.py`` (Frist, Reservierung, Versand) oder den AGB (§§ 2 bis 6).

Die Sachangaben kommen aus ``luviq_daten`` und nicht aus einer Abschrift; der zweite Absatz
("mehr") ist vertrauenswürdiges HTML mit Verweisen und wird in der Vorlage mit ``|safe`` ausgegeben.
"""

from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from . import luviq_daten


def _link(name, text, **zusatz):
    return format_html('<a href="{}"{}>{}</a>', reverse(name), mark_safe(zusatz.get('attr', '')), text)


def rabatt_faq(code):
    """FAQ-Eintrag zum öffentlichen Rabattcode (``rabatt.oeffentlicher_code``); Fragen wie „Luviq Rabattcode“ oder
    „Gutschein erste Bestellung“ sollen in Suche und KI-Antworten eine wörtliche Antwort finden."""
    erst = ' auf deine erste Bestellung' if code.nur_erstbestellung else ''
    bis = f' Der Code gilt bis {code.gueltig_bis:%d.%m.%Y}.' if code.gueltig_bis else ''
    return {
        'frage': 'Gibt es einen Rabattcode für die erste Bestellung?',
        'antwort': (f'Ja. Mit dem Code {code.code} bekommst du {code.prozent} Prozent{erst} bei Luviq Universe. Du trägst '
                    'ihn im Bestellformular auf der Seite des Stücks ins Feld „Rabattcode“ ein und tippst auf „Einlösen“; '
                    'der Knopf „Jetzt bestellen“ oben auf der Startseite trägt ihn automatisch ein. Der Abzug steht vor '
                    f'dem Absenden im Gesamtpreis, und die Rechnung lautet auf den reduzierten Betrag.{bis}'),
        'mehr': format_html(
            'Ein Code für die erste Bestellung gilt nur, wenn es unter deiner E-Mail-Adresse und deiner Lieferanschrift '
            'noch keine Bestellung gibt; stornierte Bestellungen zählen nicht. Je Bestellung gilt ein Code, er wird nicht '
            'ausgezahlt. Die Bedingungen stehen in § 3 der {}.', _link('agb', 'AGB', attr='')),
    }


def bestellen_faq(code=None, engel_url=''):
    """Fragen und Antworten des Bestellbeitrags: Liste aus ``{'frage', 'antwort', 'mehr'}``.

    ``code``: öffentlicher Rabattcode oder ``None``; mit Code kommt eine Frage dazu (nach „Wie bezahle ich“)."""
    tage = luviq_daten.RESERVIERUNG_TAGE
    z = luviq_daten.ZAHLUNG
    rechnung = luviq_daten.RECHNUNG_FRIST
    frist = luviq_daten.VERSAND['lieferfrist_werktage']
    produkte = _link('produkte', 'Übersicht')
    liste = [
        {
            'frage': 'Brauche ich ein Konto, um bei Luviq Universe zu bestellen?',
            'antwort': ('Nein. Bestellt wird direkt auf der Seite des Stücks, ohne Konto und ohne Passwort: '
                        'Du gibst deinen Namen, deine E-Mail-Adresse und die Lieferanschrift an, mehr braucht es nicht. '
                        'Einen Warenkorb gibt es nicht; jedes Stück wird einzeln bestellt.'),
            'mehr': format_html(
                'Ein Konto mit Benutzername und Passwort gibt es nur für das {}. Was der Shop bei einer Bestellung '
                'speichert, steht im Beitrag {} in diesem Wissensbereich und in der {}.',
                _link('gaestebuch', 'Gästebuch'), _link('wissen_konto', 'Was speichert der Shop – und brauche ich ein Konto?'),
                _link('datenschutz', 'Datenschutzerklärung')),
        },
        {
            'frage': 'Wie bestelle ich ein Stück?',
            'antwort': ('Auf der Übersicht ein Stück öffnen. Auf seiner Seite steht unter den Bildern der Bereich '
                        '„Direkt bestellen“; der Knopf „Direkt kaufen“ springt dorthin. Dort das Formular ausfüllen und '
                        '„Zahlungspflichtig bestellen“ wählen. Am Handy zeigt eine Leiste am unteren Rand „Direkt kaufen“, '
                        'solange das Formular nicht im Bild ist.'),
            'mehr': format_html(
                'Die {} zeigt jedes verfügbare Stück mit Preis. Ein Stück, das dort nicht mehr auftaucht, ist verkauft '
                '– Luviq legt kein Motiv ein zweites Mal auf.', produkte)
            + (format_html(' Das <a href="{}">Engel-Shirt</a> ist das aktuelle Stück zum direkten Bestellen.', engel_url)
               if engel_url else ''),
        },
        {
            'frage': 'Welche Angaben verlangt die Bestellung?',
            'antwort': ('Pflicht sind Vor- und Nachname und E-Mail-Adresse, außerdem der Haken für AGB, Widerrufsbelehrung '
                        'und Datenschutzerklärung. Für den Versand kommen Straße mit Hausnummer, Postleitzahl und Ort dazu; '
                        f'wer die Übergabe in {luviq_daten.ABHOLUNG["ort"]} nach Absprache wählt, gibt keine Anschrift an. '
                        'Die Telefonnummer ist freiwillig und dient nur Rückfragen zur Lieferung.'),
            'mehr': ('Die E-Mail-Adresse ist wichtig, weil alles darüber läuft: Eingangsbestätigung, Rechnung und Zahlungslink gehen '
                     'an diese Adresse. Tippfehler daher vor dem Absenden prüfen.'),
        },
        {
            'frage': 'Wann ist das Stück für mich reserviert?',
            'antwort': ('Sobald du die Bestellung abgeschickt hast. Ein zweiter Besucher sieht das Stück dann als '
                        '„reserviert“ und kann es nicht bestellen. Die Reservierung endet, wenn Luisa Brehler keine Rechnung '
                        f'schickt oder die Zahlung nicht innerhalb von {tage} Tagen nach Rechnungsdatum eingeht.'),
            'mehr': ('Wird das Stück wieder frei, nimmt Luisa Brehler die Freigabe von Hand vor; sie geschieht nicht '
                     'automatisch. Ein reserviertes Stück ist bis dahin für andere gesperrt.'),
        },
        {
            'frage': 'Wann kommt der Kaufvertrag zustande?',
            'antwort': ('Mit „Zahlungspflichtig bestellen“ gibst du ein verbindliches Angebot ab (§ 2 der AGB). Direkt danach '
                        'bekommst du eine Eingangsbestätigung per E-Mail; sie ist noch keine Annahme. Luisa Brehler nimmt '
                        'dein Angebot an, indem sie dir die Rechnung mit dem Zahlungslink per E-Mail schickt, und damit kommt '
                        'der Vertrag zustande. Schickt sie keine Rechnung, kommt kein Vertrag zustande, und die Reservierung endet.'),
            'mehr': format_html(
                'Mit der Eingangsbestätigung kommen die AGB und die Widerrufsbelehrung samt Muster-Widerrufsformular per E-Mail. '
                'Das Widerrufsrecht von vierzehn Tagen gilt für Einzelstücke genauso wie für Serienware, die Frist steht in '
                '<a href="https://www.gesetze-im-internet.de/bgb/__355.html" target="_blank" rel="noopener">§ 355 BGB</a>; '
                'was das im Alltag bedeutet, steht im Beitrag {}. Bis zur vollständigen Bezahlung bleibt die Ware nach § 6 '
                'der AGB Eigentum von Luisa Brehler.', _link('wissen_widerruf', 'Widerruf und Rücksendung')),
        },
        {
            'frage': 'Wie bezahle ich meine Bestellung?',
            'antwort': (f'Im Voraus, mit einem persönlichen Zahlungslink von {z["anbieter"]}: Rechnung und Zahlungslink kommen '
                        f'innerhalb von {rechnung} per E-Mail, und auf der Bezahlseite von {z["anbieter"]} zahlst du mit {z["wege"]}. '
                        'Alternativ kannst du auf das Konto überweisen, das in der Rechnung steht. Bitte zahle '
                        f'innerhalb von {tage} Tagen nach Rechnungsdatum. Weitere Zahlungsarten gibt es derzeit '
                        'nicht. Alle Preise sind Endpreise, nach § 19 UStG wird keine Umsatzsteuer berechnet.'),
            'mehr': (f'Eine Zahlung nach der Lieferung, per Lastschrift oder bei Abholung gibt es nicht. Die Zahlungsdaten gibst du '
                     f'nur auf der Bezahlseite von {z["anbieter"]} ein; der Shop sieht und speichert sie nicht. Wer Rechnung und '
                     'Link nicht findet, schaut zuerst im Spam-Ordner und schreibt sonst kurz über das Kontaktformular.'),
        },
        {
            'frage': 'Was passiert nach der Zahlung?',
            'antwort': ('Versendet wird nach Zahlungseingang (§ 4 der AGB). Ein Serienstück wie das Engel-Shirt malt Luisa Brehler '
                        'jetzt für dich von Hand; ein Einzelstück ist dann verkauft und kommt nicht zurück in die Übersicht, ein '
                        'Motiv wird nicht zweimal gemalt.'),
            'mehr': format_html(
                'Kommt die Rechnung oder später die Sendung nicht wie erwartet, hilft eine kurze Nachricht über das {}.',
                _link('kontakt', 'Kontaktformular')),
        },
        {
            'frage': 'Wie lange dauert der Versand?',
            'antwort': (f'Geliefert wird innerhalb von {frist} Werktagen, nur innerhalb Deutschlands; die Frist läuft '
                        f'{luviq_daten.FRIST_BEGINN}. Der Versand innerhalb Deutschlands '
                        'ist im Preis enthalten. Einen Laden zum Anprobieren gibt es nicht; wer in Lübeck wohnt, kann die '
                        'Übergabe nach Absprache wählen.'),
            'mehr': format_html(
                'Woher Luviq kommt und wo die Stücke heute entstehen, steht unter {}. Auf den angezeigten Preis schlägt der '
                'Shop keinen Versandbetrag auf.', _link('liefergebiet', 'Versand & Abholung')),
        },
        {
            'frage': 'Was passiert, wenn ich nicht zahle oder es mir anders überlege?',
            'antwort': ('Geht die Zahlung nicht rechtzeitig ein, kann Luisa Brehler dich per E-Mail erinnern und eine Nachfrist '
                        'von 7 Tagen setzen; danach kann sie vom Vertrag zurücktreten, und das Stück wird wieder frei (§ 4 der AGB). '
                        'Wer die Bestellung nicht ausführen möchte, gibt am besten kurz über das Kontaktformular Bescheid.'),
            'mehr': ('Das gesetzliche Widerrufsrecht von vierzehn Tagen bleibt davon unberührt. Ein Umtausch in eine andere '
                     'Größe ist bei einem Einzelstück nicht möglich.'),
        },
    ]
    if code is not None:
        stelle = next(i for i, f in enumerate(liste) if f['frage'].startswith('Wie bezahle ich')) + 1
        liste.insert(stelle, rabatt_faq(code))
    return liste
