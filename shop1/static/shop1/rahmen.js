/* Rahmen der Unterseiten (Paket 5, 26.11.2026): Daumenleiste der Startseite. Sie blendet sich aus, solange ein
   Hauptknopf, ein Formular oder der Fuß im Bild ist, damit sie nie ein Feld oder einen Absende-Knopf verdeckt.
   Dieselbe Logik wie der Anfang von startseite.js, nur mit der Auswahl für Seiten mit Formularen. */
(function () {
  var leiste = document.querySelector('.leiste');
  if (!leiste || !('IntersectionObserver' in window)) return;
  var sichtbar = new Set();
  var io = new IntersectionObserver(function (eintraege) {
    eintraege.forEach(function (e) { e.isIntersecting ? sichtbar.add(e.target) : sichtbar.delete(e.target); });
    leiste.classList.toggle('weg', sichtbar.size > 0);
  }, { threshold: 0.15 });
  document.querySelectorAll('.fuss, .knopf, main form, .lv-formular, [data-leiste-aus]').forEach(function (z) { io.observe(z); });
})();
