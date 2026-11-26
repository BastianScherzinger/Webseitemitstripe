"""Baut den Auszug in shop1/static/shop1/rahmen.css aus startseite.css (Kopf, Knöpfe, Fuß, Daumenleiste).

Die Startseite lädt nur startseite.css (ein blockierender Stil, LCP). Alle anderen öffentlichen Seiten laden
luviq.css und rahmen.css; der Rahmen (Kopf, Fuß, Daumenleiste) ist dort derselbe Quelltext, nur an body.lv-rahmen
statt body.lv-v9 gebunden und mit --rr statt --rand (luviq.css belegt --rand anders). Ein Test
(test_unterseiten_v9) prüft, dass der Auszug und startseite.css übereinstimmen.

Aufruf: python tools/rahmen_css_bauen.py   (schreibt nur den Auszug-Teil, der Rest von rahmen.css bleibt)
"""
import re
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent / 'shop1' / 'static' / 'shop1'
ANFANG = '/* ==== AUSZUG aus startseite.css (nicht von Hand ändern: tools/rahmen_css_bauen.py) ==== */'
ENDE = '/* ==== ENDE AUSZUG ==== */'
WAEHLER = re.compile(r'^\s*\.lv-v9 \.(kopf|marke|k-nav|k-wa|knopf|textlink|fuss|f-[a-z]+|leiste)\b')


def stuecke(text):
    """Zerlegt in oberste Regeln (Text einschließlich @media-Blöcken)."""
    tiefe, start, aus = 0, 0, []
    for i, z in enumerate(text):
        if z == '{':
            tiefe += 1
        elif z == '}':
            tiefe -= 1
            if tiefe == 0:
                aus.append(text[start:i + 1].strip('\n'))
                start = i + 1
    return aus


def regeln_in(block):
    return stuecke(block)


def auszug(quelle):
    text = re.sub(r'/\*.*?\*/', '', quelle, flags=re.S)
    oben, media = [], []
    for st in stuecke(text):
        st = st.strip()
        if st.startswith('@media (min-width:1000px)'):
            innen = st[st.index('{') + 1:st.rindex('}')]
            media = [r.strip() for r in regeln_in(innen) if WAEHLER.match(r)]
        elif WAEHLER.match(st):
            oben.append(st)
    return oben, media


def uebersetze(t):
    return t.replace('.lv-v9', '.lv-rahmen').replace('var(--rand)', 'var(--rr)')


def bauen():
    oben, media = auszug((WURZEL / 'startseite.css').read_text(encoding='utf-8'))
    teile = [ANFANG,
             'body.lv-rahmen{--grund:#0A0A0A;--tief:#070707;--flaeche:#11100F;--text:#F2EEE6;--leise:#A8A297;'
             '--linie:rgba(242,238,230,.13);--linie-stark:rgba(242,238,230,.28);--akzent:#C8763F;--akzent-hell:#DE9159;'
             '--auf-akzent:#140C06;--serif:"Cormorant Garamond",Georgia,serif;--sans:"Schibsted Grotesk",Arial,sans-serif;'
             '--s1:8px;--s2:16px;--s3:24px;--s4:32px;--s5:48px;--s6:64px;--s7:96px;--s8:128px;--s9:160px;--rr:var(--s3)}']
    teile += [uebersetze(r) for r in oben]
    teile.append('@media (min-width:1000px){\n  body.lv-rahmen{--rr:max(48px, calc((100vw - 1200px) / 2))}\n  '
                 + '\n  '.join(uebersetze(r) for r in media) + '\n}')
    teile.append(ENDE)
    return '\n'.join(teile)


if __name__ == '__main__':
    datei = WURZEL / 'rahmen.css'
    alt = datei.read_text(encoding='utf-8') if datei.exists() else ''
    neu = bauen()
    if ANFANG in alt:
        a, b = alt.index(ANFANG), alt.index(ENDE) + len(ENDE)
        datei.write_text(alt[:a] + neu + alt[b:], encoding='utf-8', newline='\n')
    else:
        datei.write_text(neu + '\n' + alt, encoding='utf-8', newline='\n')
    print('rahmen.css geschrieben,', len(neu), 'Zeichen im Auszug')
