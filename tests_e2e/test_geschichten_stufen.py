# -*- coding: utf-8 -*-
"""Die Geschichten in Stufen-Reitern (17.11.2026, Offen-Liste 7).

Ajdin: "lass sie auch in 1.4 rein machen das da steht amtssprache lass raus es soll
einfach von kinderleicht zu schwerer sein usw also nur A1, A2 usw". Oben im Reiter
Geschichten stehen dieselben Stufen-Reiter wie im Lernpfad, darunter nur die
Geschichten der gewaehlten Stufe, von leicht nach schwer, gezaehlt je Reiter. Eine
Stufe ohne Geschichten (B2, C1) steht als "bald" da wie C1 im Lernpfad.

Frei bleibt, was vorher frei war: storyUnlocked() kennt die Folge bis zum 17.11.2026
(GESCH_ALTE_FOLGE). Geprueft mit jedem Lernstand, den die alte Kette zuliess.
Ohne Browser: tests/test_geschichten_stufen.py.
"""
import re

import pytest
from conftest import Seite

ALTE_FOLGE = [
    "mira", "kuca1", "porodica", "pijaca", "dan", "grad", "jucer", "put", "pismo", "opcina",
    "kuca", "intervju", "b1_ljeto", "b1_dijaspora", "b1_vrijeme", "b1_voz", "b1_rafting",
    "b1_jahorina", "b1_pita", "b1_struja", "b1_svadba", "b1_posao", "b1_stan", "b1_doktor",
    "b1_selidba", "b1_telefon", "b1_rodjendan", "b1_utakmica", "b1_zanat", "b1_kahva",
    "b1_mejl", "b1_zmaj",
]
A1 = ["mira", "porodica", "kuca1", "pijaca", "dan"]
A2 = ["opcina", "jucer", "grad", "kuca", "put", "pismo"]
B1 = ["b1_vrijeme", "b1_voz", "b1_stan", "b1_ljeto", "b1_svadba", "b1_rafting", "b1_rodjendan",
      "b1_doktor", "b1_posao", "b1_jahorina", "b1_utakmica", "b1_struja", "b1_zmaj", "b1_pita",
      "b1_kahva", "b1_dijaspora", "b1_telefon", "b1_selidba", "b1_zanat", "b1_mejl", "intervju"]

LEISTE = """() => [...document.querySelectorAll('#geschReiter button')].map(b => ({
  st: b.dataset.stufe, art: b.className, an: b.getAttribute('aria-selected') === 'true',
  text: b.querySelector('.sz').textContent.trim(), rolle: b.getAttribute('role')}))"""

LAGE = """() => ({oben: document.getElementById('geschReiter').getBoundingClientRect().top,
  an: (document.querySelector('#geschReiter button[aria-selected="true"]') || {}).dataset.stufe})"""

LISTE = """() => ({
  sichtbar: getComputedStyle(document.getElementById('storyList')).display !== 'none',
  knoten: [...document.querySelectorAll('#storyList .node')].map(n => ({
    titel: n.querySelector('.titel').textContent, kreis: n.querySelector('.circle').textContent,
    klasse: n.className, zustand: n.querySelector('.state').textContent})),
  karte: document.getElementById('geschKarte').hidden ? '' : document.getElementById('geschKarte').innerText.trim()})"""


def _geschichten(seite):
    seite.js("() => { homeMode = 'stories'; showHome(); }")


def test_reihenfolge_und_stufen_in_der_app(seite, heute_stand):
    seite.starten(stand=heute_stand())
    r = seite.js("() => STORIES.map(s => [s.id, s.stufe])")
    assert r == [[i, "A1"] for i in A1] + [[i, "A2"] for i in A2] + [[i, "B1"] for i in B1]
    assert seite.fehler == []


def test_reiter_wie_im_lernpfad(seite, heute_stand):
    """Fuenf Reiter A1 bis C1 mit denselben Klassen wie im Lernpfad: A1 offen und
    gewaehlt, A2 und B1 zu (Schloss), B2 und C1 bald. Darunter nur die fuenf von A1,
    gezaehlt von 1."""
    seite.starten(stand=heute_stand())
    _geschichten(seite)
    leiste = seite.js(LEISTE)
    assert [(x["st"], x["art"], x["an"], x["rolle"]) for x in leiste] == [
        ("A1", "offen", True, "tab"), ("A2", "zu", False, "tab"), ("B1", "zu", False, "tab"),
        ("B2", "bald", False, "tab"), ("C1", "bald", False, "tab")]
    assert leiste[0]["text"] == "0/5"
    assert seite.js("() => document.getElementById('geschReiter').getAttribute('aria-label')") == "Stufen"
    li = seite.js(LISTE)
    assert li["sichtbar"] and li["karte"] == ""
    assert [k["titel"] for k in li["knoten"]] == ["Mira i Rex", "Moja porodica", "Naša kuća", "Na pijaci", "Moj dan"]
    assert li["knoten"][0]["kreis"] == "1" and "current" in li["knoten"][0]["klasse"]
    assert all("locked" in k["klasse"] for k in li["knoten"][1:])
    # dieselbe Optik: die Leiste der Geschichten traegt dieselbe Klasse wie die im Lernpfad
    assert seite.js("() => document.getElementById('geschReiter').className") == "reiterleiste"
    assert seite.fehler == []


def test_reiter_wechseln_zu_und_bald(seite, heute_stand):
    seite.starten(stand=heute_stand())
    _geschichten(seite)
    seite.page.click("#geschReiter button[data-stufe='A2']")
    li = seite.js(LISTE)
    assert [k["titel"] for k in li["knoten"]] == ["Na općini", "Jučer", "U gradu", "Kupujemo kuću",
                                                   "Put u Bosnu", "Pismo nani"]
    assert all("locked" in k["klasse"] for k in li["knoten"])
    assert "A2 ist noch zu" in li["karte"] and "Schließ erst A1 ab." in li["karte"], li["karte"]
    an = [x["st"] for x in seite.js(LEISTE) if x["an"]]
    assert an == ["A2"]
    # Gesperrt: die erste sagt, welche Stufe vorher dran ist, die zweite welche Geschichte
    seite.page.locator("#storyList .node").nth(0).click()
    seite.page.locator("#storyList .node").nth(1).click()
    z = seite.js("() => [...document.querySelectorAll('#storyList .node .state')].slice(0, 2).map(x => x.textContent)")
    assert z == ["Zuerst A1 abschließen", "Zuerst Geschichte 1 lesen"], z
    assert seite.js("() => sichtbar('storyView')") is False
    # B2 hat noch keine Geschichten: nur die Karte "kommt bald", keine Liste
    seite.page.click("#geschReiter button[data-stufe='B2']")
    li = seite.js(LISTE)
    assert li["sichtbar"] is False and li["knoten"] == [] and li["karte"] == "B2 kommt bald", li
    seite.page.click("#geschReiter button[data-stufe='A1']")
    assert len(seite.js(LISTE)["knoten"]) == 5
    assert seite.fehler == []


@pytest.mark.parametrize("breite,hoehe", [(360, 740), (412, 915)], ids=["360", "412"])
def test_leiste_bleibt_stehen(browser, basis, heute_stand, breite, hoehe):
    """Wie im Lernpfad (Ajdin 14.11.2026, tests_e2e/test_reiter.py): ein Tipp auf einen
    Reiter wechselt nur, was darunter steht. Die Leiste bleibt, wo sie war (hoechstens
    2 px) - oben, in der Mitte oder unten im Bild, in den langen Reiter B1, den kurzen
    A1 und in B2, das nur "kommt bald" zeigt. Getippt wird echt, mit der Maus."""
    ctx = browser.new_context(viewport={"width": breite, "height": hoehe}, locale="de-DE",
                              service_workers="block", reduced_motion="reduce")
    try:
        seite = Seite(ctx.new_page(), basis)
        seite.starten(stand=heute_stand(gelesen=A1 + A2))
        seite.js("() => { const v = document.getElementById('vorspann'); if(v) v.click(); }")
        seite.page.wait_for_function("() => !document.getElementById('vorspann')", timeout=15000)
        _geschichten(seite)
        assert [x["st"] for x in seite.js(LEISTE) if x["an"]] == ["B1"]
        lage = seite.js("""() => { const r = document.getElementById('geschReiter').getBoundingClientRect();
          return {oben: r.top + scrollY, hoch: r.height}; }""")
        gesprungen = []
        for ziel in (4, hoehe // 2, hoehe - lage["hoch"] - 4):
            for st in ["A1", "B2", "B1", "A2", "C1", "B1"]:
                seite.js("(y) => window.scrollTo({top: y, behavior: 'instant'})", max(0, lage["oben"] - ziel))
                vorher = seite.js(LAGE)
                seite.page.click("#geschReiter button[data-stufe='%s']" % st)
                nachher = seite.js(LAGE)
                assert nachher["an"] == st, (ziel, st, nachher)
                if abs(nachher["oben"] - vorher["oben"]) > 2:
                    gesprungen.append((ziel, vorher["an"], st, round(vorher["oben"]), round(nachher["oben"])))
        assert gesprungen == [], gesprungen
        # Die Startseite neu: oben, ohne leeren Bildschirm unter B2
        seite.page.click("#geschReiter button[data-stufe='B2']")
        seite.js("() => showHome()")
        assert seite.js("() => [scrollY, document.getElementById('storiesHome').style.minHeight]") == [0, ""]
        assert seite.js("() => document.documentElement.scrollWidth") <= breite
        assert seite.fehler == []
    finally:
        ctx.close()


@pytest.mark.parametrize("gelesen,stufe,dran", [
    ([], "A1", "mira"),
    (A1[:2], "A1", "kuca1"),
    (A1, "A2", "opcina"),
    (A1 + A2, "B1", "b1_vrijeme"),
    (A1 + A2 + B1[:20], "B1", "intervju"),
])
def test_geoeffnet_wird_der_reiter_der_naechsten(seite, heute_stand, gelesen, stufe, dran):
    seite.starten(stand=heute_stand(gelesen=gelesen))
    _geschichten(seite)
    assert [x["st"] for x in seite.js(LEISTE) if x["an"]] == [stufe]
    li = seite.js(LISTE)
    jetzt = [k["titel"] for k in li["knoten"] if "current" in k["klasse"]]
    assert jetzt == [seite.js("(id) => STORIES.find(s => s.id === id).titel", dran)]
    # Weitermachen oben fuehrt in dieselbe
    knopf = seite.js("() => document.getElementById('weiterKnopf').textContent")
    assert knopf.endswith(jetzt[0]), knopf
    assert seite.fehler == []


def test_alle_gelesen_fertig(seite, heute_stand):
    seite.starten(stand=heute_stand(gelesen=ALTE_FOLGE))
    _geschichten(seite)
    leiste = seite.js(LEISTE)
    assert [(x["st"], x["art"]) for x in leiste] == [("A1", "fertig"), ("A2", "fertig"), ("B1", "fertig"),
                                                    ("B2", "bald"), ("C1", "bald")]
    assert [x["st"] for x in leiste if x["an"]] == ["B1"]
    assert seite.fehler == []


def test_gewaehlter_reiter_bleibt_nach_einer_geschichte(seite, heute_stand):
    seite.starten(stand=heute_stand(gelesen=A1 + A2))
    _geschichten(seite)
    seite.page.click("#geschReiter button[data-stufe='A1']")
    seite.page.locator("#storyList .node").nth(2).click()
    assert seite.js("() => STORIES[rIdx].id") == "kuca1"
    seite.js("() => { stilleBitte(); backTarget(); }")
    assert [x["st"] for x in seite.js(LEISTE) if x["an"]] == ["A1"]
    assert seite.fehler == []


# ---------------------------------------------------------------------------
# Freischalten: nichts geht zu, was vorher frei war
# ---------------------------------------------------------------------------
PRUEFEN = r"""(alteFolge) => {
  const aus = [];
  const faelle = [];
  // Jeder Stand, den die alte Kette zuliess: die ersten k gelesen
  for(let k = 0; k <= alteFolge.length; k++) faelle.push(alteFolge.slice(0, k));
  // Dazu Staende, wie sie Cloud und Sicherung zusammenmischen koennten
  faelle.push(['mira', 'kuca1', 'b1_ljeto']);
  faelle.push(['intervju']);
  faelle.push(alteFolge.filter((x, i) => i % 3 === 0));
  for(const ids of faelle){
    read.clear(); ids.forEach(id => read.add(id));
    const altFrei = new Set(alteFolge.filter((id, k) => k === 0 || read.has(alteFolge[k - 1])));
    ids.forEach(id => altFrei.add(id));
    const zu = [...altFrei].filter(id => !storyUnlocked(STORIES.findIndex(s => s.id === id)));
    // Die naechste ungelesene ist frei, und ihr Reiter ist nicht "zu"
    const n = geschNaechste();
    const fehler = [];
    if(zu.length) fehler.push('zu: ' + zu.join(','));
    if(!storyUnlocked(n)) fehler.push('naechste zu: ' + STORIES[n].id);
    if(geschStand(geschStufe(n)).art === 'zu') fehler.push('Reiter der naechsten zu');
    if(fehler.length) aus.push([ids.length, fehler.join('; ')]);
  }
  return aus;
}"""


def test_alter_lernstand_bleibt_frei(seite, heute_stand):
    seite.starten(stand=heute_stand())
    assert seite.js(PRUEFEN, ALTE_FOLGE) == []
    assert seite.fehler == []


@pytest.mark.parametrize("k", [1, 2, 5, 11, 12, 13, 20, 31])
def test_alter_lernstand_aus_dem_speicher(seite, heute_stand, k):
    """Wie nach dem Update: der gespeicherte Stand nennt die ersten k nach alter Folge.
    Jede davon und die naechste nach alter Folge sind frei, in der Liste sichtbar frei."""
    gelesen = ALTE_FOLGE[:k]
    seite.starten(stand=heute_stand(gelesen=gelesen))
    _geschichten(seite)
    frei = set(gelesen) | {ALTE_FOLGE[k]}
    r = seite.js("""(ids) => {
      const zu = [];
      ids.forEach(id => {
        const i = STORIES.findIndex(s => s.id === id), st = geschStufe(i);
        geschGewaehlt = {st, bei: geschStufe(geschNaechste())}; showStoryPath();
        const knoten = [...document.querySelectorAll('#storyList .node')][geschImReiter(st).indexOf(i)];
        if(!storyUnlocked(i) || knoten.classList.contains('locked')) zu.push(id);
      });
      return zu; }""", sorted(frei))
    assert r == []
    assert seite.fehler == []


def test_beispiele_alte_und_neue_kette(seite, heute_stand):
    seite.starten(stand=heute_stand())
    r = seite.js("""() => {
      const frei = ids => { read.clear(); ids.forEach(id => read.add(id));
        return STORIES.filter((s, i) => storyUnlocked(i)).map(s => s.id); };
      return {
        nichts: frei([]),
        mira: frei(['mira']),
        bis_kuca: frei(['mira', 'kuca1', 'porodica', 'pijaca', 'dan', 'grad', 'jucer', 'put', 'pismo', 'opcina', 'kuca']),
      }; }""")
    assert r["nichts"] == ["mira"]
    # neu: Moja porodica, alt: Naša kuća
    assert r["mira"] == ["mira", "porodica", "kuca1"]
    # A1 und A2 gelesen: neu b1_vrijeme, alt "Razgovor za posao" (stand auf Platz 12)
    assert r["bis_kuca"] == A1 + A2 + ["b1_vrijeme", "intervju"], r["bis_kuca"]
    assert seite.fehler == []


# ---------------------------------------------------------------------------
# In der Geschichte: Kopfzeile, Zaehler, Blaettern
# ---------------------------------------------------------------------------
OFFEN = """(id) => { const i = STORIES.findIndex(s => s.id === id); openStory(i); stilleBitte();
  return {kicker: document.querySelector('#rBody .kicker').textContent, tag: document.getElementById('tag').textContent,
          vor: !document.getElementById('sPrev').disabled, weiter: !document.getElementById('sNext2').disabled}; }"""


@pytest.mark.parametrize("sprache,gid,kicker,tag", [
    ("de", "mira", "A1 · passt zu Level „Farben“", "Geschichte 1 von 5"),
    ("de", "porodica", "A1 · passt zu Level „Familie“", "Geschichte 2 von 5"),
    ("de", "opcina", "A2 · passt zu Level „Amt & Behörde“", "Geschichte 1 von 6"),
    ("de", "intervju", "B1 · passt zu Level „Arbeitsvertrag & Bewerbung“", "Geschichte 21 von 21"),
    ("en", "kuca", "A2 · goes with level “Renting & buying a home”", "Story 4 of 6"),
])
def test_kicker_zeigt_die_stufe(seite, heute_stand, sprache, gid, kicker, tag):
    seite.starten(sprache=sprache, stand=heute_stand(gelesen=ALTE_FOLGE))
    r = seite.js(OFFEN, gid)
    assert r["kicker"].startswith(kicker), r
    assert r["tag"] == tag, r
    assert not re.search(r"(?i)kinderbuch|einfach|mittel|fortgeschritten|amtssprache|picture book|official",
                         r["kicker"]), r
    assert seite.fehler == []


def test_blaettern_ueber_die_stufengrenze(seite, heute_stand):
    """Von der letzten in A1 geht "Nächste" in die erste von A2, "Vorherige" zurück."""
    seite.starten(stand=heute_stand(gelesen=A1))
    r = seite.js(OFFEN, "dan")
    assert r["weiter"] and r["vor"] and r["tag"] == "Geschichte 5 von 5", r
    seite.page.click("#sNext2")
    assert seite.js("() => STORIES[rIdx].id") == "opcina"
    assert seite.js("() => document.getElementById('tag').textContent") == "Geschichte 1 von 6"
    # Na općini ist noch nicht gelesen: weiter zu Jučer geht nicht
    assert seite.js("() => document.getElementById('sNext2').disabled") is True
    seite.page.click("#sPrev")
    assert seite.js("() => STORIES[rIdx].id") == "dan"
    assert seite.fehler == []


ZURUECK = r"""(alteFolge) => {
  const aus = [], gesperrt = [];
  const b = document.getElementById('sPrev');
  for(let k = 0; k <= alteFolge.length; k++){
    read.clear(); alteFolge.slice(0, k).forEach(id => read.add(id));
    STORIES.forEach((s, i) => {
      if(!storyUnlocked(i)) return;
      openStory(i); stilleBitte();
      const vorFrei = i > 0 && storyUnlocked(i - 1);
      if(b.disabled === vorFrei) aus.push([k, s.id, 'Knopf']);
      if(i > 0 && !vorFrei){
        gesperrt.push([k, s.id]);
        // Auch der Horcher selbst fragt nach, falls der Knopf doch einmal frei ist
        b.disabled = false; b.click();
        if(rIdx !== i) aus.push([k, s.id, 'Horcher: ' + STORIES[rIdx].id]);
      }
    });
  }
  stilleBitte();
  return {aus, gesperrt};
}"""


def test_zurueck_nur_in_eine_freie(seite, heute_stand):
    """Pruefung 17.11.2026: "Vorherige" oeffnete die davor ohne nachzufragen. In der
    neuen Folge ist sie bei alten Staenden manchmal gesperrt - wer bis "Kupujemo kuću"
    gelesen hat, darf "Razgovor za posao" lesen, die davor ist "Mejl rođaku" und zu.
    Mit jedem Stand der alten Kette: der Knopf ist genau dann frei, wenn die davor frei
    ist, und auch ein Tipp auf den Horcher oeffnet keine gesperrte."""
    seite.starten(stand=heute_stand())
    r = seite.js(ZURUECK, ALTE_FOLGE)
    assert r["aus"] == [], r["aus"]
    # 37 Faelle, in denen die davor zu ist, darunter die beiden aus der Pruefung
    assert len(r["gesperrt"]) == 37, r["gesperrt"]
    assert [11, "intervju"] in r["gesperrt"] and [5, "grad"] in r["gesperrt"]
    assert seite.fehler == []


def test_zurueck_aus_razgovor_za_posao(seite, heute_stand):
    """Das Beispiel aus der Pruefung, echt getippt: A1 und A2 nach alter Folge gelesen,
    "Razgovor za posao" ist frei und steht am Ende von B1. Zurueck ist gesperrt."""
    seite.starten(stand=heute_stand(gelesen=ALTE_FOLGE[:11]))
    _geschichten(seite)
    assert [x["st"] for x in seite.js(LEISTE) if x["an"]] == ["B1"]
    seite.page.locator("#storyList .node").nth(len(B1) - 1).click()
    seite.js("() => stilleBitte()")
    assert seite.js("() => STORIES[rIdx].id") == "intervju"
    assert seite.js("() => document.getElementById('tag').textContent") == "Geschichte 21 von 21"
    assert seite.js("() => [document.getElementById('sPrev').disabled, storyUnlocked(rIdx - 1)]") == [True, False]
    assert seite.fehler == []


def test_zurueck_geht_nach_dem_lesen_auf(seite, heute_stand):
    """A1 gelesen: "U gradu" ist frei (alte Folge, nach "Moj dan"), "Jučer" davor noch
    nicht. Sind alle Fragen richtig, geht "Jučer" auf - und "Vorherige" mit, ohne die
    Geschichte neu zu oeffnen."""
    seite.starten(stand=heute_stand(gelesen=ALTE_FOLGE[:5]))
    r = seite.js(OFFEN.replace("return {", "window.__f = STORIES[i].fragen.map(f => f.richtig); return {"), "grad")
    assert r["tag"] == "Geschichte 3 von 6" and r["vor"] is False, r
    for richtig in seite.js("() => window.__f"):
        seite.page.locator("#rQ #rOpts .opt").filter(has_text=re.compile("^" + re.escape(richtig) + "$")).first.click()
        weiter = seite.page.locator("#rQ .weiterbox .btn")
        weiter.wait_for(state="visible")
        weiter.click()
    seite.page.locator("#rQ .ergebnis-titel").wait_for(state="visible")
    assert seite.js("() => read.has('grad') && !document.getElementById('sPrev').disabled") is True
    seite.page.click("#sPrev")
    assert seite.js("() => STORIES[rIdx].id") == "jucer"
    assert seite.js("() => document.getElementById('tag').textContent") == "Geschichte 2 von 6"
    assert seite.fehler == []


def test_naechste_nach_allen_fragen_und_tagesaufgabe(seite, heute_stand):
    """Alle Fragen richtig: gelesen, "Nächste Geschichte" fuehrt zur naechsten in der
    neuen Folge (Moja porodica nach Mira i Rex), die Tagesaufgabe zaehlt."""
    seite.starten(stand=heute_stand())
    fragen = seite.js(OFFEN.replace("return {", "window.__f = STORIES[i].fragen.map(f => f.richtig); return {"), "mira")
    assert fragen["tag"] == "Geschichte 1 von 5"
    for richtig in seite.js("() => window.__f"):
        seite.page.locator("#rQ #rOpts .opt").filter(has_text=re.compile("^" + re.escape(richtig) + "$")).first.click()
        weiter = seite.page.locator("#rQ .weiterbox .btn")
        weiter.wait_for(state="visible")
        weiter.click()
    seite.page.locator("#rQ .ergebnis-titel").wait_for(state="visible")
    assert seite.js("() => read.has('mira') && ((tagwerk[today()] || {}).gesch || 0) >= 1") is True
    seite.page.click("#rGoNext")
    assert seite.js("() => STORIES[rIdx].id") == "porodica"
    assert seite.js("() => document.getElementById('tag').textContent") == "Geschichte 2 von 5"
    assert seite.fehler == []
