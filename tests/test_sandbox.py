# -*- coding: utf-8 -*-
"""Sandbox der Test-App: dort ist alles offen, sonst nirgends.

Ajdin am 08.11.2026: "nein bei der test app lass sie offen das ist wie eine
sandbox app", und "ja" zu einem festen Schalter "alles offen". Erkannt wird
die Test-App an der App-ID, die Android ueber App.getInfo() meldet
(de.smartdragon.zmaj.test, nur der debug-Bau der Huelle), UND an
APP_VERSION mit "-test" (app_bauen.version_einsetzen, nie bei --aab). Hier:
die Erkennung selbst in node, dass nur die Sperren daran haengen und nichts
in den Lernstand geschrieben wird. Das Verhalten im Browser pruefen
tests_e2e/test_sandbox.py."""
import io
import json
import os
import re
import shutil
import subprocess

import pytest

TEST_ID = "de.smartdragon.zmaj.test"
ECHTE_ID = "de.smartdragon.zmaj"


def _html(index_html):
    return index_html.replace("\r\n", "\n")


def _block(index_html):
    """Der Teil von SANDBOX_APP_ID bis vor allesOffen - genau die Erkennung."""
    html = _html(index_html)
    anfang = html.index("const SANDBOX_APP_ID = ")
    ende = html.index("\nconst allesOffen = ", anfang)
    return html[anfang:ende]


def _rumpf(html, kopf):
    return html.split(kopf)[1].split("\n};\n")[0]


# ---------------------------------------------------------------- Erkennung

# Jeder Fall: wie window.Capacitor aussieht, welche APP_VERSION im Paket
# steht, und ob die Sandbox an sein darf.
FAELLE = [
    ("browser_ohne_capacitor", {"capacitor": False}, "1.4", False),
    ("browser_mit_test_version", {"capacitor": False}, "1.4-test", False),
    ("capacitor_ohne_app", {"ohne_app": True}, "1.4-test", False),
    ("echte_app_store_bau", {"id": ECHTE_ID}, "1.4", False),
    ("echte_app_mit_test_version", {"id": ECHTE_ID}, "1.4-test", False),
    ("test_app", {"id": TEST_ID}, "1.4-test", True),
    ("test_app_store_version", {"id": TEST_ID}, "1.4", False),
    ("test_app_version_mittendrin", {"id": TEST_ID}, "1.4-test-x", False),
    ("nicht_nativ", {"id": TEST_ID, "nativ": False}, "1.4-test", False),
    ("nativ_fehlt", {"id": TEST_ID, "nativ": None}, "1.4-test", False),
    ("andere_test_app", {"id": "de.smartdragon.andere.test"}, "1.4-test", False),
    ("id_mit_anhang", {"id": TEST_ID + "2"}, "1.4-test", False),
    ("id_mit_vorsatz", {"id": "x." + TEST_ID}, "1.4-test", False),
    ("id_fehlt", {"id": None}, "1.4-test", False),
    ("info_null", {"info_null": True}, "1.4-test", False),
    ("get_info_wirft", {"wirft": True}, "1.4-test", False),
    ("get_info_antwortet_nie", {"haengt": True}, "1.4-test", False),
]

NODE = r"""
const [block, faelle] = [process.argv[1], JSON.parse(process.argv[2])];
const bau = new Function('window', 'APP_VERSION',
  block + '\nreturn {sandboxPruefen, sandboxErkannt, an: () => SANDBOX};');
function fenster(f, gefragt){
  if(f.capacitor === false) return {};
  const App = {
    getInfo(){
      gefragt.n++;
      if(f.wirft) return Promise.reject(new Error('kaputt'));
      if(f.haengt) return new Promise(() => {});
      if(f.info_null) return Promise.resolve(null);
      return Promise.resolve({name: 'Zmaj Test', id: f.id === null ? undefined : f.id,
                              build: '116', version: '1.4-test'});
    }
  };
  const C = {Plugins: f.ohne_app ? {} : {App}};
  if(f.nativ !== null) C.isNativePlatform = () => f.nativ !== false;
  return {Capacitor: C};
}
(async () => {
  const aus = {};
  for(const [name, f, version] of faelle){
    const gefragt = {n: 0};
    const m = bau(fenster(f, gefragt), version);
    const ergebnis = await m.sandboxPruefen();
    aus[name] = {ergebnis, an: m.an(), gefragt: gefragt.n};
  }
  // Ein zweiter Aufruf faengt wieder bei "aus" an.
  const g = {n: 0};
  const m = bau(fenster({id: TEST_ID}, g), '1.4-test');
  await m.sandboxPruefen();
  const vorher = m.an();
  aus.zweiter_aufruf = {vorher, nachher: await m.sandboxPruefen()};
  console.log(JSON.stringify(aus));
})().catch(e => { console.error(e); process.exit(1); });
""".replace("TEST_ID", json.dumps(TEST_ID))


@pytest.fixture(scope="module")
def node_ergebnis(index_html):
    if not shutil.which("node"):
        pytest.skip("node fehlt")
    # Die Zeitgrenze kurz, sonst wartet der Fall "antwortet nie" zwei Sekunden.
    block = _block(index_html)
    assert block.count("const SANDBOX_WARTEN = 2000;") == 1
    block = block.replace("const SANDBOX_WARTEN = 2000;", "const SANDBOX_WARTEN = 30;")
    aus = subprocess.run(["node", "-e", NODE, block, json.dumps(FAELLE)],
                         capture_output=True, text=True, encoding="utf-8", check=True, timeout=60)
    return json.loads(aus.stdout)


@pytest.mark.parametrize("name, fenster, version, soll", FAELLE, ids=[f[0] for f in FAELLE])
def test_sandbox_nur_in_der_test_app(node_ergebnis, name, fenster, version, soll):
    e = node_ergebnis[name]
    assert e["ergebnis"] is soll and e["an"] is soll, e


def test_store_bau_fragt_gar_nicht_erst(node_ergebnis):
    """Ohne "-test" in APP_VERSION faellt die Antwort, bevor Android
    gefragt wird."""
    assert node_ergebnis["test_app_store_version"]["gefragt"] == 0
    assert node_ergebnis["echte_app_store_bau"]["gefragt"] == 0
    assert node_ergebnis["test_app"]["gefragt"] == 1


def test_zweiter_aufruf_faengt_bei_aus_an(node_ergebnis):
    assert node_ergebnis["zweiter_aufruf"] == {"vorher": True, "nachher": True}


def test_app_id_wie_in_der_huelle(index_html):
    """SANDBOX_APP_ID ist genau die App-ID des debug-Baus: applicationId
    plus applicationIdSuffix aus app/build.gradle der Huelle."""
    assert "const SANDBOX_APP_ID = '%s';" % TEST_ID in index_html
    import huelle
    gradle = os.path.join(huelle.ordner(), "android", "app", "build.gradle")
    if not os.path.isfile(gradle):
        pytest.skip("Android-Huelle fehlt")
    with io.open(gradle, encoding="utf-8") as f:
        text = f.read()
    assert re.findall(r'\bapplicationId\s+"([^"]+)"', text) == [ECHTE_ID]
    debug = re.search(r"\bdebug\s*\{(.*?)\}", text, re.S).group(1)
    assert re.findall(r'applicationIdSuffix\s+"([^"]+)"', debug) == [".test"]
    assert ECHTE_ID + ".test" == TEST_ID
    release = re.search(r"\brelease\s*\{(.*?)\n        \}", text, re.S).group(1)
    assert "applicationIdSuffix" not in release


def test_version_endung_wie_app_bauen(tmp_path, index_html):
    """"-test" setzt app_bauen.py nur fuer das Debug-Paket und
    --nur-abgleich, nie fuer --aab - und die App prueft genau diese Endung."""
    import app_bauen
    assert app_bauen.TEST_ENDUNG == "-test"
    assert "/-test$/.test(version)" in _block(index_html)
    with io.open(os.path.join(os.path.dirname(app_bauen.__file__), "app_bauen.py"),
                 encoding="utf-8") as f:
        quelle = f.read()
    assert "    version_einsetzen(version, test=not aab)\n" in quelle.replace("\r\n", "\n")
    kopie = tmp_path / "index.html"
    for test, soll in ((True, "1.4-test"), (False, "1.4")):
        kopie.write_text("x\nconst APP_VERSION = '1.1';\ny\n", encoding="utf-8")
        assert app_bauen.version_einsetzen("1.4", test=test, pfad=str(kopie)) == soll


# ---------------------------------------------------------------- Folgen

def test_sperren_fragen_alles_offen(index_html):
    html = _html(index_html)
    assert "const allesOffen = () => ALLE_FREI || SANDBOX;" in html
    unlocked = _rumpf(html, "const isUnlocked = i => {\n")
    # Seit den Stufen-Reitern (13.11.2026) steht die Kette des Lernpfads in
    # inDerKette(), das zweite allesOffen() also dort
    assert unlocked.count("return allesOffen() || ") == 1
    assert "return inDerKette(i) || levelAngefangen(i);" in unlocked
    assert "const inDerKette = i => allesOffen() || " in html
    assert "ALLE_FREI" not in unlocked
    assert "const testAllowed = c => allesOffen() || passed.has(c.id) ||" in html
    assert "const storyUnlocked = i => allesOffen() || i===0 || read.has(STORIES[i-1].id);" in html


def test_sonst_bleibt_alles_wie_in_der_echten_app(index_html):
    """Leben, Werbung, Einstufung und Bewertung kennen die Sandbox nicht:
    in der Test-App soll sich bis auf die Sperren alles wie im Store
    verhalten."""
    html = _html(index_html)
    assert "const unlimited = () => premium || ALLE_FREI || geschenkLaeuft();" in html
    assert "return !einstufung && !ALLE_FREI && CATEGORIES.length > 0" in html
    assert "if(ALLE_FREI || bewertung.nein || bewertung.bewertet) return false;" in html
    # SANDBOX und allesOffen() nur in der Erkennung, den drei Sperren und
    # der Versionszeile
    ohne_kommentare = re.sub(r"/\*.*?\*/", "", html, flags=re.S)
    block = re.sub(r"/\*.*?\*/", "", _block(index_html), flags=re.S)
    assert len(re.findall(r"\bSANDBOX\b", block)) == 5
    assert len(re.findall(r"\bSANDBOX\b", ohne_kommentare)) == 5 + 2   # + allesOffen, versionText
    assert ohne_kommentare.count("allesOffen()") == 4


def test_erkennung_schreibt_nichts(index_html):
    """Freigeschaltet wird nur im Kopf der App: kein passed, kein known,
    kein Speichern, kein localStorage."""
    block = _block(index_html)
    for wort in ("passed", "known", "read.", "saveProgress", "localStorage", "zmaj_stand",
                 "cloud", "fetch("):
        assert wort not in block, wort
    # SANDBOX wird nur hier gesetzt: einmal angelegt, zweimal aus, einmal das Ergebnis
    html = _html(index_html)
    zuweisungen = re.findall(r"\bSANDBOX\s*=(?!=)", html)
    assert len(zuweisungen) == 4 and len(re.findall(r"\bSANDBOX\s*=(?!=)", block)) == 4


def test_gefragt_wird_vor_dem_ersten_zeichnen(index_html):
    html = _html(index_html)
    rumpf = html.split("async function starten(){\n")[1].split("\n}\n")[0]
    assert rumpf.index("await sandboxPruefen();") < rumpf.index("await ladeDaten();")
    assert rumpf.index("await sandboxPruefen();") < rumpf.index("await nachAnmeldung(")
    # Nur dort gefragt: Definition und dieser eine Aufruf
    assert html.count("sandboxPruefen()") == 2
