#!/bin/sh
# Macht die acht Store-Bilder im kopflosen Chrome (Port 9444). Anleitung: LIESMICH.txt
# 405 x 720 CSS-Punkte mal 8/3 = genau 1080 x 1920.
S="$(cd "$(dirname "$0")" && pwd)"
cd "$S"
P="C:/Users/Ajdin/AppData/Local/Programs/Thonny/python.exe"
export PYTHONIOENCODING=utf-8 BREITE=405 HOEHE=720 DSF=2.6666666667
OUT="$S/../screenshots"
mkdir -p "$OUT"
pc(){ "$P" pc.py "$@"; }

"$P" stand.py
STAND=$("$P" -c "import json;print(json.dumps(open('_stand.json',encoding='utf-8').read()))")
pc js "standGeladen = false; localStorage.clear(); localStorage.setItem('zmaj_stand', $STAND); localStorage.setItem('zmaj_einwilligung', JSON.stringify({wahl:'nein',stand:1,zeit:new Date().toISOString()})); localStorage.setItem('zmaj_sprache','de'); return 'ok'"
pc nav "http://127.0.0.1:8777/index.html"
sleep 15
pc js "$(cat antworte.js)"

# 1 Startseite
pc js "const q = questsHeute(), t = today(); tagwerk[t] = {}; q.forEach((x,i) => { tagwerk[t][x.id] = i === 0 ? x.ziel : Math.floor(x.ziel * 0.6); }); [...known].slice(40, 47).forEach((id, i) => { topf['w:' + id] = {typ: i % 2 ? 'mcrev' : 'mc', n: 0, z: Date.now() - i * 60000}; }); homeMode = 'words'; showHome(); scrollTo(0,0); await new Promise(r=>setTimeout(r,2500)); return [...document.querySelectorAll('.nachfrage, .einwilligung, .werbung')].length + ' Karten offen'"
pc bild "$OUT/01-start.png"

# 2 Lernpfad
pc js "const z = [...document.querySelectorAll('body *')].find(e => e.offsetParent && e.className === 'label' && e.textContent.trim() === 'Zuhause'); scrollBy(0, z.getBoundingClientRect().top - 70); await new Promise(r=>setTimeout(r,400)); return scrollY"
pc bild "$OUT/02-lernpfad.png"

# 3 Neues Wort
pc js "openLevel(12); await new Promise(r=>setTimeout(r,400)); startLesson(); await new Promise(r=>setTimeout(r,800)); scrollTo(0,0); return Lx.queue.map(q=>q.typ + ':' + (q.w ? q.w.de : (q.s ? q.s.text : ''))).join(' | ')"
pc bild "$OUT/03-neues-wort.png"

# 4 Auswahl, 5 richtig
pc js "let ziel = Lx.queue.findIndex(q => q.typ === 'mc' && q.w.de.length > 8); if(ziel < 0) ziel = Lx.queue.findIndex(q => q.typ === 'mc'); while(Lx.i < ziel){ await window.__antworte(true, 'lBody', ()=>Lx); } await new Promise(r=>setTimeout(r,800)); scrollTo(0,0); return document.getElementById('lBody').innerText.slice(0,120)"
pc bild "$OUT/04-auswahl.png"
pc js "const q = Lx.queue[Lx.i]; [...document.querySelectorAll('#lBody .opt')].find(o => o.textContent === q.w.bs).click(); await new Promise(r=>setTimeout(r,1000)); return document.getElementById('lBody').innerText.slice(0,160)"
pc bild "$OUT/05-richtig.png"

# 6 Luecke. Kam der Lueckensatz in dieser Lektion schon vor der Auswahlaufgabe,
# wird eine neue Lektion gemischt.
pc js "document.querySelector('#lBody .weiterbox .btn').click(); await new Promise(r=>setTimeout(r,500)); let ziel = Lx.queue.findIndex((q, i) => i >= Lx.i && q.typ === 'gap'); for(let n = 0; ziel < 0 && n < 8; n++){ startLesson(); await new Promise(r=>setTimeout(r,600)); ziel = Lx.queue.findIndex(q => q.typ === 'gap'); } while(Lx.i < ziel){ await window.__antworte(true, 'lBody', ()=>Lx); } await new Promise(r=>setTimeout(r,800)); const q = Lx.queue[Lx.i]; const inp = document.getElementById('xIn'); inp.value = q.s.answer.split(' / ')[0]; inp.dispatchEvent(new Event('input', {bubbles:true})); inp.blur(); scrollTo(0,0); await new Promise(r=>setTimeout(r,300)); return q.s.text + ' -> ' + inp.value"
pc bild "$OUT/06-luecke.png"

# 7 Geschichte mit angetipptem Wort
pc js "Lx = null; openStory(3); await new Promise(r=>setTimeout(r,600)); [...document.querySelectorAll('#rBody .w')].find(x => x.textContent === 'povrća').click(); await new Promise(r=>setTimeout(r,500)); stilleBitte(); scrollTo(0,0); return document.getElementById('rBubble').innerText"
pc bild "$OUT/07-geschichte.png"

# 8 Wiederholen
pc js "homeMode = 'topf'; showHome(); await new Promise(r=>setTimeout(r,600)); const r = document.getElementById('topfBox').getBoundingClientRect(); scrollTo(0,0); await new Promise(r=>setTimeout(r,200)); const w = [...document.querySelectorAll('button')].find(b => b.offsetParent && b.textContent.includes('Weitermachen')); scrollBy(0, w.getBoundingClientRect().top - 16); await new Promise(r=>setTimeout(r,400)); return scrollY"
pc bild "$OUT/08-wiederholen.png"
ls -la "$OUT"
