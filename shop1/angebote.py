"""Dienstleistungs-Angebote im Kontaktformular erkennen und freundlich absagen (24.11.2026).

Anlass: Von 37 gespeicherten Kontaktnachrichten (17.09. bis 24.11.2026) war keine einzige eine
Kundenanfrage. Gut ein Viertel waren Verkaufsschreiben von Agenturen – „Let's Boost Your Website
Traffic“, „Explainer Video for your website?“, „SEO Improvements Identified …“. Sie sind kein Bot-Müll,
sondern Menschen oder Vorlagen, die eine Antwort erwarten. Sie gehen **nicht** an Luisa; stattdessen
bekommt der Absender **eine** kurze, freundliche Absage in seiner Sprache.

Drei Sicherungen gegen Fehlgriffe, in dieser Reihenfolge ihrer Wichtigkeit:

1. **Falsch-Positive sind teurer als durchgelassener Spam.** Ein Text gilt nur als Angebot, wenn er
   ein Dienstleistungs-Stichwort (Video, SEO, Webdesign, Marketing, Ads, Influencer, App …) **und** ein
   Anbieter-Satzmuster („we offer“, „I can create“, „our prices start“, „wir bieten“ …) enthält – oder
   mindestens zwei Anbieter-Satzmuster. Nennt der Text dagegen ein Stück, eine Größe, eine Bestellung oder
   Luviq-Wörter (Nº 006, Jacke, Hoodie, Versand …), ist es eine Kundin und geht wie bisher an Luisa.
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
    r'\bseo\b|\baeo\b|\bsem\b|search engine|suchmaschin|google (?:1st|first|top|page|ranking|rank)|'
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

#: Anbieter-Satzmuster: wer so schreibt, verkauft etwas.
_ANGEBOT = re.compile(
    r'\bwe (?:offer|provide|specialize|specialise|create|make|produce|can (?:place|help|make|create|offer|give|boost|improve|rank|get))\b|'
    r'\bi (?:can|could) (?:give|offer|prepare|provide|create|make|place|boost|improve|rank|help you|send you (?:a|our|the) (?:proposal|quote|audit|samples?|screenshot))|'
    r'\bi (?:may|will) send you\b|\bi (?:would|\'d) like to offer\b|\bour (?:services?|prices?|pricing|team|videos?|packages?|clients?|agency|experts?|work)\b|'
    r'\bprices? start|\bstarting (?:at|from) \$?[€£$]?\s?\d|\bproposal\b|\bpricing\b|\bprice list\b|\bquote\b|'
    r'\bfree (?:audit|quote|sample|consultation|report|trial)\b|\bsamples? of our\b|\bprevious work\b|\bportfolio\b|'
    r'\bi (?:just )?(?:visited|came across|found|noticed|reviewed|checked) (?:your|a few|some|the)?\s*(?:business|website|site|page|store|shop)|'
    r'\b(?:send|share) (?:me )?your (?:target )?keywords\b|\btarget (?:keywords|market)\b|'
    r'\byour (?:google )?(?:visibility|rankings?|online presence)\b|\bwould you like (?:me|us) to send\b|'
    r'\bwe can place your website\b|'
    # de
    r'\bwir (?:bieten|erstellen|produzieren|machen|helfen|k[oö]nnen|spezialisieren)\b|\bich (?:biete|erstelle|produziere|k[oö]nnte|kann)\b.{0,60}\b(?:an|f[uü]r sie|f[uü]r euch|f[uü]r ihr)\b|'
    r'\bunser (?:angebot|team|service|leistungen?)\b|\bunsere (?:leistungen|preise|referenzen)\b|\bkostenlos(?:e|er|es)? (?:analyse|angebot|beratung|erstgespr)|'
    r'\bpreis(?:liste| ab)\b|\bangebot (?:f[uü]r|zu) (?:ihre|eure|deine)\b|\bmehr (?:kunden|reichweite|sichtbarkeit|anfragen)\b|'
    # fr / es / it / nl / pt / pl / tr / ru / uk
    r'\bnous (?:proposons|offrons|cr[ée]ons|r[ée]alisons)\b|\bnotre (?:agence|[ée]quipe|offre)\b|\bofrecemos\b|\bcreamos\b|\bnuestro (?:equipo|servicio)\b|'
    r'\bofferiamo\b|\bcreiamo\b|\bil nostro (?:team|servizio)\b|\bwij (?:bieden|maken|verzorgen)\b|\bons (?:team|aanbod)\b|'
    r'\boferecemos\b|\bcriamos\b|\bnossa (?:equipe|ag[êe]ncia)\b|\boferujemy\b|\btworzymy\b|\bnasz zesp[óo][łl]\b|'
    r'\bsunuyoruz\b|\bhizmet(?:imiz|lerimiz)\b|\bekibimiz\b|'
    r'мы (?:предлагаем|создаём|создаем|делаем|занимаемся)|наша (?:компания|команда|студия)|наши (?:услуги|цены)|'
    r'ми (?:пропонуємо|створюємо|робимо|займаємося)|наша (?:команда|студія)|наші (?:послуги|ціни)', re.I)

#: Wer das schreibt, meint Luviq und seine Stücke: nie als Angebot behandeln.
_KUNDE = re.compile(
    r'n[º°o]\s?\.?\s?\d{2,4}\b|\bnummer\s?\d|\barchiv\s?nummer|\bst[üu]ck\b|\bst[üu]cke\b|\bunikat|\bjacke\b|\bshirt|\bhoodie|'
    r'\bpullover|\bpulli\b|\bhose\b|\bjeans\b|\bkleid\b|\bmantel\b|\bweste\b|\bjacket\b|\bsweater\b|\bsize\s+(?:xs|s|m|l|xl|xxl|\d{2})\b|\bin size\b|\bgr[öo](?:ß|ss)e\b|'
    r'\bbestell|\border(?:ed|ing)?\b|\bversand|\bshipping|\bliefer|\bdelivery|\bretoure|\br[üu]cksendung|\bwiderruf|\brefund|'
    r'\bnoch (?:frei|verf[üu]gbar|da)\b|\bstill available\b|\bavailable\b|\bverf[üu]gbar|\breserv|\banprobe|\bpassform|'
    r'\bmotiv\b|\bengel\b|\bupcycl|\bbleach|\bgebleicht|\bluisa\b|\bluviq\.archive|\binstagram\.com/|\bkaufen\b|\bbuy\b|'
    r'\bstorno|\brechnung\b|\binvoice\b|\bpaket\b|\bpackage\b.{0,20}\b(?:arrived|received|angekommen)|\bdhl\b', re.I)


def ist_angebot(name='', betreff='', nachricht=''):
    """``True``, wenn das Schreiben ein Dienstleistungs-Angebot an Luviq ist (siehe Kopf des Moduls).

    Im Zweifel ``False``: dann geht die Nachricht normal an Luisa."""
    text = ' '.join((betreff or '', nachricht or ''))
    if len(text.strip()) < 25:
        return False
    if _KUNDE.search(text):
        return False
    muster = {m.group(0).lower() for m in _ANGEBOT.finditer(text)}
    dienst = _DIENST.search(text) is not None
    if dienst and muster:
        return True
    # Ohne Stichwort braucht es klar mehr als einen Zufallstreffer.
    return len(muster) >= 3


# ─── Sprache ────────────────────────────────────────────────────────────────

_WOERTER = {
    'de': r'\b(?:und|der|die|das|nicht|ich|wir|sie|ihre?|ihren|mit|f[üu]r|ist|sind|haben|wollen|k[öo]nnen|auf|eine?|dass|auch|bei|oder|mehr|hallo|guten|sehr|geehrte)\b',
    'en': r'\b(?:the|and|you|your|we|our|with|for|are|have|can|that|this|from|will|would|like|hello|hi|please|regards|about|more|if)\b',
    'fr': r'\b(?:le|la|les|des|une?|et|vous|votre|nous|notre|pour|avec|est|sont|bonjour|cordialement|sur|dans|que|qui|je|nos|vos)\b',
    'es': r'\b(?:el|los|las|una?|y|usted|su|sus|nosotros|nuestro|para|con|es|son|hola|saludos|en|que|por|m[áa]s|sitio|p[áa]gina)\b',
    'it': r'\b(?:il|lo|gli|le|una?|e|voi|vostro|vostra|noi|nostro|per|con|[èe]|sono|ciao|buongiorno|cordiali|saluti|che|del|della|sul|sito)\b',
    'nl': r'\b(?:de|het|een|en|u|uw|wij|ons|onze|voor|met|is|zijn|hallo|goedendag|groeten|van|dat|ook|naar|website)\b',
    'pt': r'\b(?:o|os|as|um|uma|e|voc[êe]|seu|sua|n[óo]s|nosso|nossa|para|com|[ée]|s[ãa]o|ol[áa]|obrigado|atenciosamente|do|da|no|na|que)\b',
    'pl': r'\b(?:i|oraz|nie|jest|s[aą]|dla|na|do|z|si[ęe]|pa[nń]stwa|dzie[nń] dobry|witam|pozdrawiam|ofert|strona|strony|mo[żz]emy|nasz|nasza)\b',
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
    if wertung[beste] < 4:
        return 'en'
    return beste


# ─── Absage ─────────────────────────────────────────────────────────────────

# Je Sprache (Betreff, Text). Keine Namen, keine Links, keine Werbung. Deutsch im Luviq-Du-Stil.
ABSAGEN = {
    'de': ('Danke für dein Angebot',
           'Hallo,\n\ndanke für dein Angebot – wir brauchen gerade keine Unterstützung bei Videos, Marketing '
           'oder Webseiten und melden uns deshalb nicht weiter dazu.\n\nViele Grüße\nLuviq'),
    'en': ('Thank you for your offer',
           'Hello,\n\nthank you for your offer – we do not need any help with videos, marketing or websites '
           'right now, so we will not follow up on this.\n\nBest wishes\nLuviq'),
    'fr': ('Merci pour votre proposition',
           'Bonjour,\n\nmerci pour votre proposition – nous n\'avons pas besoin d\'aide pour les vidéos, le '
           'marketing ou les sites web en ce moment et ne donnerons donc pas de suite.\n\nCordialement\nLuviq'),
    'es': ('Gracias por tu propuesta',
           'Hola,\n\ngracias por tu propuesta – ahora mismo no necesitamos ayuda con vídeos, marketing o '
           'páginas web, así que no responderemos más sobre este tema.\n\nUn saludo\nLuviq'),
    'it': ('Grazie per la tua proposta',
           'Ciao,\n\ngrazie per la tua proposta – al momento non abbiamo bisogno di supporto per video, '
           'marketing o siti web e quindi non daremo seguito.\n\nCordiali saluti\nLuviq'),
    'nl': ('Bedankt voor je aanbod',
           'Hallo,\n\nbedankt voor je aanbod – we hebben op dit moment geen hulp nodig bij video\'s, marketing '
           'of websites en komen er daarom niet meer op terug.\n\nGroeten\nLuviq'),
    'pt': ('Obrigado pela sua proposta',
           'Olá,\n\nobrigado pela sua proposta – de momento não precisamos de apoio com vídeos, marketing ou '
           'sites e, por isso, não voltaremos a responder sobre este assunto.\n\nCumprimentos\nLuviq'),
    'pl': ('Dziękujemy za ofertę',
           'Dzień dobry,\n\ndziękujemy za ofertę – obecnie nie potrzebujemy wsparcia przy filmach, marketingu '
           'ani stronach internetowych, dlatego nie będziemy już w tej sprawie odpisywać.\n\nPozdrawiamy\nLuviq'),
    'tr': ('Teklifiniz için teşekkürler',
           'Merhaba,\n\nteklifiniz için teşekkür ederiz – şu anda video, pazarlama veya web sitesi konusunda '
           'desteğe ihtiyacımız yok, bu yüzden bu konuda tekrar dönüş yapmayacağız.\n\nSevgiler\nLuviq'),
    'ru': ('Спасибо за ваше предложение',
           'Здравствуйте!\n\nСпасибо за ваше предложение. Сейчас нам не нужна помощь с видео, маркетингом '
           'или сайтами, поэтому мы не будем отвечать на него дальше.\n\nВсего доброго\nLuviq'),
    'uk': ('Дякуємо за вашу пропозицію',
           'Вітаємо!\n\nДякуємо за вашу пропозицію. Зараз нам не потрібна допомога з відео, маркетингом '
           'або сайтами, тому ми не відповідатимемо на неї далі.\n\nГарного дня\nLuviq'),
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
        send_brevo_email(betreff, absage_html(text), anfrage.email, recipient_name='', text_content=text,
                         auto_antwort=True)
        _log.info('Angebot abgesagt (%s) an eine Absenderadresse', kuerzel)
        return True
    except Exception:
        _log.exception('Absage nicht gestartet')
        return False
