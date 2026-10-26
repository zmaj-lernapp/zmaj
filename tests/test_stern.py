# -*- coding: utf-8 -*-
"""Stern (19.10.2026): was sich ohne Browser pruefen laesst. Das Verhalten
selbst - Knopf, Reiter, Runde, Sicherungsdatei, Zentrierung, Lage in der
Kopfzeile - prueft tests_e2e/test_stern.py im echten Browser."""
import re

STERN_TEXTE = ["stern.knopf", "stern.titel", "stern.weg", "stern.desc", "stern.leer",
               "stern.rest", "stern.anzahl", "stern.symbol", "stern.voll"]

# Der Stern aus dem gewaehlten Entwurf (Variante 1 "Ring"), viewBox um den
# Flaechenschwerpunkt. Wer ihn aendert, muss die Zentrierung neu messen.
PFAD = ("M1.41 -9.701L3.403 -5.23A0.643 0.643 0 0 0 3.923 -4.853L8.791 -4.339A1.544 1.544 0 0 1 9.662 -1.657"
        "L6.026 1.62A0.643 0.643 0 0 0 5.827 2.231L6.843 7.02A1.544 1.544 0 0 1 4.561 8.677L0.321 6.232"
        "A0.643 0.643 0 0 0 -0.321 6.232L-4.561 8.677A1.544 1.544 0 0 1 -6.843 7.02L-5.827 2.231"
        "A0.643 0.643 0 0 0 -6.026 1.62L-9.662 -1.657A1.544 1.544 0 0 1 -8.791 -4.339L-3.923 -4.853"
        "A0.643 0.643 0 0 0 -3.403 -5.23L-1.41 -9.701A1.544 1.544 0 0 1 1.41 -9.701Z")
SVG_LEER = ('<svg class="sternsym" viewBox="-12 -12 24 24" width="24" height="24" aria-hidden="true" '
            'focusable="false"><path style="stroke-width:1.9" d="' + PFAD + '"/></svg>')

# Das CSS des Entwurfs, Zeile fuer Zeile (GEWAEHLT_variante1.md). Abweichungen:
# .stern[hidden] und die Lage. Bis zum 26.10.2026 stand er in der Leiste
# (.nav .stern), dann kurz neben dem Drachen (.zmajreihe .stern, absolut,
# 44 x 44 - Ajdin: "im moment steht es so mitten im nirgendwo"). Seit dem
# 26.10.2026 spaet steht er in der Kopfzeile der Karte, rechts neben den
# Punkten (Ajdin: "nimm A"): im Fluss der Flex-Zeile, 40 x 40 mit 24-px-Stern,
# Trefferflaeche 48 ueber ::before inset -6px, margin -20px 0, damit die
# Zeile so hoch bleibt wie die Herz-Pille, und versteckt mit
# visibility:hidden statt display:none, damit der Balken nicht springt. Die
# Flaeche ist --bg wie die Herz-Pille - auf der Karte (--surface) waere ein
# --surface-Kreis kaum zu sehen. Form, Farben und Stern sind sonst die des
# Entwurfs.
CSS_ENTWURF = [
    ':root{--stern-gold-hell:#FFD84D; --stern-gold-tief:#F5B400; --stern-rand:#B07D00}',
    '@media (prefers-color-scheme: dark){ :root:not([data-theme="light"]){--stern-gold-hell:#FFDF5E; '
    '--stern-gold-tief:#F7BC12; --stern-rand:#E3A700} }',
    ':root[data-theme="dark"]{--stern-gold-hell:#FFDF5E; --stern-gold-tief:#F7BC12; --stern-rand:#E3A700}',
    '.kastenkopf .stern{--an-grund:var(--accent-soft)}',
    '@media (prefers-color-scheme: dark){ :root:not([data-theme="light"]) .kastenkopf .stern{--an-grund:var(--surface)} }',
    ':root[data-theme="dark"] .kastenkopf .stern{--an-grund:var(--surface)}',
    '.kastenkopf .stern{position:relative; flex:0 0 auto; display:flex; align-items:center; justify-content:center; '
    'box-sizing:border-box; padding:0; margin:-20px 0; font:inherit; cursor:pointer; color:var(--muted); '
    '-webkit-tap-highlight-color:transparent; transition:transform .12s, background-color .15s, '
    'border-color .15s, box-shadow .12s}',
    ".kastenkopf .stern::before{content:''; position:absolute}",
    '.kastenkopf .stern svg{display:block; flex:none; overflow:visible; pointer-events:none}',
    '.sternsym{overflow:visible}',
    '.sternsym path{fill:none; stroke:currentColor; stroke-linejoin:round}',
    '.sternsym.an path{fill:url(#sternGold); stroke:var(--stern-rand)}',
    '.kastenkopf .stern:focus-visible{outline:3px solid var(--primary); outline-offset:3px}',
    '@keyframes sternPop{0%{transform:scale(1)} 45%{transform:scale(1.22)} 100%{transform:scale(1)}}',
    '.kastenkopf .stern.pop svg{animation:sternPop .28s ease-out}',
    '@media (prefers-reduced-motion: reduce){ .kastenkopf .stern.pop svg{animation:none} }',
    '.kastenkopf .stern.v1{width:40px; height:40px; border-radius:50%; border:2px solid var(--line); '
    'background:var(--bg)}',
    '.kastenkopf .stern.v1::before{inset:-6px}',
    '.kastenkopf .stern.v1[aria-pressed="true"]{border-color:var(--accent); background:var(--an-grund)}',
    '.kastenkopf .stern.v1:active{transform:scale(.92)}',
    '#sternBox h2{display:flex; align-items:center; gap:7px}',
    '#sternBox h2 .sternsym{flex:none; color:var(--muted); position:relative; top:-1px}',
    '.topfleer .sternsym{display:inline-block; vertical-align:-3.5px; margin:0 1px; color:var(--muted)}',
    # Versteckt haelt er seinen Platz; !important gegen [hidden]{display:none !important}
    '.kastenkopf .stern[hidden]{display:flex !important; visibility:hidden}',
]


def test_stern_texte_in_allen_sprachen(sprachcodes):
    """Jede Sprache hat alle eigenen Texte, die Obergrenze steht als {n}
    darin, der Stern im leeren Kasten als {stern}, und die Zahl im Kasten
    hat Einzahl und Mehrzahl wie topf.anzahl."""
    import sprachen
    for code in sprachcodes:
        eigene = sprachen.TEXTE[code]
        for k in STERN_TEXTE:
            v = eigene.get(k)
            assert isinstance(v, str) and v.strip(), (code, k)
            assert len(v) <= 120, (code, k, v)
        assert "{n}" in eigene["stern.voll"], code
        assert eigene["stern.leer"].count("{stern}") == 1, code
        assert re.sub(r"\{\w+\}", "", eigene["stern.leer"]).count("{") == 0, code
        assert eigene["stern.anzahl"].count("|") == 1, code
        assert "<" not in "".join(eigene[k] for k in STERN_TEXTE), code


def test_stern_texte_deutsch_wie_entschieden():
    import sprachen
    de = sprachen.TEXTE["de"]
    assert {k: de[k] for k in STERN_TEXTE} == {
        "stern.knopf": "Markieren",
        "stern.titel": "Markiert",
        "stern.weg": "Nicht mehr markiert",
        "stern.desc": "Hier landen Aufgaben, die du mit dem Stern markierst. "
                      "Sie bleiben, bis du den Stern wieder wegnimmst.",
        "stern.leer": "Noch nichts markiert. Tippe in einer Aufgabe oben rechts auf {stern}.",
        "stern.rest": "markiert",
        "stern.anzahl": "Aufgabe markiert|Aufgaben markiert",
        "stern.symbol": "Stern",
        "stern.voll": "Schon {n} markiert",
    }


def test_stern_texte_nennen_oben_rechts(sprachcodes):
    """Seit dem 26.10.2026 steht der Stern oben rechts (Ajdin: "oben rechts
    neben den drachen"). Der leere Kasten sagt das in jeder Sprache, und
    keine sagt mehr "unten"."""
    import sprachen
    soll = {"de": "oben rechts", "en": "top right", "tr": "sağ üst", "sv": "upp till höger",
            "nl": "rechtsboven", "nb": "øverst til høyre", "da": "øverst til højre", "fr": "en haut à droite"}
    unten = ("unten", "bottom", "alt", "ner till", "onder", "nederst", "en bas")
    assert set(soll) == set(sprachcodes)
    for code in sprachcodes:
        leer = sprachen.TEXTE[code]["stern.leer"]
        assert soll[code] in leer, (code, leer)
        assert not any(u in leer for u in unten), (code, leer)


def test_topf_texte_unveraendert():
    """Der Kasten fuer Fehler bleibt, wie er ist (Ajdin, 19.10.2026)."""
    import sprachen
    de = sprachen.TEXTE["de"]
    assert de["topf.titel"] == "Wiederholen"
    assert de["topf.desc"] == ("Hier landen Aufgaben, die du falsch beantwortet hast. "
                               "Zweimal hintereinander richtig, dann sind sie raus.")
    assert de["topf.start"] == "Runde starten"
    assert de["topf.anzahl"] == "Aufgabe wartet|Aufgaben warten"
    assert de["topf.leer"] == ("Gerade gibt es nichts zu wiederholen. "
                               "Fehler aus Lektionen und Tests landen hier.")


def test_stern_css_genau_wie_entwurf(index_html):
    html = index_html.replace("\r\n", "\n")
    for regel in CSS_ENTWURF:
        assert regel in html, regel
    assert "merkbox" not in html, "Reste des verworfenen Kastens"


def test_stern_css_ohne_neue_pseudoklassen(index_html):
    """Alte WebViews (ab Android 7) verwerfen eine ganze Regel, wenn sie
    einen Teil davon nicht kennen - siehe .zmaj.mini in index.html."""
    regeln = [z for z in index_html.splitlines()
              if re.search(r"\.stern\b|\.sternsym\b|#sternBox|--stern-|--an-grund", z) and "{" in z]
    assert len(regeln) >= 20
    for z in regeln:
        assert not re.search(r":(is|where|has)\(|color-mix\(", z), z


def test_stern_knopf_steht_in_der_kopfzeile(index_html):
    """Seit dem 26.10.2026 spaet in der Kopfzeile der Karte (.kastenkopf),
    direkt hinter den Punkten (.tbar) - Ajdin: "nimm A". Damit ausserhalb
    des Aufgabenfelds (wegen weiterBeiTipp), nur in Lektion und Level-Test,
    nicht in der Einstufung. Leer und versteckt, bis sternKnopf() ihn auf
    eine Aufgabe stellt. Die Huelle um den Drachen (.zmajreihe, neben dem
    Drachen am 26.10.2026) ist wieder weg: der Drache steht wie in der
    Einstufung direkt in der Karte. Die Leiste darunter hat nur "abbrechen"
    und den leeren Platzhalter, genau wie vor dem 19.10.2026."""
    for ort, herz, bar, drache, knopf, body in (("l", "lHerz", "lBar", "zmajLesson", "lStern", "lBody"),
                                                ("t", "tHerz", "tBar", "zmajTest", "tStern", "tBody")):
        karte = ('<div class="card"><div class="kastenkopf"><div class="kastenherz" id="%s"></div>'
                 '<div class="tbar" id="%s"></div>'
                 '<button type="button" class="stern v1" id="%s" aria-pressed="false" hidden>%s</button></div>'
                 '<div class="zmaj mini idle" id="%s"></div><div id="%s"></div></div>'
                 % (herz, bar, knopf, SVG_LEER, drache, body))
        assert karte in index_html, knopf
    assert ('<div class="card"><div class="kastenkopf"><div class="kastenherz platzhalter" aria-hidden="true"></div>'
            '<div class="tbar" id="eBar"></div></div><div class="zmaj mini idle" id="zmajEinst"></div>'
            '<div id="eBody"></div></div>') in index_html, "die Einstufung bekommt keinen Stern"
    assert '<div class="nav"><button id="lQuit" data-t="lektion.abbrechen"></button><span></span></div>' in index_html
    assert '<div class="nav"><button id="tQuit" data-t="test.abbrechen"></button><span></span></div>' in index_html
    assert '<div class="nav"><button id="eQuit" data-t="einst.abbrechen"></button><span></span></div>' in index_html
    assert index_html.count('class="stern v1"') == 2
    assert 'class="zmajreihe"' not in index_html
    regeln = [z for z in index_html.splitlines() if "{" in z and not z.lstrip().startswith(("/*", "-", "*"))]
    assert not [z for z in regeln if ".zmajreihe" in z], "Regeln fuer die alte Huelle"
    assert 'class="stern' not in index_html.split('id="einstufungView"')[1].split("</section>")[0]
    # 24 px im Knopf, wie in der gewaehlten Vorschau
    assert "  b.innerHTML = sternSvg(an, 24);" in index_html


def test_stern_nicht_mehr_in_der_leiste(index_html):
    """Die alte Lage (19.10. bis 26.10.2026) ist ganz weg: kein Stern in einer
    .nav, keine Regel fuer ".nav .stern" und nicht mehr die Ausrichtung der
    Leiste, die es nur fuer ihn gab."""
    html = index_html.replace("\r\n", "\n")
    assert ".nav .stern" not in html
    assert "#lesson .nav, #test .nav{align-items:center}" not in html
    for zeile in html.split("\n"):
        if '<div class="nav">' in zeile:
            assert "stern" not in zeile, zeile


def test_goldverlauf_einmal_und_sichtbar(index_html):
    """Der Verlauf steht genau einmal im Dokument, und nicht in einem
    display:none-Kasten - dort malt Chrome ihn nicht."""
    assert index_html.count('id="sternGold"') == 1
    assert ('<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>'
            '<linearGradient id="sternGold" x1="0" y1="0" x2="0" y2="1">'
            '<stop offset="0" style="stop-color:var(--stern-gold-hell)"/>'
            '<stop offset="1" style="stop-color:var(--stern-gold-tief)"/></linearGradient></defs></svg>') in index_html
    assert "const STERN_PFAD = '%s';" % PFAD in index_html


def test_kasten_wie_der_bestehende(index_html):
    """#sternBox ist eine schlichte .section wie #topfBox und wird mit
    denselben Klassen gebaut."""
    # Zeilenenden angleichen: unter Linux (CI) checkt git die Datei mit LF
    # aus, unter Windows mit CRLF. 23.10.2026, PR #55.
    html = index_html.replace("\r\n", "\n")
    assert ('      <div class="section" id="topfBox"></div>\n'
            '      <div class="section" id="sternBox"></div>\n') in html
    rumpf = html.split("function sternKasten(){")[1].split("\n}\n")[0]
    for klasse in ('<div class="desc">', '<div class="topfzahl">', '<div class="topfwort">',
                   '<div class="topfleer">', '<div class="row"><button class="btn know" id="sternLos"',
                   '<div class="note">', '<div class="row schmal">'):
        assert klasse in rumpf, klasse


def test_stern_grenzen(index_html):
    assert "const STERN_MAX = 300;" in index_html
    assert "const TOPF_RUNDE = 10," in index_html
    # die Sicherungsdatei bleibt version 1 - seit 19.10.2026 baut sie
    # sicherungObjekt(), das auch die Cloud-Sicherung benutzt
    assert "return {app:'zmaj', version:1," in index_html
