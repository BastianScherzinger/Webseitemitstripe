# PayPal Sandbox Tutorial – Testen ohne echtes Geld 💳✨

Damit du den Luviq-Shop in Ruhe testen kannst, ohne echtes Geld auszugeben, musst du PayPal in den **Sandbox-Modus** versetzen. Hier ist die Schritt-für-Schritt-Anleitung:

## 1. PayPal Developer Account
1. Gehe auf [developer.paypal.com](https://developer.paypal.com/) und logge dich mit deinem normalen PayPal-Konto ein.
2. Gehe zum **Dashboard** (oben rechts).

## 2. Sandbox Accounts erstellen
Unter "Testing" > "Sandbox Accounts" findest du (oder erstellst du) zwei Konten:
- **Business Account**: Das ist "dein" Shop-Konto (Empfänger).
- **Personal Account**: Das ist das "Käufer"-Konto, mit dem du Testbestellungen machst.
*Notiere dir die E-Mail-Adressen und Passwörter dieser Sandbox-Accounts.*

## 3. App erstellen & Client ID holen
1. Gehe auf "Apps & Credentials".
2. Stelle sicher, dass oben der Schalter auf **Sandbox** steht.
3. Klicke auf "Create App". Nenne sie z.B. "Luviq Shop".
4. Nach dem Erstellen siehst du die **Client ID**. Kopiere diese.

## 4. In den Shop integrieren
1. Öffne deine `.env` Datei oder die Stelle, wo deine Umgebungsvariablen sind.
2. Trage die Client ID ein: `PAYPAL_CLIENT_ID=DEINE_SANDBOX_CLIENT_ID`.
3. In der `settings.py` (oder wo du PayPal konfigurierst) muss die Client ID an das Frontend (das JavaScript in `payment.html`) gereicht werden. Das macht der Shop bereits automatisch.

## 5. Den Test-Kauf durchführen
1. Gehe in deinen Shop und lege etwas in den Warenkorb.
2. Gehe zum Checkout und wähle **PayPal**.
3. Wenn sich das PayPal-Fenster öffnet, logge dich **NICHT** mit deinen echten Daten ein.
4. Nutze die E-Mail und das Passwort deines **Sandbox Personal Accounts** (Schritt 2).
5. Schließe die Zahlung ab.

## 6. Erfolg prüfen
- In deinem Shop sollte die Bestellung nun auf **"Bezahlt"** springen.
- Der Artikel sollte automatisch deaktiviert werden (1-of-1 Logik).
- In deinem [PayPal Sandbox Dashboard](https://www.sandbox.paypal.com/) kannst du beim Business Account den Geldeingang sehen.

---
**WICHTIG:** Bevor du die Seite live schaltest (Production), musst du eine neue App im PayPal Dashboard unter **Live** erstellen und die `PAYPAL_CLIENT_ID` in deiner Produktionsumgebung austauschen!
