# -*- coding: utf-8 -*-
r"""
bilder_playwright.py  –  die acht Store-Bilder in jeder Sprache, auf jedem Rechner

Dasselbe wie bilder_machen.sh, aber ohne Git Bash, ohne von Hand
gestarteten Chrome und ohne festen Thonny-Pfad: Das Skript liefert web/
selbst aus, startet Chromium über Playwright und macht die Bilder.

    python3 -m pip install playwright
    python3 -m playwright install chromium        # einmal, falls kein Chromium da ist
    python3 store/bilder_machen/bilder_playwright.py                 # Deutsch → store/screenshots
    python3 store/bilder_machen/bilder_playwright.py --sprache en    # → docs/assets/screenshots-en/
    python3 store/bilder_machen/bilder_playwright.py --sprache en --montage docs/assets/screenshots-en.png

Größe wie im Store: 360 x 640 CSS-Punkte mal 3 = 1080 x 1920.
Vorher muss web/inhalt existieren (python3 inhalt_bauen.py).

Tablets (seit 30.10.2026): --geraet tablet7 bzw. tablet10 macht dieselben
acht Bilder in Tablet-Breite. Das sind Rohbilder des Bildschirms (16:10, wie
ein echtes 7- bzw. 10-Zoll-Tablet), noch nicht im Store-Format; das Format
mit Überschrift und Tablet-Rahmen macht beschriften.py --geraet ...

    python3 store/bilder_machen/bilder_playwright.py --geraet tablet10 --aussehen dunkel --sprache de --ziel ROH10/de

Die Abläufe in den Schritten sind aus bilder_machen.sh übernommen. Wo dort
ein deutscher Text gesucht wurde ("Zuhause", "Weitermachen"), steht hier ein
sprachunabhängiger Weg: die Position im Lernpfad bzw. t('btn.weitermachen').
"""
import argparse
import functools
import http.server
import json
import os
import re
import socketserver
import threading
import time

HIER = os.path.dirname(os.path.abspath(__file__))
WURZEL = os.path.dirname(os.path.dirname(HIER))
WEB = os.path.join(WURZEL, "web")
# Wie in app_bauen.py (version_einsetzen), siehe --version
VERSIONSNAME_FORM = re.compile(r"([1-9][0-9]*)\.(0|[1-9][0-9]*)")
APP_VERSION_ZEILE = re.compile(r"^const APP_VERSION = '[^'\r\n]*';", re.M)
# Die Abzeichen der App (seit 1.4) und wo sie sich merkt, was schon angesehen
# wurde (ERFOLG_GESEHEN in web/index.html), siehe erfolge_ids()
ERFOLGE_LISTE = re.compile(r"^const ERFOLGE = \[(.*?)^\];", re.M | re.S)
ERFOLG_GESEHEN = "zmaj_erfolge_gesehen"

# Nach jedem Schritt, vor dem Bild: nichts davon darf im Bild stehen.
NICHTS_IM_BILD = """
    const sichtbar = e => !!e && e.getClientRects().length > 0;
    const p = document.getElementById('btnProfil');
    if(sichtbar(p) && p.classList.contains('neu')) return 'roter Punkt am Profilknopf';
    const k = document.querySelector('.kurznote');
    if(sichtbar(k)) return 'Meldung im Bild: ' + k.textContent;
    return ''"""

# Schriftzeilen, durch die der untere Bildrand geht (16.11.2026, Pruefung der
# Store-Bilder 1.4: auf fr Bild 2 stand "Médecin & assurance" nur zur oberen
# Haelfte im Bild, auf da tab7 Bild 8 fehlten "og sjældnere." die
# Unterlaengen). Gemessen wird die Tinte der Buchstaben (canvas.measureText),
# nicht das Kaestchen der Zeile: das reicht oben und unten ein paar Punkte
# ueber die Schrift hinaus, und ein angeschnittener Rand eines Kreises oder
# einer Karte ist kein Fehler. Unsichtbares (display, visibility, opacity)
# und was ein Kasten mit overflow selbst abschneidet, zaehlt nicht. Ragt von
# einer Zeile hoechstens 1,5 Punkte ins Bild (Spitzen von Akzenten und
# Oberlaengen), liest das niemand als Schrift; fehlen von ihr hoechstens
# 0,5 Punkte, sieht man es nicht.
# getClientRects und canvas messen auf Tablets verschieden (zoom, siehe
# rectFaktor in web/index.html): darum der Faktor k aus der Hoehe der Zeile.
# Gibt die Anfaenge der angeschnittenen Zeilen zurueck, [] wenn keine.
UNTEN_ANGESCHNITTEN = """
    window.__untenAngeschnitten = () => {
      const f = typeof rectFaktor === 'function' ? rectFaktor() : 1;
      const H = innerHeight / f, aus = [], rg = document.createRange();
      const cv = document.createElement('canvas').getContext('2d');
      const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      while(tw.nextNode()){
        const n = tw.currentNode, el = n.parentElement, text = n.textContent.trim();
        if(!text || !el) continue;
        rg.selectNodeContents(n);
        const zeilen = [...rg.getClientRects()].filter(r => r.width && r.top < H && r.bottom > H);
        if(!zeilen.length) continue;
        let von = -Infinity, bis = Infinity, weg = false;
        for(let a = el; a && a !== document.documentElement; a = a.parentElement){
          const s = getComputedStyle(a);
          if(s.display === 'none' || s.visibility !== 'visible' || +s.opacity === 0){ weg = true; break; }
          if(s.overflowY !== 'visible'){ const b = a.getBoundingClientRect(); von = Math.max(von, b.top); bis = Math.min(bis, b.bottom); }
        }
        if(weg) continue;
        const s = getComputedStyle(el);
        cv.font = s.fontStyle + ' ' + s.fontWeight + ' ' + s.fontSize + ' ' + s.fontFamily;
        const m = cv.measureText(s.textTransform === 'uppercase' ? text.toUpperCase() : text);
        const kasten = m.fontBoundingBoxAscent + m.fontBoundingBoxDescent;
        for(const r of zeilen){
          const k = kasten ? r.height / kasten : 1, grund = r.top + m.fontBoundingBoxAscent * k;
          const oben = Math.max(von, grund - m.actualBoundingBoxAscent * k);
          const unten = Math.min(bis, grund + m.actualBoundingBoxDescent * k);
          if(oben < H - 1.5 && unten > H + 0.5){ aus.push(text.slice(0, 40)); break; }
        }
      }
      return aus;
    };
    return 1"""

# Bildschirm in CSS-Punkten und Pixeldichte. "handy" ist das Store-Format
# selbst (so breit wie Ajdins S21). Die Tablets haben die üblichen Android-
# Maße: 600 x 960 dp (7 Zoll, wie das Nexus 7) und 800 x 1280 dp (10 Zoll).
# Ab v110 waechst die App auf Tablets mit (GROSS in web/index.html): auf
# 10 Zoll alles 1,3-mal so gross, Lektionen fuellen den Bildschirm - so
# sieht sie dort wirklich aus.
GERAETE = {
    "handy":    {"breite": 360, "hoehe": 640,  "dsf": 3},   # 1080 x 1920
    "tablet7":  {"breite": 600, "hoehe": 960,  "dsf": 2},   # 1200 x 1920
    "tablet10": {"breite": 800, "hoehe": 1280, "dsf": 2},   # 1600 x 2560
}

# (Dateiname, JavaScript). Jeder Schritt läuft im Browser als async-Funktion.
SCHRITTE = [
    ("01-start", """
        const q = questsHeute(), t = today(); tagwerk[t] = {};
        q.forEach((x,i) => { tagwerk[t][x.id] = i === 0 ? x.ziel : Math.floor(x.ziel * 0.6); });
        window.__tagwerk01 = JSON.stringify(tagwerk[t]);   // fuer Bild 8, siehe dort
        [...known].slice(40, 47).forEach((id, i) => { topf['w:' + id] = {typ: i % 2 ? 'mcrev' : 'mc', n: 0, z: Date.now() - i * 60000}; });
        homeMode = 'words'; showHome(); scrollTo(0,0);
        await new Promise(r=>setTimeout(r,2500)); return 'start'"""),
    # Bis 13.11.2026 "02-lernpfad": Sektion 1 unter "65 Levels - vom Hallo
    # bis zum Amt". Jetzt (Store-Bilder 1.3) zeigt das Bild das Amt selbst:
    # "Amt & Vertraege" aufgeklappt, ihr Kopf oben. Die Level dort sind im
    # Vorfuehrstand gesperrt - so sieht es in der App wirklich aus. Seit den
    # Stufen-Reitern (1.4) ist es Sektion 1 im Reiter B1; 03 geht darum zuerst
    # zurueck in den Reiter von Weitermachen und klappt dort Sektion 1 auf.
    # 16.11.2026 (Store-Bilder 1.4): oben steht die Reiterleiste A1 bis C1 mit
    # dem gewaehlten B1, direkt darunter die Sektion. Mit dem Kopf der Sektion
    # ganz oben war die Leiste aus dem Bild gerutscht, und man sah nicht, in
    # welcher Stufe das Amt liegt. Und: Im Vorfuehrstand ist B1 noch zu. Ueber
    # den Sektionen stand dann gross die Karte "B1 ist noch zu - Schliess erst
    # A2 ab" (reiterKarteZeichnen), das Amt rutschte halb aus dem Bild, und im
    # Store las es sich wie eine Sperre. Fuer dieses Bild gelten A1 und A2
    # darum als geschafft - so sieht es fuer jemanden aus, der bis B1 gekommen
    # ist: A1 und A2 "fertig", B1 offen, das erste Level "Jetzt dran". Nur im
    # Speicher der Seite; 03 stellt den Stand wieder her.
    ("02-amt", """
        // Seit den Stufen-Reitern (v14-reiter, 13.11.2026) steht Amt & Vertraege
        // als Sektion 1 im Reiter B1, nicht mehr an Stelle 9 der ganzen Liste:
        // SECTIONS[8] ist jetzt "Menschen & Kultur" (A2). Darum die Sektion ueber
        // ihre Kennung suchen und vorher ihren Reiter waehlen.
        const amt = 'amt';
        if(!SECTIONS.some(s => s.id === amt)) throw new Error('keine Sektion amt');
        if(typeof reiterLevel === 'function'){
          const st = stufeVon(CATEGORIES.findIndex(c => c.sektion === amt));
          window.__bestandenVorher = new Set(passed);
          STUFEN.slice(0, STUFEN.indexOf(st)).forEach(s => reiterLevel(s).forEach(i => passed.add(CATEGORIES[i].id)));
        }
        if(typeof stufeWaehlen === 'function') stufeWaehlen(stufeVon(CATEGORIES.findIndex(c => c.sektion === amt)));
        await new Promise(r=>setTimeout(r,300));
        if(offeneSektion !== amt) sektionAufklappen(amt);
        await new Promise(r=>setTimeout(r,900));
        const k = [...document.getElementById('sections').children].find(e => e.dataset.sid === amt);
        const leiste = document.getElementById('reiterLeiste');
        const oben = (leiste && leiste.getClientRects().length) ? leiste : k;
        if(oben === leiste && k.getBoundingClientRect().top - leiste.getBoundingClientRect().bottom > 40)
          throw new Error('Amt steht nicht direkt unter der Reiterleiste (Karte "noch zu"?)');
        scrollBy(0, (oben.getBoundingClientRect().top - 10) * rectFaktor());
        await new Promise(r=>setTimeout(r,600));
        // 16.11.2026 (Pruefung): Auf Franzoesisch braucht der Kopf der Sektion
        // zwei Zeilen und die Beschreibung drei, und der untere Rand schnitt
        // das sechste Level "Médecin & assurance" mitten durch die Schrift.
        // Die Seite so weit zurueckschieben, dass das Level ganz unter dem
        // Rand liegt, geht nicht: dafuer fehlen 28 Punkte, und schon 12 Punkte
        // ueber der Reiterleiste stuende die Leiste Lernpfad/Geschichten/
        // Wiederholen halb im Bild. Darum die Reiterleiste naeher an den
        // oberen Rand, hoechstens bis 0, bis keine Schriftzeile mehr am
        // unteren Rand haengt (der Rand eines Schlosskreises darf, wie auf en
        // und nl). Auf fr steht sie dann ganz oben am Rand; "Médecin &
        // assurance" und "Verrouillé" sind ganz zu sehen. Auf 10 Zoll schnitt
        // der Rand ebenso den Kopf der Sektion 5 (de, sv: bei 3 ganz zu
        // sehen). Reicht auch 0 nicht (10 Zoll tr, nl, nb), kommt die Leiste
        // Lernpfad/Geschichten/Wiederholen mit ins Bild, ganz und oben
        // (wieder 10 bis 0 Punkte). Hilft auch das nicht, bleibt es wie
        // vorher, und die Ausgabe meldet die Zeile ("unten angeschnitten") -
        // abbrechen hiesse, die ganze Sprache faellt aus.
        const modus = (document.getElementById('modeWords') || {}).parentElement;
        const wege = [];
        for(let a = 10; a >= 0; a--) wege.push([oben, a]);
        if(oben === leiste && modus) for(let a = 10; a >= 0; a--) wege.push([modus, a]);
        let weg = null;
        for(const [el, a] of wege){
          scrollBy(0, (el.getBoundingClientRect().top - a) * rectFaktor());
          await new Promise(r=>setTimeout(r,150));
          if(!window.__untenAngeschnitten().length){ weg = [el, a]; break; }
        }
        if(!weg){
          weg = [oben, 10];
          scrollBy(0, (oben.getBoundingClientRect().top - 10) * rectFaktor());
        }
        await new Promise(r=>setTimeout(r,300));
        const reiter = leiste ? leiste.querySelector('[aria-selected="true"]') : null;
        return (reiter ? reiter.dataset.stufe + ' | ' : '') + 'oben ' + (weg[0] === modus ? 'Lernpfad ' : '') + weg[1]
          + ' | ' + k.innerText.split('\\n')[0]"""),
    ("03-neues-wort", """
        // Den Vorfuehrstand aus 02 zurueck (A1 und A2 wieder offen)
        if(window.__bestandenVorher){ passed = window.__bestandenVorher; delete window.__bestandenVorher; }
        // Zurueck in den Reiter von Weitermachen (A1), dort Sektion 1 auf
        if(typeof stufeWaehlen === 'function') stufeWaehlen(stufeVon(firstOpen()));
        const eins = SECTIONS[0].id;
        if(offeneSektion !== eins) sektionAufklappen(eins);
        await new Promise(r=>setTimeout(r,900));
        openLevel(12); await new Promise(r=>setTimeout(r,400)); startLesson();
        await new Promise(r=>setTimeout(r,800)); scrollTo(0,0); return Lx.queue.length"""),
    # Bis 13.11.2026 "04-auswahl" (Auswahlaufgabe, die gewoehnlichste der
    # App). Jetzt der Satzbau aus Kacheln (seit v104, bisher auf keinem Bild):
    # eine Kachelaufgabe mit mindestens vier Woertern, zwei Kacheln schon
    # gelegt. Dafuer die Lektion aus 03 bis zu 40 Mal neu mischen.
    ("04-kacheln", """
        const passt = q => q.typ === 'kacheln' && q.s.bs.trim().split(/\\s+/).length >= 4;
        let ziel = Lx.queue.findIndex((q, i) => i >= Lx.i && passt(q));
        for(let n = 0; ziel < 0 && n < 40; n++){ startLesson(); await new Promise(r=>setTimeout(r,600)); ziel = Lx.queue.findIndex(passt); }
        if(ziel < 0) throw new Error('keine Kachelaufgabe mit vier Woertern in Level 13');
        while(Lx.i < ziel){ await window.__antworte(true, 'lBody', ()=>Lx); }
        await new Promise(r=>setTimeout(r,800));
        const q = Lx.queue[Lx.i];
        const rand = /^[.,!?¿¡:;"„“”«»…()]+|[.,!?¿¡:;"„“”«»…()]+$/g;
        const teile = q.s.bs.split(/\\s+/).map(x => x.replace(rand, '').toLowerCase()).filter(Boolean);
        for(const soll of teile.slice(0, 2)){
          const b = [...document.querySelectorAll('#lBody #xBank .kachel:not(.platz)')].find(o => o.textContent.toLowerCase() === soll);
          if(b) b.click(); await new Promise(r=>setTimeout(r,450));
        }
        scrollTo(0,0); await new Promise(r=>setTimeout(r,500));
        return q.s.bs"""),
    # Bis 11.10.2026 stand hier "05-richtig": dieselbe Aufgabe wie 04, nur
    # beantwortet. Jetzt eine Grammatikaufgabe - die zeigte bisher kein Bild.
    ("05-grammatik", """
        // Konjugation: sieht nach Grammatik aus und fragt nicht nach dem
        // Preis wie die alte Auswahlaufgabe 04.
        let ziel = -1;
        {
          const k = CATEGORIES.findIndex(c => c.id === 'konjugation');
          const lv = k >= 0 ? k : CATEGORIES.findIndex(c => ((GRAMMAR[c.id] || {}).uebungen || []).length);
          openLevel(lv); await new Promise(r=>setTimeout(r,400)); startLesson();
          await new Promise(r=>setTimeout(r,800));
          ziel = Lx.queue.findIndex(q => q.typ === 'gram');
        }
        while(Lx.i < ziel){ await window.__antworte(true, 'lBody', ()=>Lx); }
        await new Promise(r=>setTimeout(r,800)); scrollTo(0,0);
        window.__f5 = Lx.queue[Lx.i].g.frage;
        return Lx.queue[Lx.i].typ + ' ' + Lx.queue[Lx.i].g.frage"""),
    # 15.10.2026 (Store-Bilder v5, bis 30.10. nur in einem Hilfsskript außerhalb des Projekts):
    # 05 und 06 zeigten denselben Satz, weil Grammatikaufgabe und Lückensatz
    # aus derselben Konjugations-Lektion kamen. Darum nur ein Lückensatz, der
    # nicht schon in der Frage aus 05 steht, und ein ganzer Satz (Satzzeichen
    # am Ende, mindestens vier Wörter) - "Sedam, osam, ___" passt nicht zu
    # "Ganze Sätze selbst schreiben". Dafür bis zu 40 Mal neu mischen.
    ("06-luecke", """
        const wb = document.querySelector('#lBody .weiterbox .btn');
        if(wb){ wb.click(); await new Promise(r=>setTimeout(r,500)); }
        const passt = q => q.typ === 'gap' && !(window.__f5 || '').includes(q.s.text)
          && /[.?!]\\s*$/.test(q.s.text) && q.s.text.trim().split(/\\s+/).length >= 4;
        let ziel = Lx.queue.findIndex((q, i) => i >= Lx.i && passt(q));
        for(let n = 0; ziel < 0 && n < 40; n++){ startLesson(); await new Promise(r=>setTimeout(r,600)); ziel = Lx.queue.findIndex(passt); }
        while(Lx.i < ziel){ await window.__antworte(true, 'lBody', ()=>Lx); }
        await new Promise(r=>setTimeout(r,800));
        const q = Lx.queue[Lx.i]; const inp = document.getElementById('xIn');
        inp.value = q.s.answer.split(' / ')[0]; inp.dispatchEvent(new Event('input', {bubbles:true})); inp.blur();
        scrollTo(0,0); await new Promise(r=>setTimeout(r,300)); return q.s.text"""),
    ("07-geschichte", """
        Lx = null; openStory(3); await new Promise(r=>setTimeout(r,600));
        const w = [...document.querySelectorAll('#rBody .w')].find(x => x.textContent === 'povrća');
        if(w) w.click(); await new Promise(r=>setTimeout(r,500)); stilleBitte(); scrollTo(0,0);
        return document.getElementById('rBubble').innerText"""),
    # Tablets (30.10.2026) bleiben oben stehen: seit v110 hat der Reiter
    # Wiederholen eine dritte Karte ("Heute faellig"), die Seite wurde dort
    # scrollbar, und der Bildrand schnitt Flamme und Drachen mittendurch.
    # Oben passt bei 7 und 10 Zoll alles bis "Markiert" ins Bild. Das Handy
    # scrollt wie bisher.
    # 13.11.2026: Auf Niederlaendisch und Daenisch bricht die Schutz-Zeile
    # ueber dem Knopf um ("nog 9 dagen"), und ihre halbe Zeile stand oben
    # abgeschnitten im Bild. Darum danach weiterscrollen, bis keine Schrift
    # mehr am oberen Rand haengt - hoechstens bis der Knopf oben anstoesst.
    # 16.11.2026 (Pruefung): Die Aufgaben, die das Skript fuer Bild 4 bis 6
    # beantwortet, koennen Tagesaufgaben erfuellen. Auf da tab7 waren es alle
    # drei: "3/3", darunter die gruene Zeile "Alle tre klaret!", alles darunter
    # rutschte tiefer, und der untere Rand schnitt die Beschreibung von
    # "Dagens gentagelse" durch. Darum stehen die Tagesaufgaben vor Bild 8
    # wieder wie auf Bild 1 (eine erfuellt, zwei zu 60 %). Die KM bleiben,
    # wie sie sind - sie stehen auch auf Bild 7. Auf Tablets bricht das
    # Skript ab, wenn trotzdem eine Schriftzeile am unteren Rand haengt; am
    # Handy ist die angeschnittene Karte "Markiert" eine offene Frage an
    # Ajdin (Offen-Liste), dort nur der Hinweis in der Ausgabe.
    ("08-wiederholen", """
        if(window.__tagwerk01) tagwerk[today()] = JSON.parse(window.__tagwerk01);
        homeMode = 'topf'; showHome(); await new Promise(r=>setTimeout(r,600));
        scrollTo(0,0); await new Promise(r=>setTimeout(r,200));
        const text = t('btn.weitermachen');
        const w = [...document.querySelectorAll('button')].find(b => b.offsetParent && b.textContent.includes(text));
        if(w && !document.documentElement.classList.contains('gross')){
          scrollBy(0, w.getBoundingClientRect().top - 16);
          await new Promise(r=>setTimeout(r,200));
          let unten = 0; const rg = document.createRange();
          const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
          while(tw.nextNode()){
            const n = tw.currentNode;
            if(!n.textContent.trim() || !n.parentElement || !n.parentElement.offsetParent) continue;
            rg.selectNodeContents(n);
            for(const r of rg.getClientRects()) if(r.top < 0 && r.bottom > 0) unten = Math.max(unten, r.bottom);
          }
          if(unten > 0) scrollBy(0, Math.min(unten + 2, w.getBoundingClientRect().top));
        }
        await new Promise(r=>setTimeout(r,400));
        if(document.documentElement.classList.contains('gross')){
          const rest = window.__untenAngeschnitten();
          if(rest.length) throw new Error('Bild 8 unten angeschnitten: ' + rest.join(' | '));
        }
        return scrollY"""),
]


def lernstand():
    """Wie stand.py: Vorführstand aus testdaten, auf heute verschoben."""
    import datetime
    quelle = os.path.join(WURZEL, "testdaten", "zmaj-screenshots.json")
    s = json.load(open(quelle, encoding="utf-8"))["stand"]
    heute = datetime.date.today()
    s["tage"] = sorted((heute - datetime.timedelta(days=i)).isoformat() for i in range(47))
    s["rekord"] = 47
    s["frost"] = []
    s["bewertung"] = {"gezeigt": [], "nein": True, "bewertet": False}
    s["einstufung"] = {"tag": s["tage"][0], "wahl": "neu", "bis": ""}
    return json.dumps(s, ensure_ascii=False)


def erfolge_ids():
    """Die Kennungen aller Abzeichen aus web/index.html (ERFOLGE), [] ohne.

    Seit 1.4 hat die App Abzeichen. Was auf dem Geraet schon angesehen
    wurde, steht nicht im Lernstand, sondern unter ERFOLG_GESEHEN. Fehlt der
    Eintrag, nimmt die App den ersten Start nach dem Update an und meldet
    gut vier Sekunden nach dem Start "Du hast schon 5 Abzeichen" - die
    Meldung stand je nach Rechner noch auf Bild 1 (Probe 16.11.2026). Ein
    neues Abzeichen truege ausserdem den roten Punkt am Profilknopf. Darum
    gelten fuer die Bilder alle Abzeichen als gesehen; die App bleibt, wie
    sie ist."""
    with open(os.path.join(WEB, "index.html"), encoding="utf-8") as f:
        m = ERFOLGE_LISTE.search(f.read())
    return re.findall(r"\{\s*id:\s*'([^']+)'", m.group(1)) if m else []


def server_starten():
    """web/ auf einem freien Port, im Hintergrund, ohne Ausgabe."""
    class Leise(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass
    handler = functools.partial(Leise, directory=WEB)
    srv = socketserver.ThreadingTCPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, "http://127.0.0.1:%d" % srv.server_address[1]


def bilder_machen(sprache, ziel, chrome=None, geraet="handy", aussehen=None, version=None):
    """aussehen: None = wie bisher (Playwright stellt hell ein), "hell" oder
    "dunkel". Die Store-Bilder sind seit v5 (15.10.2026) dunkel; die App folgt
    dem Gerät, darum wird hier das Gerät dunkel gestellt, nicht die App.

    version: Nummer für die Fußzeile ("Zmaj v1.2"), wie sie app_bauen.py
    (version_einsetzen) aus versionName der Hülle in die gebaute App setzt.
    In web/index.html steht nur der Rückfallwert, und der hinkt vor einem
    Release eine Nummer hinterher (30.10.2026: Bilder für 1.2 zeigten 1.1).
    Ersetzt wird nur in der ausgelieferten Seite, web/ bleibt unberührt."""
    from playwright.sync_api import sync_playwright

    g = GERAETE[geraet]
    farbe = {"hell": {"color_scheme": "light"}, "dunkel": {"color_scheme": "dark"}}.get(aussehen, {})
    if not os.path.exists(os.path.join(WEB, "inhalt", sprache + ".json")):
        raise SystemExit("web/inhalt/%s.json fehlt - erst  python3 inhalt_bauen.py" % sprache)
    if version is not None:
        if not VERSIONSNAME_FORM.fullmatch(version):
            raise SystemExit("--version %r hat nicht die Form Hauptzahl.Nebenzahl (z. B. 1.2)" % version)
        with open(os.path.join(WEB, "index.html"), encoding="utf-8") as f:
            anzahl = len(APP_VERSION_ZEILE.findall(f.read()))
        if anzahl != 1:
            raise SystemExit("\"const APP_VERSION = '...';\" steht %d-mal in web/index.html statt einmal" % anzahl)
    os.makedirs(ziel, exist_ok=True)
    antworte = open(os.path.join(HIER, "antworte.js"), encoding="utf-8").read()
    srv, basis = server_starten()
    pfade = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path=chrome) if chrome else pw.chromium.launch()
            seite = browser.new_context(viewport={"width": g["breite"], "height": g["hoehe"]},
                                        device_scale_factor=g["dsf"], locale=sprache, **farbe).new_page()
            js = lambda code: seite.evaluate("async () => {" + code + "}")  # noqa: E731
            if version is not None:
                def mit_version(route):
                    antwort = route.fetch()
                    text = APP_VERSION_ZEILE.sub(lambda _: "const APP_VERSION = '%s';" % version,
                                                 antwort.text(), count=1)
                    route.fulfill(response=antwort, body=text)
                seite.route(re.compile(r"/index\.html(\?|$)"), mit_version)
            # Den Stand auf einer leeren Seite desselben Ursprungs setzen, nicht in
            # der laufenden App: deren visibilitychange speichert beim Wegnavigieren
            # sonst den eigenen, leeren Stand darueber (wie tests_e2e/conftest.py).
            seite.goto(basis + "/leer")
            js("localStorage.clear(); localStorage.setItem('zmaj_stand', %s); "
               "localStorage.setItem('zmaj_einwilligung', JSON.stringify({wahl:'nein',stand:1,zeit:new Date().toISOString()})); "
               "localStorage.setItem('zmaj_sprache', %s); "
               "localStorage.setItem(%s, %s); return 1"
               % (json.dumps(lernstand()), json.dumps(sprache),
                  json.dumps(ERFOLG_GESEHEN), json.dumps(json.dumps(erfolge_ids()))))
            seite.goto(basis + "/index.html?neu=%d" % time.time())
            seite.wait_for_function("typeof openLevel === 'function' && typeof Lx !== 'undefined'", timeout=30000)
            seite.wait_for_timeout(6000)   # Vorspann und Drache
            js(antworte)
            js(UNTEN_ANGESCHNITTEN)
            js("const st = document.createElement('style'); st.textContent = '#btnBack{display:none!important}'; "
               "document.head.append(st); return 1")
            for name, code in SCHRITTE:
                ergebnis = js(code)
                stoert = js(NICHTS_IM_BILD)
                if stoert:
                    raise SystemExit("%s %s: %s" % (sprache, name, stoert))
                pfad = os.path.join(ziel, name + ".png")
                seite.screenshot(path=pfad)
                pfade.append(pfad)
                print("  %-16s %s" % (name, str(ergebnis)[:60].replace("\n", " ")))
                # Nur ein Hinweis zum Nachsehen (siehe LIESMICH.txt). Bild 2
                # hat vorher selbst nach einem Abstand ohne halbe Zeile
                # gesucht, Bild 8 bricht auf Tablets oben schon ab.
                unten = js("return window.__untenAngeschnitten().join(' | ')")
                if unten:
                    print("  %-16s unten angeschnitten: %s" % ("", unten[:90]))
            browser.close()
    finally:
        srv.shutdown()
    return pfade


def montage(pfade, ausgabe, auswahl=(0, 1, 2, 3, 6)):
    """Fünf Bilder nebeneinander, für das README.

    Seit 13.11.2026 sind Bild 2 und 4 das Amt und die Kacheln (vorher
    Lernpfad und Auswahlaufgabe). Wer die Leiste neu macht, passt den
    Alt-Text in README.md (Bildleiste oben) mit an.

    Die Lücken sind durchsichtig (15.10.2026): Seit die Bilder dunkel sind,
    standen weiße Streifen dazwischen, auf GitHub im dunklen Modus grell.
    Die Palette bleibt MEDIANCUT - FASTOCTREE könnte zwar Alpha, verlor aber
    den weichen Schatten um den Drachen. Darum bekommen die Lücken eine
    Farbe, die in der App nicht vorkommt, und genau dieser Paletteneintrag
    wird durchsichtig. Trifft er auch nur ein Pixel der Bilder, bleiben die
    Lücken weiß wie vorher."""
    from PIL import Image
    breite, hoehe, luecke = 540, 960, 16
    loch = (255, 0, 255)
    bilder = [Image.open(pfade[i]).convert("RGB").resize((breite, hoehe), Image.LANCZOS) for i in auswahl]
    leinwand = Image.new("RGB", (breite * len(bilder) + luecke * (len(bilder) - 1), hoehe), loch)
    for i, b in enumerate(bilder):
        leinwand.paste(b, (i * (breite + luecke), 0))
    bild = leinwand.quantize(colors=256, method=Image.MEDIANCUT, dither=Image.Dither.NONE)
    extra = {}
    if len(bilder) > 1:
        idx = bild.getpixel((breite + luecke // 2, hoehe // 2))
        nur_luecken = bild.histogram()[idx] == luecke * (len(bilder) - 1) * hoehe
        if nur_luecken and tuple(bild.getpalette()[idx * 3:idx * 3 + 3]) == loch:
            extra["transparency"] = idx
    if not extra:
        leinwand = Image.new("RGB", leinwand.size, (255, 255, 255))
        for i, b in enumerate(bilder):
            leinwand.paste(b, (i * (breite + luecke), 0))
        bild = leinwand.quantize(colors=256, method=Image.MEDIANCUT, dither=Image.Dither.NONE)
    bild.save(ausgabe, optimize=True, **extra)
    print("Montage: %s (%.0f KB, Lücken %s)" % (ausgabe, os.path.getsize(ausgabe) / 1024.0,
                                                "durchsichtig" if extra else "weiß"))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    p.add_argument("--sprache", default="de")
    p.add_argument("--ziel", help="Ordner für die Bilder")
    p.add_argument("--chrome", help="Pfad zu Chromium, falls Playwright keinen eigenen hat")
    p.add_argument("--montage", help="zusätzlich eine Bildleiste für das README schreiben (braucht Pillow)")
    p.add_argument("--geraet", default="handy", choices=sorted(GERAETE),
                   help="handy (Standard, 1080 x 1920) oder Tablet-Rohbilder tablet7 / tablet10")
    p.add_argument("--aussehen", choices=("hell", "dunkel"),
                   help="Gerät hell oder dunkel stellen (ohne: hell, wie bisher; Store-Bilder seit v5: dunkel)")
    p.add_argument("--version",
                   help="Nummer in der Fußzeile wie in der gebauten App, z. B. 1.2 (versionName der Hülle); "
                        "ohne: der Rückfallwert aus web/index.html")
    a = p.parse_args(argv)
    if a.geraet != "handy" and not a.ziel:
        p.error("--geraet %s braucht --ziel (Rohbilder, nicht für store/screenshots)" % a.geraet)
    ziel = a.ziel or (os.path.join(WURZEL, "store", "screenshots") if a.sprache == "de"
                      else os.path.join(WURZEL, "docs", "assets", "screenshots-" + a.sprache))
    pfade = bilder_machen(a.sprache, ziel, a.chrome, a.geraet, a.aussehen, a.version)
    if a.montage:
        montage(pfade, a.montage)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
