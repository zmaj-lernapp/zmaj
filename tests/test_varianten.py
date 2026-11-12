# -*- coding: utf-8 -*-
"""Andere bosnische Wörter, die beim Tippen genauso gelten (varianten.py, 12.11.2026).

Bis dahin nahm „Voda je u ___.“ nur flaši - boci war falsch und kostete ein
Leben -, und „Pijem kahvu“ nahm nicht „Pijem kafu“, obwohl das Wort selbst
„kahva / kafa“ heißt. Ajdin: „die ganze app nochmal danach kontrollieren“.
Eingetragen sind nur die eindeutigen Paare; die fraglichen entscheidet er.

Getippt wird an zwei Stellen, beide in renderTask(): Schreibaufgabe
(annehmbar()) und Lückensatz. Sie laufen in Lektion, Level-Test, Einstufung,
Fehler-Topf, „Heute fällig“, Markiert und im Zahnarzt-Teil. Beim Satzbau wird
nichts getippt, dort zählt nur, dass die andere Form keine falsche Kachel ist.
In der Auswahl hält geschwister() sie aus den falschen Knöpfen, das Sprechen
bleibt. Den Ablauf in der App prüft tests_e2e/test_varianten.py.

Die Schnappschüsse unten sind ALLES, was dadurch neu richtig wird. Kommt etwas
dazu oder fällt etwas weg, scheitert der Test - dann bitte prüfen und hier
nachtragen.
"""
import ast
import glob
import io
import json
import os
import re
import shutil
import subprocess

import pytest

import inhalt
import varianten

# Schreibaufgabe: Kennung des Wortes -> zusätzliche Antworten
WOERTER = {
    "braun:kafena": ["smeđa"],
    "rosa:roza": ["ružičasta"],
    "jetzt:sada": ["sad"],
    "abend:večer": ["veče"],
    "nachbar:komšija": ["susjed"],
    "hose:pantalone": ["hlače"],
    "grüne bohnen:boranija": ["mahune"],
    "mayonnaise:majonez": ["majoneza"],
    "senf:senf": ["gorušica"],
    "thunfisch:tunjevina": ["tuna"],
    "bosnischer kaffee:bosanska kahva": ["bosanska kafa"],
    "hahn:horoz": ["pijetao"],
    "lamm:jagnje": ["janje"],
    "insel:ostrvo": ["otok"],
    "luft:zrak": ["vazduh"],
    "flasche:flaša": ["boca"],
    "decke (bettdecke):deka": ["pokrivač"],
    "waschbecken:lavabo": ["umivaonik"],
    "nachbarin:komšinica": ["susjeda"],
    "leiter:merdevine": ["ljestve"],
    "schraube:šaraf": ["vijak"],
    "säge:testera": ["pila"],
    "drucker:štampač": ["printer"],
    "nie:nikad": ["nikada"],
    "ich trinke kaffee:Pijem kahvu": ["Pijem kafu"],
    "ich rufe den arzt:Zovem doktora": ["Zovem ljekara"],
    "eine tasse kaffee:šolja kahve": ["šolja kafe"],
    "viele menschen:mnogo ljudi": ["puno ljudi"],
    "viel / viele:mnogo": ["puno"],
    "ich helfe meiner mutter:Pomažem majci": ["Pomažem mami"],
    "am nachmittag:popodne": ["poslijepodne"],
    "ein kaffee:jedna kahva": ["jedna kafa"],
    "zwei kaffee:dvije kahve": ["dvije kafe"],
    "zweimal:dva puta": ["dvaput"],
    "interessant:zanimljivo": ["interesantno"],
    "gepäck:prtljag": ["prtljaga"],
    "büro:kancelarija": ["ured"],
    "ingenieur:inženjer": ["inžinjer"],
    "computer:računar": ["kompjuter"],
    "der kaffee ist heiß:Kahva je vruća": ["Kafa je vruća"],
    "gehen wir einen kaffee trinken:Idemo na kahvu": ["Idemo na kafu"],
    "nachbarn (mehrzahl):komšije": ["susjedi"],
}

# Lückensatz: Text -> zusätzliche Antworten
LUECKEN = {
    "Jednu ___, molim.": ["kafu"],
    "Moj ___ je dobar čovjek.": ["susjed"],
    "___ za pasoš je trideset maraka.": ["Naknada"],
    "Pijem ___.": ["kafu"],
    "Volim svoju ___.": ["mamu"],
    "Pomažem ___.": ["mami"],
    "Kečap i ___, molim.": ["gorušicu"],
    "Uzet ću ___.": ["somun"],
    "Voda je u ___.": ["boci"],
    "Koja je ___ za WiFi?": ["lozinka"],
    "Švicarska je mala ___.": ["zemlja"],
}

# Satzbau: Satz -> was zu "ohne" dazukommt. Fast alles sperrte die App schon
# über "auch" und " / " der Wörter (kahva / kafa, majka mit auch mama); neu
# ist puno neben mnogo.
KACHELN = {
    "Kako si, mama?": ["majka"],
    "Kahva je crna.": ["kafa"],
    "Mama je u kuhinji.": ["majka"],
    "Doktor je u bolnici.": ["ljekar"],
    "Brz oporavak, mama!": ["majka"],
    "Kahva je u džezvi.": ["kafa"],
    "Uzet ću pogaču.": ["somun"],
    "Koja je šifra za WiFi?": ["lozinka"],
    "Moja mama voli kruške.": ["majka"],
    "Moja majka i moj babo.": ["mama"],
    "Kahva bez šećera.": ["kafa"],
    "Kahva bez mlijeka.": ["kafa"],
    "Ima mnogo djece": ["puno"],
    "Na pijaci ima mnogo ljudi.": ["puno"],
    "Kahva sa šećerom.": ["kafa"],
    "Kahva je jako vruća.": ["kafa"],
    "Može li jedna kahva?": ["kafa"],
    "Švicarska je mala država.": ["zemlja"],
    "Moja majka je Bosanka.": ["mama"],
    "Taksa za pasoš je trideset maraka.": ["naknada"],
}


def _woerter(daten):
    for kat in daten["kategorien"] + daten["zahnarzt"]["kategorien"]:
        yield from kat["words"]


def test_liste_und_kennungen_sauber(grunddaten):
    assert varianten.pruefe_varianten(grunddaten) == []
    assert varianten.pruefe_kennungen(grunddaten) == []


def test_schreibaufgaben_genau_so(alle_daten):
    """In jeder Sprache dieselben - das Bosnische wird nie übersetzt."""
    for code, daten in alle_daten.items():
        assert {w["id"]: w["auch_var"] for w in _woerter(daten) if "auch_var" in w} == WOERTER, code


def test_lueckensaetze_genau_so(alle_daten):
    for code, daten in alle_daten.items():
        assert {s["text"]: s["auch_var"] for s in daten["saetze"] if "auch_var" in s} == LUECKEN, code


def test_satzbau_sperrt_genau_so(grunddaten):
    import vokabeln
    vorher = {s["bs"]: list(s.get("ohne") or []) for s in inhalt.satzbau_fuer_app(vokabeln.SATZBAU)}
    neu = {}
    for s in grunddaten["satzbau"]:
        alt = vorher[s["bs"]]
        assert s.get("ohne", [])[:len(alt)] == alt, s["bs"]      # was die Autoren sperren, bleibt vorn
        if s.get("ohne", []) != alt:
            neu[s["bs"]] = s["ohne"][len(alt):]
    assert neu == KACHELN


def test_nur_was_getippt_wird_und_nichts_doppelt(grunddaten):
    for w in _woerter(grunddaten):
        if "auch_var" not in w:
            continue
        assert varianten.tippbar(w["bs"]), w["bs"]
        da = {x.lower() for x in [w["bs"]] + list(w.get("auch") or [])}
        for v in w["auch_var"]:
            assert " / " not in v and v == v.strip() and v.lower() not in da, (w["bs"], v)
    for s in grunddaten["saetze"]:
        for v in s.get("auch_var", []):
            assert " / " not in v and v.lower() not in {s["answer"].lower()} | {a.lower() for a in s.get("auch", [])}


def test_was_ajdin_ausgeschlossen_hat_bleibt_draussen(grunddaten, wurzel):
    """zaehlt_nicht der Wortschatz-Pakete (tests/test_paket10.py bis 20): Ajdin hat
    diese Formen beim Tippen ausdrücklich nicht freigegeben."""
    verboten = set()
    for pfad in glob.glob(os.path.join(wurzel, "tests", "test_paket*.py")):
        baum = ast.parse(io.open(pfad, encoding="utf-8").read())
        for knoten in baum.body:
            if isinstance(knoten, ast.Assign) and any(getattr(z, "id", "") == "ZAEHLT_NICHT" for z in knoten.targets):
                for formen in ast.literal_eval(knoten.value).values():
                    verboten |= {f.lower() for f in formen}
    assert len(verboten) > 10, verboten
    alle = [v.lower() for w in _woerter(grunddaten) for v in w.get("auch_var", [])]
    alle += [v.lower() for s in grunddaten["saetze"] for v in s.get("auch_var", [])]
    assert not verboten & set(alle)
    gebeugt = {f.lower() for p in varianten.VARIANTEN for f in varianten.faelle(p["b"]).values()}
    assert not verboten & gebeugt


# --- der Mechanismus an kleinen Beispielen ---

def _z(antworten, wort=True, kennung="x", fall=None):
    mehr, probleme = varianten.zusatz(antworten, kennung, wort, fall=fall)
    return mehr, probleme


@pytest.mark.parametrize("antwort, wort, mehr", [
    ("flaša", True, ["boca"]),
    ("Daj mi flašu", True, ["Daj mi bocu"]),             # gebeugt, mitten im Satz
    ("Flašu", False, ["Bocu"]),                          # Großschreibung bleibt
    ("Voda je u flaši.", True, ["Voda je u boci."]),
    ("flašica", True, []),                               # nur ganze Wörter
    ("kahvana", True, []),
    ("kahva-bar", True, []),                             # Bindestrich hält zusammen
    ("komšija", True, ["susjed"]),                       # allein: der Nominativ
    ("komšije", True, ["susjedi"]),                      # Gen. Sg. oder Nom. Pl. - allein Nom. Pl.
    ("dva puta dnevno", True, ["dvaput dnevno"]),        # zwei Wörter
    ("dva", True, []),
    ("roza", True, ["ružičasta"]),                       # ALLEIN
    ("roza haljina", True, []),
    ("roza", False, []),                                 # ALLEIN nie im Lückensatz
    ("Dobro veče", True, []),                            # nur von a nach b
    ("Pijem kafu", True, []),
    ("Pijem kahvu sada", True, ["Pijem kahvu sad", "Pijem kafu sada", "Pijem kafu sad"]),
    ("senf", True, []),                                  # Paar mit Kennungen: nur dort
    ("šifra", False, []),
    ("taksi", True, []),                                 # das Taxi, nicht taksa
])
def test_zusatz_an_beispielen(antwort, wort, mehr):
    assert _z([antwort], wort) == (mehr, [])


def test_zusatz_fall_und_kennung():
    # komšija im Lückensatz: Nom. Sg. (susjed) oder Gen. Pl. (susjeda) - ohne Fall nichts, aber ein Befund
    mehr, probleme = _z(["komšija"], False)
    assert mehr == [] and len(probleme) == 1 and "FALL angeben" in probleme[0]
    assert _z(["komšija"], False, fall="sg_nom") == (["susjed"], [])
    assert _z(["komšija"], False, fall="pl_gen") == (["susjeda"], [])
    assert _z(["flaši"], False) == (["boci"], [])          # Dat. und Lok. - beides boci
    assert _z(["šifra"], False, kennung="Koja je ___ za WiFi?") == (["lozinka"], [])
    assert _z(["senf"], True, kennung="senf:senf") == (["gorušica"], [])
    assert _z(["senf"], False, kennung="Kečap i ___, molim.", fall="sg_akk") == (["gorušicu"], [])


def test_hoechstens_zwei_woerter_je_antwort():
    mehr, probleme = _z(["sada kahvu flašu"], True)
    assert mehr == [] and len(probleme) == 1


def test_befund_bei_wort_mit_anderer_bedeutung():
    """Eine Form von a, die die App als eigenes Wort kennt, meldet pruefe_varianten()."""
    daten = {"kategorien": [{"id": "x", "words": [
        {"id": "küken:kahvu", "bs": "kahvu", "de": "Küken"},
        {"id": "tisch:sada", "bs": "sada", "de": "Tisch"}, {"id": "jetzt:sada", "bs": "sada", "de": "jetzt"},
        {"id": "nie / niemals:nikad", "bs": "nikad", "de": "nie / niemals"},
        {"id": "nie:nikad", "bs": "nikad", "de": "nie"}]}],
        "saetze": []}
    probleme = varianten.pruefe_varianten(daten)
    assert any("'kahvu' ist in der App ein eigenes Wort" in p for p in probleme), probleme
    assert any("'sada' steht in der App bei Wörtern mit verschiedener Bedeutung" in p for p in probleme), probleme
    assert not any("'nikad'" in p for p in probleme), probleme     # „nie“ steckt in beiden Bedeutungen


def test_paare_beugen_gleich():
    for p in varianten.VARIANTEN:
        a, b = varianten.faelle(p["a"]), varianten.faelle(p["b"])
        assert set(a) == set(b), p["beleg"]


# --- die App hängt sie an ---

def _html(index_html):
    return index_html.replace("\r\n", "\n")


def test_app_haengt_sie_an_beiden_tippstellen_an(index_html):
    html = _html(index_html)
    assert "return [w.bs, ...gleich, ...(w.auch || []), ...(w.auch_var || [])];" in html
    assert "const antworten = [s.answer, ...(s.auch || []), ...(s.auch_var || [])].join(' / ');" in html
    assert "const _auchAlle = w => [...(w.auch || []), ...(w.auch_var || [])];" in html
    assert html.count("_auchAlle(") == 2              # in geschwister() für beide Richtungen
    # kachelAblenker() nimmt "ohne" wie bisher
    assert "...(s.ohne || []).map(kachelNorm)" in html


def test_tippbar_wie_in_der_app(index_html):
    """varianten.tippbar() ist typable() aus web/index.html. Ändert sich das
    eine, muss das andere mit - sonst fehlen Varianten oder stehen umsonst da."""
    assert "const typable = w => w.bs.length<=14 && !/[.…→]/.test(w.bs) && !w.bs.includes(' / ');" in _html(index_html)
    assert varianten.TIPPBAR_LAENGE == 14 and varianten.NIE_TIPPBAR.pattern == "[.…→]"


# --- matches() aus web/index.html in node, mit dem echten Inhalt ---

def _stueck(html, anfang, ende):
    assert html.count(anfang) == 1, anfang
    a = html.index(anfang)
    return html[a:html.index(ende, a)]


NODE = r"""
const ein = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const f = new Function(ein.bloecke + '\nreturn {matches, zahlWert, fastRichtig};')();
process.stdout.write(JSON.stringify({
  faelle: ein.faelle.map(([eingabe, antworten]) => f.matches(eingabe, antworten)),
  zahlen: ein.zahlen.map(x => f.zahlWert(x)),
}));
"""

ZAHLEN = {"dvadeset jedan": 21, "dvadeset i jedan": 21, "Trideset i pet": 35, "devedeset i devet": 99,
          "dvadeset i": None, "i jedan": None, "pet i dva": None, "sto i jedan": None, "dvadeset i i jedan": None,
          "dvadeset ili jedan": None}


@pytest.fixture(scope="module")
def node_ergebnis(index_html, grunddaten):
    if not shutil.which("node"):
        pytest.skip("node fehlt")
    html = _html(index_html)
    bloecke = "\n".join([
        _stueck(html, "const strip = s =>", "\n/* ---------- Gesprochenes vergleichen"),
        _stueck(html, "const ZAHL_EINER = ", "\n/* ---- Zahlen, die wechseln"),
        _stueck(html, "function matches(guess, answer){", "\n/* ---------- Fast richtig: erst ein Hinweis"),
        _stueck(html, "function einTippfehler(a, b){", "\n/* So lange nach dem Hinweis"),
    ])
    faelle = []
    for w in _woerter(grunddaten):
        if "auch_var" in w:
            vorher = [w["bs"]] + list(w.get("auch") or [])
            for v in w["auch_var"]:
                faelle.append((v, " / ".join(vorher), "no"))                      # bis 12.11.2026
                faelle.append((v, " / ".join(vorher + w["auch_var"]), "ok"))      # jetzt
    for s in grunddaten["saetze"]:
        if "auch_var" in s:
            vorher = [s["answer"]] + list(s.get("auch") or [])
            for v in s["auch_var"]:
                faelle.append((v, " / ".join(vorher), "no"))
                faelle.append((v, " / ".join(vorher + s["auch_var"]), "ok"))
    # Nichts anderes wird richtig: andere Fälle des anderen Wortes, das andere Wort im Lückensatz
    for eingabe, wort in (("bocu", "flaša"), ("boce", "flaša"), ("susjeda", "komšija"), ("susjed", "komšije"),
                          ("Pijem kafa", "Pijem kahvu"), ("kafu", "jedna kahva")):
        w = next(x for x in _woerter(grunddaten) if x["bs"] == wort)
        faelle.append((eingabe, " / ".join([w["bs"]] + w.get("auch", []) + w["auch_var"]), "no"))
    for eingabe, text in (("boca", "Voda je u ___."), ("susjeda", "Moj ___ je dobar čovjek."),
                          ("kafa", "Pijem ___."), ("mama", "Volim svoju ___."), ("gorušica", "Kečap i ___, molim.")):
        s = next(x for x in grunddaten["saetze"] if x["text"] == text)
        faelle.append((eingabe, " / ".join([s["answer"]] + s.get("auch", []) + s["auch_var"]), "no"))
    ein = {"bloecke": bloecke, "faelle": [f[:2] for f in faelle], "zahlen": list(ZAHLEN)}
    aus = subprocess.run(["node", "-e", NODE], input=json.dumps(ein), capture_output=True, text=True,
                         encoding="utf-8", check=True, timeout=120)
    erg = json.loads(aus.stdout)
    return faelle, erg


def test_matches_vorher_falsch_jetzt_richtig(node_ergebnis):
    faelle, erg = node_ergebnis
    assert len(faelle) > 100
    falsch = [(f, r) for f, r in zip(faelle, erg["faelle"]) if f[2] != r]
    assert falsch == []


def test_zahlen_mit_und(node_ergebnis):
    """dvadeset jedan / dvadeset i jedan: bs-Web 156 / 193. In zahlWert(), damit
    es für jede Zahl gilt, beim Tippen wie beim Sprechen."""
    _, erg = node_ergebnis
    assert dict(zip(ZAHLEN, erg["zahlen"])) == ZAHLEN


def test_zahl_mit_und_in_matches(index_html):
    html = _html(index_html)
    assert "if(teile.length === 3 && teile[1] === 'i') teile.splice(1, 1);" in html
    assert re.search(r"const zg = zahlWert\(g\);", html)
