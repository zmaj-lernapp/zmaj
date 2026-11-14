# -*- coding: utf-8 -*-
"""Andere bosnische Wörter, die beim Tippen genauso gelten (varianten.py, 12.11.2026).

Bis dahin nahm „Voda je u ___.“ nur flaši - boci war falsch und kostete ein
Leben -, und „Pijem kahvu“ nahm nicht „Pijem kafu“, obwohl das Wort selbst
„kahva / kafa“ heißt. Ajdin: „die ganze app nochmal danach kontrollieren“.
Zuerst nur die eindeutigen Paare, seit dem 14.11.2026 auch die fraglichen aus
Tabelle 2c (Prüfbericht 1.4, F6): „nimm doch kroatische und die anderen rein
die sind nur nicht sichtbar“ - beim Tippen richtig, gezeigt nie.

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
    "braun:kafena": ["smeđa", "kahvena", "braon"],
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
    "decke (bettdecke):deka": ["pokrivač", "ćebe"],
    "waschbecken:lavabo": ["umivaonik"],
    "nachbarin:komšinica": ["susjeda"],
    "leiter:merdevine": ["ljestve", "skale"],
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
    # Tabelle 2c (Ajdin, 14.11.2026, F6). Die Nummer ist die Zeile der Tabelle.
    "brot:hljeb": ["kruh"],                                   # 1
    "ich esse brot:Jedem hljeb": ["Jedem kruh"],
    "es gibt kein brot:Nema hljeba": ["Nema kruha"],
    "suppe:supa": ["juha"],                                   # 2
    "gehalt:plata": ["plaća"],                                # 3
    "bruttogehalt:bruto plata": ["bruto plaća"],
    "nettogehalt:neto plata": ["neto plaća"],
    "langsam:polako": ["polahko"],                            # 4
    "minute:minuta": ["minut"],                               # 5
    "gestern:jučer": ["juče"],                                # 6
    "woche:sedmica": ["hefta"],                               # 7
    "letzte woche:prošle sedmice": ["prošle hefte"],
    "topf:lonac": ["šerpa"],                                  # 8, bosanski lonac nicht
    "pfanne:tava": ["tiganj"],                                # 9
    "spinat:špinat": ["spanać"],                              # 10
    "garten:bašta": ["bašča"],                                # 11
    "tochter:kćerka": ["kći", "kćer"],                        # 12
    "stunde / uhr:sat": ["sahat"],                            # 13
    "geschichte (fach):historija": ["povijest"],              # 14
    "besuch:posjeta": ["posjet"],                             # 15
    "miete:kirija": ["stanarina", "najamnina"],               # 16
    "kühlschrank:frižider": ["hladnjak"],                     # 17
    "backofen:rerna": ["pećnica"],
    "tüte / plastiktüte:kesa": ["vrećica"],
    "essig:sirće": ["ocat"],
    "zimmerdecke:plafon": ["strop"],
    "fabrik:fabrika": ["tvornica"],
    "aprikose:kajsija": ["marelica"],
    "lauch:praziluk": ["poriluk"],
    "handtuch:peškir": ["ručnik"],
    "laden:prodavnica": ["radnja"],                           # 18
    "geschäft:radnja": ["prodavnica"],
    "hof (am haus):dvorište": ["avlija"],                     # 19
    "hof / innenhof:avlija": ["dvorište"],
    "manchmal:ponekad": ["nekad", "nekada"],                  # 20, nekada seit der dritten Runde
    "kaffeetasse (traditionell):fildžan": ["findžan"],        # 22 (21 oben bei kafena)
    "auto:auto": ["kola"],                                    # 23
    "geld:novac": ["pare"],                                   # 24
    "handy:mobitel": ["mobilni"],                             # 25
    "markt:pijaca": ["pazar"],                                # 26
    "speisekarte:jelovnik": ["meni"],                         # 27
    "formular:obrazac": ["formular"],                         # 28
    "entschuldigung (du):Izvini": ["Oprosti"],                # 29
    "ob:da li": ["je li"],                                    # 31
    "vielen dank:Hvala puno": ["Puno hvala", "Hvala lijepa", "Hvala mnogo"],   # 32
    "auf wiedersehen:Doviđenja": ["Do viđenja"],              # 33
    "tschüss:Ćao": ["Do viđenja"],                            #    das Wort nimmt auch Doviđenja
    "guten abend:Dobro veče": ["Dobra večer"],                # 34
    "am abend:navečer": ["uveče"],                            # 35
    "am morgen:ujutro": ["ujutru"],
    "bei meinem freund:kod prijatelja": ["kod druga"],        # 36
    "anrede: freund!:prijatelju!": ["druže!"],
    "fenster:prozor": ["pendžer"],                            # 37 (deka und merdevine oben)
    "wand:zid": ["duvar"],
    "straße:ulica": ["sokak"],
    "schrank:ormar": ["dolap"],
    "gast:gost": ["musafir"],
    "gäste:gosti": ["musafiri"],
    "medikament:lijek": ["hap"],
    "erkältung:prehlada": ["nahlada"],
    "hefe:kvasac": ["germa"],
    "treppe:stepenice": ["basamaci"],
    "hund:pas": ["kuče"],
    "stück:komad": ["parče"],
    "metzgerei:mesnica": ["kasapnica"],
    "schulferien:raspust": ["ferije"],
    "haselnuss:lješnjak": ["lješnik"],
    "kürbis:bundeva": ["tikva"],                              # 39
    "granatapfel:nar": ["šipak"],
    "beißen:ugristi": ["ujesti"],
    "verkehr:saobraćaj": ["promet"],
    # Dritte Runde (Ajdin, 14.11.2026 abends, Offen-Liste 5a)
    "entschuldigung (sie):Izvinite": ["Oprostite"],
    "ich habe ein auto:Imam auto": ["Imam kola"],
    "im auto:u autu": ["u kolima"],
    "ich habe kein geld:Nemam novca": ["Nemam para"],
    "auf dem markt:na pijaci": ["na pazaru"],
    "auf der straße:na ulici": ["na sokaku"],
    "er hat einen hund:On ima psa": ["On ima kuče"],
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
    # Tabelle 2c. „Hvala ___!“ (Nr. 32) und „Pitam se ___ li dolazi.“ (Nr. 31)
    # haben ein "auch" am Lückensatz in vokabeln.py, kein Paar hier.
    "Djeca ne vole ___.": ["spanać"],                        # 10
    "Kolika je ___ mjesečno?": ["stanarina", "najamnina"],   # 16
    "Svi ___ su došli.": ["musafiri"],                       # 37
    "Idem u ___.": ["kasapnicu"],                            # 37
    # Dritte Runde (Ajdin, 14.11.2026 abends, Offen-Liste 5a)
    "___, molim Vas.": ["Oprostite"],
    "Supa je u ___.": ["šerpi"],
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
    # Tabelle 2c: gesperrt wird in beide Richtungen. Hier ist plaća das Verb
    # („zahlt“) und oprosti „verzeih“ - plata und izvini als falsche Kachel
    # wären harmlos, die Sperre kostet nur eine Auswahl. izvini liegt wegen
    # KACHEL_VERWECHSELBAR ohnehin nie als Kachel.
    "Svako plaća svoje": ["plata"],
    "Molim te, oprosti mi.": ["izvini"],
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
    ("veče", True, []),                                  # nur von a nach b (večer -> veče)
    ("Dobro veče", True, ["Dobra večer"]),               # Tabelle 2c Nr. 34, die ganze Wendung
    ("Pijem kafu", True, []),
    ("Pijem kahvu sada", True, ["Pijem kahvu sad", "Pijem kafu sada", "Pijem kafu sad"]),
    ("senf", True, []),                                  # Paar mit Kennungen: nur dort
    ("šifra", False, []),
    ("taksi", True, []),                                 # das Taxi, nicht taksa
    # Tabelle 2c (14.11.2026): mehrere Paare mit demselben a
    ("kafena", True, ["smeđa", "kahvena", "braon"]),
    ("kafena haljina", True, ["smeđa haljina", "kahvena haljina"]),      # braon nur allein
    ("kafena kesa", True, ["kafena vrećica", "smeđa kesa", "smeđa vrećica", "kahvena kesa", "kahvena vrećica"]),
    ("bosanski lonac", True, []),                        # šerpa nur beim Wort allein
    ("jelovnik", True, []),                              # meni nur bei „Speisekarte“
    ("meni", True, []),                                  # nur von a nach b: „mir“ nimmt nie jelovnik
    ("Nemam novca", True, []),                           # para nur an „Nemam novca“ (Kennung)
    ("u autu", True, []),                                # kolima nur an „u autu“ (Kennung)
    ("Imam auto", True, []),                             # kola nur an auto und „Imam auto“
    ("plati", True, []),                                 # das Verb, nicht plata
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


def test_kennungen_der_gefaehrlichen_paare():
    """meni, kola, pare, sahat, tikva, šipak, ujesti und promet heißen auch etwas
    anderes. Sie gelten nur am einen Wort der App, nie umgekehrt."""
    for a, b, kennung in (("jelovnik", "meni", "speisekarte:jelovnik"), ("auto", "kola", "auto:auto"),
                          ("novac", "pare", "geld:novac"), ("sat", "sahat", "stunde / uhr:sat"),
                          ("bundeva", "tikva", "kürbis:bundeva"), ("nar", "šipak", "granatapfel:nar"),
                          ("ugristi", "ujesti", "beißen:ugristi"), ("saobraćaj", "promet", "verkehr:saobraćaj")):
        assert _z([a], True, kennung=kennung) == ([b], []), a
        assert _z([a], True) == ([], []), a                 # an jedem anderen Wort nichts
        assert _z([b], True, kennung=kennung) == ([], []), b
        paare = [p for p in varianten.VARIANTEN if varianten.faelle(p["a"]).get("grund") == a]
        assert [p["gilt"] for p in paare] == [[kennung] + SAETZE_DRITTE_RUNDE.get(a, [])], a


# Dritte Runde (14.11.2026 abends): „Imam kola“ - das Paar auto / kola gilt auch dort.
SAETZE_DRITTE_RUNDE = {"auto": ["ich habe ein auto:Imam auto"]}


def test_dasselbe_paar_zweimal_ist_ein_befund(monkeypatch):
    """Dasselbe a darf mehrere b haben (kafena), aber nicht zweimal dasselbe b."""
    monkeypatch.setattr(varianten, "VARIANTEN", [
        {"a": "kafena", "b": "braon", "gilt": varianten.ALLEIN, "beleg": "x"},
        {"a": "kafena", "b": "kahvena", "gilt": varianten.ALLEIN, "beleg": "x"},
        {"a": "kafena", "b": "braon", "gilt": varianten.UEBERALL, "beleg": "x"}])
    probleme = varianten.pruefe_varianten({"kategorien": [], "saetze": []})
    assert probleme == ["Variante kafena / braon: 'kafena' -> 'braon' steht schon bei einem anderen Paar"]


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


# --- Tabelle 2c (Ajdin, 14.11.2026, Prüfbericht 1.4, F6) in matches() ---

# Je Zeile der Tabelle mindestens ein Beispiel: ("w", Kennung des Wortes) für die
# Schreibaufgabe, ("l", Text) für den Lückensatz, dazu die Eingabe. Bis dahin
# falsch ("no"), jetzt richtig ("ok"). Nr. 30 (Gdje) gehört zu F7, Nr. 38
# (tisuća) bleibt, wie es war.
TABELLE_2C = {
    1: [("w", "brot:hljeb", "kruh"), ("w", "es gibt kein brot:Nema hljeba", "Nema kruha")],
    2: [("w", "suppe:supa", "juha")],
    3: [("w", "gehalt:plata", "plaća"), ("w", "nettogehalt:neto plata", "neto plaća")],
    4: [("w", "langsam:polako", "polahko")],
    5: [("w", "minute:minuta", "minut")],
    6: [("w", "gestern:jučer", "juče")],
    7: [("w", "woche:sedmica", "hefta"), ("w", "letzte woche:prošle sedmice", "prošle hefte")],
    8: [("w", "topf:lonac", "šerpa")],
    9: [("w", "pfanne:tava", "tiganj")],
    10: [("w", "spinat:špinat", "spanać"), ("l", "Djeca ne vole ___.", "spanać")],
    11: [("w", "garten:bašta", "bašča")],
    12: [("w", "tochter:kćerka", "kći"), ("w", "tochter:kćerka", "kćer")],
    13: [("w", "stunde / uhr:sat", "sahat")],
    14: [("w", "geschichte (fach):historija", "povijest")],
    15: [("w", "besuch:posjeta", "posjet")],
    16: [("w", "miete:kirija", "stanarina"), ("l", "Kolika je ___ mjesečno?", "najamnina")],
    17: [("w", "kühlschrank:frižider", "hladnjak"), ("w", "backofen:rerna", "pećnica"),
         ("w", "tüte / plastiktüte:kesa", "vrećica"), ("w", "essig:sirće", "ocat"),
         ("w", "zimmerdecke:plafon", "strop"), ("w", "fabrik:fabrika", "tvornica"),
         ("w", "aprikose:kajsija", "marelica"), ("w", "lauch:praziluk", "poriluk"),
         ("w", "handtuch:peškir", "ručnik")],
    18: [("w", "laden:prodavnica", "radnja"), ("w", "geschäft:radnja", "prodavnica")],
    19: [("w", "hof (am haus):dvorište", "avlija"), ("w", "hof / innenhof:avlija", "dvorište")],
    20: [("w", "manchmal:ponekad", "nekad")],
    21: [("w", "braun:kafena", "braon"), ("w", "braun:kafena", "kahvena")],
    22: [("w", "kaffeetasse (traditionell):fildžan", "findžan")],
    23: [("w", "auto:auto", "kola")],
    24: [("w", "geld:novac", "pare")],
    25: [("w", "handy:mobitel", "mobilni")],
    26: [("w", "markt:pijaca", "pazar")],
    27: [("w", "speisekarte:jelovnik", "meni")],
    28: [("w", "formular:obrazac", "formular")],
    29: [("w", "entschuldigung (du):Izvini", "Oprosti")],
    31: [("w", "ob:da li", "je li"), ("l", "Pitam se ___ li dolazi.", "je")],
    32: [("w", "vielen dank:Hvala puno", "Puno hvala"), ("w", "vielen dank:Hvala puno", "Hvala lijepa"),
         ("w", "vielen dank:Hvala puno", "Hvala mnogo"), ("l", "Hvala ___!", "lijepa"), ("l", "Hvala ___!", "mnogo")],
    33: [("w", "auf wiedersehen:Doviđenja", "Do viđenja")],
    34: [("w", "guten abend:Dobro veče", "Dobra večer")],
    35: [("w", "am abend:navečer", "uveče"), ("w", "am morgen:ujutro", "ujutru")],
    36: [("w", "bei meinem freund:kod prijatelja", "kod druga"), ("w", "anrede: freund!:prijatelju!", "druže!")],
    37: [("w", "fenster:prozor", "pendžer"), ("w", "wand:zid", "duvar"), ("w", "straße:ulica", "sokak"),
         ("w", "schrank:ormar", "dolap"), ("w", "gast:gost", "musafir"), ("l", "Svi ___ su došli.", "musafiri"),
         ("w", "medikament:lijek", "hap"), ("w", "erkältung:prehlada", "nahlada"), ("w", "hefe:kvasac", "germa"),
         ("w", "treppe:stepenice", "basamaci"), ("w", "hund:pas", "kuče"), ("w", "stück:komad", "parče"),
         ("w", "metzgerei:mesnica", "kasapnica"), ("l", "Idem u ___.", "kasapnicu"),
         ("w", "schulferien:raspust", "ferije"), ("w", "decke (bettdecke):deka", "ćebe"),
         ("w", "leiter:merdevine", "skale"), ("w", "haselnuss:lješnjak", "lješnik")],
    39: [("w", "kürbis:bundeva", "tikva"), ("w", "granatapfel:nar", "šipak"), ("w", "beißen:ugristi", "ujesti"),
         ("w", "verkehr:saobraćaj", "promet")],
}

# Bleibt falsch: die andere Richtung, Wörter mit derselben Form und anderer
# Bedeutung, und wo das Wort nicht allein steht, obwohl Geschlecht oder Zahl
# anders sind (Ajdin: „nur wo das Wort allein steht“). Die sechs Sätze, die Ajdin
# in der dritten Runde freigegeben hat („Nemam para“, „u kolima“ …), stehen unten
# bei DRITTE_RUNDE.
GEGEN_2C = [
    ("w", "mir:meni / mi", "jelovnik"),                               # meni heißt auch „mir“
    ("w", "mir ist es egal:Svejedno mi je", "Svejedno jelovnik je"),
    ("w", "mir ist es egal:Svejedno mi je", "Jelovnik je svejedno"),
    ("w", "geld:novac", "para"),                                      # pare nur so, wie es allein steht
    ("w", "geld einzahlen:uplatiti novac", "uplatiti pare"),
    ("w", "das auto des vaters:auto oca", "kola oca"),                # kola nur an auto und „Imam auto“
    ("w", "das auto des vaters:auto oca", "očev kola"),
    ("l", "Putujemo ___.", "kolima"),
    ("w", "krankenwagen / rettung:hitna", "auto hitne pomoći"),       # nie von kola nach auto
    ("l", "Koliko je ___?", "sahata"),                                # sahat nur beim Wort sat
    ("l", "Koliko je ___?", "sahati"),
    ("w", "bosnischer schmortopf:bosanski lonac", "bosanska šerpa"),  # šerpa nur am Wort lonac, šerpi in „Supa je u ___.“
    ("w", "der hund hat mich gebissen:Pas me je ujeo", "Pas me je ugrizao"),   # nie von ujesti nach ugristi
    ("w", "verkehrs-:saobraćajni", "prometni"),                       # promet nur beim Wort saobraćaj
    ("w", "verzeih mir:Oprosti mi", "Izvini mi"),                     # nie von oprosti nach izvini
    ("w", "manchmal / früher:nekad", "ponekad"),                      # nie von nekad nach ponekad
    ("w", "handel:trgovina", "prodavnica"),                           # trgovina gehört nicht dazu
    ("w", "voll:pun", "mnogo"),                                       # puno → mnogo nur in „Hvala ___!“
    ("w", "dass:da", "je"),                                           # da → je nur in „Pitam se ___ li dolazi.“
    ("l", "Mislim ___ je dobro.", "je"),
    ("w", "nie:nikad", "nekad"),
]


def _antworten_von(daten, art, wer, ohne_neu=False):
    """Alle Antworten, wie die App sie prüft. ohne_neu: so, wie es vor dem
    14.11.2026 war - ohne auch_var und ohne das "auch" der beiden Lückensätze."""
    if art == "w":
        w = next(x for x in _woerter(daten) if x["id"] == wer)
        mehr = [] if ohne_neu else w.get("auch_var", [])
        return " / ".join([w["bs"]] + list(w.get("auch") or []) + mehr)
    s = next(x for x in daten["saetze"] if x["text"] == wer)
    if ohne_neu:
        return s["answer"]
    return " / ".join([s["answer"]] + list(s.get("auch") or []) + list(s.get("auch_var") or []))


@pytest.fixture(scope="module")
def node_2c(index_html, grunddaten):
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
    for nr, beispiele in TABELLE_2C.items():
        for art, wer, eingabe in beispiele:
            faelle.append(((nr, art, wer, eingabe, "vorher"), eingabe, _antworten_von(grunddaten, art, wer, True)))
            faelle.append(((nr, art, wer, eingabe, "jetzt"), eingabe, _antworten_von(grunddaten, art, wer)))
    for art, wer, eingabe in GEGEN_2C:
        faelle.append((("gegen", art, wer, eingabe), eingabe, _antworten_von(grunddaten, art, wer)))
    ein = {"bloecke": bloecke, "faelle": [f[1:] for f in faelle], "zahlen": []}
    aus = subprocess.run(["node", "-e", NODE], input=json.dumps(ein), capture_output=True, text=True,
                         encoding="utf-8", check=True, timeout=120)
    return dict(zip([f[0] for f in faelle], json.loads(aus.stdout)["faelle"]))


def test_tabelle_2c_jede_zeile_hat_ein_beispiel():
    assert set(TABELLE_2C) == set(range(1, 40)) - {30, 38}


def test_tabelle_2c_vorher_falsch_jetzt_richtig(node_2c):
    falsch = {k: v for k, v in node_2c.items() if k[0] != "gegen" and v != ("no" if k[-1] == "vorher" else "ok")}
    assert falsch == {}


def test_tabelle_2c_nichts_anderes_wird_richtig(node_2c):
    falsch = {k: v for k, v in node_2c.items() if k[0] == "gegen" and v != "no"}
    assert falsch == {}
    assert len([k for k in node_2c if k[0] == "gegen"]) == len(GEGEN_2C)


def test_tisuca_bleibt_tausend(index_html):
    """Tabelle 2c Nr. 38: tisuća gilt weiter als 1000 (Ajdin, 14.11.2026)."""
    assert "const ZAHL_SONDER = {jedna:1, jedno:1, dvije:2, dvoje:2, tisuca:1000};" in _html(index_html)


# --- Dritte Runde (Ajdin, 14.11.2026 abends, Offen-Liste 5a) in matches() ---
# Je „Ja“ in Release\Pruefbericht_1.4.md, „Dritte Runde“: bis dahin falsch, jetzt richtig.
DRITTE_RUNDE = [
    ("w", "entschuldigung (sie):Izvinite", "Oprostite"),               # Oprostite neben Izvinite
    ("l", "___, molim Vas.", "Oprostite"),
    ("w", "manchmal:ponekad", "nekada"),                              # nekada bei ponekad
    # Zweite Form auch in ganzen Sätzen, genau diese sieben Stellen
    ("w", "ich habe ein auto:Imam auto", "Imam kola"),
    ("w", "im auto:u autu", "u kolima"),
    ("w", "ich habe kein geld:Nemam novca", "Nemam para"),
    ("w", "auf dem markt:na pijaci", "na pazaru"),
    ("w", "auf der straße:na ulici", "na sokaku"),
    ("l", "Supa je u ___.", "šerpi"),
    ("w", "er hat einen hund:On ima psa", "On ima kuče"),
]
# Bleibt falsch: die du-Form war nicht gefragt, und nie von oprosti nach izvini.
GEGEN_DRITTE_RUNDE = [
    ("w", "entschuldigung (du):Izvini", "Oprostite"),
    ("w", "entschuldigung (sie):Izvinite", "Oprosti"),
    ("w", "verzeih mir:Oprosti mi", "Oprostite mi"),
    ("l", "Molim te, ___ mi.", "oprostite"),
    ("l", "Molim te, ___ mi.", "izvini"),
    ("w", "manchmal:ponekad", "nikada"),                              # nikada heißt „nie“
    ("w", "nie:nikad", "nekada"),
    ("w", "manchmal / früher:nekad", "ponekad"),                      # nie von nekad nach ponekad
    # Keine weiteren gebeugten Formen: nur die sieben Stellen, nur die genannte Form
    ("w", "ich habe ein auto:Imam auto", "Imam kolima"),
    ("w", "im auto:u autu", "u kola"),
    ("w", "er hat einen hund:On ima psa", "On ima kučeta"),
    ("w", "auf der straße:na ulici", "na sokak"),
    ("w", "auf dem markt:na pijaci", "na pazar"),
    ("w", "mit dem auto:autom", "kolima"),
    ("l", "Putujemo ___.", "kolima"),
    ("w", "geld einzahlen:uplatiti novac", "uplatiti para"),
    ("w", "geld abheben:podići novac", "podići pare"),
    ("w", "wir suchen die straße:Tražimo ulicu", "Tražimo sokak"),
    ("w", "ich habe angst vor hunden:Bojim se pasa", "Bojim se kučeta"),
    ("w", "vorsicht vor dem hund!:Čuvaj se psa!", "Čuvaj se kučeta!"),
    ("w", "der hund hat mich gebissen:Pas me je ujeo", "Kuče me je ujelo"),
    ("l", "Na pijaci ima mnogo ___.", "pazaru"),
    ("l", "Koliko je ___?", "sahat"),                                 # „Koliko je sahat?“: Ajdin „Ne“
]


@pytest.fixture(scope="module")
def node_dritte(index_html, grunddaten):
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
    for art, wer, eingabe in DRITTE_RUNDE:
        faelle.append(((art, wer, eingabe, "vorher"), eingabe, _antworten_von(grunddaten, art, wer, True)))
        faelle.append(((art, wer, eingabe, "jetzt"), eingabe, _antworten_von(grunddaten, art, wer)))
    for art, wer, eingabe in GEGEN_DRITTE_RUNDE:
        faelle.append((("gegen", art, wer, eingabe), eingabe, _antworten_von(grunddaten, art, wer)))
    ein = {"bloecke": bloecke, "faelle": [f[1:] for f in faelle], "zahlen": []}
    aus = subprocess.run(["node", "-e", NODE], input=json.dumps(ein), capture_output=True, text=True,
                         encoding="utf-8", check=True, timeout=120)
    return dict(zip([f[0] for f in faelle], json.loads(aus.stdout)["faelle"]))


def test_dritte_runde_vorher_falsch_jetzt_richtig(node_dritte):
    falsch = {k: v for k, v in node_dritte.items() if k[0] != "gegen" and v != ("no" if k[-1] == "vorher" else "ok")}
    assert falsch == {}
    assert len([k for k in node_dritte if k[0] != "gegen"]) == 2 * len(DRITTE_RUNDE)


def test_dritte_runde_nichts_anderes_wird_richtig(node_dritte):
    falsch = {k: v for k, v in node_dritte.items() if k[0] == "gegen" and v != "no"}
    assert falsch == {}
    assert len([k for k in node_dritte if k[0] == "gegen"]) == len(GEGEN_DRITTE_RUNDE)


def test_dritte_runde_nein_bleibt_nein(grunddaten):
    """Ajdin „Ne“: „Koliko je sahat?“ (oben in GEGEN_DRITTE_RUNDE) und „Moja je ovo
    kolegica.“ als andere Wortstellung beim Satzbau."""
    s = [x for x in grunddaten["satzbau"] if x["bs"] == "Ovo je moja kolegica."]
    assert len(s) == 1 and not s[0].get("auch"), s
    luecke = [x for x in grunddaten["saetze"] if x["text"] == "Koliko je ___?"]
    assert len(luecke) == 1 and not luecke[0].get("auch") and not luecke[0].get("auch_var"), luecke
