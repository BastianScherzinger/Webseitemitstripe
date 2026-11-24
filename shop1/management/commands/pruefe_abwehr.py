"""Prüfbefehl für die Spam-Abwehr der Formulare – in beide Richtungen.

Eine Abwehr lässt sich in eine Richtung leicht verschärfen: Schwelle runter, und kein Bot
kommt mehr durch. Die Kosten stehen auf der anderen Seite und fallen nie auf, weil eine
abgewiesene echte Anfrage niemandem fehlt – sie kommt einfach nicht an. Deshalb prüft
dieser Befehl beide Richtungen mit denselben Zahlen aus ``shop1/spamschutz.py``:

* **Bot-Fälle** müssen die Schwelle erreichen (Honigtopf, Gewinnspiel mit Link, fremde
  Domain mit dem Markennamen, Linkliste in fremder Schrift).
* **Mensch-Fälle** müssen durchkommen – auch die unbequemen: ohne JavaScript (kein
  Zeitstempel), mit der eigenen Seite im Text, mit einem Instagram-Link, in
  Großbuchstaben, aus einem Tab von gestern, mit der eigenen Domain dieser Seite.
* Die **Mail-Obergrenze** lässt genau so viele Mails durch, wie eingestellt ist, und
  keine mehr.
* Seit 24.11.2026 die **Dienstleistungs-Angebote**: Verkaufsschreiben (SEO, Video, Webdesign …)
  in elf Sprachen müssen als Angebot erkannt und in ihrer Sprache beantwortet werden; Kundinnen,
  auch solche, die nach einem Video oder Foto des Stücks fragen, dürfen nie als Angebot gelten.

Der Lauf schreibt nichts: kein Formular wird abgeschickt, keine Mail verschickt, nichts
gespeichert; die Zähler der Obergrenze laufen unter einem eigenen Namen.

    python manage.py pruefe_abwehr

Rückgabe: Fehler (Exitcode 1), wenn ein Mensch geblockt oder ein Bot durchgelassen würde.
"""

import time

from django.core.management.base import BaseCommand, CommandError

from shop1 import spamschutz

_MENSCH_TEXT = 'Hallo Luisa, ich hätte gern eine Jacke mit einem Drachen auf dem Rücken. Geht das bis Dezember?'


def _daten(jetzt, *, name='Anna Müller', email='anna@gmail.com', betreff='Frage zu einem Motiv',
           nachricht=_MENSCH_TEXT, alter=60, zeit=True, **zusatz):
    """POST-Daten eines Formulars, das vor ``alter`` Sekunden angezeigt wurde."""
    daten = {'name': name, 'email': email, 'betreff': betreff, 'nachricht': nachricht}
    if zeit:
        from django.core import signing
        daten[spamschutz.FELD_ZEIT] = signing.dumps(int(jetzt - alter), salt=spamschutz._SALZ)
    daten.update(zusatz)
    return daten


def faelle(jetzt=None):
    """``[(Bezeichnung, daten, soll_geblockt)]`` – die Fälle dieses Befehls."""
    jetzt = time.time() if jetzt is None else jetzt
    return [
        # ── Bots: müssen die Schwelle erreichen ──
        ('Bot: Gewinnspiel mit telegra.ph-Link (Vorfall 16.09.2026)',
         _daten(jetzt, name='RobertBoobe', betreff='THE LAMBORGHINI AVENTADOR SWEEPSTAKES CLOSES SOON',
                nachricht='You are a snap away from an Lamborghini Aventador https://telegra.ph/Win-today',
                alter=1), True),
        ('Bot: Honigtopf ausgefüllt, sonst harmlos',
         _daten(jetzt, **{spamschutz.FELD_FALLE: 'https://x.example'}), True),
        ('Bot: Honigtopf unter dem alten Namen „webseite“',
         _daten(jetzt, **{spamschutz.FELD_FALLE_ALT: 'https://x.example'}), True),
        ('Bot: fremde Domain mit dem Markennamen als Absender',
         _daten(jetzt, email='domains@search-luviq-alsfeld.xyz'), True),
        ('Bot: fremde Domain mit dem Markennamen im Text, nackt geschrieben',
         _daten(jetzt, nachricht='Ihr Eintrag läuft ab, verlängern unter luviq-alsfeld-shop.pro bitte.'), True),
        ('Bot: Linkliste in kyrillischer Schrift',
         _daten(jetzt, name='Иван', nachricht='Перевод руб. http://a.example http://b.example http://c.example',
                alter=1), True),
        # ── Bots der Logs vom 24.11.2026 ──
        ('Bot: Preisfrage-Vorlage mit Lücken im Betreff und Satz in Zufallssprache',
         _daten(jetzt, name='Robertstady', email='joshuaguerrero2v7t40d@gmail.com',
                betreff='Hi    write about your the price for reseller',
                nachricht='Sveiki, aš norėjau sužinoti jūsų kainą.'), True),
        ('Bot: Zahlenmuster in Name, Betreff und Text mit Wegwerf-Adresse',
         _daten(jetzt, name='NARTYTRYUT2173457NEWETREWT', email='abbey46901@belettersmail.com',
                betreff='TOTUTYJ2173457TIRTYRTTR', nachricht='MERTYHRTHYHT2173457MARTHHDF'), True),
        ('Bot: Tastaturgeklapper mit der eigenen Domain am Ende',
         _daten(jetzt, name='Michaelprove', email='ingeiiv7braun@mail.com',
                betreff='Mnfuhfiejfuwduqwdhuwdwuhdu huwfqwuhfbqwihqwife',
                nachricht='Jfeuwgduwefhw fuhefyugewfhqwyfuewu uwqduiqwhfqefhwduhwfe uwhidwdfefue luviq-luebeck.com'),
         True),
        # ── Menschen: müssen durchkommen ──
        ('Mensch: kurz „Ist Nº 006 noch frei?“', _daten(jetzt, name='Jana', betreff='Frage',
                                                        nachricht='Ist Nº 006 noch frei?'), False),
        ('Mensch: englisch, mit Instagram-Link, fragt nach dem Engel-Shirt',
         _daten(jetzt, name='Maya Stone', email='maya@example.com', betreff='Engel shirt',
                nachricht='Hi! I found you on instagram (https://instagram.com/maya.stone). Is the engel shirt still '
                          'available in size M and do you ship to Austria?'), False),
        ('Mensch: fragt nach dem Preis (ohne Vorlagen-Lücken)',
         _daten(jetzt, betreff='Preis für das Engel-Shirt', nachricht='Ich schreibe wegen des Preises vom Shirt.'),
         False),
        ('Mensch: fragt nach einem Video vom Stück',
         _daten(jetzt, betreff='Video vom Hoodie?',
                nachricht='Hallo Luisa, kannst du mir ein kurzes Video oder Foto vom Hoodie schicken, damit ich '
                          'die Farbe in echt sehen kann?'), False),
        ('Mensch: lange Wörter und Fachbegriffe, deutsch',
         _daten(jetzt, nachricht='Ich interessiere mich für Weihnachtsgeschenke, Kapuzenpullover und eine '
                                 'Übergangsjacke; Nachhaltigkeit und Handarbeit sind mir wichtig.'), False),
        ('Mensch: polnisch', _daten(jetzt, name='Kasia', email='kasia@wp.pl', betreff='Pytanie',
                                    nachricht='Dzień dobry, chciałabym zapytać czy kurtka jest jeszcze dostępna '
                                              'oraz ile kosztuje wysyłka do Polski. Dziękuję.'), False),
        ('Mensch: normale Anfrage', _daten(jetzt), False),
        ('Mensch: ohne JavaScript, also ohne Zeitstempel', _daten(jetzt, zeit=False), False),
        ('Mensch: nennt die eigene Seite ohne http (nackte Domain)',
         _daten(jetzt, nachricht='So etwas wie auf meinshop.de hätte ich gern, nur mit einem Drachen.'), False),
        ('Mensch: verweist auf ein Instagram-Bild',
         _daten(jetzt, nachricht='So eine Jacke wie hier: https://instagram.com/p/abc – geht das?'), False),
        ('Mensch: schreibt von der eigenen Domain dieser Seite',
         _daten(jetzt, email='luisa@luviq-alsfeld.com', nachricht='Test von www.luviq-alsfeld.com aus.'), False),
        ('Mensch: schreibt die Marke ohne Domain',
         _daten(jetzt, nachricht='Ich folge Luviq schon lange und möchte ein eigenes Stück.'), False),
        ('Mensch: in Großbuchstaben getippt',
         _daten(jetzt, nachricht='HALLO, ICH BRAUCHE DIE JACKE BIS ZUM ERSTEN ADVENT, GEHT DAS?'), False),
        ('Mensch: Tab von gestern (25 Stunden alt) bei einer normalen Anfrage',
         _daten(jetzt, alter=25 * 3600), False),
        ('Mensch: sehr schnell (2 Sekunden, Browser-Autofill)', _daten(jetzt, alter=2), False),
    ]


#: Verkaufsschreiben in elf Sprachen: (Sprache, Betreff, Text). Alle müssen als Angebot gelten.
ANGEBOTE = [
    ('de', 'Videos für Ihre Website', 'Hallo, wir erstellen Werbevideos und Reels für Onlineshops. Unser Team '
     'bietet Ihnen ein kostenloses Angebot an, die Preise starten bei 195 Euro. Möchten Sie Beispiele sehen?'),
    ('en', 'Explainer Video for your website?', 'Hi, I just visited your site and wondered if you have considered '
     'an impactful video to advertise your business? Our prices start from $195. Let me know if you want to see '
     'samples of our previous work.'),
    ('en', 'Let\'s Boost Your Website Traffic', 'Hello http://luviq-luebeck.com, I hope you are doing well. We '
     'specialize in SEO strategies. Send me your target keywords and market, I will send over a complete proposal.'),
    ('fr', 'Vidéo pour votre site', 'Bonjour, nous créons des vidéos publicitaires et des reels pour les boutiques '
     'en ligne. Notre équipe vous propose un devis gratuit, nos prix commencent à 195 euros. Voulez-vous voir des '
     'exemples ?'),
    ('es', 'Vídeo para su web', 'Hola, nosotros creamos vídeos publicitarios y reels para tiendas online. Nuestro '
     'equipo le ofrece un presupuesto gratis y los precios empiezan en 195 euros. Le gustaría ver ejemplos de '
     'nuestro trabajo?'),
    ('it', 'Video per il vostro sito', 'Buongiorno, noi creiamo video pubblicitari e reel per negozi online. Il '
     'nostro team vi offre un preventivo gratuito, i prezzi partono da 195 euro. Volete vedere degli esempi del '
     'nostro lavoro?'),
    ('nl', 'Video voor uw website', 'Hallo, wij maken reclamevideo\'s en reels voor webshops. Ons team bieden wij u '
     'een gratis offerte aan, onze prijzen beginnen bij 195 euro. Wilt u voorbeelden van ons werk zien?'),
    ('pt', 'Vídeo para o seu site', 'Olá, nós criamos vídeos publicitários e reels para lojas online. A nossa '
     'equipa oferece um orçamento grátis e os nossos preços começam em 195 euros. Gostaria de ver exemplos do '
     'nosso trabalho?'),
    ('pl', 'Film promocyjny dla Twojej strony', 'Dzień dobry, tworzymy filmy reklamowe i reels dla sklepów '
     'internetowych. Nasz zespół oferujemy bezpłatną wycenę, ceny zaczynają się od 195 euro. Czy chcą Państwo '
     'zobaczyć przykłady naszych prac?'),
    ('tr', 'Web siteniz için video', 'Merhaba, online mağazalar için reklam videoları ve reels hazırlıyoruz. '
     'Ekibimiz size ücretsiz teklif sunuyoruz, fiyatlarımız 195 euro ile başlıyor. Çalışmalarımızdan örnekler '
     'görmek ister misiniz?'),
    ('ru', 'Видео для вашего сайта', 'Здравствуйте! Мы создаём рекламные видео и reels для интернет-магазинов. '
     'Наша команда предлагает бесплатный расчёт, цены от 195 евро. Хотите посмотреть примеры наших работ?'),
    ('uk', 'Відео для вашого сайту', 'Вітаємо! Ми створюємо рекламні відео та reels для інтернет-магазинів. '
     'Наша команда пропонує безкоштовний розрахунок, ціни від 195 євро. Хочете побачити приклади наших робіт?'),
]

#: Kundinnen und andere echte Schreiben: dürfen nie als Angebot gelten (Betreff, Text).
KEINE_ANGEBOTE = [
    ('Ist Nº 006 noch frei?', 'Hallo, ist Nº 006 noch frei? Viele Grüße Jana'),
    ('Video vom Hoodie?', 'Hallo Luisa, kannst du mir ein kurzes Video oder Foto von der Jacke schicken, damit '
     'ich die Farbe sehen kann? Danke!'),
    ('Reel', 'Hi, ich bin Influencerin und folge euch seit langem. Hättet ihr Lust auf eine Kooperation? Ich würde '
     'ein Stück tragen und ein Reel dazu machen.'),
    ('Wholesale', 'Hello, I run a small shop and would like to buy your jackets. Do you have a price list and '
     'shipping to Austria?'),
    ('Question', 'Hello, I love your handmade shirt. Is the engel shirt still available? Could you do a video '
     'call to show it?'),
    ('Fotografin', 'Hi, ich bin Fotografin und mache Videos für kleine Labels. Ich würde die Stücke gern bei einem '
     'Shooting tragen, Größe M. Mein Insta: https://instagram.com/foto.anna'),
]


class Command(BaseCommand):
    """``python manage.py pruefe_abwehr``: Fälle aus ``faelle()`` gegen ``spamschutz.bewerte``, dazu die Mail-Obergrenze."""
    help = 'Prüft die Spam-Abwehr der Formulare in beide Richtungen (Bots geblockt, Menschen nicht).'

    def handle(self, *args, **optionen):
        jetzt = time.time()
        fehler = []
        self.stdout.write(f'Schwelle: {spamschutz.SCHWELLE} Punkte\n')
        for bezeichnung, daten, soll_geblockt in faelle(jetzt):
            punkte, gruende = spamschutz.bewerte(daten, jetzt)
            geblockt = punkte >= spamschutz.SCHWELLE
            ok = geblockt == soll_geblockt
            marke = 'OK    ' if ok else 'FEHLER'
            self.stdout.write(f'  {marke} {punkte:>2} Punkte  {bezeichnung}'
                              + (f'  [{", ".join(gruende)}]' if gruende else ''))
            if not ok:
                fehler.append(bezeichnung + (' – ein Mensch würde abgewiesen' if geblockt
                                             else ' – ein Bot käme durch'))

        # Dienstleistungs-Angebote: erkannt und in der richtigen Sprache beantwortet – und Kundinnen nie.
        from shop1 import angebote
        for kuerzel, betreff, text in ANGEBOTE:
            erkannt = angebote.ist_angebot('', betreff, text)
            erkannte_sprache = angebote.sprache(f'{betreff} {text}')
            ok = erkannt and erkannte_sprache == kuerzel and kuerzel in angebote.ABSAGEN
            self.stdout.write(f'  {"OK    " if ok else "FEHLER"}    Angebot ({kuerzel}) erkannt: {erkannt}, '
                              f'Sprache der Absage: {erkannte_sprache}')
            if not ok:
                fehler.append(f'Angebot in {kuerzel} nicht richtig behandelt (erkannt={erkannt}, '
                              f'Sprache={erkannte_sprache})')
        for betreff, text in KEINE_ANGEBOTE:
            erkannt = angebote.ist_angebot('', betreff, text)
            self.stdout.write(f'  {"FEHLER" if erkannt else "OK    "}    Mensch: „{betreff}“ gilt '
                              f'{"als Angebot" if erkannt else "nicht als Angebot"}')
            if erkannt:
                fehler.append(f'Mensch-Fall „{betreff}“ würde als Angebot abgesagt')

        # Mail-Obergrenze: genau ``stunde`` Mails durch, die nächste nicht.
        art = f'pruefung-{int(jetzt)}'
        stunde = 3
        durch = sum(1 for _ in range(stunde + 2)
                    if spamschutz.mail_budget_ok(art, stunde=stunde, tag=100))
        ok = durch == stunde
        self.stdout.write(f'  {"OK    " if ok else "FEHLER"}    Mail-Obergrenze: {durch} von {stunde + 2} '
                          f'Versuchen durchgelassen (Soll {stunde})')
        if not ok:
            fehler.append(f'Mail-Obergrenze lässt {durch} statt {stunde} Mails durch')

        self.stdout.write(
            f'\nEingestellt: höchstens {spamschutz.MAIL_OBERGRENZE_STUNDE} Mails je Stunde und '
            f'{spamschutz.MAIL_OBERGRENZE_TAG} je Tag und Formular (je Gunicorn-Prozess).')
        self.stdout.write('Eigene Domains (nie als Nachahmer gewertet): '
                          + ', '.join(sorted(spamschutz.eigene_domains())))
        if fehler:
            raise CommandError('Spam-Abwehr fehlerhaft:\n  - ' + '\n  - '.join(fehler))
        self.stdout.write(self.style.SUCCESS('\nSpam-Abwehr in beide Richtungen in Ordnung.'))
