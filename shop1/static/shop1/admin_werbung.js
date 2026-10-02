// Verwaltung › Werbung: Knöpfe der Seite und Diagramme (Chart.js liegt im Projekt).
// Ausgelagert aus admin/werbung_list.html (V09); die Daten kommen per json_script
// aus dem Template („werbung-timeline“, „werbung-plattformen“).
(function () {
function toggleEdit(id) {
    document.getElementById('edit-' + id).classList.toggle('hidden');
}

// Knöpfe dieser Seite über data-werbung statt onclick – die CSP mit Nonce
// blockiert Handler-Attribute (SI09). Steht vor dem ersten Chart-Aufruf,
// damit die Knöpfe auch dann wirken, wenn Chart.js nicht lädt.
document.addEventListener('click', function (e) {
    var el = e.target.closest ? e.target.closest('[data-werbung]') : null;
    if (!el) return;
    var aktion = el.getAttribute('data-werbung');
    var wert = el.getAttribute('data-werbung-wert');
    var formular = document.getElementById('create-form');
    if (aktion === 'formular-umschalten' && formular) {
        formular.classList.toggle('hidden');
    } else if (aktion === 'formular-schliessen' && formular) {
        formular.classList.add('hidden');
    } else if (aktion === 'formular-oeffnen' && formular) {
        formular.classList.remove('hidden');
        el.closest('.glass-card').style.display = 'none';
    } else if (aktion === 'bearbeiten') {
        toggleEdit(wert);
    } else if (aktion === 'verlauf' && window.switchTimeline) {
        window.switchTimeline(wert);
    }
});

Chart.defaults.color = 'rgba(255,255,255,0.4)';
Chart.defaults.borderColor = 'rgba(255,255,255,0.05)';

// Ohne Werbungen gibt es keine Verlaufsdaten (json_script im Template) und keine Diagramme.
if (!document.getElementById('werbung-timeline')) { return; }

// ── KPI totals aus Timeline ───────────────────────────────────────────────
const TIMELINE = JSON.parse(document.getElementById('werbung-timeline').textContent);
const totalViews30  = TIMELINE.views.reduce((s, v) => s + v, 0);
const totalKlicks30 = TIMELINE.klicks.reduce((s, v) => s + v, 0);
document.getElementById('kpi-views').textContent  = totalViews30.toLocaleString('de-DE');
document.getElementById('kpi-klicks').textContent = totalKlicks30.toLocaleString('de-DE');

// ── Chart 1: Reichweite nach Plattform (Balken) ──────────────────────────
(function() {
    const BD = JSON.parse(document.getElementById('werbung-plattformen').textContent);
    const canvas = document.getElementById('siteChart');
    const noData = document.getElementById('site-no-data');
    if (!canvas) return;

    const hasData = (BD.views || []).some(v => v > 0) || (BD.klicks || []).some(v => v > 0);
    if (!hasData || !BD.labels || !BD.labels.length) {
        canvas.style.display = 'none';
        if (noData) noData.style.display = 'flex';
        return;
    }

    new Chart(canvas, {
        type: 'bar',
        data: {
            labels: BD.labels,
            datasets: [
                {
                    label: 'Views (Impressionen)',
                    data: BD.views,
                    backgroundColor: BD.colors.map(c => c + '33'),
                    borderColor: BD.colors,
                    borderWidth: 2,
                    borderRadius: 8,
                    minBarLength: 4,
                },
                {
                    label: 'Klicks',
                    data: BD.klicks,
                    backgroundColor: BD.colors.map(c => c + '88'),
                    borderColor: BD.colors,
                    borderWidth: 2,
                    borderRadius: 8,
                    minBarLength: 4,
                },
            ],
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: { position: 'bottom', labels: { boxWidth: 10, padding: 14, font: { size: 10 } } },
                tooltip: {
                    callbacks: {
                        label: ctx => ` ${ctx.dataset.label}: ${ctx.parsed.y.toLocaleString('de-DE')}`,
                    },
                },
            },
            scales: {
                x: { grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { font: { size: 11, weight: 'bold' } } },
                y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { font: { size: 10 } } },
            },
        },
    });
})();

// ── Chart 2: Tagesverlauf (Linie) ────────────────────────────────────────
var timelineChart = null;
(function() {
    const canvas = document.getElementById('timelineChart');
    const noData = document.getElementById('timeline-no-data');
    if (!canvas) return;

    const hasData = TIMELINE.views.some(v => v > 0) || TIMELINE.klicks.some(v => v > 0);
    if (!hasData) {
        canvas.style.display = 'none';
        if (noData) noData.style.display = 'flex';
        return;
    }

    const makeDataset = (label, data, color) => ({
        label,
        data,
        borderColor: color,
        backgroundColor: color.replace(')', ',0.08)').replace('rgb', 'rgba'),
        tension: 0.4,
        fill: true,
        pointRadius: 3,
        pointHoverRadius: 6,
    });

    timelineChart = new Chart(canvas, {
        type: 'line',
        data: {
            labels: TIMELINE.labels,
            datasets: [makeDataset('Views', TIMELINE.views, '#f97316')],
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: { label: ctx => ` ${ctx.dataset.label}: ${ctx.parsed.y.toLocaleString('de-DE')}` },
                },
            },
            scales: {
                x: { grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { maxTicksLimit: 10, font: { size: 10 } } },
                y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { font: { size: 10 } } },
            },
        },
    });
})();

window.switchTimeline = function(mode) {
    const btnV = document.getElementById('btn-views');
    const btnK = document.getElementById('btn-klicks');
    const activeClass  = 'bg-glow-orange/15 border-glow-orange/40 text-glow-orange';
    const inactiveClass = 'bg-white/5 border-white/10 text-white/40';

    if (mode === 'views') {
        btnV.className = btnV.className.replace(inactiveClass, activeClass);
        btnK.className = btnK.className.replace(activeClass, inactiveClass);
    } else {
        btnK.className = btnK.className.replace(inactiveClass, activeClass);
        btnV.className = btnV.className.replace(activeClass, inactiveClass);
    }

    if (!timelineChart) return;
    const makeDataset = (label, data, color) => ({
        label, data,
        borderColor: color,
        backgroundColor: color.replace(')', ',0.08)').replace('rgb', 'rgba'),
        tension: 0.4, fill: true, pointRadius: 3, pointHoverRadius: 6,
    });
    timelineChart.data.datasets =
        mode === 'views'
            ? [makeDataset('Views', TIMELINE.views, '#f97316')]
            : [makeDataset('Klicks', TIMELINE.klicks, '#38bdf8')];
    timelineChart.update();
};
})();
