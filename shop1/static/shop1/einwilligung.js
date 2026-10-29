/* Einwilligung (§ 25 TDDDG): Fremdskript erst nach „Akzeptieren".
   Gespeichert wird nur die Wahl selbst ("ja"/"nein") im localStorage dieser
   Seite – das ist für die gewünschte Funktion unbedingt erforderlich. */
(function () {
    var kasten = document.getElementById('lv-einwilligung');
    if (!kasten) { return; }
    var SCHLUESSEL = 'lv-einwilligung';
    function lies() { try { return localStorage.getItem(SCHLUESSEL); } catch (e) { return null; } }
    function merke(wert) { try { localStorage.setItem(SCHLUESSEL, wert); } catch (e) { /* ohne Speicher: jedes Mal fragen */ } }
    function lade() {
        var adresse = kasten.getAttribute('data-skript');
        if (!adresse || document.querySelector('script[data-einwilligung-geladen]')) { return; }
        var s = document.createElement('script');
        s.src = adresse; s.defer = true; s.setAttribute('data-einwilligung-geladen', '');
        document.head.appendChild(s);
    }
    kasten.querySelectorAll('[data-einwilligung]').forEach(function (knopf) {
        knopf.addEventListener('click', function () {
            var wert = knopf.getAttribute('data-einwilligung');
            merke(wert);
            kasten.hidden = true;
            if (wert === 'ja') { lade(); } else if (lies() === 'nein' && document.querySelector('script[data-einwilligung-geladen]')) { location.reload(); }
        });
    });
    document.querySelectorAll('[data-einwilligung-aendern]').forEach(function (a) {
        a.addEventListener('click', function (e) { e.preventDefault(); kasten.hidden = false; });
    });
    var wahl = lies();
    if (wahl === 'ja') { lade(); } else if (wahl !== 'nein') { kasten.hidden = false; }
})();
