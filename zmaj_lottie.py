# -*- coding: utf-8 -*-
# Erzeugt web/maskottchen/zmaj.json: Drache "Zmaj" als Lottie-Animation.
#
# v7 (15.10.2026): BILD-DRACHE. Ajdin hat nach den Vorschauen entschieden,
# dass die Bildteile aus Google Gemini "viel besser" aussehen: der Gemini-
# Drache ist jetzt der Drache der App. Das Rig bleibt das der Variante B
# unten (Kopf wie im Bild, --kopf 1.0) mit allen Zeitleisten und Markern;
# statt der Vektorformen haengen an seinen Ebenen 32 Bilder (Lottie-Ebenen
# ty 2, Abschnitt "Bild-Drache" und BILD_TEILE): Rumpf mit Beinen, zwei
# Fluegel, Schwanz, Ober- und Unterarme (Oberarm haengend und erhoben,
# Unterarm offen, als Faust fuer den Jubel, an der Wange fuers Weinen)
# und je Stimmung ein ganzer Kopf mit den
# Hornspitzen als eigenem Bild. Augen, Lider, Brauen, Muender und Traenen
# stecken im Kopfbild; das Gesicht wechselt mit der Stimmung, im Leerlauf
# blinzelt er mit einem eigenen Kopf.
# Die Bilder liegen NICHT in der JSON-Datei, sondern als WebP daneben:
# web/maskottchen/teile/<teil>.webp (Grundfarbe) und je Hautfarbe
# web/maskottchen/haut/<farbe>/<teil>.webp - beides schreibt haut_einbauen.py
# aus den PNG-Teilen. In zmaj.json steht u = "teile/" relativ zur Datei; die
# App setzt den Pfad beim Laden selbst (zmajDaten in web/index.html) und
# nimmt den Hautsatz der getragenen Farbe, wenn es ihn gibt.
# Kostueme (Zierrat): Seit 16.10.2026 sind 24 Stuecke von Gemini gemalt -
# Huete, Kronen, Brillen und Ohrensachen je fuer den Kopf von vorn und
# abgewandt, Kleidung mit Aermeln je Armteil, die Funkelsterne einzeln
# (Abschnitt "Gemalte Kostueme", GEMALT); ihre Bilder liegen in
# web/maskottchen/zierrat/<stueck>/. Was am Kopf sitzt, wechselt die
# Fassung nach dem Kopfplan (KOPFPLAN). Vektor sind nur noch die Galaxie-
# Sterne und der Rueckfall des Skeletts; die Vektor-Fassungen der anderen
# Stuecke liefert nur noch --vektor aus. Das Skelett (Halloween) ist seit
# 16.10.2026 der gemalte Hautsatz haut/skelett/ (nur Knochen, wie die
# Fest-Entscheidung vom 01.10.2026 verlangt); das Vektor-Skelett weicht ihm
# und bleibt der Rueckfall (HAUT_ERSETZT).
# Bewegung: Nach Ajdins Rueckmeldung zum Probevideo (15.10.2026) hat der
# Bild-Drache eigene, ruhigere Zeitleisten ("Bewegung des Bild-Drachen"):
# beim Jubel liegen die Arme vor den Fluegeln statt darin, der Kopf neigt
# sich hoechstens 4,5 Grad um den Halspunkt und rutscht nicht vom Hals, und
# jede Stimmung beginnt und endet in der Ruhe. Der Kopf wechselt hart, mit
# einem kurzen Blinzeln dazwischen (KOPF_WECHSEL). Bei einer falschen
# Antwort (no, no_l, no_r) schuettelt er seit 16.10.2026 richtig den Kopf:
# die gemalten abgewandten Koepfe links und rechts im Wechsel, dazwischen
# der finstere Frontkopf, ohne den Kopf um den Hals zu kippen (SCHUETTELN).
# Welcher Kopf in welchem Bild zu sehen ist, steht an EINER Stelle, im
# Kopfplan (KOPFPLAN, kopf_deckkraft, kopf_spur); Kopfbilder, Hornspitzen,
# Kopf-Kostueme und das Vektor-Skelett richten sich alle danach.
# --vektor behaelt die alten Zeitleisten.
#   python zmaj_lottie.py           Bild-Drache, schreibt nach web/maskottchen
#   python zmaj_lottie.py --vektor  der gezeichnete Drache v6 wie bisher
#                                   (Kopf 1.2) - nur noch zum Vergleichen, er
#                                   wird nicht weiter verfeinert
#
# v6 (14.10.2026): neue Figur nach den Vorlagen, die Ajdin ausgesucht hat
# (Profilbild/Entwuerfe_Gemini/pro_vorne.png und die Stimmungsbilder daneben,
# Stil "Entwurf 1"). Der Drache STEHT jetzt, frontal, ohne Buecherstapel:
# blauer Koerper mit dunkelblauem Umriss, grosse Flughaeute mit Fingerknochen
# und gewelltem Unterrand, goldene geriffelte Hoerner, ein kleiner Stachel in
# der Kopfmitte, seitliche Ohrflossen, grosse Augen mit Glanzpunkt, Schnauze
# mit Nasenloechern, gelber gerippter Bauch vom Hals bis zwischen die Beine,
# Schwanz nach rechts mit Stacheln und Pfeilspitze.
# Die Formen sind an der Vorlage abgemessen: Punkte stehen in Pixeln von
# pro_vorne.png (2048 x 2048) und werden mit V() bzw. Hk() auf die Leinwand
# umgerechnet. Wer etwas nachmessen will, legt die Vorlage daneben.
#
# Vertrag mit der App (nicht aendern, ohne web/index.html mitzuziehen):
#   Leinwand 520 x 500, 30 Bilder/s.
#   Stimmungen als Marker: idle, cheer, sad, ok, no, cry (Traenen), no_l, no_r -
#   mit denselben Bildbereichen wie bisher (SEG unten).
#   no_l und no_r sind zwei Fassungen fuer eine falsche Antwort: Der Drache
#   wendet den Kopf ab - einmal nach links, einmal nach rechts - und schaut
#   dabei traurig. Die App wechselt sich damit ab, damit es nach mehreren
#   Fehlern nicht immer gleich aussieht. Beim Bild-Drachen (seit 16.10.2026)
#   schuetteln no, no_l und no_r den Kopf und schauen dabei durchgehend
#   finster; no_l beginnt nach links, no_r nach rechts (SCHUETTELN).
#   Ebenennamen: an "head", "body", "armL"/"armR", "wingL"/"wingR", "tail"
#   haengen Kostueme (seit 15.10.2026 auch an "unterarmL"/"unterarmR": die
#   langen Jackenaermel); "skelett" leert per zmaj_leert die Fleisch-Ebenen.
#   Die App sortiert die Ebenen nach "ind" - darum stehen die Bild-Ebenen in
#   ORDER direkt vor ihrer Rig-Ebene (v7).
#   Farben: Beim Bild-Drachen ist eine Hautfarbe ein Bildsatz (haut/<farbe>/).
#   Nur ohne Satz - und beim Vektor-Drachen - tauscht die App die acht
#   Farben in FARB_QUELLE (web/index.html) per exaktem Abgleich, siehe
#   "Farben" unten; die Kostuemfarben liegen alle ausserhalb davon.
#
# Kopfgroesse: Aufruf mit --kopf F skaliert die ganze Kopfgruppe (mit Hoernern,
# Augen, Gesicht und allen Kopf-Kostuemen) um den Hals.
#   --kopf 1.0  Variante B: Proportionen wie in der Vorlage. Standard fuer
#               den Bild-Drachen - Ajdin, 15.10.2026: Kopf wie im Bild.
#   --kopf 1.2  Variante A: Kopf 20 % groesser, damit Gesicht und Stimmung im
#               kleinen Feld (100-120 px) lesbar bleiben. Standard mit
#               --vektor (bis 15.10.2026 die Fassung der App).
#   --aus ORDNER  schreibt zmaj.json und alle zmajz-*.json dorthin statt nach
#               web/maskottchen (zum Vergleichen, ohne die App anzufassen).
#               Die Bilder bleiben in web/maskottchen; render.js findet sie.
# In Thonny ausfuehren (F5) erzeugt den Bild-Drachen in web/maskottchen.
import json, os, math, sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def _schalter(name, vorgabe):
    """--name WERT aus der Befehlszeile; ohne Angabe die Vorgabe (Thonny)."""
    if "--" + name in sys.argv:
        i = sys.argv.index("--" + name)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return vorgabe


# v7, 15.10.2026: Standard ist der Bild-Drache (siehe Kopfkommentar), Kopf
# wie in den Bildern (1.0). --vektor baut den gezeichneten Drachen v6 wie
# bisher, mit Kopf 1.2 als Vorgabe - nur noch zum Vergleichen.
VEKTOR = "--vektor" in sys.argv
KOPF = float(_schalter("kopf", "1.2" if VEKTOR else "1.0"))
AUSGABE = _schalter("aus", "web/maskottchen")

W, H, FR = 520, 500, 30
SEG = {"idle": (0, 90), "cheer": (90, 150), "sad": (150, 210), "ok": (210, 240), "no": (240, 270), "cry": (270, 360),
       "no_l": (360, 400), "no_r": (400, 440)}
OP = 440

# ---------- Farben ----------
# Acht Rollen, die die App beim Umfaerben tauscht (FARB_QUELLE in web/index.html,
# gleiche Reihenfolge). Abgemessen an pro_vorne.png, 14.10.2026:
#   BLUE    Koerper                         415EA1
#   BLUE_L  hell: Lichtkanten, Schnauze     5281B3
#   BLUE_D  dunkel: der UMRISS, Schatten (halb deckend), Brauen, Mundlinie,
#           Nasenloecher - alles Dunkle, das mit der Haut die Farbe wechseln
#           soll. Gruener Drache = dunkelgruener Umriss.
#   WING    Flughaut                        7E9CDF
#   WING_D  Flughautschatten                6282CC
#   YEL     Bauch und Hoerner               F6C044
#   YEL_D   Bauchrillen, Bauchkante, Schatten auf Gold
#   AMBER   Umriss der Hoerner (in der Vorlage braun statt blau)
# Was nie umfaerben darf - Augenweiss, Iris, Pupille, Zunge, Maul, Traenen -
# hat eigene Werte, die keiner der acht gleichen.
def col(h): h = h.lstrip("#"); return [int(h[i:i+2], 16)/255 for i in (0, 2, 4)] + [1]
BLUE = col("415EA1"); BLUE_L = col("5281B3"); BLUE_D = col("26366A"); WING = col("7E9CDF"); WING_D = col("6282CC")
YEL = col("F6C044"); YEL_D = col("D79536"); AMBER = col("A86D27"); WHITE = col("FFFFFF"); INK = col("0B1533")
IRIS = col("3C6BB3"); IRIS_D = col("2A4F8F"); PUPILLE = col("112649")
RED = col("7A1F2B"); TONGUE = col("FF7B8E"); TEAR = col("8FD3FF")
# Zierrat aus dem Laden. Warme Töne, damit sie sich vom blauen Kopf abheben.
HUT = col("C8392B"); HUT_D = col("9E2A1E"); HUT_HELL = col("FFF1E0")
KRONE = col("F5C518"); KRONE_D = col("C79A00"); STEIN = col("C8392B")
GLAS = col("BFD8FF"); RAHMEN = col("2B2B2B")
KH = col("2B2B2B"); KH_HELL = col("5A5A5A"); KH_POLSTER = col("F5C518")
# Vier Sätze, die am 18.09.2026 dazugekommen sind: bosnisch, Winter, cool,
# fleißig. Alle deutlich dunkler oder wärmer als Blau und Gelb des Drachen,
# sonst verschwinden sie auf ihm.
FES = col("A4161A"); FES_D = col("74100F"); QUASTE = col("14141A")
# 0C2A8A war zu nah am Blau des Drachen - Trikot und Flaggenschal
# verschwanden auf ihm. Jetzt ein deutlich dunkleres Marineblau, dazu ueberall
# eine helle Kante, damit sich das Stueck vom Koerper abhebt.
# Tiefes Koenigsblau wie auf dem Trikot der Nationalelf, dazu Gold fuer die
# Laengsstreifen. Deutlich dunkler als das Blau des Drachen (2448B8), sonst
# verschwindet das Trikot auf ihm.
TRIKOT = col("142D82"); TRIKOT_H = col("F2C42C"); TRIKOT_W = col("FFFFFF"); TRIKOT_D = col("0A1C56")
SCHAL_B = col("101C5C"); SCHAL_G = col("FFD23F")
WOLLE = col("C8392B"); WOLLE_D = col("8E2318"); FELL = col("FFF1E0")
KAPPE = col("1F7A4D"); KAPPE_D = col("125232"); KAPPE_H = col("35B075")
LEDER = col("4A3020"); LEDER_H = col("744E33"); NIET = col("C9A227")
# Umhang und grosse Krone: die beiden Stuecke, die es nur mit der
# Vollversion gibt. Dunkles Weinrot mit Goldkante - warm genug, um sich
# vom blauen Koerper abzuheben, und dunkel genug, dass die gelbe Kante
# darauf leuchtet. Auf einem goldenen Drachen traegt die dunkle Flaeche.
UMHANG = col("BE1622"); UMHANG_D = col("8A0F17"); UMHANG_H = col("F2C94C")
# Roeter als der erste Entwurf: 6B1F3A war ein Weinrot und zog ins
# Violette. Ajdin am 29.09.2026: "gibt es kein roetlicheres rot fuer den
# koeniglichen umhang". Jetzt ein klares Rot, wie man es von
# Kroenungsmaenteln kennt.
PERLE = col("FFF6DC")
DUNKELGLAS = col("1C1C24"); GLANZ = col("FFFFFF")
DOKTOR = col("23252B"); DOKTOR_H = col("454956")
STRICK = col("7B3F51"); STRICK_H = col("A85C72"); STRICK_D = col("55283A")   # Weinrot: hebt sich von Blau UND Gelb ab
GOLDR = col("C9A227")

# ---------- Keyframes ----------
def anim(pairs, dims=1):
    # dims wird nicht mehr gebraucht: lottie-web nimmt fuer jede Dimension
    # den ersten Wert der Kurve, wenn nur einer dasteht (v6, spart Platz).
    ks = []
    for idx, p in enumerate(pairs):
        t, v = p[0], p[1]; hold_ = len(p) > 2 and p[2]
        k = {"t": t, "s": v if isinstance(v, list) else [v]}
        if hold_: k["h"] = 1
        elif idx < len(pairs) - 1:
            k["i"] = {"x": [0.35], "y": [1]}; k["o"] = {"x": [0.65], "y": [0]}
        ks.append(k)
    return {"a": 1, "k": ks}
def const(v): return {"a": 0, "k": v}
def hold(t, v): return (t, v, True)


def spur(werte, ruhe, dims=1):
    """Eine Zeitleiste ueber alle Stimmungen.
    werte: {abschnitt: [(t, wert), ...]}, t RELATIV zum Abschnittsbeginn.
    Fehlt ein Abschnitt, steht dort die Ruhe. Der letzte Wert jedes Abschnitts
    wird GEHALTEN bis zum naechsten Abschnitt: die App spielt immer nur einen
    Abschnitt (playSegments), und Lottie soll nie ueber eine Grenze hinweg
    in die naechste Stimmung hineinrechnen. v5 hielt stattdessen den ERSTEN
    Wert eines Abschnitts - dadurch sprang z. B. "sad" bei jeder Schleife
    nach zwoelf Bildern ruckartig in die Pose."""
    ks = []
    for name, (a, e) in sorted(SEG.items(), key=lambda kv: kv[1][0]):
        liste = werte.get(name) or [(0, ruhe)]
        for j, (t, v) in enumerate(liste):
            assert 0 <= t < e - a, (name, t)
            ks.append(hold(a + t, v) if j == len(liste) - 1 else (a + t, v))
    return anim(ks, dims)

# ---------- Formen (Listen von unten nach oben; put() dreht um) ----------
def fill(c, o=100): return {"ty": "fl", "c": const(c), "o": const(o), "r": 1}
def stroke(c, w, o=100): return {"ty": "st", "c": const(c), "o": const(o), "w": const(w), "lc": 2, "lj": 2}
def ellipse(cx, cy, w, h): return {"ty": "el", "p": const([cx, cy]), "s": const([w, h])}
def rect(cx, cy, w, h, r=0): return {"ty": "rc", "p": const([cx, cy]), "s": const([w, h]), "r": const(r)}
def tr(r=0, o=100, p=(0, 0), s=(100, 100), a=(0, 0)):
    return {"ty": "tr", "p": const(list(p)), "a": const(list(a)), "s": const(list(s)), "r": const(r), "o": const(o)}
def group(*items, r=0, o=100, p=(0, 0), s=(100, 100)): return {"ty": "gr", "it": list(items) + [tr(r, o, p, s)]}
def poly(points):   # Vieleck mit scharfen Ecken, z. B. für Zähne
    return {"ty": "sh", "ks": const({"c": True, "v": [list(p) for p in points], "i": [[0, 0]]*len(points), "o": [[0, 0]]*len(points)})}
def _ausduennen(points, scharf, eps):
    """Punkte weglassen, die kaum etwas am Umriss aendern (Ramer-Douglas-
    Peucker, eps in Einheiten der Ebene). Die an der Vorlage abgemessenen
    Umrisse haben dicht liegende Punkte; ohne Ausduennen wurde zmaj.json
    v6 ueber 140 KB gross. Ecken (scharf) und Anfang/Ende bleiben."""
    n = len(points)
    if n < 8 or eps <= 0:
        return points, scharf
    fest = sorted({0, n - 1} | set(scharf))
    behalten = set(fest)
    def teile(a, b):
        if b - a < 2: return
        (ax, ay), (bx, by) = points[a], points[b]
        l = math.hypot(bx - ax, by - ay) or 1
        k, d = max(((i, abs((bx - ax) * (ay - points[i][1]) - (ax - points[i][0]) * (by - ay)) / l) for i in range(a + 1, b)),
                   key=lambda q: q[1])
        if d > eps:
            behalten.add(k); teile(a, k); teile(k, b)
    for a, b in zip(fest, fest[1:]):
        teile(a, b)
    neu = sorted(behalten)
    return [points[i] for i in neu], tuple(neu.index(i) for i in scharf if i in behalten)
AUSDUENNEN = 0.6
def smooth(points, closed=True, tension=0.6, scharf=()):
    """Rundet die Ecken eines Streckenzugs. scharf = Nummern der Punkte, die
    trotzdem eine echte Ecke bleiben sollen - gebraucht fuer den V-Ausschnitt:
    eine gerundete Spitze saehe aus wie ein Rundhals."""
    points, scharf = _ausduennen(list(points), tuple(scharf), AUSDUENNEN)
    n = len(points); v = []; it = []; ot = []
    scharf = set(scharf)
    for k in range(n):
        p0 = points[(k-1) % n] if closed else points[max(k-1, 0)]
        p1 = points[k]; p2 = points[(k+1) % n] if closed else points[min(k+1, n-1)]
        if k in scharf:
            tx = ty = 0
        else:
            tx = (p2[0]-p0[0]) * tension / 2; ty = (p2[1]-p0[1]) * tension / 2
        v.append([round(p1[0], 2), round(p1[1], 2)]); it.append([round(-tx, 2), round(-ty, 2)]); ot.append([round(tx, 2), round(ty, 2)])
    return {"ty": "sh", "ks": const({"c": closed, "v": v, "i": it, "o": ot})}
def arc(a, b, bulge):
    """Bogen von a nach b; bulge > 0 wölbt nach unten (y wächst nach unten)."""
    dx = (b[0]-a[0]) * 0.45
    return {"ty": "sh", "ks": const({"c": False, "v": [list(a), list(b)], "i": [[0, 0], [-dx, bulge]], "o": [[dx, bulge], [0, 0]]})}
def taper(center, widths, tension=0.6):
    n = len(center); left = []; right = []
    for k in range(n):
        p0 = center[max(k-1, 0)]; p2 = center[min(k+1, n-1)]
        dx, dy = p2[0]-p0[0], p2[1]-p0[1]; l = math.hypot(dx, dy) or 1
        nx, ny = -dy/l, dx/l; w = widths[k]/2
        left.append((center[k][0]+nx*w, center[k][1]+ny*w)); right.append((center[k][0]-nx*w, center[k][1]-ny*w))
    return smooth(left + right[::-1], tension=tension)
def bump(cx, cy, w, h, c=YEL):   # runder Stachel
    return group(smooth([(cx-w/2, cy), (cx, cy-h), (cx+w/2, cy)], tension=0.7), fill(c))
def mirror(pts): return [(-x, y) for x, y in pts]


# ---------- Vorlage -> Leinwand ----------
# Alle Masse unten sind Pixel in pro_vorne.png (2048 x 2048): x waechst nach
# rechts, y nach unten, die Figur steht auf x = 1024, die Zehen enden bei
# y = 1870. K ist der Massstab auf die Leinwand: so passt die Figur mit
# Fluegeln (Vorlage 68..1981 breit) in 520 Punkte Breite, und oben bleibt
# Luft fuer den groesseren Kopf der Variante A und die Spruenge (bei 0.245
# schnitt der Jubelsprung die Hornspitzen am oberen Rand ab).
K = 0.235
BODEN = 474                       # Leinwand-y der Fusssohlen
RUMPF = (260, 345)                # Ursprung der Koerper-Ebene auf der Leinwand
def V(x, y):
    """Vorlagenpunkt -> Koerper-Ebene (Leinwandpunkte, Ursprung Rumpfmitte).
    Alle Ebenen am Koerper (Arme, Beine, Fluegel, Schwanz) rechnen in denselben
    Koordinaten; ihr Drehpunkt steht als Anker UND Position darin."""
    return (round((x - 1024) * K, 2), round((y - 1870) * K + BODEN - RUMPF[1], 2))
def VL(pts): return [V(x, y) for x, y in pts]
def SP(pts): return [(2048 - x, y) for x, y in pts]          # an der Mittelachse spiegeln
def SYM(links):
    """Linke Haelfte eines Umrisses (oben Mitte -> unten Mitte) zu einem
    geschlossenen, symmetrischen Umriss ergaenzen."""
    return links + SP(links[-2:0:-1])
# Der Kopf rechnet in eigenen Einheiten: so breit wie der Kopf von v5 (156),
# Scheitel bei y = -128. Darum sitzen die Kostueme, die fuer v5 gebaut
# wurden, wenigstens ungefaehr - und wachsen mit, wenn der Kopf waechst.
U = 0.3824
def Hk(x, y): return (round((x - 1024) * U, 2), round((y - 398) * U - 128, 2))
def HL(pts): return [Hk(x, y) for x, y in pts]
LW = round(14 * K, 2)             # Umriss am Koerper: 14 px in der Vorlage
LWK = round(14 * U, 2)            # derselbe Umriss im Kopf
HALS = (1024, 820)                # um diesen Punkt dreht und waechst der Kopf


def form(pts, f, s=BLUE_D, w=LW, t=0.5, o=100, so=100):
    """Flaeche mit Umriss (Umriss liegt oben)."""
    return group(smooth(pts, tension=t), stroke(s, w, so), fill(f, o))
def flaeche(pts, f, o=100, t=0.5): return group(smooth(pts, tension=t), fill(f, o))
def linie(pts, c=BLUE_D, w=LW, o=100, t=0.5): return group(smooth(pts, closed=False, tension=t), stroke(c, w, o))
# Mehrere Pfade gleicher Farbe in EINER Gruppe: jede Gruppe kostet in der
# Datei rund 100 Zeichen fuer ihre Transformation. Ueberlappende Flaechen
# werden dabei vereinigt statt doppelt abgedunkelt.
def flaechen(liste, f, o=100, t=0.5): return group(*[smooth(p, tension=t) for p in liste], fill(f, o))
def linien(liste, c=BLUE_D, w=LW, o=100, t=0.5): return group(*[smooth(p, closed=False, tension=t) for p in liste], stroke(c, w, o))
def paarweise(links, rechts):
    """Gleich gebaute Formen fuer links und rechts paarweise in EINE Gruppe:
    zwei Pfade, eine Farbe. Die beiden Seiten ueberlappen sich nie, also
    sieht es genauso aus - und die Datei wird deutlich kleiner."""
    aus = []
    for a, b in zip(links, rechts):
        pa = [i for i in a["it"] if i["ty"] in ("sh", "el", "rc")]
        pb = [i for i in b["it"] if i["ty"] in ("sh", "el", "rc")]
        ra = [i for i in a["it"] if i["ty"] not in ("sh", "el", "rc")]
        rb = [i for i in b["it"] if i["ty"] not in ("sh", "el", "rc")]
        if ra == rb and all(i["ty"] in ("fl", "st", "tr") for i in ra):
            aus.append({"ty": "gr", "it": pa + pb + ra})
        else:
            aus += [a, b]
    return aus
def kreis(c, d, f, s=None, w=LW):
    return group(ellipse(c[0], c[1], d, d), *( [stroke(s, w)] if s else []), fill(f))
def ellipse_pfad(cx, cy, w, h):
    """Ellipse als Pfad (fuer Masken)."""
    k = 0.5523; rx, ry = w / 2, h / 2
    return {"c": True, "v": [[cx, cy - ry], [cx + rx, cy], [cx, cy + ry], [cx - rx, cy]],
            "i": [[-rx * k, 0], [0, -ry * k], [rx * k, 0], [0, ry * k]],
            "o": [[rx * k, 0], [0, ry * k], [-rx * k, 0], [0, -ry * k]]}

# Zierrat aus dem Laden, in drei Gruppen - so wie die Reiter im Laden. Aus
# jeder Gruppe kann ein Stück getragen werden, alle drei zusammen.
#
# Wo eine Gruppe in ORDER steht, entscheidet, was was verdeckt:
#   Kopf und Brille liegen ganz vorn, über Augen, Hörnern und allem anderen.
#   Die Halssachen stehen HINTER dem Kopf und hinter den Armen, aber vor dem
#   Körper. Dadurch schiebt sich der Kopf über den oberen Rand des Schals,
#   genau wie bei einem echten Schal, und die Arme liegen auf der Weste.
KOPF_TEILE = ["hut", "krone", "krone_gross", "fes", "kappe", "doktorhut", "ohrenschuetzer", "kopfhoerer",
              # Festtage, Entwurf vom 01.10.2026 - siehe unten bei "Festtage"
              "hexenhut", "nikolausmuetze", "bajramfes", "hasenohren"]
BRILLEN    = ["brille", "sonnenbrille", "lesebrille", "monokel"]
HALS_TEILE = ["trikot", "umhang", "schal_bih", "schal_winter", "weste_leder", "weste_strick",
              "jelek"]   # Festtage: Bajram, Entwurf vom 01.10.2026
# Zwei Ebenen, die zur Haut gehoeren statt zur Kleidung: die Sterne der
# Galaxie-Haut liegen direkt auf dem Koerper, das Funkeln davor. Beide
# gibt es nur mit der Vollversion.
HAUT_TEILE = ["funkeln", "galaxie", "skelett"]   # skelett: Halloween, Entwurf vom 01.10.2026
ZIERRAT = KOPF_TEILE + BRILLEN + HALS_TEILE + HAUT_TEILE
# Die drei Kleidungsstuecke bekommen Aermel. Das sind eigene Ebenen, denn sie
# haengen an den Armen und nicht am Koerper - die Arme wippen, ein am Koerper
# festgemachter Aermel bliebe stehen. Sie stehen in ORDER vor "armL", liegen
# also VOR den Armen und decken sie zu.
AERMEL_STUECKE = ["trikot", "weste_leder", "weste_strick"]
AERMEL = [s + "_" + a for s in AERMEL_STUECKE for a in ("armL", "armR")]
# v6, 15.10.2026: Der Arm hat einen Ellbogen. Die beiden Jacken haben lange
# Aermel und brauchen darum auch am Unterarm einen - als eigene Ebene, die
# am Unterarm haengt und VOR ihm liegt (der Unterarm liegt vor dem Gesicht).
LANGE_AERMEL = ["weste_leder", "weste_strick"]
UNTERAERMEL = {a: [s + "_unterarm" + a for s in LANGE_AERMEL] for a in ("L", "R")}
# Ebenen, die nur zusammen mit einem Stueck ausgeliefert werden. Der
# Schriftzug auf dem Fanschal ist die erste davon: er muss VOR dem Stoff
# liegen, ist aber eine eigene Ebene, weil Lottie Text nicht als Form kennt.
NUR_MIT = {"schal_bih": ["schal_bih_text"]}
# Das Skelett braucht Ebenen an Kopf, Armen, Fluegeln und Schwanz: jede
# haengt an ihrem Koerperteil und bewegt sich mit ihm. Seit v6 hat der Arm
# ein Gelenk - der Unterarm ist eine eigene Ebene und bekommt eigene Knochen.
SKELETT_EBENEN = ["skelett_augen", "skelett_kopf", "skelett_zaehne", "skelett_armL", "skelett_armR",
                  "skelett_unterarmL", "skelett_unterarmR",
                  "skelett_wingL", "skelett_wingR", "skelett_schwanz"]
NUR_MIT["skelett"] = SKELETT_EBENEN
NUR_MIT.update({s: [s + "_armL", s + "_armR"] for s in AERMEL_STUECKE})
for _s in LANGE_AERMEL:
    NUR_MIT[_s] += [_s + "_unterarmL", _s + "_unterarmR"]
# v6: Der Hermelinkragen des Koenigsmantels liegt VOR den Armen, der Mantel
# dahinter - zwei Ebenen. Die Galaxie-Haut hat Sterne auch auf Fluegeln und
# Schwanz; die bewegen sich, also haengen die Sterne dort an ihnen.
NUR_MIT["umhang"] = ["umhang_kragen"]
NUR_MIT["galaxie"] = ["galaxie_wingL", "galaxie_wingR", "galaxie_schwanz"]

# ======================= Bild-Drache (v7) =======================
# 15.10.2026, Ajdin nach den Vorschauen: die Bildteile aus Google Gemini
# sehen "viel besser" aus als der gezeichnete Drache. Seitdem besteht der
# Drache in der App aus Bildern, die am Rig der Variante B haengen: dieselben
# Ebenen, Drehpunkte, Keyframes und Marker wie bisher, nur ohne Formen. Jedes
# Teil ist eine Bild-Ebene (Lottie ty 2) mit der Rig-Ebene als Eltern.
# Das Gesicht wechselt mit dem Kopfbild: je Stimmung ein ganzer Kopf (mit
# Hoernern), dazu die Hornspitzen als eigenes Bild fuer die Ebene "hoerner"
# vor den Hueten. Augen, Lider, Brauen, Muender und Traenen gibt es als
# Vektor nur noch fuer das Skelett (siehe dort).
#   teil: (Rig-Ebene, Breite, Hoehe, Drehpunkt x, y im Bild, sichtbar)
# Die Bilder haben 2 Pixel je Leinwand-Einheit (PX_JE_EINHEIT), Kopf und
# Hornspitzen bei Kopf 1.0. Der Drehpunkt liegt genau auf dem Anker der
# Rig-Ebene. Die Zahlen stammen aus teile.json des Teilesatzes (15.10.2026);
# dort steht auch, aus welchem Gemini-Bogen, Kasten und welcher Maske jedes
# Teil geschnitten ist. Die Quellen (Gemini-Boegen, PNG-Teile, Masken,
# Hautboegen, teile.json und die Schneidewerkzeuge) liegen seit dem
# 15.10.2026 ausserhalb des Repos, aber nicht mehr im Temp-Ordner:
# App Zeugs\Profilbild\Drache_Bildteile\ (LIESMICH.txt dort). Eine Kopie
# von teile.json steht im Repo unter grafik/drache/teile.json.
# Die Dateien liegen als <teil>.webp in web/maskottchen/teile/, je
# Hautfarbe dieselben Namen in haut/<farbe>/ (haut_einbauen.py).
# sichtbar: None = immer; "kopf" = Kopf- und Hornbilder, sie folgen
# dem Kopfplan (KOPFPLAN) unten; sonst Stimmungen aus SEG, dazu "cheer_hoch" (die
# Bilder des Jubels mit erhobenen Armen, JUBEL_HOCH) und "cheer_ruhe" (die
# uebrigen Jubelbilder, Arme unten).
PX_JE_EINHEIT = 2.0
BILD_TEILE = {
    "body":             ("body",      328, 575, 163.0, 569.0, None),
    "wingL":            ("wingL",     415, 381, 384.32, 245.9, None),
    "wingR":            ("wingR",     416, 381, 30.68, 245.9, None),
    "tail":             ("tail",      372, 270, 90.32, 212.6, None),
    # Der Oberarm endet oben weich: haengend geht er so in die Schulter ueber.
    # Erhoben (Jubel, Weinen) lag das weiche Ende frei ueber dem Fluegel und
    # sah aus wie ein verwaschener Stummel (Pruefung 15.10.2026). Dafuer gibt
    # es "_hoch": dasselbe Bild, die Innenseite oben mit Umriss und oben eine
    # runde Kappe mit Umriss (werkzeuge\teile_richten.py in den Quellen).
    # Erhoben rueckt die Schulter dazu ein Stueck zur Mitte (ARM_RUECK).
    "oberarmL":         ("armL",      104, 146, 68.58, 28.8, ("idle", "sad", "ok", "no", "no_l", "no_r", "cheer_ruhe")),
    "oberarmR":         ("armR",      104, 147, 35.42, 29.8, ("idle", "sad", "ok", "no", "no_l", "no_r", "cheer_ruhe")),
    "oberarmL_hoch":    ("armL",      104, 146, 68.58, 28.8, ("cheer_hoch", "cry")),
    "oberarmR_hoch":    ("armR",      104, 147, 35.42, 29.8, ("cheer_hoch", "cry")),
    "unterarmL_offen":  ("unterarmL",  92, 167, 60.86, 24.4, ("idle", "sad", "ok", "no", "no_l", "no_r", "cheer_ruhe")),
    "unterarmR_offen":  ("unterarmR",  92, 167, 30.14, 24.4, ("idle", "sad", "ok", "no", "no_l", "no_r", "cheer_ruhe")),
    # Faust und Hand an der Wange sind in die Ruhelage zurueckgerechnet: in
    # der Jubel- bzw. Weinpose des Rigs liegen sie so, wie Gemini sie zeichnete.
    # Die Faust nur, solange die Arme oben sind: bis 15.10.2026 stand sie im
    # ganzen Jubel, und am Ende sprang die haengende Faust zur offenen Hand.
    "unterarmL_faust":  ("unterarmL",  83, 145, 54.86, 21.4, ("cheer_hoch",)),
    "unterarmR_faust":  ("unterarmR",  83, 145, 28.14, 21.4, ("cheer_hoch",)),
    # Seit 16.10.2026 ist das Feld der Hand an der Wange 114 x 220 statt
    # 88 x 151: das gemalte Skelett (haut/skelett/) haelt sich beim Weinen
    # die Knochenhaende vor die Augenhoehlen, seine Finger reichen weiter.
    # Alle Saetze teilen sich ein Asset; die kleineren Bilder der anderen
    # Saetze erweitert haut_einbauen.py durchsichtig (FELD dort) - rechts um
    # 26 Pixel nach links, darum dort der Drehpunkt 55.14 statt 29.14.
    "unterarmL_wange":  ("unterarmL", 114, 220, 58.86, 23.4, ("cry",)),
    "unterarmR_wange":  ("unterarmR", 114, 220, 55.14, 23.4, ("cry",)),
    "kopf_blinzeln":    ("head",      245, 306, 122.0, 295.5, "kopf"),
    "kopf_jubel":       ("head",      244, 322, 122.0, 295.5, "kopf"),
    "kopf_froh":        ("head",      245, 324, 122.0, 295.5, "kopf"),
    "kopf_traurig":     ("head",      249, 310, 124.0, 298.5, "kopf"),
    "kopf_weinen":      ("head",      249, 319, 124.0, 299.5, "kopf"),
    "kopf_finster":     ("head",      249, 310, 124.0, 299.5, "kopf"),
    # Der rechte Kopf ist der linke, gespiegelt (Licht dann von rechts).
    "kopf_links":       ("head",      250, 303, 117.0, 291.5, "kopf"),
    "kopf_rechts":      ("head",      250, 303, 133.0, 291.5, "kopf"),
    "kopf_neutral":     ("head",      245, 307, 122.0, 295.5, "kopf"),
    "hoerner_blinzeln": ("hoerner",   244,  72, 121.0, 295.5, "kopf"),
    "hoerner_jubel":    ("hoerner",   244,  73, 122.0, 295.5, "kopf"),
    "hoerner_froh":     ("hoerner",   244,  73, 122.0, 295.5, "kopf"),
    "hoerner_traurig":  ("hoerner",   249,  75, 124.0, 298.5, "kopf"),
    "hoerner_weinen":   ("hoerner",   249,  76, 124.0, 299.5, "kopf"),
    "hoerner_finster":  ("hoerner",   249,  76, 124.0, 299.5, "kopf"),
    "hoerner_links":    ("hoerner",   190,  69, 57.0, 291.5, "kopf"),
    "hoerner_rechts":   ("hoerner",   190,  69, 133.0, 291.5, "kopf"),
    "hoerner_neutral":  ("hoerner",   245,  72, 122.0, 295.5, "kopf"),
}
# Die Rig-Ebenen, deren Formen die Bilder ersetzen. "legs" hat kein eigenes
# Bild: Unterschenkel und Fuesse stehen still am Koerper und sind in body.
BILD_EBENEN = sorted({v[0] for v in BILD_TEILE.values()} | {"legs"})
# Zwei Blinzler in der Ruhe, wie die Lider des Vektor-Drachen (geschlossen
# bei 31 und 65): je vier Bilder, eine gute Zehntelsekunde.
BLINZELN = [(30, 34), (64, 68)]
# Die Gesichtsebenen des Vektor-Drachen. Im Bild-Drachen sind sie im Kopfbild.
GESICHT = ["eyes", "lids", "eyes_happy", "eyes_cry", "brows", "mouth_idle", "mouth_open", "mouth_sad", "mouth_cry", "tears"]
# Welcher Hautsatz ein Stueck ueberfluessig macht: die App laesst jede Ebene
# mit "zmaj_ohne_haut": <farbe> weg, wenn sie den Hautsatz haut/<farbe>/
# laedt.
# Bis 15.10.2026 stand hier schon einmal {"skelett": "skelett"}: der
# damalige Bildsatz haut/skelett/ zeigte statt der Knochen einen
# elfenbeinfarbenen Drachen mit Fleisch, Bauchschuppen und blauen Augen mit
# Iris. Das widerspricht der Fest-Entscheidung vom 01.10.2026 (Skelett =
# nur Knochen wie Knochentrocken, runde schwarze Hoehlen mit gelbem Punkt,
# kein Fleisch, ausdruecklich keine Augen mit Iris); der Satz flog raus
# (Quellen: Drache_Bildteile\haut_skelett_verworfen), und einen Tag lang
# war das Skelett immer das Vektor-Skelett.
# 16.10.2026: Gemini hat das Skelett auf den Original-Boegen neu GEMALT -
# nur Knochen, die Schaedel in der Form des Originalkopfs mit runden
# schwarzen Hoehlen und gelbem Punkt, ohne Iris, Schwanz nur Wirbel, und
# nach Ajdins Wunsch vom 15.10.2026 durchgehend boese, mit Nasenbein-Linie
# und schmalen Nasenoeffnungen statt "Schweinsnase", das Becken auf den
# Oberschenkeln, Krallenknochen statt "komischer" Finger. Es hat dieselben
# 32 Teile mit denselben Drehpunkten (bis auf die Haende an der Wange,
# siehe BILD_TEILE) und haengt darum am selben Rig: dieselbe Bewegung wie
# der normale Drache, auch beim Kopfschuetteln, und die Brauen sind Teil
# jedes Kopfbilds, drehen also mit. Damit ist es wieder der Hautsatz
# haut/skelett/ (Quellen: Drache_Bildteile\fertig\haut\skelett), und das
# Vektor-Skelett weicht ihm. Fehlt der Satz in der App, bleibt das
# Vektor-Skelett der Rueckfall: zmaj_leert nimmt die Bild-Ebenen heraus, und
# das Stueck bringt das Vektor-Gesicht mit - wie mit --vektor.
# Nachpruefung 16.10.2026: Gemini hatte die Nasenbein-Linie gemalt, die
# Nasenloecher blieben aber runde Tropfen; sie sind im Bildsatz jetzt
# schmale, kantige Oeffnungen (Drache_Bildteile\werkzeuge\befunde_16_10\
# nase_kantig.py). Dort auch weg: ein loser Dorn und gerade Schnittkanten
# ohne Umriss am Schwanz, Halsreste unter dem Kinn des Jubelkopfs.
# Korrektur 16.10.2026 nach Ajdins Rueckmeldung ("zu dicke Halswirbel; beim
# Schwanz fehlt ein Schwanzwirbel, der ist abgeschnitten; die Schultern
# gucken zu sehr raus"): Lendenwirbel zwischen Brustkorb und Becken auf 68 %
# Breite und das Brustbein unter dem Kinn schmaler (der Hals selbst liegt in
# jeder Stimmung hinter dem Kopf), die zwei oben abgeschnittenen Wirbel am
# Schwanzansatz durch ganze Wirbel ersetzt, und die Oberarmkoepfe ruecken
# 15 Bildpixel zum Rumpf (Knochen um den Ellbogen gedreht, Drehpunkte und
# Bildgroessen unveraendert). Werkzeug: Drache_Bildteile\werkzeuge\
# befunde_16_10\korrektur_1610.py (alter Stand daneben in vor_korrektur_1610).
# Nachpruefung 16.10.2026: Zwischen Becken und erstem Schwanzwirbel blieb
# eine Luecke - der Schwanz schwebte frei zwischen den Beinen (beim Drachen
# mit Haut liegt dort der Koerper davor, beim Skelett sieht man durch). Das
# ist der fehlende Wirbel: tail hat jetzt einen Wirbel mehr am Ansatz, in
# der Kruemmung weitergefuehrt, hinter dem ersten und oben hinter dem Becken
# (Ebene "tail" liegt hinter "body") - der Schwanz haengt am Becken.
# Bildgroesse bleibt. Werkzeug: befunde_16_10\skelett_wirbel.py.
# Zweite Korrektur 16.10.2026 nach Ajdins Rueckmeldung ("immer noch breite
# Halswirbel, die muessen duenner sein wie die Schwanzwirbel; die Schultern
# sind nicht im Schluesselbein; unter der Schulter sieht etwas aus wie ein
# Beckenknochen"): Gemini hatte Brustkorb, Schluesselbeine und Schulterknaufe
# an den langen Hals des blauen Drachen gemalt, die Arme haengen im Rig aber
# viel tiefer (SCHULTER). Unter dem Kiefer sah man darum die oberen Rippen
# (wie breite Halswirbel), die Arme setzten an den unteren Rippen an, und
# deren nach aussen gebogene Enden wirkten unter der Schulter wie ein
# Beckenkamm. Der Oberkoerper in body ist neu: schlanke Halswirbel (schmaler
# als die Schwanzwirbel) bis zum Brustbein, Schluesselbeine leicht abfallend
# bis zu den Schultergelenken genau am Oberarmkopf, kleine Schulterblatt-
# spitzen, darunter ein kurzer, breiter Brustkorb mit drei Rippenpaaren
# (mehr passen zwischen Schulter und Becken nicht), schlanke Lende bis ins
# Becken; Becken, Beine und Fuesse unveraendert. Gezeichnet und von Gemini
# im Nahausschnitt an Ort und Stelle nachgemalt (befunde_16_10\rumpf_neu.py);
# vor dem schlanken Hals standen an jedem Schaedel unter den Kieferecken
# Halsstriche frei in der Luft - weg (befunde_16_10\kinn_reste.py).
# Bildgroessen und Drehpunkte bleiben, das Rig ist unveraendert. Damit sind
# die Saetze oben vom schmaleren Brustbein unter dem Kinn und vom Hals, der
# hinter dem Kopf liegt, ueberholt: der Hals ist jetzt eine duenne Wirbel-
# kette und unter dem Kinn zu sehen.
# Nachpruefung 16.10.2026 nachmittags: Dadurch lag das Kinn frei, und die
# Schaedelbilder endeten unten mit einer geraden Kante ohne Umriss - unter
# dem dunklen U des Unterkiefers hing ein Stummel vom alten Hals (beige, mit
# senkrechten Strichen), beim Jubel war das U selbst abgeschnitten. Jetzt
# endet jeder Schaedel am U: darunter durchsichtig, wo das U fehlte, ist es
# rund geschlossen und der Umriss nachgezogen (Bildgroessen bleiben).
# Werkzeug: befunde_16_10\korrektur4\kinn4.py.
# Dritte Korrektur 16.10.2026 nachmittags nach Ajdins Rueckmeldung ("die
# Halswirbel sind jetzt viel zu duenn, mach sie etwas dicker"): Die
# schlanke Wirbelkette war schmaler als die Lendenwirbel und wirkte unter
# dem grossen Schaedel wie ein Faden. Die Halskette in body ist jetzt
# gleichmaessig 1,5-fach vergroessert - um den Punkt, an dem der unterste
# Wirbel auf dem Schluesselbein sitzt; Form und Umriss der gemalten Wirbel
# bleiben, sie sind nur kraeftiger (so breit wie die Lendenwirbel, deutlich
# schmaler als die alten Rippenbaender), und der Hals geht hinter dem
# Schluesselbein hinab. Damit ist "schlanke Halswirbel (schmaler als die
# Schwanzwirbel)" oben ueberholt. Alles andere in body bleibt Pixel fuer
# Pixel, Bildgroesse und Drehpunkt auch. Werkzeug: befunde_16_10\
# korrektur5_hals\hals_dicker.py (Stand davor in vor_korrektur5_hals).
HAUT_ERSETZT = {"skelett": "skelett"}
# Ebenen, die der Bild-Drache gar nicht ausliefert. "eyes" (Augenweiss mit
# blauer Iris) blieb bis 15.10.2026 in der Grunddatei stehen und lag mit
# offenen Vektor-Augen ueber jedem Kopfbild - das Blinzeln war unsichtbar,
# die traurigen und finsteren Augen zugedeckt, und am abgewandten Kopf sah
# man vier Augen (Pruefung 15.10.2026). Das Skelett braucht sie auch nicht:
# seine Augenhoehlen (skelett_augen) sind eigene, groessere Formen, und die
# Iris lugte beim Wegschauen (no_l/no_r) blau unter ihnen hervor.
WEG_IM_BILD = [] if VEKTOR else ["eyes"]
if not VEKTOR:
    NUR_MIT["skelett"] = SKELETT_EBENEN + [g for g in GESICHT if g not in WEG_IM_BILD]
ZIERRAT_ALLE = ZIERRAT + [n for v in NUR_MIT.values() for n in v]

# ======================= Gemalte Kostueme (v7, 16.10.2026) =======================
# Ajdin am 15.10.2026 nach der Seite mit allen Kostuemen: die Huete besser
# machen (Kappe, Fes, Muetze, am meisten Doktorhut, Krone und grosse Krone -
# "die grosse Krone sah vorher doch ganz anders aus"), Nikolausmuetze,
# Bajram-Fes und Jelek "sehen noch nicht gut aus", der Schal ist "viel zu
# starr, als waere das nicht aus Stoff", und an Trikot, Strick- und
# Lederjacke und am Koenigsmantel "sind die Oberarme viel zu sehr betont, als
# waere die Schulter nicht mehr am Torso dran". Diese 15 Stuecke hat Gemini
# darum im Stil des Drachen GEMALT (dunkelblauer Umriss, weiche
# Zellschattierung, Stoff mit Falten, Metall mit Glanz), direkt auf den
# gemalten Drachen: die Huete auf Frontkopf und abgewandtem Kopf zugleich,
# die Kleidung am stehenden Drachen und - fuer die erhobenen Arme - auf den
# Teilebogen. Ausgeschnitten wurde mit denselben Kaesten, Masken und
# Matrizen wie die Teile des Drachen; jedes Bild liegt also genau auf
# seinem Teil. Brillen, Ohrenschuetzer, Kopfhoerer, Hexenhut, Hasenohren,
# Funkeln und Galaxie blieben vorerst Vektor (Entscheidung 15.10.2026) -
# bis auf die Galaxie sind sie seit 16.10.2026 auch gemalt (siehe unten).
# Quellen: Drache_Bildteile\fertig\zierrat\ (PNG, so wie haut_einbauen.py
# --zierrat sie umwandelt), Lage, Herkunft und Kontrollboegen in
# Drache_Bildteile\kostueme_quellen\ (die Zahlen unten stammen aus den
# anker.json dort).
# Jedes Stueck ist eine Liste von Bild-Ebenen (ty 2) wie die des Drachen:
#   web/maskottchen/zierrat/<stueck>/<teil>.webp, im Schnipsel als Asset
#   "<stueck>_<teil>" mit u = "zierrat/<stueck>/" (relativ zu zmaj.json),
#   Ebene "bild_<stueck>_<teil>" mit der Rig-Ebene als Eltern, 2 Pixel je
#   Leinwand-Einheit (am Kopf wie die Kopfbilder umgerechnet).
# Sie ersetzen die Vektor-Ebene des Stuecks und stehen in ORDER genau an
# ihrer Stelle ("vor": die Bild-Ebene liegt direkt vor dieser Ebene) - so
# bleibt die Tiefe, die oben bei KOPF_TEILE/HALS_TEILE begruendet ist.
# Einzige Ausnahme ist der Mantel (siehe GEMALTE_RUMPFSTUECKE).
#
# Kopfstuecke: je eine Fassung fuer den Kopf von vorn (alle Frontkoepfe)
# und fuer den abgewandten Kopf; welche zu sehen ist, sagt der Kopfplan
# (kopf_deckkraft(seite=...)) - beim Kopfschuetteln springt der Hut im
# selben Bild wie der Kopf. "rechts" ist "links" gespiegelt, wie kopf_rechts
# der gespiegelte kopf_links ist (mittlere Abweichung 3/255); die Datei
# rechts.webp ist schon gespiegelt, ihr Drehpunkt also Breite - x.
#   stueck: ((vorne: Breite, Hoehe, Drehpunkt x, y), (links: ...)) in
#   Pixeln; der Drehpunkt liegt auf dem Anker der Kopf-Ebene.
# Gemini setzte Kappe, Muetze, Bajram-Fes, Doktorhut und grosse Krone etwas
# zu tief; ihre Frontfassungen sitzen 2 bis 7 Kopf-Einheiten hoeher als
# gemalt, damit die Brauen auch beim Jubel frei bleiben (Drehpunkt schon
# darum verschoben). Wo Gemini ein Horn VOR den Hut gemalt hat, hat das
# Bild ein Loch und das Horn des Kopfbilds schaut durch. Die Hornspitzen
# (bild_hoerner_*, vor den Vektor-Hueten) leert ein gemalter Hut darum mit
# zmaj_leert: am abgewandten Kopf lag sonst das FERNE Horn vor Muetze,
# grosser Krone und Nikolausmuetze, und vorn stach das rechte Horn durch
# die Nikolausmuetze (Pruefung 16.10.2026).
# Nachpruefung 16.10.2026: Die grosse Krone verdeckte vorn beide Hoerner,
# am abgewandten Kopf stand das nahe Horn davor, und mit sieben
# Perlenzacken, Samt und geschliffenem Rubin hatte sie nichts vom alten
# Entwurf ("die grosse Krone sah vorher doch ganz anders aus"). Sie ist
# neu gemalt nach dem Entwurf auf master (breiter Reif, vier Zacken, zwei
# Perlen, aussen zwei rote Steine, ein grosser runder Stein); Gemini bekam
# dafuer eine flache Skizze an der richtigen Stelle, frei gemalt schwebte
# die Krone ueber den Hoernern. Bei ihr und bei der Nikolausmuetze (vorn
# ragte nur ein Horn heraus) stehen jetzt in BEIDEN Ansichten beide Hoerner
# ganz vor dem Stueck, und der Kopfstachel liegt unter dem Fellrand der
# Muetze, statt ihn zu durchstechen.
# Korrektur 16.10.2026 (Ajdin: "Die grosse Krone sieht sehr komisch auf dem
# Kopf aus"): Gemini hatte die Skizze nicht eingehalten - die Krone war fast
# so hoch wie der Kopf, ihr Reif schwebte auf Hoehe der Hoerner ueber dem
# Schaedel (die goldenen Hoerner standen wie Zierrat IN der Krone), die
# Seitensteine sassen auf langen Stielen, und am abgewandten Kopf stand sie
# frontal. Jetzt hat Gemini die Krone frei gemalt (von vorn und dreiviertel
# gedreht, Entwurf wie oben: breit und niedrig, vier kurze Zacken, Perlen und
# Steine direkt auf den Spitzen), und Groesse und Sitz sind gesetzt statt
# gemalt: 168 Kopf-Einheiten breit, der Reif sitzt mit der Unterkante bei
# -104 auf dem Schaedel (Brauen frei), am abgewandten Kopf 10 Einheiten zum
# Hinterkopf; die Hoerner stehen ganz davor (Loch im Kronenbild, wo das
# Kopfbild Horn ist). Werkzeug: kostueme2\korrektur\werk\krone.py.
# Dritte Fassung (16.10.2026 mittags, "Hoerner innen" oder "laessig am Horn"):
# siehe KRONE_GROSS unten.
#
# Die restlichen neun (16.10.2026, Ajdin nach dem Vergleich gemalt gegen
# gezeichnet: "mal auch die restlichen"): Brille, Sonnenbrille, Lesebrille,
# Monokel, Ohrenschuetzer, Kopfhoerer, Hexenhut, Hasenohren und Funkeln.
# Gemalt wie die Huete auf Frontkopf und kopf_links; Lage und Herkunft in
# Drache_Bildteile\kostueme_quellen\rest_anker.json (Kontrollbogen
# rest_bogen.png daneben). Sie stehen unten in GEMALTE_HUETE, mit drei
# Besonderheiten:
# - Brillen: Gemini malt das Auge hinter dem Glas mit. Die Glaeser sind
#   darum ersetzt durch eine leichte Toenung (24 % deckend) mit Geminis
#   Glanzlichtern - durch das Glas sieht man das Auge des jeweiligen
#   Kopfbilds, also auch Blinzeln, Jubel- und Weinaugen. Die Sonnenbrille
#   ist ganz deckend. Die Brillen lassen die Hornspitzen stehen
#   (HORNSPITZEN_BLEIBEN): sie beruehren die Hoerner nicht. BRILLE_GEDREHT
#   (Verschieben und Stauchen der Vektor-Brille am abgewandten Kopf) faellt
#   fuer sie weg - die Seitenbilder sind fuer kopf_links gemalt.
# - Monokel: es sitzt immer auf demselben Auge des Drachen. Gespiegelt
#   sprang es beim Kopfschuetteln von einem Auge aufs andere; rechts ist
#   darum ein eigenes Bild (EIGENES_RECHTS), gemalt auf dem gespiegelten
#   abgewandten Kopf.
# - Hexenhut und Hasenohren: frei gemalt reichten sie bis -314 bzw. -300
#   Kopf-Einheiten, im Jubelsprung schneidet die Leinwand aber ab etwa -278
#   ab. Gemini bekam darum eine flache Skizze an der richtigen Stelle; jetzt
#   endet der Hut bei -217, die Ohren bei -234 (vorn) bzw. -239.
# Die Funkelsterne stehen in GEMALTE_FUNKEN.
GEMALTE_HUETE = {
    "kappe":          ((195, 121,  97.09, 280.12), (198, 134,  80.56, 269.1)),
    "fes":            ((151, 144,  74.63, 333.1),  (165, 165,  55.98, 314.02)),
    "hut":            ((215, 226, 106.84, 379.29), (211, 212,  87.76, 353.86)),
    "doktorhut":      ((335, 185, 166.59, 326.74), (304, 206, 119.55, 320.81)),
    "krone":          ((132, 116,  65.3,  288.6),  (123, 106,  58.94, 283.51)),
    "krone_gross":    None,      # Form nach KRONE_GROSS, siehe unten
    "nikolausmuetze": ((293, 239, 110.23, 311.48), (264, 245,  77.59, 292.41)),
    "bajramfes":      ((151, 173,  74.2,  333.52), (157, 176,  64.88, 323.77)),
    "ohrenschuetzer": ((348, 218, 173.38, 272.07), (314, 231, 140.32, 276.3)),
    "kopfhoerer":     ((362, 296, 180.58, 341.57), (336, 302, 149.64, 339.45)),
    "hexenhut":       ((278, 153, 138.62, 310.63), (278, 153, 124.21, 310.63)),
    "hasenohren":     ((186, 182,  92.85, 331.83), (198, 188, 119.55, 337.34)),
    "brille":         ((208,  89, 103.45, 155.52), (235,  93, 123.37, 152.13)),
    "sonnenbrille":   ((203,  77, 100.48, 148.73), (192,  81, 119.55, 144.92)),
    "lesebrille":     ((181,  60,  89.88, 127.54), (180,  70, 120.4,  127.54)),
    "monokel":        (( 91, 140, -10.56, 152.55), ( 93, 132,  40.3,  144.07)),
}
# Stuecke mit eigenem Bild fuer kopf_rechts statt des gespiegelten linken.
EIGENES_RECHTS = {"monokel": (54, 76, -55.06, 149.58)}
# Grosse Krone, dritte Fassung (16.10.2026 mittags). Ajdin zur Krone von
# heute morgen (sie sass zwischen den Hoernern, die Hoerner davor): "mach doch
# bei der Krone, dass die Hoerner innen sind und die Krone aussen, oder so
# laessig, die Krone haengt so seitlich ab und haengt an einem Horn". Gemini
# hat beides gemalt, auf den Koepfen und nach einer Skizze an der richtigen
# Stelle (dieselbe Krone wie bisher: vier Zacken, zwei Perlen, zwei rote
# Steine, grosser runder Stein):
#   "laessig"  (B, Standard - Ajdin hat es ausfuehrlicher beschrieben): die
#              Krone sitzt schraeg und haengt seitlich am linken Horn des
#              Drachen (vorn rechts im Bild). Das Horn sticht innen durch die
#              Kronenoeffnung: unten liegt der Reif davor, darueber steht das
#              Horn vor der Rueckwand (Loch im Kronenbild, das Horn des
#              Kopfbilds schaut durch). Es ist in allen Ansichten DASSELBE
#              Horn - am nach rechts gedrehten Kopf das ferne, darum hat
#              rechts ein eigenes Bild (EIGENES_RECHTS); gespiegelt sprang die
#              Krone beim Kopfschuetteln von Horn zu Horn (Gemini hatte sie
#              im ersten Versuch dort auch ans nahe Horn gehaengt).
#              Nachpruefung 16.10.2026 nachmittags: Geminis zweites rechts-
#              Bild stand aufrecht hinter dem Kopf auf einem gemalten goldenen
#              Hornstreifen wie auf einem Stiel, unten fehlte ein Stueck Reif.
#              Rechts ist jetzt die Frontkrone selbst, an das ferne Horn
#              gelegt (41 Einheiten zur Mitte, in der Breite auf 92 %
#              gestaucht): das Horn geht durch die Luecke ueber dem Reif, die
#              Spitze ragt oben heraus, das nahe Horn steht davor
#              (befunde_16_10\korrektur4\krone4.py).
#              Korrektur 16.10.2026 nachmittags (Ajdin zum Kontrollbogen: "bei
#              Krone Kopf links muss das anders aussehen, sieht komisch aus
#              ... nimm die Krone auf einem Horn"): so sass die Krone mittig
#              oben auf dem Schaedel und deckte das ferne Horn bis auf die
#              Spitze zu - wie eine normale Krone, nicht am Horn. Geprueft im
#              Kopfschuetteln: (a) dasselbe Horn, (b) immer das nahe Horn
#              (rechts = links gespiegelt). (b) haengt sichtbar am Horn, die
#              Krone springt dabei aber bei jedem Schwung ueber den Kopf auf
#              die andere Seite (vorn rechts, abgewandt links). Genommen ist
#              (a) neu gelegt: die Krone haengt am fernen Horn nach aussen
#              herunter (22 Einheiten zur Mitte, 12 tiefer, 18 Grad mehr
#              geneigt, 88 % breit und 92 % gross - das ferne Horn ist
#              weiter weg), das Horn steht hinter ihr und ragt links oben
#              heraus; sie bleibt beim Schuetteln auf derselben Seite und
#              schwingt nur mit. Das alte Hornloch der Frontkrone ist
#              zugemalt (befunde_16_10\korrektur5\krone5.py).
#              Nachpruefung 16.10.2026 abends: so lehnte sie 45 Grad schraeg
#              vor dem Hinterkopf, und das ferne Horn kam links oben NEBEN
#              ihrem Rand heraus statt durch die Oeffnung - sie lehnte neben
#              dem Horn, statt darauf zu haengen. Rechts ist jetzt die Krone
#              vom nahen Horn (links.png, Geminis Dreiviertelansicht) so an
#              das ferne Horn gelegt, wie sie am nahen haengt: abgebildet
#              ueber die Hornachse (Spitze und Mitte 55 Einheiten darunter
#              vom nahen auf das ferne Horn), dann 25 Grad zurueckgedreht -
#              sie neigt sich wie vorn und am nahen Horn nach rechts -,
#              85 % gross (weiter weg) und 4 Einheiten tiefer. Das ferne Horn
#              steht IN der Krone und ragt zwischen den Zacken heraus, das
#              nahe Horn steht davor. Ausprobiert und verworfen: gespiegelt
#              (neigt sich zur Kopfmitte, liegt wie aufgesetzt auf dem
#              Schaedel), und hinter dem Schaedel (nur halb zu sehen).
#              Werkzeug: befunde_16_10\korrektur6\krone6b.py.
#              Siebte Fassung 16.10.2026 abends (Ajdin: "bei Kopf links sitzt
#              sie einfach oben auf dem Kopf, haengt an keinem Horn", und:
#              "weil die ja seitlich am Kopf runterhaengt, muss sie sich auch
#              seitlich sein ... wenn die Krone von uns weg dreht, ist nur
#              noch die Haelfte zu sehen ... sie darf sich nicht auf der
#              Stelle drehen, die Juwelen muessen sich beim Kopfdrehen
#              mitbewegen"). Bis dahin waren links und rechts dieselbe
#              Frontkrone, nur verschoben und in der Bildebene gedreht. Jetzt
#              dreht sie mit dem Kopf um die Senkrechte (45 Grad wie die
#              Seitenkoepfe): die Frontkrone als Reif (Kegelmantel) gedeutet,
#              rundum ergaenzt (acht Zacken, Perlen und rote Steine im
#              Wechsel), gedreht und als Skizze auf kopf_links bzw. den
#              gespiegelten Kopf gelegt; Gemini hat beide fertig gemalt.
#              links (nahes Horn): die Krone zeigt ihre Seite und ist zu uns
#              gekippt (man sieht in den Reif hinein), der grosse Stein ist
#              zur Schnauze hin nach links gewandert, das Horn steigt innen
#              auf und steht vor der Innenwand.
#              rechts (fernes Horn, eigenes Bild): sie haengt hinten am Kopf,
#              Schaedel, Stacheln und nahes Horn liegen davor - nur die obere
#              Haelfte mit dem Stein am rechten Ende schaut heraus, die
#              Spitze des fernen Horns ragt oben aus ihr heraus.
#              Vorn bleibt die Krone, wie sie ist. Werkzeuge:
#              befunde_16_10\korrektur7\ (krone3d.py, volltextur.py, krone7.py).
#              Nachpruefung 16.10.2026 spaet abends: rechts stand die Krone
#              trotzdem waagerecht hinter dem Kopf (Band etwa -6 Grad, vorn
#              +31, links +22) - Gemini hatte die schraege Skizze beim Malen
#              geradegerueckt; wieder "aufgesetzt" statt am Horn. Dazu endete
#              das Band rechts ohne Kontur, ein halber roter Stein ragte
#              heraus. Rechts kommt jetzt direkt aus dem 3D-Modell (ohne
#              Gemini): die gemalte Frontkrone rundum, mit dem Kopf um 45 Grad
#              gedreht - die Schraeglage ist die der Frontkrone, mitgedreht
#              (das Band faellt nach rechts aussen ab), der Stein sitzt am
#              Schnauzenende des Bands, das ferne Horn steht in der Krone und
#              ragt zwischen den Zacken heraus. Perlen und Steine sind runde
#              Bilder an ihrer 3D-Stelle (in der Textur wurden sie zur Kante
#              hin zu Splittern); halb hinter einer Zacke verdeckte fallen
#              weg; ringsum ein dunkler Umriss. Links: die halbierte Perle
#              neben der roten Zacke und der weisse Splitter rechts aussen
#              sind weg, beide Seitenkronen leicht nachgeschaerft.
#              Werkzeuge: befunde_16_10\korrektur8\ (krone8.py, links8.py).
#   "innen"    (A): ein breiter, niedriger Reif tief auf dem Schaedel um beide
#              Hornansaetze; die Hoerner wachsen innen aus der Krone heraus.
#              Rechts = links gespiegelt (die Krone ist symmetrisch).
# Umschalten: KRONE_GROSS unten aendern UND die Bilder der Form nach
# web/maskottchen/zierrat/krone_gross/ legen - die von "innen" liegen fertig
# in Drache_Bildteile\werkzeuge\befunde_16_10\korrektur3\krone_A\ (Kopie
# von kostueme2\korrektur3\krone_A\, dort LIESMICH.txt mit dem Befehl;
# die von "laessig" in Drache_Bildteile\fertig\zierrat\krone_gross\).
# Passen Bilder und Zahlen nicht zusammen,
# meldet dieser Bau "ACHTUNG, Bilder des Drachen" und der Test schlaegt fehl.
# Werkzeuge: kostueme2\korrektur3\werk\kronen_skizze.py und krone3.py.
#   Form: (vorne, links, eigenes rechts oder None) wie in GEMALTE_HUETE
KRONE_GROSS = "laessig"
KRONE_GROSS_FORMEN = {
    "laessig": ((173, 155, -9.71, 285.63), (173, 165, -18.19, 292.41), (145, 111, 21.22, 273.34)),
    "innen":   ((262, 108, 130.57, 272.07), (229, 119, 96.66, 276.3), None),
}
GEMALTE_HUETE["krone_gross"] = KRONE_GROSS_FORMEN[KRONE_GROSS][:2]
if KRONE_GROSS_FORMEN[KRONE_GROSS][2]:
    EIGENES_RECHTS["krone_gross"] = KRONE_GROSS_FORMEN[KRONE_GROSS][2]
# Gemalte Kopfstuecke, die die Hornspitzen (bild_hoerner_*) NICHT leeren.
HORNSPITZEN_BLEIBEN = ["brille", "sonnenbrille", "lesebrille", "monokel"]
# Funkeln (16.10.2026): sieben gemalte Sterne, je eine Bild-Ebene an "body"
# auf dem Platz des Vektorsterns (FUNKEN), mit denselben Keyframes fuer
# Groesse, Drehung und Deckkraft (funke_zeit) - sie blitzen also wie bisher
# der Reihe nach auf. Die Sternmitte liegt in der Bildmitte (64/64), die
# laengste Spitze 62,5 Pixel davon; so gross wie der Vektorstern ist das
# Bild bei Skala 100 * Radius / 62,5. Gelb und weiss wie die Vektorsterne,
# mit dunkelblauem Umriss wie der Drache (auf hellem Grund sichtbar).
#   Platz (Nummer in FUNKEN): (Bild, Radius der laengsten Spitze in Pixeln)
GEMALTE_FUNKEN = {0: ("stern_5", 62.53), 1: ("stern_6", 62.29), 2: ("stern_1", 62.54), 3: ("stern_2", 62.29),
                  4: ("stern_3", 62.54), 5: ("stern_7", 62.53), 6: ("stern_8", 62.28)}
STERN_PX = 128
# Kleidung am Rumpf (Eltern "body"): stueck: {teil: (Breite, Hoehe,
# Drehpunkt x, y, vor)}. Das Bild ist alles, was Gemini am Drachen
# veraendert hat und nicht mit nackter Haut verbunden ist - so bleibt auch
# die gelbe Schaerpe des Trikots ueber dem gelben Bauch erhalten. Was der
# Kopf oder die Arme verdecken, fehlt im Bild nicht: Gemini hat den Rumpf
# ein zweites Mal ohne Arme angezogen.
# Der Mantel des Koenigsmantels haengt HINTER dem Koerper und dem Schwanz
# (vor "skelett_wingL", also direkt hinter "tail"), aber vor den Fluegeln:
# Gemini hat ihn so gemalt, Schwanz und Beine liegen vor dem Samt. Vor dem
# Koerper, wo die Vektor-Ebene "umhang" sass, haette er nur Loecher, wo der
# Koerper durchschaut - und der Schwanz, der im Jubel um 9 Grad schwingt,
# waere am Lochrand abgeschnitten. Der Fanschal traegt "BOSNA" im Bild;
# die Textebene schal_bih_text faellt beim gemalten Schal weg.
# Hermelinkragen (Nachpruefung 16.10.2026): Er bestand aus zwei getrennten
# runden Fellpolstern, die seitlich ueber die Schulterlinie standen - wieder
# "Schulter/Oberarm betont", wie Ajdin es am Mantel bemaengelt hatte, und
# beim Jubel kamen die Arme aus den Polstern. Jetzt eine schmale Stola: um
# den Hals, flach auf den abfallenden Schultern, vorn zwei Baender bis zur
# Brustmitte mit goldener Spange. Sie liegt HINTER den Armen (Platz der
# Vektor-Ebene umhang, wie die anderen Halssachen) - vor den Armen haetten
# ihre Baender beim Weinen die Unterarme auf der Brust zugedeckt.
# (Seit 16.10.2026 mittags liegt ein Schulterumhang darueber - siehe "Dritte
# Durchsicht" unten; die Baender liegen weiter hinter den Armen.)
#
# Korrektur nach Ajdins Rueckmeldung vom 16.10.2026 (Quellen, Werkzeuge,
# Vorher/Nachher: kostueme2\korrektur\ im Arbeitsordner des Drachen):
# - Oberteile beim Jubel: "wenn der Drache sich freut, sind die Arme sehr
#   komisch, am meisten an den Schultern". Die Oberteile waren fuer haengende
#   Arme gemalt; erhoben sassen die Aermel wie Roehren mit runder Kappe vorn
#   auf der Brust, daneben standen die Ecken der Armloecher. Gemini hat den
#   angezogenen Drachen im Jubelbild 120 neu gemalt (Aermel wachsen aus den
#   Achseln, die Schulter steigt in den Aermel). Daraus "rumpf_jubel" am Rumpf
#   und die Aermel "oberarmL/R_jubel" (GEMALTE_AERMEL, JUBEL_OBERTEILE); sie
#   gelten, solange die Arme im Jubel oben stehen (cheer_oben, JUBEL_OBEN),
#   sonst das bisherige Rumpfbild. Der Arm steht dort relativ zum Rumpf
#   zwischen 119 und 136 Grad, darum passt eine Fassung fuer den ganzen
#   Jubel. Beim Weinen (Arme an den Wangen) bleibt es beim alten; in den je
#   drei Bildern, in denen die Arme waagerecht hoch- und runtergehen
#   (cheer_quer), bleibt das alte Rumpfbild, die Aermel sind aber schon die
#   Jubel-Aermel (Nachpruefung unten).
#   Nachpruefung 16.10.2026: Beim Trikot hatte der Schnitt nur genommen, was
#   sich deutlich vom nackten Drachen abhebt - blauer Stoff auf blauer Haut
#   und die gelbe Schaerpe auf dem gelben Bauch fielen weg: Loecher im Rumpf,
#   vom Aermel nur Umriss und Borte, kein Saum. Ausserdem hatten Trikot und
#   Lederjacke die Masken der Strickjacke bekommen (gleicher Name im
#   Zwischenspeicher) - daher Schlitze am Kragen und Kerben an den Achseln.
#   Neu geschnitten: Stoff ist, was innerhalb des Umrisses liegt, den Gemini
#   um das Stueck gemalt hat (Flaeche von aussen geflutet), jede Jacke mit
#   ihren eigenen Masken; unten (ab der Taille) geht das Bild weich ins alte
#   Rumpfbild ueber - es ist heil, hat den Saum, und der Wechsel in Bild 94
#   und 142 springt dort nicht. Die alten erhobenen Aermel standen in den
#   Uebergangsbildern (cheer_quer) als steife Polster waagerecht ab, beim
#   Trikot wie ein hartes T; dort gelten jetzt die schlanken Jubel-Aermel.
#   Werkzeug: Drache_Bildteile\werkzeuge\befunde_16_10\schulter2.py.
# - Jelek: sass mit den Schulterecken neben dem Hals auf den Fluegeln (oberer
#   Rand 278 Einheiten ueber dem Drehpunkt, Trikot 225). Jetzt 95 % breit,
#   88 % hoch und 4 Einheiten tiefer: oben am Halsansatz, die Ecken auf den
#   Schultern, unten an der Taille.
# - Schals: "Beim Freuen geht der Schal komisch in den Arm rein, am meisten
#   beim bosnischen Schal." Die Enden sind 36 Einheiten breit und haengen bis
#   an die Seiten der Brust; die Oberarme lagen in jedem Bild mit 5 bis 11
#   Einheiten darauf (beim Jubel und bei ok, wenn die Arme nach innen
#   schwingen, bis zu 25). Der Schal liegt jetzt VOR den Oberarmen (direkt
#   vor den Aermeln, "trikot_armL" - Trikot und Schal sind beide Halssachen,
#   also nie zusammen), hinter Kopf und Unterarmen: um den Hals auf den
#   Schultern, die Enden ueber der Brust; erhobene Arme gehen hinter dem
#   Wickel hoch, statt ihn zu durchstossen.
# - Koenigsmantel: zwischen den Haelften war nur gemalt, was neben Koerper
#   und haengenden Armen zu sehen war - beim Jubel ein Loch mit den Umrissen
#   der Arme. Der Mantel ist jetzt innen ganz (dunkelroter Samt unter den
#   gemalten Haelften), gleiche Groesse und Lage.
# - Farben: Jelek, Schal und Muetze (Winter), Nikolausmuetze, Fes, Bajram-Fes,
#   Mantel in dunklerem Rot, die Kappe in dunklerem Gruen - auf roter bzw.
#   gruener Haut waren sie kaum vom Drachen zu unterscheiden. Nachpruefung
#   16.10.2026: auch die spaeter gemalten Ohrenschuetzer (Rot auf roter Haut
#   wie beim Jelek, als einziges der neun Stuecke). Dunkle Stuecke auf der
#   Haut "nacht" (Sonnenbrille, Kopfhoerer, Doktorhut) und der Hexenhut auf
#   "galaxie" bleiben: sie stehen mit Umriss, Glanzlichtern bzw. Goldband
#   vor allem ueber dem Kopf, gegen den Hintergrund.
#
# Dritte Durchsicht 16.10.2026 mittags (Ajdin nach dem Video der Kostueme;
# Quellen, Werkzeuge und Vorher/Nachher: kostueme2\korrektur3\):
# - Koenigsmantel: "die Schultern gucken raus, die muessen im Gewand sein".
#   Zwischen der schmalen Stola und dem Mantel hinter dem Koerper standen in
#   jeder Stimmung die blauen Schultern frei. Gemini hat den Mantel im
#   Ruhebild 0 und im Jubelbild 120 neu gemalt: ein kurzer roter
#   Schulterumhang mit Goldborte liegt ueber beiden Schultern und dem oberen
#   Oberarm, die Stola obenauf, die Arme kommen unter der Borte hervor (beim
#   Jubel hebt der Umhang sich mit, die Arme kommen oben heraus). Daraus
#   "kragen" (Umhang + Stola) und "baender" (die zwei Hermelinbaender auf der
#   Brust), beide am Rumpf; beim Jubel mit erhobenen Armen (cheer_oben) die
#   Fassungen "_jubel". Der Kragen liegt VOR den Oberarmen (Platz
#   "trikot_armL", Halssachen gibt es nur einzeln): der Umhang deckt die
#   Schultern, die Arme schwingen darunter (idle/ok/sad hoechstens 9 Grad,
#   beim Weinen gehen sie unter dem Umhang hoch). Am Arm haengt nichts - so
#   bricht die Borte nirgends. Die Baender bleiben HINTER den Armen wie die
#   alte Stola: schwingen die Arme nach innen, liegen sie vor den Baendern.
#   Unten blendet der Kragen ueber 7 Einheiten aus, darunter haengt der
#   bisherige lange Mantel (unveraendert). Werkzeug: korrektur3\werk\mantel3.py.
# - Jelek: "wenn der Drache sich freut, ist das Jelek zu niedrig, es muss sich
#   mitbewegen". Es hing richtig am Rumpf (Sprung und Strecken macht es mit),
#   war aber fuer haengende Arme gemalt: mit erhobenen Armen steigen die
#   Schultern, und die Schulterteile des Jeleks endeten darunter. Wie bei den
#   Jacken jetzt ein Jubelbild "rumpf_jubel" (Gemini, Bild 120): die
#   Schulterteile liegen auf den Schultern, die Armloecher oeffnen sich nach
#   oben. Ein Jelek hat keine Aermel - das Bild liegt darum VOR den Oberarmen
#   (der Rand des Armlochs deckt den Armansatz) und gilt nur, solange die
#   Arme im Jubel oben stehen (cheer_oben). Beim Weinen bleibt das alte Bild:
#   dort liegen die Arme vor der Brust, das Jubelbild deckte sie zu
#   (ausprobiert). Unter dem Kinn gemalter Kragen bleibt im Bild, obwohl der
#   Kopf ihn in Bild 120 verdeckt - ohne ihn endete das Jelek mit einer
#   geraden Kante, sobald der Kopf beim Huepfen hoeher steht. Unten geht es
#   weich ins alte Bild ueber (Saum gleich, kein Sprung). Werkzeug:
#   korrektur3\werk\jelek3.py.
# - Trikot, Jacken und Schals geprueft: Trikot und Jacken haben ihre
#   Jubelbilder schon, die Schals liegen um den Hals und gehen mit ihm hoch.
# Nachpruefung 16.10.2026 nachmittags (Werkzeuge in
# Drache_Bildteile\werkzeuge\befunde_16_10\korrektur4\, Quellen davor in
# vor_korrektur4\; dieselben Gemini-Antworten, nur neu geschnitten):
# - Koenigsmantel: Schulterumhang (Jubel) und Hermelin am Hals (sonst) waren
#   oben mit dem Lineal abgeschnitten - das Bildfeld begann 120 Rumpfpixel
#   unter dem Oberrand des Rumpfbilds, der Umhang reicht hoeher. Jetzt hat er
#   oben Geminis Umriss (kragen 428 x 208, kragen_jubel 412 x 229). Dazu
#   raus: drachenblaue Hautreste neben der Goldborte (auf gold- und rosa-Haut
#   als Flecken sichtbar) und Reste der Baender im Kragenbild (grauer Rand,
#   weisse Fetzen, goldene Splitter an den Enden) - der Kragen liegt vor den
#   Armen, die beim ok-Schwung vor die Baender gehen; die eckigen Kerben am
#   Bandrand sind rund geschlossen. Werkzeug: mantel4.py.
# - Jelek-Jubelbild: Kragen- und Schulterspitzen waren oben waagerecht
#   gekappt, an den Armloechern standen Schnittstufen und blaue Hautreste.
#   Ursache war das Oeffnen der Maske mit einem 11x11-Quadrat (aus Spitzen
#   werden flache Kanten); jetzt rund und klein, jedes Drachenblau ist kein
#   Stoff (250 x 314). Werkzeug: jelek4.py.
# - Bewusst geblieben: in den je drei Uebergangsbildern des Jubels
#   (cheer_quer) gilt beim Jelek noch das Ruhebild - wie bei Trikot und
#   Jacken; ein Jubelbild dort deckte die waagerechten Arme zu.
# Vierte Durchsicht 16.10.2026 nachmittags (Ajdin: "Die Arme sind beim
# Mantel komisch abgeschnitten, und beim Jubel geht er durch den Mantel";
# Werkzeuge, Quellen, Vorher/Nachher: kostueme2\korrektur5\ bzw.
# Drache_Bildteile\werkzeuge\befunde_16_10\korrektur5\):
# - In Ruhe begann der Unterarm schon unter der Goldborte. Er liegt aber VOR
#   dem Kragen (die Unterarme liegen vor allem, auch vor dem Kopf), also lag
#   sein oberes Ende auf Borte und Samt - eine gerade Kante quer ueber dem
#   Umhang. Dazu fehlte im Kragenbild genau dort ein Stueck (beim Schneiden
#   war die Flaeche der Unterarme aus Bild 0 herausgenommen worden). Jetzt
#   ist der Kragen dort ganz (mantel5.py), und ein eigenes Bild "saum" - die
#   zwei Fluegel des Umhangs mit Borte, Pixel fuer Pixel wie im Kragen -
#   liegt VOR den Unterarmen (Platz "tears"): der Arm kommt unter der Borte
#   hervor. Wo der Saum liegt, ist in keiner Stimmung der Kopf, und die
#   Unterarme bleiben mehr als 8 Bildpixel von seinen inneren Kanten weg
#   (gemessen ueber alle Bilder: saum_analyse.py), also schneidet er sie
#   nirgends; die Borte hat dort ihren vollen unteren Umriss. Der Saum gilt
#   nur, solange die Arme haengen (SAUM_ZEIT) - beim Weinen und in den
#   Uebergangsbildern des Jubels gehen die Unterarme vor dem Umhang hoch.
# - Jubel: Gemini hatte die erhobenen Arme oben AUS dem Schulterumhang
#   kommen lassen; als Bild vor den Oberarmen sah das aus, als stiessen sie
#   durch den Samt. Jetzt liegt der Umhang (kragen_jubel) HINTER den Armen
#   wie ein Umhang, der ueber die Schultern nach hinten faellt; die zwei
#   Zipfel am Hals, aus denen bei Gemini die Arme kamen, sind abgeschnitten,
#   die Kante faellt vom Fell schraeg zur Schulterborte ab. Die Stola mit
#   Spange (stola_jubel) liegt VOR den Oberarmen: die Arme kommen unter dem
#   Fell hervor, ihr runder Ansatz liegt nicht sichtbar auf dem Fell
#   (jubel5.py). Ausprobiert und verworfen: der Ruhekragen hinter den
#   erhobenen Armen - er liegt zu tief, Schultern und Fell schauten frei.
JUBEL_OBERTEILE = ["trikot", "weste_leder", "weste_strick"]
OHNE_JUBEL = ("idle", "sad", "ok", "no", "no_l", "no_r", "cheer_ruhe", "cheer_quer", "cry")
# Koenigsmantel (16.10.2026 abends, Nachpruefung nach Ajdins "die Arme sind
# beim Mantel komisch abgeschnitten"): in den je drei Uebergangsbildern des
# Jubels (cheer_quer) lag noch der Ruhekragen ueber den Oberarmen - die
# waagerechten bzw. halb erhobenen Unterarme kamen seitlich aus dem
# Umhangrand wie aus einem Schlitz, und beim ersten Jubelbild sprang der
# Kragen auf die Stola. Jetzt gilt dort schon der Jubel-Umhang (hinter den
# Armen) mit der Stola vor den Oberarmen: die Arme sind von der Schulter an
# zu sehen, und der Wechsel faellt auf das Bild, in dem die Arme ohnehin
# hochschnellen. Beim Weinen bleibt der Ruhekragen (die Unterarme liegen
# dort vor ihm). Im Mantelbild sind ausserdem die feinen blauvioletten
# Striche im roten Samt neben den Beinen weg (Reste vom Umriss des blauen
# Drachen aus Geminis Bild, im Jubel und bei Traurig zu sehen) - aus dem
# Samt ringsum zugewachsen. Werkzeuge: befunde_16_10\korrektur6\
# (mantel_striche.py).
# Fuenfte Durchsicht 16.10.2026 abends (Ajdin: beim Weinen verschwanden die
# Oberarme unter dem Fellkragen und die Haende kamen aus dem Pelz an die
# Wangen; dazu seine Idee: "Wenn man mit einem Umhang die Haende hebt, geht
# der Umhang von den Schultern runter. Wir brauchen 2 Bilder fuer den
# Umhang"). Der Mantel hat jetzt zwei Zustaende:
#   Arme unten (MANTEL_RUHE: idle, sad, ok, no, no_l, no_r, Anfang und Ende
#     des Jubels) - Schulterumhang mit Fell auf den Schultern, die Arme
#     kommen darunter hervor (kragen, saum, baender wie bisher).
#   Arme oben (MANTEL_RUTSCH: Jubel mit erhobenen Armen und das ganze
#     Weinen) - der Umhang ist nach hinten von den Schultern gerutscht:
#     Hermelinkragen und Spange haengen tiefer, hinter den Oberarmen;
#     Schultern und Arme liegen ganz frei davor, keine Hand kommt aus dem
#     Pelz. Bild "rutsch" am Rumpf, Platz "umhang" (hinter den Armen, vor dem
#     Koerper). Gemini hat es am Jubelbild 120 gemalt - Vorlage war der
#     Drache mit nur dem langen Mantel, Muster der Ruhemantel. EIN Bild fuer
#     Jubel und Weinen, wie Ajdin es beschrieben hat; Geminis eigenes
#     Weinbild war unbrauchbar (es hatte den ganzen Drachen neu gezeichnet,
#     Fluegel und Bauch verschoben). Was die erhobenen Arme im Jubelbild
#     verdecken, stammt aus einem zweiten Gemini-Bild desselben Mantels
#     ohne Arme (nur das Fell) - beim Weinen liegen die Arme anders, und dort
#     lief der Kragen sonst mit einer Kante am alten Armumriss aus.
#   Dazwischen, in den je drei Bildern, in denen die Arme waagerecht hoch-
#   und runtergehen (cheer_quer): "rutsch_quer", das Bild ohne Arme ganz -
#   der Fellkragen liegt lose als Bogen ueber den Schultern, darunter das
#   rote Futter, die waagerechten Arme davor. Mit "rutsch" lag dort, wo im
#   Jubelbild der Arm stand, die gerade Oberkante des langen Mantels frei.
#   So rutscht der Umhang mit der Armbewegung: auf den Schultern - lose -
#   heruntergerutscht, und beim Senken der Arme zurueck; beim Weinen
#   wechselt er mit dem harten Schnitt der Stimmung. Die bisherigen
#   Jubelbilder kragen_jubel, stola_jubel und baender_jubel fallen weg
#   (Sicherung in Drache_Bildteile\werkzeuge\befunde_16_10\vor_korrektur7\).
#   Werkzeuge: befunde_16_10\korrektur7\ (mantel7.py).
# Nachpruefung 16.10.2026 spaet abends: in beiden Rutschbildern gab es nur
#   Fellbogen und Spange - das rote Schulterstueck mit der Goldborte
#   verschwand zwischen Bild 90 und 91 und kam zwischen 145 und 146 wieder
#   (Weinen: 269/270). Jetzt haengt in jedem Fellbogen genau das
#   Schulterstueck aus der Ruhe (Samt und Borte aus kragen, ohne Fell),
#   40 Rumpfpixel tiefer und 8 nach aussen, unter dem Fell und hinter den
#   Armen; oben im Bogen, wo es nicht hinreicht, setzt sich der Samt im
#   Schatten des Kragens fort. Ein Bild "rutsch" fuer ALLE Bilder mit
#   gehobenen Armen (waagerecht, oben, Weinen): der Mantel ohne Arme ganz
#   (bisher rutsch_quer) - beim Weinen lief der Pelz neben dem Hals im
#   alten Jubelbild stumpf hinter dem Arm aus, jetzt laeuft der Fellbogen
#   dahinter durch; und zwischen waagerechten und erhobenen Armen wechselt
#   kein Bild mehr. Gemini hatte statt des gerutschten Schulterstuecks den
#   ganzen Ruhemantel nachgemalt (Kragen wieder am Hals) - nicht genommen.
#   Werkzeuge: befunde_16_10\korrektur8\ (mantel8.py).
# 17.10.2026 (Ajdin nach dem Video: das Fell passte nicht, "dieses Rote an
#   der Schulter soll ja weggehen, so maessig nach hinten geworfen werden";
#   nachts hat er dazu ein Konzeptbild von Gemini abgenommen: "jaaa genau
#   sooo"). Mit gehobenen Armen ist der Umhang jetzt nach hinten geworfen:
#   seine vorderen Kanten liegen als Goldboegen neben dem Hals, von der
#   Spange (zwei Knoepfe mit Steg) hinauf bis unter die Wangen, innen rotes
#   Futter und ein schmales Hermelinband am Hals; hinter den Schultern
#   bauscht sich der Samt. Schultern und Arme liegen frei davor. Drei
#   Bilder statt des einen Rutschbilds:
#   "rutsch"        Jubel (Arme waagerecht und oben): Boegen, Futter, Fell,
#                   Spange - vor dem Koerper, hinter den Armen.
#   "rutsch_weinen" dasselbe fuer die Haende an den Wangen. Die Oberarme
#                   stehen dort anders, darum ein eigenes Gemini-Bild der
#                   Weinpose (Vorlage: das Konzept und der Drache bei Bild 300).
#   "rutsch_hinten" der lange Mantel hinter den Schultern hoeher gezogen
#                   (jede Spalte oben bis zu einer runden Kante gestreckt) -
#                   hinter dem Koerper, vor dem langen Mantel, fuer Jubel und
#                   Weinen. Er deckt die gerade Oberkante des langen Mantels,
#                   die mit waagerechten Armen frei lag; nach unten ist er
#                   Pixel fuer Pixel der lange Mantel, also ohne Naht.
#   Im Konzept stehen Geminis Arme weiter aussen als die des Drachen: an
#   Ort und Stelle laegen die Goldboegen ganz hinter den Oberarmen, und den
#   ganzen Kragen schmaler zu verzerren zerdrueckte Knoepfe und Fell. Die
#   Teile sind darum neu zusammengesetzt: das Goldband laeuft mit seinem
#   Querschnitt aus dem Konzept an der Innenkante der Oberarme entlang (in
#   dem Bild, in dem sie am weitesten innen stehen - in allen anderen ist
#   der Bogen ganz zu sehen), das Fell ist nur gedreht, Spange und Steg
#   sind Geminis Pixel. Der Wechsel vom Kragen auf den Schultern zum
#   geworfenen Umhang faellt wie bisher auf das Bild, in dem die Arme
#   hochschnellen (beim Weinen auf den harten Schnitt der Stimmung).
#   Werkzeuge: befunde_16_10\korrektur10\ (vorn10.py, montage10.py, hinten10.py).
# 17.10.2026 nachmittags (Pruefung der zehnten Runde gegen das Konzept): der
#   Kragen sah nur ungefaehr aus wie dort - ein schmales V, die Goldboegen
#   duenne Streifen innen an den Oberarmen ("wie Hosentraeger"), das Fell
#   halb so breit, das rote Futter bis auf einen Zwickel weg, mit der Haut
#   "gold" verschwanden Boegen und Spange fast; bei waagerechten Armen
#   standen die Boegen frei wie zwei Pfaehle bis unters Kinn; der Samt
#   hinter den Schultern war spaltenweise gestreckt (Strichcode, Naehte, ein
#   Stueck Goldborte darin); beim Weinen endeten Bogenspitzen und Futter oben
#   mit gerader Kante, ein Bogen hatte eine Delle, dazu vier lose Pixel.
#   Der Vorderteil ist darum neu gebaut statt aus Geminis Pixeln geschnitten:
#   - EIN durchgehender Goldbogen in U-Form, gemalt mit dem Querschnitt des
#     Konzept-Goldbands (dunkle Kante, Gold, heller Glanzstreif), breiter als
#     vorher, mit dunklem Umriss rundum (hebt ihn auch von goldener Haut ab)
#     und runden Spitzen wie im Konzept. Er liegt 4 Pixel unter den
#     Oberarmen (in dem Bild, in dem sie am weitesten innen stehen), so ist
#     er in jedem Bild breit zu sehen.
#   - das Hermelin des Konzepts als volle Sichel am Bogen entlang, unten
#     hinter dem Knopf; zwischen Gold und Fell das rote Futter, oben ein
#     Zwickel mit dunkler, leicht gewoelbter Kante (keine Schnittkante).
#   - Knoepfe und Steg aus dem Konzept, fuer Jubel und Weinen dieselben.
#   Drei Vorderbilder: "rutsch" (Arme oben, cheer_oben), "rutsch_quer" (die
#   je drei Bilder mit waagerechten Armen, cheer_quer: der Bogen steigt am
#   Hals nur bis unter das Fell und geht dann ueber die Schulter nach aussen
#   hinab hinter den Arm - dort liegt er wirklich ueber den Schultern, statt
#   neben dem Kinn frei zu stehen; der Wechsel zum hohen Kragen faellt auf
#   das Bild, in dem die Arme hochschnellen) und "rutsch_weinen" (die runde
#   Spitze endet oben am Unterarm). "rutsch_hinten" ist glatter Samt:
#   die Farbe je Spalte aus dem langen Mantel knapp unter seiner Oberkante,
#   breit geglaettet, oben ein heller Wulst mit dunklem Umriss, unten weich
#   in den langen Mantel geblendet. Geminis Arme stehen im Konzept weiter
#   aussen als die des Drachen; neben den Oberarmen ist weniger Platz, darum
#   bleibt der Kragen in der Mitte etwas schmaler als im Konzept.
#   Werkzeuge: befunde_16_10\korrektur11\ (kragen11.py, hinten11.py).
# 17.10.2026 abends (Ajdin mit beiden Konzeptbildern daneben: "man sieht den
#   Umhang immer noch hinter den Armen" - "nimm dafuer rechtes Bild", also
#   umhang_konzept\wurf_2.png). Dort ist der Mantel schlank: neben dem Kopf
#   und hinter den erhobenen Armen ist kein Rot, der Samt beginnt erst an
#   der Schulter und faellt neben dem Rumpf zu Boden, die Goldkanten laufen
#   fast senkrecht hinab. In der App ragte der breite lange Mantel (dazu der
#   hochgezogene Samt) hinter den Armen bis an Ellbogen und Faeuste. wurf_2
#   ist aus Bild 120 gemalt und liegt pixelgenau darauf; die Teile sind
#   daraus geschnitten:
#   "rutsch_hinten"       der lange Mantel fuer Arme oben und Weinen, statt
#                         "mantel" (der gilt nur noch mit haengenden Armen).
#                         Was in Bild 120 hinter Koerper, Armen und Schwanz
#                         liegt, ist von der anderen Seite gespiegelt (der
#                         Mantel ist symmetrisch) bzw. aus dem Samt ringsum
#                         zugewachsen. Ueber einer Schulterlinie ist er
#                         durchsichtig: im Spalt zwischen Hals und erhobenem
#                         Arm liegt nie Rot, aussen beginnt er wie im
#                         Konzept am Oberarm.
#   "rutsch_hinten_quer"  derselbe Mantel fuer die waagerechten Arme
#                         (cheer_quer); seine Oberkante liegt in allen sechs
#                         Bildern unter dem Oberarm - kein Samt darueber.
#   "rutsch"              der Stehkragen aus wurf_2: Goldband, rotes Futter,
#                         Hermelin, zwei Knoepfe mit Kette. Ein Bild fuer
#                         alle gehobenen Arme (waagerecht, oben, Weinen) -
#                         kein Kragenwechsel mehr, wenn die Arme
#                         hochschnellen. Er liegt VOR den Oberarmen (hinter
#                         Unterarmen und Kopf, wie der Kragen mit haengenden
#                         Armen): Geminis Oberarme sind schmaler, das
#                         Goldband liegt dort, wo beim Drachen die Innenkante
#                         des Oberarms ist. Hinter den Armen war es fast ganz
#                         verdeckt - daher der schmale Kragen der Runden davor.
#   rutsch_quer und rutsch_weinen fallen weg (Sicherung in
#   Drache_Bildteile\werkzeuge\befunde_16_10\vor_korrektur12\umhang\).
#   Werkzeuge: befunde_16_10\korrektur12\ (ausschnitt12.py, hinten12.py,
#   vorn12.py, teile12.py).
# 17.10.2026 spaet abends (Pruefung der zwoelften Runde):
#   - Gruener Rand: rutsch_hinten hatte an Saum, Goldkante und Unterkante
#     einen olivgruenen Saum vom Greenscreen (die Kanten aus wurf_2 waren
#     nicht entgruent). Jetzt hat kein Pixel einen Gruenueberhang, der
#     Umriss ist dunkelbraun wie sonst. Dazu sind duenne Spalten im Samt
#     unter dem Schwanz zu - beim Sprung schien dort der Hintergrund durch.
#   - Harter Wechsel im Jubel: mit den Armen sprang auch der lange Mantel in
#     einem Bild von breit (mantel) auf schlank (rutsch_hinten) und zurueck.
#     In den drei Bildern mit waagerechten Armen (cheer_quer: 91-93 beim
#     Heben, 143-145 beim Senken) haengen jetzt Zwischenstufen
#     "mantel_quer1" bis "mantel_quer3" (25, 50 und 75 % des Weges; die
#     Goldbaender sind Zeile fuer Zeile aufeinander verzerrt, kein doppeltes
#     Band): der Mantel schwingt in drei Bildern von breit nach schlank.
#     "rutsch_hinten_quer" faellt weg. Der Kragen wechselt weiter in dem
#     Bild, in dem die Arme hochschnellen (Schulterumhang mit Stola ->
#     Stehkragen) - dort bewegt sich ohnehin alles.
#   - Stehkragen bei waagerechten Armen: die Spitzen des Goldbands standen
#     wie zwei Hoerner neben dem Kinn, dazwischen Hintergrund. Dort ist er
#     senkrecht gestaucht (KRAGEN_STAUCHEN, um KRAGEN_FUSS zwischen den
#     Knoepfen) und waechst mit dem Heben auf volle Hoehe.
#   Werkzeuge: befunde_16_10\korrektur13\ (putzen13.py, morph13.py,
#   teile13.py).
MANTEL_RUHE = tuple(z for z in OHNE_JUBEL if z not in ("cheer_quer", "cry"))
MANTEL_RUTSCH = ("cheer_quer", "cheer_oben", "cry")
# Die drei Bilder mit waagerechten Armen als Stufen (17.10.2026 spaet
# abends): Stufe 1 liegt an der Ruhe, 3 an den erhobenen Armen - beim Heben
# 91/92/93, beim Senken 145/144/143 (_bilder). Je Stufe eine Zwischenstufe
# des langen Mantels (mantel_quer1-3) und eine Hoehe des Stehkragens
# (Anteil der vollen Hoehe, gestaucht um KRAGEN_FUSS, Bildpunkt in
# rutsch.webp unten zwischen den Knoepfen).
MANTEL_STUFEN = ("cheer_quer_1", "cheer_quer_2", "cheer_quer_3")
KRAGEN_STAUCHEN = {"cheer_quer_1": 0.72, "cheer_quer_2": 0.81, "cheer_quer_3": 0.90}
KRAGEN_FUSS = (107.0, 112.0)
# Stimmungen mit haengenden Armen (Saum des Koenigsmantels vor den Unterarmen)
SAUM_ZEIT = ("idle", "sad", "ok", "no", "no_l", "no_r", "cheer_ruhe")
#   stueck: {teil: (Breite, Hoehe, Drehpunkt x, y, vor[, sichtbar])}
GEMALTE_RUMPFSTUECKE = {
    "trikot":       {"rumpf":       (245, 273, 121.94, 456.47, "trikot", OHNE_JUBEL),
                     "rumpf_jubel": (325, 323, 161.94, 496.47, "trikot", ("cheer_oben",))},
    "weste_leder":  {"rumpf":       (264, 295, 130.38, 493.99, "weste_leder", OHNE_JUBEL),
                     "rumpf_jubel": (344, 345, 170.38, 533.99, "weste_leder", ("cheer_oben",))},
    "weste_strick": {"rumpf":       (247, 284, 122.88, 462.57, "weste_strick", OHNE_JUBEL),
                     "rumpf_jubel": (327, 334, 162.88, 502.57, "weste_strick", ("cheer_oben",))},
    "jelek":        {"rumpf":       (253, 316, 125.8, 487.51, "jelek", OHNE_JUBEL),
                     "rumpf_jubel": (250, 314, 124.8, 485.51, "trikot_armL", ("cheer_oben",))},
    "umhang":       {"rutsch_hinten":      (693, 474, 346.0, 473.0, "skelett_wingL", ("cheer_oben", "cry")),
                     "mantel_quer1":       (729, 411, 364.0, 410.0, "skelett_wingL", (MANTEL_STUFEN[0],)),
                     "mantel_quer2":       (717, 411, 358.0, 410.0, "skelett_wingL", (MANTEL_STUFEN[1],)),
                     "mantel_quer3":       (705, 411, 352.0, 410.0, "skelett_wingL", (MANTEL_STUFEN[2],)),
                     "mantel":             (742, 517, 370.05, 514.16, "skelett_wingL", MANTEL_RUHE),
                     "kragen":             (428, 208, 213.0, 503.0, "trikot_armL", MANTEL_RUHE),
                     "rutsch":             (215, 142, 107.0, 523.0, "trikot_armL", MANTEL_RUTSCH),
                     "saum":               (428, 221, 213.0, 503.0, "tears", SAUM_ZEIT),
                     "baender":            (129, 180, 63.0, 385.0, "umhang", MANTEL_RUHE)},
    "schal_winter": {"rumpf":  (191, 288,  94.74, 545.58, "trikot_armL")},
    "schal_bih":    {"rumpf":  (243, 396, 120.53, 556.37, "trikot_armL")},
}
# Aermel (Trikot kurz, die Jacken lang): je Armteil des Drachen ein Bild an
# derselben Rig-Ebene, mit 12 Pixeln (Unterarm an Faust und Wange: 10) Rand
# um das Feld des Armteils, sonst derselbe Drehpunkt. Ein Aermel ist genau
# dann zu sehen, wenn sein Armteil zu sehen ist (BILD_TEILE): erhobener
# Oberarm mit runder Kappe an der Schulter, Unterarm offen, als Faust oder
# an der Wange. "_hoch" nutzt das Feld des haengenden Oberarms.
#   Armteil: (Breite, Hoehe, Drehpunkt x, y)
# Die Aermel sind schlank und gehen oben weich in den Rumpf ueber - Ajdins
# "es muss nach innen gehen" (15.10.2026).
GEMALTE_AERMEL = {
    "oberarmL":        (128, 170, 80.58, 40.8),  "oberarmR":        (128, 171, 47.42, 41.8),
    "unterarmL_offen": (116, 191, 72.86, 36.4),  "unterarmR_offen": (116, 191, 42.14, 36.4),
    "unterarmL_faust": (109, 171, 67.86, 34.4),  "unterarmR_faust": (109, 171, 41.14, 34.4),
    "unterarmL_wange": (108, 171, 68.86, 33.4),  "unterarmR_wange": (108, 171, 39.14, 33.4),
}
OBERARME = ["oberarmL", "oberarmL_hoch", "oberarmR", "oberarmR_hoch"]
UNTERARME = [u + "_" + v for u in ("unterarmL", "unterarmR") for v in ("offen", "faust", "wange")]
ZIERRAT_ORDNER = "zierrat"


def gemalte_kostueme():
    """{stueck: [(teil, Rig-Ebene, Breite, Hoehe, Drehpunkt x, y, sichtbar, vor)]}
    sichtbar: None = immer, "vorn"/"links"/"rechts" = Seite im Kopfplan,
    sonst Stimmungen wie in BILD_TEILE."""
    t = {}
    for st, (vorne, links) in GEMALTE_HUETE.items():
        b, h, x, y = links
        rechts = EIGENES_RECHTS.get(st, (b, h, round(b - x, 2), y))
        t[st] = [("vorne", "head") + vorne + ("vorn", st), ("links", "head") + links + ("links", st),
                 ("rechts", "head") + rechts + ("rechts", st)]
    # Funkeln: die Lage setzt erst der Bau unten (funken_ebene), hier nur
    # Bild, Groesse und Bildmitte als Drehpunkt.
    t["funkeln"] = [(GEMALTE_FUNKEN[i][0], "body", STERN_PX, STERN_PX, STERN_PX / 2, STERN_PX / 2, None, "funkeln")
                    for i in sorted(GEMALTE_FUNKEN)]
    for st, teile in GEMALTE_RUMPFSTUECKE.items():
        t[st] = [(n, "body") + e[:4] + (e[5] if len(e) > 5 else None, e[4]) for n, e in teile.items()]
    for st in AERMEL_STUECKE:
        for arm in OBERARME + (UNTERARME if st in LANGE_AERMEL else []):
            ebene, sichtbar = BILD_TEILE[arm][0], BILD_TEILE[arm][5]
            vor = st + ("_arm" + arm[7] if arm.startswith("oberarm") else "_unterarm" + arm[8])
            feld = GEMALTE_AERMEL[arm.replace("_hoch", "")]
            # Jubel-Aermel (16.10.2026, siehe JUBEL_OBERTEILE): im Feld des
            # Oberarms, solange die Arme im Jubel erhoben sind - seit der
            # Nachpruefung vom 16.10.2026 auch in den Uebergangsbildern mit
            # waagerechten Armen (cheer_quer), wo der alte erhobene Aermel
            # als steifes Polster abstand. Der alte bleibt fuers Weinen.
            if st in JUBEL_OBERTEILE and arm.endswith("_hoch"):
                t[st].append((arm.replace("_hoch", "_jubel"), ebene) + feld + (("cheer_oben", "cheer_quer"), vor))
                sichtbar = tuple(z for z in sichtbar if z != "cheer_hoch")
            t[st].append((arm, ebene) + feld + (sichtbar, vor))
    return t


# Nur beim Bild-Drachen: der Vektor-Drache (--vektor) behaelt seine
# gezeichneten Kostueme und bleibt Byte fuer Byte, wie er war.
GEMALT = {} if VEKTOR else gemalte_kostueme()
GEMALT_EBENEN = ["bild_%s_%s" % (st, e[0]) for st, teile in GEMALT.items() for e in teile]
ZIERRAT_ALLE += GEMALT_EBENEN


# Kopfwechsel (Ajdin nach dem Probevideo, 15.10.2026: "die Koepfe bewegen
# sich noch komisch"). Die kurzen Reaktionen beginnen und enden in der Ruhe,
# mit dem neutralen Kopf davor und danach.
# Erster Versuch war eine Blende: der neue Kopf in 3 Bildern ueber dem
# neutralen auf, am Ende in 4 wieder ab. Das zeigte zwei Gesichter
# uebereinander - offene Augen durch die geschlossenen, zwei Muender, und
# wo der Unterkiefer von jubel/froh tiefer reicht, einen grauen Streifen
# ueber dem Hals (Pruefung 15.10.2026). Darum jetzt wie im Zeichentrick:
# der Kopf wechselt hart, und bei froh und finster liegt ein kurzes
# Blinzeln dazwischen. Mit geschlossenen Augen faellt der Wechsel nicht
# auf, das liest sich wie ein Lidschlag. Der Jubelkopf hat ohnehin
# geschlossene Augen; er kommt direkt und geht ueber das Blinzeln.
#   Stimmung: (Bilder am Anfang, Bilder am Ende, Kopf in diesen Bildern)
# Die Stimmungen in Schleife (sad, cry) schneiden hart: ein Uebergang am
# Anfang kaeme bei jeder Runde wieder.
# Bis 15.10.2026 wandten no_l und no_r den Kopf einmal ab und hielten ihn
# dort (Wechsel auf kopf_links bzw. kopf_rechts zwei Bilder nach Beginn, im
# Moment, in dem der Kopf kurz schmal wurde - DREHEN und head_scale), und no
# wiegte den Kopf um den Hals. Ajdin am 15.10.2026: "er soll nicht den Kopf
# wackeln wie ein Inder, sondern richtig den Kopf schuetteln", und dabei
# "durchgehend boese gucken" - beim Abwenden kamen links/rechts der neutrale
# Kopf und das Blinzeln dazwischen. Jetzt SCHUETTELN unten.
KOPF_JE_STIMMUNG = {"idle": "neutral", "cheer": "jubel", "sad": "traurig", "ok": "froh", "no": "finster",
                    "cry": "weinen", "no_l": "finster", "no_r": "finster"}
KOPF_WECHSEL = {"cheer": (0, 2, "blinzeln"), "ok": (2, 2, "blinzeln")}
# Kopfschuetteln bei einer falschen Antwort (16.10.2026): Der Kopf dreht
# abwechselnd nach links und rechts - die gemalten abgewandten Koepfe -, und
# auf dem Weg durch die Mitte steht fuer zwei Bilder der finstere Frontkopf.
# Vorweg zwei Bilder finster (er schaut erst boese, dann schuettelt er), am
# Ende bleibt er finster bis zum letzten Bild; zurueck in die Ruhe (neutral)
# geht es erst mit idle danach. Nie der neutrale Kopf und kein Blinzeln im
# Abschnitt: der Blinzelkopf laechelt. Der Kopf kippt dabei nicht mehr um
# den Hals (head_rot/head_pos ruhen in no, no_l, no_r) - das war das Wackeln.
# Tempo: 4 Bilder je Seite + 2 Bilder Mitte = 0,2 s je Schwung, gut zwei
# Hin-und-her je Sekunde - so schuettelt man energisch den Kopf; no_l und
# no_r sind 10 Bilder laenger und schwingen mit 5 Bildern je Seite etwas
# ruhiger, danach 0,4 s finsterer Blick. Die App wechselt bei falschen
# Antworten zwischen no_l und no_r (zmajReact in web/index.html), darum
# beginnt das eine links und das andere rechts.
#   Stimmung: (Seiten nacheinander, Bilder finster vorweg, Bilder je Seite,
#              Bilder finster dazwischen)
SCHUETTELN = {"no":   ("LRLR", 2, 4, 2),
              "no_l": ("LRLR", 2, 5, 2),
              "no_r": ("RLRL", 2, 5, 2)}
SEITEN = {"L": "links", "R": "rechts"}
# Die Bilder des Jubels, in denen die Arme oben sind (relativ zum Beginn):
# dort Faust und Oberarm mit Kappe, davor und danach die haengende Hand.
JUBEL_HOCH = (1, 56)
# Darin die Bilder, in denen die Arme wirklich oben stehen (16.10.2026,
# gemessen: Oberarm 119 bis 136 Grad gegen den Rumpf; in den drei Bildern
# davor und danach geht er waagerecht durch, 25 bis 60 Grad). Nur hier gelten
# die Jubel-Fassungen der Oberteile (JUBEL_OBERTEILE): mit waagerechten Armen
# standen ihre hochgezogenen Schultern neben dem Hals. "cheer_quer" sind die
# Bilder von JUBEL_HOCH ausserhalb davon (dort altes Rumpfbild, aber schon
# die Jubel-Aermel - Nachpruefung 16.10.2026, siehe gemalte_kostueme).
JUBEL_OBEN = (4, 53)
# Je drei Bilder mit waagerechten Armen beim Heben und beim Senken - so
# viele Stufen hat der Uebergang des Koenigsmantels (MANTEL_STUFEN).
assert JUBEL_OBEN[0] - JUBEL_HOCH[0] == JUBEL_HOCH[1] - JUBEL_OBEN[1] == len(MANTEL_STUFEN)


def schuettel_folge(name):
    """Die Koepfe eines Schuettel-Abschnitts, Bild fuer Bild ab Beginn."""
    seiten, vorweg, je_seite, dazwischen = SCHUETTELN[name]
    a, e = SEG[name]
    folge = ["finster"] * vorweg
    for i, s in enumerate(seiten):
        folge += ["finster"] * (dazwischen if i else 0) + [SEITEN[s]] * je_seite
    assert len(folge) < e - a, (name, "Schuetteln laenger als der Abschnitt")
    return folge + ["finster"] * (e - a - len(folge))


# ======================= Kopfplan =======================
# 16.10.2026: EIN Plan dafuer, welcher Kopf in welchem Bild zu sehen ist.
# Bis dahin rechneten die Kopfbilder (kopf_folge), die Brillen (umschalten
# mit DREHEN) und die Huete (_mitruecken, ganze Stimmung lang) je fuer sich
# aus, wann der Kopf abgewandt ist. Beim Schuetteln wechselt er aber viermal
# je Abschnitt die Seite - drei Rechnungen laufen da leicht auseinander, und
# dann sitzt der Hut einen Augenblick auf dem falschen Kopf. Jetzt fragt
# jede Ebene am Kopf denselben Plan:
#   KOPFPLAN[t] = (kopf, seite) fuer jedes Bild t = 0..OP-1
#     kopf   Name des Kopfbilds ohne "kopf_"/"hoerner_": neutral, blinzeln,
#            jubel, froh, traurig, weinen, finster, links, rechts
#     seite  wohin die Schnauze zeigt: "vorn", "links" oder "rechts"
#   kopf_deckkraft(kopf=None, seite=None)
#            Halte-Keyframes 100/0 fuer eine Ebene, die nur bei diesem Kopf
#            und/oder auf dieser Seite zu sehen ist. So schalten die Kopf- und
#            Hornbilder (bild_deckkraft), und genauso die gemalten Huete
#            (je ein Bild vorn/links/rechts, sichtbar_werte). Das gemalte
#            Skelett braucht nichts Eigenes: es ist ein Hautsatz mit
#            denselben Kopfbildern.
#   kopf_spur(je_seite, ruhe)
#            Halte-Keyframes fuer einen beliebigen Wert je Seite, z. B. Ort
#            und Breite: Brillen (BRILLE_GEDREHT), Huete und Kronen
#            (SCHAEDEL_GEDREHT) und das Gesicht des Vektor-Skeletts
#            (GESICHT_GEDREHT).
# Blenden gibt es keine, mit Absicht: jeder Wechsel ist hart und faellt fuer
# alle Ebenen auf dasselbe Bild (eine Blende zeigte zwei Gesichter
# uebereinander, siehe oben; test_immer_genau_ein_kopf prueft es). Weiche
# Uebergaenge macht der Plan mit einem Zwischenkopf (Blinzeln, KOPF_WECHSEL).
def kopfplan():
    plan = []
    for t in range(OP):
        name = next(n for n, (a, e) in SEG.items() if a <= t < e)
        a, e = SEG[name]
        k = KOPF_JE_STIMMUNG[name]
        if name == "idle" and any(a + x <= t < a + y for x, y in BLINZELN):
            k = "blinzeln"
        if name in KOPF_WECHSEL:
            vorn, hinten, zwischen = KOPF_WECHSEL[name]
            if t < a + vorn or t >= e - hinten:
                k = zwischen
        if name in SCHUETTELN:
            k = schuettel_folge(name)[t - a]
        plan.append((k, k if k in SEITEN.values() else "vorn"))
    return plan


KOPFPLAN = kopfplan()


def _halten(werte):
    """Halte-Keyframes nur dort, wo sich der Wert aendert, dazu einer am
    Ende (OP) mit dem Wert von Bild 0, wie bei allen Zeitleisten hier."""
    ks = [hold(t, werte[t]) for t in range(OP) if t == 0 or werte[t] != werte[t - 1]]
    return anim(ks + [hold(OP, werte[0])])


def kopf_deckkraft(kopf=None, seite=None):
    """100, wo der Kopfplan diesen Kopf und/oder diese Seite zeigt, sonst 0."""
    return _halten([100.0 if kopf in (None, k) and seite in (None, s) else 0.0 for k, s in KOPFPLAN])


def kopf_spur(je_seite, ruhe):
    """Ein Wert je Seite des Kopfplans ({"links": ..., "rechts": ...}),
    sonst ruhe - gehalten, damit er im selben Bild springt wie das Kopfbild."""
    return _halten([je_seite.get(s, ruhe) for _k, s in KOPFPLAN])


# Wie weit Schaedel und Gesicht am abgewandten Kopf wandern, in Kopf-
# Einheiten (Hk). Im Bild kopf_links liegt die Schaedeldecke weiter rechts
# (Kopfraster 15.10.2026: Mitte bei +10 bis +15 statt 0), Augen und Schnauze
# ruecken zur Schnauzenseite und stehen enger. kopf_rechts ist der Spiegel.
#   SCHAEDEL_GEDREHT: Huete, Kronen, Ohrensachen und der Schaedel des
#     Vektor-Skeletts ruecken so weit mit (dx) - seit 16.10.2026 nur noch
#     die Vektor-Stuecke; die gemalten Huete haben eigene Seitenbilder.
#   GESICHT_GEDREHT: Augenhoehlen, Brauen, Mund und Schnauze des Vektor-
#     Skeletts (dx, dy, Breite %). Weniger weit als die Augen im Bild (die
#     Brillen ruecken um 27, BRILLE_GEDREHT unten): der Vektor-Schaedel
#     bleibt von vorn gesehen, und weiter aussen staende die Augenhoehle
#     ueber seinen Rand hinaus. Gegen den mitgerueckten Schaedel sind es
#     18 Einheiten, dazu 80 % Breite - das liest sich als Drehung.
# Das Vektor-Skelett hat keine gemalten Seitenkoepfe; so dreht es den Kopf
# in denselben Bildern wie der Bild-Drache (Ajdin, 15.10.2026: bei Kopf
# links/rechts machte das Skelett "eine ganz andere Animation").
SCHAEDEL_GEDREHT = {"links": 12, "rechts": -12}
GESICHT_GEDREHT = {"links": (-6, 4, 80), "rechts": (6, 4, 80)}


def _bilder(z):
    """Die Bildnummern zu einem Eintrag in "sichtbar" (siehe BILD_TEILE)."""
    if z.startswith("cheer_quer_"):
        # Stufe k der waagerechten Arme (MANTEL_STUFEN): beim Heben das k-te,
        # beim Senken das k-letzte Bild von cheer_quer
        a, _e = SEG["cheer"]
        k = int(z[len("cheer_quer_"):])
        return [a + JUBEL_HOCH[0] + k - 1, a + JUBEL_HOCH[1] - k]
    if z in ("cheer_hoch", "cheer_ruhe", "cheer_oben", "cheer_quer"):
        a, e = SEG["cheer"]
        hoch = range(a + JUBEL_HOCH[0], a + JUBEL_HOCH[1])
        oben = range(a + JUBEL_OBEN[0], a + JUBEL_OBEN[1])
        return {"cheer_hoch": hoch, "cheer_oben": oben,
                "cheer_quer": [t for t in hoch if t not in oben],
                "cheer_ruhe": [t for t in range(a, e) if t not in hoch]}[z]
    return range(*SEG[z])


def sichtbar_werte(sichtbar):
    """Deckkraft (0..100) fuer jedes Bild 0..OP-1 zu einem Eintrag
    "sichtbar": None = immer, eine Seite des Kopfplans ("vorn", "links",
    "rechts" - die gemalten Huete) oder eine Liste von Stimmungen."""
    if sichtbar is None:
        return [100.0] * OP
    if sichtbar in ("vorn", "links", "rechts"):
        return [100.0 if s == sichtbar else 0.0 for _k, s in KOPFPLAN]
    w = [0.0] * OP
    for z in sichtbar:
        for t in _bilder(z):
            w[t] = 100.0
    return w


def bild_werte(teil):
    """Deckkraft (0..100) eines Bildteils fuer jedes Bild 0..OP-1."""
    sichtbar = BILD_TEILE[teil][5]
    if sichtbar == "kopf":
        name = teil.split("_", 1)[1]
        return [100.0 if k == name else 0.0 for k, _s in KOPFPLAN]
    return sichtbar_werte(sichtbar)


def bild_deckkraft(teil):
    """Halte-Keyframes je Wechsel. Die Eltern-Ebene gibt ihre Deckkraft in
    Lottie nicht weiter - darum schaltet jedes Bild selbst."""
    return _halten(bild_werte(teil))


# "hoerner" ganz vorn: die Hutebenen liegen dahinter, also ragen die Spitzen
# oben aus jedem Hut heraus, statt darunter zu verschwinden.
# v6: Die Unterarme (mit den Haenden) liegen VOR dem Gesicht - beim Weinen
# halten sie sich die Haende an die Wangen (Vorlage pro_weinen.png). Die
# Oberarme bleiben hinter dem Kopf. Ganz hinten ein Schatten am Boden; der
# Buecherstapel ("perch") ist weg, der Drache steht.
# v6, 15.10.2026: Unteraermel vor den Unterarmen, Mantelkragen zwischen Kopf
# und Armen, Galaxie-Sterne direkt vor Schwanz und Fluegeln.
ORDER = ["funkeln", "hoerner"] + KOPF_TEILE + BRILLEN + \
        ["tears", "skelett_unterarmL"] + UNTERAERMEL["L"] + ["unterarmL", "skelett_unterarmR"] + UNTERAERMEL["R"] + \
        ["unterarmR",
         "brows", "mouth_cry", "mouth_sad", "mouth_open", "mouth_idle", "skelett_zaehne",
         "eyes_cry", "eyes_happy", "lids", "skelett_augen", "eyes", "skelett_kopf", "head", "umhang_kragen"] + \
        AERMEL + ["skelett_armL", "armL", "skelett_armR", "armR"] + \
        ["schal_bih_text"] + HALS_TEILE + \
        ["galaxie", "skelett", "body", "legs", "skelett_schwanz", "galaxie_schwanz", "tail",
         "skelett_wingL", "galaxie_wingL", "wingL", "skelett_wingR", "galaxie_wingR", "wingR", "schatten"]
# v7: Die Bild-Ebenen stehen in ORDER direkt vor ihrer (leeren) Rig-Ebene,
# also genau auf deren Tiefe. Wichtig, weil die App die Ebenen nach "ind"
# sortiert: mit neuen, hohen Nummern laege der Rumpf ueber dem Kopf (so ist
# es beim ersten Probelauf passiert), und die Kostueme passten nicht mehr
# dazwischen.
# 16.10.2026: Die Bild-Ebenen der gemalten Kostueme stehen direkt vor der
# Ebene, die ihr "vor" nennt (GEMALT) - meist die Vektor-Ebene, die sie
# ersetzen. Die Vektor-Ebene bleibt in ORDER (put() braucht ihre Nummer),
# wird aber nicht mehr ausgeliefert (ZIERRAT_ALLE).
if not VEKTOR:
    _vor = {}
    for _st, _teile in GEMALT.items():
        for _e in _teile:
            _vor.setdefault(_e[7], []).append("bild_%s_%s" % (_st, _e[0]))
    ORDER = [b for n in ORDER for b in _vor.get(n, []) + ["bild_" + t for t, v in BILD_TEILE.items() if v[0] == n] + [n]]
IDX = {n: i+1 for i, n in enumerate(ORDER)}
built = {}
def put(name, shapes, parent=None, p=(0, 0), a=(0, 0), r=0, animk=None, s=100, masken=None):
    L = {"ddd": 0, "ind": IDX[name], "ty": 4, "nm": name, "sr": 1,
         "ks": {"o": const(100), "r": const(r), "p": const([p[0], p[1], 0]), "a": const([a[0], a[1], 0]), "s": const([s, s, 100])},
         "ao": 0, "shapes": list(reversed(shapes)), "ip": 0, "op": OP, "st": 0, "bm": 0}
    if parent: L["parent"] = IDX[parent]
    if animk: L["ks"].update(animk)
    if masken:
        L["hasMask"] = True
        L["masksProperties"] = [{"inv": False, "mode": "a", "pt": const(m), "o": const(100), "x": const(0), "nm": "Maske %d" % (i + 1)}
                                for i, m in enumerate(masken)]
    built[name] = L

def textebene(name, wort, x, y, groesse, farbe, parent, sperrung=-30, r=0):
    """Eine Lottie-Textebene. Lottie kennt keine Buchstaben als Formen - es
    schreibt echten Text und ueberlaesst die Schrift dem Anzeigeprogramm.
    Deshalb steht unten in der Datei eine Schriftenliste; "ZmajFett" zeigt
    auf Nunito, die Schrift der Oberflaeche, die in web/fonts liegt.
    j=2 heisst mittig, tr ist die Sperrung in Tausendstel Geviert.
    r dreht die Zeile (Grad im Uhrzeigersinn) - v6: 90 fuer den Schriftzug,
    der der Laenge nach auf dem Schalende steht."""
    return {"ddd": 0, "ind": IDX[name], "ty": 5, "nm": name, "sr": 1,
            "parent": IDX[parent], "ao": 0,
            "ks": {"o": const(100), "r": const(r), "p": const([x, y, 0]),
                   "a": const([0, 0, 0]), "s": const([100, 100, 100])},
            "t": {"d": {"k": [{"s": {"s": groesse, "f": "ZmajFett", "t": wort,
                                     "j": 2, "tr": sperrung, "lh": groesse * 1.2,
                                     "ls": 0, "fc": farbe[:3]}, "t": 0}]},
                  "p": {}, "m": {"g": 1, "a": const([0, 0])}, "a": []},
            "ip": 0, "op": OP, "st": 0, "bm": 0}


def P(dx=0, dy=0): return [260 + dx, BODEN + dy, 0]
def S3(x, y): return [x, y, 100]
def HP(dx=0, dy=0):
    h = V(*HALS); return [round(h[0] + dx, 2), round(h[1] + dy, 2), 0]

# ======================= Zeitleisten =======================
# Jede Stimmung beginnt und endet so, dass die App sie sauber abspielen kann:
# idle, sad und cry laufen in Schleife (Anfang = Ende), cheer, ok, no, no_l
# und no_r laufen einmal und enden nahe der Ruhepose, weil danach idle kommt.
# Der Koerper hat seinen Anker an den Fusssohlen: Stauchen und Strecken
# druecken die Figur auf den Boden, statt sie schweben zu lassen.
SQ = S3(100, 100)
body_pos = spur({
    "cheer": [(0, P()), (6, P()), (14, P(0, -22)), (22, P()), (28, P()), (34, P()), (42, P(0, -22)), (50, P()), (59, P())],
    "ok":    [(0, P()), (4, P()), (10, P(0, -18)), (16, P()), (29, P())],
    "no":    [(0, P()), (8, P(-2)), (16, P(2)), (24, P(-1)), (29, P())],
}, P(), dims=3)
_schluchz = [(t, S3(103, 95.5) if k % 2 else S3(101, 97.5)) for k, t in enumerate(range(0, 89, 9))] + [(89, S3(101, 97.5))]
body_scale = spur({
    "idle":  [(0, SQ), (45, S3(101, 98.6)), (89, SQ)],
    "cheer": [(0, SQ), (6, S3(108, 92)), (14, S3(97, 104)), (22, S3(107, 94)), (28, SQ), (34, S3(108, 92)), (42, S3(97, 104)),
              (50, S3(107, 94)), (56, SQ), (59, SQ)],
    "sad":   [(0, S3(102, 96.5)), (30, S3(103, 95.5)), (59, S3(102, 96.5))],
    "ok":    [(0, SQ), (4, S3(107, 93)), (10, S3(96, 105)), (16, S3(104, 96)), (22, SQ), (29, SQ)],
    "cry":   _schluchz,
    "no_l":  [(0, SQ), (14, S3(101, 98)), (39, SQ)],
    "no_r":  [(0, SQ), (14, S3(101, 98)), (39, SQ)],
}, SQ, dims=3)
head_rot = spur({
    "idle":  [(0, 0), (30, -2.5), (60, 2), (89, 0)],
    "cheer": [(0, 0), (6, 3), (14, -5), (22, 3), (28, 0), (34, 3), (42, -5), (50, 3), (59, 0)],
    "sad":   [(0, 5), (30, 6.5), (59, 5)],
    "ok":    [(0, 0), (4, 3), (10, -5), (18, 2), (29, 0)],
    "no":    [(0, 0), (6, -6), (12, 6), (18, -5), (24, 3), (29, 0)],
    "cry":   [(0, 0), (22, -2), (45, 0), (67, 2), (89, 0)],
    "no_l":  [(0, 0), (12, -11), (32, -10), (39, -3)],
    "no_r":  [(0, 0), (12, 11), (32, 10), (39, 3)],
}, 0)
# Bei "falsch" schuettelt der Kopf seitlich (Verschiebung UND leichtes Kippen).
head_pos = spur({
    "sad":  [(0, HP(0, 6))],
    "no":   [(0, HP()), (6, HP(-9)), (12, HP(9)), (18, HP(-7)), (24, HP(4)), (29, HP())],
    "cry":  [(0, HP(0, 5))],
    # no_l: Kopf nach links abwenden und dort bleiben, am Ende halb zurueck
    "no_l": [(0, HP()), (12, HP(-9, 3)), (32, HP(-9, 3)), (39, HP(-3, 1))],
    # no_r: dasselbe nach rechts
    "no_r": [(0, HP()), (12, HP(9, 3)), (32, HP(9, 3)), (39, HP(3, 1))],
}, HP(), dims=3)
def wing_rot(sg):
    # positiv = im Uhrzeigersinn: der linke Fluegel hebt sich, der rechte senkt sich
    return spur({
        "idle":  [(0, 0), (40, 5*sg), (72, -2*sg), (89, 0)],
        "cheer": [(0, 0), (6, -8*sg), (14, 20*sg), (22, -5*sg), (28, 12*sg), (34, -8*sg), (42, 20*sg), (50, -5*sg), (59, 0)],
        "sad":   [(0, -14*sg), (30, -16*sg), (59, -14*sg)],
        "ok":    [(0, 0), (5, -6*sg), (11, 15*sg), (19, -4*sg), (29, 0)],
        "no":    [(0, 0), (10, -6*sg), (20, 4*sg), (29, 0)],
        "cry":   [(0, -14*sg), (45, -17*sg), (89, -14*sg)],
        "no_l":  [(0, 0), (14, -8*sg), (39, -3*sg)],
        "no_r":  [(0, 0), (14, -8*sg), (39, -3*sg)],
    }, 0)
# Fluegelschlag: die Haut wird beim Hochschlagen schmaler, wie von vorn gesehen
wing_scale = spur({
    "idle":  [(0, SQ), (40, S3(95, 100)), (89, SQ)],
    "cheer": [(0, SQ), (6, SQ), (14, S3(86, 100)), (22, SQ), (28, S3(92, 100)), (34, SQ), (42, S3(86, 100)), (50, SQ), (59, SQ)],
    "ok":    [(0, SQ), (11, S3(90, 100)), (29, SQ)],
}, SQ, dims=3)
tail_rot = spur({
    "idle":  [(0, 0), (45, -5), (89, 0)],
    "cheer": [(0, 0), (8, 9), (16, -9), (24, 9), (32, -9), (40, 9), (48, -9), (59, 0)],
    "sad":   [(0, 6), (30, 7), (59, 6)],
    "ok":    [(0, 0), (8, -8), (18, 6), (29, 0)],
    "no":    [(0, 0), (15, 5), (29, 0)],
    "cry":   [(0, 7), (45, 9), (89, 7)],
    "no_l":  [(0, 0), (18, -6), (39, 0)],
    "no_r":  [(0, 0), (18, 6), (39, 0)],
}, 0)
# Arme: Oberarm dreht in der Schulter, Unterarm im Ellbogen. Werte fuer den
# linken Arm, der rechte spiegelt (sg = -1). Weinen: Haende an die Wangen -
# ausgerechnet mit Schulter (838,1010), Ellbogen (762,1190) und Handmitte
# (712,1400) der Vorlage, Ziel ist die Wange bei (870,725).
ARM_WEINEN = (115, 101)
arm_scale = spur({"cheer": [(0, SQ), (8, S3(100, 120)), (53, S3(100, 120)), (59, SQ)]}, SQ, dims=3)
def arm_rot(sg):
    w = ARM_WEINEN[0]
    return spur({
        "idle":  [(0, 0), (45, 3*sg), (89, 0)],
        "cheer": [(0, 0), (8, 118*sg), (14, 124*sg), (22, 114*sg), (30, 124*sg), (38, 114*sg), (46, 124*sg), (53, 118*sg), (59, 0)],
        "sad":   [(0, -5*sg), (30, -6*sg), (59, -5*sg)],
        "ok":    [(0, 0), (7, 9*sg), (18, 9*sg), (29, 0)],
        "cry":   [(t, (w + (3 if k % 2 else 0))*sg) for k, t in enumerate(range(0, 89, 9))] + [(89, w*sg)],
    }, 0)
def unterarm_rot(sg):
    return spur({
        "cheer": [(0, 0), (8, 46*sg), (22, 54*sg), (30, 40*sg), (38, 54*sg), (46, 40*sg), (53, 46*sg), (59, 0)],
        "sad":   [(0, -10*sg)],
        "ok":    [(0, 0), (7, -6*sg), (18, -6*sg), (29, 0)],
        "cry":   [(0, ARM_WEINEN[1]*sg)],
    }, 0)
# Lider: Hoehe in Prozent der Augenhoehe, von oben gemessen
lids_scale = spur({
    "idle": [(0, S3(100, 0)), (28, S3(100, 0)), (31, S3(100, 100)), (34, S3(100, 0)), (62, S3(100, 0)), (65, S3(100, 100)),
             (68, S3(100, 0)), (89, S3(100, 0))],
    "sad":  [(0, S3(100, 12)), (40, S3(100, 12)), (43, S3(100, 100)), (46, S3(100, 12)), (59, S3(100, 12))],
    "no":   [(0, S3(100, 0)), (5, S3(100, 24)), (29, S3(100, 12))],
    "no_l": [(0, S3(100, 0)), (10, S3(100, 22)), (39, S3(100, 18))],
    "no_r": [(0, S3(100, 0)), (10, S3(100, 22)), (39, S3(100, 18))],
}, S3(100, 0), dims=3)
pupil_pos = spur({
    "idle": [(0, [0, 0]), (25, [3, 0.5]), (45, [3, 0.5]), (60, [-3, 0.5]), (75, [-3, 0.5]), (89, [0, 0])],
    "sad":  [(0, [0, 4])],
    "ok":   [(0, [0, 0]), (8, [0, -2]), (29, [0, 0])],
    "no":   [(0, [0, 1])],
    # Blick weicht mit aus: erst zur Seite, am Ende halb zurueck
    "no_l": [(0, [0, 1]), (10, [-6, 3]), (39, [-4, 2])],
    "no_r": [(0, [0, 1]), (10, [6, 3]), (39, [4, 2])],
}, [0, 0], dims=2)
def opa(on):
    ks = [hold(a, 100 if n in on else 0) for n, (a, b) in SEG.items()]
    ks.append(hold(OP, 100 if "idle" in on else 0)); return anim(ks)
# Brauen: Drehung um ihre Mitte (positiv = innen runter = finster) und Hub.
def brow_rot(sg):
    return spur({
        "cheer": [(0, -6*sg)],
        "sad":   [(0, -22*sg)],
        "ok":    [(0, -5*sg)],
        "no":    [(0, 0), (5, 18*sg), (29, 16*sg)],
        "cry":   [(0, -20*sg)],
        "no_l":  [(0, 0), (10, -14*sg), (39, -12*sg)],
        "no_r":  [(0, 0), (10, -14*sg), (39, -12*sg)],
    }, 0)
def brow_pos(p):
    def q(dy): return [p[0], round(p[1] + dy, 2)]
    return spur({"cheer": [(0, q(-5))], "sad": [(0, q(-4))], "ok": [(0, q(-4))],
                 "no": [(0, q(0)), (5, q(3)), (29, q(3))], "cry": [(0, q(-1))]}, q(0), dims=2)
mouth_open_scale = spur({"cheer": [(0, SQ), (8, S3(112, 118)), (52, S3(112, 118)), (59, SQ)]}, SQ, dims=3)
mouth_cry_scale = spur({"cry": [(t, S3(106, 94) if k % 2 else S3(96, 105)) for k, t in enumerate(range(0, 89, 8))] + [(89, S3(96, 105))]},
                       SQ, dims=3)
def traene(start, x0, y0, dx, fall=36):
    """Zeitleisten (Ort, Deckkraft) fuer einen Tropfen: faellt schraeg nach
    aussen und wird dabei durchsichtig, zweimal je cry-Schleife."""
    a, e = SEG["cry"]; n = e - a
    def ort(u): return [round(x0 + dx * u, 2), round(y0 + 48 * u, 2), 0]
    def deck(u): return 100 if u <= 0.6 else round(100 * (1 - u) / 0.4)
    stuecke = []                                   # (von, bis, u_von, u_bis)
    for t0 in sorted({start % n, (start + n // 2) % n}):
        t1 = t0 + fall
        if t1 < n:
            stuecke.append((t0, t1, 0.0, 1.0))
        else:                                      # ueber das Ende: Rest am Anfang
            stuecke.append((t0, n - 1, 0.0, (n - 1 - t0) / fall))
            stuecke.append((0, t1 - n, (n - t0) / fall, 1.0))
    stuecke.sort()
    pk, ok = [], []
    for von, bis, u0, u1 in stuecke:
        pk += [(a + von, ort(u0)), hold(a + bis, ort(u1))]
        ok += [(a + von, deck(u0))]
        if u0 < 0.6 < u1: ok.append((a + von + round((0.6 - u0) / (u1 - u0) * (bis - von)), 100))
        ok.append(hold(a + bis, deck(u1) if u1 < 1 else 0))
    ruhe = ort(0)
    pk = [hold(0, ruhe)] + ([hold(a, ruhe)] if pk[0][0] > a else []) + pk + [hold(e, ruhe)]
    ok = [hold(0, 0)] + ([hold(a, 0)] if ok[0][0] > a else []) + ok + [hold(e, 0)]
    return anim(pk), anim(ok)
schatten_scale = spur({
    "cheer": [(0, SQ), (6, S3(104, 100)), (14, S3(78, 80)), (22, SQ), (34, S3(104, 100)), (42, S3(78, 80)), (50, SQ), (59, SQ)],
    "ok":    [(0, SQ), (10, S3(86, 88)), (16, SQ), (29, SQ)],
}, SQ, dims=3)

# ---------- Bewegung des Bild-Drachen (v7) ----------
# Ajdin nach dem Probevideo der Bildteile, 15.10.2026:
#  1. "Beim Jubel gehen die hochgestreckten Arme in die Fluegel hinein." Mit
#     den Winkeln oben (Oberarm 118, Unterarm 46 Grad) lag der erhobene Arm
#     fast genau auf dem inneren Fluegelknochen (Vorlage (888,950) bis
#     (656,540)), und die Fluegel schlugen um 20 Grad nach oben und wurden
#     auf 86 % schmal - dabei wanderten sie in die Arme hinein. Gleiche Farbe,
#     gleicher Umriss: der Arm verschwand in der Flughaut. Jetzt geht der Arm
#     steiler hoch (128 Grad) und die Faust liegt zwischen Kopf und Fluegel;
#     die Summe Oberarm + Unterarm bleibt 164 Grad, so steht die Faust so
#     aufrecht wie in pro_jubel_vorne.png. Die Fluegel schlagen beim Jubel
#     vor allem nach aussen-unten (weg von den Armen) und werden hoechstens
#     auf 95 % schmal. Die Arme liegen in ORDER ohnehin vor den Fluegeln.
#  2. "Die Koepfe bewegen sich noch komisch." Das Gesicht steckt jetzt im
#     Bild; die alten Kopfbewegungen waren fuer ein gezeichnetes Gesicht
#     gedacht und mit bis zu 11 Grad und 9 Einheiten seitlich viel zu gross -
#     der Kopf rutschte dabei sichtbar vom Hals. Und sad, cry und no_l
#     sprangen beim Start sofort in ihre Pose. Jetzt: hoechstens 4,5 Grad um
#     den Halspunkt, seitlich hoechstens 2 Einheiten, und jede Stimmung
#     beginnt und endet in der Ruhe - auch die Schleifen (sad und cry seufzen
#     bzw. schluchzen aus der Ruhe heraus). Dazu der Kopfwechsel mit
#     Blinzeln (KOPF_WECHSEL oben).
#  3. Pruefung 15.10.2026, zwei Spruenge zurueck in die Ruhe, nach jeder
#     falschen bzw. jeder Jubel-Antwort zu sehen: am Ende von no_l/no_r
#     standen die Fluegel noch 3 Grad schraeg und schnappten in idle zurueck
#     (jetzt 0 am Ende); und beim Jubel gingen die Arme in fuenf Bildern
#     steif durch die Waagerechte wie bei einer Vogelscheuche. Jetzt fuehrt
#     der Ellbogen: der Unterarm knickt erst ein (85 Grad), der Arm folgt -
#     die Faust geht auf kurzem Weg nach oben, und zurueck genauso. Die
#     Faust gibt es nur, solange die Arme oben sind (JUBEL_HOCH); unten
#     steht schon die offene Hand von idle.
#     sad und cry setzen weiter hart ein: es sind Schleifen, Anfang = Ende.
#  4. 16.10.2026, Kopfschuetteln (SCHUETTELN, KOPFPLAN): in no, no_l und no_r
#     kippt und rutscht der Kopf nicht mehr um den Hals - das Schuetteln
#     machen allein die gemalten Seitenkoepfe. Auch das kurze Schmalwerden
#     des Kopfes beim Abwenden (head_scale, DREHEN) ist weg: bei vier
#     Wechseln je Abschnitt pumpte der Kopf. Das Vektor-Gesicht (nur noch
#     am Skelett) schaut in no_l und no_r so finster wie in no.
# Der Vektor-Drache (--vektor) behaelt die alten Zeitleisten unveraendert.
if not VEKTOR:
    _schluchz_bild = [(0, SQ)] + [(t, S3(102, 97) if k % 2 == 0 else S3(100.8, 98.6))
                                  for k, t in enumerate(range(9, 81, 9))] + [(89, SQ)]
    body_scale = spur({
        "idle":  [(0, SQ), (45, S3(101, 98.6)), (89, SQ)],
        "cheer": [(0, SQ), (6, S3(108, 92)), (14, S3(97, 104)), (22, S3(107, 94)), (28, SQ), (34, S3(108, 92)),
                  (42, S3(97, 104)), (50, S3(107, 94)), (56, SQ), (59, SQ)],
        "sad":   [(0, SQ), (30, S3(102, 96.5)), (59, SQ)],
        "ok":    [(0, SQ), (4, S3(107, 93)), (10, S3(96, 105)), (16, S3(104, 96)), (22, SQ), (29, SQ)],
        "cry":   _schluchz_bild,
        "no_l":  [(0, SQ), (14, S3(101, 98)), (39, SQ)],
        "no_r":  [(0, SQ), (14, S3(101, 98)), (39, SQ)],
    }, SQ, dims=3)
    head_rot = spur({
        "idle":  [(0, 0), (30, -1.5), (60, 1.2), (89, 0)],
        "cheer": [(0, 0), (14, -2.5), (28, 0.8), (42, -2.5), (54, 0), (59, 0)],
        "sad":   [(0, 0), (30, 2), (59, 0)],
        "ok":    [(0, 0), (10, -2.5), (20, 1), (29, 0)],
        "cry":   [(0, 0), (22, -1.5), (45, 0), (67, 1.5), (89, 0)],
    }, 0)
    head_pos = spur({
        "sad":  [(0, HP()), (30, HP(0, 3)), (59, HP())],
        "cry":  [(0, HP()), (22, HP(0, 2.5)), (45, HP()), (67, HP(0, 2.5)), (89, HP())],
    }, HP(), dims=3)

    def wing_rot(sg):
        # positiv hebt die Spitze - und schiebt den inneren Knochen zum Arm hin
        return spur({
            "idle":  [(0, 0), (40, 5*sg), (72, -2*sg), (89, 0)],
            "cheer": [(0, 0), (6, -8*sg), (14, 4*sg), (22, -10*sg), (28, -2*sg), (34, -8*sg), (42, 4*sg), (50, -10*sg),
                      (59, 0)],
            "sad":   [(0, -14*sg), (30, -16*sg), (59, -14*sg)],
            "ok":    [(0, 0), (5, -6*sg), (11, 15*sg), (19, -4*sg), (29, 0)],
            "no":    [(0, 0), (10, -6*sg), (20, 4*sg), (29, 0)],
            "cry":   [(0, -14*sg), (45, -17*sg), (89, -14*sg)],
            "no_l":  [(0, 0), (14, -8*sg), (32, -6*sg), (39, 0)],
            "no_r":  [(0, 0), (14, -8*sg), (32, -6*sg), (39, 0)],
        }, 0)
    wing_scale = spur({
        "idle":  [(0, SQ), (40, S3(95, 100)), (89, SQ)],
        "cheer": [(0, SQ), (6, SQ), (14, S3(95, 100)), (22, SQ), (28, S3(97, 100)), (34, SQ), (42, S3(95, 100)), (50, SQ),
                  (59, SQ)],
        "ok":    [(0, SQ), (11, S3(90, 100)), (29, SQ)],
    }, SQ, dims=3)

    # Jubel: oben von Bild 5 bis 51, auf und ab in je fuenf Bildern ueber
    # den eingeknickten Ellbogen (siehe 3. oben). Unten ab Bild 57.
    def arm_rot(sg):
        w = ARM_WEINEN[0]
        return spur({
            "idle":  [(0, 0), (45, 3*sg), (89, 0)],
            "cheer": [(0, 0), (2, 50*sg), (5, 128*sg), (14, 134*sg), (22, 124*sg), (30, 134*sg), (38, 124*sg),
                      (46, 134*sg), (51, 128*sg), (54, 50*sg), (57, 0), (59, 0)],
            "sad":   [(0, -5*sg), (30, -6*sg), (59, -5*sg)],
            "ok":    [(0, 0), (7, 9*sg), (18, 9*sg), (29, 0)],
            "cry":   [(t, (w + (3 if k % 2 else 0))*sg) for k, t in enumerate(range(0, 89, 9))] + [(89, w*sg)],
        }, 0)

    def unterarm_rot(sg):
        return spur({
            "cheer": [(0, 0), (2, 85*sg), (5, 36*sg), (14, 30*sg), (22, 40*sg), (30, 30*sg), (38, 40*sg), (46, 30*sg),
                      (51, 36*sg), (54, 85*sg), (57, 0), (59, 0)],
            "sad":   [(0, -10*sg)],
            "ok":    [(0, 0), (7, -6*sg), (18, -6*sg), (29, 0)],
            "cry":   [(0, ARM_WEINEN[1]*sg)],
        }, 0)
    arm_scale = spur({"cheer": [(0, SQ), (5, S3(100, 120)), (51, S3(100, 120)), (57, SQ), (59, SQ)]}, SQ, dims=3)

    # Das Vektor-Gesicht traegt nur noch das Skelett. Auch dort sollen no,
    # no_l und no_r in der Ruhe enden - bisher blieben Blick, Lider und
    # Brauen schraeg stehen und schnappten in idle zurueck.
    # 16.10.2026: no_l und no_r schauen finster wie no (zusammengekniffene
    # Lider, Brauen innen runter, Blick geradeaus) statt traurig zur Seite -
    # die Seite macht jetzt der Kopfplan (GESICHT_GEDREHT).
    def _finster(lang, ruhe, an, halb):
        """Finsterer Blick ueber einen ganzen Schuettel-Abschnitt: in 5 Bildern
        auf, bis 5 Bilder vor Schluss halten, dann zurueck in die Ruhe."""
        return [(0, ruhe), (5, an), (lang - 6, halb), (lang - 1, ruhe)]
    _NO = {n: SEG[n][1] - SEG[n][0] for n in SCHUETTELN}
    lids_scale = spur({
        "idle": [(0, S3(100, 0)), (28, S3(100, 0)), (31, S3(100, 100)), (34, S3(100, 0)), (62, S3(100, 0)),
                 (65, S3(100, 100)), (68, S3(100, 0)), (89, S3(100, 0))],
        "sad":  [(0, S3(100, 12)), (40, S3(100, 12)), (43, S3(100, 100)), (46, S3(100, 12)), (59, S3(100, 12))],
        **{n: _finster(lang, S3(100, 0), S3(100, 24), S3(100, 12)) for n, lang in _NO.items()},
    }, S3(100, 0), dims=3)
    pupil_pos = spur({
        "idle": [(0, [0, 0]), (25, [3, 0.5]), (45, [3, 0.5]), (60, [-3, 0.5]), (75, [-3, 0.5]), (89, [0, 0])],
        "sad":  [(0, [0, 4])],
        "ok":   [(0, [0, 0]), (8, [0, -2]), (29, [0, 0])],
        **{n: _finster(lang, [0, 0], [0, 1], [0, 1]) for n, lang in _NO.items()},
    }, [0, 0], dims=2)

    def brow_rot(sg):
        return spur({
            "cheer": [(0, -6*sg)],
            "sad":   [(0, -22*sg)],
            "ok":    [(0, -5*sg)],
            "cry":   [(0, -20*sg)],
            **{n: _finster(lang, 0, 18*sg, 16*sg) for n, lang in _NO.items()},
        }, 0)

    def brow_pos(p):
        def q(dy): return [p[0], round(p[1] + dy, 2)]
        return spur({"cheer": [(0, q(-5))], "sad": [(0, q(-4))], "ok": [(0, q(-4))], "cry": [(0, q(-1))],
                     **{n: _finster(lang, q(0), q(3), q(3)) for n, lang in _NO.items()}}, q(0), dims=2)


# ======================= Die Figur =======================
# ---------- Schatten am Boden (haengt NICHT am Koerper: er springt nicht mit) ----------
put("schatten", [group(ellipse(0, 0, 210, 18), fill(INK, 13))], p=(262, BODEN + 2), animk={"s": schatten_scale})

# ---------- Koerper: Hals, Rumpf, Oberschenkel ----------
# Ein einziger Umriss von unter dem Kinn bis zu den Knien; die Oberschenkel
# gehoeren dazu, damit an der Huefte keine Naht entsteht. Unterschenkel und
# Fuesse liegen dahinter in "legs". Zwischen den Beinen eine Kerbe, in der
# das untere Ende des Bauchs sitzt.
KOERPER_L = [(1024, 770), (955, 774), (910, 790), (903, 850), (899, 905), (885, 938), (860, 962), (838, 990),
             (828, 1040), (824, 1110), (820, 1180), (814, 1240), (806, 1300), (798, 1360), (784, 1415), (763, 1462),
             (747, 1520), (742, 1585), (748, 1636), (765, 1672), (795, 1695), (845, 1708), (905, 1712), (945, 1700),
             (958, 1655), (975, 1615), (1000, 1600), (1024, 1598)]
BAUCH_L = [(1024, 790), (946, 795), (942, 850), (940, 930), (930, 1005), (918, 1050), (904, 1090), (891, 1130),
           (881, 1170), (874, 1215), (868, 1260), (866, 1310), (867, 1360), (871, 1410), (876, 1450), (888, 1492),
           (906, 1532), (930, 1572), (952, 1610), (978, 1642), (1000, 1660), (1024, 1668)]
# Rillen: Mitte (y) und wie weit die Enden hoeher liegen; gemessen an der Vorlage
RILLEN = [(875, 20, 81), (978, 18, 86), (1084, 22, 111), (1208, 28, 145), (1344, 28, 157), (1475, 28, 148), (1584, 22, 95)]
def rille(yc, hub, hb):
    a = V(1024 - hb + 8, yc - hub); b = V(1024 + hb - 8, yc - hub)
    return arc(a, b, hub * K / 0.75)
body_shapes = [
    form(VL(SYM(KOERPER_L)), BLUE),
    # Schatten rechts (Licht kommt von links oben) und an den Innenseiten der Schenkel
    flaechen([VL([(1100, 800), (1146, 930), (1200, 1020), (1226, 1200), (1238, 1380), (1268, 1460), (1298, 1540), (1298, 1630),
                  (1278, 1680), (1220, 1704), (1160, 1690), (1175, 1560), (1188, 1420), (1186, 1250), (1160, 1100), (1112, 960)]),
              VL([(850, 1470), (912, 1520), (952, 1580), (946, 1690), (900, 1708), (880, 1640), (868, 1560)])], BLUE_D, 23),
    # Lichtkanten links an Hals und Oberschenkel
    linien([VL([(918, 805), (915, 860), (912, 905)]), VL([(768, 1480), (757, 1540), (756, 1600), (766, 1650)])], BLUE_L, 1.8),
    # Oberschenkel setzen sich mit einer Linie vom Rumpf ab (wie in der Vorlage)
    linien([VL([(842, 1452), (882, 1492), (922, 1548), (950, 1606)]), VL(SP([(842, 1452), (882, 1492), (922, 1548), (950, 1606)]))],
           BLUE_D, LW * 0.85),
    # Bauch
    form(VL(SYM(BAUCH_L)), YEL, s=YEL_D, w=2.2),
    flaeche(VL([(1100, 880), (1118, 1000), (1150, 1120), (1172, 1260), (1176, 1380), (1160, 1480), (1120, 1560), (1070, 1640),
                (1112, 1520), (1140, 1420), (1150, 1300), (1138, 1170), (1108, 1040), (1092, 920)]), YEL_D, 30),
    flaeche(VL([(926, 1010), (902, 1100), (886, 1200), (881, 1320), (886, 1430), (900, 1490), (900, 1400), (898, 1300),
                (903, 1200), (916, 1110), (934, 1036)]), WHITE, 34),
    # Schatten unter dem Kinn
    flaeche(VL([(946, 800), (1024, 812), (1102, 800), (1104, 850), (1024, 872), (944, 850)]), YEL_D, 45),
    group(*[rille(*r) for r in RILLEN], stroke(YEL_D, 2.4, 90)),
]
put("body", body_shapes, p=(260, BODEN), a=(0, BODEN - RUMPF[1]), animk={"p": body_pos, "s": body_scale})

# ---------- Unterschenkel und Fuesse ----------
BEIN_L = [(830, 1640), (822, 1700), (816, 1730), (800, 1748), (770, 1764), (735, 1778), (708, 1790), (692, 1808),
          (684, 1832), (688, 1852), (705, 1860), (724, 1856), (738, 1868), (762, 1872), (786, 1866), (800, 1874),
          (830, 1876), (862, 1868), (888, 1853), (908, 1830), (922, 1797), (936, 1758), (946, 1715), (948, 1640)]
def bein_formen(sp):
    f = SP if sp else (lambda q: q)
    return [
        form(VL(f(BEIN_L)), BLUE, t=0.45),
        flaeche(VL(f([(948, 1650), (946, 1715), (936, 1758), (922, 1797), (906, 1830), (884, 1853), (870, 1840), (896, 1790),
                      (910, 1730), (912, 1660)])), BLUE_D, 24),
        linien([VL(f([(724, 1856), (746, 1800)])), VL(f([(786, 1866), (806, 1804)]))], BLUE_D, LW * 0.8),
        # Krallen: helle Boegen vorn an den drei Zehen, dazu eine Lichtkante
        linien([VL(f([(694, 1846), (696, 1826), (707, 1812)])), VL(f([(738, 1862), (742, 1840), (754, 1825)])),
                VL(f([(800, 1868), (805, 1844), (818, 1828)])), VL(f([(800, 1752), (760, 1772), (720, 1790)]))], BLUE_L, 1.8),
    ]
put("legs", paarweise(bein_formen(False), bein_formen(True)), parent="body")

# ---------- Schwanz ----------
# Kommt hinter dem rechten Bein hervor, laeuft nach rechts und biegt nach
# oben; oben vier Stacheln, unten ein gelbes Band mit Rillen, am Ende eine
# Pfeilspitze mit zwei Widerhaken.
SCHWANZ = [(1140, 1592), (1230, 1585), (1300, 1572), (1360, 1570), (1420, 1578), (1480, 1586), (1530, 1582), (1575, 1565),
           (1612, 1538), (1640, 1500), (1658, 1458), (1668, 1420), (1680, 1402),
           (1618, 1415), (1640, 1352), (1650, 1282), (1641, 1234), (1628, 1208),   # linker Widerhaken, Spitze
           (1680, 1240), (1730, 1300), (1760, 1370), (1768, 1418), (1716, 1404),   # rechter Widerhaken
           (1734, 1452), (1732, 1510), (1714, 1565), (1685, 1615), (1645, 1660), (1590, 1700),
           (1525, 1732), (1455, 1752), (1380, 1764), (1310, 1762), (1240, 1747), (1180, 1720), (1140, 1690)]
SCHWANZ_SCHARF = tuple(SCHWANZ.index(q) for q in [(1680, 1402), (1618, 1415), (1628, 1208), (1768, 1418), (1716, 1404)])
STACHELN = [[(1316, 1585), (1320, 1505), (1335, 1493), (1370, 1491), (1390, 1500), (1402, 1585)],
            [(1414, 1595), (1462, 1527), (1506, 1596)],
            [(1514, 1596), (1553, 1521), (1596, 1580)],
            [(1596, 1566), (1606, 1488), (1622, 1464), (1655, 1462), (1666, 1505)]]
SCHWANZ_BAUCH = [(1145, 1690), (1180, 1717), (1240, 1744), (1310, 1759), (1380, 1761), (1455, 1749), (1525, 1729), (1588, 1697),
                 (1640, 1658), (1664, 1630), (1622, 1652), (1566, 1684), (1500, 1706), (1430, 1716), (1360, 1716),
                 (1290, 1706), (1220, 1686), (1160, 1664)]
tail_shapes = [
    *[group(smooth(VL(s), tension=0.45), stroke(BLUE_D, LW), fill(BLUE)) for s in STACHELN],
    group(smooth(VL(SCHWANZ), tension=0.5, scharf=SCHWANZ_SCHARF), stroke(BLUE_D, LW), fill(BLUE)),
    flaeche(VL([(1180, 1650), (1300, 1680), (1420, 1696), (1530, 1685), (1610, 1645), (1666, 1580), (1700, 1500), (1712, 1440),
                (1722, 1470), (1712, 1540), (1680, 1610), (1625, 1662), (1560, 1700), (1450, 1740), (1330, 1745), (1220, 1720)]), BLUE_D, 24),
    flaeche(VL([(1636, 1226), (1648, 1282), (1640, 1350), (1630, 1404), (1672, 1398), (1678, 1330), (1670, 1270)]), BLUE_L, 55),
    linie(VL([(1330, 1588), (1420, 1594), (1500, 1601), (1565, 1588), (1608, 1560), (1640, 1520), (1658, 1470), (1666, 1430)]),
          BLUE_L, 1.8),
    form(VL(SCHWANZ_BAUCH), YEL, s=YEL_D, w=2.0),
    linien([VL(l) for l in [[(1250, 1678), (1246, 1722)], [(1330, 1698), (1327, 1744)], [(1410, 1708), (1409, 1752)],
                            [(1490, 1702), (1494, 1740)], [(1560, 1684), (1570, 1712)]]], YEL_D, 1.8, 85),
]
put("tail", tail_shapes, parent="body", p=V(1180, 1650), a=V(1180, 1650), animk={"r": tail_rot})

# ---------- Fluegel ----------
# Wie in der Vorlage: ein kraeftiger Armknochen von der Schulter hinauf zum
# Handgelenk (mit Daumenkralle), von dort die Vorderkante zur aeusseren
# Spitze und zwei Fingerknochen zu den Zacken; dazwischen die Flughaut mit
# drei Boegen am Unterrand, oben dunkler, unten heller.
FLUEGEL_HAUT = [
    (668, 445),
    (650, 428), (610, 442), (570, 456), (530, 473), (490, 492), (450, 514), (410, 538), (370, 568), (330, 601), (290, 640),
    (250, 685), (210, 739), (170, 804), (130, 884), (105, 950), (85, 1030), (72, 1100), (70, 1140),
    (92, 1112), (112, 1076), (132, 1046), (152, 1024), (172, 1010), (200, 1002), (228, 1013), (248, 1048), (266, 1150),
    (290, 1127), (312, 1100), (335, 1080), (365, 1065), (400, 1059), (432, 1066), (462, 1084), (492, 1114), (520, 1158), (552, 1218),
    (575, 1182), (600, 1152), (640, 1124), (690, 1106), (740, 1104), (790, 1098),
    (850, 1060), (885, 990), (880, 940),
    (840, 912), (792, 878), (752, 838), (714, 778), (690, 712), (676, 640), (670, 560), (668, 500)]
FLUEGEL_SCHARF = (18, 27, 37)
FINGER = [
    ([(655, 452), (560, 478), (460, 530), (360, 598), (270, 680), (200, 770), (145, 880), (105, 1000), (76, 1124)],
     [60, 56, 52, 48, 44, 40, 34, 26, 12]),
    ([(568, 520), (470, 700), (370, 920), (268, 1146)], [42, 34, 24, 8]),
    ([(606, 545), (578, 760), (562, 980), (553, 1214)], [42, 34, 24, 8]),
    ([(668, 448), (656, 540), (662, 650), (700, 760), (760, 850), (830, 910), (888, 950)], [62, 58, 56, 56, 58, 60, 62]),
]
def band(mitte, breiten, seite=1):
    """Streifen entlang einer Linie, nur zu einer Seite hin (seite +1: links
    der Laufrichtung im Bild). Fuer die Schatten an den Fingerknochen."""
    rand = []
    for k, q in enumerate(mitte):
        a = mitte[max(k - 1, 0)]; b = mitte[min(k + 1, len(mitte) - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]; l = math.hypot(dx, dy) or 1
        rand.append((q[0] - dy / l * breiten[k] * seite, q[1] + dx / l * breiten[k] * seite))
    return list(mitte) + rand[::-1]
# Die Haut ist an jedem Knochen dunkler, zur Mitte jedes Feldes hin hell -
# in der Vorlage liegt der Schatten jeweils links am naechsten Knochen.
FLUEGEL_SCHATTEN = [
    band(FINGER[1][0], [74, 74, 52, 0]),
    band(FINGER[2][0], [78, 78, 56, 0]),
    band(FINGER[3][0][:6], [60, 84, 96, 96, 84, 60]),
    band(FINGER[0][0][:8], [40, 62, 72, 72, 62, 50, 36, 18], -1),
]
def fluegel_formen(sp):
    f = SP if sp else (lambda q: q)
    teile = [group(smooth(VL(f(FLUEGEL_HAUT)), tension=0.5, scharf=FLUEGEL_SCHARF), stroke(BLUE_D, LW), fill(WING))]
    teile.append(flaechen([VL(f(s)) for s in FLUEGEL_SCHATTEN], WING_D, 100, t=0.45))
    for mitte, breite in FINGER:
        teile.append(group(taper(VL(f(mitte)), [b * K for b in breite], tension=0.5), stroke(BLUE_D, LW), fill(BLUE)))
    teile += [linien([VL(f([(628, 448), (540, 474), (450, 520), (360, 586), (276, 666), (210, 754), (156, 858), (118, 970)])),
                      VL(f([(640, 500), (634, 600), (650, 700), (690, 780), (745, 840)]))], BLUE_L, 1.8),
              # Handgelenk mit Daumenkralle
              group(smooth(VL(f([(626, 446), (656, 424), (704, 424), (750, 446), (708, 458), (676, 472), (640, 470)])),
                           tension=0.45, scharf=(3,)), stroke(BLUE_D, LW), fill(WING))]
    return teile
SCHULTER_FL = (880, 940)
put("wingL", fluegel_formen(False), parent="body", p=V(*SCHULTER_FL), a=V(*SCHULTER_FL),
    animk={"r": wing_rot(1), "s": wing_scale})
put("wingR", fluegel_formen(True), parent="body", p=V(*SP([SCHULTER_FL])[0]), a=V(*SP([SCHULTER_FL])[0]),
    animk={"r": wing_rot(-1), "s": wing_scale})

# ---------- Arme ----------
# Oberarm (armL/armR) dreht in der Schulter, der Unterarm mit der Hand
# (unterarmL/R) haengt daran und dreht im Ellbogen. Der Unterarm hat oben
# eine runde Kappe ohne Umriss, die das Ende des Oberarms zudeckt - so gibt
# es am gestreckten Arm keine Naht.
SCHULTER = (838, 1010); ELLBOGEN = (762, 1190)
def kapsel(a, b, ra, rb, n=7):
    """Geschlossener Umriss um die Strecke a-b mit runden Enden (Radien ra, rb)."""
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    pts = []
    for k in range(n + 1):                       # Halbkreis um b
        t = ang - math.pi / 2 + math.pi * k / n
        pts.append((b[0] + rb * math.cos(t), b[1] + rb * math.sin(t)))
    for k in range(n + 1):                       # Halbkreis um a
        t = ang + math.pi / 2 + math.pi * k / n
        pts.append((a[0] + ra * math.cos(t), a[1] + ra * math.sin(t)))
    return pts
UNTERARM_RAND = [(704, 1190), (694, 1240), (682, 1285), (668, 1322), (650, 1345), (640, 1380), (640, 1420), (643, 1455),
                 (650, 1478), (662, 1490), (673, 1480), (677, 1442), (680, 1474), (688, 1494), (700, 1498), (708, 1486),
                 (709, 1444), (712, 1476), (721, 1491), (732, 1489), (737, 1470), (739, 1432), (745, 1460), (756, 1475),
                 (767, 1467), (771, 1440), (777, 1402), (788, 1372), (791, 1346), (782, 1322), (790, 1280), (806, 1236),
                 (820, 1190)]
UNTERARM_KAPPE = [(813, 1158), (790, 1137), (762, 1131), (734, 1137), (711, 1158)]
UNTERARM_SCHARF = tuple(UNTERARM_RAND.index(q) for q in [(677, 1442), (709, 1444), (739, 1432)])
def oberarm_rand(n=8):
    """Umriss des Oberarms OHNE die Innenseite der Schulterkappe: dort geht
    der Arm in den Rumpf ueber, in der Vorlage ist da keine Linie."""
    ra, rb = 64, 58
    ang = math.atan2(ELLBOGEN[1] - SCHULTER[1], ELLBOGEN[0] - SCHULTER[0])
    def um(c, r, w): return (c[0] + r * math.cos(w), c[1] + r * math.sin(w))
    pts = [um(SCHULTER, ra, math.radians(a)) for a in (-50, -75, -100, -125, -150)]
    pts.append(um(SCHULTER, ra, ang + math.pi / 2))
    pts += [um(ELLBOGEN, rb, ang + math.pi / 2 - math.pi * k / n) for k in range(n + 1)]
    innen = um(SCHULTER, ra, ang - math.pi / 2)
    pts.append((pts[-1][0] + (innen[0] - pts[-1][0]) * 0.55, pts[-1][1] + (innen[1] - pts[-1][1]) * 0.55))
    return pts
def oberarm_formen(sp):
    f = SP if sp else (lambda q: q)
    return [flaeche(VL(f(kapsel(SCHULTER, ELLBOGEN, 64, 58))), BLUE, t=0.55),
            linie(VL(f(oberarm_rand())), BLUE_D, LW, t=0.55),
            linie(VL(f([(800, 990), (776, 1040), (760, 1090), (746, 1150)])), BLUE_L, 1.8)]
# Beim Jubel ballt er die Haende zu Faeusten (Vorlage pro_jubel_vorne.png):
# derselbe Unterarm noch einmal mit Faust statt offener Hand, und je nach
# Stimmung ist das eine oder das andere sichtbar.
FAUST_RAND = [(704, 1190), (694, 1240), (682, 1285), (668, 1322), (652, 1345), (644, 1380), (646, 1414), (660, 1440),
              (690, 1453), (730, 1453), (762, 1442), (784, 1420), (792, 1385), (790, 1350), (782, 1322), (790, 1280),
              (806, 1236), (820, 1190)]
def huelle(teile, o):
    """Formen (von unten nach oben) als eine Gruppe mit eigener Deckkraft."""
    return {"ty": "gr", "it": list(reversed(teile)) + [
        {"ty": "tr", "p": const([0, 0]), "a": const([0, 0]), "s": const([100, 100]), "r": const(0), "o": o}]}
def unterarm_formen(sp):
    f = SP if sp else (lambda q: q)
    rand = VL(f(UNTERARM_RAND)); faust = VL(f(FAUST_RAND))
    licht = linie(VL(f([(704, 1200), (694, 1250), (680, 1300), (662, 1345), (654, 1390)])), BLUE_L, 1.8)
    offen = [group(smooth(rand + VL(f(UNTERARM_KAPPE)), tension=0.5, scharf=UNTERARM_SCHARF), fill(BLUE)),
             group(smooth(rand, closed=False, tension=0.5, scharf=UNTERARM_SCHARF), stroke(BLUE_D, LW)),
             linien([VL(f([(677, 1442), (675, 1412)])), VL(f([(709, 1444), (708, 1412)])), VL(f([(739, 1432), (743, 1404)]))],
                    BLUE_D, LW * 0.8),
             licht]
    geballt = [group(smooth(faust + VL(f(UNTERARM_KAPPE)), tension=0.5), fill(BLUE)),
               group(smooth(faust, closed=False, tension=0.5), stroke(BLUE_D, LW)),
               linien([VL(f([(690, 1453), (688, 1424)])), VL(f([(727, 1453), (726, 1424)])),
                       VL(f([(772, 1360), (752, 1392), (718, 1404), (690, 1400)]))], BLUE_D, LW * 0.8),
               licht]
    return [huelle(offen, opa({"idle", "sad", "ok", "no", "cry", "no_l", "no_r"})), huelle(geballt, opa({"cheer"}))]
put("armL", oberarm_formen(False), parent="body", p=V(*SCHULTER), a=V(*SCHULTER), animk={"r": arm_rot(1), "s": arm_scale})
put("armR", oberarm_formen(True), parent="body", p=V(*SP([SCHULTER])[0]), a=V(*SP([SCHULTER])[0]),
    animk={"r": arm_rot(-1), "s": arm_scale})
# Bild-Drache, 15.10.2026: Der Drehpunkt der Schulter liegt im Bild am
# AUSSENrand des Oberarms. Erhoben (Jubel, Weinen) liegt der Arm darum ganz
# neben dem Koerper, mit einem Streifen Fluegel zwischen Armwurzel und
# Rumpf - er sah angeklebt aus. In diesen beiden Stimmungen rueckt die
# Schulter so viele Einheiten zur Koerpermitte (dx) und nach unten (dy);
# Unterarm und Aermel haengen am Arm und kommen mit.
ARM_RUECK = {"cheer": (9, 2), "cry": (6, 0)}
if not VEKTOR:
    for _n, _sg in (("armL", 1), ("armR", -1)):
        _p0 = built[_n]["ks"]["p"]["k"]

        def _q(dx, dy, p=_p0, sg=_sg): return [round(p[0] + sg * dx, 2), round(p[1] + dy, 2), 0]
        _h = _q(*ARM_RUECK["cheer"])
        built[_n]["ks"]["p"] = spur({"cheer": [(0, _q(0, 0)), (5, _h), (51, _h), (57, _q(0, 0)), (59, _q(0, 0))],
                                     "cry": [(0, _q(*ARM_RUECK["cry"]))]}, _q(0, 0), dims=3)
put("unterarmL", unterarm_formen(False), parent="armL", p=V(*ELLBOGEN), a=V(*ELLBOGEN), animk={"r": unterarm_rot(1)})
put("unterarmR", unterarm_formen(True), parent="armR", p=V(*SP([ELLBOGEN])[0]), a=V(*SP([ELLBOGEN])[0]),
    animk={"r": unterarm_rot(-1)})

# ---------- Kopf ----------
# Rechnet in Hk-Einheiten (siehe oben). Die Ebene sitzt mit dem Halspunkt auf
# dem Hals und wird dort um KOPF vergroessert - Hoerner, Gesicht und alle
# Kopf-Kostueme haengen an ihr und wachsen mit.
KOPF_L = [(1024, 398), (985, 400), (950, 405), (915, 418), (885, 436), (862, 456), (849, 478), (842, 505), (838, 540),
          (833, 580), (826, 615), (819, 645), (816, 670), (818, 692), (826, 712), (842, 735), (868, 758), (905, 785),
          (950, 810), (990, 827), (1024, 833)]
FLOSSE_OBEN = [(850, 492), (833, 484), (814, 472), (799, 460), (786, 450), (776, 446), (775, 470), (777, 495), (781, 514),
               (788, 535), (800, 553), (813, 569), (842, 570)]
FLOSSE_UNTEN = [(840, 566), (813, 569), (800, 576), (787, 584), (778, 593), (773, 600), (776, 606), (784, 612), (796, 618),
                (810, 624), (822, 630), (832, 628)]
HORN_L = [(819, 193), (811, 205), (799, 220), (791, 235), (785, 250), (781, 265), (778, 280), (776, 295), (777, 310),
          (777, 325), (781, 340), (787, 355), (798, 370), (808, 385), (818, 400), (828, 415), (835, 430), (840, 450), (846, 480),
          (900, 470), (955, 420), (948, 400), (943, 385), (934, 370), (927, 355), (915, 340), (898, 325), (876, 310),
          (853, 295), (840, 280), (834, 265), (831, 250), (828, 235), (827, 220), (825, 205)]
HORN_RILLEN = [((790, 256), (825, 253), -9), ((784, 300), (851, 300), -16), ((789, 343), (905, 341), -22), ((814, 386), (933, 388), -22)]
HORN_DUNKEL = [(811, 205), (791, 235), (781, 265), (776, 295), (777, 325), (787, 355), (808, 385), (828, 415), (840, 450),
               (846, 480), (872, 470), (842, 422), (818, 382), (803, 340), (798, 300), (802, 262), (812, 228)]
HORN_HELL = [(826, 215), (832, 255), (846, 285), (876, 312), (912, 338), (935, 365), (945, 395), (926, 372), (898, 347),
             (866, 324), (840, 300), (826, 268), (821, 232)]
STACHEL = [(1022, 326), (1038, 348), (1050, 385), (1051, 425), (1040, 462), (1024, 486), (1008, 462), (997, 425), (998, 385),
           (1008, 348)]
def horn_formen(sp):
    f = SP if sp else (lambda q: q)
    teile = [group(smooth(HL(f(HORN_L)), tension=0.5, scharf=(0,)), stroke(AMBER, LWK * 0.75), fill(YEL)),
             flaeche(HL(f(HORN_DUNKEL)), YEL_D, 45), flaeche(HL(f(HORN_HELL)), WHITE, 35)]
    teile.append(group(*[arc(Hk(*f([a])[0]), Hk(*f([b])[0]), wb * U) for a, b, wb in HORN_RILLEN], stroke(YEL_D, LWK * 0.55, 90)))
    return teile
def kopf_formen(sp_breite=1.0, gesicht_dazu=(), gesicht_tr=None):
    """Hoerner, Ohrflossen, Kopf, Stachel, Schnauze. sp_breite < 1 macht den
    Kopf schmaler (Schaedel des Skeletts). gesicht_dazu: weitere Formen, die
    zum Gesicht gehoeren (die Nasenloecher des Skeletts). gesicht_tr: ein
    Lottie-"tr" - dann stehen Schnauze, Augenpartie, Nasenruecken und
    Nasenloecher in einer eigenen Gruppe mit dieser Bewegung, und das
    Gesicht rueckt gegen den Schaedel: so dreht das Vektor-Skelett den Kopf
    (GESICHT_GEDREHT, 16.10.2026). Ohne gesicht_tr ist alles wie bisher."""
    def sch(pts): return [(round(x * sp_breite, 2), y) for x, y in pts]
    def flossen(sp):
        f = SP if sp else (lambda q: q)
        return [group(smooth(sch(HL(f(FLOSSE_OBEN))), tension=0.45, scharf=(5,)), stroke(BLUE_D, LWK), fill(BLUE)),
                group(smooth(sch(HL(f(FLOSSE_UNTEN))), tension=0.45, scharf=(5,)), stroke(BLUE_D, LWK), fill(BLUE)),
                flaeche(sch(HL(f([(780, 470), (779, 500), (790, 535), (812, 562), (800, 520), (790, 480)]))), BLUE_L, 70)]
    schaedel = paarweise(horn_formen(False), horn_formen(True)) + paarweise(flossen(False), flossen(True)) + [
        group(smooth(sch(HL(SYM(KOPF_L))), tension=0.5), stroke(BLUE_D, LWK), fill(BLUE))]
    gesicht = [
        # Schnauze heller, Kinn und Wangen unten etwas dunkler
        group(ellipse(*Hk(1024, 698), 250 * U * sp_breite, 118 * U), fill(BLUE_L, 32)),
        flaeche(sch(HL([(842, 700), (868, 745), (920, 790), (980, 818), (1024, 824), (1068, 818), (1128, 790), (1180, 745),
                        (1206, 700), (1170, 760), (1100, 800), (1024, 812), (948, 800), (878, 760)])), BLUE_D, 22),
        linie(sch(HL([(866, 476), (859, 505), (855, 540), (850, 580), (843, 615), (837, 645), (835, 672)])), BLUE_L, LWK * 0.5),
        # Augenpartie etwas heller
        group(ellipse(*Hk(1024 - 112 * sp_breite, 562), 126 * U, 128 * U), ellipse(*Hk(1024 + 112 * sp_breite, 562), 126 * U, 128 * U),
              fill(BLUE_L, 30))]
    stachel = [
        # Stachel in der Kopfmitte
        group(smooth(HL(STACHEL), tension=0.5, scharf=(0, 5)), stroke(BLUE_D, LWK * 0.85), fill(BLUE)),
        flaeche(HL([(1020, 336), (1006, 362), (1000, 400), (1004, 440), (1016, 472), (1021, 430), (1022, 380)]), BLUE_L, 70)]
    nase = [
        # Nasenruecken: ein Bogen ueber die Schnauze, der sich an beiden Enden
        # um die Nasenloecher legt; darin je ein tropfenfoermiges Loch
        linie(sch(HL([(952, 700), (947, 682), (957, 664), (985, 651), (1024, 644), (1063, 651), (1091, 664), (1101, 682),
                      (1096, 700)])), BLUE_D, LWK * 0.62),
        flaechen([sch(HL([(962, 680), (978, 674), (990, 686), (986, 702), (971, 707), (962, 696)])),
                  sch(HL(SP([(962, 680), (978, 674), (990, 686), (986, 702), (971, 707), (962, 696)])))], BLUE_D),
    ] + list(gesicht_dazu)
    if gesicht_tr is None:
        return schaedel + gesicht + stachel + nase
    # Der Stachel liegt ueber der Stirn und beruehrt das Gesicht nicht - er
    # darf darunter rutschen. In einer Lottie-Gruppe liegt das erste Stueck
    # oben; put() dreht nur die oberste Liste um, darum hier selbst.
    return schaedel + stachel + [{"ty": "gr", "it": list(reversed(gesicht + nase)) + [gesicht_tr]}]
KOPF_SKALA = round(K / U * KOPF * 100, 3)
# Bis 15.10.2026 hatte der Bild-Drache hier noch head_scale (kurz schmal
# beim Abwenden); seit dem Kopfschuetteln (16.10.2026) steht die Groesse.
put("head", kopf_formen(), parent="body", p=V(*HALS), a=Hk(*HALS), s=KOPF_SKALA,
    animk={"r": head_rot, "p": head_pos})

# Nur die SPITZEN der beiden Hoerner, als Ebene vor den Hueten: ein Hut deckt
# den Hornansatz zu, und es sieht aus, als kaemen die Hoerner oben heraus.
# Ohne Hut liegt die Spitze genau auf dem Horn darunter. Umriss nur an den
# Seiten - die gerade Schnittkante unten bekommt keinen, sonst saehe man sie.
HORN_SPITZE = [(777, 330), (777, 310), (776, 295), (778, 280), (781, 265), (785, 250), (791, 235), (799, 220), (811, 205),
               (819, 193), (825, 205), (827, 220), (828, 235), (831, 250), (834, 265), (840, 280), (853, 295), (876, 310), (905, 330)]
def hornspitze(sp):
    f = SP if sp else (lambda q: q)
    pts = HL(f(HORN_SPITZE))
    teile = [group(smooth(pts, tension=0.5, scharf=(0, 9, len(pts) - 1)), fill(YEL)),
             flaeche(HL(f([(811, 205), (791, 235), (781, 265), (776, 295), (777, 328), (800, 328), (798, 300), (802, 262), (812, 228)])),
                     YEL_D, 45),
             flaeche(HL(f([(826, 215), (832, 255), (846, 285), (876, 312), (895, 328), (866, 324), (840, 300), (826, 268), (821, 232)])),
                     WHITE, 35),
             group(smooth(pts, closed=False, tension=0.5, scharf=(9,)), stroke(AMBER, LWK * 0.75))]
    teile.append(group(*[arc(Hk(*f([a])[0]), Hk(*f([b])[0]), wb * U) for a, b, wb in HORN_RILLEN[:2]], stroke(YEL_D, LWK * 0.55, 90)))
    return teile
put("hoerner", paarweise(hornspitze(False), hornspitze(True)), parent="head")

# ---------- Augen ----------
# Weiss fest, darueber eine bewegliche Gruppe aus Iris, Pupille und Glanz.
# Wichtig: in einer Lottie-Gruppe faerbt eine Fuellung alle folgenden Formen
# mit, darum bekommt jede Form ihre eigene Untergruppe.
AUGE = (918, 584); AUGE_B, AUGE_H = 92, 102
def auge_oben(cx, cy, w, h, n=9):
    """Obere Haelfte des Augenumrisses - darauf liegt der kraeftigere Lidstrich."""
    return [(cx + w / 2 * math.cos(math.pi + math.pi * k / n), cy + h / 2 * math.sin(math.pi + math.pi * k / n)) for k in range(n + 1)]
def augen_formen():
    weiss, beweglich = {}, {}
    for sp in (False, True):
        f = SP if sp else (lambda q: q)
        c = Hk(*f([AUGE])[0])
        weiss[sp] = [group(ellipse(c[0], c[1], AUGE_B * U, AUGE_H * U), stroke(BLUE_D, 8 * U), fill(WHITE)),
                     linie([(x, y) for x, y in auge_oben(c[0], c[1], AUGE_B * U, AUGE_H * U)], BLUE_D, 12 * U, t=0.4)]
        i = Hk(*f([(928, 596)])[0]); pu = Hk(*f([(930, 600)])[0])
        g1 = Hk(*f([(913, 572)])[0]); g2 = Hk(*f([(944, 620)])[0])
        beweglich[sp] = [group(ellipse(g2[0], g2[1], 10 * U, 10 * U), fill(WHITE, 85)),
                         group(ellipse(g1[0], g1[1], 24 * U, 24 * U), fill(WHITE)),
                         group(ellipse(pu[0], pu[1], 32 * U, 42 * U), fill(PUPILLE)),
                         group(ellipse(i[0], i[1] + 13 * U, 46 * U, 30 * U), fill(WHITE, 16)),
                         group(ellipse(i[0], i[1], 62 * U, 72 * U), stroke(IRIS_D, 4 * U), fill(IRIS))]
    return paarweise(weiss[False], weiss[True]), paarweise(beweglich[False], beweglich[True])
_weiss, _beweglich = augen_formen()
put("eyes", _weiss + [{"ty": "gr", "it": _beweglich + [
        {"ty": "tr", "p": pupil_pos, "a": const([0, 0]), "s": const([100, 100]), "r": const(0), "o": const(100)}]}],
    parent="head", animk={"o": opa({"idle", "sad", "ok", "no", "no_l", "no_r"})})
# Lider: je eine Ellipse wie das Auge, von der Oberkante her aufgezogen. Eine
# Maske in Augenform schneidet ab, was seitlich uebersteht - sonst saehe man
# den Lidstrich neben dem Auge.
def lider():
    # Beide Lider in EINER Gruppe: sie werden nur in der Hoehe gestaucht, und
    # beide Augen haben dieselbe Oberkante - ein Anker auf dieser Hoehe reicht.
    pfade, masken = [], []
    for sp in (False, True):
        f = SP if sp else (lambda q: q)
        c = Hk(*f([AUGE])[0])
        pfade.append(ellipse(c[0], c[1], AUGE_B * U, AUGE_H * U))
        masken.append(ellipse_pfad(c[0], c[1], (AUGE_B + 9) * U, (AUGE_H + 9) * U))
    oben = (0, Hk(*AUGE)[1] - AUGE_H * U / 2)
    return [{"ty": "gr", "it": pfade + [stroke(BLUE_D, 9 * U), fill(BLUE),
                                        {"ty": "tr", "p": const(list(oben)), "a": const(list(oben)), "s": lids_scale,
                                         "r": const(0), "o": const(100)}]}], masken
_lid, _maske = lider()
put("lids", _lid, parent="head", masken=_maske)
def zu_augen(bogen_unten):
    """Geschlossene Augen als Boegen: oben gewoelbt (Freude) - beim Weinen
    zusaetzlich zusammengekniffen mit einem Strich darunter."""
    teile = {}
    for sp in (False, True):
        f = SP if sp else (lambda q: q)
        teile[sp] = [linie(HL(f([(878, 602), (897, 579), (918, 571), (939, 579), (958, 602)])), BLUE_D, 12 * U)]
        if bogen_unten:
            teile[sp] += [linie(HL(f([(884, 606), (918, 598), (952, 606)])), BLUE_D, 7 * U),
                          group(ellipse(*Hk(*f([(918, 616)])[0]), 64 * U, 16 * U), fill(TEAR, 85))]
    return paarweise(teile[False], teile[True])
put("eyes_happy", zu_augen(False), parent="head", animk={"o": opa({"cheer"})})
put("eyes_cry", zu_augen(True), parent="head", animk={"o": opa({"cry"})})

# ---------- Brauen ----------
BRAUE = [(872, 508), (890, 484), (913, 471), (940, 477)]; BRAUE_MITTE = (906, 486)
def braue(sp):
    f = SP if sp else (lambda q: q)
    m = Hk(*f([BRAUE_MITTE])[0])
    return {"ty": "gr", "it": [smooth(HL(f(BRAUE)), closed=False, tension=0.5), stroke(BLUE_D, 13 * U),
                               {"ty": "tr", "p": brow_pos(m), "a": const(list(m)), "s": const([100, 100]),
                                "r": brow_rot(-1 if sp else 1), "o": const(100)}]}
put("brows", [braue(False), braue(True)], parent="head")

# ---------- Muender ----------
put("mouth_idle", [linie(HL([(880, 672), (893, 690), (950, 733), (1024, 752), (1098, 733), (1155, 690), (1168, 672)]), BLUE_D, 10 * U)],
    parent="head", animk={"o": opa({"idle"})})
MUND_AUF = [(898, 700), (960, 722), (1024, 728), (1088, 722), (1150, 700), (1132, 740), (1095, 778), (1060, 798), (1024, 803),
            (988, 798), (953, 778), (916, 740)]
MUND_OBEN = Hk(1024, 715)
put("mouth_open", [
    group(smooth(HL(MUND_AUF), tension=0.5, scharf=(0, 4)), fill(RED)),
    group(smooth(HL([(962, 792), (990, 772), (1024, 767), (1058, 772), (1086, 792), (1060, 800), (1024, 803), (988, 800)]), tension=0.5),
          fill(TONGUE)),
    group(poly(HL([(928, 711), (944, 744), (958, 719)])), fill(WHITE)),
    group(poly(HL([(1090, 719), (1104, 744), (1120, 711)])), fill(WHITE)),
    group(smooth(HL(MUND_AUF), tension=0.5, scharf=(0, 4)), stroke(BLUE_D, 9 * U)),
    linie(HL([(884, 686), (898, 700)]), BLUE_D, 8 * U), linie(HL([(1164, 686), (1150, 700)]), BLUE_D, 8 * U),
], parent="head", p=MUND_OBEN, a=MUND_OBEN, animk={"o": opa({"cheer", "ok"}), "s": mouth_open_scale})
put("mouth_sad", [linie(HL([(952, 762), (988, 742), (1024, 736), (1060, 742), (1096, 762)]), BLUE_D, 10 * U)],
    parent="head", animk={"o": opa({"sad", "no", "no_l", "no_r"})})
MUND_WEIN = [(930, 742), (975, 728), (1024, 734), (1073, 728), (1118, 742), (1100, 772), (1062, 792), (1024, 797), (986, 792), (948, 772)]
MUND_WEIN_OBEN = Hk(1024, 735)
put("mouth_cry", [
    group(smooth(HL(MUND_WEIN), tension=0.5, scharf=(0, 4)), fill(RED)),
    group(ellipse(*Hk(1024, 784), 70 * U, 22 * U), fill(TONGUE)),
    group(poly(HL([(946, 737), (956, 760), (968, 733)])), fill(WHITE)),
    group(poly(HL([(1080, 733), (1092, 760), (1102, 737)])), fill(WHITE)),
    group(smooth(HL(MUND_WEIN), tension=0.5, scharf=(0, 4)), stroke(BLUE_D, 9 * U)),
], parent="head", p=MUND_WEIN_OBEN, a=MUND_WEIN_OBEN, animk={"o": opa({"cry"}), "s": mouth_cry_scale})

# ---------- Traenen ----------
drop = smooth([(0, -12), (7, 0), (0, 9), (-7, 0)], tension=0.7)
tears_shapes = []
for k, (start, x0, y0, dx) in enumerate([(0, *Hk(874, 606), -8), (18, *Hk(1174, 606), 8), (30, *Hk(880, 612), -12), (9, *Hk(1168, 612), 12)]):
    _ort, _deck = traene(start, x0, y0, dx)
    tears_shapes.append({"ty": "gr", "it": [drop, fill(TEAR, 90),
                                            {"ty": "tr", "p": _ort, "a": const([0, 0]), "s": const([80, 80]),
                                             "r": const(0), "o": _deck}]})
put("tears", tears_shapes, parent="head")


# ======================= Kostueme (Zierrat) =======================
# v6, 14.10.2026: Die Stuecke unten sind fuer den Drachen v5 gebaut und hier
# unveraendert uebernommen - bis auf das Skelett, das die neue Anatomie
# braucht (stehend, Arm mit Ellbogen). Die Kopfstuecke rechnen in denselben
# Kopf-Einheiten wie v5 (Kopf 156 breit, Scheitel bei -128) und wachsen mit
# dem Kopf; die Brillen sitzen aber noch auf der v5-Augenhoehe (y = -74,
# Augen bei +-32; v6: y = -57, Augen bei +-40), und die Halssachen und Aermel
# noch auf dem sitzenden v5-Rumpf (v6: Hals bei y = -128, Schultern -82,
# Rumpf +-48 breit). Das Anpassen ist ein eigener Schritt.
#
# 15.10.2026, dieser Schritt: alle Stuecke sitzen jetzt auf der Figur v6.
#   - Kopfstuecke in Kopf-Einheiten (Hk), abgemessen am v6-Kopf: Scheitel
#     y = -128, Brauen -86 bis -100, Augen bei x = +-40.5 / y = -57 (35 x 39
#     gross), Ohrflossen x = -66..-96 / y = -110..-40, Hornansatz x = +-26..+-68
#     bei y = -97..-120, Hornspitzen bis -206. Huete enden unten bei etwa
#     -98, damit die Brauen sichtbar bleiben, und decken die Hornansaetze zu -
#     die Hoerner kommen seitlich bzw. oben heraus ("hoerner" liegt vorn).
#   - Oben ist bei Variante A wenig Platz: im Jubelsprung (22 Punkte hoch
#     und 104 % gestreckt) schneidet die Leinwand alles ab, was hoeher als
#     etwa y = -220 liegt. Kein Kopfstueck geht darueber.
#   - Koerperstuecke (Hals, Kleidung, Aermel) stehen wie der Drache selbst
#     in Pixeln der Vorlage pro_vorne.png und gehen ueber VL() auf die
#     Leinwand - so folgen sie genau seinem Umriss.
#   - Jedes Stueck hat jetzt einen Umriss in seinem eigenen dunklen Ton, wie
#     die Figur (Stil "Entwurf 1"); flach aufgelegt sah es aufgeklebt aus.
# ======================= Kopfsachen =======================
# v5: Alle sitzen mit ihrem unteren Rand zwischen y = -96 und -104. Dort ist
# der Schädel 59 bis 66 breit (Mittelpunkt 0/-60, Halbachsen 78 und 68), und
# nur so breit dürfen sie sein. Vorher saßen sie bei -124, wo der Schädel
# noch +-31 misst - deshalb hingen sie in der Luft.
# v6: Der Schaedel ist oben schmaler und runder (bei y = -100 etwa +-66, bei
# -120 etwa +-42). Die Stuecke sind etwas breiter als er, sonst saessen sie
# wie aufgemalt, und sitzen mit dem unteren Rand bei -96 bis -100.
KLW = round(LWK * 0.7, 2)          # Umriss der Kopfstuecke (Kopf-Einheiten)
def hoeher(dy, teile):
    """Ein Kopfstueck als Ganzes um dy verschieben (negativ = hoeher).
    v6, 15.10.2026: Mit dem unteren Rand bei -98 lagen die Brauen in der
    Ruhe gerade noch frei, aber traurig (innen hoch) und beim Jubel
    (ganz hoch) verschwanden sie unter dem Hut - und mit ihnen ein guter
    Teil der Stimmung. Darum sitzen alle Huete und Kronen 5 bis 7
    Einheiten hoeher; die Zahlen in den Stuecken sind die vor dem
    Verschieben. Innerhalb einer Gruppe liest Lottie von oben nach unten -
    put() dreht nur die aeussere Liste um, also hier selbst umdrehen."""
    return [group(*reversed(teile), p=(0, dy))]
HUT_U = col("6E1A12"); KRONE_U = col("9A7400"); FES_U = col("4E0A0A"); KAPPE_U = col("0B3820")
DOKTOR_U = col("0E0F12"); WOLLE_U = col("5E160E"); KH_U = col("121212")

# ---------- Bommelmütze ----------
# v6: Umschlag von -96 auf -116 hoch (er lag auf den Brauen; Zahlen unten
# plus hoeher()), Muetze und Bommel mit; Bommel oben bei -209, unter der
# Schnittkante im Jubelsprung.
put("hut", hoeher(-6, [
    form([(-70, -106), (-64, -150), (-30, -176), (0, -181), (30, -176), (64, -150), (70, -106)], HUT, HUT_U, KLW, t=0.55),
    group(rect(0, -124, 140, 8, 4), fill(HUT_D, 22)),                 # Schatten ueber dem Umschlag
    group(smooth([(-34, -134), (-14, -162), (8, -174)], closed=False, tension=0.5), stroke(HUT_D, 5, 38)),
    group(rect(0, -110, 150, 24, 12), stroke(HUT_U, KLW), fill(HUT_HELL)),    # Umschlag
    group(ellipse(0, -186, 32, 32), stroke(HUT_U, KLW), fill(HUT_HELL)),     # Bommel
]), parent="head")

# ---------- Krone ----------
# v6: 17 Einheiten hoeher, damit der Reif ueber den Brauen sitzt; die
# Zacken liegen hinter dem Reif, beide mit dunkelgoldenem Umriss.
_KRONE_ZACKEN = [(-64, -110), (-64, -162), (-40, -138), (-20, -174), (0, -140), (20, -174), (40, -138), (64, -162), (64, -110)]
put("krone", hoeher(-5, [
    group(smooth(_KRONE_ZACKEN, tension=0.12), stroke(KRONE_U, KLW), fill(KRONE)),
    group(rect(0, -112, 132, 22, 6), stroke(KRONE_U, KLW), fill(KRONE)),     # Reif
    group(rect(0, -105, 128, 6, 3), fill(KRONE_D, 35)),
    group(ellipse(-20, -174, 15, 15), stroke(KRONE_U, 2), fill(STEIN)),
    group(ellipse(20, -174, 15, 15), stroke(KRONE_U, 2), fill(STEIN)),
    group(ellipse(0, -140, 13, 13), stroke(KRONE_U, 2), fill(STEIN)),
]), parent="head")

# ---------- Grosse Krone (nur Vollversion) ----------
# Dieselbe Bauart wie die kleine, nur hoeher, breiter und mit einem
# grossen Stein in der Mitte. Sie muss sich auf einen Blick von der
# kleinen unterscheiden - sonst fragt sich jeder, wofuer er zahlt.
# v6: Reif 17 Einheiten hoeher und etwas schmaler; die Perlen oben
# bleiben bei -207, unter der Schnittkante im Jubelsprung (Variante A).
_KRONE_GR_ZACKEN = [(-72, -112), (-72, -176), (-48, -146), (-29, -194), (0, -154), (29, -194), (48, -146), (72, -176), (72, -112)]
put("krone_gross", hoeher(-5, [
    group(smooth(_KRONE_GR_ZACKEN, tension=0.1), stroke(KRONE_U, KLW), fill(KRONE)),   # fuenf Zacken
    group(rect(0, -116, 148, 30, 9), stroke(KRONE_U, KLW), fill(KRONE)),     # Reif
    group(rect(0, -105, 144, 8, 4), fill(KRONE_D, 40)),               # Schatten unten am Reif
    group(rect(0, -126, 144, 6, 3), fill(PERLE, 55)),                 # helle Kante oben
    group(ellipse(0, -116, 28, 28), stroke(KRONE_U, 2.5), fill(STEIN)),       # grosser Stein
    group(ellipse(-6, -122, 9, 9), fill(PERLE, 60)),                  # Glanzpunkt darauf
    group(ellipse(-29, -194, 15, 15), stroke(KRONE_U, 2), fill(PERLE)),
    group(ellipse(29, -194, 15, 15), stroke(KRONE_U, 2), fill(PERLE)),
    group(ellipse(-72, -176, 12, 12), stroke(KRONE_U, 2), fill(STEIN)),
    group(ellipse(72, -176, 12, 12), stroke(KRONE_U, 2), fill(STEIN)),
]), parent="head")

# ---------- Fes ----------
# v6: unten bei -105 statt -96 (Brauen), oben bei -183.
def fes_formen(rot, rot_d, rot_u, quaste, quaste_d):
    return [
        group(smooth([(-60, -100), (-50, -178), (50, -178), (60, -100)], tension=0.06), stroke(rot_u, KLW), fill(rot)),
        group(ellipse(0, -178, 100, 18), stroke(rot_u, KLW * 0.7), fill(rot_d)),     # Deckel von leicht oben
        group(rect(0, -105, 116, 9, 4), fill(rot_d, 28)),
        group(smooth([(8, -180), (44, -164), (58, -134)], closed=False, tension=0.5), stroke(quaste_d, 5)),
        group(rect(60, -120, 15, 30, 7), fill(quaste)),               # Quaste haengt neben dem Hut
        group(rect(60, -106, 15, 7, 3), fill(quaste_d)),
    ]
put("fes", hoeher(-5, fes_formen(FES, FES_D, FES_U, QUASTE, QUASTE)), parent="head")

# ---------- Kappe, verkehrt herum ----------
# v6: 14 bis 18 Einheiten hoeher, Bund bei -113 (vorher -98, auf den Brauen).
put("kappe", hoeher(-6, [
    form([(-68, -104), (-58, -150), (0, -172), (58, -150), (68, -104)], KAPPE, KAPPE_U, KLW, t=0.6),
    group(smooth([(-30, -112), (-16, -152), (0, -168)], closed=False, tension=0.5), stroke(KAPPE_D, 4, 42)),
    group(smooth([(30, -112), (16, -152), (0, -168)], closed=False, tension=0.5), stroke(KAPPE_D, 4, 42)),
    group(ellipse(0, -170, 14, 14), stroke(KAPPE_U, 2), fill(KAPPE_D)),
    group(rect(0, -107, 142, 19, 9), stroke(KAPPE_U, KLW * 0.8), fill(KAPPE_D)),   # Bund
    group(rect(0, -107, 46, 13, 6), fill(KAPPE_H)),                   # Verschlussriemen
    group(ellipse(-10, -107, 6, 6), fill(KAPPE_D)),
    group(ellipse(10, -107, 6, 6), fill(KAPPE_D)),
]), parent="head")

# ---------- Doktorhut ----------
# v6: Kappe unten bei -105, Brett elf Einheiten hoeher.
put("doktorhut", hoeher(-5, [
    group(smooth([(-60, -100), (-55, -138), (55, -138), (60, -100)], tension=0.1), stroke(DOKTOR_U, KLW), fill(DOKTOR)),
    group(rect(0, -105, 124, 10, 5), fill(DOKTOR_H, 40)),
    group(poly([(-104, -142), (0, -176), (104, -142), (0, -110)]), stroke(DOKTOR_U, KLW), fill(DOKTOR)),   # Brett
    group(poly([(-98, -142), (0, -172), (98, -142), (0, -113)]), stroke(DOKTOR_H, 2.5, 50)),
    group(ellipse(0, -142, 15, 15), fill(GOLDR)),
    group(smooth([(0, -142), (56, -136), (90, -124)], closed=False, tension=0.5), stroke(GOLDR, 5)),
    group(rect(92, -106, 13, 34, 6), fill(GOLDR)),                    # Quaste
]), parent="head")

# ---------- Ohrenschützer ----------
# Neu gezeichnet: ein schmaler Bügel und zwei satte, runde Polster mit hellem
# Kern. Die gezackte "Fell"-Kontur von vorher sah aus wie zwei Blumen.
# v6: Die Polster sitzen jetzt auf den Ohrflossen (x = -66..-96,
# y = -110..-40) statt halb auf den Augen; der Buegel liegt eng am Schaedel
# und quert die Hornansaetze unterhalb von -154 - darueber liegen die
# Hornspitzen vorn, und der Buegel saehe zerschnitten aus.
OHR_MITTE = (-85, -76)
_BUEGEL = [(-84, -100), (-72, -124), (-44, -142), (0, -149), (44, -142), (72, -124), (84, -100)]
put("ohrenschuetzer", [
    group(smooth(_BUEGEL, closed=False, tension=0.55), stroke(WOLLE_U, 13)),
    group(smooth(_BUEGEL, closed=False, tension=0.55), stroke(WOLLE_D, 8)),
    group(smooth([(-74, -118), (-46, -138), (-10, -146)], closed=False, tension=0.5), stroke(WOLLE, 3.5, 55)),
    # Kein heller Kern mehr: mit Kern lasen sich die Polster wie ein zweites
    # Augenpaar. Jetzt satte Wolle, ein weicher Schatten und ein kleiner
    # Glanz oben links - das liest sich als weiches Kissen.
    *paarweise([group(ellipse(*OHR_MITTE, 48, 62), stroke(WOLLE_U, KLW), fill(WOLLE)),
                group(ellipse(OHR_MITTE[0], OHR_MITTE[1] + 8, 38, 40), fill(WOLLE_D, 40))],
               [group(ellipse(-OHR_MITTE[0], OHR_MITTE[1], 48, 62), stroke(WOLLE_U, KLW), fill(WOLLE)),
                group(ellipse(-OHR_MITTE[0], OHR_MITTE[1] + 8, 38, 40), fill(WOLLE_D, 40))]),
    # Gedreht um die eigene Mitte (p=), nicht um den Kopfmittelpunkt: bis
    # 15.10.2026 stand die Ellipse bei (-93,-92) mit r=-20 um (0, 0) - der
    # linke Glanz landete bei (-119,-55) und schwebte neben dem Polster, der
    # rechte sass halb auf dem Rand (Pruefung 15.10.2026). Beide oben links
    # auf ihrem Polster, das Licht kommt von links oben.
    group(ellipse(0, 0, 14, 10), fill(FELL, 40), r=-20, p=(OHR_MITTE[0] - 9, OHR_MITTE[1] - 17)),
    group(ellipse(0, 0, 14, 10), fill(FELL, 40), r=-20, p=(-OHR_MITTE[0] - 9, OHR_MITTE[1] - 17)),
], parent="head")

# ---------- Kopfhörer ----------
# Auch neu: Bügel mit Polster oben, Muscheln mit Ring und Glanz statt zweier
# flacher Ellipsen.
# v6: Muscheln auf den Ohrflossen, Buegel eng am Schaedel wie beim
# Ohrenschuetzer.
_KH_BUEGEL = [(-86, -98), (-72, -126), (-44, -145), (0, -152), (44, -145), (72, -126), (86, -98)]
put("kopfhoerer", [
    group(smooth(_KH_BUEGEL, closed=False, tension=0.55), stroke(KH, 12)),
    group(smooth([(-32, -147), (0, -152), (32, -147)], closed=False, tension=0.5), stroke(KH_HELL, 7, 70)),
    *paarweise([group(rect(-86, -102, 14, 24, 6), fill(KH)),                   # Aufhaengung
                group(rect(-87, -74, 42, 60, 18), stroke(KH_U, KLW * 0.8), fill(KH)),   # Muschel
                group(rect(-87, -74, 28, 44, 12), fill(KH_POLSTER))],          # Polster
               [group(rect(86, -102, 14, 24, 6), fill(KH)),
                group(rect(87, -74, 42, 60, 18), stroke(KH_U, KLW * 0.8), fill(KH)),
                group(rect(87, -74, 28, 44, 12), fill(KH_POLSTER))]),
    group(ellipse(-92, -88, 8, 12), fill(WHITE, 30)),
    group(ellipse(82, -88, 8, 12), fill(WHITE, 30)),
], parent="head")

# ======================= Brillen =======================
# Unveraendert - die gefielen.
# v6, 15.10.2026: Form wie gehabt, aber auf die neuen Augen gesetzt - sie
# sitzen bei x = +-40.5, y = -57 statt +-32 / -74 und sind 35 x 39 gross.
# Die Buegel laufen zu den Ohrflossen (Schaedelrand bei y = -66 etwa +-72).
AUG_X, AUG_Y = round(Hk(*AUGE)[0], 1), round(Hk(*AUGE)[1], 1)        # -40.5, -56.9

# ---------- Runde Brille ----------
put("brille", [
    group(smooth([(-63, -63), (-69, -66), (-75, -70)], closed=False, tension=0.5), stroke(RAHMEN, 4.5)),
    group(smooth([(63, -63), (69, -66), (75, -70)], closed=False, tension=0.5), stroke(RAHMEN, 4.5)),
    group(arc((-17, -61), (17, -61), -5), stroke(RAHMEN, 4.5)),        # Steg
    group(ellipse(AUG_X, AUG_Y, 47, 47), stroke(RAHMEN, 5), fill(GLAS, 28)),
    group(ellipse(-AUG_X, AUG_Y, 47, 47), stroke(RAHMEN, 5), fill(GLAS, 28)),
], parent="head")

# ---------- Sterne fuer die Galaxie-Haut (nur Vollversion) ----------
# Ein vierzackiger Stern: schmale Spitzen, dazwischen eingezogen. Ueber
# poly(), damit die Spitzen wirklich spitz bleiben - smooth() wuerde
# runde Blasen daraus machen.
def stern(cx, cy, r, c, o=100):
    e = r * 0.26
    return group(poly([(cx, cy - r), (cx + e, cy - e), (cx + r, cy), (cx + e, cy + e),
                       (cx, cy + r), (cx - e, cy + e), (cx - r, cy), (cx - e, cy - e)]),
                 fill(c, o))

# Ein Stern, der an seinem Platz aufblitzt. Der Stern selbst steht auf
# (0,0) und wird erst durch die Verschiebung der Gruppe gesetzt - nur so
# waechst er um seine eigene Mitte. Legte man ihn gleich auf (cx,cy),
# zoege ihn jede Groessenaenderung zur Bildmitte hin.
#   platz   Nummer des Sterns, 0 bis anzahl-1 - bestimmt, wann er dran ist
#   anzahl  wie viele Sterne sich den Abschnitt teilen
#
# Wichtig: die App spielt nie die ganze Zeitleiste. playMood() ruft
# playSegments() mit einem Abschnitt aus SEG - im Ruhezustand die Bilder 0
# bis 90, in Schleife. Ein Takt ueber die ganze Datei liesse die meisten
# Blitze nie fallen und schnitte die spaeten Sterne an der Abschnittsgrenze
# mitten im Leuchten ab. Deshalb bekommt jeder Stern in JEDEM Abschnitt
# genau einen Blitz, und der ist vor der Grenze zu Ende.
# Eigenes Gelb fuer die Funken: YEL tauscht die Skelettfarbe zu Halloween
# mit aus, die gekauften Funken waeren dann knochenfarben (Gegenpruefung
# 01.10.2026). Mindestens 2/255 Abstand in einem Kanal, sonst zaehlt es
# in faerbe() noch als YEL.
FUNKE_GELB = col("FFCE22")
def funke_zeit(platz, anzahl=7, o=100):
    """Keyframes eines Sterns: (Groesse, Deckkraft, Drehung), je eine Liste
    (Bild, Wert). Seit 16.10.2026 eigene Funktion: die gemalten Sterne
    (GEMALTE_FUNKEN) blitzen genauso wie die Vektorsterne."""
    # Bild, Groesse, Deckkraft, Drehung. Schnell auf, langsam wieder weg -
    # so blitzt es, statt zu pulsieren. 26 Bilder, damit auch die kurzen
    # Abschnitte (ok und no sind nur 30 lang) noch einen ganzen Blitz fassen.
    DAUER = 26
    schritte = [(0, 0, 0, -35), (6, 124, o, -8), (15, 96, o, 0), (DAUER, 0, 0, 10)]
    gs, go, gr = [], [], []
    # Nur die langen Abschnitte. In den kurzen Reaktionen (ok und no sind je
    # 30 Bilder, no_l und no_r je 40) blieben nach Abzug der Blitzdauer so
    # wenige Bilder uebrig, dass alle sieben Sterne fast gleichzeitig
    # losgingen - das sieht nach einem einzigen Blinzeln aus und kostete die
    # Haelfte der Dateigroesse. Dort funkelt jetzt nichts; die Reaktion
    # dauert eine Sekunde, danach ist ohnehin wieder Ruhezustand.
    for a, e in sorted(SEG.values()):
        fenster = (e - a) - DAUER
        if e - a < 50:
            continue                      # zu kurz fuer sieben gestaffelte Blitze
        start = a + (fenster * platz) // max(1, anzahl - 1)
        for dt, sv, ov, rv in schritte:
            k = start + dt
            gs.append((k, sv)); go.append((k, ov)); gr.append((k, rv))
    return gs, go, gr


def funke(cx, cy, r, c, platz, anzahl=7, o=100):
    gs, go, gr = funke_zeit(platz, anzahl, o)
    gs = [(k, [sv, sv]) for k, sv in gs]
    e = r * 0.26
    zeiger = {"ty": "tr", "p": const([cx, cy]), "a": const([0, 0]),
              "s": anim(gs, dims=2), "r": anim(gr), "o": anim(go)}
    return {"ty": "gr", "it": [
        poly([(0, -r), (e, -e), (r, 0), (e, e), (0, r), (-e, e), (-r, 0), (-e, -e)]),
        fill(c), zeiger]}

# Die Sterne sitzen auf dem Bauch und den Schenkeln - dort, wo bei der
# Umfaerbung die dunkle Flaeche liegt. Verschiedene Groessen, damit es
# nach Sternenhimmel aussieht und nicht nach Punktmuster.
# v6, 15.10.2026: Der Bauch bleibt gelb, und die Sterne darauf gingen unter.
# Jetzt liegen sie auf der dunklen Haut: Schenkel, Unterschenkel, neben dem
# Bauch und am Hals - und, als eigene Ebenen, die mit Fluegeln und Schwanz
# mitgehen, auch auf der Flughaut und dem Schwanz. Punkte in Pixeln der
# Vorlage; Groessen in Koerper-Einheiten (Punkt: Durchmesser, Stern: Radius).
def himmel(liste, f=lambda q: q):
    """liste: (art, x, y, groesse, deckkraft) mit art 'p' Punkt, 's' Stern."""
    teile = []
    for art, x, y, g, o in liste:
        cx, cy = V(*f([(x, y)])[0])
        teile.append(stern(cx, cy, g, WHITE, o) if art == "s" else group(ellipse(cx, cy, g, g), fill(WHITE, o)))
    return teile
put("galaxie", himmel([
    ("s", 800, 1575, 7.5, 95), ("p", 852, 1650, 3.6, 85), ("p", 804, 1668, 3, 70), ("p", 884, 1515, 2.8, 75),
    ("s", 1256, 1602, 6.5, 90), ("p", 1212, 1668, 3.6, 80), ("p", 1284, 1520, 2.8, 70),
    ("p", 893, 975, 2.8, 75), ("p", 1152, 1012, 2.8, 70), ("p", 1135, 1120, 2.2, 60),
    ("p", 922, 846, 2.6, 65), ("p", 1128, 832, 2.4, 60),
    ("p", 790, 1822, 3, 70), ("s", 1262, 1792, 5, 85), ("p", 900, 1780, 2.4, 60),
]), parent="body")
# 15.10.2026, Bild-Drache mit Galaxie-Haut: der Punkt am linken Schenkel
# stand bei (778, 1668) genau auf dem Umriss des Rumpfbilds und ragte halb
# ueber den Rand - auf dunklem Grund ein heller Fleck neben dem Bein. Um 26
# Vorlagen-Pixel nach innen geschoben (804, 1668), in allen Stimmungen
# geprueft: kein Sternpixel mehr ausserhalb des Drachen.
_STERNE_FLUEGEL = [("s", 330, 800, 6, 90), ("p", 450, 680, 3.2, 80), ("p", 210, 930, 2.8, 70), ("p", 470, 900, 3.2, 75),
                   ("s", 420, 1010, 4.6, 85), ("p", 560, 700, 2.6, 65), ("p", 300, 1030, 2.4, 60), ("p", 600, 960, 2.8, 70),
                   ("p", 640, 600, 2.2, 60)]
_STERNE_FLUEGEL_R = [("s", 360, 760, 5.4, 90), ("p", 470, 650, 3.2, 80), ("p", 230, 900, 2.8, 70), ("p", 500, 930, 3.2, 75),
                     ("s", 380, 1000, 5, 85), ("p", 590, 760, 2.6, 65), ("p", 270, 1050, 2.4, 60), ("p", 610, 1050, 2.8, 70),
                     ("p", 150, 960, 2.2, 60)]
put("galaxie_wingL", himmel(_STERNE_FLUEGEL), parent="wingL")
put("galaxie_wingR", himmel(_STERNE_FLUEGEL_R, SP), parent="wingR")
put("galaxie_schwanz", himmel([("p", 1330, 1640, 2.6, 75), ("s", 1450, 1640, 4.6, 90), ("p", 1560, 1610, 2.6, 70),
                               ("p", 1640, 1525, 3, 75), ("p", 1690, 1462, 2.2, 65), ("s", 1700, 1335, 4, 85)]),
    parent="tail")

# ---------- Funkeln (nur Vollversion) ----------
# Sieben Sterne rund um den Drachen. Jeder steht still und blitzt einmal
# je Stimmungsabschnitt auf, der Reihe nach - so leuchtet immer irgendwo
# einer und nie alle zugleich. Im Ruhezustand sind das 90 Bilder, also
# drei Sekunden fuer alle sieben. Sie haengen am Koerper, wippen mit ihm.
# Ajdin am 29.09.2026: die Sterne sollen nicht kreisen, sondern funkeln.
# v6, 15.10.2026: neue Plaetze. Der stehende Drache fuellt mit Fluegeln und
# Kopf fast die ganze Leinwand; die alten Plaetze lagen auf Kopf, Fluegeln
# und Schwanz. Jetzt: ueber den Fluegeln neben dem Kopf, links und rechts
# unter den Fluegelspitzen, neben dem linken Fuss und unter dem Schwanz -
# alle mindestens 20 Punkte von der Figur und vom Rand entfernt, auch im
# Jubelsprung.
# 16.10.2026: Die Plaetze stehen in FUNKEN, weil die gemalten Sterne
# (GEMALTE_FUNKEN) dieselben brauchen - (x, y, Radius, Farbe) in Koerper-
# Einheiten, der Index ist der Platz in der Reihe.
FUNKEN = [(-130, -262, 16, WHITE), (-205, 15, 13, WHITE), (212, -4, 14, FUNKE_GELB), (150, -250, 11, FUNKE_GELB),
          (-226, -150, 14, FUNKE_GELB), (-120, 100, 11, WHITE), (132, 124, 12, WHITE)]
put("funkeln", [funke(x, y, r, c, i) for i, (x, y, r, c) in enumerate(FUNKEN)], parent="body")

# ---------- Monokel (nur Vollversion) ----------
# Ein Glas ueber dem rechten Auge, Goldrand, Kettchen nach unten. Die
# Augen sitzen bei x = -32 und x = 32 auf Hoehe -74; das Glas ist etwas
# groesser als das Auge, damit es davor liegt und nicht darin.
# v6: aufs rechte Auge bei (40.5, -57). Das Kettchen endet auf der Wange -
# bis y = 18 wie vorher reichte es am schmaleren v6-Kinn ins Leere.
put("monokel", [
    group(ellipse(-AUG_X, AUG_Y, 52, 52), fill(GLAS, 26)),            # Glas
    group(ellipse(-AUG_X, AUG_Y, 52, 52), stroke(RAHMEN, 5.5)),       # dunkler Rand
    group(ellipse(-AUG_X, AUG_Y, 45, 45), stroke(KRONE, 2.5, 85)),    # Goldlinie innen
    # Dunkel statt golden: auf dem goldenen Drachen verschwand ein
    # goldener Rand vollstaendig. 29.09.2026.
    group(smooth([(58, -38), (68, -22), (63, -4)], closed=False, tension=0.5),
          stroke(RAHMEN, 2.5)),                                     # Kettchen
    group(ellipse(63, -3, 9, 9), stroke(RAHMEN, 1.5), fill(KRONE)),   # Knopf am Ende
], parent="head")

# ---------- Sonnenbrille ----------
# v6: Glaeser auf den Augen (vorher 17 Einheiten zu hoch und zu eng).
put("sonnenbrille", [
    group(smooth([(-65, -70), (-71, -72), (-77, -76)], closed=False, tension=0.5), stroke(RAHMEN, 4.5)),
    group(smooth([(65, -70), (71, -72), (77, -76)], closed=False, tension=0.5), stroke(RAHMEN, 4.5)),
    group(rect(0, -70, 22, 7, 3), fill(RAHMEN)),
    group(rect(AUG_X, -58, 50, 40, 11), stroke(RAHMEN, 4), fill(DUNKELGLAS)),
    group(rect(-AUG_X, -58, 50, 40, 11), stroke(RAHMEN, 4), fill(DUNKELGLAS)),
    group(smooth([(-57, -67), (-45, -73)], closed=False), stroke(GLANZ, 4.5, 40)),
    group(smooth([(24, -67), (36, -73)], closed=False), stroke(GLANZ, 4.5, 40)),
], parent="head")

# ---------- Lesebrille ----------
# v6: sitzt tief auf dem Nasenruecken (y = -38), der Blick geht ueber den
# Rand - die Augen sind unten halb dahinter.
put("lesebrille", [
    group(smooth([(-56, -42), (-65, -52), (-73, -60)], closed=False, tension=0.5), stroke(GOLDR, 4)),
    group(smooth([(56, -42), (65, -52), (73, -60)], closed=False, tension=0.5), stroke(GOLDR, 4)),
    group(arc((-18, -40), (18, -40), -4), stroke(GOLDR, 4)),
    # Rahmen 5 statt 4.5: im Laden (150 px) war die feine Goldlinie kaum zu sehen
    group(ellipse(-37, -38, 38, 30), stroke(GOLDR, 5), fill(GLAS, 24)),
    group(ellipse(37, -38, 38, 30), stroke(GOLDR, 5), fill(GLAS, 24)),
], parent="head")

# ======================= Um den Hals =======================
# Zwei Erkenntnisse aus der Durchsicht:
#   Der Hals sitzt bei y = -52, dort endet der Kopf. Ein Band muss dort liegen
#   und darf nur etwa +-42 breit sein, nicht +-62 - sonst liegt es auf den
#   Schultern statt um den Hals. Die obere Haelfte verschwindet hinter dem Kopf,
#   und genau das laesst es wie einen Schal aussehen.
#   Kleidung muss dem Umriss des Koerpers folgen. Der ist auf Brusthoehe +-74
#   breit; alles Schmalere sieht aus wie eine aufgelegte Platte.
# Gemessen am 18.09.2026: der Koerper ist gerundet 164 Punkte breit, die
# Kleidung war 156 - vier Punkte blauer Rand ringsum, und genau der liess sie
# wie eine aufgelegte Platte aussehen. Jetzt traegt der Stoff auf, wie er es
# auf einem Stofftier auch tut.
#
# v6, 15.10.2026: Beide Regeln gelten weiter, nur die Zahlen nicht mehr. Der
# Drache steht, und alles hier steht wie sein Koerper in Pixeln der Vorlage
# (VL() rechnet auf die Leinwand um): Hals 903..1145, Kinn bei y = 835,
# Schultern 960..1040, Rumpf bis zur Huefte (y = 1500) 806..1242, Bauch
# 866..1182. Die Kleidung liegt 8 bis 14 Pixel ausserhalb des Koerperumrisses.
# Neu ist: Die Arme haengen VOR den Rumpfseiten. In der Ruhe sieht man vom
# Rumpf nur den Streifen zwischen den Armen, beim Jubel (Arme oben) den
# ganzen. Darum haben Trikot und Jacken Aermel, und die offenen Jacken
# reichen ueber den Rand des Bauchs, sonst blieben von ihnen zwei Faeden.
LWZ = round(LW * 0.8, 2)            # Umriss der Kleidung (Koerper-Einheiten)
def sym_scharf(n, ks):
    """Nummern scharfer Ecken in SYM(links), wenn links n Punkte hat: jede
    Ecke links und ihr Spiegelbild rechts."""
    return tuple(ks) + tuple(2 * n - 2 - k for k in ks if 0 < k < n - 1)
# Rumpfseite der Kleidung, links: von der Schulter am Hals bis zur Huefte,
# rund 10 Pixel ausserhalb des Koerpers; dann der Saum bis zur Mitte.
SEITE_L = [(890, 900), (874, 930), (850, 954), (828, 984), (816, 1040), (813, 1110), (809, 1180), (803, 1240),
           (795, 1300), (787, 1360), (773, 1412), (753, 1458), (738, 1500)]
SAUM_L = [(790, 1528), (870, 1546), (950, 1554), (1024, 1556)]
KRAGEN = (940, 884)                 # Ecke des Ausschnitts am Hals (links)
def hemd_umriss(v_tief):
    """Geschlossenes Oberteil mit V-Ausschnitt bis y = v_tief (Vorlage)."""
    links = [(1024, v_tief), KRAGEN] + SEITE_L + SAUM_L
    return VL(SYM(links)), sym_scharf(len(links), (0, 1, 1 + len(SEITE_L)))
def v_kante(v_tief, dx=0):
    """Die beiden Kanten des Ausschnitts als offener Zug (fuer Kragen/Bund)."""
    return VL([(KRAGEN[0] + dx, KRAGEN[1]), (1024, v_tief), (2048 - KRAGEN[0] - dx, KRAGEN[1])])
def offen_umriss(vorn, unten_x=None):
    """Linke Bahn einer vorn offenen Jacke: vom Hals ueber Schulter, Seite und
    Saum bis zur Vorderkante bei x = vorn und an ihr wieder hinauf."""
    ux = unten_x or vorn
    pts = [(KRAGEN[0] - 4, KRAGEN[1] - 4)] + SEITE_L + [(790, 1528), (870, 1546), (ux, 1553),
                                                       (vorn + 2, 1420), (vorn + 2, 1260), (vorn, 1110), (vorn - 4, 1000)]
    return pts, (0, len(SEITE_L), len(SEITE_L) + 3)

# ---------- Aermel ----------
# v5: eine Ellipse am waagrechten Arm. v6: Der Arm haengt und hat einen
# Ellbogen. Der Aermel ist eine Kappe ueber der Schulter (Radius r0 um den
# Schulterpunkt), die dem Oberarm folgt - kurz mit geradem Buendchen
# (Trikot) oder bis ueber den Ellbogen (Jacken). Die Jacken haben dazu
# einen Aermel am Unterarm, der als eigene Ebene vor dem Unterarm liegt und
# mit ihm dreht; seine runde Kappe deckt das Gelenk, wie beim Arm selbst.
# Alles in Pixeln der Vorlage fuer den LINKEN Arm; rechts wird gespiegelt.
def _arm_achse():
    (sx, sy), (ex, ey) = SCHULTER, ELLBOGEN
    lg = math.hypot(ex - sx, ey - sy)
    return (ex - sx) / lg, (ey - sy) / lg, lg
def aermel_umriss(laenge, r0=74, r1=70, rund=False, n=8):
    """Umriss des Oberarm-Aermels und die Nummern seiner scharfen Ecken."""
    ux, uy, _ = _arm_achse()
    a_in = math.atan2(-ux, uy)                       # Richtung zur Koerpermitte
    sx, sy = SCHULTER
    pts = [(sx + r0 * math.cos(a_in - math.pi * k / n), sy + r0 * math.sin(a_in - math.pi * k / n)) for k in range(n + 1)]
    cx, cy = sx + laenge * ux, sy + laenge * uy
    if rund:
        pts += [(cx + r1 * math.cos(a_in + math.pi - math.pi * k / n), cy + r1 * math.sin(a_in + math.pi - math.pi * k / n))
                for k in range(n + 1)]
        return pts, ()
    pts += [(cx - r1 * uy, cy + r1 * ux), (cx + 6 * ux, cy + 6 * uy), (cx + r1 * uy, cy - r1 * ux)]
    return pts, (n + 1, n + 3)
def buendchen_oben(laenge, breite, r=70):
    """Streifen quer ueber den Oberarm-Aermel kurz vor seinem Ende."""
    ux, uy, _ = _arm_achse(); sx, sy = SCHULTER
    def q(lg, s, b=0): return (sx + lg * ux + s * r * uy + b * ux, sy + lg * uy - s * r * ux + b * uy)
    return [q(laenge - breite, -1), q(laenge, -1), q(laenge, 0, 6), q(laenge, 1), q(laenge - breite, 1)]
# Unterarm-Aermel (lang): Kappe ueber dem Ellbogen, Seiten 10 Pixel ausserhalb
# von UNTERARM_RAND, Buendchen kurz vor der Hand (die beginnt bei y = 1345).
UA_AERMEL = [(830, 1192), (816, 1240), (800, 1286), (795, 1326), (760, 1337), (725, 1339), (690, 1333), (656, 1321),
             (672, 1286), (684, 1240), (692, 1192), (700, 1158), (722, 1133), (762, 1121), (802, 1133), (824, 1158)]
UA_SCHARF = (3, 7)
UA_BUND = [(661, 1300), (797, 1304), (795, 1326), (760, 1337), (725, 1339), (690, 1333), (656, 1321)]
def sp_arm(s):
    """+1 links, -1 rechts: rechts an der Mittelachse der Vorlage spiegeln."""
    return (lambda q: q) if s > 0 else SP
def aermelpaar(stueck, formen):
    """Derselbe Aermel an beiden Armen. formen(s) bekommt +1 fuer links und
    -1 fuer rechts; damit wird an der Mittelachse gespiegelt, genauso wie es
    die Armebenen selbst tun."""
    put(stueck + "_armL", formen(1), parent="armL")
    put(stueck + "_armR", formen(-1), parent="armR")
def unteraermelpaar(stueck, formen):
    put(stueck + "_unterarmL", formen(1), parent="unterarmL")
    put(stueck + "_unterarmR", formen(-1), parent="unterarmR")
def aermel_oben(s, laenge, farbe, umriss, rund=False):
    pts, sch = aermel_umriss(laenge, rund=rund)
    return group(smooth(VL(sp_arm(s)(pts)), tension=0.5, scharf=sch), stroke(umriss, LWZ), fill(farbe))
def aermel_unten(s, farbe, umriss):
    return group(smooth(VL(sp_arm(s)(UA_AERMEL)), tension=0.5, scharf=UA_SCHARF), stroke(umriss, LWZ), fill(farbe))

# ---------- Zmajevi-Trikot ----------
# Nach dem Bild, das Ajdin am 18.09.2026 geschickt hat: tiefblau, duenne
# goldene Laengsstreifen, Wappen links auf der Brust, goldener Kragen.
# Die Streifen enden oben und unten innerhalb des Umrisses, damit sie nicht
# ueber den Rand hinauslaufen - in Lottie gibt es hier keine Maske.
# v6: Das Trikot bedeckt den Rumpf vom Hals bis zur Huefte, V-Ausschnitt bis
# y = 990, kurze Aermel mit goldenem Abschluss.
TRIKOT_U = col("06103A")
_TRIKOT, _TRIKOT_SCHARF = hemd_umriss(990)
put("trikot", [
    group(smooth(_TRIKOT, tension=0.5, scharf=_TRIKOT_SCHARF), stroke(TRIKOT_U, LWZ), fill(TRIKOT)),
    linien([VL([(884, 924), (884, 1536)]), VL([(954, 917), (954, 1542)]),
            # Der mittlere Streifen faengt erst UNTER der Spitze des Ausschnitts an,
            # sonst schwebte er mitten im Loch.
            VL([(1024, 1004), (1024, 1545)]),
            VL([(1094, 917), (1094, 1542)]), VL([(1164, 924), (1164, 1536)])], TRIKOT_H, 2.2, 75),
    # Wappen: angedeutet, mehr ist bei dieser Groesse nicht zu erkennen
    group(smooth(VL([(916, 1024), (986, 1024), (986, 1078), (951, 1106), (916, 1078)]), tension=0.25, scharf=(0, 1)),
          stroke(TRIKOT_W, 1.6, 75), fill(TRIKOT_D)),
    group(poly(VL([(924, 1031), (978, 1031), (924, 1074)])), fill(TRIKOT_H)),
    # Der Kragen liegt AUF dem Rand des Ausschnitts, nicht daneben.
    group(smooth(v_kante(990), closed=False, tension=0), stroke(TRIKOT_H, 3.4)),
], parent="body")
# Trikot: kurzer Aermel mit goldenem Abschluss, wie am echten Trikot.
aermelpaar("trikot", lambda s: [
    aermel_oben(s, 122, TRIKOT, TRIKOT_U),
    group(smooth(VL(sp_arm(s)(buendchen_oben(122, 20))), tension=0.4, scharf=(0, 1, 3, 4)), fill(TRIKOT_H)),
    group(smooth(VL(sp_arm(s)(aermel_umriss(122)[0])), tension=0.5, scharf=aermel_umriss(122)[1]), stroke(TRIKOT_U, LWZ)),
])

# ---------- Strickweste ----------
# (Im Laden "Strickjacke": V-Ausschnitt, lange Aermel.)
# v6: geschlossen mit tiefem V bis y = 1140, Knopfleiste darunter, Rippenbund
# am Saum. Lange Aermel bis zum Handgelenk.
STRICK_U = col("3A1726")
_STRICK, _STRICK_SCHARF = hemd_umriss(1140)
put("weste_strick", [
    group(smooth(_STRICK, tension=0.5, scharf=_STRICK_SCHARF), stroke(STRICK_U, LWZ), fill(STRICK)),
    # Strickrippen quer, nur angedeutet
    group(arc(V(836, 1262), V(1212, 1262), 2.5), arc(V(832, 1350), V(1216, 1350), 2.5), stroke(STRICK_H, 2.2, 40)),
    # Rippenbund am Saum
    group(smooth(VL(SYM([(1024, 1512), (900, 1508), (800, 1490), (744, 1470), (738, 1500), (790, 1528), (870, 1546),
                         (950, 1554), (1024, 1556)])), tension=0.5), fill(STRICK_H, 70)),
    # Knopfleiste und Knoepfe
    linie(VL([(1024, 1140), (1024, 1550)]), STRICK_D, 1.6, 70),
    *[group(ellipse(*V(1024, y), 5, 5), stroke(STRICK_U, 1.2), fill(STRICK_H)) for y in (1196, 1290, 1384, 1470)],
    # Vorher ein aufgemaltes V auf geschlossenem Stoff. Jetzt ein Rippenband,
    # das den echten Ausschnitt einfasst - wie der Bund einer Strickjacke.
    group(smooth(v_kante(1140), closed=False, tension=0), stroke(STRICK_H, 4.2)),
], parent="body")
# Strickjacke: langer Aermel, zwei Rippen quer, dickes Buendchen.
def _strick_quer(s, a, b):
    return group(smooth(VL(sp_arm(s)([a, b])), closed=False), stroke(STRICK_H, 2.2, 45))
aermelpaar("weste_strick", lambda s: [
    aermel_oben(s, 196, STRICK, STRICK_U, rund=True),
    _strick_quer(s, (752, 1060), (874, 1112)), _strick_quer(s, (736, 1110), (858, 1162)),
])
unteraermelpaar("weste_strick", lambda s: [
    # dunkler Rand: sonst verschmilzt der Aermel mit dem Rumpf, beides ist ja
    # derselbe Weinton
    aermel_unten(s, STRICK, STRICK_U),
    _strick_quer(s, (690, 1230), (814, 1240)),
    group(smooth(VL(sp_arm(s)(UA_BUND)), tension=0.4, scharf=(0, 1)), stroke(STRICK_U, LWZ * 0.8), fill(STRICK_H)),
])

# ---------- Koenigsmantel (nur Vollversion) ----------
# Was ein Koenig traegt: tiefrotes Tuch, Goldkante, und vorn der
# Hermelinbesatz - weisses Fell mit schwarzen Schwaenzchen. Der Kragen
# liegt quer ueber den Schultern und ist das, was man zuerst sieht;
# darunter faellt der Mantel bis unter den Bauch und bleibt vorn offen,
# damit der gelbe Bauch hervorschaut. Ajdin am 29.09.2026: "mach das,
# was ein koenig traegt".
# v6: Der Mantel faellt bis zu den Knien und weitet sich nach unten ueber
# den Koerper hinaus. Der Hermelinkragen ist eine eigene Ebene VOR den Armen
# ("umhang_kragen"): er liegt ueber den Schultern, die Arme kommen beim
# Jubeln darunter hervor.
UMHANG_U = col("5A070C")
# Die Aussenkante weitet sich bis x = 636: so steht das Rot auch neben den
# herabhaengenden Armen, nicht nur zwischen ihnen.
MANTEL_L = [(936, 880), (890, 900), (862, 926), (838, 958), (812, 1010), (786, 1080), (758, 1170), (728, 1280),
            (698, 1400), (670, 1520), (648, 1630), (636, 1716), (720, 1742), (830, 1752), (934, 1746),
            (952, 1600), (958, 1400), (956, 1200), (950, 1030), (944, 930)]
MANTEL_SCHARF = (11, 14)
# Die Innenkante, an der der Hermelin entlanglaeuft.
MANTEL_I = [(947, 900), (952, 1030), (957, 1200), (958, 1400), (954, 1600), (940, 1736)]
def mantel(sp):
    f = SP if sp else (lambda q: q)
    return [group(smooth(VL(f(MANTEL_L)), tension=0.5, scharf=MANTEL_SCHARF), stroke(UMHANG_U, LWZ), fill(UMHANG)),
            # Falten
            group(smooth(VL(f([(820, 1250), (770, 1480), (740, 1712)])), closed=False, tension=0.5),
                  smooth(VL(f([(905, 1420), (895, 1600), (885, 1738)])), closed=False, tension=0.5),
                  smooth(VL(f([(700, 1540), (685, 1712)])), closed=False, tension=0.5), stroke(UMHANG_D, 2.6, 45)),
            # Goldkante unten
            group(smooth(VL(f([(642, 1704), (720, 1728), (830, 1738), (930, 1732)])), closed=False, tension=0.5),
                  stroke(UMHANG_H, 2.4))]
put("umhang", paarweise(mantel(False), mantel(True)) + [
    # Hermelinbesatz vorn: breit, weiss, bis unten durch - so wie an einem
    # echten Kroenungsmantel. Ajdin hat ein Bild geschickt, 29.09.2026.
    group(smooth(VL(MANTEL_I), closed=False, tension=0.5), smooth(VL(SP(MANTEL_I)), closed=False, tension=0.5),
          stroke(FELL, 10)),
    # Die schwarzen Schwaenzchen darauf, klein und viele.
    group(*[ellipse(*V(*q), 3.2, 5) for y in (1130, 1290, 1450, 1610) for q in ((957 if y < 1600 else 950, y),
                                                                               (2048 - (957 if y < 1600 else 950), y))],
          fill(QUASTE)),
], parent="body")
# Der Kragen ist ein eigener kleiner Umhang ueber den Schultern:
# breit, unten rund, ganz in Hermelin.
# v6: so breit, dass er ueber die Schulterkappen der Arme hinausreicht -
# schmaler sass er wie ein Laetzchen unter dem Kinn.
KRAGEN_FELL = col("B8A68E")
_KRAGEN_SCHWAENZE = [(772, 1002), (842, 1040), (912, 1064), (980, 1078), (812, 942), (882, 972), (950, 992)]
put("umhang_kragen", [
    group(smooth(VL(SYM([(1024, 846), (950, 846), (870, 862), (800, 896), (752, 946), (736, 1000), (752, 1046),
                         (816, 1074), (900, 1092), (964, 1100), (1024, 1102)])), tension=0.5), stroke(KRAGEN_FELL, LWZ), fill(FELL)),
    group(*[ellipse(*V(*q), 3.2, 5) for q in _KRAGEN_SCHWAENZE + SP(_KRAGEN_SCHWAENZE) + [(1024, 1084)]], fill(QUASTE)),
], parent="body")

# ---------- Lederweste ----------
# (Im Laden "Lederjacke".) Vorn offen: zwei Bahnen am Umriss entlang,
# dazwischen bleibt der gelbe Bauch.
# Breitere Bahnen: vorher waren es zwei schmale Streifen am Rand. Die Oeffnung
# in der Mitte bleibt, damit der gelbe Bauch noch hervorschaut.
# v6: Die Vorderkanten stehen bei x = 946 / 1102, rund 40 Pixel innerhalb des
# Bauchrands - sonst verschwaende die Jacke in der Ruhe hinter den Armen.
# Revers oben, Nieten, lange Aermel.
LEDER_U = col("24160C")
_LEDER, _LEDER_SCHARF = offen_umriss(946)
_REVERS = [(936, 880), (946, 1110), (884, 984), (896, 906)]
def lederbahn(sp):
    f = SP if sp else (lambda q: q)
    return [group(smooth(VL(f(_LEDER)), tension=0.5, scharf=_LEDER_SCHARF), stroke(LEDER_U, LWZ), fill(LEDER)),
            group(smooth(VL(f(_REVERS)), tension=0.15, scharf=(0, 1, 2, 3)), stroke(LEDER_U, LWZ * 0.8), fill(LEDER_H)),
            group(*[ellipse(*V(*f([q])[0]), 4.2, 4.2) for q in [(893, 1176), (890, 1306)]], fill(NIET))]
put("weste_leder", paarweise(lederbahn(False), lederbahn(True)), parent="body")
# Lederjacke: langer Aermel, helleres Buendchen, eine Niete wie am Rumpf.
aermelpaar("weste_leder", lambda s: [
    aermel_oben(s, 196, LEDER, LEDER_U, rund=True),
    group(ellipse(*V(*sp_arm(s)([(800, 1090)])[0]), 4.2, 4.2), fill(NIET)),
])
unteraermelpaar("weste_leder", lambda s: [
    aermel_unten(s, LEDER, LEDER_U),
    group(smooth(VL(sp_arm(s)(UA_BUND)), tension=0.4, scharf=(0, 1)), stroke(LEDER_U, LWZ * 0.8), fill(LEDER_H)),
])

# ---------- Dicker Schal ----------
# Das Ende faengt weiter aussen an (x = 26 statt 10) und liegt tiefer: in der
# Mitte direkt unter dem Maul sah es aus wie eine herausgestreckte Zunge.
# Breiter als vorher: auf das Ende soll BOSNA passen, und dafuer braucht es
# Platz. Gilt fuer beide Schals - der Winterschal wird dadurch schoen dick.
# Tiefer und breiter. Der rechte Arm liegt VOR dem Schal und deckt alles
# zwischen y = -30 und -2 zu - gemessen. Was gesehen werden soll, muss
# darunter haengen.
# v6: Das Band liegt um den Hals unter dem Kinn (Vorlage y = 840..930, 300
# Pixel breit - der Hals ist 242), das Ende faellt rechts der Mitte ueber
# Brust und Bauch, zwischen Kinn und rechtem Arm. Der Arm haengt jetzt
# seitlich und verdeckt es nicht mehr.
SCHAL_BAND = (0, round(V(1024, 887)[1], 1), 76, 24)          # Mitte x, y, Breite, Hoehe
SCHAL_ENDE = VL([(1058, 900), (1132, 900), (1150, 1060), (1152, 1238), (1074, 1238), (1062, 1060)])
SCHAL_FRANSEN = [VL([(x, 1238), (x, 1272)]) for x in (1084, 1102, 1120, 1138)]
def schal_band(farbe, umriss):
    x, y, b, h = SCHAL_BAND
    return group(rect(x, y, b, h, h / 2), stroke(umriss, LWZ), fill(farbe))
def schal_ende(farbe, umriss):
    return group(smooth(SCHAL_ENDE, tension=0.3, scharf=(0, 1, 3, 4)), stroke(umriss, LWZ), fill(farbe))

WOLLE_U2 = col("5E160E")
put("schal_winter", [
    schal_ende(WOLLE, WOLLE_U2),
    group(*[smooth(q, closed=False) for q in SCHAL_FRANSEN], stroke(WOLLE_D, 2.6)),
    linien([VL([(1080, 920), (1090, 1225)]), VL([(1104, 920), (1112, 1225)]), VL([(1128, 920), (1134, 1225)])],
           WOLLE_D, 1.6, 34),
    schal_band(WOLLE, WOLLE_U2),
    linien([[(x, SCHAL_BAND[1] - 8), (x, SCHAL_BAND[1] + 8)] for x in (-26, -13, 0, 13, 26)], WOLLE_D, 1.6, 34),
], parent="body")

# ---------- Schal in den Landesfarben ----------
# Kein Flaggennachbau mehr. Das gelbe Dreieck war auf einem daumenbreiten Band
# nicht zu erkennen - jetzt ein Fanschal mit Laengsstreifen, so wie echte
# Fanschals gemacht sind, mit drei Sternen auf dem herabhaengenden Ende.
# Dritter Anlauf. Sterne und Dreieck der Flagge sind bei der Groesse, in der
# der Drache in der App steht, nicht zu erkennen - auf dem Bildschirm wurden
# daraus weisse Punkte und ein gelber Balken. Jetzt ein schlichter Fanschal:
# dunkelblau mit zwei gelben Laengsstreifen. Die Landesfarben bleiben.
# Wie ein echter Fanschal: dunkelblau, gelbe Laengsstreifen, und auf dem
# herabhaengenden Ende ein gelbes Feld mit dem Landesnamen. Nur Blau und
# Gelb - Ajdin am 18.09.2026 mit einem Bild echter Schals.
# v6: Das Ende ist schmaler als BOSNA lang ist - der Name laeuft deshalb wie
# auf echten Fanschals der Laenge nach, von oben nach unten gelesen.
SCHAL_U = col("070D2E")
put("schal_bih", [
    schal_ende(SCHAL_B, SCHAL_U),
    group(*[smooth(q, closed=False) for q in SCHAL_FRANSEN], stroke(SCHAL_G, 2.6)),
    group(poly(VL([(1066, 958), (1140, 958), (1141, 972), (1067, 972)])), fill(SCHAL_G)),   # Streifen ueber der Schrift
    group(poly(VL([(1072, 1196), (1150, 1196), (1150, 1210), (1072, 1210)])), fill(SCHAL_G)),   # und einer darunter
    group(smooth(SCHAL_ENDE, tension=0.3, scharf=(0, 1, 3, 4)), stroke(SCHAL_G, 1.4, 90)),   # gelbe Kante ums Ende
    schal_band(SCHAL_B, SCHAL_U),
    group(rect(0, SCHAL_BAND[1] - 5, 68, 3.4, 1.7), rect(0, SCHAL_BAND[1] + 5, 68, 3.4, 1.7), fill(SCHAL_G)),   # Streifen
], parent="body")
# Gelbe Schrift auf dem blauen Stoff - Ajdin am 18.09.2026: "mit gelber
# schrift bosna und hintergrund ist blau".
_SCHRIFT = V(1106, 1084)
built["schal_bih_text"] = textebene("schal_bih_text", "BOSNA", round(_SCHRIFT[0] - 3.4, 1), round(_SCHRIFT[1], 1), 12,
                                    SCHAL_G, "body", sperrung=40, r=90)


# ---------- Festtage ----------
# Entwurf vom 01.10.2026. Ajdin: "wir koennen jetzt schonmal die kostueme
# oder das app layout entwerfen fuer die feste wie halloween oder
# weihnachten oder bayram oder ostern". Vier Kopfstuecke, je eines pro Fest.
HEXE = col("3B1F5E"); HEXE_D = col("24123D"); HEXE_BAND = col("F28C28"); SCHNALLE = col("F5C518")
NIKO = col("D62B2B"); NIKO_D = col("A11B1B"); NIKO_FELL = col("FFF8F0")
BAJRAM = col("A4161A"); BAJRAM_D = col("74100F"); GOLD = col("F5C518"); GOLD_D = col("C79A00")
OHR = col("FBF7FA"); OHR_INNEN = col("F6A8C4"); OHR_BAND = col("8FD6B4")

# Hexenhut fuer Halloween: breite Krempe, die Spitze knickt nach rechts ab.
# v6: Krempe bei -114 statt -100. Die Spitze knickt frueher und flacher ab
# und bleibt unter -216 - bei -226 schnitt die Leinwand sie im Jubelsprung
# von Variante A ab.
HEXE_U = col("140A24")
put("hexenhut", hoeher(-6, [
    group(ellipse(0, -108, 180, 28), stroke(HEXE_U, KLW), fill(HEXE_D)),       # Krempe
    group(smooth([(-54, -112), (-40, -150), (-18, -182), (10, -201), (40, -208), (62, -200),
                  (40, -191), (20, -176), (24, -148), (38, -128), (54, -112)], tension=0.45, scharf=(5,)),
          stroke(HEXE_U, KLW), fill(HEXE)),
    group(smooth([(-30, -126), (-14, -168), (12, -192)], closed=False, tension=0.5), stroke(HEXE_D, 5, 50)),
    group(rect(0, -121, 106, 15, 4), fill(HEXE_BAND)),                # Band
    group(rect(0, -121, 24, 19, 4), stroke(SCHNALLE, 4)),             # Schnalle
]), parent="head")

# Nikolausmuetze fuer Weihnachten und Neujahr: der Zipfel faellt nach rechts.
# v6: Pelzrand bei -117 statt -98 (er lag auf den Brauen).
NIKO_U = col("6E1010")
put("nikolausmuetze", hoeher(-7, [
    group(smooth([(-66, -108), (-58, -154), (-12, -186), (44, -188), (90, -164),
                  (114, -128), (94, -126), (68, -152), (40, -148), (66, -108)], tension=0.5), stroke(NIKO_U, KLW), fill(NIKO)),
    group(smooth([(-30, -130), (6, -172), (60, -174)], closed=False, tension=0.5), stroke(NIKO_D, 5, 45)),
    group(rect(0, -110, 150, 26, 13), stroke(NIKO_U, KLW * 0.8), fill(NIKO_FELL)),   # Pelzrand
    group(ellipse(112, -122, 34, 34), stroke(NIKO_U, KLW * 0.8), fill(NIKO_FELL)),   # Bommel am Zipfel
]), parent="head")

# Bajram-Fes: der Fes aus dem Laden, aber mit goldenem Halbmond und Stern
# vorne und goldener Quaste - sonst saehe er aus wie der gekaufte.
# v6: dieselbe Form wie der Fes (fes_formen), nur in den Bajram-Farben.
BAJRAM_U = col("4E0A0A")
put("bajramfes", hoeher(-5, fes_formen(BAJRAM, BAJRAM_D, BAJRAM_U, GOLD, GOLD_D) + [
    group(rect(0, -105, 116, 9, 4), fill(GOLD, 90)),                  # goldenes Band unten
    group(ellipse(-6, -142, 36, 36), fill(GOLD)),                     # Halbmond: Gold ...
    group(ellipse(3, -146, 29, 29), fill(BAJRAM)),                    # ... und rot darueber
    stern(15, -144, 9.5, GOLD),
]), parent="head")

# Hasenohren fuer Ostern: ein Haarreif mit zwei Ohren.
# v6: Die Ohren stehen ZWISCHEN den Hoernern (deren Innenkante liegt bei
# y = -127 erst bei x = +-29) und sind etwas kuerzer - die Spitzen bleiben
# unter -216, sonst schneidet sie der Jubelsprung ab. Der Reif liegt auf dem
# Scheitel und quert die Hornansaetze.
OHR_U = col("C9B8C4")
def hasenohr(x, y, r):
    # Innen vor aussen: in einer Gruppe steht das Vordere ZUERST. Bis v5
    # stand das Innenohr an zweiter Stelle und lag damit unsichtbar hinter
    # dem weissen Ohr (gefunden 15.10.2026).
    return group(group(ellipse(0, -40, 18, 62), fill(OHR_INNEN)),
                 group(ellipse(0, -44, 36, 90), stroke(OHR_U, KLW * 0.8), fill(OHR)), r=r, p=(x, y))
put("hasenohren", [
    hasenohr(-20, -126, -14),
    hasenohr(20, -127, 10),
    group(smooth([(-68, -100), (-44, -124), (0, -134), (44, -124), (68, -100)], closed=False, tension=0.6),
          stroke(OHR_BAND, 9)),                                       # Haarreif
], parent="head")


# Skelett fuer Halloween. Ajdin: "was voll cool waere ist bei halloween das
# der drache ein skelettdrache waere", in Runde 2: "mit skelett meine ich
# komplett wie Knochentrocken aus Mario", in Runde 3: "der muss doch viel
# duenner sein weil er nur aus knochen besteht und zb am schwanz sind die
# schwarzen stellen unnoetig".
#
# Deshalb hat der Skelett-Drache KEIN Fleisch mehr: Die Ebene "skelett"
# traegt die Liste zmaj_leert, und die App leert beim Zusammensetzen genau
# diese Ebenen des Grunddrachens (Koerper, Beine, Arme, Schwanz, Fluegel).
# Die Ebenen selbst bleiben stehen, nur ohne Formen - sie tragen weiter die
# Bewegung, und die Knochen haengen an ihnen. Lottie kennt den Schluessel
# zmaj_leert nicht und uebergeht ihn.
# Der Kopf bleibt: ein Schaedel ist rund. Die App faerbt ihn knochenweiss
# (FARBEN.skelett), diese Ebenen setzen Augenhoehlen und Nase hinein.
SKEL_D = col("1B1C22"); KNOCHEN = col("F1EBDA"); KNOCHEN_D = col("A79D84")
# v6: dazu die beiden Unterarme - der Arm hat jetzt ein Gelenk.
SKELETT_LEERT = ["body", "legs", "armL", "armR", "unterarmL", "unterarmR", "tail", "wingL", "wingR", "head"]
# v7: Beim Bild-Drachen sind Haut und Fleisch Bilder - die nimmt die App
# beim Leeren ganz heraus (Bild-Ebenen haben keine Formen, die man leeren
# koennte). Einen Bildsatz haut/skelett/ gibt es seit 15.10.2026 nicht mehr
# (HAUT_ERSETZT): das Skelett ist immer dieses Vektor-Skelett.
if not VEKTOR:
    SKELETT_LEERT += ["bild_" + t for t in BILD_TEILE]


def knochen(a, b, dicke, knubbel=None, c=KNOCHEN, rand=KNOCHEN_D):
    """Ein Knochen von a nach b: Schaft mit zwei runden Enden, dazu eine
    dunklere Kante, damit er auch auf hellem Grund steht."""
    knubbel = knubbel or dicke * 1.3
    (ax, ay), (bx, by) = a, b
    nx, ny = by - ay, -(bx - ax); l = math.hypot(nx, ny) or 1
    nx, ny = nx / l * knubbel * 0.36, ny / l * knubbel * 0.36
    def lage(farbe, plus):
        # v6, 15.10.2026: die vier Knubbel in EINER Gruppe - gleiches Bild,
        # aber das Skelett mit gegliederten Fluegelfingern wurde sonst ueber
        # 190 KB gross.
        return [group(smooth([a, b], closed=False, tension=0), stroke(farbe, dicke + plus)),
                group(*[ellipse(x + s * nx, y + s * ny, knubbel + plus, knubbel + plus) for x, y in (a, b) for s in (1, -1)],
                      fill(farbe))]
    return lage(rand, 3) + lage(c, 0)


def bogen(punkte, dicke, c=KNOCHEN, rand=KNOCHEN_D):
    """Ein gebogener Knochen (Rippe, Schluesselbein) mit Kante."""
    return [group(smooth(punkte, closed=False, tension=0.5), stroke(rand, dicke + 3)),
            group(smooth(punkte, closed=False, tension=0.5), stroke(c, dicke))]


def wirbel(x, y, b, h, winkel=0):
    return [group(rect(0, 0, b + 3, h + 3, (h + 3) * 0.45), fill(KNOCHEN_D), r=winkel, p=(x, y)),
            group(rect(0, 0, b, h, h * 0.45), fill(KNOCHEN), r=winkel, p=(x, y))]


def rippe(y, breit):
    links = [(-5, y), (-breit * 0.5, y - 6), (-breit * 0.92, y + 2), (-breit, y + 13)]
    return bogen(links, 6) + bogen(mirror(links), 6)


def bein(sg):
    """v6: stehend - Oberschenkel von der Huefte zum Knie, Schienbein zum
    Knoechel, drei Zehen nach vorn. sg = 1 linkes Bein (im Bild), -1 rechtes.
    Punkte aus der Vorlage, wie der Drache selbst."""
    f = (lambda q: q) if sg > 0 else SP
    huefte, knie, fuss = VL(f([(915, 1470), (850, 1650), (868, 1760)]))
    teile = knochen(huefte, knie, 8, 12) + knochen(knie, fuss, 7, 11)
    for z in VL(f([(705, 1846), (758, 1862), (818, 1866)])):
        teile += knochen(fuss, z, 4.5, 7)
    return teile


# Wo der Rumpf in der Koerper-Ebene liegt (v6, stehend): Hals bei y = -128,
# Schultern bei -82, Becken bei 63 bis 85.
_SCH = V(*SCHULTER)
put("skelett", [
    *bein(1), *bein(-1),
    # Wirbelsaeule: oben der Hals bis unter den Schaedel, unten bis ins Becken
    *[t for y in (-124, -113, -102, 52, 60) for t in wirbel(0, y, 13, 8)],
    # Becken
    group(smooth([(-32, 66), (-12, 62), (0, 70), (12, 62), (32, 66), (28, 80), (10, 86), (-10, 86), (-28, 80)],
                 tension=0.5), stroke(KNOCHEN_D, 3)),
    group(smooth([(-32, 66), (-12, 62), (0, 70), (12, 62), (32, 66), (28, 80), (10, 86), (-10, 86), (-28, 80)],
                 tension=0.5), fill(KNOCHEN)),
    # Brustkorb ohne Fuellung: fuenf Rippenpaare und eine kurze, dazu das Brustbein
    *rippe(-72, 26), *rippe(-54, 34), *rippe(-34, 38), *rippe(-14, 40), *rippe(6, 36), *rippe(24, 26),
    *knochen((0, -80), (0, 20), 9, 11),
    # Schluesselbeine bis zu den Schultern, an denen die Arme haengen
    *knochen((-6, -90), (_SCH[0] + 4, _SCH[1]), 6, 9), *knochen((6, -90), (-_SCH[0] - 4, _SCH[1]), 6, 9),
], parent="body")
built["skelett"]["zmaj_leert"] = SKELETT_LEERT

# Kopf des Skeletts. Mehrere Versuche mit einem eigenen Schaedel - eckig,
# mit Herz-Nase, Augenhoehlen als Vielecke und kleinen Punkten darin, einer
# umrandeten Schnauze und Jochbein-Linien - sahen nicht mehr nach Zmaj aus
# (Ajdin: "irgendwas sagt mir, es ist nicht so wie der Original-Drache").
# Im Vergleich nebeneinander war es klar: Zmaj erkennt man an seiner
# Kopfform, an den grossen Augen, an zwei kleinen Nasenloechern, der hellen
# Schnauze und den Hoernern.
#
# Darum ist der Kopf der Original-Kopf, Form fuer Form, mit nur drei
# Aenderungen: knochenweiss (macht die App), etwas schmaler ("nur etwas
# schmaler, weil keine Haut und keine Muskeln und Fett dran sind" - v6: 92 %
# der Breite), und die Nasenloecher sind schwarze Loecher.
# "head" wird geleert, damit nicht der breite Kopf dahinter hervorschaut.
# 16.10.2026: Beim Kopfschuetteln dreht auch der Schaedel nach dem Kopfplan
# den Kopf - der Schaedel rueckt wie die Huete (SCHAEDEL_GEDREHT), Schnauze
# und Nasenloecher dorthin, wo Augenhoehlen und Brauen hinruecken
# (GESICHT_GEDREHT, gerechnet gegen den schon verschobenen Schaedel).
_NASENLOECHER = [
    group(ellipse(0, 0, 26 * U, 18 * U), fill(SKEL_D), r=-25, p=Hk(1024 - 52 * 0.92, 690)),
    group(ellipse(0, 0, 26 * U, 18 * U), fill(SKEL_D), r=25, p=Hk(1024 + 52 * 0.92, 690)),
]
if VEKTOR:
    put("skelett_kopf", kopf_formen(0.92, gesicht_dazu=_NASENLOECHER), parent="head")
else:
    _schnauze_tr = {"ty": "tr", "a": const([0, 0]), "r": const(0), "o": const(100),
                    "p": kopf_spur({s: [dx - SCHAEDEL_GEDREHT[s], dy] for s, (dx, dy, _b) in GESICHT_GEDREHT.items()}, [0, 0]),
                    "s": kopf_spur({s: [b, 100] for s, (_x, _y, b) in GESICHT_GEDREHT.items()}, [100, 100])}
    put("skelett_kopf", kopf_formen(0.92, gesicht_dazu=_NASENLOECHER, gesicht_tr=_schnauze_tr), parent="head",
        animk={"p": kopf_spur({s: [dx, 0, 0] for s, dx in SCHAEDEL_GEDREHT.items()}, [0, 0, 0])})

# Augen: runde schwarze Hoehlen, so gross wie die Augen des Originals, darin
# nur ein gelber Punkt, der dem Blick folgt (Ajdin: "es reicht ein gelber
# Punkt"). Eine volle Iris mit Pupille und Glanzlichtern war zu viel.
# Eigenes Gelb: AMBER und YEL wuerden von der Skelettfarbe mitgefaerbt.
# (Hiess bis v5 IRIS; seit v6 ist IRIS das Blau der echten Augen.)
IRIS_SKELETT = col("FFC61A")
def _hoehlen():
    teile, punkte = [], []
    for sp in (False, True):
        f = SP if sp else (lambda q: q)
        c = Hk(*f([(918 + 6, 586)])[0]); p = Hk(*f([(928, 594)])[0])
        teile.append(group(ellipse(c[0], c[1], (AUGE_B + 6) * U, (AUGE_H + 4) * U), fill(SKEL_D)))
        punkte.append(group(ellipse(p[0], p[1], 26 * U, 30 * U), fill(IRIS_SKELETT)))
    return teile, punkte
_hoe, _pkt = _hoehlen()
put("skelett_augen", _hoe + [
    {"ty": "gr", "it": _pkt + [
        {"ty": "tr", "p": pupil_pos, "a": const([0, 0]), "s": const([100, 100]), "r": const(0), "o": const(100)}]},
], parent="head", animk={"o": opa({"idle", "sad", "ok", "no", "no_l", "no_r"})})

# Zwei kleine Fangzaehne am Laecheln - ein Totenkopf ohne Zaehne sah zahm
# aus. Nur in der Ruhe sichtbar, wie mouth_idle selbst.
put("skelett_zaehne", [
    group(poly(HL([(948, 734), (960, 760), (972, 742)])), stroke(KNOCHEN_D, 3 * U), fill(KNOCHEN)),
    group(poly(HL([(1076, 742), (1088, 760), (1100, 734)])), stroke(KNOCHEN_D, 3 * U), fill(KNOCHEN)),
], parent="head", animk={"o": opa({"idle"})})


# Arme: ein Oberarmknochen; am Unterarm Elle und drei Fingerknochen.
def skelett_arm(sg):
    f = (lambda q: q) if sg > 0 else SP
    a, b = VL(f([(830, 1022), ELLBOGEN]))
    return knochen(a, b, 7, 11)
def skelett_unterarm(sg):
    f = (lambda q: q) if sg > 0 else SP
    e, w = VL(f([ELLBOGEN, (722, 1360)]))
    teile = knochen(e, w, 6, 10)
    for z in VL(f([(664, 1462), (700, 1478), (738, 1460)])):
        teile += knochen(w, z, 4, 6)
    return teile
put("skelett_armL", skelett_arm(1), parent="armL")
put("skelett_armR", skelett_arm(-1), parent="armR")
put("skelett_unterarmL", skelett_unterarm(1), parent="unterarmL")
put("skelett_unterarmR", skelett_unterarm(-1), parent="unterarmR")


# Fluegel nur aus Knochen, wie bei einer Fledermaus ohne Haut: der Armknochen
# laeuft bis zum Handgelenk, von dort gehen drei Finger zu den Zacken.
# v6, 15.10.2026: Die Finger waren je ein duenner Bogen vom Handgelenk bis
# zur Spitze und sahen aus wie Fuehler. Jetzt folgen sie den Fingerknochen
# der Figur (FINGER) und bestehen aus drei Gliedern mit Gelenkknubbeln, die
# nach aussen duenner werden - wie die Hand des Arms.
GELENK = (668, 452)
FINGER_GLIEDER = [[(652, 462), (470, 528), (262, 700), (78, 1126)],          # Vorderkante
                  [(640, 482), (500, 640), (380, 900), (268, 1144)],
                  [(648, 492), (588, 740), (566, 980), (553, 1210)]]
def skelett_fluegel(sg):
    f = (lambda q: q) if sg > 0 else SP
    s1, s2, g = VL(f([(880, 940), (720, 790), GELENK]))
    teile = knochen(s1, s2, 8, 12) + knochen(s2, g, 8, 12)                 # Armknochen mit Knick
    for glieder in FINGER_GLIEDER:
        p = VL(f(glieder))
        for (a, b), (d, k) in zip(zip(p, p[1:]), [(5.5, 8.5), (4.5, 7), (3.6, 6)]):
            teile += knochen(a, b, d, k)
    teile += [group(ellipse(g[0], g[1], 18, 18), fill(KNOCHEN_D)),
              group(ellipse(g[0], g[1], 15, 15), fill(KNOCHEN))]           # Handgelenk
    # Daumenkralle am Handgelenk, wie an der Figur
    teile += [group(poly(VL(f([(640, 448), (706, 420), (668, 470)]))), stroke(KNOCHEN_D, 2.5), fill(KNOCHEN))]
    return teile
put("skelett_wingL", skelett_fluegel(1), parent="wingL")
put("skelett_wingR", skelett_fluegel(-1), parent="wingR")


# Schwanz: nur Wirbel, nach hinten kleiner, jeder mit einem kleinen Dorn;
# am Ende die Pfeilspitze als Knochen. Keine dunkle Fuellung mehr.
def schwanz_wirbel(c, breiten, n=13, t=0.6):
    m = len(c); seg = []
    for k in range(m - 1):
        p0, p1, p2, p3 = c[max(k - 1, 0)], c[k], c[k + 1], c[min(k + 2, m - 1)]
        o = ((p2[0] - p0[0]) * t / 2, (p2[1] - p0[1]) * t / 2)
        i = ((p3[0] - p1[0]) * t / 2, (p3[1] - p1[1]) * t / 2)
        bz = [p1, (p1[0] + o[0], p1[1] + o[1]), (p2[0] - i[0], p2[1] - i[1]), p2]
        for j in range(40):
            u = j / 40.0
            x = (1-u)**3*bz[0][0] + 3*(1-u)**2*u*bz[1][0] + 3*(1-u)*u*u*bz[2][0] + u**3*bz[3][0]
            y = (1-u)**3*bz[0][1] + 3*(1-u)**2*u*bz[1][1] + 3*(1-u)*u*u*bz[2][1] + u**3*bz[3][1]
            seg.append((x, y, breiten[k] + (breiten[k + 1] - breiten[k]) * u))
    seg.append((c[-1][0], c[-1][1], breiten[-1]))
    laenge = [0.0]
    for p, q in zip(seg, seg[1:]):
        laenge.append(laenge[-1] + math.hypot(q[0] - p[0], q[1] - p[1]))
    schritt = laenge[-1] / n; teile = []
    for q in range(n):
        ziel = schritt * (q + 0.5)
        k = next(i for i, l in enumerate(laenge) if l >= ziel)
        x, y, w = seg[k]; p = seg[max(k - 1, 0)]; r = seg[min(k + 1, len(seg) - 1)]
        winkel = math.degrees(math.atan2(r[1] - p[1], r[0] - p[0]))
        hoch = w * 0.62
        # Dorn: zeigt nach oben, also auf die Seite der Normalen mit kleinerem y
        tx, ty = math.cos(math.radians(winkel)), math.sin(math.radians(winkel))
        nx, ny = (-ty, tx) if tx < 0 else (ty, -tx)
        if ny > 0: nx, ny = -nx, -ny
        fuss = [(x + nx * hoch * 0.3 + tx * d, y + ny * hoch * 0.3 + ty * d) for d in (-schritt * 0.2, schritt * 0.2)]
        spitze = (x + nx * hoch * 1.15, y + ny * hoch * 1.15)
        teile += [group(poly([fuss[0], spitze, fuss[1]]), stroke(KNOCHEN_D, 3)),
                  group(poly([fuss[0], spitze, fuss[1]]), fill(KNOCHEN))]
        teile += wirbel(x, y, schritt * 0.72, hoch, winkel)
    return teile
# Mittellinie des v6-Schwanzes (Vorlage) und seine Pfeilspitze
# v6, 15.10.2026: Die Spitze war ein schlichtes Dreieck, das mit einer Luecke
# ueber dem letzten Wirbel hing. Jetzt die Pfeilspitze der Figur mit beiden
# Widerhaken, als Knochenplatte mit einem Loch in der Mitte, und die
# Wirbelkette reicht bis an ihren Fuss.
tail_c = VL([(1190, 1660), (1300, 1668), (1420, 1672), (1530, 1650), (1610, 1602), (1662, 1530), (1688, 1446)])
SPITZE_SCHWANZ = VL([(1688, 1432), (1630, 1424), (1648, 1356), (1654, 1286), (1636, 1222), (1700, 1262), (1744, 1320),
                     (1764, 1376), (1762, 1424), (1720, 1414)])
SPITZE_LOCH = VL([(1676, 1384), (1684, 1318), (1708, 1350), (1704, 1390)])
put("skelett_schwanz", schwanz_wirbel(tail_c, [30, 27, 23, 19, 15, 12, 10], n=12)
    + [*knochen(VL([(1686, 1458)])[0], VL([(1690, 1420)])[0], 4.5, 7),
       group(smooth(SPITZE_SCHWANZ, tension=0.35, scharf=(1, 4, 8)), stroke(KNOCHEN_D, 3), fill(KNOCHEN)),
       group(smooth(SPITZE_LOCH, tension=0.5), fill(KNOCHEN_D, 55))],
    parent="tail")

# Jelek fuer Bajram: die bestickte Weste aus der bosnischen Tracht -
# dunkles Weinrot, vorn offen, mit goldener Kante und Ranken.
# Runde 2 war zu klein (Ajdin: "der jelek ist wieder zu klein guck genau"):
# er sass wie ein Laetzchen auf dem Bauch. Jetzt reicht er wie die
# Lederweste ueber den ganzen Rumpf, von der Schulter bis unter den Bauch,
# und steht an der Seite ueber den Koerperrand hinaus.
# v6, 15.10.2026: auf den stehenden Rumpf gesetzt (Pixel der Vorlage). Ohne
# Aermel, wie die echte Weste; die Vorderkanten laufen leicht gebogen ueber
# den Bauchrand (x = 936..958), unten gerundet bis zur Huefte. Ranken und
# Knoepfe liegen in dem Streifen, den die Arme in der Ruhe frei lassen.
JELEK = col("6E1423"); JELEK_D = col("4A0C17"); JELEK_GOLD = col("E9B949")
JELEK_L = [(KRAGEN[0] - 6, KRAGEN[1] - 2)] + SEITE_L[:-1] + [(744, 1478), (772, 1514), (840, 1534), (912, 1530), (946, 1492),
                                                            (958, 1390), (958, 1260), (950, 1130), (942, 1010), (936, 930)]
JELEK_INNEN = [(926, 940), (932, 1010), (940, 1130), (946, 1260), (946, 1385), (934, 1478), (908, 1508), (842, 1512), (786, 1496)]
def ranke(x, y, s=1, g=1.0):
    pkt = [(0, 0), (9, -11), (20, -4), (16, 7), (7, 4), (9, -2)]
    return group(smooth([(x + px * g * s, y + py * g) for px, py in pkt], closed=False, tension=0.55),
                 stroke(JELEK_GOLD, 2.2, 95))
def blatt(x, y, s=1):
    return group(smooth([(x, y), (x + 5 * s, y - 4), (x + 9 * s, y), (x + 5 * s, y + 3.5)], tension=0.6), fill(JELEK_GOLD, 90))
def jelek_bahn(sp):
    f = SP if sp else (lambda q: q)
    s = -1 if sp else 1
    def pt(x, y): return V(*f([(x, y)])[0])
    return [group(smooth(VL(f(JELEK_L)), tension=0.45, scharf=(0,)), stroke(JELEK_GOLD, 2.6), fill(JELEK)),
            group(smooth(VL(f([(752, 1440), (744, 1478), (772, 1514), (840, 1534), (912, 1530), (946, 1492), (954, 1430),
                                 (900, 1470), (820, 1470)])), tension=0.45), fill(JELEK_D, 55)),
            group(smooth(VL(f(JELEK_INNEN)), closed=False, tension=0.45), stroke(JELEK_GOLD, 1.2, 70)),
            *[ranke(*pt(x, y), s, 0.8) for x, y in [(858, 1110), (850, 1250), (846, 1385)]],
            *[blatt(*pt(x, y), s) for x, y in [(892, 1030), (884, 1180), (880, 1320)]],
            # Goldknoepfe (toke) an der Kante, wie an der echten Weste
            group(*[ellipse(*pt(x, y), 4.6, 4.6) for x, y in [(934, 1000), (942, 1110), (946, 1220), (948, 1330), (944, 1430)]],
                  fill(JELEK_GOLD))]
put("jelek", jelek_bahn(False) + jelek_bahn(True), parent="body")

# ---------- Ausgabe ----------
# Eine Grunddatei ohne jeden Zierrat, dazu je Stück eine winzige Datei mit
# genau seiner Ebene. Die App holt die Grunddatei einmal, dazu die Schnipsel
# der getragenen Stücke, haengt sie aneinander und sortiert nach "ind" -
# damit steht wieder genau die Reihenfolge aus ORDER. So kostet jede
# Kombination aus Kopf, Brille und Hals keine einzige Datei extra.
# Vorher war jedes Stück eine vollständige Animation mit 75 KB, und der
# Drache konnte deshalb immer nur eines tragen.
def kompakt(x, schluessel=None):
    """Zahlen fuer die Datei kuerzen: Farben (c, fc) auf 4 Stellen - die App
    vergleicht sie mit 0.004 Spielraum -, grosse Werte auf eine, kleine auf
    zwei Nachkommastellen; glatte Werte als ganze Zahl."""
    if isinstance(x, dict):
        # Farbe steht als {"a": 0, "k": [r, g, b, a]} unter "c" - das "k" darin
        # erbt den Schluessel "c", sonst wuerde sie auf 2 Stellen gerundet und
        # die App erkennte sie beim Umfaerben nicht mehr.
        return {k: kompakt(v, schluessel if (k == "k" and schluessel in ("c", "fc")) else k) for k, v in x.items()}
    if isinstance(x, list): return [kompakt(v, schluessel) for v in x]
    if isinstance(x, float):
        if schluessel in ("c", "fc"): r = round(x, 4)
        elif schluessel in ("v", "i", "o"): r = round(x, 1)
        else: r = round(x, 1 if abs(x) >= 10 else 2)
        return int(r) if r == int(r) else r
    return x
# ---------- Bild-Drache: Bilder an das Rig haengen (v7) ----------
# Die Rig-Ebenen bleiben mit allen Keyframes stehen und tragen die Bewegung,
# Kostueme und Bilder haengen an ihnen; nur ihre Formen fallen weg.
def _bild_ebene(name, ref, ebene, ax, ay, o):
    """Eine Bild-Ebene (ty 2) an der Rig-Ebene "ebene", Drehpunkt ax/ay im
    Bild auf deren Anker, Deckkraft o. Fuer die Teile des Drachen und seit
    16.10.2026 auch fuer die gemalten Kostueme."""
    # Die Hornspitzen-Ebene hat keine eigene Lage: sie rechnet in den
    # Einheiten des Kopfes, dessen Drehpunkt also auch ihrer ist.
    anker = built["head" if ebene == "hoerner" else ebene]["ks"]["a"]["k"]
    am_kopf = ebene in ("head", "hoerner")
    # Bilder am Kopf: 2 Pixel je LEINWAND-Einheit bei Kopf 1.0, der Kopf
    # selbst ist aber um K/U verkleinert - daher die Umrechnung.
    s = round(100 / (PX_JE_EINHEIT * (K / U if am_kopf else 1)), 3)
    return {"ddd": 0, "ind": IDX[name], "ty": 2, "nm": name, "refId": ref, "sr": 1,
            "parent": IDX[ebene],
            "ks": {"o": o,
                   "r": const(0), "p": const([anker[0], anker[1], 0]), "a": const([ax, ay, 0]), "s": const([s, s, 100])},
            "ao": 0, "ip": 0, "op": OP, "st": 0, "bm": 0}


def bildebene(teil):
    ebene, _b, _h, ax, ay, sichtbar = BILD_TEILE[teil]
    return _bild_ebene("bild_" + teil, teil, ebene, ax, ay, const(100) if sichtbar is None else bild_deckkraft(teil))


def zierrat_bildebene(stueck, eintrag):
    """Bild-Ebene eines gemalten Kostuems (GEMALT); Asset "<stueck>_<teil>"."""
    teil, ebene, _b, _h, ax, ay, sichtbar, _vor = eintrag
    return _bild_ebene("bild_%s_%s" % (stueck, teil), "%s_%s" % (stueck, teil), ebene, ax, ay,
                       const(100) if sichtbar is None else _halten(sichtbar_werte(sichtbar)))


def kragen_stauchen(L):
    """Den Stehkragen (bild_umhang_rutsch) in den Bildern mit waagerechten
    Armen senkrecht stauchen (KRAGEN_STAUCHEN, 17.10.2026 spaet abends): um
    KRAGEN_FUSS, so bleiben Knoepfe und Kette am Platz und nur die Spitzen
    liegen tiefer - sie standen sonst wie Hoerner neben dem Kinn. Mit dem
    Heben der Arme waechst er auf volle Hoehe. Anker und Lage werden auf
    KRAGEN_FUSS umgerechnet; bei voller Hoehe liegt das Bild wie vorher."""
    ax, ay = L["ks"]["a"]["k"][:2]
    px, py = L["ks"]["p"]["k"][:2]
    s = L["ks"]["s"]["k"][0]
    fx, fy = KRAGEN_FUSS
    L["ks"]["a"] = const([fx, fy, 0])
    L["ks"]["p"] = const([round(px + (fx - ax) * s / 100, 3), round(py + (fy - ay) * s / 100, 3), 0])
    f = [1.0] * OP
    for z, k in KRAGEN_STAUCHEN.items():
        for t in _bilder(z):
            f[t] = k
    L["ks"]["s"] = _halten([[s, round(s * k, 3), 100] for k in f])


# Kostueme auf dem abgewandten Kopf (v7, 15.10.2026). Die Stuecke sind fuer
# den Kopf von vorn gebaut. Im Bild kopf_links stehen die Augen enger, etwas
# tiefer und ein wenig zur Schnauze hin; mittig gelassen sah bei der
# Sonnenbrille das nahe Auge daneben heraus. Die Brillen rutschten darum (bis
# 16.10.2026, siehe unten) mit dem Kopfwechsel 4 Einheiten zur Seite und 4
# nach unten und wurden auf 90 %
# schmal (rechts gespiegelt) - ausprobiert in Stufen von -29 bis 0 und 80 bis
# 90 %, so liegen Brille, Sonnenbrille, Lesebrille und Monokel auf den Augen.
# Huete, Ohrenschuetzer und Kopfhoerer sitzen auf dem Schaedel; sie ruecken
# um SCHAEDEL_GEDREHT mit (unten).
# 16.10.2026: Bis dahin schaltete umschalten() die Brillen nach DREHEN, also
# einmal je Stimmung no_l/no_r. Jetzt nach der Seite im Kopfplan (kopf_spur):
# bei jedem Schwung des Kopfschuettelns, im selben Bild wie das Kopfbild.
# Dabei neu ausgemessen: im Bild kopf_links liegen die Augen (das Weisse) bei
# x = -62,6 und +8,5 Kopf-Einheiten, 7,5 tiefer als von vorn (-41,5/+41,1);
# mit -4/4/90 % stand die Brille weit rechts davon, und das nahe Auge
# schaute zwischen den Glaesern hervor (Kontaktbogen 16.10.2026). Jetzt
# Mitte -27, 7 tiefer, Abstand 86 % - beide Glaeser liegen auf den Augen,
# das Monokel auf dem nahen bzw. fernen Auge.
BRILLE_GEDREHT = {"links": (-27, 7, 86), "rechts": (27, 7, 86)}     # dx, dy, Breite %
# Das Gesicht des Vektor-Skeletts rueckt mit dem Kopf (GESICHT_GEDREHT, siehe
# Kopfplan). Diese Ebenen haengen am Kopf, liegen mit Anker 0/0 in Kopf-
# Einheiten und haben selbst keine Ortsbewegung - ihr Ort und ihre Breite
# kommen ganz aus dem Kopfplan. mouth_open und mouth_cry fehlen mit Absicht:
# sie haben eigenen Anker und eigene Groesse und sind nur in cheer, ok und
# cry zu sehen, wo der Kopf immer vorn ist.
GESICHT_SKELETT = ["skelett_augen", "skelett_zaehne", "lids", "brows", "mouth_idle", "mouth_sad",
                   "eyes_happy", "eyes_cry", "tears"]
ASSETS = []
ZIERRAT_ASSETS = {}      # stueck: Assets seines Schnipsels (gemalte Kostueme)
if not VEKTOR:
    _mitte = [0, AUG_Y, 0]
    # Seit 16.10.2026 sind alle Brillen gemalt (GEMALTE_HUETE) und haben eigene
    # Seitenbilder; BRILLE_GEDREHT bleibt fuer eine Vektor-Brille, falls eine
    # wieder dazukommt.
    for _n in [b for b in BRILLEN if b not in GEMALT]:
        built[_n]["ks"]["a"] = const(_mitte)
        built[_n]["ks"]["p"] = kopf_spur({s: [dx, round(AUG_Y + dy, 2), 0] for s, (dx, dy, _b) in BRILLE_GEDREHT.items()}, _mitte)
        built[_n]["ks"]["s"] = kopf_spur({s: [b, 100, 100] for s, (_x, _y, b) in BRILLE_GEDREHT.items()}, [100, 100, 100])
    for _n in BILD_EBENEN:
        built[_n]["shapes"] = []
    for _t in BILD_TEILE:
        built["bild_" + _t] = bildebene(_t)
    # u ist relativ zur Lottie-Datei, wie es Lottie vorsieht: so findet auch
    # ein Aufruf mit path (web/_feature.html) die Bilder. Die App laedt mit
    # animationData und setzt den Pfad selbst (zmajDaten in web/index.html),
    # je nach Hautfarbe auf teile/ oder haut/<farbe>/.
    ASSETS = [{"id": t, "w": v[1], "h": v[2], "u": "teile/", "p": t + ".webp", "e": 0} for t, v in BILD_TEILE.items()]
    for _stueck, _farbe in HAUT_ERSETZT.items():
        for _n in [_stueck] + NUR_MIT.get(_stueck, []):
            built[_n]["zmaj_ohne_haut"] = _farbe
    # Gemalte Kostueme (16.10.2026, GEMALT): ihre Bild-Ebenen und Assets.
    # Die Assets stehen NICHT in zmaj.json, sondern im Schnipsel des Stuecks
    # (unten): die App laedt die Bilder nur, wenn das Stueck getragen wird.
    # Sie haengen nicht von der Hautfarbe ab - u zeigt immer auf zierrat/.
    _hornspitzen = ["bild_" + t for t in BILD_TEILE if t.startswith("hoerner_")]
    for _st, _teile in GEMALT.items():
        for _e in _teile:
            built["bild_%s_%s" % (_st, _e[0])] = zierrat_bildebene(_st, _e)
        if _st in GEMALTE_HUETE and _st not in HORNSPITZEN_BLEIBEN:
            built["bild_%s_vorne" % _st]["zmaj_leert"] = _hornspitzen
        ZIERRAT_ASSETS[_st] = [{"id": "%s_%s" % (_st, e[0]), "w": e[2], "h": e[3], "u": "%s/%s/" % (ZIERRAT_ORDNER, _st),
                                "p": e[0] + ".webp", "e": 0} for e in _teile]
    # Stehkragen des Koenigsmantels bei waagerechten Armen gestaucht
    if "umhang" in GEMALT:
        kragen_stauchen(built["bild_umhang_rutsch"])
    # Gemalte Funkelsterne (GEMALTE_FUNKEN): auf den Platz des Vektorsterns,
    # Groesse, Drehung und Deckkraft wie funke() - die Skala rechnet die
    # Bildpixel auf den Radius des Vektorsterns um.
    for _i, (_bild, _radius) in GEMALTE_FUNKEN.items():
        _x, _y, _r, _c = FUNKEN[_i]
        _gs, _go, _gr = funke_zeit(_i, len(FUNKEN))
        _k = _r / _radius
        built["bild_funkeln_" + _bild]["ks"].update(
            {"p": const([_x, _y, 0]), "s": anim([(t, [round(v * _k, 2), round(v * _k, 2), 100]) for t, v in _gs]),
             "r": anim(_gr), "o": anim(_go)})
    # Kopfstuecke am abgewandten Kopf. Die Kopfbilder kopf_links/kopf_rechts
    # zeigen den Kopf gedreht: der Schaedel liegt dann weiter hinten, also im
    # Bild zur anderen Seite hin (Kopfraster 15.10.2026: Mitte der
    # Schaedeldecke bei +10 bis +15 Kopf-Einheiten statt 0, der nahe
    # Ohrlappen bei +85..+100). Huete, Kronen und Ohrensachen ruecken darum
    # um 12 Einheiten mit (SCHAEDEL_GEDREHT); ohne das sass der Hut auf der
    # Stirn und das linke Ohrpolster neben dem Kopf in der Luft. Gehalten, wie
    # die Kopfbilder selbst: das Stueck springt mit dem Bild um, nicht
    # dazwischen. Bis 15.10.2026 rueckte es die ganze Stimmung no_l/no_r lang
    # mit, auch in den Bildern, in denen noch der Frontkopf stand; seit dem
    # Kopfschuetteln (16.10.2026) Bild fuer Bild nach dem Kopfplan.
    def _mitruecken(name):
        tr_ = {"ty": "tr", "p": kopf_spur({s: [dx, 0] for s, dx in SCHAEDEL_GEDREHT.items()}, [0, 0]),
               "a": const([0, 0]), "s": const([100, 100]), "r": const(0), "o": const(100)}
        built[name]["shapes"] = [{"ty": "gr", "it": built[name]["shapes"] + [tr_]}]
    # Die gemalten Huete haben je Seite ein eigenes Bild (GEMALTE_HUETE) -
    # mitruecken muessen nur noch die Vektor-Stuecke (seit 16.10.2026 ist
    # keins mehr am Kopf; die Schleife bleibt fuer ein neues Vektor-Stueck).
    for _n in KOPF_TEILE:
        if _n not in GEMALT:
            _mitruecken(_n)
    # Das Gesicht des Vektor-Skeletts (GESICHT_SKELETT oben).
    for _n in GESICHT_SKELETT:
        _ks = built[_n]["ks"]
        assert _ks["p"] == const([0, 0, 0]) and _ks["a"] == const([0, 0, 0]) and _ks["s"] == const([100, 100, 100]), _n
        _ks["p"] = kopf_spur({s: [dx, dy, 0] for s, (dx, dy, _b) in GESICHT_GEDREHT.items()}, [0, 0, 0])
        _ks["s"] = kopf_spur({s: [b, 100, 100] for s, (_x, _y, b) in GESICHT_GEDREHT.items()}, [100, 100, 100])
    # Liegen die Bilder schon da, und passen sie? Fehlt eines, zeigt Lottie
    # an seiner Stelle nichts - das soll nicht erst in der App auffallen.
    try:
        from haut_einbauen import webp_groesse
    except ImportError:
        webp_groesse = None
    _fehler = []
    for _a in ASSETS + [a for v in ZIERRAT_ASSETS.values() for a in v]:
        _p = os.path.join("web", "maskottchen", _a["u"], _a["p"])
        if not os.path.isfile(_p):
            _fehler.append("fehlt: " + _p)
        elif webp_groesse and webp_groesse(_p) != (_a["w"], _a["h"]):
            _fehler.append("%s ist %s gross, erwartet %dx%d" % (_p, webp_groesse(_p), _a["w"], _a["h"]))
    if _fehler:
        print("ACHTUNG, Bilder des Drachen:\n  " + "\n  ".join(_fehler[:8])
              + ("\n  ... und %d weitere" % (len(_fehler) - 8) if len(_fehler) > 8 else "")
              + "\n  Erst: python haut_einbauen.py --teile <Ordner mit den PNG-Teilen>"
              + "\n  bzw. --zierrat <Ordner mit den gemalten Kostuemen>")

built = {n: kompakt(L) for n, L in built.items()}
fehlt = [n for n in ORDER if n not in built]
assert not fehlt, "Ebenen in ORDER ohne Inhalt: %s" % fehlt
markers = [{"tm": a, "cm": n, "dr": b - a} for n, (a, b) in SEG.items()]
# Die Schriftenliste gehoert in die Grunddatei: die App setzt die Schnipsel
# auf sie auf, und ohne diesen Eintrag wuesste Lottie nicht, womit es den
# Schriftzug auf dem Fanschal setzen soll. Nunito liegt in web/fonts.
doc = {"v": "5.7.4", "fr": FR, "ip": 0, "op": OP, "w": W, "h": H, "nm": "Zmaj", "ddd": 0, "assets": ASSETS,
       "fonts": {"list": [{"fName": "ZmajFett", "fFamily": "Nunito",
                           "fStyle": "Bold", "fPath": "", "fWeight": "800",
                           "origin": 0, "ascent": 75}]},
       "layers": [built[n] for n in ORDER if n not in ZIERRAT_ALLE and n not in WEG_IM_BILD], "markers": markers}
os.makedirs(AUSGABE, exist_ok=True)
grund = os.path.join(AUSGABE, "zmaj.json")
with open(grund, "w", encoding="utf-8") as f:
    json.dump(doc, f, separators=(",", ":"))
print("%s, Kopf %.2f  %-20s %7d Bytes, %2d Ebenen, %d Bilder" % ("Vektor" if VEKTOR else "Bild", KOPF, "zmaj.json",
                                                              os.path.getsize(grund), len(doc["layers"]), len(ASSETS)))

# Jeder Schnipsel ist eine LISTE von Ebenen - meist eine, beim Fanschal zwei.
# Seit 16.10.2026 ist der Schnipsel eines gemalten Stuecks (GEMALT) ein
# Objekt {"layers": [...], "assets": [...]}: seine Bild-Ebenen und die
# Bilder dazu (zierrat/<stueck>/). zmajDaten() in web/index.html vertraegt
# alle drei Formen (dazu das einzelne Objekt der aeltesten Schnipsel).
gesamt = 0
for stueck in ZIERRAT:
    pfad = os.path.join(AUSGABE, "zmajz-%s.json" % stueck)
    if stueck in GEMALT:
        ebenen = [built["bild_%s_%s" % (stueck, e[0])] for e in GEMALT[stueck]]
        inhalt = {"layers": ebenen, "assets": ZIERRAT_ASSETS[stueck]}
    else:
        ebenen = [built[stueck]] + [built[n] for n in NUR_MIT.get(stueck, [])]
        inhalt = ebenen
    with open(pfad, "w", encoding="utf-8") as f:
        json.dump(inhalt, f, separators=(",", ":"))
    gesamt += os.path.getsize(pfad)
    print("   %-23s %7d Bytes  (%d Ebene%s, ind %s)"
          % (stueck, os.path.getsize(pfad), len(ebenen), "" if len(ebenen) == 1 else "n",
             ",".join(str(e["ind"]) for e in ebenen)))
print("%d Schmuckstücke, zusammen %d Bytes" % (len(ZIERRAT), gesamt))

# Die alten Vollfassungen je Stück werden nicht mehr gebraucht und würden
# sonst mit in die App wandern.
for alt in ["hut", "krone", "brille", "kopfhoerer"]:
    pfad = os.path.join(AUSGABE, "zmaj-%s.json" % alt)
    if os.path.exists(pfad):
        os.remove(pfad)
        print("entfernt: %s" % pfad)
