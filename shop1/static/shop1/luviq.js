/* Luviq Universe – kleine Seitenfunktionen ohne Bibliothek.

   Ersetzt seit dem 02.10.2026 Alpine.js (Messpunkte PF31, SI09): Alpine
   brauchte 'unsafe-eval' in der Content-Security-Policy und einen Abruf bei
   cdn.jsdelivr.net, wurde aber nur für drei Dinge benutzt, die hier stehen.
   Die Skriptdatei liegt auf der eigenen Adresse, die CSP erlaubt sie über
   script-src 'self'. Alles läuft nach dem Aufbau der Seite (defer).
*/
(function () {
    'use strict';

    // 1. Einblenden: .scroll-reveal bekommt .visible, sobald es im Bild ist
    //    (vorher x-intersect.once). Ohne IntersectionObserver sofort sichtbar.
    var einblendungen = document.querySelectorAll('.scroll-reveal');
    function zeigen(el) { el.classList.add('visible'); }
    if ('IntersectionObserver' in window) {
        var beobachter = new IntersectionObserver(function (eintraege) {
            eintraege.forEach(function (e) {
                if (e.isIntersecting) { zeigen(e.target); beobachter.unobserve(e.target); }
            });
        });
        einblendungen.forEach(function (el) { beobachter.observe(el); });
    } else {
        einblendungen.forEach(zeigen);
    }

    // 2. Gästebuch: <button data-antwort-schalter> blendet das Antwortfeld
    //    [data-antwort] im selben Beitrag ein und aus (vorher x-show). Ohne
    //    Skript bleibt das Feld sichtbar und damit benutzbar.
    document.querySelectorAll('[data-antwort]').forEach(function (feld) { feld.hidden = true; });
    document.addEventListener('click', function (e) {
        var knopf = e.target.closest ? e.target.closest('[data-antwort-schalter]') : null;
        if (!knopf) { return; }
        var huelle = knopf.parentNode;
        var feld = huelle ? huelle.querySelector('[data-antwort]') : null;
        if (!feld) { return; }
        feld.hidden = !feld.hidden;
        knopf.setAttribute('aria-expanded', feld.hidden ? 'false' : 'true');
    });

    // 3. Panel: <input type="checkbox" data-alle-auswaehlen="feldname"> setzt
    //    alle Kästchen dieses Namens in derselben Tabelle (vorher @change).
    document.addEventListener('change', function (e) {
        var ziel = e.target;
        var name = ziel && ziel.getAttribute ? ziel.getAttribute('data-alle-auswaehlen') : null;
        if (!name) { return; }
        var tabelle = ziel.closest('table');
        if (!tabelle) { return; }
        tabelle.querySelectorAll('input[name="' + name + '"]').forEach(function (kaestchen) {
            kaestchen.checked = ziel.checked;
        });
    });
})();
