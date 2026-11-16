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
# Die Tagesaufgaben zieht die App mit der Geraete-Kennung (LOKAL_ID, siehe
# questSaat und zieh in web/index.html) und dem Datum als Startwert. Ohne
# feste Kennung erfand jeder Lauf eine neue, und Handy, Tablets und Sprachen
# zeigten verschiedene Aufgaben (Store-Bilder 1.4). Mit der ersten stehen an
# einem Tag ueberall dieselben drei (Feinschliff 16.11.2026); die weiteren
# nur, wenn sie am Rand nicht aufgehen (siehe bilder_machen).
GERAETE_ID_SCHLUESSEL = "zmaj_id"
GERAETE_IDS = ("zmaj-store-bilder",) + tuple("zmaj-store-bilder-%d" % i for i in range(2, 7))

# Nach jedem Schritt, vor dem Bild: nichts davon darf im Bild stehen.
NICHTS_IM_BILD = """
    const sichtbar = e => !!e && e.getClientRects().length > 0;
    const p = document.getElementById('btnProfil');
    if(sichtbar(p) && p.classList.contains('neu')) return 'roter Punkt am Profilknopf';
    const k = document.querySelector('.kurznote');
    if(sichtbar(k)) return 'Meldung im Bild: ' + k.textContent;
    return ''"""

# KM und Tagesaufgaben, soweit im Bild (Feinschliff 16.11.2026): auf allen
# Bildern einer Sprache und eines Geraets dieselben wie auf Bild 1, sonst
# bricht das Skript ab. Auf 10 Zoll en und fr standen auf Bild 7 und 8
# 1250 KM statt 1240, auf dem Handy de Bild 8 "2/3" statt "1/3".
STAND_IM_BILD = """
    const sichtbar = e => !!e && e.getClientRects().length > 0;
    const m = document.getElementById('muenzBar'), q = document.getElementById('questBox');
    return [sichtbar(m) ? m.textContent.trim() : '', sichtbar(q) ? q.innerText.trim().replace(/\\s+/g, ' ') : '']"""

# Was der obere oder untere Bildrand durchschneidet (16.11.2026, Pruefung der
# Store-Bilder 1.4: auf fr Bild 2 stand "Médecin & assurance" nur zur oberen
# Haelfte im Bild, auf da tab7 Bild 8 fehlten "og sjældnere." die
# Unterlaengen; Feinschliff am selben Tag: halbe Zeilen auf Bild 1, 4 und 8,
# auf 7 Zoll 1 bis 3 Pixel der naechsten Zeile, "Lektion abbrechen" halb im
# Bild). Der Rand des Bildschirms ist auch der Rand im Rahmen, den
# beschriften.py darum legt.
#   - Schriftzeilen: gemessen wird die Tinte der Buchstaben (canvas.measureText)
#     Zeile fuer Zeile, nicht das Kaestchen der Zeile - das reicht oben und
#     unten ein paar Punkte ueber die Schrift hinaus; eine Unterstreichung
#     ("Ueberspringen") reicht weiter hinab. Von einer Zeile ausserhalb darf
#     kein Geraetepixel ins Bild ragen (dazu ein Pixel Saum fuer die
#     Kantenglaettung) - bis 16.11. durften es 1,5 Punkte sein, auf 7 Zoll
#     waren das sichtbare Spitzen. Eine Zeile im Bild haelt 4 Geraetepixel
#     Abstand zum Rand: sass die Grundlinie genau auf dem Rand, sah die Zeile
#     abgeschnitten aus, auch wenn ihr nichts fehlte.
#   - Knoepfe mit Schrift (auch Reiter und Kacheln): der Kasten darf nicht
#     durchgeschnitten sein, wenn von seiner Schrift etwas im Bild steht -
#     sonst steht ein halber Knopf da, auch wenn sein Text ganz ist. Ein
#     Rand ohne Schrift (Kreis, Karte, der obere Rand des naechsten Knopfs)
#     ist kein Fehler, und Level-Zeilen und Sektionskoepfe sind Karten der
#     Liste, die unten weiterlaeuft.
#   - Oben auch kein halber Kasten ohne Schrift (Pillen der Kopfleiste,
#     Drache, Flamme); grosse Karten duerfen dort angeschnitten sein.
# Unsichtbares (display, visibility, opacity) und was ein Kasten mit overflow
# selbst abschneidet, zaehlt nicht. getClientRects und canvas messen auf
# Tablets verschieden (zoom, siehe rectFaktor in web/index.html): darum der
# Faktor k aus der Hoehe der Zeile.
# __randSchnitte() gibt die angeschnittenen Zeilen und Knoepfe zurueck, [] wenn
# keine. __randFrei() sucht vor jedem Bild die naechste Lage der Seite ohne
# solche (Punkt fuer Punkt; siehe dort), und vor jedem Bild bricht das
# Skript ab, wenn trotzdem etwas angeschnitten ist - damit spaetere Laeufe
# nicht still schlechter werden.
RAND_PRUEFUNG = r"""
    // [von, bis, unterstrichen] - wo Kaesten mit overflow abschneiden; null = unsichtbar
    const ausschnitt = el => {
      let von = -Infinity, bis = Infinity, strich = false;
      for(let a = el; a && a !== document.documentElement; a = a.parentElement){
        const s = getComputedStyle(a);
        if(s.display === 'none' || s.visibility !== 'visible' || +s.opacity === 0) return null;
        if(s.overflowY !== 'visible'){ const b = a.getBoundingClientRect(); von = Math.max(von, b.top); bis = Math.min(bis, b.bottom); }
        if(/underline/.test(s.textDecorationLine)) strich = true;
      }
      return bis - von < 2 ? null : [von, bis, strich];
    };
    const durchsichtig = c => !c || c === 'transparent' || /rgba\([^)]*,\s*0\)$/.test(c);
    const bemalt = (el, s) => /^(img|svg|canvas|video)$/i.test(el.tagName) || !durchsichtig(s.backgroundColor)
      || s.backgroundImage !== 'none' || s.boxShadow !== 'none'
      || ['Top', 'Bottom', 'Left', 'Right'].some(k => parseFloat(s['border' + k + 'Width']) > 0 && !durchsichtig(s['border' + k + 'Color']));
    const faktor = () => typeof rectFaktor === 'function' ? rectFaktor() : 1;
    const KNOEPFE = 'button, [role=button], [role=tab], .btn, .kachel, a[href], input:not([type=hidden]), select, textarea';
    // Streifen oben (Pruefung nach der Kopfleiste 16.11.2026): Auf den Bildern,
    // deren Seite nicht ganz oben steht (Bild 2, am Handy Bild 8), stand das
    // oberste Teil nur 6 bis 10 Punkte unter dem Rand - knapper als die 10
    // Punkte, die Ajdin bei der Kopfleiste schon "knapp" fand; Bild 8 hatte
    // vor dem Feinschliff 16. Mit Rollen allein geht es dort nicht: Zwischen
    // Reiterleiste, Leiste Lernpfad/Geschichten/Wiederholen, Karte "Heute"
    // und "Weitermachen" sind nur 9 bis 13 Punkte frei, bei 16 stuende das
    // Teil darueber halb im Bild. Darum liegt fuer diese Bilder oben ein
    // Streifen in der Farbe des Grunds, so hoch wie der Rand oben der App
    // (padding-top von body, 16 Punkte, auf 10 Zoll mitgewachsen): oben sieht
    // das Bild aus wie eine Seite, die ganz oben steht. Was darunter liegt,
    // ist verdeckt, und __randSchnitte misst den oberen Rand an seiner
    // Unterkante (__band(), 0 ohne Streifen). Die App bleibt, wie sie ist.
    const BAND = '__streifenOben';
    window.__band = () => { const s = document.getElementById(BAND); return s ? s.getBoundingClientRect().bottom : 0; };
    window.__bandFarbe = () => {
      const s = document.getElementById(BAND);
      if(s) s.style.background = getComputedStyle(document.body).backgroundColor;   // Grund der Sektion
    };
    window.__bandAn = () => {
      window.__polsterZurueck();
      let s = document.getElementById(BAND);
      if(!s){ s = document.createElement('div'); s.id = BAND; document.body.appendChild(s); }
      s.style.cssText = 'position:fixed; left:0; top:0; width:100%; pointer-events:none; z-index:2147483647; height:'
        + (parseFloat(getComputedStyle(document.body).paddingTop) || 0) + 'px';
      window.__bandFarbe();
    };
    window.__bandWeg = () => { const s = document.getElementById(BAND); if(s) s.remove(); };
    // Wie weit ein Schatten (box-shadow, nicht inset) unter den Kasten reicht:
    // "Weitermachen" hat unten eine dunkle Kante, die nicht im Kasten liegt.
    const schattenUnten = s => {
      if(!s.boxShadow || s.boxShadow === 'none') return 0;
      let tief = 0;
      for(const teil of s.boxShadow.split(/,(?![^(]*\))/)){
        if(/inset/.test(teil)) continue;
        const z = (teil.match(/-?[\d.]+px/g) || []).map(parseFloat);
        if(z.length >= 2) tief = Math.max(tief, z[1] + Math.max(0, z[2] || 0) + (z[3] || 0));
      }
      return tief;
    };
    window.__randSchnitte = () => {
      const f = faktor(), H = innerHeight / f, px = 1 / (devicePixelRatio * f), luft = 4 * px;
      const B = window.__band();
      const raender = [['oben', B], ['unten', H]], aus = [];
      const rg = document.createRange(), zr = document.createRange();
      const cv = document.createElement('canvas').getContext('2d');
      const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      while(tw.nextNode()){
        const n = tw.currentNode, el = n.parentElement;
        if(!el || !n.textContent.trim()) continue;
        rg.selectNodeContents(n);
        const nah = [...rg.getClientRects()].filter(r => r.width && r.height
          && raender.some(([, E]) => r.top - r.height < E && r.bottom + r.height > E));
        if(!nah.length) continue;
        const box = ausschnitt(el);
        if(!box) continue;
        const s = getComputedStyle(el), t = n.textContent, zeichen = [];
        for(let i = 0; i < t.length; i++){
          zr.setStart(n, i); zr.setEnd(n, i + 1);
          const q = zr.getBoundingClientRect();
          if(q.width || q.height) zeichen.push([t[i], q]);
        }
        cv.font = s.fontStyle + ' ' + s.fontWeight + ' ' + s.fontSize + ' ' + s.fontFamily;
        for(const r of nah){
          let zeile = zeichen.filter(([, q]) => q.top < r.bottom - 0.01 && q.bottom > r.top + 0.01
            && q.left > r.left - 1 && q.right < r.right + 1).map(([c]) => c).join('').trim();
          if(!zeile) continue;
          if(s.textTransform === 'uppercase') zeile = zeile.toUpperCase();
          const m = cv.measureText(zeile), kasten = m.fontBoundingBoxAscent + m.fontBoundingBoxDescent;
          const k = kasten ? r.height / kasten : 1, grund = r.top + m.fontBoundingBoxAscent * k;
          const strich = box[2] ? 0.2 * parseFloat(s.fontSize) * k : 0;
          const oben = Math.max(box[0], grund - m.actualBoundingBoxAscent * k - px);
          const unten = Math.min(box[1], grund + m.actualBoundingBoxDescent * k + strich + px);
          if(oben >= unten) continue;
          if(oben < B && unten > B || oben < H && unten > H) aus.push((oben < B ? 'oben: ' : 'unten: ') + zeile.slice(0, 40));
          else if(unten > B && oben < B + luft) aus.push('oben zu knapp: ' + zeile.slice(0, 40));
          else if(oben < H && unten > H - luft) aus.push('unten zu knapp: ' + zeile.slice(0, 40));
        }
      }
      for(const b of document.querySelectorAll(KNOEPFE)){
        if(b.closest('.node, .skopf')) continue;
        const r = b.getBoundingClientRect();
        if(!r.width || !r.height || r.height > H / 4) continue;
        const quer = raender.filter(([, E]) => r.top < E - px && r.bottom > E + px);
        if(!quer.length || !ausschnitt(b) || !bemalt(b, getComputedStyle(b))) continue;
        let schrift = /^(INPUT|SELECT|TEXTAREA)$/.test(b.tagName) && !!(b.value || b.placeholder);
        const tk = document.createTreeWalker(b, NodeFilter.SHOW_TEXT);
        while(!schrift && tk.nextNode()){
          if(!tk.currentNode.textContent.trim()) continue;
          rg.selectNodeContents(tk.currentNode);
          schrift = [...rg.getClientRects()].some(q => q.width && q.bottom > B && q.top < H);
        }
        const name = (b.innerText || b.value || '').trim().replace(/\s+/g, ' ').slice(0, 40);
        if(schrift) quer.forEach(([wo]) => aus.push(wo + ', Knopf: ' + name));
      }
      // Oben auch kein halber Kasten ohne Schrift: die untere Haelfte der
      // Pillen der Kopfleiste, der Drache oder die Flamme sahen dort
      // abgeschnitten aus (Probe 7 Zoll Bild 8). Grosse Karten duerfen - am
      // Rand des Bildschirms, nicht am Streifen: Dort saehe eine halbe Karte
      // aus, als liefe sie unter einer Leiste durch. Am Streifen zaehlt auch
      // der Schatten unter dem Kasten.
      for(const el of document.body.querySelectorAll('*')){
        if(el.id === BAND) continue;
        const r = el.getBoundingClientRect();
        if(!r.width || !r.height || r.top >= B - px || r.height > (B ? H : H / 4)) continue;
        if(el.ownerSVGElement) continue;
        const s = getComputedStyle(el);
        if(!(r.bottom + (B ? schattenUnten(s) : 0) > B + px) || !bemalt(el, s) || !ausschnitt(el)) continue;
        aus.push('oben, Kasten: ' + String(el.id || el.className || el.tagName).slice(0, 30));
      }
      return aus;
    };
    // Wie weit die Seite hinauf darf, bis das oberste Teil (bemalter Kasten
    // oder Schrift) oben anstoesst; in Punkten fuer scrollTo. Ein halber
    // Punkt Luft: auf 7 Zoll de Bild 8 steht "Heute ist nichts fällig." erst
    // 16 Punkte weiter oben ganz im Bild, die Kopfleiste dann einen Punkt
    // unter dem Rand - knapp, aber ganz (Probe 16.11.2026). Liegt oben der
    // Streifen, zaehlt erst, was unter ihm anfaengt.
    window.__kopfRaum = () => {
      const f = faktor(), B = window.__band();
      let oben = innerHeight / f / 3;
      for(const el of document.body.querySelectorAll('*')){
        if(el.id === BAND) continue;
        const r = el.getBoundingClientRect();
        if(!r.width || !r.height || r.top < B - 0.5 || r.top >= oben) continue;
        if(!bemalt(el, getComputedStyle(el)) && ![...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())) continue;
        if(ausschnitt(el)) oben = r.top;
      }
      return Math.max(0, (oben - 0.5) * f);
    };
    // KM und Tagesaufgaben wie auf Bild 1 (16.11.2026): die Antworten fuer
    // Bild 4 bis 6 erfuellen manchmal eine Tagesaufgabe, und auf 10 Zoll en
    // und fr standen auf Bild 7 und 8 dann 1250 KM statt 1240.
    window.__standZurueck = () => {
      if(window.__muenzen01){ muenzenGes = window.__muenzen01[0]; muenzenAus = window.__muenzen01[1]; }
      if(window.__tagwerk01) tagwerk[today()] = JSON.parse(window.__tagwerk01);
      if(typeof renderLives === 'function') renderLives();
    };
    // Luft ueber dem obersten Teil (Kopfleiste), wenn die Seite ganz oben
    // steht: mindestens __luftMin Punkte (Pruefung nach dem Feinschliff
    // 16.11.2026: auf 7 Zoll Bild 1 stand die Kopfleiste bei de, en, tr, nl
    // und da nur 3 bis 4 Punkte unter dem Rand, am Handy auf Bild 1 9 bis 10
    // und auf Bild 4 9 bis 11, und wirkte gedraengt - wie vorher die
    // Reiterleiste ganz oben auf fr Handy Bild 2). 16 ist der Rand oben der
    // App (padding-top von body); dort steht die Kopfleiste 16 bis 17 Punkte
    // unter dem Rand, die Karte einer Lektion 16, auf 10 Zoll 21 bis 22
    // (Probe 16.11.2026). Erst stand hier 8 - das war noch gedraengt (Ajdin:
    // "ja ist schon knapp"). __luftOben() misst sie in Punkten der Seite.
    window.__luftMin = 16;
    window.__luftOben = () => window.__kopfRaum() / faktor() + 0.5;
    // Den oberen Rand der Seite (padding-top von body, 16 Punkte) wie in
    // der App; __randFrei vergroessert ihn nur fuer das eine Bild.
    window.__polsterZurueck = () => {
      if(window.__polster0 === undefined) window.__polster0 = document.body.style.paddingTop;
      document.body.style.paddingTop = window.__polster0;
    };
    // Vor jedem Bild: Stand wie Bild 1, kein Fokusrahmen (Bild 3 zeigte
    // "Weiter" mit Tastaturfokus), dann die naechste Lage ohne Anschnitt,
    // Punkt fuer Punkt abwechselnd in beide Richtungen:
    //   - die Seite rollt hinauf, bis oben etwas anstoesst (opts.runter,
    //     ohne: __kopfRaum, hoechstens 40 Punkte); steht sie ganz oben, nur
    //     so weit, dass ueber der Kopfleiste __luftMin Punkte bleiben;
    //   - die Seite rollt hinunter, wenn sie nicht ganz oben steht (opts.hoch);
    //   - steht sie ganz oben, rueckt sie stattdessen tiefer: der Rand ueber
    //     der Kopfleiste waechst um bis zu opts.polster Punkte (ohne: 24).
    //     Ohne das gab es auf 10 Zoll sv und nb Bild 1 keine Lage ohne halben
    //     Level-Titel ("Veckodagar"), und auf 7 Zoll de Bild 8 stand die
    //     Kopfleiste sonst einen Punkt unter dem Rand. Auf 7 Zoll Bild 1 (de,
    //     en, tr, nl, da) ragte die Beschreibung des letzten Levels ("Essen &
    //     Trinken") ins Bild; ganz zu sehen ist sie erst 13 bis 14 Punkte
    //     weiter oben, mit der Kopfleiste 3 bis 4 Punkte unter dem Rand.
    //     Darum dort 21 Punkte mehr Rand oben: das Level liegt ganz unter
    //     dem Rand, und ueber der Kopfleiste ist Luft wie unter einer
    //     Statusleiste (Probe 16.11.2026: von 12 Punkten hinauf bis 20 Punkte
    //     mehr Rand ging nichts auf). Die App selbst bleibt, wie sie ist.
    // opts.nurPruefen: nichts verschieben, nur nachsehen (fuer Bilder, die
    // ihre Lage schon selbst gesucht haben). Chrome rollt hier nur um ganze
    // Punkte (Probe 16.11.2026), darum in Schritten von einem Punkt.
    // Gibt '' zurueck, wenn es keine solche Lage gibt.
    window.__randFrei = async (opts) => {
      opts = opts || {};
      window.__standZurueck();
      const a = document.activeElement;
      if(a && a !== document.body && a.blur) a.blur();
      const bild = () => new Promise(r => requestAnimationFrame(() => r()));
      await bild();
      if(opts.nurPruefen) return window.__randSchnitte().length ? '' : 'frei';
      window.__polsterZurueck();
      await bild();
      const b = document.body, pt0 = parseFloat(getComputedStyle(b).paddingTop) || 0;
      const f = faktor(), y0 = scrollY, kopf = window.__kopfRaum();
      window.__obenStand = y0 < 0.5;   // fuer die Pruefung der Luft oben (ein_lauf)
      const runter = Math.min(opts.runter === undefined ? (y0 < 0.5 ? Math.max(0, kopf - window.__luftMin * f) : kopf) : opts.runter, 40 * f);
      const hoch = Math.min(opts.hoch || 0, y0);
      const polster = y0 < 0.5 ? (opts.polster === undefined ? 24 : opts.polster) : 0;
      const wege = [];
      for(let k = 0; k <= Math.max(runter, hoch, polster); k++){
        if(k <= runter + 1e-6) wege.push(['rollen', k]);
        if(k && k <= hoch) wege.push(['rollen', -k]);
        else if(k && k <= polster) wege.push(['polster', k]);
      }
      for(const [art, k] of wege){
        if(art === 'rollen'){ window.__polsterZurueck(); scrollTo({top: y0 + k, behavior: 'instant'}); }
        else { scrollTo({top: y0, behavior: 'instant'}); b.style.paddingTop = (pt0 + k) + 'px'; }
        await bild();
        if(art === 'rollen' && Math.abs(scrollY - y0 - k) > 0.5) continue;
        if(!window.__randSchnitte().length)
          return 'frei' + (!k ? '' : art === 'polster' ? ' Rand oben +' + k : ' ' + (k > 0 ? '+' : '') + k);
      }
      window.__polsterZurueck();
      scrollTo({top: y0, behavior: 'instant'});
      await bild();
      return '';
    };
    // Bild 4 und 6 (Pruefung nach dem Feinschliff 16.11.2026): Die Lektion
    // steht ganz oben und darf nicht mehr hinauf (__luftMin), nur tiefer -
    // dann steht ihre Karte aber tiefer als auf Bild 3 und 5 (16 Punkte unter
    // dem Rand). Am Handy schnitt der Rand ohne mehr Rand oben je nach Satz
    // "Lektion abbrechen" oder "Ueberspringen"; "Gdje je crvena torba?"
    // brauchte 23 Punkte mehr, "Ne znam gdje je ključ." 13. Ein Satz mit mehr
    // als 4 Punkten gilt darum erst ab dem 9. Versuch und nur, wenn kein Satz
    // davor weniger brauchte (wahl.bester); im letzten Versuch jeder, der
    // aufgeht. Gibt die Lage zurueck wie __randFrei, '' = naechster Satz.
    window.__satzFrei = async (versuch, letzter, wahl) => {
      const frei = await window.__randFrei();
      const m = /Rand oben \+(\d+)/.exec(frei), k = m ? +m[1] : 0;
      if(!frei || k <= 4 || letzter) return frei;
      const gut = versuch >= 8 && k <= wahl.bester;
      wahl.bester = Math.min(wahl.bester, k);
      if(gut) return frei;
      window.__polsterZurueck();
      return '';
    };
    // Lage fuer eine Seite, die nicht ganz oben steht (Bild 2, am Handy
    // Bild 8): Streifen oben an (siehe __bandAn), dann steht das Teil anker
    // 0, 1, 2 ... bis Punkte unter dem Streifen, bis nichts mehr am Rand
    // haengt. Was ueber dem Anker liegt, verschwindet unter dem Streifen oder
    // steht ganz im Bild; halb im Bild meldet es __randSchnitte. Gerollt wird
    // um ganze Punkte (wie in __randFrei), und zwar so, dass der Anker nie
    // ueber "k Punkte unter dem Streifen" steht. Gibt '' zurueck und nimmt den
    // Streifen wieder weg, wenn es keine solche Lage gibt.
    window.__bandFrei = async (anker, bis) => {
      window.__standZurueck();
      const a = document.activeElement;
      if(a && a !== document.body && a.blur) a.blur();
      window.__bandAn();
      const bild = () => new Promise(r => requestAnimationFrame(() => r()));
      await bild();
      const f = faktor(), B = window.__band();
      for(let k = 0; k <= bis; k++){
        scrollTo({top: scrollY + Math.floor((anker.getBoundingClientRect().top - B - k) * f), behavior: 'instant'});
        await bild();
        const d = anker.getBoundingClientRect().top - B;
        if(d < k - 0.01 || d >= k + 1) continue;   // so weit rollt die Seite nicht (Anfang oder Ende)
        if(!window.__randSchnitte().length) return 'Streifen +' + k;
      }
      window.__bandWeg();
      await bild();
      return '';
    };
    // Vor dem Bild: Steht die Seite ganz oben, ueber dem obersten Teil
    // mindestens __luftMin Punkte (__luftOben); steht sie nicht ganz oben,
    // muss der Streifen liegen - dann misst __luftOben ab dem Streifen.
    // Gibt [Luft, Mindestmass, Streifen ja/nein] zurueck.
    window.__luftPruefen = () => {
      const B = window.__band();
      window.__bandFarbe();
      if(!window.__obenStand && !B) return [0, window.__luftMin, false];
      return [window.__luftOben(), window.__luftMin, !!B];
    };
    return 1"""

# Der Drache blinzelt (Pruefung 16.11.2026: Bild 5 auf Handy en, sv, nl, da
# und 7 Zoll nb mit geschlossenen Augen). Er ist eine Lottie-Animation, und
# in seiner Ruheschleife zeigt er zweimal je Durchgang fuer vier Bilder den
# Kopf "bild_kopf_blinzeln" statt "bild_kopf_neutral" (maskottchen/zmaj.json).
# Vor dem Bild wartet das Skript darum, bis jeder sichtbare Drache den Kopf
# mit offenen Augen zeigt, haelt alle Animationen dort an und laesst sie
# nach dem Bild weiterlaufen. Animationen ohne diese Ebenen (aeltere
# Zeichnung) bleiben unbeachtet. Die App bleibt, wie sie ist.
DRACHE_ANHALTEN = r"""
    const deckkraft = (l, fr) => {
      const o = l && l.ks && l.ks.o;
      if(!o) return 100;
      if(!o.a) return +o.k || 0;
      let v = 0;
      for(const k of o.k){ if(k.t <= fr){ if(k.s !== undefined) v = Array.isArray(k.s) ? k.s[0] : k.s; } else break; }
      return +v || 0;
    };
    const augenOffen = a => {
      const ls = (a.animationData && a.animationData.layers) || [];
      const offen = ls.find(l => l.nm === 'bild_kopf_neutral'), zu = ls.find(l => l.nm === 'bild_kopf_blinzeln');
      if(!offen) return true;
      const fr = (a.firstFrame || 0) + (a.currentFrame || 0);
      return deckkraft(offen, fr) > 0 && !(zu && deckkraft(zu, fr) > 0);
    };
    const animationen = () => (window.lottie && lottie.getRegisteredAnimations ? lottie.getRegisteredAnimations() : [])
      .filter(a => a.isLoaded && a.wrapper && a.wrapper.isConnected);
    const sichtbar = a => a.wrapper.getClientRects().length > 0;
    window.__drachePausieren = async () => {
      const t0 = Date.now();
      while(Date.now() - t0 < 8000){
        const alle = animationen();
        if(alle.filter(sichtbar).every(augenOffen)){
          window.__angehalten = alle.filter(a => !a.isPaused);
          window.__angehalten.forEach(a => a.pause());
          return alle.filter(sichtbar).length;
        }
        await new Promise(r => setTimeout(r, 15));
      }
      throw new Error('Drache: nach 8 s noch keine offenen Augen');
    };
    window.__dracheNoch = () => animationen().filter(sichtbar)
      .filter(a => !augenOffen(a) || (!a.isPaused && (window.__angehalten || []).includes(a))).length
      ? 'Drache hat sich bewegt' : '';
    window.__dracheWeiter = () => {
      (window.__angehalten || []).forEach(a => { try{ a.play(); }catch(e){} });
      window.__angehalten = [];
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
        window.__muenzen01 = [muenzenGes, muenzenAus];     // KM wie hier auf allen Bildern (__standZurueck)
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
        // vorher, und das Skript bricht vor dem Bild ab (seit dem
        // Feinschliff 16.11.2026, mit der strengeren Messung und in halben
        // Punkten; vorher stand dann nur ein Hinweis in der Ausgabe). Ganz
        // oben am Rand wirkte die Reiterleiste gedraengt (fr Handy); darum
        // unter 4 Punkten erst die Leiste Lernpfad/Geschichten/Wiederholen
        // darueber, dann erst die Reiterleiste naeher an den Rand.
        // Pruefung nach der Kopfleiste 16.11.2026: Auch 10 Punkte waren
        // knapp (am Handy fr 7, mit der Leiste Lernpfad oben). Hoeher als 11
        // ging die Reiterleiste nicht, dann stand die Leiste darueber halb im
        // Bild. Jetzt liegt oben der Streifen (siehe __bandAn), und die
        // Reiterleiste steht 0 bis 24 Punkte unter ihm, bis unten keine Zeile
        // mehr haengt; geht das nicht, ebenso die Leiste Lernpfad/Geschichten/
        // Wiederholen und zuletzt die Karte "Heute" (Probe 16.11.2026: am
        // Handy en und nl schnitt der Rand unten ab 13 bzw. 12 Punkten
        // ueber der Reiterleiste die Beschreibung des letzten Levels, mit der
        // Leiste Lernpfad oben die des fuenften; mit "Heute" oben stehen drei
        // Level im Bild). Geht nichts davon, bricht das Skript vor dem Bild ab.
        const modus = (document.getElementById('modeWords') || {}).parentElement;
        let frei = '', wer = '';
        const anker = [['Reiterleiste', oben]];
        if(oben === leiste) anker.push(['Lernpfad', modus], ['Heute', document.getElementById('questBox')]);
        for(const [name, el] of anker){
          if(!el || !el.getClientRects().length) continue;
          frei = await window.__bandFrei(el, 24);
          if(frei){ wer = name; break; }
        }
        await new Promise(r=>setTimeout(r,300));
        const reiter = leiste ? leiste.querySelector('[aria-selected="true"]') : null;
        return (reiter ? reiter.dataset.stufe + ' | ' : '') + 'oben ' + (frei ? wer + ', ' + frei : 'angeschnitten')
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
    # 16.11.2026 (Feinschliff): Am Handy stand je nach Satz "Ueberspringen"
    # ohne Unterlaengen am unteren Rand (de, en, da) oder der Knopf
    # "Lektion abbrechen" halb im Bild (nl, nb, fr). Die Seite rueckt darum
    # bis zu ihrem oberen Rand hinauf (__randFrei); reicht das nicht, kommt
    # ein anderer Satz (bis zu 12 Mal neu gemischt) - das Motiv bleibt.
    # Pruefung danach (16.11.2026): Hinauf darf die Lektion nicht mehr (die
    # Karte stand 9 bis 11 statt 16 Punkte unter dem Rand, siehe __luftMin),
    # nur tiefer, und von den Saetzen gilt der, der dafuer am wenigsten
    # braucht (__satzFrei).
    ("04-kacheln", """
        const passt = q => q.typ === 'kacheln' && q.s.bs.trim().split(/\\s+/).length >= 4;
        const rand = /^[.,!?¿¡:;"„“”«»…()]+|[.,!?¿¡:;"„“”«»…()]+$/g;
        let q = null, frei = '';
        const wahl = {bester: Infinity};
        for(let versuch = 0; versuch < 12 && !frei; versuch++){
          if(versuch){ startLesson(); await new Promise(r=>setTimeout(r,600)); }
          let ziel = Lx.queue.findIndex((q, i) => i >= Lx.i && passt(q));
          for(let n = 0; ziel < 0 && n < 40; n++){ startLesson(); await new Promise(r=>setTimeout(r,600)); ziel = Lx.queue.findIndex(passt); }
          if(ziel < 0) throw new Error('keine Kachelaufgabe mit vier Woertern in Level 13');
          while(Lx.i < ziel){ await window.__antworte(true, 'lBody', ()=>Lx); }
          await new Promise(r=>setTimeout(r,800));
          q = Lx.queue[Lx.i];
          const teile = q.s.bs.split(/\\s+/).map(x => x.replace(rand, '').toLowerCase()).filter(Boolean);
          for(const soll of teile.slice(0, 2)){
            const b = [...document.querySelectorAll('#lBody #xBank .kachel:not(.platz)')].find(o => o.textContent.toLowerCase() === soll);
            if(b) b.click(); await new Promise(r=>setTimeout(r,450));
          }
          scrollTo(0,0); await new Promise(r=>setTimeout(r,500));
          frei = await window.__satzFrei(versuch, versuch === 11, wahl);
        }
        return q.s.bs + ' | ' + (frei || 'angeschnitten')"""),
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
    # 16.11.2026 (Feinschliff): wie 04 - erst hinaufruecken, sonst ein
    # anderer Satz. Pruefung danach: wie 04 nicht mehr hinauf, und der Satz,
    # der am wenigsten mehr Rand oben braucht (__satzFrei).
    ("06-luecke", """
        const wb = document.querySelector('#lBody .weiterbox .btn');
        if(wb){ wb.click(); await new Promise(r=>setTimeout(r,500)); }
        const passt = q => q.typ === 'gap' && !(window.__f5 || '').includes(q.s.text)
          && /[.?!]\\s*$/.test(q.s.text) && q.s.text.trim().split(/\\s+/).length >= 4;
        let q = null, frei = '';
        const wahl = {bester: Infinity};
        for(let versuch = 0; versuch < 12 && !frei; versuch++){
          if(versuch){ startLesson(); await new Promise(r=>setTimeout(r,600)); }
          let ziel = Lx.queue.findIndex((q, i) => i >= Lx.i && passt(q));
          for(let n = 0; ziel < 0 && n < 40; n++){ startLesson(); await new Promise(r=>setTimeout(r,600)); ziel = Lx.queue.findIndex(passt); }
          while(Lx.i < ziel){ await window.__antworte(true, 'lBody', ()=>Lx); }
          await new Promise(r=>setTimeout(r,800));
          q = Lx.queue[Lx.i]; const inp = document.getElementById('xIn');
          inp.value = q.s.answer.split(' / ')[0]; inp.dispatchEvent(new Event('input', {bubbles:true})); inp.blur();
          scrollTo(0,0); await new Promise(r=>setTimeout(r,300));
          frei = await window.__satzFrei(versuch, versuch === 11, wahl);
        }
        return q.s.text + ' | ' + (frei || 'angeschnitten')"""),
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
    # wieder wie auf Bild 1 (eine erfuellt, zwei zu 60 %).
    # Feinschliff 16.11.2026: Seitdem stehen vor jedem Bild auch die KM wie
    # auf Bild 1 (__standZurueck). Am Handy schnitt der untere Rand eine
    # Zeile der Karte "Markiert" durch (de, sv, nl, da). Mit "Weitermachen"
    # oben gab es oft keine Lage ohne: weiter hinauf stiess der Knopf oben
    # an, weiter hinunter stand ueber ihm allein "9 dage tilbage" oder der
    # Drache halb im Bild. Darum probiert das Handy drei Ausschnitte, bis
    # einer aufgeht: oben die Karte "Heute" ("Weitermachen" ganz aus dem
    # Bild), oben "Weitermachen" wie bisher, oben die Leiste Lernpfad/
    # Geschichten/Wiederholen. In jedem sucht __randFrei den Rand zwischen
    # zwei Zeilen. Tablets bleiben ganz oben, wie bisher. Die Karte
    # "Markiert" bleibt unten angeschnitten oder steht ganz im Bild.
    # Pruefung nach der Kopfleiste 16.11.2026: am Handy mit dem Streifen oben
    # (__bandFrei statt __randFrei, siehe dort).
    ("08-wiederholen", """
        if(window.__tagwerk01) tagwerk[today()] = JSON.parse(window.__tagwerk01);
        homeMode = 'topf'; showHome(); await new Promise(r=>setTimeout(r,600));
        scrollTo(0,0); await new Promise(r=>setTimeout(r,200));
        const text = t('btn.weitermachen');
        const w = [...document.querySelectorAll('button')].find(b => b.offsetParent && b.textContent.includes(text));
        let frei = '', wie = 'ganz oben';
        if(document.documentElement.classList.contains('gross')) frei = await window.__randFrei();
        else if(w){
          // Pruefung nach der Kopfleiste 16.11.2026: Bis dahin rollte die
          // Seite hinauf, bis die Karte "Heute" oben anstiess - sie stand 6
          // bis 7 Punkte unter dem Rand, "Weitermachen" bei de 10 (vor dem
          // Feinschliff 16). Jetzt liegt oben der Streifen (siehe __bandAn),
          // und unter ihm stehen der Reihe nach die Karte "Heute" ("Weiter-
          // machen" mit seinem Schatten darunter verdeckt), "Weitermachen" und
          // die Leiste Lernpfad/Geschichten/Wiederholen, je 0 bis 24 Punkte
          // tiefer, bis unten keine Zeile mehr haengt.
          const leiste = (document.getElementById('modeWords') || {}).parentElement;
          for(const [name, el] of [['Heute', document.getElementById('questBox')], ['Weitermachen', w], ['Leiste', leiste]]){
            if(!el || !el.getClientRects().length) continue;
            wie = name + ' oben';
            frei = await window.__bandFrei(el, 24);
            if(frei) break;
          }
        }
        return scrollY + ' | ' + wie + ' | ' + (frei || 'angeschnitten')"""),
]

# Wie weit __randFrei die Seite vor dem Bild verschieben darf (Punkte, siehe
# dort). Ohne Eintrag: hinauf, bis oben etwas anstoesst, oder tiefer mit
# mehr Rand oben. Bild 2, 4, 6 und 8 suchen ihre Lage selbst; hier wird nur
# noch nachgeprueft.
SPIELRAUM = {
    "02-amt": {"nurPruefen": True},
    "04-kacheln": {"nurPruefen": True},
    "06-luecke": {"nurPruefen": True},
    "08-wiederholen": {"nurPruefen": True},
}


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


def bilder_machen(sprache, ziel, chrome=None, geraet="handy", aussehen=None, version=None, kennung_ab=1):
    """aussehen: None = wie bisher (Playwright stellt hell ein), "hell" oder
    "dunkel". Die Store-Bilder sind seit v5 (15.10.2026) dunkel; die App folgt
    dem Gerät, darum wird hier das Gerät dunkel gestellt, nicht die App.

    version: Nummer für die Fußzeile ("Zmaj v1.2"), wie sie app_bauen.py
    (version_einsetzen) aus versionName der Hülle in die gebaute App setzt.
    In web/index.html steht nur der Rückfallwert, und der hinkt vor einem
    Release eine Nummer hinterher (30.10.2026: Bilder für 1.2 zeigten 1.1).
    Ersetzt wird nur in der ausgelieferten Seite, web/ bleibt unberührt.

    kennung_ab: mit welcher Geraete-Kennung (1 bis 6, siehe GERAETE_IDS) der
    erste Durchgang beginnt. Wer nur einzelne Bilder eines Satzes neu macht,
    braucht dieselben Tagesaufgaben wie auf den uebrigen (Pruefung nach der
    Kopfleiste 16.11.2026: Store-Bilder 1.4 nl am Handy mit Kennung 2)."""
    from playwright.sync_api import sync_playwright

    if not 1 <= kennung_ab <= len(GERAETE_IDS):
        raise SystemExit("--kennung %r: 1 bis %d" % (kennung_ab, len(GERAETE_IDS)))
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
    srv, basis = server_starten()
    pfade = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path=chrome) if chrome else pw.chromium.launch()
            # Feinschliff 16.11.2026: Haengt am Rand eine halbe Zeile, und es
            # gibt keine Lage ohne (Tablets haben wenig Spielraum: die Seite
            # darf nur bis zur Kopfleiste hinauf), kommt der ganze Lauf noch
            # einmal mit der naechsten Geraete-Kennung - andere
            # Tagesaufgaben, deren Text anders umbricht, und alles darunter
            # steht eine Zeile hoeher oder tiefer. Auf allen Bildern eines
            # Laufs bleiben es dieselben.
            for kennung in GERAETE_IDS[kennung_ab - 1:]:
                try:
                    pfade = ein_lauf(browser, basis, sprache, ziel, g, geraet, farbe, version, kennung)
                    break
                except Angeschnitten as e:
                    fehler = str(e)
                    print("  %-16s %s - noch einmal mit anderen Tagesaufgaben" % ("(" + kennung + ")", fehler))
            else:
                raise SystemExit(fehler)
            browser.close()
    finally:
        srv.shutdown()
    return pfade


class Angeschnitten(Exception):
    """Am Bildrand haengt eine halbe Zeile oder ein halber Knopf."""


def ein_lauf(browser, basis, sprache, ziel, g, geraet, farbe, version, kennung):
    """Ein Durchgang durch alle Schritte mit einer Geraete-Kennung; gibt die
    Pfade der Bilder zurueck."""
    kontext = browser.new_context(viewport={"width": g["breite"], "height": g["hoehe"]},
                                  device_scale_factor=g["dsf"], locale=sprache, **farbe)
    seite = kontext.new_page()
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
       "localStorage.setItem(%s, %s); localStorage.setItem(%s, %s); return 1"
       % (json.dumps(lernstand()), json.dumps(sprache),
          json.dumps(ERFOLG_GESEHEN), json.dumps(json.dumps(erfolge_ids())),
          json.dumps(GERAETE_ID_SCHLUESSEL), json.dumps(kennung)))
    seite.goto(basis + "/index.html?neu=%d" % time.time())
    seite.wait_for_function("typeof openLevel === 'function' && typeof Lx !== 'undefined'", timeout=30000)
    seite.wait_for_timeout(6000)   # Vorspann und Drache
    js(open(os.path.join(HIER, "antworte.js"), encoding="utf-8").read())
    js(RAND_PRUEFUNG)
    js(DRACHE_ANHALTEN)
    js("const st = document.createElement('style'); st.textContent = '#btnBack{display:none!important}'; "
       "document.head.append(st); return 1")
    pfade, stand1 = [], None
    for name, code in SCHRITTE:
        # Rand oben wieder wie in der App, kein Streifen oben
        js("window.__polsterZurueck(); window.__bandWeg(); window.__obenStand = false; return 1")
        ergebnis = js(code)
        lage = js("return await window.__randFrei(%s)" % json.dumps(SPIELRAUM.get(name, {})))
        stoert = js(NICHTS_IM_BILD)
        if stoert:
            raise SystemExit("%s %s: %s" % (sprache, name, stoert))
        stand = js(STAND_IM_BILD)
        stand1 = stand1 or stand
        for was, jetzt, vorher in zip(("KM", "Tagesaufgaben"), stand, stand1):
            if jetzt and jetzt != vorher:
                raise SystemExit("%s %s %s: %s %r statt %r wie auf Bild 1"
                                 % (sprache, geraet, name, was, jetzt, vorher))
        # Abbruch statt Hinweis (Feinschliff 16.11.2026), siehe RAND_PRUEFUNG
        schnitte = js("return window.__randSchnitte()")
        if schnitte:
            raise Angeschnitten("%s %s %s: am Rand angeschnitten: %s"
                                % (sprache, geraet, name, " | ".join(schnitte)))
        # Stand die Seite ganz oben, klebt die Kopfleiste nicht am Rand
        # (Pruefung nach dem Feinschliff 16.11.2026, siehe __luftMin); steht
        # sie nicht ganz oben, liegt oben der Streifen (Pruefung nach der
        # Kopfleiste, siehe __bandAn) - auf jedem Bild
        luft = js("return window.__luftPruefen()")
        if luft[0] < luft[1] - 0.5:
            raise SystemExit("%s %s %s: ueber dem obersten Teil nur %.1f Punkte Luft statt %s%s"
                             % (sprache, geraet, name, luft[0], luft[1],
                                "" if luft[2] or luft[0] else " (Seite nicht ganz oben, kein Streifen)"))
        lage += " | Luft oben %.0f%s" % (luft[0], " (Streifen)" if luft[2] else "")
        pfad = os.path.join(ziel, name + ".png")
        for _ in range(4):
            js("return await window.__drachePausieren()")
            seite.screenshot(path=pfad)
            bewegt = js("return window.__dracheNoch()")
            js("window.__dracheWeiter(); return 1")
            if not bewegt:
                break
        else:
            raise SystemExit("%s %s %s: %s" % (sprache, geraet, name, bewegt))
        pfade.append(pfad)
        print("  %-16s %s | %s" % (name, str(ergebnis)[:60].replace("\n", " "), lage))
    print("  %-16s Tagesaufgaben: %s" % ("(" + kennung + ")", stand1[1][:70]))
    kontext.close()
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
    p.add_argument("--kennung", type=int, default=1,
                   help="mit der wievielten Geräte-Kennung (Tagesaufgaben) begonnen wird, 1 bis %d; "
                        "nur zum Nachmachen einzelner Bilder eines Satzes" % len(GERAETE_IDS))
    a = p.parse_args(argv)
    if a.geraet != "handy" and not a.ziel:
        p.error("--geraet %s braucht --ziel (Rohbilder, nicht für store/screenshots)" % a.geraet)
    ziel = a.ziel or (os.path.join(WURZEL, "store", "screenshots") if a.sprache == "de"
                      else os.path.join(WURZEL, "docs", "assets", "screenshots-" + a.sprache))
    pfade = bilder_machen(a.sprache, ziel, a.chrome, a.geraet, a.aussehen, a.version, a.kennung)
    if a.montage:
        montage(pfade, a.montage)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
