# 🚀 Luviq Universe – Google SEO Guide

Ich habe den Code deines Shops bereits für Google optimiert. Damit deine Seite aber auch wirklich gefunden wird (besonders unter dem Begriff "railway hosting luviq"), musst du noch ein paar manuelle Schritte durchführen.

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

### 3. Backlinks (Warum Railway Hosting Luviq?)
Damit man dich unter "railway hosting luviq" findet:
*   Verlinke deine Seite von deinen Social Media Profilen (Instagram, TikTok).
*   Erwähne in deiner Bio Begriffe wie "Handbemalte Kunst auf Railway gehostet" oder ähnliches. Google verknüpft diese Begriffe dann mit deiner Seite.

---

## 🛡️ Sicherheit & Dauerhaftigkeit
*   **HTTPS**: Deine Seite läuft bereits über HTTPS (durch Railway). Das ist ein positiver Ranking-Faktor.
*   **DEBUG-Mode**: Sobald du mit dem Testen fertig bist, sollten wir `DEBUG="False"` in der `.env` setzen. Ich habe es aktuell auf `True` gelassen, damit du PayPal testen kannst. **Wichtig:** Für Google ist eine schnelle, fehlerfreie Seite (ohne Debug-Infos) besser.

Wenn du den Verifizierungs-Code von Google hast, sag Bescheid!
