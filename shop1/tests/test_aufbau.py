"""Designwache: der sichtbare Aufbau jeder Seite bleibt, wie er ist.

Regel 1 des Verbesserungslaufs schützt Reihenfolge der Elemente, CSS-Klassen,
Kennungen, Überschriftentexte und die Zahl der Bilder, Formulare und Links.
Erlaubt sind Alternativtexte, ``aria-*``, Meta-Angaben, ``title``, JSON-LD,
``rel``, ``loading``, ``srcset``, Fliesstext, Serverkonfiguration, Python-Code
und Tests. Genau diese Trennung bildet ``_aufbau.fingerabdruck`` ab.

Die Referenz liegt in ``aufbau_referenz.json`` neben dieser Datei. Sie wird
**nie** automatisch nachgezogen. Wer sie neu erfassen will, löscht sie und
lässt die Tests laufen::

    rm shop1/tests/aufbau_referenz.json
    python manage.py test shop1.tests.test_aufbau

Der Lauf schreibt die Datei dann neu und schlägt trotzdem fehl – damit eine
verlorene Referenz nicht still durchgeht. Danach zeigt ``git diff`` genau,
was sich am Aufbau geändert hat, und wer das ohne Freigabe tut, sieht es im
Commit.
"""

import json
from pathlib import Path

from ._aufbau import fingerabdruck, unterschiede
from ._basis import OEFFENTLICHE_SEITEN, LuviqTestCase, erzeuge_produkt

REFERENZ_DATEI = Path(__file__).with_name('aufbau_referenz.json')

#: Produktname der Referenzseite. Muss stabil bleiben, sonst ändert sich der
#: Slug und damit die erfasste Adresse.
REFERENZPRODUKT = 'Referenzstueck fuer die Designwache'

#: Adresse der Produktdetailseite, abgeleitet aus REFERENZPRODUKT.
PRODUKTSEITE = '/produkt/referenzstueck-fuer-die-designwache/'

#: Alle Seiten, deren Aufbau bewacht wird.
BEWACHTE_SEITEN = OEFFENTLICHE_SEITEN + [PRODUKTSEITE]


class DesignwacheTest(LuviqTestCase):
    """Vergleicht den Aufbau jeder Seite mit der abgelegten Referenz."""

    def setUp(self):
        erzeuge_produkt(REFERENZPRODUKT)

    def _erfasse(self):
        abdruecke = {}
        for pfad in BEWACHTE_SEITEN:
            antwort = self.hole(pfad)
            self.assertEqual(
                antwort.status_code, 200,
                f'{pfad} antwortet mit {antwort.status_code}; der Aufbau '
                f'lässt sich so nicht erfassen',
            )
            abdruecke[pfad] = fingerabdruck(antwort.content.decode())
        return abdruecke

    def test_die_wache_erfasst_ueberhaupt_seiten(self):
        """Blockiert, wenn die Referenz leer ist.

        Verhindert den Fehler, der diesen Lauf schon einmal ungeschützt liess:
        eine Wache, die null Seiten erfasst, vergleicht zwei leere Mengen und
        meldet 'Aufbau unverändert'. Sie gibt dann alles frei, gerade wenn
        Templates angefasst werden. Erfasst sie nichts, muss sie anhalten.
        """
        self.assertTrue(
            REFERENZ_DATEI.exists(),
            f'{REFERENZ_DATEI.name} fehlt – die Designwache ist wirkungslos',
        )
        referenz = json.loads(REFERENZ_DATEI.read_text(encoding='utf-8'))
        self.assertGreaterEqual(
            len(referenz), len(BEWACHTE_SEITEN),
            f'Die Referenz kennt {len(referenz)} von {len(BEWACHTE_SEITEN)} '
            f'Seiten. Eine unvollständige Wache schützt nur scheinbar.',
        )
        for pfad, abdruck in referenz.items():
            with self.subTest(pfad=pfad):
                self.assertTrue(
                    abdruck.get('tags'),
                    f'Der Fingerabdruck von {pfad} ist leer',
                )

    def test_der_aufbau_jeder_seite_ist_unveraendert(self):
        """Schlägt an, sobald ein Element, eine Kennung, eine CSS-Klasse, ein
        Überschriftentext oder die Zahl der Bilder, Formulare und Links sich
        ändert – die Punkte, die Regel 1 wörtlich schützt.

        Meta-Angaben, ``alt``, ``aria-*``, JSON-LD und Fliesstext bleiben
        absichtlich unberührt: das ist die erlaubte Arbeit.
        """
        aktuell = self._erfasse()

        if not REFERENZ_DATEI.exists():
            REFERENZ_DATEI.write_text(
                json.dumps(aktuell, indent=1, ensure_ascii=False, sort_keys=True) + '\n',
                encoding='utf-8',
            )
            self.fail(
                f'Es gab keine Referenz. {REFERENZ_DATEI.name} wurde aus dem '
                f'aktuellen Stand neu geschrieben ({len(aktuell)} Seiten). '
                f'Bitte per "git diff" prüfen und bewusst übernehmen – dieser '
                f'Lauf schlägt absichtlich fehl, damit eine verlorene Referenz '
                f'nicht still als "Aufbau unverändert" durchgeht.'
            )

        referenz = json.loads(REFERENZ_DATEI.read_text(encoding='utf-8'))
        for pfad in BEWACHTE_SEITEN:
            with self.subTest(pfad=pfad):
                self.assertIn(pfad, referenz, f'{pfad} fehlt in der Referenz')
                abweichungen = unterschiede(referenz[pfad], aktuell[pfad])
                self.assertFalse(
                    abweichungen,
                    f'Der Aufbau von {pfad} hat sich geändert:\n  '
                    + '\n  '.join(abweichungen[:8]),
                )
