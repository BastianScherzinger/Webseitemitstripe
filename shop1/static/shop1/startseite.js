/* Startseite v9: Hero-Galerie, Daumenleiste, Einblenden. Eigene Datei auf der eigenen Adresse (CSP script-src 'self'),
   aus dem freigegebenen Entwurf (Design/luviq/redesign-2026-11-24/v8/_skript/v8.js und v9bau.py) übernommen,
   ohne den Teil der Vorschau-Hülle. */
/* Daumenleiste (Handy) ausblenden, solange ein Anfrage-Knopf, der Kontakt oder der Fuß sichtbar ist */
(function(){
  var leiste = document.querySelector('.leiste');
  if(!leiste || !('IntersectionObserver' in window)) return;
  var sichtbar = new Set();
  var io = new IntersectionObserver(function(eintraege){
    eintraege.forEach(function(e){ e.isIntersecting ? sichtbar.add(e.target) : sichtbar.delete(e.target); });
    leiste.classList.toggle('weg', sichtbar.size > 0);
  }, {threshold: 0.15});
  document.querySelectorAll('.kontakt, .fuss, .knopf').forEach(function(z){ io.observe(z); });
})();

/* Hero-Galerie v6
   - alle 3,5 s das nächste ganze Shirt, Bewegung 600 ms (nur Scroll-Position, kein Layout)
   - wischen, Striche antippen, Pfeile (PC) und Tasten links/rechts
   - nach jeder Handbewegung 8 s Pause, dann läuft sie weiter
   - prefers-reduced-motion: kein Auto-Wechsel, Sprünge ohne Gleiten
   - läuft nur, solange sie sichtbar ist und der Tab offen */
document.querySelectorAll('.galerie.auto').forEach(function(g){
  var spur = g.querySelector('.spur'), dias = [].slice.call(g.querySelectorAll('.dia')), knoepfe = [].slice.call(g.querySelectorAll('.punkte button'));
  var seitenK = [].slice.call(g.querySelectorAll('.seiten button'));
  var ruhig = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var jetzt = -1, sichtbar = true, uhr = null, pause = null, gleitet = false, pausiert = false;
  var TAKT = 3500, PAUSE = 8000, DAUER = 600;

  function ziel(i){ return dias[i].offsetLeft - dias[0].offsetLeft; }
  function zu(i){
    i = (i + dias.length) % dias.length;
    markiere(i, true);
    var von = spur.scrollLeft, nach = ziel(i);
    if (ruhig || Math.abs(nach - von) < 2){ spur.scrollLeft = nach; return; }
    gleitet = true; spur.classList.add('gleitet');
    var t0 = performance.now();
    (function schritt(t){
      var p = Math.min(1, (t - t0) / DAUER), e = p < .5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2;
      spur.scrollLeft = von + (nach - von) * e;
      if (p < 1) requestAnimationFrame(schritt);
      else { spur.classList.remove('gleitet'); spur.scrollLeft = nach; gleitet = false; }
    })(t0);
  }
  function planen(){
    clearTimeout(uhr);
    var laeuft = !ruhig && !pausiert && sichtbar && !document.hidden;
    g.classList.toggle('laeuft', laeuft);
    if (laeuft) uhr = setTimeout(function(){ zu(jetzt + 1); }, TAKT);
  }
  function markiere(i, neu){
    if (i === jetzt && !neu) return;
    var anders = i !== jetzt; jetzt = i;
    knoepfe.forEach(function(k, n){ k.classList.toggle('an', n === i); k.setAttribute('aria-current', n === i ? 'true' : 'false'); });
    var seite = dias[i].dataset.seite; seitenK.forEach(function(b){ b.setAttribute('aria-pressed', (b.dataset.ziel === '0') === (seite === 'vorne') ? 'true' : 'false'); });
    if (anders){ g.classList.remove('laeuft'); void g.offsetWidth; } /* Strich-Füllung neu starten */
    planen();
  }
  function hand(){ /* Handbewegung: 8 s Pause, dann weiter */
    pausiert = true; clearTimeout(pause); planen();
    pause = setTimeout(function(){ pausiert = false; planen(); }, PAUSE);
  }

  if ('IntersectionObserver' in window){
    var beob = new IntersectionObserver(function(es){ es.forEach(function(e){ if (e.isIntersecting && !gleitet) markiere(dias.indexOf(e.target)); }); }, {root: spur, threshold: .6});
    dias.forEach(function(d){ beob.observe(d); });
    new IntersectionObserver(function(es){ sichtbar = es[0].isIntersecting; planen(); }, {threshold: .4}).observe(g);
  }
  markiere(0);
  ['pointerdown', 'touchstart', 'wheel'].forEach(function(t){ spur.addEventListener(t, hand, {passive: true}); });
  knoepfe.forEach(function(k, n){ k.addEventListener('click', function(){ hand(); zu(n); }); });
  seitenK.forEach(function(b){ b.addEventListener('click', function(){ hand(); zu(+b.dataset.ziel); }); });
  g.querySelectorAll('.pfeil').forEach(function(p){ p.addEventListener('click', function(){ hand(); zu(jetzt + (p.dataset.weg === 'zurueck' ? -1 : 1)); }); });
  g.addEventListener('keydown', function(e){
    if (e.key === 'ArrowRight' || e.key === 'ArrowLeft'){ e.preventDefault(); hand(); zu(jetzt + (e.key === 'ArrowRight' ? 1 : -1)); }
  });
  document.addEventListener('visibilitychange', planen);
});

/* Einblenden beim Scrollen: nur was beim Laden unter dem sichtbaren Rand liegt, wartet */
(function(){
  if (!('IntersectionObserver' in window) || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var io = new IntersectionObserver(function(es){
    es.forEach(function(e){ if (e.isIntersecting){ e.target.classList.remove('wartet'); io.unobserve(e.target); } });
  }, {rootMargin: '0px 0px -8% 0px'});
  document.querySelectorAll('[data-auf]').forEach(function(el){
    if (el.getBoundingClientRect().top > window.innerHeight){ el.classList.add('wartet'); io.observe(el); }
  });
})();
