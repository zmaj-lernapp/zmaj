# -*- coding: utf-8 -*-
"""Schreiben der Cloud-Sicherung mit Antwortmaske (20.11.2026, Optimierung
Punkt 4) - im echten Browser.

Ohne Maske schickt Firestore auf jedes PATCH das ganze Dokument zurueck,
beim Vollstand rund 0,9 MB, die die App nie liest (geprueft_netz.md B1). Mit
mask.fieldPaths=rev kommt nur rev zurueck. Die Falle daneben:
updateMask.fieldPaths=rev schriebe NUR rev, und daten bliebe alt - eine
still veraltete Sicherung. Geprueft wird hier:
  - die genaue Adresse des Schreibens, und dass nur rev zurueckkommt,
  - dass trotzdem der ganze Stand geschrieben wird (genau das, was die App
    schickt) - und dass genau diese Pruefung die Falle bemerkt,
  - dass die Attrappe die beiden Parameter wie Firestore unterscheidet.
Firebase beantwortet firebase_attrappe.py, kein Byte verlaesst den Rechner.
"""
import json

import pytest
from firebase_attrappe import FIREBASE, PROJEKT, UID, Attrappe

ADRESSE = ("https://firestore.googleapis.com/v1/projects/%s/databases/(default)/documents/users/%s"
           "?mask.fieldPaths=rev" % (PROJEKT, UID))
# Wie die Home-Taste: in den Hintergrund mit etwas Neuem.
WEG_MIT_NEUEM = """(woerter) => {
    woerter.forEach(w => known.add(w));
    Object.defineProperty(document, 'hidden', {configurable: true, get: () => true});
    document.dispatchEvent(new Event('visibilitychange'));
}"""
# Die Falle nachgestellt: dieselbe App, aber mit updateMask statt mask.
FALLE = """() => { const echt = window.fetch;
    window.fetch = (url, o) => echt(o && o.method === 'PATCH'
        ? String(url).replace('?mask.fieldPaths=', '?updateMask.fieldPaths=') : url, o); }"""


def _starten(seite, heute_stand, cloud_html):
    attrappe = Attrappe()
    seite.page.route("**/app/index.html", lambda r: r.fulfill(
        status=200, content_type="text/html; charset=utf-8", body=cloud_html))
    for host in FIREBASE:
        seite.page.route("https://%s/**" % host, attrappe)
    gesendet = []
    seite.page.on("request", lambda r: gesendet.append((r.url, r.post_data))
                  if r.method == "PATCH" and "firestore.googleapis.com" in r.url else None)
    seite.starten(stand=heute_stand())
    assert seite.js("async () => await cloudAnmelden('anonym')") is True
    seite.page.wait_for_function("() => !cloudLaeuft")
    return attrappe, gesendet


def _zweites_schreiben(seite, attrappe, woerter):
    seite.js(WEG_MIT_NEUEM, woerter)
    for _ in range(400):
        if len(attrappe.schreiben) >= 2:
            break
        seite.page.wait_for_timeout(25)
    seite.page.wait_for_function("() => !cloudLaeuft")


def _ganz_gesichert(attrappe, gesendet):
    """Steht in der Cloud genau das, was die App zuletzt geschickt hat -
    daten UND rev, und nichts sonst?"""
    return json.loads(gesendet[-1][1])["fields"] == attrappe.dok


def test_schreiben_fragt_nur_rev_zurueck(seite, heute_stand, cloud_html):
    attrappe, gesendet = _starten(seite, heute_stand, cloud_html)
    # Das erste Schreiben gleich nach der Anmeldung (es gibt noch kein Dokument).
    assert [u for u, _ in gesendet] == [ADRESSE]
    assert attrappe.schreiben[0]["query"] == "mask.fieldPaths=rev"
    assert attrappe.schreiben[0]["mask"] == ["rev"] and attrappe.schreiben[0]["updateMask"] is None
    assert attrappe.schreiben[0]["antwort"] == {"fields": {"rev": attrappe.dok["rev"]}}
    assert set(attrappe.dok) == {"daten", "rev"}

    # Das naechste Schreiben (beim Verlassen) ebenso.
    _zweites_schreiben(seite, attrappe, ["neu:maske-eins"])
    assert [u for u, _ in gesendet] == [ADRESSE, ADRESSE]
    assert [s["query"] for s in attrappe.schreiben] == ["mask.fieldPaths=rev"] * 2
    assert attrappe.schreiben[1]["antwort"] == {"fields": {"rev": attrappe.dok["rev"]}}
    merker = seite.js("() => JSON.parse(localStorage.getItem('zmaj_cloud'))")
    assert merker["rev"] == attrappe.dok["rev"]["stringValue"]
    assert seite.fehler == []


@pytest.mark.parametrize("falle", [False, True], ids=["mask", "falle_updateMask"])
def test_mit_antwortmaske_wird_der_ganze_stand_geschrieben(seite, heute_stand, cloud_html, falle):
    """Mit der Antwortmaske steht danach genau der geschickte Stand in der
    Cloud, mit den neuen Woertern. Die Gegenprobe (falle): schreibt die App
    updateMask statt mask, bleibt daten alt - und genau diese Pruefung
    schlaegt dann an."""
    attrappe, gesendet = _starten(seite, heute_stand, cloud_html)
    assert _ganz_gesichert(attrappe, gesendet)
    vorher = attrappe.dok["daten"]
    if falle:
        seite.js(FALLE)
    neu = ["neu:maske-zwei", "neu:maske-drei"]
    _zweites_schreiben(seite, attrappe, neu)
    assert len(gesendet) == 2
    geschickt = json.loads(gesendet[-1][1])["fields"]
    assert set(geschickt) == {"daten", "rev"}
    assert set(neu) <= set(json.loads(geschickt["daten"]["stringValue"])["stand"]["gewusst"])
    if falle:
        assert attrappe.schreiben[-1]["updateMask"] == ["rev"]
        assert attrappe.dok["daten"] == vorher                  # daten still alt
        assert not _ganz_gesichert(attrappe, gesendet)
    else:
        assert _ganz_gesichert(attrappe, gesendet)
        assert set(neu) <= set(json.loads(attrappe.dok["daten"]["stringValue"])["stand"]["gewusst"])
    assert seite.fehler == []


# ------------------------------------------ die Attrappe ohne Browser ---

class _Anfrage:
    def __init__(self, abfrage, felder):
        self.url = ("https://firestore.googleapis.com/v1/projects/%s/databases/(default)/documents/users/%s%s"
                    % (PROJEKT, UID, abfrage))
        self.method = "PATCH"
        self.headers = {"authorization": "Bearer id-1"}
        self.post_data = json.dumps({"fields": felder})


class _Weg:
    def __init__(self):
        self.antwort = None

    def fulfill(self, status, headers=None, content_type=None, body=None):
        self.antwort = (status, json.loads(body))

    def abort(self):
        self.antwort = "abgebrochen"


def _patch(attrappe, abfrage, felder):
    weg = _Weg()
    attrappe(weg, _Anfrage(abfrage, felder))
    return weg.antwort


ALT = {"daten": {"stringValue": "alt"}, "rev": {"stringValue": "r1"}}
NEU = {"daten": {"stringValue": "neu"}, "rev": {"stringValue": "r2"}}


def test_attrappe_ohne_maske_ersetzt_und_schickt_alles():
    a = Attrappe()
    a.dok = dict(ALT, extra={"stringValue": "x"})
    assert _patch(a, "", NEU) == (200, {"fields": NEU})
    assert a.dok == NEU
    assert a.schreiben[-1]["mask"] is None and a.schreiben[-1]["updateMask"] is None


def test_attrappe_antwortmaske_schreibt_alles_und_schickt_nur_rev():
    a = Attrappe()
    a.dok = dict(ALT)
    assert _patch(a, "?mask.fieldPaths=rev", NEU) == (200, {"fields": {"rev": NEU["rev"]}})
    assert a.dok == NEU


def test_attrappe_updatemask_schreibt_nur_rev():
    """Die Falle: updateMask.fieldPaths=rev laesst daten alt."""
    a = Attrappe()
    a.dok = dict(ALT)
    assert _patch(a, "?updateMask.fieldPaths=rev", NEU) == (200, {"fields": {"daten": ALT["daten"],
                                                                             "rev": NEU["rev"]}})
    assert a.dok == {"daten": ALT["daten"], "rev": NEU["rev"]}
    # Ein Feld in der Schreibmaske, das im Koerper fehlt, ist danach weg.
    _patch(a, "?updateMask.fieldPaths=daten", {"rev": {"stringValue": "r3"}})
    assert a.dok == {"rev": NEU["rev"]}
    # Beide zusammen: nur rev geschrieben, nur rev zurueck.
    a.dok = dict(ALT)
    assert _patch(a, "?updateMask.fieldPaths=rev&mask.fieldPaths=rev", NEU) == (200, {"fields": {"rev": NEU["rev"]}})
    assert a.dok["daten"] == ALT["daten"]
