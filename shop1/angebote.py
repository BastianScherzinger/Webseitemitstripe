"""Dienstleistungs-Angebote im Kontaktformular erkennen und freundlich absagen (24.11.2026).

Anlass: Von 37 gespeicherten Kontaktnachrichten (17.09. bis 24.11.2026) war keine einzige eine
Kundenanfrage. Gut ein Viertel waren Verkaufsschreiben von Agenturen – „Let's Boost Your Website
Traffic“, „Explainer Video for your website?“, „SEO Improvements Identified …“. Sie sind kein Bot-Müll,
sondern Menschen oder Vorlagen, die eine Antwort erwarten. Sie gehen **nicht** an Luisa; stattdessen
bekommt der Absender **eine** kurze, freundliche Absage in seiner Sprache.

Drei Sicherungen gegen Fehlgriffe, in dieser Reihenfolge ihrer Wichtigkeit:

1. **Falsch-Positive sind teurer als durchgelassener Spam.** Ein Text gilt nur als Angebot, wenn **drei**
   Dinge zugleich zutreffen: (a) ein Dienst-Stichwort (Video, Reel, UGC, SEO, Marketing, Webdesign, Ads,
   App …), (b) eine Leistung, die sich ausdrücklich an Luviqs Geschäft richtet („for your brand/business/
   shop“, „your sales/traffic/rankings“, „grow your …“, „für dein Unternehmen/deine Reichweite“ …) und
   (c) **kein** Kauf- oder Kundenwort (Nº 006, Jacke, coat, sweatshirt, custom hoodie, Versand, ship, order,
   Schüler, Presse …). Die Kundenwort-Prüfung kommt immer zuerst. Berufsangaben („I'm a designer“, „we
   create“) zählen nie. Einzige Ausnahme: ein ausdrücklicher Tausch („in exchange for a free piece“,
   „gegen ein Stück“) hebt nur die Kundenwort-Sperre auf, Dienst-Stichwort und Ziel brauchen weiterhin beide.
   Im Zweifel geht die Nachricht an Luisa.
2. **Keine Absage an Bots.** Die Absage geht nur, wenn die Punktwertung (``spamschutz``) keinen
   Bot-Hinweis zeigt (Honigtopf, Zeitfalle, Linkflut, Spamwörter, Kauderwelsch, Wegwerf-Adresse …) und die
   Adresse brauchbar ist (keine ``noreply``, keine eigene Domain, keine Wegwerf-Domain).
3. **Höchstens eine Absage je Adresse und 30 Tage, höchstens** ``ABSAGE_TAGESGRENZE`` **je Tag** (beides
   gezählt in der Datenbank, nicht im Cache – übersteht Neustarts und beide Gunicorn-Prozesse).

Die Absage enthält keinen Link, keine Werbung und keinen Text des Absenders (nichts davon wird
übernommen), nur den Satz in der erkannten Sprache. Betreff fest. Kopfzeile ``Auto-Submitted:
auto-replied``, damit Postfächer keine Antwortschleife bauen.

Schalter: ``ABSAGE_AKTIV`` (Vorgabe an; ``aus``/``0``/``false`` = es wird nur eingestuft und gespeichert,
nichts verschickt), ``ABSAGE_TAGESGRENZE`` (Vorgabe 15), ``ABSAGE_PAUSE_TAGE`` (Vorgabe 30).
"""

import logging
import os
import re
import datetime

from django.utils import timezone
from django.utils.html import escape

_log = logging.getLogger('shop1')

TAGESGRENZE_VORGABE = 15
PAUSE_TAGE_VORGABE = 30


# ─── Erkennen ───────────────────────────────────────────────────────────────

#: Wovon das Schreiben handelt: Dienstleistungen, die Luviq nicht braucht.
_DIENST = re.compile(
    r'search index|\bseo\b|\baeo\b|\bsem\b|search engine|suchmaschin|google (?:1st|first|top|page|ranking|rank)|'
    r'\branking|\brankings\b|\bbacklink|\borganic (?:traffic|reach)|website traffic|web ?traffic|'
    r'\bvideos?\b|\bvideo ?(?:production|marketing|ads?|content|promotion)|explainer|\breels?\b|'
    r'\bimage ?film|\bimagefilm|\bwerbefilm|\bwerbevideo|\bvideoproduktion|\bvideograf|\bugc\b|'
    r'\bweb ?design|\bwebdesign|\bwebsite (?:design|redesign|audit|development|review)|'
    r'\bdesign (?:&|and|und) performance|\blanding ?page|\bweb ?entwicklung|\bwebentwicklung|'
    r'\bmarketing\b|\bonline ?marketing|\bonlinemarketing|\bdigital marketing|\bsocial media (?:management|marketing|growth|manager)|'
    r'\bgoogle ads\b|\bfacebook ads\b|\bmeta ads\b|\bppc\b|\badvertis|\bwerbeagentur|\bmarketing ?agentur|'
    r'\binfluencer|\bapp ?(?:development|entwicklung)|\bmobile app\b|\blead ?generation|\bleads\b|'
    r'\bfollowers\b|\bchatbot|\bautomation\b|\bbranding\b|\blogo ?design|'
    # fr / es / it / nl / pt / pl / tr / ru / uk
    r'r[ée]f[ée]rencement|vid[ée]o|agence|posicionamiento|agencia|publicidad|posizionamento|agenzia|'
    r'zoekmachine|bureau voor|reclame|agência|publicidade|pozycjonowani|agencja|reklam|film promocyjny|'
    r'reklam ajans|arama motoru|продвижени|раскрутк|видео|реклам|сайт|сео\b|маркетинг|відео|просуванн|'
    r'розкрутк|рекламн', re.I)

#: (b) Die Leistung richtet sich ausdrücklich an Luviqs Geschäft. Wörter, die auch Kundinnen benutzen (quote,
#: pricing, price list, Preisliste, proposal, portfolio, „ich habe deine Seite gesehen“, „unser Team“,
#: „wir können“) und Berufsangaben („I'm a designer“, „we create“) stehen hier bewusst **nicht**.
_ZIEL = re.compile(
    r'\bfor your (?:brand|business|shop|store|website|company|account|webshop|online ?shop)\b|'
    r'\byour (?:\w+ ){0,2}(?:sales|traffic|rankings?|followers|engagement|online presence|conversions|visibility|'
    r'organic reach|target keywords|keywords)\b|'
    r'\b(?:grow|boost|increase|improve|strengthen) your\b|\brank (?:\w+ ){0,3}(?:on|higher|in) google\b|'
    r'\brank (?:\w+ ){0,3}higher\b|\byour (?:website|site) on google\b|\bgoogle[\'’]?s? search index\b|'
    r'\b(?:reviewed|audited|analy[sz]ed) your (?:website|site)\b|\b(?:issues|errors) (?:on|with) your (?:website|site)\b|'
    r'\b(?:advertise|promote|market) your (?:business|brand|shop|store|company)\b|\bfor your (?:\w+ )?business\b|'
    r'\b(?:videos?|reels?|content|ads|campaigns?) for (?:\w+ )?(?:brands?|businesses|companies|shops|stores|clients)\b|'
    r'\btarget market\b|'
    # de
    r'\bf[uü]r (?:dein|euer|ihr)\w* (?:unternehmen|gesch[aä]ft|shop|marke|website|webseite|firma|label)\b|'
    r'\b(?:deine|eure|ihre) (?:reichweite|ums[aä]tze|sichtbarkeit|rankings?|besucher|follower)\b|'
    r'\bf[uü]r (?:\w+ )?(?:shops|onlineshops|webshops|unternehmen|firmen|marken)\b|'
    r'\bwir bieten\b|\bunsere agentur\b|\bich biete\b|'
    # fr / es / it / nl / pt / pl / tr / ru / uk
    r'\bpour (?:votre|vos|les|des) (?:marque|entreprise|boutiques?|sites?|activit[ée]|commerces?|marques|entreprises)\b|'
    r'\bvotre (?:visibilit[ée]|trafic|r[ée]f[ée]rencement|chiffre d)\w*|\bnous (?:proposons|offrons)\b|\bnotre agence\b|'
    r'\bpara (?:su|tu|sus|tus) (?:marca|negocio|tienda|web|empresa)\b|\bpara (?:tiendas|negocios|empresas|marcas)\b|'
    r'\bofrecemos\b|\bnuestra agencia\b|\bper (?:negozi|aziende|brand|attivit[àa])\b|\bla vostra (?:azienda|attivit[àa]|visibilit[àa]|sito|marca)\b|'
    r'\bofferiamo\b|\bla nostra agenzia\b|\bvoor (?:uw |jouw )?(?:webshops?|bedrijven|merken|winkels|website|bedrijf)\b|'
    r'\bwij (?:bieden|maken)\b|\bpara (?:lojas|empresas|marcas|neg[óo]cios)\b|\bsua (?:marca|empresa|loja)\b|\boferecemos\b|'
    r'\bdla (?:sklep[óo]w|firm|marek|pa[nń]stwa|twojej|twojego)\b|\boferujemy\b|\bnasza agencja\b|'
    r'\b(?:siteniz|i[sş]letmeniz|markan[ıi]z) i[çc]in\b|\bsunuyoruz\b|\bajans[ıi]m[ıi]z\b|'
    r'для (?:вашего|вашей|вашего бизнеса|интернет)|мы (?:предлагаем|занимаемся)|наша (?:компания|студия)|'
    r'для (?:вашого|вашої|інтернет)|ми (?:пропонуємо|займаємося)|наша (?:студія)', re.I)

#: (c) Wer das schreibt, meint Luviq und seine Stücke oder will etwas kaufen: nie als Angebot behandeln.
_KUNDE = re.compile(
    r'n[º°o]\s?\.?\s?\d{2,4}\b|\bnummer\s?\d|\barchiv\s?nummer|\bst[üu]ck(?:e|en)?\b|\bunikat|\bjacke\b|\bshirts?\b|\bt-shirt|\bhoodie|'
    r'\bpullover|\bpulli\b|\bhose\b|\bjeans\b|\bkleid\b|\bmantel\b|\bweste\b|\bjacket\b|\bsweater\b|sweatshirt|\bcoats?\b|'
    r'\bcostumes?\b|\bkost[üu]m|\bcommission\w*|\btrikots?\b|\bsudadera|\bveste\b|\bgiacca\b|\bbluz\w*|'
    r'\bsize\s+(?:xs|s|m|l|xl|xxl|\d{2})\b|\bin size\b|\bgr[öo](?:ß|ss)e\b|\bteil(?:e|en)?\b|\bpieces?\b|\bitems?\b|'
    r'\bbestell|\border(?:s|ed|ing)?\b|\bversand|\bship(?:s|ped|ping)?\b|\bliefer|\bdelivery|\blivr|\bspedizion|'
    r'\bsipari[sş]|\bwysy[łl]|\bretoure|\br[üu]cksendung|\bwiderruf|\brefund|\bnoch (?:frei|verf[üu]gbar|da)\b|'
    r'\bstill available\b|\bavailable\b|\bverf[üu]gbar|\breserv|\banprobe|\bpassform|\bmotiv\b|\bengel\b|\bupcycl|\bbleach|'
    r'\bgebleicht|\bluisa\b|\bluviq\.archive|\binstagram\.com/|\bkaufen\b|\bkupi[ćc]|\bbuy\b|\bpurchase\b|'
    r'\bcustom(?:ized|ised)?[ -](?:\w+ )?(?:coat|jacket|hoodie|shirt|sweatshirt|dress|vest|pants|trousers|jeans|sweater|'
    r'pullover|design|made|order|piece|print)\w*|\bcustom(?:er)?s? (?:order|piece)\w*|\bma[ßs]anfertig|\bgeschenk|\bgift\b|\bmerch\b|\blogo auf\b|'
    r'\barbeitskleidung|\bworkwear|\bsch[üu]ler|\bschule\b|\bklasse\b|\bschool\b|\bstudent\w*|\bstudent(?:in)?\b|\bthesis\b|'
    r'\bpresse\b|\bpress\b|\bmagazin|\bkooperation|\bcollab\w*|\bone like (?:that|this)\b|\bstorno|\brechnung\b|\binvoice\b|'
    r'\bpaket\b|\bdhl\b|\bwhat(?:s|\'s| is) the price\b|\bwas kostet\b|\bhow much\b|\bworkshop\b|\binterview', re.I)

#: Ausdrücklicher Tausch (Creator bietet Video/Reel gegen ein Gratis-Stück): hebt nur die Kundenwort-Sperre
#: auf. Ein beliebiges „free“ oder „kostenlos“ (free shipping, kostenloser Versand) zählt **nicht**.
_TAUSCH = re.compile(
    r'\bin exchange for\b|\bim austausch (?:f[üu]r|gegen)\b|\bgegen (?:ein|einen|eine) (?:kostenlos\w* |gratis )?'
    r'(?:st[üu]ck|teil|shirt|hoodie|jacke|produkt)\b|\bfor (?:a|an) free (?:item|piece|product|shirt|hoodie|jacket)\b|'
    r'\bfor free (?:items?|pieces?|products?)\b', re.I)


def ist_angebot(name='', betreff='', nachricht=''):
    """``True``, wenn jemand Luviq eine Dienstleistung für das eigene Geschäft verkaufen will (siehe Modulkopf).

    Verlangt Dienst-Stichwort **und** Ziel „Luviqs Geschäft“, und kein Kundenwort (die Prüfung kommt zuerst;
    nur ein ausdrücklicher Tausch hebt sie auf). Im Zweifel ``False``: dann geht die Nachricht an Luisa."""
    text = ' '.join((betreff or '', nachricht or ''))
    if len(text.strip()) < 25:
        return False
    if _KUNDE.search(text) and not _TAUSCH.search(text):
        return False
    return _DIENST.search(text) is not None and _ZIEL.search(text) is not None


# ─── Sprache ────────────────────────────────────────────────────────────────

_WOERTER = {
    'de': r'\b(?:und|der|die|das|nicht|ich|wir|sie|ihre?|ihren|mit|f[üu]r|ist|sind|haben|wollen|k[öo]nnen|auf|eine?|dass|auch|bei|oder|mehr|hallo|guten|sehr|geehrte)\b',
    'en': r'\b(?:the|and|you|your|we|our|with|for|are|have|can|that|this|from|will|would|like|hello|hi|please|regards|about|more|if)\b',
    'fr': r'\b(?:le|la|les|des|une?|et|vous|votre|nous|notre|pour|avec|est|sont|bonjour|cordialement|sur|dans|que|qui|je|nos|vos)\b',
    'es': r'\b(?:el|los|las|una?|y|usted|su|sus|nosotros|nuestro|para|con|es|son|hola|saludos|en|que|por|m[áa]s|sitio|p[áa]gina)\b',
    'it': r'\b(?:il|lo|gli|le|una?|e|voi|vostro|vostra|noi|nostro|per|con|[èe]|sono|ciao|buongiorno|cordiali|saluti|che|del|della|sul|sito)\b',
    'nl': r'\b(?:de|het|een|en|u|uw|wij|ons|onze|voor|met|is|zijn|hallo|goedendag|groeten|van|dat|ook|naar|website)\b',
    'pt': r'\b(?:o|os|as|um|uma|e|voc[êe]|seu|sua|n[óo]s|nosso|nossa|para|com|[ée]|s[ãa]o|ol[áa]|obrigado|atenciosamente|do|da|no|na|que)\b',
    'pl': r'\b(?:nie|jest|s[aą]|dla|si[ęe]|oraz|pa[nń]stwa|dzie[nń] dobry|witam|pozdrawiam|oferuj\w+|sklep\w*|strony|mo[żz]emy|nasz\w*|dzi[ęe]kuj\w*|prosz[ęe]|czy)\b',
    'tr': r'\b(?:ve|bir|bu|i[çc]in|ile|sizin|bizim|merhaba|selam|te[şs]ekk[üu]r|de[ğg]erli|web sitesi|olarak|daha|var|sunuyoruz|hizmet)\b',
}
_ZEICHEN = {
    'es': '¿¡ñ', 'pt': 'ãõ', 'pl': 'ąęłńśźż', 'tr': 'ğşı', 'fr': 'œêèàùâî', 'de': 'äöüß',
}


def sprache(text):
    """Sprachkürzel (``de en fr es it nl pt pl tr ru uk``) aus Schrift und Stichwörtern; Rückfall ``en``.

    Ohne Fremdbibliothek. Reicht für die Absage – ein Fehlgriff ergibt eine freundliche Absage in der
    falschen, aber verständlichen Sprache, nie etwas Schlimmeres."""
    text = (text or '')[:3000]
    kyr = len(re.findall('[Ѐ-ӿ]', text))
    lat = len(re.findall('[A-Za-zÀ-ž]', text))
    if kyr and kyr >= lat * 0.5:
        if re.search('[іїєґІЇЄҐ]', text):
            return 'uk'
        return 'ru'
    if re.search('[一-鿿぀-ヿ가-힯]', text) and lat < 20:
        return 'en'
    kleiner = text.lower()
    wertung = {}
    for kuerzel, muster in _WOERTER.items():
        wertung[kuerzel] = len(re.findall(muster, kleiner, re.I)) * 2
    for kuerzel, zeichen in _ZEICHEN.items():
        wertung[kuerzel] = wertung.get(kuerzel, 0) + sum(kleiner.count(z) for z in zeichen) * 3
    # Englisch ist Rückfall und hat viele Kurzwörter, die auch in anderen Sprachen vorkommen.
    wertung['en'] = wertung.get('en', 0) * 0.9
    beste = max(wertung, key=lambda k: wertung[k])
    # Bei Unsicherheit Englisch: eine andere Sprache nur mit klarem Abstand zum Englischen (zwei englische
    # Texte wurden einmal für Polnisch gehalten, weil „i“ und „z“ als polnische Wörter zählten).
    if beste != 'en' and wertung[beste] < wertung['en'] + 4:
        return 'en'
    if wertung[beste] < 4:
        return 'en'
    return beste


# ─── Absage ─────────────────────────────────────────────────────────────────

# Je Sprache (Betreff, Text). Keine Namen, keine Links, keine Werbung. Deutsch im Luviq-Du-Stil.
ABSAGEN = {
    'de': ('Danke für deine Nachricht',
           'Hallo,\n\ndanke für deine Nachricht! Falls du uns eine Dienstleistung anbietest (zum Beispiel Videos, '
           'Marketing oder Webdesign): Das brauchen wir gerade nicht, und wir melden uns dazu nicht weiter.\n\n'
           'Falls du etwas von Luviq möchtest, antworte einfach kurz auf diese Mail, dann meldet sich Luisa '
           'persönlich.\n\nViele Grüße\nLuviq'),
    'en': ('Thank you for your message',
           'Hello,\n\nthank you for your message! If you are offering us a service (for example videos, marketing '
           'or web design): we do not need that right now, and we will not follow up on it.\n\nIf you would like '
           'something from Luviq, simply reply briefly to this email and Luisa will get back to you '
           'personally.\n\nBest wishes\nLuviq'),
    'fr': ('Merci pour votre message',
           'Bonjour,\n\nmerci pour votre message ! Si vous nous proposez un service (par exemple des vidéos, du '
           'marketing ou du web design) : nous n\'en avons pas besoin pour le moment et nous ne donnerons pas '
           'suite.\n\nSi vous souhaitez quelque chose de Luviq, répondez simplement brièvement à cet e-mail, '
           'et Luisa vous répondra personnellement.\n\nCordialement\nLuviq'),
    'es': ('Gracias por tu mensaje',
           'Hola,\n\n¡gracias por tu mensaje! Si nos ofreces un servicio (por ejemplo vídeos, marketing o diseño '
           'web): ahora mismo no lo necesitamos y no responderemos más sobre ello.\n\nSi quieres algo de Luviq, '
           'responde brevemente a este correo y Luisa se pondrá en contacto contigo personalmente.\n\n'
           'Un saludo\nLuviq'),
    'it': ('Grazie per il tuo messaggio',
           'Ciao,\n\ngrazie per il tuo messaggio! Se ci stai proponendo un servizio (ad esempio video, marketing '
           'o web design): al momento non ne abbiamo bisogno e non daremo seguito.\n\nSe desideri qualcosa da '
           'Luviq, rispondi brevemente a questa e-mail e Luisa ti risponderà personalmente.\n\n'
           'Cordiali saluti\nLuviq'),
    'nl': ('Bedankt voor je bericht',
           'Hallo,\n\nbedankt voor je bericht! Als je ons een dienst aanbiedt (bijvoorbeeld video\'s, marketing '
           'of webdesign): die hebben we nu niet nodig en we komen er niet meer op terug.\n\nWil je iets van '
           'Luviq? Antwoord dan kort op deze e-mail, dan neemt Luisa persoonlijk contact met je op.\n\n'
           'Groeten\nLuviq'),
    'pt': ('Obrigado pela sua mensagem',
           'Olá,\n\nobrigado pela sua mensagem! Se está a oferecer-nos um serviço (por exemplo vídeos, marketing '
           'ou web design): de momento não precisamos e não voltaremos a responder sobre isso.\n\nSe quiser '
           'algo da Luviq, responda brevemente a este e-mail e a Luisa entrará em contacto consigo '
           'pessoalmente.\n\nCumprimentos\nLuviq'),
    'pl': ('Dziękujemy za wiadomość',
           'Dzień dobry,\n\ndziękujemy za wiadomość! Jeśli oferują nam Państwo usługę (na przykład filmy, '
           'marketing lub projektowanie stron): obecnie jej nie potrzebujemy i nie będziemy w tej sprawie '
           'odpisywać.\n\nJeśli chcą Państwo czegoś od Luviq, wystarczy krótko odpowiedzieć na tę wiadomość, '
           'a Luisa odpisze osobiście.\n\nPozdrawiamy\nLuviq'),
    'tr': ('Mesajınız için teşekkürler',
           'Merhaba,\n\nmesajınız için teşekkürler! Bize bir hizmet sunuyorsanız (örneğin video, pazarlama veya '
           'web tasarımı): şu anda buna ihtiyacımız yok ve bu konuda tekrar dönüş yapmayacağız.\n\nLuviq\'ten '
           'bir şey istiyorsanız bu e-postayı kısaca yanıtlamanız yeterli, Luisa size kişisel olarak '
           'dönecektir.\n\nSevgiler\nLuviq'),
    'ru': ('Спасибо за ваше сообщение',
           'Здравствуйте!\n\nСпасибо за ваше сообщение! Если вы предлагаете нам услугу (например, видео, '
           'маркетинг или веб-дизайн): сейчас она нам не нужна, и мы не будем отвечать на это дальше.\n\n'
           'Если вам нужно что-то от Luviq, просто коротко ответьте на это письмо, и Луиза ответит вам '
           'лично.\n\nВсего доброго\nLuviq'),
    'uk': ('Дякуємо за ваше повідомлення',
           'Вітаємо!\n\nДякуємо за ваше повідомлення! Якщо ви пропонуєте нам послугу (наприклад, відео, '
           'маркетинг або веб-дизайн): зараз вона нам не потрібна, і ми не відповідатимемо на це далі.\n\n'
           'Якщо вам потрібно щось від Luviq, просто коротко дайте відповідь на цей лист, і Луїза відповість '
           'вам особисто.\n\nГарного дня\nLuviq'),
}

_ROLLEN = ('noreply', 'no-reply', 'donotreply', 'do-not-reply', 'mailer-daemon', 'postmaster', 'bounce',
           'abuse', 'root', 'admin', 'webmaster', 'hostmaster')


def absage_aktiv():
    return (os.getenv('ABSAGE_AKTIV') or 'an').strip().lower() not in ('aus', 'off', '0', 'false', 'nein')


def _zahl(name, vorgabe):
    try:
        return max(0, int(os.getenv(name, vorgabe)))
    except (TypeError, ValueError):
        return vorgabe


def absage_text(kuerzel):
    """``(betreff, text)`` in der Sprache; unbekannt = Englisch."""
    return ABSAGEN.get(kuerzel) or ABSAGEN['en']


def absage_html(text):
    """Schlichte HTML-Fassung der Absage (ein Absatz je Textabsatz, nichts verlinkt)."""
    absaetze = [a for a in text.split('\n\n') if a.strip()]
    koerper = ''.join(f'<p style="margin:0 0 14px">{escape(a).replace(chr(10), "<br>")}</p>' for a in absaetze)
    return ('<div style="font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.5;color:#222">'
            + koerper + '</div>')


def adresse_brauchbar(email, eigene_domains=()):
    """Eine Absage geht nur an eine Adresse, die nach Mensch oder Firma aussieht."""
    email = (email or '').strip().lower()
    if email.count('@') != 1 or ' ' in email:
        return False
    lokal, domain = email.split('@')
    if not lokal or '.' not in domain:
        return False
    if lokal in _ROLLEN or lokal.startswith(('noreply', 'no-reply', 'donotreply')):
        return False
    from .spamschutz import wegwerf_adresse
    if wegwerf_adresse(email):
        return False
    if any(domain == d or domain.endswith('.' + d) for d in eigene_domains):
        return False
    return True


#: Hinweise der Punktwertung, bei denen **nie** geantwortet wird (Bot, Flut, Fälschung).
KEINE_ANTWORT = frozenset({
    'falle', 'zu-schnell', 'zeit-gefaelscht', 'links', 'link-im-kopf', 'spamwort', 'fremdschrift-link',
    'kauderwelsch', 'wegwerf-mail', 'preis-bot', 'zahlenmuster', 'markenimitation', 'name-zusammen',
    'ohne-zeit', 'wiederholung',
})


def darf_absage(email, gruende, eigene_domains=()):
    """``(ok, warum_nicht)`` – Schalter, Bot-Hinweise, Adresse, Pause je Adresse, Tagesgrenze."""
    from .models import KontaktAnfrage
    if not absage_aktiv():
        return False, 'schalter-aus'
    if KEINE_ANTWORT.intersection(gruende):
        return False, 'bot-hinweis'
    if not adresse_brauchbar(email, eigene_domains):
        return False, 'adresse'
    jetzt = timezone.now()
    pause = datetime.timedelta(days=_zahl('ABSAGE_PAUSE_TAGE', PAUSE_TAGE_VORGABE))
    if KontaktAnfrage.objects.filter(email__iexact=email.strip(), absage_am__gte=jetzt - pause).exists():
        return False, 'pause'
    tag = datetime.timedelta(days=1)
    if KontaktAnfrage.objects.filter(absage_am__gte=jetzt - tag).count() >= _zahl(
            'ABSAGE_TAGESGRENZE', TAGESGRENZE_VORGABE):
        return False, 'tagesgrenze'
    return True, ''


def antwort_adresse():
    """Reply-To der Absage: Luisas Adresse (``ADMIN_EMAIL``, sonst ``DEFAULT_FROM_EMAIL``)."""
    from django.conf import settings
    return os.getenv('ADMIN_EMAIL') or settings.DEFAULT_FROM_EMAIL


def absage_senden(anfrage, text_fuer_sprache):
    """Schickt die Absage und trägt Zeit und Sprache an der gespeicherten Anfrage ein.

    Wirft nie. ``True``, wenn der Versand angestoßen ist. Der Eintrag steht **vor** dem Versand
    (zählt für Pause und Tagesgrenze auch, wenn der Versand scheitert – lieber eine Absage zu wenig)."""
    from .models import KontaktAnfrage
    from .utils import send_brevo_email
    try:
        kuerzel = sprache(text_fuer_sprache)
        betreff, text = absage_text(kuerzel)
        KontaktAnfrage.objects.filter(pk=anfrage.pk).update(absage_am=timezone.now(), absage_sprache=kuerzel)
        # Rückweg: Absender (From) ist Luisas Postfach (DEFAULT_FROM_EMAIL), und Reply-To zeigt ausdrücklich
        # auf dieselbe Adresse wie die Mails an sie (ADMIN_EMAIL) – eine Antwort landet bei Luisa.
        send_brevo_email(betreff, absage_html(text), anfrage.email, recipient_name='', text_content=text,
                         reply_to=antwort_adresse(), auto_antwort=True)
        _log.info('Angebot abgesagt (%s) an eine Absenderadresse', kuerzel)
        return True
    except Exception:
        _log.exception('Absage nicht gestartet')
        return False
