# -*- coding: utf-8 -*-
"""Die Kopfleiste in EINER Zeile (29.10.2026).

Ajdin hat die v109-Testfassung mit Anmeldung auf seinem S21 Ultra
ausprobiert: links das Herz, rechts Laden, "Ich" und Zahnrad - und die
Muenzen ("0 KM") allein in einer zweiten Zeile. "das muss alles auf einer
Leiste sein".

Ursache war der Profilknopf. Seit v109 steht er nach der Anmeldung in der
Leiste, mit Figur UND Namen; vorher blieb er ohne Server versteckt. Damit
passte die Zeile nicht mehr, und kopfEng() schob die Muenzen nach unten
(header.eng). Jetzt traegt er nur die Figur wie Laden und Zahnrad (der Name
steht im title), und Luecken und Polster sind etwas knapper - siehe das CSS
bei header in web/index.html.

Geprueft wird angemeldet und nicht angemeldet, mit 0 bis 99 999 Muenzen,
Leben als Zahl, ohne Leben und unbegrenzt (Vollversion), auf der
Startseite, in der Levelansicht, in einer Geschichte und im Laden: bei 360,
384 und 412 Punkten Breite steht alles in einer Zeile, nichts ueberlappt,
nichts ragt ueber den Rand. Bei 320 Punkten duerfen die Muenzen in die
zweite Zeile rutschen (der Ausweg von kopfEng() fuer sehr kleine Schirme
und grosse Schrift) - aber auch dort ueberlappt nichts, und die Seite laesst
sich nicht seitlich schieben.

Wie auf dem Handy ist das Capacitor-Plugin App da, die Zuruecktaste oben
gibt es also nicht (setzeZurueck); die hat das Handy selbst.
"""
import pytest
from conftest import Seite
from test_anmeldung import PLUGIN, _gelernt, _mail_anmelden, _starten

# Wie auf dem Handy: mit dem Plugin App blendet setzeZurueck() die Taste aus.
HANDY = PLUGIN + "\nwindow.Capacitor.Plugins.App = {};\n"

# Lage der Pillen und Knoepfe im Kopf
KOPF = """() => { const h = document.querySelector('header'), k = h.getBoundingClientRect();
  const teile = [...h.querySelectorAll('.livesbar, .muenzbar, .hbtns .back')]
    .filter(e => e.offsetParent && e.getClientRects().length)
    .map(e => { const r = e.getBoundingClientRect();
                return {id: e.id, l: r.left, r: r.right, o: r.top, u: r.bottom}; })
    .sort((a, b) => a.l - b.l);
  const p = document.getElementById('btnProfil');
  return {eng: h.classList.contains('eng'), links: k.left, rechts: k.right, teile,
          zeilen: new Set(teile.map(x => Math.round(x.o))).size,
          seite: document.documentElement.scrollWidth, breit: innerWidth,
          profil: {titel: p.title, text: p.innerText.trim(), breit: p.getBoundingClientRect().width}}; }"""

# Die Ansichten mit Kopfleiste
ANSICHTEN = [
    ("start", "homeMode = 'words'; showHome();"),
    ("level", "openLevel(0);"),
    ("geschichte", "openStory(0);"),
    ("laden", "showLaden();"),
]

# Muenzen und Leben: (Name, Muenzen, Leben, Vollversion)
STAENDE = [
    ("0km", 0, 5, False),
    ("999km", 999, 3, False),
    ("12345km_0leben", 12345, 0, False),
    ("99999km_unbegrenzt", 99999, 5, True),
]

STAND_SETZEN = """([km, leben, voll]) => { muenzenGes = km; muenzenAus = 0;
  lives = {anzahl: leben, zeit: Date.now()}; premium = voll; renderLives(); }"""

# Wie gross ist die Flaeche, die einen Tipp annimmt? Senkrecht und
# waagerecht durch die Mitte abgetastet, in halben Punkten.
TREFFER = """(id) => { const e = document.getElementById(id), r = e.getBoundingClientRect();
  const cx = (r.left + r.right) / 2, cy = (r.top + r.bottom) / 2;
  const trifft = (x, y) => { const z = document.elementFromPoint(x, y); return !!z && (z === e || e.contains(z)); };
  let hoch = 0, breit = 0;
  for(let y = r.top - 20; y <= r.bottom + 20; y += 0.5) if(trifft(cx, y)) hoch += 0.5;
  for(let x = r.left - 20; x <= r.right + 20; x += 0.5) if(trifft(x, cy)) breit += 0.5;
  return {hoch, breit, kreis: [Math.round(r.width), Math.round(r.height)], oben: r.top - 7}; }"""


def _kontext(browser, basis, breite, hoehe):
    ctx = browser.new_context(viewport={"width": breite, "height": hoehe}, locale="de-DE",
                              service_workers="block", reduced_motion="reduce")
    return ctx, Seite(ctx.new_page(), basis)


def angemeldet(seite, cloud_html, heute_stand):
    """Mit E-Mail angemeldet, wie Ajdin: der Profilknopf steht im Kopf."""
    seite.page.add_init_script(HANDY)
    attrappe = _starten(seite, cloud_html, stand=_gelernt(heute_stand), plugin=False)
    attrappe.konto_anlegen("ich@probe.example", "Geheim#123")
    _mail_anmelden(seite, "ich@probe.example", "Geheim#123")
    seite.page.wait_for_function("() => sichtbar('pfad') && $('btnProfil').style.display === 'inline-block'")
    return attrappe


def ansicht(seite, js, stand):
    seite.js("async () => { stilleBitte(); " + js + " await new Promise(r => setTimeout(r, 200)); }")
    seite.js(STAND_SETZEN, list(stand))
    seite.page.wait_for_function("() => [...document.querySelectorAll('header img.sym')].every(i => i.complete)")
    return seite.js(KOPF)


def trefferflaechen(seite):
    """Pruefung 29.10.2026: Laden, Profil und Zahnrad sind sichtbar 38 x 38,
    zum Tippen aber 42 x 48 (::after); das Herz nimmt Tipps auf der ganzen
    Pille an statt nur auf 49 x 23. Nichts ueberlappt: die Muenzen und
    jeder Knopf bekommen den Tipp auf ihre eigene Mitte."""
    for knopf in ("btnShop", "btnProfil", "btnSettings"):
        f = seite.js(TREFFER, knopf)
        assert f["kreis"] == [38, 38] and f["oben"] >= 0, (knopf, f)
        assert f["hoch"] >= 47.5 and f["breit"] >= 41.5, (knopf, f)
    f = seite.js(TREFFER, "livesKnopf")
    assert f["hoch"] >= 47.5 and f["breit"] >= 48, f
    assert seite.js("""() => ['muenzBar', 'btnShop', 'btnProfil', 'btnSettings', 'livesKnopf'].every(id => {
        const e = document.getElementById(id), r = e.getBoundingClientRect();
        const z = document.elementFromPoint((r.left + r.right) / 2, (r.top + r.bottom) / 2);
        return z === e || e.contains(z); })""")


def pruefen(k, eine_zeile=True):
    """Eine Zeile (oder bei 320 Punkten hoechstens zwei), nichts
    ueberlappt, nichts ragt ueber den Rand."""
    if eine_zeile:
        assert not k["eng"] and k["zeilen"] == 1, k
    else:
        assert k["zeilen"] <= 2, k
    t = k["teile"]
    for i, a in enumerate(t):
        assert a["l"] >= k["links"] - 0.5 and a["r"] <= k["rechts"] + 0.5, (a, k)
        for b in t[i + 1:]:
            neben = a["r"] <= b["l"] + 0.5 or b["r"] <= a["l"] + 0.5
            ueber = a["u"] <= b["o"] + 0.5 or b["u"] <= a["o"] + 0.5
            assert neben or ueber, ("ueberlappt", a, b, k)
    assert k["seite"] <= k["breit"], k


@pytest.mark.parametrize("breite,hoehe", [(360, 800), (384, 854), (412, 915)])
def test_angemeldet_alles_in_einer_zeile(browser, basis, cloud_html, heute_stand, breite, hoehe):
    ctx, seite = _kontext(browser, basis, breite, hoehe)
    try:
        angemeldet(seite, cloud_html, heute_stand)
        for name, js in ANSICHTEN:
            for stand in STAENDE:
                k = ansicht(seite, js, stand[1:])
                ids = [x["id"] for x in k["teile"]]
                assert ids == ["livesBar", "muenzBar", "btnShop", "btnProfil", "btnSettings"], (name, stand, ids)
                pruefen(k)
        # Der Profilknopf: nur die Figur, rund wie Laden und Zahnrad, der
        # Name fuer Bildschirmleser im title.
        assert k["profil"] == {"titel": "Profil", "text": "", "breit": 38}, k["profil"]
        # Zum Tippen gross genug, auf der Startseite und im Laden.
        for name, js in (ANSICHTEN[0], ANSICHTEN[3]):
            ansicht(seite, js, STAENDE[-1][1:])
            trefferflaechen(seite)
        assert seite.fehler == []
    finally:
        ctx.close()


@pytest.mark.parametrize("breite", [360, 412])
def test_ohne_anmeldung_alles_in_einer_zeile(browser, basis, heute_stand, breite):
    """Die Quelle (CLOUD_AN = false) und der Weg "Erst einmal
    weiterlernen": ohne Profilknopf, sonst gleich."""
    ctx, seite = _kontext(browser, basis, breite, 800)
    try:
        seite.page.add_init_script("window.Capacitor = {Plugins: {App: {}}};")
        seite.starten(stand=heute_stand())
        for name, js in ANSICHTEN:
            for stand in STAENDE:
                k = ansicht(seite, js, stand[1:])
                assert [x["id"] for x in k["teile"]] == ["livesBar", "muenzBar", "btnShop", "btnSettings"], (name, stand)
                pruefen(k)
        assert seite.fehler == []
    finally:
        ctx.close()


def test_320_bricht_nicht(browser, basis, cloud_html, heute_stand):
    """Bei 320 Punkten passt eine kurze Muenzzahl noch in die Zeile; bei
    vier, fuenf Stellen duerfen die Muenzen darunter in die Mitte. Kein
    Element faellt weg, nichts ueberlappt, nichts schiebt die Seite."""
    ctx, seite = _kontext(browser, basis, 320, 640)
    try:
        angemeldet(seite, cloud_html, heute_stand)
        for name, js in ANSICHTEN:
            for stand in STAENDE:
                k = ansicht(seite, js, stand[1:])
                assert len(k["teile"]) == 5, (name, stand, k)
                pruefen(k, eine_zeile=stand[1] < 1000)
        assert seite.fehler == []
    finally:
        ctx.close()
