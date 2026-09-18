# -*- coding: utf-8 -*-
# Erzeugt web/maskottchen/zmaj.json: Drache "Zmaj" als Lottie-Animation.
# v5: Frontansicht (schaut den Lernenden an), sitzt auf einem Bücherstapel,
# runde weiche Formen.
# Stimmungen: idle, cheer, sad, ok, no, cry (Tränen), no_l, no_r.
#
# no_l und no_r sind zwei Fassungen für eine falsche Antwort: Der Drache
# wendet den Kopf ab – einmal nach links, einmal nach rechts – und schaut
# dabei traurig. Die App wechselt sich damit ab, damit es nach mehreren
# Fehlern nicht immer gleich aussieht.
# In Thonny ausführen (F5), dann App neu laden.
import json, os, math
os.chdir(os.path.dirname(os.path.abspath(__file__)))

W, H, FR = 520, 500, 30
CX, CY = 260, 290                       # Körpermitte
SEG = {"idle": (0, 90), "cheer": (90, 150), "sad": (150, 210), "ok": (210, 240), "no": (240, 270), "cry": (270, 360),
       "no_l": (360, 400), "no_r": (400, 440)}
OP = 440

def col(h): h = h.lstrip("#"); return [int(h[i:i+2], 16)/255 for i in (0, 2, 4)] + [1]
BLUE = col("2448B8"); BLUE_L = col("3F66DF"); BLUE_D = col("17307F"); WING = col("6C90FF"); WING_D = col("3A5CD0")
YEL = col("FFCB1F"); YEL_D = col("D9A400"); AMBER = col("F2A900"); WHITE = col("FFFFFF"); INK = col("0B1533")
# BOOK1_D nur fuer den Schatten am Buecherstapel. Frueher stand dort BLUE_D,
# also dieselbe Farbe wie die Drachenbeine - beim Umfaerben des Drachen waere
# der Stapel mitgegangen, obwohl er nicht zum Drachen gehoert.
BOOK1_D = col("122C74")
RED = col("7A1F2B"); TONGUE = col("FF7B8E"); TEAR = col("8FD3FF"); BOOK1 = col("1B3A9E"); BOOK2 = col("FFCB1F"); PAGE = col("FFF6DC")
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
DUNKELGLAS = col("1C1C24"); GLANZ = col("FFFFFF")
DOKTOR = col("23252B"); DOKTOR_H = col("454956")
STRICK = col("7B3F51"); STRICK_H = col("A85C72"); STRICK_D = col("55283A")   # Weinrot: hebt sich von Blau UND Gelb ab
GOLDR = col("C9A227")

# ---------- Keyframes ----------
def anim(pairs, dims=1):
    ks = []
    for idx, p in enumerate(pairs):
        t, v = p[0], p[1]; hold_ = len(p) > 2 and p[2]
        k = {"t": t, "s": v if isinstance(v, list) else [v]}
        if hold_: k["h"] = 1
        elif idx < len(pairs) - 1:
            k["i"] = {"x": [0.35]*dims, "y": [1]*dims}; k["o"] = {"x": [0.65]*dims, "y": [0]*dims}
        ks.append(k)
    return {"a": 1, "k": ks}
def const(v): return {"a": 0, "k": v}
def hold(t, v): return (t, v, True)

# ---------- Formen (Listen von unten nach oben; put() dreht um) ----------
def fill(c, o=100): return {"ty": "fl", "c": const(c), "o": const(o), "r": 1}
def stroke(c, w, o=100): return {"ty": "st", "c": const(c), "o": const(o), "w": const(w), "lc": 2, "lj": 2}
def ellipse(cx, cy, w, h): return {"ty": "el", "p": const([cx, cy]), "s": const([w, h])}
def rect(cx, cy, w, h, r=0): return {"ty": "rc", "p": const([cx, cy]), "s": const([w, h]), "r": const(r)}
def tr(r=0, o=100, p=(0, 0), s=(100, 100)):
    return {"ty": "tr", "p": const(list(p)), "a": const([0, 0]), "s": const(list(s)), "r": const(r), "o": const(o)}
def group(*items, r=0, o=100, p=(0, 0), s=(100, 100)): return {"ty": "gr", "it": list(items) + [tr(r, o, p, s)]}
def poly(points):   # Vieleck mit scharfen Ecken, z. B. für Zähne
    return {"ty": "sh", "ks": const({"c": True, "v": [list(p) for p in points], "i": [[0, 0]]*len(points), "o": [[0, 0]]*len(points)})}
def smooth(points, closed=True, tension=0.6, scharf=()):
    """Rundet die Ecken eines Streckenzugs. scharf = Nummern der Punkte, die
    trotzdem eine echte Ecke bleiben sollen - gebraucht fuer den V-Ausschnitt:
    eine gerundete Spitze saehe aus wie ein Rundhals."""
    n = len(points); v = []; it = []; ot = []
    scharf = set(scharf)
    for k in range(n):
        p0 = points[(k-1) % n] if closed else points[max(k-1, 0)]
        p1 = points[k]; p2 = points[(k+1) % n] if closed else points[min(k+1, n-1)]
        if k in scharf:
            tx = ty = 0
        else:
            tx = (p2[0]-p0[0]) * tension / 2; ty = (p2[1]-p0[1]) * tension / 2
        v.append([p1[0], p1[1]]); it.append([-tx, -ty]); ot.append([tx, ty])
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

# Zierrat aus dem Laden, in drei Gruppen - so wie die Reiter im Laden. Aus
# jeder Gruppe kann ein Stück getragen werden, alle drei zusammen.
#
# Wo eine Gruppe in ORDER steht, entscheidet, was was verdeckt:
#   Kopf und Brille liegen ganz vorn, über Augen, Hörnern und allem anderen.
#   Die Halssachen stehen HINTER dem Kopf und hinter den Armen, aber vor dem
#   Körper. Dadurch schiebt sich der Kopf über den oberen Rand des Schals,
#   genau wie bei einem echten Schal, und die Arme liegen auf der Weste.
KOPF_TEILE = ["hut", "krone", "fes", "kappe", "doktorhut", "ohrenschuetzer", "kopfhoerer"]
BRILLEN    = ["brille", "sonnenbrille", "lesebrille"]
HALS_TEILE = ["trikot", "schal_bih", "schal_winter", "weste_leder", "weste_strick"]
ZIERRAT = KOPF_TEILE + BRILLEN + HALS_TEILE
# Die drei Kleidungsstuecke bekommen Aermel. Das sind eigene Ebenen, denn sie
# haengen an den Armen und nicht am Koerper - die Arme wippen, ein am Koerper
# festgemachter Aermel bliebe stehen. Sie stehen in ORDER vor "armL", liegen
# also VOR den Armen und decken sie zu.
AERMEL_STUECKE = ["trikot", "weste_leder", "weste_strick"]
AERMEL = [s + "_" + a for s in AERMEL_STUECKE for a in ("armL", "armR")]
# Ebenen, die nur zusammen mit einem Stueck ausgeliefert werden. Der
# Schriftzug auf dem Fanschal ist die erste davon: er muss VOR dem Stoff
# liegen, ist aber eine eigene Ebene, weil Lottie Text nicht als Form kennt.
NUR_MIT = {"schal_bih": ["schal_bih_text"]}
NUR_MIT.update({s: [s + "_armL", s + "_armR"] for s in AERMEL_STUECKE})
ZIERRAT_ALLE = ZIERRAT + [n for v in NUR_MIT.values() for n in v]
# "hoerner" ganz vorn: die Hutebenen liegen dahinter, also ragen die Spitzen
# oben aus jedem Hut heraus, statt darunter zu verschwinden.
ORDER = ["hoerner"] + KOPF_TEILE + BRILLEN + \
        ["tears", "brows", "mouth_cry", "mouth_sad", "mouth_open", "mouth_idle",
         "eyes_cry", "eyes_happy", "lids", "eyes", "head"] + \
        AERMEL + ["armL", "armR"] + \
        ["schal_bih_text"] + HALS_TEILE + \
        ["body", "legs", "tail", "wingL", "wingR", "perch"]
IDX = {n: i+1 for i, n in enumerate(ORDER)}
built = {}
def put(name, shapes, parent=None, p=(0, 0), a=(0, 0), r=0, animk=None):
    L = {"ddd": 0, "ind": IDX[name], "ty": 4, "nm": name, "sr": 1,
         "ks": {"o": const(100), "r": const(r), "p": const([p[0], p[1], 0]), "a": const([a[0], a[1], 0]), "s": const([100, 100, 100])},
         "ao": 0, "shapes": list(reversed(shapes)), "ip": 0, "op": OP, "st": 0, "bm": 0}
    if parent: L["parent"] = IDX[parent]
    if animk: L["ks"].update(animk)
    built[name] = L

def textebene(name, wort, x, y, groesse, farbe, parent, sperrung=-30):
    """Eine Lottie-Textebene. Lottie kennt keine Buchstaben als Formen - es
    schreibt echten Text und ueberlaesst die Schrift dem Anzeigeprogramm.
    Deshalb steht unten in der Datei eine Schriftenliste; "ZmajFett" zeigt
    auf Nunito, die Schrift der Oberflaeche, die in web/fonts liegt.
    j=2 heisst mittig, tr ist die Sperrung in Tausendstel Geviert."""
    return {"ddd": 0, "ind": IDX[name], "ty": 5, "nm": name, "sr": 1,
            "parent": IDX[parent], "ao": 0,
            "ks": {"o": const(100), "r": const(0), "p": const([x, y, 0]),
                   "a": const([0, 0, 0]), "s": const([100, 100, 100])},
            "t": {"d": {"k": [{"s": {"s": groesse, "f": "ZmajFett", "t": wort,
                                     "j": 2, "tr": sperrung, "lh": groesse * 1.2,
                                     "ls": 0, "fc": farbe[:3]}, "t": 0}]},
                  "p": {}, "m": {"g": 1, "a": const([0, 0])}, "a": []},
            "ip": 0, "op": OP, "st": 0, "bm": 0}


def P(dx=0, dy=0): return [CX+dx, CY+dy, 0]
S3 = lambda x, y: [x, y, 100]

# ---------- Zeitleisten ----------
body_pos = anim([(0, P()), (45, P(0, -6)), (90, P()),
    hold(90, P()), (96, P(0, 8)), (104, P(0, -48)), (112, P(0, 2)), (118, P()), (124, P(0, 8)), (132, P(0, -48)), (140, P(0, 2)), (150, P()),
    hold(150, P()), (162, P(0, 10)), (185, P(0, 12)), (210, P(0, 10)),
    hold(210, P()), (214, P(0, 6)), (220, P(0, -22)), (226, P(0, 2)), (232, P()), (240, P()),
    hold(240, P()), (250, P(-3)), (260, P(3)), (270, P()),
    hold(270, P(0, 10)), (276, P(-2, 12)), (282, P(2, 10)), (288, P(-2, 12)), (294, P(2, 10)), (300, P(-2, 12)), (306, P(2, 10)), (312, P(-2, 12)), (318, P(2, 10)), (324, P(-2, 12)), (330, P(2, 10)), (336, P(-2, 12)), (342, P(2, 10)), (348, P(-2, 12)), (354, P(2, 10)), (360, P(0, 10)),
    hold(360, P(0, 8)), (374, P(-4, 11)), (392, P(-4, 11)), (400, P(0, 9)),
    hold(400, P(0, 8)), (414, P(4, 11)), (432, P(4, 11)), (440, P(0, 9))])
body_scale = anim([(0, S3(100, 100)), (45, S3(102, 98)), (90, S3(100, 100)),
    hold(90, S3(100, 100)), (96, S3(114, 86)), (104, S3(92, 108)), (112, S3(108, 93)), (118, S3(100, 100)), (124, S3(114, 86)), (132, S3(92, 108)), (140, S3(108, 93)), (150, S3(100, 100)),
    hold(150, S3(100, 100)), (162, S3(105, 95)), (185, S3(106, 94)), (210, S3(105, 95)),
    hold(210, S3(100, 100)), (214, S3(112, 88)), (220, S3(94, 108)), (226, S3(105, 96)), (232, S3(100, 100)), (240, S3(100, 100)),
    hold(240, S3(100, 100)), (270, S3(100, 100)),
    hold(270, S3(105, 95)), (300, S3(104, 96)), (330, S3(106, 94)), (360, S3(105, 95)),
    hold(360, S3(103, 97)), (380, S3(104, 96)), (400, S3(103, 97)),
    hold(400, S3(103, 97)), (420, S3(104, 96)), (440, S3(103, 97))], dims=3)
head_rot = anim([(0, 0), (30, -4), (60, 3), (90, 0),
    hold(90, 0), (96, 5), (104, -12), (112, 4), (118, 0), (124, 5), (132, -12), (140, 4), (150, 0),
    hold(150, 0), (165, 8), (210, 8),
    hold(210, 0), (214, 5), (220, -10), (228, 2), (240, 0),
    hold(240, 0), (247, -4), (254, 4), (261, -3), (266, 2), (270, 0),
    hold(270, 6), (285, 10), (300, 6), (315, 10), (330, 6), (345, 10), (360, 6),
    hold(360, 2), (374, -11), (392, -9), (400, 0),
    hold(400, -2), (414, 11), (432, 9), (440, 0)])
# Bei „falsch“ schüttelt der Kopf seitlich (Verschiebung), er kippt nicht.
head_pos = anim([(0, [0, -60, 0]), hold(90, [0, -60, 0]), hold(150, [0, -60, 0]), (165, [0, -50, 0]), (210, [0, -50, 0]),
    hold(210, [0, -60, 0]),
    hold(240, [0, -60, 0]), (247, [-16, -60, 0]), (254, [16, -60, 0]), (261, [-11, -60, 0]), (266, [7, -60, 0]), (270, [0, -60, 0]),
    hold(270, [0, -50, 0]), (360, [0, -50, 0]),
    # no_l: Kopf nach links abwenden und dort bleiben
    hold(360, [0, -56, 0]), (374, [-24, -54, 0]), (392, [-24, -54, 0]), (400, [-9, -56, 0]),
    # no_r: dasselbe nach rechts
    hold(400, [0, -56, 0]), (414, [24, -54, 0]), (432, [24, -54, 0]), (440, [9, -56, 0])])
def wing_rot(sg):
    return anim([(0, 0), (40, 10*sg), (72, -3*sg), (90, 0),
        hold(90, 0), (96, -10*sg), (104, 30*sg), (112, -8*sg), (118, 18*sg), (124, -10*sg), (132, 30*sg), (140, -8*sg), (150, 0),
        hold(150, 0), (165, -18*sg), (210, -18*sg), hold(210, 0), (214, -8*sg), (220, 20*sg), (230, -4*sg), (240, 0),
        hold(240, 0), (250, -8*sg), (260, 5*sg), (270, 0), hold(270, -18*sg), (360, -18*sg),
        hold(360, -16*sg), (400, -16*sg), hold(400, -16*sg), (440, -16*sg)])
tail_rot = anim([(0, 0), (45, -8), (90, 0), hold(90, 0), (98, 12), (106, -12), (114, 12), (122, -12), (130, 12), (138, -12), (150, 0),
    hold(150, 0), (165, 8), (210, 8), hold(210, 0), (218, -10), (232, 0), (240, 0), hold(240, 0), (255, 5), (270, 0), hold(270, 8), (360, 8),
    hold(360, 6), (378, -8), (400, 2), hold(400, 6), (418, 16), (440, 8)])
lids_scale = anim([(0, S3(100, 0)), (28, S3(100, 0)), (31, S3(100, 100)), (34, S3(100, 0)), (62, S3(100, 0)), (65, S3(100, 100)), (68, S3(100, 0)), (90, S3(100, 0)),
    hold(90, S3(100, 0)), hold(150, S3(100, 0)), (162, S3(100, 45)), (210, S3(100, 45)),
    hold(210, S3(100, 0)), hold(240, S3(100, 0)), (270, S3(100, 0)), hold(270, S3(100, 0)), (360, S3(100, 0)),
    hold(360, S3(100, 42)), (400, S3(100, 42)), hold(400, S3(100, 42)), (440, S3(100, 42))], dims=3)
pupil_pos = anim([(0, [0, 0, 0]), (25, [5, 1, 0]), (45, [5, 1, 0]), (60, [-5, 1, 0]), (75, [-5, 1, 0]), (90, [0, 0, 0]),
    hold(90, [0, 0, 0]), hold(150, [0, 0, 0]), (162, [0, 6, 0]), (210, [0, 6, 0]), hold(210, [0, 0, 0]), (218, [0, -3, 0]), (232, [0, 0, 0]),
    hold(240, [0, 0, 0]), (270, [0, 0, 0]), hold(270, [0, 0, 0]), (360, [0, 0, 0]),
    # Blick weicht mit aus: erst zur Seite, am Ende halb zurück
    hold(360, [0, 3, 0]), (372, [-9, 4, 0]), (392, [-9, 4, 0]), (400, [-4, 3, 0]),
    hold(400, [0, 3, 0]), (412, [9, 4, 0]), (432, [9, 4, 0]), (440, [4, 3, 0])])
def opa(on):
    ks = [hold(a, 100 if n in on else 0) for n, (a, b) in SEG.items()]
    ks.append(hold(OP, 100 if "idle" in on else 0)); return anim(ks)
brow_l = anim([(0, -6), hold(90, -6), (98, -14), (150, -14), hold(150, -6), (162, 18), (210, 18), hold(210, -6), (216, -14), (232, -6), hold(240, -6), (246, -24), (262, -24), (270, -6), hold(270, 22), (360, 22),
    hold(360, 17), (400, 17), hold(400, 17), (440, 17)])
brow_r = anim([(0, 6), hold(90, 6), (98, 14), (150, 14), hold(150, 6), (162, -18), (210, -18), hold(210, 6), (216, 14), (232, 6), hold(240, 6), (246, 24), (262, 24), (270, 6), hold(270, -22), (360, -22),
    hold(360, -17), (400, -17), hold(400, -17), (440, -17)])
arm_l = anim([(0, 28), (45, 34), (90, 28), hold(90, 28), (100, -130), (110, -110), (120, -130), (130, -110), (140, -130), (150, 28),
    hold(150, 28), (165, 44), (210, 44), hold(210, 28), (218, -80), (232, 28), (240, 28), hold(240, 28), (270, 28), hold(270, 60), (360, 60),
    hold(360, 42), (376, 48), (400, 44), hold(400, 42), (416, 48), (440, 44)])
arm_r = anim([(0, -28), (45, -34), (90, -28), hold(90, -28), (100, 130), (110, 110), (120, 130), (130, 110), (140, 130), (150, -28),
    hold(150, -28), (165, -44), (210, -44), hold(210, -28), (218, 80), (232, -28), (240, -28), hold(240, -28), (270, -28), hold(270, -60), (360, -60),
    hold(360, -42), (376, -48), (400, -44), hold(400, -42), (416, -48), (440, -44)])
mouth_cry_scale = anim([hold(0, S3(100, 100)), hold(270, S3(100, 100)), (278, S3(108, 92)), (286, S3(94, 108)), (294, S3(108, 92)), (302, S3(94, 108)), (310, S3(108, 92)), (318, S3(94, 108)), (326, S3(108, 92)), (334, S3(94, 108)), (342, S3(108, 92)), (350, S3(94, 108)), (360, S3(100, 100))], dims=3)
def tear_anim(start, x0, y0):
    """Ein Tropfen: fällt, wird durchsichtig, wiederholt sich zweimal im cry-Abschnitt."""
    ks = [hold(0, [x0, y0, 0]), hold(270, [x0, y0, 0])]
    t = 270 + start
    for _ in range(2):
        ks += [hold(t, [x0, y0, 0]), (t+1, [x0, y0, 0]), (t+38, [x0, y0+70, 0])]
        t += 45
    ks.append(hold(360, [x0, y0, 0]))
    return anim(ks)
def tear_opa(start):
    ks = [hold(0, 0), hold(270, 0)]
    t = 270 + start
    for _ in range(2):
        ks += [hold(t, 100), (t+24, 100), (t+38, 0), hold(t+39, 0)]
        t += 45
    ks.append(hold(360, 0)); return anim(ks)

# ---------- Sitzplatz: Bücherstapel ----------
put("perch", [group(rect(0, 26, 300, 46, 14), fill(BOOK1)), group(rect(8, 22, 300, 14, 6), fill(PAGE)), group(rect(0, 42, 300, 8, 4), fill(BOOK1_D, 60)),
              group(rect(-6, -22, 250, 44, 14), fill(BOOK2)), group(rect(2, -26, 250, 14, 6), fill(PAGE)), group(rect(-6, -6, 250, 8, 4), fill(YEL_D, 55)),
              group(ellipse(0, 52, 320, 26), fill(INK, 12))],
    p=(CX, 420))

# ---------- Körper ----------
put("body", [group(smooth([(-74, -10), (-40, -70), (40, -70), (74, -10), (66, 58), (0, 76), (-66, 58)], tension=0.6), fill(BLUE)),
             group(smooth([(-50, 4), (-20, -30), (20, -30), (50, 4), (44, 58), (0, 70), (-44, 58)], tension=0.6), fill(YEL)),
             group(arc((-36, 6), (36, 6), 8), stroke(YEL_D, 3.5, 50)), group(arc((-40, 22), (40, 22), 8), stroke(YEL_D, 3.5, 50)),
             group(arc((-36, 38), (36, 38), 7), stroke(YEL_D, 3.5, 50)), group(arc((-26, 54), (26, 54), 5), stroke(YEL_D, 3.5, 50)),
             group(ellipse(-26, -46, 44, 24), fill(BLUE_L, 35))],
    p=(CX, CY), animk={"p": body_pos, "s": body_scale})
put("legs", [group(smooth([(-76, 30), (-40, 24), (-30, 62), (-50, 80), (-84, 72)], tension=0.6), fill(BLUE_D)),
             group(smooth([(76, 30), (40, 24), (30, 62), (50, 80), (84, 72)], tension=0.6), fill(BLUE_D)),
             group(ellipse(-62, 82, 62, 26), fill(YEL)), group(ellipse(62, 82, 62, 26), fill(YEL)),
             group(ellipse(-82, 88, 16, 14), fill(AMBER)), group(ellipse(-62, 92, 16, 14), fill(AMBER)), group(ellipse(-42, 88, 16, 14), fill(AMBER)),
             group(ellipse(82, 88, 16, 14), fill(AMBER)), group(ellipse(62, 92, 16, 14), fill(AMBER)), group(ellipse(42, 88, 16, 14), fill(AMBER))],
    parent="body")
put("armL", [group(ellipse(-20, 2, 52, 28), fill(BLUE_D)), group(ellipse(-44, 6, 26, 22), fill(BLUE_L)),
             group(ellipse(-56, 4, 10, 8), fill(AMBER)), group(ellipse(-54, 12, 10, 8), fill(AMBER))], parent="body", p=(-58, -8), animk={"r": arm_l})
put("armR", [group(ellipse(20, 2, 52, 28), fill(BLUE_D)), group(ellipse(44, 6, 26, 22), fill(BLUE_L)),
             group(ellipse(56, 4, 10, 8), fill(AMBER)), group(ellipse(54, 12, 10, 8), fill(AMBER))], parent="body", p=(58, -8), animk={"r": arm_r})

tail_c = [(0, 0), (-40, 34), (-100, 44), (-150, 20), (-176, -20)]
put("tail", [group(taper(tail_c, [40, 32, 24, 16, 10]), fill(BLUE)),
             bump(-40, 22, 20, 14), bump(-100, 32, 18, 12), bump(-150, 12, 14, 10),
             group(smooth([(-176, -20), (-198, -34), (-206, -14), (-190, 2), (-168, -6)], tension=0.65), fill(YEL))],
    parent="body", p=(-30, 56), animk={"r": tail_rot})

# Flügel wie beim klassischen Drachen: OBEN ein glatter runder Bogen (Armknochen),
# UNTEN die Membran mit weichen Zacken zwischen den Fingern.
WING_TIPS = [(-160, -98), (-166, -44), (-146, 6), (-96, 34)]     # Zacken an der Unterkante
wing_pts = [(0, 0),                                   # Schulter
            (-38, -58), (-88, -112), (-130, -130),    # Oberkante: runder Bogen
            (-160, -98),                              # Zacke 1
            (-126, -82),                              # Tal
            (-166, -44),                              # Zacke 2
            (-122, -36),                              # Tal
            (-146, 6),                                # Zacke 3
            (-98, -6),                                # Tal
            (-96, 34),                                # Zacke 4
            (-50, 6), (-16, 14)]                      # zurück zum Körper
def wing_shapes(pts, sg):
    knochen = [group(arc((0, 0), (x*sg, y), -6*sg), stroke(WING_D, 3.5, 38)) for x, y in WING_TIPS[:3]]
    schatten = [(x*sg, y) for x, y in [(0, 0), (-34, -52), (-80, -102), (-118, -118), (-96, -96), (-56, -58), (-16, -12)]]
    return [group(smooth(pts, tension=0.42), fill(WING)),
            group(smooth(schatten, tension=0.5), fill(WING_D, 20))] \
           + knochen + [group(taper([(0, 0), (-64*sg, -84), (-130*sg, -130)], [19, 13, 7]), fill(BLUE_L))]
put("wingL", wing_shapes(wing_pts, 1), parent="body", p=(-48, -44), animk={"r": wing_rot(1)})
put("wingR", wing_shapes(mirror(wing_pts), -1), parent="body", p=(48, -44), animk={"r": wing_rot(-1)})

# ---------- Kopf (schaut nach vorn) ----------
# Die drei oberen Hörner stehen hier für sich, weil sie zweimal gebraucht
# werden: einmal im Kopf und einmal als Ebene davor, die über den Hüten liegt.
HORN_OBEN = [
    group(smooth([(0, 0), (-16, -28), (-10, -70), (14, -46), (20, -10)], tension=0.65), fill(AMBER), p=(-52, -118)),
    group(smooth([(0, 0), (16, -28), (10, -70), (-14, -46), (-20, -10)], tension=0.65), fill(AMBER), p=(52, -118)),
    bump(0, -128, 26, 34),
]
head_shapes = [
    group(ellipse(0, -60, 156, 136), fill(BLUE)),
    group(ellipse(0, -22, 96, 58), fill(BLUE_L, 70)),                             # Schnauze
    group(ellipse(-18, -30, 9, 6), fill(INK, 55)), group(ellipse(18, -30, 9, 6), fill(INK, 55)),
    group(ellipse(-58, -44, 26, 20), fill(BLUE_L, 45)), group(ellipse(58, -44, 26, 20), fill(BLUE_L, 45)),   # Wangen, nur leichte Wölbung
    # Hörner statt Ohren: zwei große oben, zwei kleinere seitlich, eines in der Mitte.
    # Die drei oberen stehen weiter unten NOCH EINMAL als eigene Ebene, die vor
    # den Hüten liegt – dadurch spießen sie jeden Hut auf, statt darunter zu
    # verschwinden. Hier bleiben sie trotzdem, sonst fehlten sie ohne Hut.
    *HORN_OBEN,
    group(smooth([(0, 0), (-10, -18), (-6, -44), (10, -28), (13, -6)], tension=0.65), fill(YEL), p=(-76, -76), r=-52),
    group(smooth([(0, 0), (10, -18), (6, -44), (-10, -28), (-13, -6)], tension=0.65), fill(YEL), p=(76, -76), r=52),
    group(ellipse(-34, -98, 46, 16), fill(WHITE, 14), r=-25),
]
put("head", head_shapes, parent="body", p=(0, -60), animk={"r": head_rot, "p": head_pos})
# Augen: Weiß fest, darüber eine bewegliche Gruppe aus Iris, Pupille und Glanzlicht.
# Wichtig: in einer Lottie-Gruppe färbt eine Füllung alle folgenden Formen mit,
# darum bekommt jede Form ihre eigene Untergruppe. Reihenfolge hier: oben zuerst.
put("eyes", [group(ellipse(-32, -74, 46, 52), fill(WHITE)), group(ellipse(32, -74, 46, 52), fill(WHITE)),
             {"ty": "gr", "it": [
                 group(ellipse(-24, -62, 5, 5), fill(WHITE, 70)), group(ellipse(38, -62, 5, 5), fill(WHITE, 70)),   # kleiner Glanz unten
                 group(ellipse(-37, -83, 11, 11), fill(WHITE)), group(ellipse(25, -83, 11, 11), fill(WHITE)),        # Glanzlicht
                 group(ellipse(-30, -72, 19, 26), fill(INK)), group(ellipse(32, -72, 19, 26), fill(INK)),            # Pupille
                 group(ellipse(-30, -72, 31, 35), fill(AMBER)), group(ellipse(32, -72, 31, 35), fill(AMBER)),        # Iris
                 {"ty": "tr", "p": pupil_pos, "a": const([0, 0]), "s": const([100, 100]), "r": const(0), "o": const(100)}]}],
    parent="head", animk={"o": opa({"idle", "sad", "ok", "no", "no_l", "no_r"})})
put("lids", [group(ellipse(-32, -74, 48, 54), fill(BLUE)), group(ellipse(32, -74, 48, 54), fill(BLUE))],
    parent="head", p=(0, -101), a=(0, -101), animk={"s": lids_scale})
put("eyes_happy", [group(arc((-52, -70), (-12, -70), -22), stroke(INK, 5.5)), group(arc((12, -70), (52, -70), -22), stroke(INK, 5.5))],
    parent="head", animk={"o": opa({"cheer"})})
put("eyes_cry", [group(arc((-52, -78), (-12, -78), 18), stroke(INK, 5.5)), group(arc((12, -78), (52, -78), 18), stroke(INK, 5.5))],
    parent="head", animk={"o": opa({"cry"})})
# Zähne: spitze Fangzähne, die aus dem Oberkiefer nach unten ragen
put("mouth_idle", [group(arc((-30, -8), (30, -8), 16), stroke(INK, 4.5)),
                   group(poly([(-21, 0), (-14, 15), (-7, 1)]), fill(WHITE)),
                   group(poly([(7, 1), (14, 15), (21, 0)]), fill(WHITE))],
    parent="head", animk={"o": opa({"idle"})})
put("mouth_open", [group(smooth([(-38, -12), (0, -4), (38, -12), (26, 22), (0, 32), (-26, 22)], tension=0.6), fill(RED)),
                   group(ellipse(0, 16, 34, 18), fill(TONGUE)),
                   group(poly([(-28, -9), (-21, 9), (-14, -10)]), fill(WHITE)), group(poly([(14, -10), (21, 9), (28, -9)]), fill(WHITE)),
                   group(poly([(-17, 27), (-12, 13), (-7, 27)]), fill(WHITE)), group(poly([(7, 27), (12, 13), (17, 27)]), fill(WHITE))],
    parent="head", animk={"o": opa({"cheer", "ok"})})
put("mouth_sad", [group(arc((-26, 0), (26, 0), -16), stroke(INK, 4.5))], parent="head", animk={"o": opa({"sad", "no", "no_l", "no_r"})})
put("mouth_cry", [group(smooth([(-28, -10), (28, -10), (24, 26), (0, 34), (-24, 26)], tension=0.6), fill(RED)),
                  group(ellipse(0, 20, 26, 14), fill(TONGUE))],
    parent="head", p=(0, 0), a=(0, 0), animk={"o": opa({"cry"}), "s": mouth_cry_scale})
put("brows", [group(rect(0, 0, 40, 9, 4.5), fill(INK), p=(-32, -108)), group(rect(0, 0, 40, 9, 4.5), fill(INK), p=(32, -108))], parent="head")
built["brows"]["shapes"][1]["it"][-1]["r"] = brow_l
built["brows"]["shapes"][0]["it"][-1]["r"] = brow_r

drop = smooth([(0, -12), (7, 0), (0, 9), (-7, 0)], tension=0.7)
tears_shapes = []
for k, (start, x0, y0) in enumerate([(0, -50, -52), (18, 50, -52), (30, -46, -52), (9, 46, -52)]):
    tears_shapes.append({"ty": "gr", "it": [drop, fill(TEAR, 90), {"ty": "tr", "p": tear_anim(start, x0, y0), "a": const([0, 0]), "s": const([100, 100]), "r": const(0), "o": tear_opa(start)}]})
put("tears", tears_shapes, parent="head")

# Nur die SPITZEN der beiden großen Hörner, als Ebene vor den Hüten. Ihre
# untere Kante liegt bei y = -150 und damit unter der Oberkante jedes Hutes;
# dadurch verschwindet sie hinter dem Hut, und es sieht aus, als käme das
# Horn oben heraus. Ganze Hörner davor hatten den Hut dahinter erdrückt.
# Das mittlere Horn bleibt hinten - es ist kurz, ein Hut darf es zudecken.
SPITZE = [(-15.5, -32), (-10, -70), (16.5, -32)]
put("hoerner", [
    group(smooth(SPITZE, tension=0.65), fill(AMBER), p=(-52, -118)),
    group(smooth([(-x, y) for x, y in SPITZE], tension=0.65), fill(AMBER), p=(52, -118)),
], parent="head")

# ======================= Kopfsachen =======================
# Alle sitzen mit ihrem unteren Rand zwischen y = -96 und -104. Dort ist der
# Schädel 59 bis 66 breit (Mittelpunkt 0/-60, Halbachsen 78 und 68), und nur
# so breit dürfen sie sein. Vorher saßen sie bei -124, wo der Schädel noch
# +-31 misst - deshalb hingen sie in der Luft.

# ---------- Bommelmütze ----------
put("hut", [
    group(smooth([(-68, -94), (-56, -144), (0, -168), (56, -144), (68, -94)], tension=0.62), fill(HUT)),
    group(smooth([(-32, -120), (-12, -150), (8, -160)], closed=False, tension=0.5), stroke(HUT_D, 5, 38)),
    group(rect(0, -96, 146, 27, 13), fill(HUT_HELL)),                 # Umschlag
    group(rect(0, -107, 146, 8, 4), fill(HUT_D, 20)),                 # Schatten darunter
    group(ellipse(0, -174, 32, 32), fill(HUT_HELL)),                  # Bommel
], parent="head")

# ---------- Krone ----------
put("krone", [
    group(rect(0, -100, 136, 24, 7), fill(KRONE)),                    # Reif
    group(rect(0, -92, 136, 8, 4), fill(KRONE_D, 35)),
    group(smooth([(-66, -98), (-66, -152), (-40, -128), (-20, -164),
                  (0, -130), (20, -164), (40, -128), (66, -152), (66, -98)], tension=0.12), fill(KRONE)),
    group(ellipse(-20, -164, 16, 16), fill(STEIN)),
    group(ellipse(20, -164, 16, 16), fill(STEIN)),
    group(ellipse(0, -130, 14, 14), fill(STEIN)),
], parent="head")

# ---------- Fes ----------
put("fes", [
    group(smooth([(-64, -96), (-55, -172), (55, -172), (64, -96)], tension=0.06), fill(FES)),
    group(ellipse(0, -172, 112, 19), fill(FES_D)),                    # Deckel von leicht oben
    group(rect(0, -100, 124, 9, 4), fill(FES_D, 28)),
    group(smooth([(10, -174), (46, -158), (62, -128)], closed=False, tension=0.5), stroke(QUASTE, 5)),
    group(rect(64, -110, 16, 32, 7), fill(QUASTE)),                   # Quaste hängt neben dem Hut
    group(rect(64, -96, 16, 7, 3), fill(QUASTE)),
], parent="head")

# ---------- Kappe, verkehrt herum ----------
put("kappe", [
    group(smooth([(-70, -94), (-60, -142), (0, -162), (60, -142), (70, -94)], tension=0.6), fill(KAPPE)),
    group(smooth([(-30, -104), (-16, -146), (0, -158)], closed=False, tension=0.5), stroke(KAPPE_D, 4, 42)),
    group(smooth([(30, -104), (16, -146), (0, -158)], closed=False, tension=0.5), stroke(KAPPE_D, 4, 42)),
    group(ellipse(0, -160, 15, 15), fill(KAPPE_D)),
    group(rect(0, -98, 144, 20, 10), fill(KAPPE_D)),                  # Bund
    group(rect(0, -98, 46, 14, 7), fill(KAPPE_H)),                    # Verschlussriemen
    group(ellipse(-10, -98, 6, 6), fill(KAPPE_D)),
    group(ellipse(10, -98, 6, 6), fill(KAPPE_D)),
], parent="head")

# ---------- Doktorhut ----------
put("doktorhut", [
    group(smooth([(-62, -94), (-57, -132), (57, -132), (62, -94)], tension=0.1), fill(DOKTOR)),
    group(rect(0, -98, 128, 11, 5), fill(DOKTOR_H, 40)),
    group(poly([(-104, -136), (0, -170), (104, -136), (0, -104)]), fill(DOKTOR)),   # Brett
    group(poly([(-104, -136), (0, -170), (104, -136), (0, -104)]), stroke(DOKTOR_H, 3, 50)),
    group(ellipse(0, -136, 16, 16), fill(GOLDR)),
    group(smooth([(0, -136), (56, -130), (90, -118)], closed=False, tension=0.5), stroke(GOLDR, 5)),
    group(rect(92, -100, 14, 34, 6), fill(GOLDR)),                    # Quaste
], parent="head")

# ---------- Ohrenschützer ----------
# Neu gezeichnet: ein schmaler Bügel und zwei satte, runde Polster mit hellem
# Kern. Die gezackte "Fell"-Kontur von vorher sah aus wie zwei Blumen.
put("ohrenschuetzer", [
    group(smooth([(-72, -88), (-46, -140), (0, -152), (46, -140), (72, -88)], closed=False, tension=0.55),
          stroke(WOLLE_D, 11)),
    group(smooth([(-64, -98), (-38, -134), (0, -144)], closed=False, tension=0.5), stroke(WOLLE, 5, 50)),
    # Kein heller Kern mehr: mit Kern lasen sich die Polster wie ein zweites
    # Augenpaar. Jetzt satte Wolle, ein weicher Schatten und ein kleiner
    # Glanz oben links - das liest sich als weiches Kissen.
    group(ellipse(-78, -60, 54, 62), fill(WOLLE)),
    group(ellipse(78, -60, 54, 62), fill(WOLLE)),
    group(ellipse(-78, -52, 46, 40), fill(WOLLE_D, 40)),
    group(ellipse(78, -52, 46, 40), fill(WOLLE_D, 40)),
    group(ellipse(-86, -74, 16, 12), fill(FELL, 40), r=-20),
    group(ellipse(70, -74, 16, 12), fill(FELL, 40), r=20),
], parent="head")

# ---------- Kopfhörer ----------
# Auch neu: Bügel mit Polster oben, Muscheln mit Ring und Glanz statt zweier
# flacher Ellipsen.
put("kopfhoerer", [
    group(smooth([(-76, -86), (-48, -142), (0, -156), (48, -142), (76, -86)], closed=False, tension=0.55),
          stroke(KH, 13)),
    group(smooth([(-30, -148), (0, -156), (30, -148)], closed=False, tension=0.5), stroke(KH_HELL, 9, 70)),
    group(rect(-76, -74, 16, 30, 7), fill(KH)),                       # Aufhängung links
    group(rect(76, -74, 16, 30, 7), fill(KH)),
    group(rect(-79, -62, 48, 66, 20), fill(KH)),                      # Muschel links
    group(rect(79, -62, 48, 66, 20), fill(KH)),
    group(rect(-79, -62, 32, 48, 14), fill(KH_POLSTER)),              # Polster
    group(rect(79, -62, 32, 48, 14), fill(KH_POLSTER)),
    group(ellipse(-84, -76, 10, 14), fill(WHITE, 30)),
    group(ellipse(74, -76, 10, 14), fill(WHITE, 30)),
], parent="head")

# ======================= Brillen =======================
# Unveraendert - die gefielen.

# ---------- Runde Brille ----------
put("brille", [
    group(smooth([(-78, -86), (-58, -80), (-54, -76)], closed=False, tension=0.5), stroke(RAHMEN, 6)),
    group(smooth([(78, -86), (58, -80), (54, -76)], closed=False, tension=0.5), stroke(RAHMEN, 6)),
    group(rect(0, -74, 24, 6, 3), fill(RAHMEN)),
    group(ellipse(-32, -74, 52, 52), fill(GLAS, 28)),
    group(ellipse(-32, -74, 52, 52), stroke(RAHMEN, 7)),
    group(ellipse(32, -74, 52, 52), fill(GLAS, 28)),
    group(ellipse(32, -74, 52, 52), stroke(RAHMEN, 7)),
], parent="head")

# ---------- Sonnenbrille ----------
put("sonnenbrille", [
    group(smooth([(-82, -92), (-62, -84), (-56, -78)], closed=False, tension=0.5), stroke(RAHMEN, 6)),
    group(smooth([(82, -92), (62, -84), (56, -78)], closed=False, tension=0.5), stroke(RAHMEN, 6)),
    group(rect(0, -84, 26, 8, 4), fill(RAHMEN)),
    group(rect(-33, -76, 58, 46, 12), fill(DUNKELGLAS)),
    group(rect(33, -76, 58, 46, 12), fill(DUNKELGLAS)),
    group(rect(-33, -76, 58, 46, 12), stroke(RAHMEN, 5)),
    group(rect(33, -76, 58, 46, 12), stroke(RAHMEN, 5)),
    group(smooth([(-52, -86), (-38, -93)], closed=False), stroke(GLANZ, 5, 40)),
    group(smooth([(14, -86), (28, -93)], closed=False), stroke(GLANZ, 5, 40)),
], parent="head")

# ---------- Lesebrille ----------
put("lesebrille", [
    group(smooth([(-74, -60), (-58, -52), (-52, -46)], closed=False, tension=0.5), stroke(GOLDR, 4)),
    group(smooth([(74, -60), (58, -52), (52, -46)], closed=False, tension=0.5), stroke(GOLDR, 4)),
    group(rect(0, -46, 20, 4, 2), fill(GOLDR)),
    group(ellipse(-30, -46, 42, 38), fill(GLAS, 24)),
    group(ellipse(30, -46, 42, 38), fill(GLAS, 24)),
    group(ellipse(-30, -46, 42, 38), stroke(GOLDR, 4.5)),
    group(ellipse(30, -46, 42, 38), stroke(GOLDR, 4.5)),
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
KOERPER = [(-78, -8), (-42, -68), (42, -68), (78, -8), (69, 58), (0, 76), (-69, 58)]

# Derselbe Umriss, aber oben eingekerbt: da guckt der Hals durch.
# Die drei Punkte der Kerbe sind "scharf", damit die Spitze spitz bleibt.
# Die Zahl in AUSSCHNITT ist die Nummer der Punkte 2, 3 und 4.
AUSSCHNITT = (2, 3, 4)
#                                     +-- Ausschnitt --+
KOERPER_V = [(-78, -8), (-42, -68), (-22, -62), (0, -32), (22, -62), (42, -68),
             (78, -8), (69, 58), (0, 76), (-69, 58)]
# Die Strickjacke traegt den Ausschnitt tiefer, so wie eine echte V-Jacke.
KOERPER_V_TIEF = [(-78, -8), (-42, -68), (-26, -60), (0, -22), (26, -60), (42, -68),
                  (78, -8), (69, 58), (0, 76), (-69, 58)]

# ---------- Zmajevi-Trikot ----------
# Nach dem Bild, das Ajdin am 18.09.2026 geschickt hat: tiefblau, duenne
# goldene Laengsstreifen, Wappen links auf der Brust, goldener Kragen.
# Die Streifen enden oben und unten innerhalb des Umrisses, damit sie nicht
# ueber den Rand hinauslaufen - in Lottie gibt es hier keine Maske.
put("trikot", [
    group(smooth(KOERPER_V, tension=0.6, scharf=AUSSCHNITT), fill(TRIKOT)),
    group(smooth([(-46, -52), (-50, 48)], closed=False), stroke(TRIKOT_H, 3, 75)),
    group(smooth([(-23, -56), (-25, 56)], closed=False), stroke(TRIKOT_H, 3, 75)),
    # Der mittlere Streifen faengt erst UNTER der Spitze des Ausschnitts an,
    # sonst schwebte er mitten im Loch.
    group(smooth([(0, -26), (0, 60)], closed=False), stroke(TRIKOT_H, 3, 75)),
    group(smooth([(23, -56), (25, 56)], closed=False), stroke(TRIKOT_H, 3, 75)),
    group(smooth([(46, -52), (50, 48)], closed=False), stroke(TRIKOT_H, 3, 75)),
    # Wappen: angedeutet, mehr ist bei dieser Groesse nicht zu erkennen
    group(smooth([(-46, -44), (-26, -44), (-26, -20), (-36, -12), (-46, -20)], tension=0.25), fill(TRIKOT_D)),
    group(poly([(-44, -42), (-28, -42), (-44, -22)]), fill(TRIKOT_H)),
    group(smooth([(-46, -44), (-26, -44), (-26, -20), (-36, -12), (-46, -20)], tension=0.25),
          stroke(TRIKOT_W, 2, 70)),
    group(smooth(KOERPER_V, tension=0.6, scharf=AUSSCHNITT), stroke(TRIKOT_H, 3, 60)),   # goldene Kante
    # Der Kragen liegt jetzt AUF dem Rand des Ausschnitts, nicht mehr daneben.
    group(smooth([(-22, -62), (0, -32), (22, -62)], closed=False, tension=0), stroke(TRIKOT_H, 6)),
], parent="body")

# ---------- Strickweste ----------
put("weste_strick", [
    group(smooth(KOERPER_V_TIEF, tension=0.6, scharf=AUSSCHNITT), fill(STRICK)),
    group(arc((-52, -4), (52, -4), 8), stroke(STRICK_H, 4, 45)),
    group(arc((-54, 16), (54, 16), 8), stroke(STRICK_H, 4, 45)),
    group(arc((-46, 36), (46, 36), 7), stroke(STRICK_H, 4, 45)),
    group(smooth([(-62, 50), (0, 66), (62, 50), (60, 62), (0, 78), (-60, 62)], tension=0.5), fill(STRICK_H, 70)),
    # Vorher ein aufgemaltes V auf geschlossenem Stoff. Jetzt ein Rippenband,
    # das den echten Ausschnitt einfasst - wie der Bund einer Strickjacke.
    group(smooth([(-26, -60), (0, -22), (26, -60)], closed=False, tension=0), stroke(STRICK_H, 8)),
    group(smooth(KOERPER_V_TIEF, tension=0.6, scharf=AUSSCHNITT), stroke(STRICK_H, 3, 50)),
], parent="body")

# ---------- Lederweste ----------
# Vorn offen: zwei Bahnen am Umriss entlang, dazwischen bleibt der gelbe Bauch.
# Breitere Bahnen: vorher waren es zwei schmale Streifen am Rand. Die Oeffnung
# in der Mitte bleibt, damit der gelbe Bauch noch hervorschaut.
LEDER_L = [(-42, -68), (-78, -8), (-69, 58), (-36, 72), (-20, 58), (-14, -4), (-30, -64)]
put("weste_leder", [
    group(smooth(LEDER_L, tension=0.5), fill(LEDER)),
    group(smooth([(-x, y) for x, y in LEDER_L], tension=0.5), fill(LEDER)),
    group(smooth(LEDER_L, tension=0.5), stroke(LEDER_H, 3.5, 70)),
    group(smooth([(-x, y) for x, y in LEDER_L], tension=0.5), stroke(LEDER_H, 3.5, 70)),
    group(poly([(-42, -68), (-14, -4), (-2, -26), (-24, -70)]), fill(LEDER_H)),     # Revers
    group(poly([(42, -68), (14, -4), (2, -26), (24, -70)]), fill(LEDER_H)),
    group(ellipse(-56, -4, 9, 9), fill(NIET)),
    group(ellipse(-53, 26, 9, 9), fill(NIET)),
    group(ellipse(56, -4, 9, 9), fill(NIET)),
    group(ellipse(53, 26, 9, 9), fill(NIET)),
], parent="body")

# ---------- Aermel ----------
# Gemessen am linken Arm: die Ebene haengt bei (-58, -8) am Koerper, der
# Oberarm laeuft dort von x = 6 bis x = -46 und ist 28 dick, die Pfote sitzt
# zwischen -31 und -57. Der Kleiderumriss endet bei x = -78 am Koerper, also
# bei -20 im Arm. Was zwischen -20 und -57 liegt, war blank.
#
# Darum reichen die Aermel nach innen bis x = +14: sie greifen ueber die
# Schulter auf den Stoff, damit dort auch beim Wippen keine Luecke aufgeht.
# Nach aussen hoeren sie vor den Krallen auf - eine Pfote steckt nicht im
# Aermel.
def aermelpaar(stueck, formen):
    """Derselbe Aermel an beiden Armen. formen(s) bekommt +1 fuer links und
    -1 fuer rechts; damit wird an der Mittelachse gespiegelt, genauso wie es
    die Armebenen selbst tun."""
    put(stueck + "_armL", formen(1), parent="armL")
    put(stueck + "_armR", formen(-1), parent="armR")


# Trikot: kurzer Aermel mit goldenem Abschluss, wie am echten Trikot.
aermelpaar("trikot", lambda s: [
    group(ellipse(-11 * s, 2, 50, 34), fill(TRIKOT)),
    group(ellipse(-29 * s, 2, 14, 32), fill(TRIKOT_H)),
    group(ellipse(-11 * s, 2, 50, 34), stroke(TRIKOT_H, 3, 55)),
])

# Strickjacke: langer Aermel, zwei Rippen quer, dickes Buendchen.
aermelpaar("weste_strick", lambda s: [
    group(ellipse(-14 * s, 2, 56, 34), fill(STRICK)),
    group(smooth([(-21 * s, -15), (-22 * s, 17)], closed=False), stroke(STRICK_H, 3.5, 45)),
    group(smooth([(-31 * s, -13), (-32 * s, 15)], closed=False), stroke(STRICK_H, 3.5, 45)),
    group(ellipse(-37 * s, 3, 14, 30), fill(STRICK_H, 75)),
    group(ellipse(-14 * s, 2, 56, 34), stroke(STRICK_D, 3, 60)),   # dunkler Rand: sonst
    # verschmilzt der Aermel mit dem Rumpf, beides ist ja derselbe Weinton
])

# Lederjacke: langer Aermel, helleres Buendchen, eine Niete wie am Rumpf.
aermelpaar("weste_leder", lambda s: [
    group(ellipse(-14 * s, 2, 58, 35), fill(LEDER)),
    group(ellipse(-36 * s, 3, 16, 31), fill(LEDER_H, 60)),
    group(ellipse(-21 * s, 2, 8, 8), fill(NIET)),
    group(ellipse(-14 * s, 2, 58, 35), stroke(LEDER_H, 3.5, 70)),
])

# ---------- Dicker Schal ----------
# Das Ende faengt weiter aussen an (x = 26 statt 10) und liegt tiefer: in der
# Mitte direkt unter dem Maul sah es aus wie eine herausgestreckte Zunge.
# Breiter als vorher: auf das Ende soll BOSNA passen, und dafuer braucht es
# Platz. Gilt fuer beide Schals - der Winterschal wird dadurch schoen dick.
# Tiefer und breiter. Der rechte Arm liegt VOR dem Schal und deckt alles
# zwischen y = -30 und -2 zu - gemessen. Was gesehen werden soll, muss
# darunter haengen.
SCHAL_ENDE = [(26, -34), (34, 2), (32, 48), (72, 50), (76, 4), (58, -36)]


def schal(band_farbe, band_dunkel, ende_extra=()):
    """Band um den Hals plus ein Ende, das ueber die Brust faellt.
    Das Ende steht ZUERST in der Liste, also unter dem Band - so wirkt es,
    als kaeme es unter der Schlinge hervor."""
    return [
        group(smooth(SCHAL_ENDE, tension=0.45), fill(band_farbe)),
        group(rect(49, 36, 26, 11, 4), fill(band_dunkel)),
        group(rect(40, 44, 5, 13, 2), fill(band_dunkel)),
        group(rect(49, 46, 5, 13, 2), fill(band_dunkel)),
        group(rect(58, 44, 5, 13, 2), fill(band_dunkel)),
        group(rect(0, -42, 110, 30, 15), fill(band_farbe)),
    ] + list(ende_extra)

put("schal_winter", schal(WOLLE, WOLLE_D, [
    group(rect(0, -42, 110, 8, 4), fill(WOLLE_D, 20)),
    group(smooth([(-40, -52), (-40, -32)], closed=False), stroke(WOLLE_D, 4, 34)),
    group(smooth([(-20, -54), (-20, -30)], closed=False), stroke(WOLLE_D, 4, 34)),
    group(smooth([(0, -55), (0, -29)], closed=False), stroke(WOLLE_D, 4, 34)),
    group(smooth([(20, -54), (20, -30)], closed=False), stroke(WOLLE_D, 4, 34)),
    group(smooth([(40, -52), (40, -32)], closed=False), stroke(WOLLE_D, 4, 34)),
]), parent="body")

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
put("schal_bih", [
    group(smooth(SCHAL_ENDE, tension=0.45), fill(SCHAL_B)),
    group(rect(54, 12, 44, 7, 3), fill(SCHAL_G)),                     # gelber Streifen ueber der Schrift
    group(rect(54, 44, 44, 7, 3), fill(SCHAL_G)),                     # und einer darunter
    group(rect(55, 52, 32, 11, 4), fill(SCHAL_B)),
    group(rect(45, 60, 5, 13, 2), fill(SCHAL_B)),
    group(rect(55, 62, 5, 13, 2), fill(SCHAL_B)),
    group(rect(65, 60, 5, 13, 2), fill(SCHAL_B)),
    group(smooth(SCHAL_ENDE, tension=0.45), stroke(SCHAL_G, 3, 90)),  # gelbe Kante ums Ende
    group(rect(0, -38, 112, 34, 17), fill(SCHAL_B)),
    group(rect(0, -50, 96, 7, 3), fill(SCHAL_G)),                     # Streifen oben
    group(rect(0, -26, 96, 7, 3), fill(SCHAL_G)),                     # Streifen unten
    group(rect(0, -38, 112, 34, 17), stroke(SCHAL_G, 3, 90)),         # gelbe Kante ums Band
], parent="body")
# Gelbe Schrift auf dem blauen Stoff - Ajdin am 18.09.2026: "mit gelber
# schrift bosna und hintergrund ist blau".
built["schal_bih_text"] = textebene("schal_bih_text", "BOSNA", 54, 33, 15, SCHAL_G, "body")

# ---------- Ausgabe ----------
# Eine Grunddatei ohne jeden Zierrat, dazu je Stück eine winzige Datei mit
# genau seiner Ebene. Die App holt die Grunddatei einmal, dazu die Schnipsel
# der getragenen Stücke, haengt sie aneinander und sortiert nach "ind" -
# damit steht wieder genau die Reihenfolge aus ORDER. So kostet jede
# Kombination aus Kopf, Brille und Hals keine einzige Datei extra.
# Vorher war jedes Stück eine vollständige Animation mit 75 KB, und der
# Drache konnte deshalb immer nur eines tragen.
markers = [{"tm": a, "cm": n, "dr": b - a} for n, (a, b) in SEG.items()]
# Die Schriftenliste gehoert in die Grunddatei: die App setzt die Schnipsel
# auf sie auf, und ohne diesen Eintrag wuesste Lottie nicht, womit es den
# Schriftzug auf dem Fanschal setzen soll. Nunito liegt in web/fonts.
doc = {"v": "5.7.4", "fr": FR, "ip": 0, "op": OP, "w": W, "h": H, "nm": "Zmaj", "ddd": 0, "assets": [],
       "fonts": {"list": [{"fName": "ZmajFett", "fFamily": "Nunito",
                           "fStyle": "Bold", "fPath": "", "fWeight": "800",
                           "origin": 0, "ascent": 75}]},
       "layers": [built[n] for n in ORDER if n not in ZIERRAT_ALLE], "markers": markers}
os.makedirs("web/maskottchen", exist_ok=True)
json.dump(doc, open("web/maskottchen/zmaj.json", "w", encoding="utf-8"), separators=(",", ":"))
print("%-26s %7d Bytes, %2d Ebenen" % ("zmaj.json", os.path.getsize("web/maskottchen/zmaj.json"), len(doc["layers"])))

# Jeder Schnipsel ist eine LISTE von Ebenen - meist eine, beim Fanschal zwei.
gesamt = 0
for stueck in ZIERRAT:
    pfad = "web/maskottchen/zmajz-%s.json" % stueck
    ebenen = [built[stueck]] + [built[n] for n in NUR_MIT.get(stueck, [])]
    json.dump(ebenen, open(pfad, "w", encoding="utf-8"), separators=(",", ":"))
    gesamt += os.path.getsize(pfad)
    print("   %-23s %7d Bytes  (%d Ebene%s, ind %s)"
          % (stueck, os.path.getsize(pfad), len(ebenen), "" if len(ebenen) == 1 else "n",
             ",".join(str(e["ind"]) for e in ebenen)))
print("%d Schmuckstücke, zusammen %d Bytes" % (len(ZIERRAT), gesamt))

# Die alten Vollfassungen je Stück werden nicht mehr gebraucht und würden
# sonst mit in die App wandern.
for alt in ["hut", "krone", "brille", "kopfhoerer"]:
    pfad = "web/maskottchen/zmaj-%s.json" % alt
    if os.path.exists(pfad):
        os.remove(pfad)
        print("entfernt: %s" % pfad)
