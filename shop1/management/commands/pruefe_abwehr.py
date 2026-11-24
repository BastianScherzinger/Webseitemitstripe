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
    ('de', 'Videos für Ihre Website', 'Hallo, wir bieten Werbevideos und Reels für Onlineshops an. Unsere Agentur '
     'macht ein kostenloses Erstgespräch, die Preise starten bei 195 Euro. Möchten Sie Beispiele sehen?'),
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


#: Kundinnen-Nachrichten, die die erste Fassung fälschlich als Angebot abgesagt hätte (Abnahme 24.11.2026):
#: Kundenwörter wie quote, price list, Preisliste, „ich habe dein Reel gesehen“ lösen nie ein Angebot aus.
KUNDINNEN_REGRESSION = [
 ('Instagram', 'Hi, I noticed your shop on Instagram, love your videos! Do you ship to the UK?'),
 ('Reels Preisliste', 'Hi, I saw your reels. Could you share your price list?'),
 ('Reel gleiche', 'Hey, saw your reel!! can i get one like that? whats the price list'),
 ('Seite gefunden', 'Hey I came across your page on Instagram and I love your videos. Can you make one for me? Please send me a quote'),
 ('Quote', 'Hi, could you send me a quote and your pricing? Happy to get a proposal for a custom design.'),
 ('Video gesehn', 'hallo, hab das video gesehn, was kostet die preisliste ab 50 euro?'),
 ('Marketing-Kram', 'Hallo Luisa, meine Freundin mag Marketing-Kram nicht, sie hätte gern was Ruhiges zum Geburtstag. Habt ihr eine Preisliste?'),
 ('Firmenlogo', 'Hallo, könnt ihr unser Firmenlogo (Branding für unser Team) auf Arbeitskleidung bringen? Wir können 20 Teile abnehmen.'),
 ('Schulklasse', 'Hallo, wir sind eine 10. Klasse und machen ein Video über nachhaltige Mode für ein Schulprojekt. Unser Team sind 4 Schüler, dürfen wir euch ein paar Fragen stellen?'),
 ('K1', 'Hello! I run a small boutique and would love to feature your hoodie in our marketing newsletter. Could you send your portfolio and a price list?'),
 ('K2', 'Hallo, ich suche ein Geschenk. Kannst du mir ein kurzes Video vom Stück schicken? Danke!'),
 ('K3', 'Hi, do you do custom designs? I would like a jacket with my dog on it. What would the pricing be?'),
 ('K4', 'Guten Tag, wir sind ein Verein und möchten 15 Hoodies mit Logo bedrucken lassen. Bitte um ein Angebot mit Preisliste.'),
 ('K5', 'Hey, I saw your reel on Instagram about the bleached jacket. Is it still available and what is the quote for shipping to Canada?'),
 ('K6', 'Hallo Luisa, ich arbeite bei einer Zeitung und würde gern über euer Upcycling-Label berichten. Hättet ihr Zeit für ein Interview? Gern auch per Video.'),
 ('K7', 'Hi! Love your brand. I do photography as a hobby, could I take photos of the pieces for you and pay for the shirt myself? Let me know the pricing.'),
 ('K8', 'Hi, I am a student and need a video for a school project about slow fashion. Can I interview you? Our team has 3 members.'),
 ('K9', 'Hello, we are planning a marketing event in Hamburg and would love to have your pieces at our pop-up. Can you send a proposal for the booth costs?'),
 ('K10', 'Moin, ich habe euer Reel gesehen und finde die Jacke mega. Gibt es sie auch in L? Was ist der Preis?'),
 ('K11', 'Hello, I came across your website while looking for a gift for my sister. Do you have a price list and do you ship to Austria?'),
 ('K12', 'Hi Luisa, my brand needs branding merch for our team of 12. Can you make hoodies with our logo? Please send a quote.'),
 ('K13', 'Hey, ich bin Fotografin und würde gern ein Shooting mit deinen Stücken machen, Größe M. Hast du Interesse an einer Kooperation?'),
]

#: Ein Creator bietet ein Video gegen ein Gratis-Stück an: ein Video-Angebot, also Absage.
CREATOR_ANGEBOTE = [
 ('C1', 'Collab: UGC video for a free piece', "Hi, I'm a UGC creator with 20k followers. I can make a reel and a TikTok video of your hoodie in exchange for a free piece."),
]

#: Die echten Verkaufsschreiben aus der Produktion (gekürzt, ohne Namen und Adressen), müssen erkannt werden.
ECHTE_ANGEBOTE = [
 ('Robin', 'Question about your Google visibility', 'Hello, The way people search online is changing. Along with Google, more people are using AI platforms. We offer a combined SEO + AEO strategy to improve visibility across Google, voice search. If youd like to strengthen your online presence, we would be happy to share our service proposal and pricing.'),
 ('Valentina', 'Let’s Boost Your Website Traffic', 'Hello http://luviq-luebeck.com, We can place your website on Google 1st page. I can give you our Complete SEO Action Plan along with a customary reach and add great value to your product/ service. I may send you a SEO Packages & price list. If interested. Best Regards, Valentina Online SEO Consultant'),
 ('Marco', 'Design & Performance Review for luviq-luebeck.com', 'Hello luviq-luebeck.com, I noticed a few design-related issues on your website luviq-luebeck.com that could impact its performance and user experience. Would you like me to send a screenshot highlighting these errors? I can also prepare a detailed audit report, along with a proposal and pricing to improve your website’s design and optimize its ranking.'),
 ('Juliana', 'Let’s Boost Your Website Traffic', 'Hello http://luviq-luebeck.com, I hope you’re doing well. I found your business online and believe there’s potential to increase your search rankings and organic traffic. We specialize in practical SEO strategies designed for sustainable growth. Send me your target keywords and market,I’ll send over a complete proposal . Warm regards, Juliana Digital Marketing Expert'),
 ('Rose', 'Let’s Boost Your Website Traffic', 'Hello http://luviq-luebeck.com, I hope you’re doing well. I came across your business online and thought you might be interested in improving your visibility and traffic on search engines. We specialize in helping businesses strengthen their online presence through effective SEO strategies. Once you share your target keywords and target market, I’ll send a full proposal.'),
 ('Joanna', 'Explainer Video for your website?', "Hi, I just visited luviq-luebeck.com and wondered if you've ever considered an impactful video to advertise your business? Our videos can generate impressive results on both your website and across social media. Our prices start from just $195 (USD) / £145. Let me know if you're interested in seeing samples of our previous work. Regards, Joanna"),
 ('Joanna alt', 'Video Promotion for your website', "Hi, I just visited luviq-alsfeld.com and wondered if you've ever considered an impactful video to advertise your business? Our videos can generate impressive results on both your website and across social media."),
 ('Jase', 'SEO Improvements Identified for Your Website luviq-alsfeld.com', 'Hello, I recently reviewed your website luviq-alsfeld.com and noticed a few SEO-related issues that may be affecting your Google rankings, website traffic, and overall online visibility. Would you like me to send details?'),
 ('Marylin', 'Results for luviq-alsfeld.com', "Hi Feature luviq-alsfeld.com in Google's Search Index to be visible in Google search results! List luviq-alsfeld.com here: indexhelp.pro"),
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
        for name, text in KUNDINNEN_REGRESSION:
            erkannt = angebote.ist_angebot('', name, text)
            self.stdout.write(f'  {"FEHLER" if erkannt else "OK    "}    Mensch: Kundin „{name}“ gilt '
                              f'{"als Angebot" if erkannt else "nicht als Angebot"}')
            if erkannt:
                fehler.append(f'Kundin „{name}“ würde als Angebot abgesagt')
        for name, betreff, text in CREATOR_ANGEBOTE + ECHTE_ANGEBOTE:
            erkannt = angebote.ist_angebot('', betreff, text)
            self.stdout.write(f'  {"OK    " if erkannt else "FEHLER"}    Angebot „{name}“ erkannt: {erkannt}')
            if not erkannt:
                fehler.append(f'Angebot „{name}“ nicht erkannt')
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
