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

#: (b) Verkäufer-Formeln aus der Kaltakquise. Jede Zeile ist EINE Formel (ein Treffer in der Zeile = 1). Ein Angebot
#: braucht mindestens ``MIN_FORMELN`` verschiedene. Breite Wendungen („für dein Geschäft“, „deine Reichweite“) sind
#: bewusst kein Signal mehr: die benutzen Kundinnen auch.
FORMELN = (
    # en
    r"let me know if (?:you['’]?re|you are) interested|\binterested in (?:a|our|the)\b|\bwould you be interested\b",
    r"\b(?:schedule|book|hop on|jump on|set up|arrange) (?:a|an) (?:quick |short |brief |free |15[- ]minute )?(?:call|chat|meeting|demo)\b|"
    r"\b(?:quick|short|brief) (?:call|chat)\b",
    r"\bfree (?:audit|consultation|trial|sample|quote for your|report|analysis|seo|proposal|demo|mockup)\b",
    r"\bour (?:clients|customers|services|team of|portfolio|agency|creators|packages|experts|case stud)",
    r"\bwe (?:help|helped|specialize|specialise|offer|provide|produce|create|build|grow|can (?:build|boost|help|grow|get|rank|improve|increase)|are (?:an?|available)|work with)\b",
    r"\b(?:i|we) (?:specialize|specialise)\b|\bi['’]m an? (?:freelance|independent|professional)\b|\bi can (?:rebuild|build|boost|help|rank|improve|increase|grow|create|make)\b",
    r"\bhire me\b|\bif (?:you['’]?re|you are) not interested\b|\breply (?:yes|with)\b|\bunsubscribe\b",
    r"\b(?:rates|prices|packages|plans) (?:start|from)\b|\bstarting (?:at|from) [$€£]?\d|\bat a (?:low|great|special|competitive) price\b|\baffordable (?:price|rate)s?\b",
    r"\b(?:boost|increase|improve|grow|skyrocket|double) your (?:\w+ ){0,2}(?:sales|traffic|rankings?|followers|engagement|conversions|visibility|revenue|reach|online presence)\b|"
    r"\byour (?:site|website|shop|store|business) (?:could|can|would|needs?|is hurting|is invisible|is not|isn['’]t)\b|\bhurting your\b|\bwant more (?:followers|traffic|sales|clients|customers)\b",
    r"\b(?:reviewed|audited|analy[sz]ed) (?:\w+ ){0,3}(?:your|that your) (?:website|site|shop|store)\b|\bfound \d+ (?:seo )?(?:issues|errors|problems)\b|"
    r"\bcan i send you (?:a|an|our|the)\b|\bsend you (?:a|our) (?:free )?(?:report|proposal|quote|sample|portfolio|offer)\b",
    r"\b(?:new|more) (?:clients|leads|customers)\b|\bguarantee[d]? (?:results|rankings?|traffic|sales|followers|first page)\b|\bfirst page (?:of|on) google\b|\bpage (?:1|one) (?:of|on) google\b|\bhigh[- ]converting\b|\b\d+ (?:real |organic )?followers in\b",
    # de
    r"\bwir (?:sind eine|bieten|erstellen|steigern|betreuen|drehen|produzieren|helfen|bringen|k[öo]nnen auch|haben (?:uns|bereits)|arbeiten mit)\b|\bwir sind (?:eine|ein) (?:\w+ ){0,2}(?:agentur|firma|unternehmen|team|studio)\b|\bunsere (?:agentur|kunden|leistungen|dienstleistung\w*|referenzen|pakete)\b|\bich biete\b|\bich bin (?:freiberuflich|selbst[äa]ndig)\w*|\bals (?:\w+-)?agentur\b",
    r"\bunverbindlich(?:es|e|en)? (?:angebot|gespr[äa]ch|beratung|analyse)\b|\bkostenlos(?:e|en|er)? (?:analyse|beratung|erstgespr[äa]ch|audit|test|probe|muster|bericht)\b|\b(?:darf|d[üu]rfte) ich (?:dir|ihnen|euch) (?:unser|ein|mal)\b|\bwann passt (?:ein|ihnen|dir)\b|\b(?:kurzes|kurzen|kurz) (?:telefonat|gespr[äa]ch|call)\b|\bstehen (?:wir|ich) gern(?:e)? zur verf[üu]gung\b",
    r"\b(?:auf|bringen (?:sie|dich|euch) auf) seite (?:1|eins)\b|\b(?:deine|ihre|eure) (?:reichweite|ums[äa]tze|umsatz|sichtbarkeit|follower|besucherzahlen)\b.{0,40}\b(?:steigern|erh[öo]hen|verdoppeln|verbessern)|\b(?:steigern|erh[öo]hen|verdoppeln|verbessern) (?:wir |sie |du )?(?:\w+ ){0,2}(?:deine|ihre|eure|die) (?:reichweite|ums[äa]tze|umsatz|sichtbarkeit|follower|besucherzahlen)\b|\bgarantiert\b",
    # fr
    r"\bnous (?:proposons|offrons|sommes une|aidons|produisons|cr[ée]ons)\b|\bnotre (?:agence|[ée]quipe|portfolio|service)\b|\baudit gratuit\b|\b(?:devis|analyse|consultation|[ée]chantillon) gratuit\w*\b|\bappel (?:rapide|gratuit)\b|\bam[ée]liorer votre (?:visibilit|r[ée]f[ée]rencement|trafic)",
    # es
    r"\bofrecemos\b|\bsomos una (?:agencia|empresa)\b|\bnuestra (?:agencia|empresa|oferta|cartera)\b|\b(?:auditor[ií]a|consulta|an[áa]lisis|presupuesto|muestra) gratuit[ao]\b|\bllamada (?:r[áa]pida|breve|gratuita)\b|\bmejorar (?:su|tu) (?:visibilidad|posicionamiento|tr[áa]fico)\b",
    # it
    r"\bofferiamo\b|\bsiamo un['’]?(?:agenzia|azienda)\b|\bla nostra (?:agenzia|azienda|offerta)\b|\b(?:analisi|consulenza|preventivo|campione) gratuit[ao]\b|\bchiamata (?:veloce|breve|gratuita)\b|\bmigliorare la (?:vostra|tua) visibilit",
    # nl
    r"\bwij (?:bieden|maken|helpen|zijn een|leveren|verzorgen)\b|\bonze (?:diensten|klanten|agency|bureau|pakketten)\b|\b(?:gratis|vrijblijvende?) (?:analyse|offerte|adviesgesprek|audit|proef|advies)\b|\bkort (?:gesprek|telefoongesprek|belletje)\b|\bgraag plannen wij\b|\bhoger in google\b",
    # pl
    r"\b(?:oferujemy|proponujemy|zajmujemy si[ęe]|specjalizujemy si[ęe])\b|\bnasza (?:agencja|firma|oferta)\b|\b(?:bezp[łl]atn\w+|darmow\w+) (?:audyt|analiz\w+|wycen\w+|konsultacj\w+|pr[óo]bk\w+)|\bkr[óo]tk\w+ (?:rozmow|spotkani|telefon)\w*|\bpierwsz\w+ stron\w+ google\b",
    # tr
    r"\bsunuyoruz\b|\bajans[ıi]m[ıi]z\b|\bhizmet(?:ler)?imiz\b|\b(?:[üu]cretsiz|bedava) (?:analiz|denetim|dan[ıi][sş]manl[ıi]k|teklif|g[öo]r[üu][sş]me)\b|\bk[ıi]sa bir g[öo]r[üu][sş]me\b|\bsat[ıi][sş]lar[ıi]n[ıi]z[ıi] art[ıi]r\w*|\bm[üu][sş]terilerimiz\b",
    # ru / uk
    r"мы (?:предлагаем|занимаемся|поможем|создаём|создаем|делаем|продвигаем)|наша (?:компания|студия|команда|агентство)|наше агентство|бесплатн\w+ (?:аудит|анализ|консультац\w+|пробн\w+)|для (?:вашего )?бизнеса|в топ (?:google|гугл|10)|выведем|ми (?:пропонуємо|займаємося)|наша студія|безкоштовн\w+ (?:аудит|аналіз)",
    # weitere Formeln (Abnahme 3): Verkäufer-Wendungen in den Sprachen und Prod-Pitches
    r"\blet me know if you (?:want|would like|[''’]d like)\b|\bwould you like (?:me )?to (?:see|send|have|get|receive)\b|\bwant to see (?:some )?(?:samples|examples)\b|\bsamples of our (?:previous |past )?work\b|\bwondered if you\b|\bhave you (?:ever )?considered\b|\bwould love to (?:make|create|work|collaborate|help)\b",
    r"\bour (?:videos|prices|rates|work|seo|plan|offer|team)\b|\b(?:seo|service) (?:packages?|proposal|action plan)\b|\bprice list\b|\bproposal and pricing\b|\bwould be happy to (?:share|send|help|discuss)\b|\b(?:advertise|promote|market) your (?:business|brand|shop|store|company)\b|\bgoogle (?:1st|first) page\b|\bimprove (?:the |your )?visibility\b|\bvisible in google\b|\bin google[\'’]?s? search index\b",
    r"\bnoticed (?:\w+[- ]){0,6}issues?\b|\bi[\'’]m an? (?:\w+ ){0,3}(?:creator|editor|designer|developer|consultant|freelancer|photographer|videographer|influencer|producer)\b|\bi (?:make|create|produce|design|build) (?:authentic |high[- ]quality |engaging |professional )?\w* ?(?:videos|reels|websites|content)\b",
    # de
    r"\bgern(?:e)? (?:erstelle|schicke|sende) ich\b|\bein angebot (?:erstellen|schicken|senden|zusenden)\b|\bw[äa]re (?:ein|eine) (?:\w+ ){0,4}interessant\b|\bwir (?:drehen|produzieren|erstellen|bieten|betreuen)\b|\bkurzer (?:werbefilm|imagefilm)\b|\bunser (?:angebot|team|service)\b",
    # es / pt / it / nl / pl / uk (3. Person, Preis, Beispiele)
    r"\bnosotros (?:creamos|ofrecemos|hacemos)\b|\bnuestro equipo\b|\bprecios (?:empiezan|desde|comienzan)\b|\bpresupuesto (?:gratis|gratuito)\b|\b(?:le|te) interesa\b|\bgustar[ií]a ver ejemplos\b",
    r"\bn[óo]s (?:criamos|oferecemos|fazemos)\b|\bnossa equipa\b|\bnossa equipe\b|\bpre[çc]os come[çc]am\b|\bor[çc]amento gr[áa]tis\b|\bgostaria de ver exemplos\b",
    r"\bnoi (?:creiamo|offriamo|facciamo)\b|\bil nostro team\b|\bi prezzi partono\b|\bvolete vedere (?:degli )?esempi\b",
    r"\bmogen wij u\b|\bkorte video\w*|\bwij maken\b|\bwilt u (?:een|graag)\b",
    r"\boferuje\b|\boferujemy\b|\bdla sklep[óo]w\b|\bpozycjonowanie\b|\bpozycjonowania\b|\bdla firm\b|\bch[ęe]tnie (?:przygotujemy|wyślemy)",
    r"наша команда|пропонує|ціни від|безкоштовн\w+ розрахунок|хочете побачити приклади|хотите увидеть примеры|цены от|реклам\w+ для (?:интернет|вашего)",
    r"\bi[çc]in (?:profesyonel|reklam|video)\w*|\bsunar[ıi]z\b|\bs[uü]nar\b|\bfiyatlar[ıi]m[ıi]z\b",
)
_FORMELN = tuple(re.compile(f, re.I) for f in FORMELN)
MIN_FORMELN = 2


def tausch_angebot(text):
    """Creator bietet Video/Reel für die Marke gegen ein Gratis-Stück an („for your brand … in exchange for a free
    piece“). Ohne „für deine Marke“ (nur „featuring your pieces“) bleibt es eine normale Anfrage an Luisa."""
    return bool(_TAUSCH.search(text) and _FUER_MARKE.search(text))


_FUER_MARKE = re.compile(r"\bfor your (?:brand|business|shop|store|company|label|website)\b|"
                         r"\bf[üu]r (?:dein|deine|euer|eure|ihr|ihre)\w* (?:marke|label|shop|firma|unternehmen)\b", re.I)


def formeln_zaehlen(text):
    """Anzahl der verschiedenen Verkäufer-Formeln im Text (jede verschiedene Wendung zählt einmal)."""
    gefunden = set()
    for f in _FORMELN:
        for m in f.finditer(text):
            gefunden.add(m.group(0).lower())
    if tausch_angebot(text):
        gefunden.add('tausch')
    return len(gefunden)


#: (c) Wer das schreibt, meint Luviq und seine Stücke oder will etwas kaufen: nie als Angebot behandeln.
_KUNDE = re.compile(
    r'n[º°o]\s?\.?\s?\d{2,4}\b|\bnummer\s?\d|\barchiv\s?nummer|\bst[üu]ck(?:e|en)?\b|\bunikat|\bjacke\b|\bshirts?\b|\bt-shirt|\bhoodie|'
    r'\bpullover|\bpulli\b|\bhose\b|\bjeans\b|\bkleid\b|\bmantel\b|\bweste\b|\bjacket\b|\bsweater\b|sweatshirt|\bcoats?\b|'
    r'\bcostumes?\b|\bkost[üu]m|\bcommission\w*|\btrikots?\b|\bsudadera|\bveste\b|\bgiacca\b|\bbluz\w*|'
    r'\bsize\s+(?:xs|s|m|l|xl|xxl|\d{2})\b|\bin size\b|\bgr[öo](?:ß|ss)e\b|\bteil(?:e|en)?\b|\bpieces?\b|\bitems?\b|'
    r'\bbestell|\border(?:s|ed|ing)?\b|\bversand|\bship(?:s|ped|ping)?\b|\bliefer|\bdelivery|\blivr|\bspedizion|'
    r'\bsipari[sş]|\bwysy[łl]|\bretoure|\br[üu]cksendung|\bwiderruf|\brefund|\bnoch (?:frei|verf[üu]gbar|da)\b|'
    r'\bstill available\b|\bavailable in\b|\bis (?:it|this|that) available\b|\bverf[üu]gbar|\breserv|\banprobe|\bpassform|\bmotiv\b|\bengel\b|\bupcycl|\bbleach|'
    r'\bgebleicht|\bluisa\b|\bluviq\.archive|\binstagram\.com/|\bkaufen\b|\bkupi[ćc]|\bbuy\b|\bpurchase\b|'
    r'\bcustom(?:ized|ised)?[ -](?:\w+ )?(?:coat|jacket|hoodie|shirt|sweatshirt|dress|vest|pants|trousers|jeans|sweater|'
    r'pullover|design|made|order|piece|print)\w*|\bcustom(?:er)?s? (?:order|piece)\w*|\bma[ßs]anfertig|\bgeschenk|\bgift\b|\bmerch\b|\blogo auf\b|'
    r'\barbeitskleidung|\bworkwear|\bsch[üu]ler|\bschule\b|\bklasse\b|\bschool\b|\bstudent\w*|\bstudent(?:in)?\b|\bthesis\b|'
    r'\bpresse\b|\bpress\b|\bmagazin|\bkooperation|\bcollab\w*|\bone like (?:that|this)\b|\bstorno|\brechnung\b|\binvoice\b|'
    r'\bgutschein|\bvoucher|\bgift ?cards?|\bcartes? cadeau|\bbons? d.?achat|\btarjetas? regalo|\bbuon[oi] regalo|\bcadeaubon|\bbon(?:y|u)? podarunkow|\bhediye [çc]eki|'
    r'\bnewsletter|\bзаказ|\bкупить|\bкупи\w*|\bхуди|\bскидк|\bдоставк|\bachet(?:er|e|ons)\b|\bcommander\b|\bcommande\w*|\bcomprar\b|\bpedido|\bpedir\b|\benv[ií]o\b|\bacquist\w+|\bcomprare\b|\bordinare\b|\bordine\b|'
    r'\bkopen\b|\bbestellen\b|\bbezorg\w*|\bkupowa[ćc]\b|\bzam[óo]wi\w*|\bsatın al\w*|\bpaypal\b|\bzahl(?:e|en|ung)\b|'
    r'\bpaket\b|\bdhl\b|\bwhat(?:s|\'s| is) the price\b|\bwas kostet\b|\bhow much\b|\bworkshop\b|\binterview', re.I)

#: Ausdrücklicher Tausch (Creator bietet Video/Reel gegen ein Gratis-Stück): hebt nur die Kundenwort-Sperre
#: auf. Ein beliebiges „free“ oder „kostenlos“ (free shipping, kostenloser Versand) zählt **nicht**.
_TAUSCH = re.compile(
    r'\bin exchange for\b|\bim austausch (?:f[üu]r|gegen)\b|\bgegen (?:ein|einen|eine) (?:kostenlos\w* |gratis )?'
    r'(?:st[üu]ck|teil|shirt|hoodie|jacke|produkt)\b|\bfor (?:a|an) free (?:item|piece|product|shirt|hoodie|jacket)\b|'
    r'\bfor free (?:items?|pieces?|products?)\b', re.I)


def ist_angebot(name='', betreff='', nachricht=''):
    """``True``, wenn jemand Luviq eine Dienstleistung für das eigene Geschäft verkaufen will (siehe Modulkopf).

    Verlangt Dienst-Stichwort **und** mindestens zwei Verkäufer-Formeln (``FORMELN``), und kein Kundenwort (die Prüfung kommt zuerst;
    nur ein ausdrücklicher Tausch hebt sie auf). Im Zweifel ``False``: dann geht die Nachricht an Luisa."""
    text = ' '.join((betreff or '', nachricht or ''))
    if len(text.strip()) < 25:
        return False
    if _KUNDE.search(text) and not tausch_angebot(text):
        return False
    return _DIENST.search(text) is not None and formeln_zaehlen(text) >= MIN_FORMELN


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


def erkennung_aktiv():
    """``ANGEBOT_ERKENNUNG`` (Vorgabe **aus**): nur bei „an“ gibt es Einstufung „angebot“ und Absage.

    Aus: jede Nicht-Spam-Nachricht geht wie eine normale Anfrage an Luisa; erkennt ``ist_angebot`` ein Angebot,
    steht nur „[evtl. Angebot]“ im Betreff der Mail."""
    return (os.getenv('ANGEBOT_ERKENNUNG') or 'aus').strip().lower() in ('an', 'ein', 'on', '1', 'true', 'ja')


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
    'ohne-zeit', 'wiederholung', 'linkflut', 'kurzlink', 'zeit-abgelaufen', 'flirt-bot', 'kaltakquise-bot',
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
