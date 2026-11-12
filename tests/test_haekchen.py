# -*- coding: utf-8 -*-
"""Fehlende Haekchen beim Tippen: "pada kisa" fuer "Pada kiša".

Die Regel steht seit dem Start in matches() (web/index.html): fehlen nur
Haekchen (š, č, ć, ž, đ als d), Gross/klein, Satzzeichen am Ende, Komma oder
Bindestrich, ist die Antwort 'almost' - sie zaehlt als richtig, kostet kein
Leben, und die Rueckmeldung zeigt die Schreibweise ("Richtig! Mit
Sonderzeichen: Pada kiša", task.fast). Davon getrennt ist "Fast richtig!"
(task.fast_richtig, fastRichtig()): genau ein Tippfehler neben der Antwort
gibt einmal einen Hinweis und einen zweiten Versuch - fuer jedes Wort, auch
ein anderes echtes Wort oder eine andere Endung (Ajdin am 27.10.2026: "mach
doch einfach nur fast richtig dann bezieht es sich auf alle wörter"). Ein
fehlendes Haekchen ist nie dieser eine Tippfehler, es zaehlt gar nicht mit.

Getippt wird nur in zwei Aufgaben, der Schreibaufgabe ('type') und dem
Lueckensatz ('gap'), und beide gehen in Lektion, Wiederholen, Level-Test,
Einstufung und Zahnarzt durch dasselbe renderTask(). Satzbau (Kacheln) und
Grammatik sind Antippen, nicht Tippen.

Gefunden und behoben bei der Pruefung am 12.11.2026:
- Zahlwoerter: "sest" fuer "šest" war 'ok' statt 'almost' (zahlWert()
  vergleicht selbst ohne Haekchen), die App zeigte "Tačno!" ohne die
  Schreibweise.
- Ziffer und fehlendes Haekchen zusammen ("5 brace" fuer "pet braće") war
  'no' und kostete ein Leben.
- Bei einer weiteren Antwort ("cao" fuer "Doviđenja / Ćao") nannte die
  Rueckmeldung die erste Antwort, also ein anderes Wort als das getippte.
- Ein Haekchen als eigenes Zeichen (NFD) war nur 'almost', obwohl richtig.

Die Pruefung laeuft in node auf genau den Funktionen aus web/index.html. Den
Ablauf im Browser pruefen tests_e2e/test_tippfehler.py und
tests_e2e/test_haekchen.py.
"""
import json
import re
import shutil
import subprocess
import unicodedata

import pytest


def _html(index_html):
    return index_html.replace("\r\n", "\n")


def _stueck(html, anfang, ende):
    """Von anfang (einmal vorhanden) bis vor ende."""
    assert html.count(anfang) == 1, anfang
    a = html.index(anfang)
    e = html.index(ende, a)
    return html[a:e]


def _bloecke(index_html):
    html = _html(index_html)
    return "\n".join([
        _stueck(html, "const strip = s =>", "\n/* ---------- Gesprochenes vergleichen"),
        _stueck(html, "const ZAHL_EINER = ", "\n/* ---- Zahlen, die wechseln"),
        _stueck(html, "const typable = w =>", "\n"),
        _stueck(html, "function matches(guess, answer){", "\n/* ---------- Fast richtig: erst ein Hinweis"),
        _stueck(html, "function einTippfehler(a, b){", "\n/* So lange nach dem Hinweis"),
    ])


# Wie renderTask() bei 'type' und 'gap' entscheidet (test_ablauf_wie_in_der_app
# haelt beide Stellen daran fest): leer, sonst der Hinweis, wenn matches() 'no'
# sagt und fastRichtig() einen Tippfehler sieht, sonst richtig, richtig mit
# Sonderzeichen oder falsch.
NODE = r"""
const ein = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const f = new Function(ein.bloecke +
  '\nreturn {matches, fastGleich, gemeinteAntwort, fastRichtig, einTippfehler, clean, typable};')();
function bewertung(eingabe, antworten){
  const r = f.matches(eingabe, antworten);
  if(r === 'leer') return ['leer', null];
  if(r === 'no' && f.fastRichtig(eingabe, antworten)) return ['hinweis', null];
  if(r === 'ok') return ['richtig', null];
  if(r === 'almost') return ['sonderzeichen', f.gemeinteAntwort(eingabe, antworten)];
  return ['falsch', null];
}
const aus = {
  faelle: ein.faelle.map(([antworten, eingabe]) => bewertung(eingabe, antworten)),
  inhalt: ein.inhalt.map(([antworten, eingabe]) => bewertung(eingabe, antworten)),
  typable: ein.woerter.map(bs => f.typable({bs})),
  nie_tippfehler: ein.faelle.map(([antworten, eingabe]) => f.fastRichtig(eingabe, antworten)),
};
process.stdout.write(JSON.stringify(aus));
"""

S = "sonderzeichen"

# (Antworten wie an matches() uebergeben, Eingabe, Stufe, gezeigte Schreibweise)
FAELLE = [
    # Das Beispiel aus der Pruefung: Wort "Es regnet" = "Pada kiša"
    ("Pada kiša", "pada kisa", S, "Pada kiša"),
    ("Pada kiša", "Pada kisa", S, "Pada kiša"),
    ("Pada kiša", "PADA KISA", S, "Pada kiša"),
    ("Pada kiša", "pada kisa.", S, "Pada kiša"),
    ("Pada kiša", "  pada   kisa!  ", S, "Pada kiša"),
    ("Pada kiša", "pada kisa?", S, "Pada kiša"),
    ("Pada kiša", "pada, kisa", S, "Pada kiša"),      # Komma wie ein Haekchen (06.11.2026)
    ("Pada kiša", "pada-kisa", S, "Pada kiša"),
    ("Pada kiša", "pada kişa", S, "Pada kiša"),       # tuerkische Tastatur: ş statt š
    ("Pada kiša", "pada kiša", "richtig", None),
    ("Pada kiša", "PADA KIŠA", "richtig", None),
    ("Pada kiša", "Pada kiša!", "richtig", None),
    ("Pada kiša", "Pada kiša", "richtig", None),  # š als s + Haekchen-Zeichen (NFD)
    ("Pada kiša", "pada kisq", "hinweis", None),      # Tippfehler UND fehlendes Haekchen
    ("Pada kiša", "pada kisq! ", "hinweis", None),    # Leerzeichen hinter dem "!" (bis 12.11.2026 kein Hinweis)
    ("Pada kiša", "Pada kišq.  ", "hinweis", None),
    ("Pada kiša", "pada kša", "hinweis", None),
    ("Pada kiša", "padakisa", "hinweis", None),       # das Leerzeichen ist der eine Tippfehler
    ("Pada kiša", "pada kosq", "falsch", None),
    ("Pada kiša", "   ", "leer", None),
    # ćevapi
    ("ćevapi", "cevapi", S, "ćevapi"),
    ("ćevapi", "Cevapi", S, "ćevapi"),
    ("ćevapi", "CEVAPI", S, "ćevapi"),
    ("ćevapi", "cevapi!", S, "ćevapi"),
    ("ćevapi", "čevapi", S, "ćevapi"),                 # falsches Haekchen zaehlt wie keins
    ("ćevapi", "Ćevapi", "richtig", None),
    ("ćevapi", "ĆEVAPI", "richtig", None),
    ("ćevapi", "ćevapi", "richtig", None),
    ("ćevapi", "cevapu", "hinweis", None),
    ("ćevapi", "cevap", "hinweis", None),
    ("ćevapi", "kebapi", "falsch", None),
    # džezva: dž ohne Haekchen ist dz
    ("džezva", "dzezva", S, "džezva"),
    ("džezva", "DZEZVA", S, "džezva"),
    ("džezva", "Dzezva.", S, "džezva"),
    ("džezva", "džezva", "richtig", None),
    ("džezva", "DŽEZVA", "richtig", None),
    ("džezva", "dezva", "hinweis", None),
    ("džezva", "dzezvq", "hinweis", None),
    # đ: d gilt, dj ist ein Buchstabe zu viel (Entscheidung 06.11.2026)
    ("Doviđenja", "dovidenja", S, "Doviđenja"),
    ("Doviđenja", "DOVIDENJA", S, "Doviđenja"),
    ("Doviđenja", "dovidjenja", "hinweis", None),
    # Weitere Antworten: gezeigt wird die, die getippt wurde
    ("Doviđenja / Ćao", "cao", S, "Ćao"),
    ("Doviđenja / Ćao", "Cao!", S, "Ćao"),
    ("Doviđenja / Ćao", "dovidenja", S, "Doviđenja"),
    ("Doviđenja / Ćao", "ćao", "richtig", None),
    ("U zdravlje! / Živjeli!", "zivjeli", S, "Živjeli!"),
    ("amidža / stric / striko / adžo", "adzo", S, "adžo"),
    ("amidža / stric / striko / adžo", "amidza", S, "amidža"),
    ("Račun, molim", "Racun molim", S, "Račun, molim"),
    ("sogan-dolma", "sogandolma", S, "sogan-dolma"),
    # Lueckensaetze: "Pada ___." mit kiša, "Kahva je u ___." mit džezvi
    ("kiša", "kisa", S, "kiša"),
    ("kiša", "KISA.", S, "kiša"),
    ("kiša", "kisq", "hinweis", None),
    ("kiša", "kosa", "hinweis", None),                 # ein echtes Wort, trotzdem fast richtig
    ("džezvi", "dzezvi", S, "džezvi"),
    ("Šta", "sta", S, "Šta"),
    ("ću", "cu", S, "ću"),                             # Haekchen gelten auch unter 4 Buchstaben
    ("ću", "cy", "falsch", None),                      # der Tippfehler-Hinweis erst ab 4
    # Zahlwoerter: ohne Haekchen wie jedes andere Wort, Ziffern bleiben richtig
    ("četiri", "cetiri", S, "četiri"),
    ("četiri", "Cetiri.", S, "četiri"),
    ("četiri", "4", "richtig", None),
    ("četiri", "četiri", "richtig", None),
    ("četiri", "cetri", "hinweis", None),
    ("šest", "sest", S, "šest"),
    ("šest", "6", "richtig", None),
    ("šesnaest", "sesnaest", S, "šesnaest"),
    ("Dvije", "dva", "richtig", None),
    ("Dvije", "2", "richtig", None),
    ("pet", "5", "richtig", None),
    ("pet", "sest", "falsch", None),
    ("pet braće", "5 braće", "richtig", None),
    ("pet braće", "5 brace", S, "pet braće"),
    ("sedam ćevapa", "7 cevapa", S, "sedam ćevapa"),
]


def _ohne_haekchen(text):
    t = text.replace("đ", "d").replace("Đ", "D")
    t = unicodedata.normalize("NFD", t)
    return unicodedata.normalize("NFC", re.sub("[̀-ͯ]", "", t))


def _norm(text):
    """Wie norm() in matches()."""
    t = re.sub(r"[.!?…]+$", "", unicodedata.normalize("NFC", text).lower())
    return re.sub(r"\s+", " ", t).strip()


def _sauber(text):
    """Wie clean() in web/index.html."""
    t = _ohne_haekchen(text.lower())
    t = re.sub(r"[.!?…]+$", "", t)
    return re.sub(r"\s+", " ", re.sub("[,-]", " ", t)).strip()


def _inhalt(daten):
    """Jede Antwort im Inhalt mit Haekchen, ohne sie getippt: (Antworten,
    Eingabe, Antwort). Woerter nur, wenn sie als Schreibaufgabe kommen koennen
    (typable(), wird in node nachgeprueft), Lueckensaetze alle."""
    aus, woerter = [], []
    for kat in daten["kategorien"]:
        for w in kat["words"]:
            woerter.append(w["bs"])
            alts = [w["bs"]] + list(w.get("auch") or [])
            for a in alts:
                for form in a.split(" / "):
                    if _ohne_haekchen(form) != form:
                        aus.append((" / ".join(alts), _ohne_haekchen(form), form, w["bs"]))
    for s in daten["saetze"]:
        alts = [s["answer"]] + list(s.get("auch") or [])
        for a in alts:
            if _ohne_haekchen(a) != a:
                aus.append((" / ".join(alts), _ohne_haekchen(a), a, None))
    return aus, woerter


@pytest.fixture(scope="module")
def node_ergebnis(index_html, grunddaten):
    if not shutil.which("node"):
        pytest.skip("node fehlt")
    inhalt, woerter = _inhalt(grunddaten)
    ein = {"bloecke": _bloecke(index_html), "faelle": [f[:2] for f in FAELLE],
           "inhalt": [i[:2] for i in inhalt], "woerter": woerter}
    aus = subprocess.run(["node", "-e", NODE], input=json.dumps(ein), capture_output=True, text=True,
                         encoding="utf-8", check=True, timeout=120)
    erg = json.loads(aus.stdout)
    erg["_inhalt"] = inhalt
    erg["_typable"] = dict(zip(woerter, erg["typable"]))
    return erg


@pytest.mark.parametrize("nr", range(len(FAELLE)), ids=["%s|%s" % f[:2] for f in FAELLE])
def test_haekchen_und_tippfehler(node_ergebnis, nr):
    antworten, eingabe, stufe, wort = FAELLE[nr]
    assert node_ergebnis["faelle"][nr] == [stufe, wort], (antworten, eingabe)


def test_fehlendes_haekchen_ist_nie_der_eine_tippfehler(node_ergebnis):
    """fastRichtig() sieht in einem fehlenden Haekchen keinen Tippfehler -
    sonst kaeme statt "richtig" erst der Hinweis. (Ein fehlender Bindestrich
    oder eine Ziffer ist etwas anderes, hier nur die Haekchen.)"""
    gezaehlt = 0
    for (antworten, eingabe, stufe, _), tipp in zip(FAELLE, node_ergebnis["nie_tippfehler"]):
        if stufe in (S, "richtig") and _sauber(eingabe) in [_sauber(a) for a in antworten.split(" / ")]:
            gezaehlt += 1
            assert tipp is False, (antworten, eingabe)
    assert gezaehlt > 40, gezaehlt


def test_jede_antwort_ohne_haekchen_zaehlt(node_ergebnis):
    """Im ganzen Inhalt: jede Antwort, die getippt werden kann, gilt ohne
    Haekchen als richtig - nie falsch, nie erst der Hinweis. Und die
    Rueckmeldung nennt die getippte Antwort mit ihren Haekchen (oder eine
    weitere, die ohne Haekchen genauso aussieht)."""
    fehler, gezaehlt = [], 0
    for (antworten, eingabe, form, bs), (stufe, wort) in zip(node_ergebnis["_inhalt"], node_ergebnis["inhalt"]):
        if bs is not None and not node_ergebnis["_typable"][bs]:
            continue
        gezaehlt += 1
        if stufe == "richtig":
            # Nur, wenn eine andere Antwort genau so heisst wie das Getippte.
            if _norm(eingabe) not in [_norm(a) for a in antworten.split(" / ")]:
                fehler.append((antworten, eingabe, stufe))
        elif stufe != S or _sauber(wort) != _sauber(eingabe):
            fehler.append((antworten, eingabe, stufe, wort))
    assert gezaehlt > 1000, gezaehlt
    assert fehler == [], fehler[:20]


def _zweig(html, typ):
    """Der Zweig von renderTask() fuer typ, bis zum naechsten oder zum Ende."""
    anfang = "  if(task.typ==='" + typ + "'){"
    assert html.count(anfang) == 1, typ
    a = html.index(anfang)
    enden = [html.find(e, a + 1) for e in ("\n  if(task.typ==='", "\n}\n")]
    return html[a:min(e for e in enden if e > 0)]


def test_ablauf_wie_in_der_app(index_html):
    """Beide Stellen, an denen getippt wird, entscheiden gleich: matches(),
    dann der Hinweis (vertippt mit fastRichtig()), dann 'ok' oder 'almost'
    als richtig, und bei 'almost' gemeinteAntwort() mit denselben Antworten."""
    html = _html(index_html)
    render = _stueck(html, "function renderTask(task, body, done, opts={}){", "\n/* =================== LEKTION")
    assert render.count("<input") == 2 and html.count('id="xIn"') == 2
    assert "if(!paar && !fastRichtig(inp.value, antworten)) return false;" in render
    for typ, antworten in (("type", "auchOk"), ("gap", "antworten")):
        zweig = _zweig(html, typ)
        assert "<input" in zweig, typ
        assert "const r=matches(inp.value, " + antworten + ");" in zweig, typ
        assert "if(vertippt(r, " + antworten in zweig, typ
        assert "const ok = r==='ok' || r==='almost';" in zweig, typ
        assert "r==='almost' ? gemeinteAntwort(inp.value, " + antworten + ")" in zweig, typ
    for typ in ("kacheln", "gram", "mc", "mcrev", "listen", "speak"):
        assert "<input" not in _zweig(html, typ), typ


def test_lektion_test_und_einstufung_gehen_durch_render_task(index_html):
    html = _html(index_html)
    for aufruf in ("renderTask(task, $('lBody'), ", "renderTask(Tx.qs[Tx.i], $('tBody'), ",
                   "renderTask(Ex.qs[Ex.i], body, "):
        assert html.count(aufruf) == 1, aufruf
    # Der Level-Test stellt Schreibaufgaben.
    assert "if(typable(p.w) && i%4===2) typ = 'type';" in _stueck(html, "function buildTest(){", "\nfunction testBar()")
