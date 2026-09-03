# 🚀 Luviq Universe – Google SEO Guide

Der Code des Shops ist für Google vorbereitet. Damit die Seite auch wirklich gefunden wird, sind noch ein paar manuelle Schritte nötig.

**Ziel-Suchbegriffe:** maßgeblich sind die Begriffe, die in `templates/base.html` als `meta name="keywords"` hinterlegt sind — also Marke plus Angebot plus Ort: „Luviq", „Luviq Universe", „Second Hand Mode Alsfeld", „Vintage Mode Hessen", „handbemalte Kleidung kaufen", „Upcycling Mode Deutschland", „1 of 1 Unikate". Der früher hier genannte Begriff „railway hosting luviq" war falsch: Railway ist der Hosting-Anbieter, kein Wort, nach dem Kundschaft sucht. Auf Hosting-Begriffe zu optimieren bringt keine Käufer und verwässert das Markenprofil.

## ✅ Was ich bereits getan habe:
1.  **Dynamische Sitemap**: Unter `/sitemap.xml` wird nun automatisch eine Liste aller deiner Produkte und Seiten für Google bereitgestellt.
2.  **Robots.txt**: Unter `/robots.txt` findet Google nun die Anweisung, was indexiert werden darf.
3.  **Meta-Tags**: Alle Seiten haben jetzt optimierte Titel, Beschreibungen und "Open Graph" Tags (damit Links auf WhatsApp/Instagram schön aussehen).
4.  **Struktur**: Die Seite nutzt nun semantisches HTML, was Google hilft, den Inhalt besser zu verstehen.

---

## 🛠️ Deine nächsten Schritte (WICHTIG!)

### 1. Google Search Console (Der wichtigste Schritt)
Google findet neue Seiten nicht immer sofort. Du musst Google sagen, dass du existierst:
1.  Gehe auf die [Google Search Console](https://search.google.com/search-console/about).
2.  Füge deine Domain (z.B. `https://deine-seite.up.railway.app`) als neue Property hinzu.
3.  **Verifizierung**: Google wird dir eine HTML-Datei oder einen Meta-Tag geben. Schick mir diesen Tag, dann baue ich ihn ein, oder lade die Datei in den `static` Ordner hoch.
4.  **Sitemap einreichen**: Klicke links auf "Sitemaps" und gib `sitemap.xml` ein. Damit fängt Google sofort an, deine Produkte zu lesen.

### 2. Google Business Profile
Wenn du "Luviq" lokal oder als Marke stärken willst:
*   Erstelle ein kostenloses [Google Business Profil](https://www.google.com/business/).
*   Verlinke dort deine Railway-URL. Das gibt der Seite einen massiven Boost in der Vertrauenswürdigkeit bei Google.

### 3. Backlinks
Damit man dich unter deinen echten Suchbegriffen findet:
*   Verlinke deine Seite von deinen Social-Media-Profilen (Instagram, TikTok).
*   Erwähne in deiner Bio das, was du tatsächlich anbietest — z. B. „handbemalte 1-of-1 Vintage-Unikate aus Alsfeld". Google verknüpft diese Begriffe dann mit deiner Seite. Den Hosting-Anbieter dort zu nennen bringt nichts.

---

## 🛡️ Sicherheit & Dauerhaftigkeit
*   **HTTPS**: Deine Seite läuft bereits über HTTPS (durch Railway). Das ist ein positiver Ranking-Faktor.
*   **DEBUG-Mode**: `DEBUG` steht **nicht** auf `True`. `mainweb/settings.py` liest `DEBUG` aus der Umgebung und nimmt ohne gesetzte Variable `False` an (`os.getenv('DEBUG', 'False') == 'True'`). Das ist der richtige Zustand und muss so bleiben: Mit `DEBUG=True` würden bei Fehlern interne Details öffentlich angezeigt, HSTS und die Secure-Cookies wären abgeschaltet und `ALLOWED_HOSTS` stünde auf `*`. Für Google ist eine schnelle, fehlerfreie Seite ohne Debug-Infos ohnehin besser.

Wenn du den Verifizierungs-Code von Google hast, sag Bescheid!
