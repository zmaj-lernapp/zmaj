/* =================== AUFGABEN-BAUSTEINE =================== */
/* Zwei Vokabeln koennen in einer Oberflaechensprache dieselbe Uebersetzung
   haben: auf Daenisch heissen majka und mama beide "mor", auf Franzoesisch
   kolac und torta beide "gateau". Auf Deutsch faellt das nie auf.
   Ohne diese Funktion waere die Auswahlaufgabe dort nicht entscheidbar und
   die Schreibaufgabe nicht loesbar - eine richtige Antwort kostet ein Herz.
   Gefunden am 26.09.2026, elf Stellen ueber acht Sprachen. */
const _bedeutung = s => String(s||'').toLowerCase().replace(/[.!?\u2026]+$/,'').replace(/\s+/g,' ').trim();
/* Geschwister sind Woerter, die als Antwort genauso gelten: gleiche
   Uebersetzung (im Daenischen zeigen majka und mama beide "mor") oder
   ausdruecklich gleichwertig ueber "auch" in vokabeln.py (majka und mama
   auch im Deutschen, wo "Mutter" und "Mama" verschieden dastehen - Ajdin
   am 05.10.2026: "bei der einen Frage ist nur majka richtig und bei der
   anderen nur mama"). Fuer die Auswahl gilt "auch" in beide Richtungen,
   beim Tippen nur fuer das Wort, bei dem es steht (annehmbar()): bei
   "Hallo" (Merhaba) zaehlt auch Zdravo, bei "Hallo (neutral)" aber nicht
   Merhaba. Verglichen wird je Form, weil "auch" auch einen Teil wie "drug"
   aus "drug / drugarica" nennen darf. Ajdin am 05.10.2026, 34 Paare. */
const _formen = s => String(s||'').split(' / ').map(_bedeutung);
/* Alle Woerter, unter denen eine Aufgabe Antworten sucht. Im Lernpfad dieselben
   wie immer; im Zahnarzt-Teil dazu seine eigenen, sonst stuenden dort zwei
   gleich uebersetzte Saetze als richtig und falsch nebeneinander. */
const wortVorrat = () => CATEGORIES.concat(imZa() ? zaLevel() : []).flatMap(c=>c.words);
/* Aspektpaare (31.10.2026, Wortschatz-Paket 1): ostati und ostajati heissen
   beide "bleiben", doći und dolaziti beide "kommen". Ajdin: "beide wörter
   rein die sollen separat sein wenn einer gelernt wurde dann ist der andere
   noch nicht gelernt" - eigene Kennung, eigener Lernstand, und
   vollendet/unvollendet zeigt die App nicht an. Deshalb:
   - in der Auswahl stehen die beiden nie zusammen (geschwister()), auch
     wenn ihre Bedeutungen verschieden dastehen (popiti "trinken /
     austrinken" neben piti "trinken");
   - beim Tippen ist das Gegenstueck NICHT richtig (annehmbar() laesst es
     weg), sondern bekommt einmal "Fast richtig!" mit dem Hinweis auf das
     andere Verb des Paares (task.partner, partnerAntworten()) - ohne Leben,
     wie ein Tippfehler.
   Das Feld "partner" in vokabeln.py nennt das bs des Gegenstuecks und
   steht nur an einem der beiden; gelesen wird es in beide Richtungen. */
const istPartner = (w, x) => !!(w && x && x.bs !== w.bs && (x.partner === w.bs || w.partner === x.bs));
function partnerVon(w){
  return CATEGORIES.flatMap(c=>c.words).filter(x => istPartner(w, x));
}
/* Was beim Tippen als Gegenstueck erkannt wird: seine Formen und sein
   "auch", mit " / " wie bei matches(). Leer, wenn das Wort keins hat. */
function partnerAntworten(w){
  return partnerVon(w).flatMap(x => [x.bs, ...(x.auch || [])]).join(' / ');
}
/* Wortschatz-Pakete 5 bis 9 (06.11.2026): diese Woerter heissen teilweise gleich
   („so“, „ganz“, „hier“, „sehr“) und sollen nie zusammen in einer Auswahl stehen.
   Beim Tippen zaehlt das andere Wort trotzdem nicht: "auch" hat Ajdin dafuer
   nicht freigegeben.
   Pruefbericht 1.3 (06.11.2026): Bei der Frage "ziehen" (vući) stand povlačiti
   mit "ziehen / zurückziehen" als falscher Knopf, bei "also" (dakle) pa mit "und
   dann / also". Wer das antippt, hat recht und verliert ein Leben. Die Paare ab
   der zweiten Zeile sind genau solche Faelle, jeder in mindestens einer der acht
   Sprachen; bei važan / bitan und nakon / po trennt nur auf Deutsch die Klammer.
   Die Liste gilt in allen Sprachen, tests_e2e/test_antworten.py sucht je Sprache
   nach weiteren. */
const NIE_NEBENEINANDER = [['sav', 'cijeli'], ['tu', 'ovdje'], ['tako', 'ovako'], ['vrlo / veoma', 'jako'],
  ['vući', 'povlačiti'], ['dakle', 'pa'], ['iz', 'od'], ['Hajde!', 'Hajmo!'], ['tražiti', 'zvati'],
  ['dokument', 'potvrda'], ['Sve je dobro', 'Šta ima?'], ['bitan', 'važan'], ['nakon', 'po'],
  /* Wortschatz-Pakete 10 bis 20 (07.11.2026): was die Paketdateien beim Einbau ausdruecklich
     nicht zusammen in eine Auswahl stellen ("einbau_hinweis", b2_2_pruefung.md: gleiche
     deutsche Teil-Bedeutung wie ein Wort der App, unuk / unuka sehen im Akkusativ gleich aus). */
  ['unuk', 'unuka'], ['izbrisati', 'brisati'], ['izbrisati', 'obrisati'],
  ['rješenje / upravni akt', 'rješenje'], ['začin', 'začini'], ['začiniti', 'začini'], ['tablica', 'natpis'],
  ['tablica', 'tabla'], ['pronalazak', 'otkriće'], ['trg', 'mjesto'], ['objekat', 'zgrada'],
  ['središte', 'centar'], ['prijevoz / prevoz', 'transport'], ['željeznička stanica', 'stanica'],
  ['automobil', 'auto'], ['udes', 'nesreća'], ['sjena', 'hlad'], ['njiva', 'polje'], ['stablo', 'drvo'],
  ['prijelaz / prelaz', 'raskrsnica'], ['većinom', 'uglavnom'], ['skroz', 'sasvim'],
  ['približno', 'otprilike'], ['suviše', 'previše'], ['pravilno', 'tačan'], ['svakodnevno', 'dnevni'],
  ['dosad / dosada', 'dosada'], ['iznenada', 'odjednom'], ['najzad', 'konačno'], ['zamalo', 'skoro'],
  ['van', 'izvan'], ['van', 'vani'], ['jednak', 'isti'], ['kompletan', 'potpun'], ['ispravan', 'tačan'],
  ['obojica', 'oba'], ['obojica', 'oboje'], ['manjak', 'nedostatak'], ['curiti', 'kapi'],
  ['procuriti', 'kapi'], ['renovirati', 'obnoviti'], ['trpjeti', 'podnijeti'], ['pretrpjeti', 'podnijeti'],
  ['pamćenje', 'memorija'], ['uznemiriti', 'smetati'], ['uznemiravati', 'smetati'], ['trenirati', 'vježbati'],
  ['ispitivanje', 'istraživanje'], ['ispitivanje', 'pregled'], ['istraživati', 'pregledati'],
  ['istražiti', 'pregledati'], ['ispitati', 'razmatrati'], ['ispitivati', 'razmatrati'],
  ['proučiti', 'studirati'], ['proučavati', 'studirati'], ['debata', 'rasprava / diskusija'],
  ['razjasniti', 'riješiti'], ['servis', 'radionica'], ['ravnica', 'nivo'], ['ribolov / pecanje', 'pecati'],
  ['prebaciti', 'prenijeti'], ['prebacivati', 'prenijeti'], ['slijediti', 'pratiti'],
  ['uslijediti', 'pratiti'], ['izraditi', 'kreirati'], ['izrađivati', 'kreirati'], ['okončati', 'završiti'],
  ['urediti', 'uspostaviti'], ['urediti', 'složiti'], ['uređivati', 'uspostaviti'], ['uređivati', 'složiti'],
  ['unaprijediti', 'poboljšati'], ['unapređivati', 'poboljšati'], ['makar', 'bar'], ['nedovoljno', 'premalo'],
  ['najprije', 'prvo'], ['omiljen', 'popularan'], ['miran', 'smiren'], ['mnoštvo', 'količina'],
  /* Im Level trauer_beileid heisst patnja "Leid" und stradanje "Verunglücken / Leid": der
     falsche Knopf waere in Wahrheit richtig (tests_e2e/test_antworten.py, V1). */
  ['patnja', 'stradanje'],
  /* Stufen-Reiter (13.11.2026): tako ("so") und pa ("und dann / also") stehen seitdem beide
     im Level kleine_woerter. Auf Englisch heisst pa "and then / so" - bei der Frage "so"
     waere der falsche Knopf in Wahrheit richtig (tests_e2e/test_antworten.py, V1, en). */
  ['tako', 'pa'],
  /* Pruefbericht 1.4 (14.11.2026), V4: Molim heisst "Bitte", auf Englisch "Please / you're
     welcome (polite)", und ist die uebliche Antwort auf Hvala. Neben "Gern geschehen" (Nema
     na čemu) war der falsche Knopf in Wahrheit richtig, schon in Level 1 und in allen acht
     Sprachen. dići und dizati sind die Kurzformen von podići und podizati (Ajdin,
     v111_entscheidungen.md Nr. 53), auch ueber Kreuz. Beim Tippen aendert sich nichts. */
  ['Molim', 'Nema na čemu'], ['podići / podignuti', 'dići'], ['podići / podignuti', 'dizati'],
  ['podizati', 'dići'], ['podizati', 'dizati'],
  /* Pruefbericht 1.4 (14.11.2026), B8: zajam und pozajmica heissen in allen Sprachen
     "Darlehen" (Level bank_darlehen), jaran und drug / drugarica beide "Kumpel" (Level
     kennenlernen). Nur die Klammer trennt sie. */
  ['zajam', 'pozajmica'], ['jaran', 'drug / drugarica']];
/* Pruefbericht 1.4 (14.11.2026), B5: Ćao ist auch „Hallo“ (Ajdin, F16). Es stand als
   falscher Knopf neben „Hallo“, in 46 bis 57 von 400 Ziehungen. Bei Merhaba und, nach
   Ajdins „passt“ (Offen-Liste, Punkt 2), auch bei Zdravo („Hallo (neutral, überall)“)
   zaehlt es beim Tippen; das "auch" am Wort haelt es aus der Auswahl (geschwister()).
   Solange Zdravo Ćao beim Tippen nicht nahm, stand oben das Paar Zdravo / Ćao. Seit dem
   14.11.2026 ist es raus: es waere doppelt und sagte "beim Tippen zaehlt es nicht". */
/* Seit den Paketen 10 bis 20 sind es gut 90 Paare, und distractors() fragt fuer jedes Wort
   des Vorrats: als Menge nachschlagen statt die Liste jedes Mal abzulaufen (07.11.2026). */
const _NIE = new Set(NIE_NEBENEINANDER.flatMap(([x, y]) => [x + '\u0000' + y, y + '\u0000' + x]));
const nieNebeneinander = (a, b) => _NIE.has(a + '\u0000' + b);
/* auch_var zaehlt hier wie auch (12.11.2026): steht boca einmal als eigenes
   Wort in der App, liegt es nie als falscher Knopf neben flaša. */
const _auchAlle = w => [...(w.auch || []), ...(w.auch_var || [])];
function geschwister(w){
  const b = _bedeutung(w.de);
  const meineAuch = new Set(_auchAlle(w).flatMap(_formen));
  const meineFormen = _formen(w.bs);
  return wortVorrat().filter(x => x.bs !== w.bs &&
    ((b && _bedeutung(x.de) === b) ||
     istPartner(w, x) ||
     nieNebeneinander(w.bs, x.bs) ||
     _formen(x.bs).some(f => meineAuch.has(f)) ||
     _auchAlle(x).flatMap(_formen).some(f => meineFormen.includes(f))));
}
/* auch_var (12.11.2026, varianten.py): andere bosnische Woerter, die beim
   Tippen genauso gelten - bei "Flasche" auch boca, bei "Pijem kahvu" auch
   "Pijem kafu". Gebaut in inhalt.py, nur an Woertern, die getippt werden
   koennen (typable()). Sie zaehlen beim Tippen, hier und im Lueckensatz,
   und halten in der Auswahl falsche Knoepfe fern (geschwister()). Beim
   Sprechen zaehlt weiter nur bs. */
function annehmbar(w){
  const b = _bedeutung(w.de);
  const gleich = b ? wortVorrat().filter(x => x.bs !== w.bs && _bedeutung(x.de) === b && !istPartner(w, x)).map(x=>x.bs) : [];
  return [w.bs, ...gleich, ...(w.auch || []), ...(w.auch_var || [])];
}
function distractors(target, words, n){
  /* Auch die Bedeutung vergleichen, nicht nur das bosnische Wort. Sonst
     landen "majka" und "mama" in derselben Auswahl, beide zeigen "mor". */
  const gleich = new Set(geschwister(target).map(x=>x.bs));
  const raus = w => w.bs===target.bs || gleich.has(w.bs);
  let pool = words.filter(w=>!raus(w));
  if(pool.length<n) pool = wortVorrat().filter(w=>!raus(w));
  /* Pruefbericht 1.3 (06.11.2026), beides auf einem Weg:
     - Keine Bedeutung zweimal. Bei "Was bedeutet ...?" stand sonst zweimal
       "herstellen" da, und der doppelte Knopf schied sofort aus.
     - Zuerst dieselbe Art: Wort zu Wort, Satz zu Satz (istWort() auf der deutschen
       Bedeutung, damit jede Sprache dieselben Saetze hat). Wer ein Wort sucht,
       strich vorher die Saetze und musste weniger wissen, und ein Satz fiel als
       einziger auf. Die andere Art fuellt nur auf, in 21 Leveln reicht die eigene
       nicht. Reichen die verschiedenen Bedeutungen im Level nicht, dann der ganze
       Vorrat. */
  const seen = new Set([target.bs]), bedeutungen = new Set([_bedeutung(target.de)]); const out=[];
  const nimm = liste => {
    for(const w of liste){
      if(out.length===n) return;
      const b = _bedeutung(w.de);
      if(!seen.has(w.bs) && !bedeutungen.has(b)){ seen.add(w.bs); bedeutungen.add(b); out.push(w); }
    }
  };
  const satz = w => !istWort(grundBedeutung(w)), gemischt = shuffle(pool.slice());
  nimm(gemischt.filter(w => satz(w) === satz(target)));
  nimm(gemischt);
  if(out.length<n) nimm(shuffle(wortVorrat().filter(w=>!raus(w))));
  return out;
}
/* sprache: 'bs', wenn die Antworten bosnisch sind (17.10.2026) - dann traegt
   jeder Knopf lang="bs" und wird bosnisch vorgelesen. Bei mcrev sind es
   Bedeutungen in der Sprache der App, dort bleibt es leer. Bei der Grammatik
   ist es eine Funktion: sie bekommt die Antwort und sagt fuer jede einzeln
   'bs' oder '' (siehe gramAntwortBosnisch). */
function renderChoice(box, opts, correctKey, keyOf, onDone, sprache){
  box.innerHTML='';
  let answered=false;
  /* Antworten ueber 14 Zeichen stehen kleiner und ohne Serifen da (.opt.long).
     Bis zum 14.11.2026 je Knopf - war nur die richtige Antwort lang, stand
     sie als einzige anders da, und umgekehrt eine kurze richtige zwischen
     langen falschen. Bei den Fragen zu den Geschichten 31 B1-Fragen und 38
     der alten, ueber alle Sprachen gezaehlt (Pruefbericht 1.4, B13). Jetzt
     alle Knoepfe einer Aufgabe gleich: klein, sobald einer lang ist. */
  const klein = opts.some(o => keyOf(o).length > 14);
  opts.forEach(o=>{
    const b=document.createElement('button'); const label=keyOf(o);
    b.className='opt'+(klein?' long':''); b.textContent=label;
    const lang = typeof sprache === 'function' ? sprache(label) : sprache;
    if(lang) b.lang = lang;
    b.addEventListener('click',()=>{
      if(answered) return; answered=true;
      box.querySelectorAll('.opt').forEach(x=>{ x.disabled=true; if(x.textContent===correctKey) x.classList.add('right'); });
      const ok = label===correctKey; if(!ok) b.classList.add('wrong');
      sound(ok?'ok':'no');
      onDone(ok);
    });
    box.appendChild(b);
  });
  /* Ragen zwei Knoepfe nebeneinander ueber den Rand der Karte, stehen sie
     untereinander wie lange Antworten - sonst liess sich die ganze Seite
     seitlich verschieben. Bei grosser Systemschrift ab 130 %, aber auch
     bei normaler Schrift in spaeten Levels ("Bedienungsanleitung" neben
     "Waeschetrockner"). Ein paar Punkte in den Innenabstand der Karte
     hinein bleiben erlaubt, so sah es schon immer aus.
     Gefunden bei der Pruefung am 06.10.2026. */
  /* scrollWidth zaehlt in Punkten der Seite, getBoundingClientRect auf dem
     Tablet in Bildschirmpunkten - f rechnet um (rectFaktor(), am Handy 1) */
  const karte = (box.closest('.card') || box.parentElement).getBoundingClientRect();
  const f = rectFaktor() / GROSS;
  if(box.getBoundingClientRect().left * f + box.scrollWidth > karte.right * f) box.classList.add('one');
}

/* Die Frage einer Grammatikaufgabe: der bosnische Satz oben, die
   Uebersetzung aus der Klammer am Ende darunter in einer eigenen Zeile.
   Vorher stand beides in einer Zeile und brach mitten in der Klammer um -
   „___ kahve, molim.“ (Zwei / Kaffee, bitte.). Ajdin beim Durchspielen des
   Einstufungstests, 01.10.2026: "besser wenn der bosnische Satz auf einer
   Zeile ist und die Uebersetzung darunter". */
function gramFrageHtml(frage){
  const roh = String(frage || '').trim();
  const k = roh.match(/^(.*\S)\s*\(([^()]{2,})\)\s*$/);
  if(!k) return '<div class="ex-q">' + esc(roh) + '</div>';
  return '<div class="ex-q">' + esc(k[1]) + '<span class="ex-q-sub">' + esc(k[2].trim()) + '</span></div>';
}

/* Grammatikaufgaben tragen ihre Bedeutung meist schon in Klammern mit:
   „___ stanuješ?“ (Wo wohnst du?). Daraus wird nach der Antwort der fertige
   Satz und darunter seine Übersetzung. Steht keine Lücke in der Frage, gibt
   es nichts zusammenzusetzen - dann bleibt die Zeile weg, statt bloss die
   schon sichtbare Antwort zu wiederholen. */
function gramLoesung(g){
  const roh = String(g.frage || '').trim();
  const ANF = /^[\u201e\u201c\u201d"\u00ab\u00bb\u2018\u2019'\s]+/;
  const END = /[\u201e\u201c\u201d"\u00ab\u00bb\u2018\u2019'\s]+$/;
  if(roh.indexOf('___') >= 0){
    const klammer = roh.match(/\(([^()]{2,})\)\s*$/);
    const satz = (klammer ? roh.slice(0, klammer.index) : roh)
                   .replace('___', g.richtig).replace(ANF, '').replace(END, '').trim();
    return satz ? [satz, klammer ? klammer[1].trim() : ''] : null;
  }
  /* Keine Luecke: Manche Aufgaben geben den Satz in der eigenen Sprache vor
     und fragen nach der bosnischen Fassung - \u201eIch bin nicht m\u00fcde.\u201c mit der
     Antwort \u201eNisam umoran.\u201c. Dann ist die Frage selbst die \u00dcbersetzung.
     Nur dann, wenn ausser dem Zitat nichts dasteht - hoechstens eine
     Einleitung mit Doppelpunkt. Sonst geriete \u201eMehrzahl von \u201aku\u0107a\u2018?\u201c
     mit hinein, und dort ist das Zitat bosnisch, nicht die \u00dcbersetzung.
     Die Anfuehrungszeichen unterscheiden sich je Sprache, deshalb wird nach
     dem ersten und dem letzten gesucht statt nach einem festen Paar. */
  const Q = '\u201e\u201c\u201d"\u00ab\u00bb\u2018\u2019';
  let a = -1, b = -1;
  for(let i = 0; i < roh.length; i++){
    if(Q.indexOf(roh[i]) >= 0){ if(a < 0) a = i; b = i; }
  }
  if(a < 0 || b < a + 4) return null;
  if(b !== roh.length - 1) return null;          // hinter dem Zitat steht noch etwas
  const davor = roh.slice(0, a).trim();
  if(davor && davor.slice(-1) !== ':') return null;
  const inhalt = roh.slice(a + 1, b).trim();
  return inhalt ? [g.richtig, inhalt] : null;
}

/* Ist die Antwort einer Grammatikaufgabe bosnisch? (17.10.2026) Fast immer:
   "moja", "smo", "Gdje" - dann lang="bs". Nicht bei der Frage nach dem
   Geschlecht ("Welches Geschlecht hat „kuća“?"): dort heissen die Antworten
   "weiblich (ona)", auf Englisch "feminine (ona)" - ein Wort in der Sprache
   der App, dahinter das bosnische Fuerwort in Klammern. Mit lang="bs" laese
   ein Screenreader "weiblich" mit bosnischer Stimme (WCAG 3.1.2). Erkannt
   wird genau diese Klammer am Ende, sie steht in jeder Sprache gleich da
   (grammatik.py, Lektion genus). */
const GESCHLECHT_KLAMMER = /\((on|ona|ono)\)\s*$/;
const gramAntwortBosnisch = antwort => !GESCHLECHT_KLAMMER.test(String(antwort || ''));

/* Die Rueckmeldung nach der Antwort, in das Feld feld (#xFb einer Aufgabe,
   #rFb einer Geschichten-Frage). Das Wort darin ist meist bosnisch und
   steht seit dem 17.10.2026 als <span lang="bs"> da - ein Screenreader
   liest es dann bosnisch statt deutsch; zu sehen ist alles wie vorher.
   Bosnisch ist auch das Lob "Tačno!" (in allen Sprachen gleich). Nicht
   bosnisch sind die Bedeutung bei mcrev, die Geschlechter der Grammatik und
   die Antworten der Geschichten-Fragen: dort bosnisch === false.
   Danach wird die Rueckmeldung angesagt (#ansage, siehe ansagen()) - erst
   nach WEITER_NACH, wenn der Fokus auf Weiter liegt. */
function rueckmeldungZeigen(feld, klasse, schluessel, wort, bosnisch, anhang){
  if(!feld) return;
  const W = '\u0001';
  const teile = esc(t(schluessel, {wort: W})).split(W);
  const wortHtml = bosnisch === false ? esc(wort) : '<span lang="bs">'+esc(wort)+'</span>';
  feld.innerHTML = (schluessel === 'task.richtig' ? '<span lang="bs">'+teile.join('')+'</span>' : teile.join(wortHtml))
                 + (anhang ? esc(' ('+anhang+')') : '');
  feld.className = 'feedback '+klasse;
  ansagen(feld.innerHTML, WEITER_NACH + 80);
}

/* ---- Was eine Aufgabe vorliest (26.10.2026) ----
   Fuer pufferLaden(): genau der Text, den renderTask() an speak() bzw.
   spaeterSprechen() gibt - sonst laege der falsche Puffer bereit. Woerter:
   w.bs. Lueckensatz: der fertige Satz, sonst die Loesung (lueckeText,
   dieselbe Funktion wie in renderTask). Kacheln: der Satz. Mit wechselnder
   Zahl die gezogene Fassung; bei der naechsten Aufgabe ist sie noch nicht
   gezogen (das tut erst renderTask), dann nichts - ein Satz kommt ohnehin
   erst nach der Antwort, bis dahin ist sein Puffer laengst da.
   Grammatik: die Antwort, wenn sie bosnisch ist. */
function lueckeText(s){
  const ganz = s.text.replace('___', s.answer);
  return hoerbar(ganz) ? ganz : hoerbar(s.answer) ? s.answer : null;
}
function aufgabeText(task){
  if(!task) return null;
  if(task.typ === 'gap' || task.typ === 'kacheln'){
    if(!task.s || (task.s.zahl && task.v === undefined)) return null;
    const s = zahlFassung(task.s, task.v);
    return task.typ === 'gap' ? lueckeText(s) : s.bs;
  }
  if(task.typ === 'gram') return task.g && gramAntwortBosnisch(task.g.richtig) ? task.g.richtig : null;
  return task.w ? task.w.bs : null;
}
/* Die Aufgabe nach dieser - in Lektion, Level-Test oder Einstufung. */
function folgeAufgabe(task){
  for(const liste of [Lx && Lx.queue, Tx && Tx.qs, Ex && Ex.qs]){
    const i = Array.isArray(liste) ? liste.indexOf(task) : -1;
    if(i >= 0) return liste[i + 1] || null;
  }
  return null;
}
function woerterVorladen(task){
  if(!canListen) return;
  [task, folgeAufgabe(task)].forEach(a => {
    const text = aufgabeText(a);
    if(text) pufferLaden(audioDatei(text));
  });
}

function renderTask(task, body, done, opts={}){
  /* NUR innerhalb dieser Aufgabe suchen. Lektion und Test benutzen dieselben
     Kennungen (xOpts, xFb, ...). Sind beide gefuellt, liefert
     document.getElementById immer die ERSTE im Dokument - die der Lektion.
     Der Test legte seine Antwortknoepfe dadurch in den unsichtbaren
     Lektionskoerper und stand selbst ohne Knoepfe da. */
  const $$ = id => body.querySelector('#'+id);
  stilleBitte();                       // das Wort der vorigen Aufgabe nicht hineinreden lassen
  ansagen('');                         // ebenso ihr Ergebnis, falls es noch auf seine Ansage wartet
  const meineAufgabe = aufgabeMarke;   // gilt fuer verspaetete Erkennungs-Ergebnisse
  const pool = task.pool || curWords();
  const w = task.w;
  /* Zahlen, die wechseln (25.10.2026): einmal je Aufgabe ziehen, siehe
     zahlZiehen(). Die Wiederholung ({...task, retry:true}) hat task.v schon
     und kommt mit derselben Zahl. */
  if(task.s && task.s.zahl && task.v === undefined) task.v = zahlZiehen(task.s);
  woerterVorladen(task);               // ihr Wort und das der naechsten Aufgabe dekodieren (26.10.2026)
  const kick = (text)=> '<div class="kicker aufgabe'+(task.rep||task.retry?' mitmarke':'')+'">'+text+(task.rep?' · <span class="rep">'+t('task.wiederholung',{label:esc(task.rep)})+'</span>':'')+(task.retry?' · <span class="rep">'+t('task.nochmal')+'</span>':'')+'</div>';
  const rueckmeldung = (klasse, schluessel, wort, bosnisch, anhang)=>
    rueckmeldungZeigen($$('xFb'), klasse, schluessel, wort, bosnisch, anhang);
  const fb = (ok, right, extra, bosnisch)=> ok ? rueckmeldung('ok', 'task.richtig')
                                               : rueckmeldung('no', 'task.falsch', right, bosnisch, extra);
  /* Nach der Antwort: das Bosnische und darunter, was es heißt. Vorher
     konnte man eine Auswahlaufgabe richtig lösen, ohne je zu erfahren, was
     das Wort bedeutet - und bei den Höraufgaben stand überhaupt nichts
     Übersetztes auf dem Bildschirm. Ajdin am 18.09.2026. */
  /* auch (17.11.2026, Offen-Liste 7): oben steht als Loesung eine andere
     richtige Form als bs (naechsteAntwort(), gemeinteAntwort()). Dann kommt
     ueber bs klein "Auch richtig:" - sonst stuenden zwei verschiedene
     Loesungen ohne Erklaerung untereinander. Gesprochen wird weiter bs. */
  const loesung = (bs, de, auch)=>{
    const feld = $$('xFb');
    if(!feld || !bs || body.querySelector('.loesung')) return;
    feld.insertAdjacentHTML('afterend',
      '<div class="loesung">'+(auch ? '<span class="lauch">'+esc(t('task.auch_richtig'))+'</span>' : '')+
      '<span class="lbs" lang="bs">'+esc(bs)+'</span>'+
      (de ? '<span class="lde">'+esc(de)+'</span>' : '')+'</div>');
  };
  /* Ist gezeigt eine andere Form als die Hauptform haupt (" / " getrennt)? */
  const andereForm = (gezeigt, haupt)=> !String(haupt).split(' / ').includes(gezeigt);
  /* Der Hinweis "Fast richtig!" (24.10.2026, siehe fastRichtig()) fuer die
     Schreibaufgabe und den Lueckensatz - in Lektion, Wiederholen, Level-Test
     und Einstufung, die alle hier durchgehen. Einmal je Aufgabe. Er steht
     gelb wie "fast richtig" im Rueckmeldefeld, die Eingabe bleibt offen und
     bekommt den Fokus zurueck, der Text bleibt stehen. Kein done(), also
     nichts gezaehlt und kein Leben weg, kein Ton, keine Loesung, nichts
     gesprochen. Angesagt wird gleich und nicht erst nach WEITER_NACH: der
     Fokus wandert ja nicht zu Weiter, er bleibt im Feld.
     vertippt(r, antworten) sagt true, wenn check() hier aufhoeren soll.
     Das gilt auch, wenn derselbe Text innerhalb von DOPPELT_MS noch einmal
     kommt - Enter zweimal, Enter und gleich Pruefen. Danach ist derselbe
     Text der zweite Versuch: wer den Fehler nicht findet und noch einmal
     prueft, bekommt die Loesung und haengt nicht fest.
     Bei grosser Schrift oder offener Tastatur stand der Hinweis unter dem
     Rand, und er hat keinen Ton: wer ihn nicht sah, merkte nichts und
     verlor beim naechsten Pruefen ein Leben (Pruefer 24.10.2026). Deshalb
     holt scrollIntoView ihn ins Bild wie weiterBeiTipp() den Weiter-Knopf -
     'nearest' bewegt nichts, solange er zu sehen ist. Der Fokus bleibt im
     Feld, damit die Tastatur offen bleibt.
     Seit dem 27.10.2026 steht hier fuer alles derselbe Text, auch fuer eine
     andere Endung im Lueckensatz und fuer ein anderes echtes Wort (siehe
     fastRichtig()). Ein Hinweis je Aufgabe - nach dem einen zaehlt der
     naechste Versuch. */
  /* Seit dem 31.10.2026 auch fuer das Aspekt-Gegenstueck (partner): wer bei
     "bleiben" ostajati tippt, wo ostati gemeint ist, bekommt einmal
     task.partner ("Fast richtig! Gemeint ist das andere Verb des Paares.")
     statt eines Fehlers - derselbe Ablauf, nur der Text ist ein anderer.
     partner: die Antworten des Gegenstuecks wie bei matches(), sonst leer. */
  const tippHinweis = (inp)=>{
    let gezeigt = null;
    return (r, antworten, partner)=>{
      if(gezeigt){
        const doppelt = inp.value === gezeigt.text && Date.now() - gezeigt.zeit < DOPPELT_MS;
        if(doppelt) inp.focus();
        return doppelt;
      }
      if(r !== 'no') return false;
      const paar = !!partner && matches(inp.value, partner) !== 'no';
      if(!paar && !fastRichtig(inp.value, antworten)) return false;
      const hinweis = paar ? t('task.partner') : t('task.fast_richtig');
      gezeigt = {text: inp.value, zeit: Date.now()};
      const feld = $$('xFb');
      feld.textContent = hinweis;
      feld.className = 'feedback almost';
      inp.focus();
      try{ feld.scrollIntoView({block:'nearest', behavior: kachelnRuhig() ? 'auto' : 'smooth'}); }catch(e){}
      ansagen(esc(hinweis), 80);
      return true;
    };
  };
  // Geschuetztes Leerzeichen: das Zeichen bricht nie allein in eine neue Zeile
  const skipBtn = (text)=> opts.noSkip ? '' : '<button class="skip" id="xSkip">'+text+'\u00a0'+zeichen('weiter')+'</button>';
  const wireSkip = ()=>{ const b=$$('xSkip'); if(b) b.addEventListener('click',()=>done({ok:false, skipped:true})); };

  if(task.typ==='intro'){
    body.innerHTML = '<div class="kicker aufgabe mitmarke"><span class="rep new">'+t('task.neues_wort')+'</span></div><div class="de">'+esc(w.de)+'</div><div class="big'+(w.bs.length>16?' long':'')+'" lang="bs">'+esc(w.bs)+'</div>'+
      (canListen?'<button class="listen" id="xListen">'+mitSymbol('lautsprecher', t('task.hoeren'))+'</button>':'')+
      '<div class="row unten"><button class="btn know" id="xNext">'+t('task.weiter')+'</button></div>';
    if(canListen){ $$('xListen').addEventListener('click',()=>speak(w.bs)); spaeterSprechen(w.bs, BEIM_ERSCHEINEN); }
    $$('xNext').addEventListener('click',()=>done({ok:true, intro:true})); $$('xNext').focus();
    return;
  }
  if(task.typ==='mc'){
    body.innerHTML = kick(t('task.was_heisst'))+'<div class="prompt'+(w.de.length>18?' long':'')+'">'+esc(w.de)+'</div><div class="options" id="xOpts"></div><div class="feedback" id="xFb"></div>';
    renderChoice($$('xOpts'), shuffle([w, ...distractors(w, pool, 3)]), w.bs, o=>o.bs, ok=>{ fb(ok, w.bs); loesung(w.bs, w.de); spaeterSprechen(w.bs, nachAntwort(ok), ok); done({ok}); }, 'bs');
    return;
  }
  if(task.typ==='mcrev'){
    body.innerHTML = kick(t('task.was_bedeutet'))+'<div class="big'+(w.bs.length>16?' long':'')+'" lang="bs">'+esc(w.bs)+'</div><div class="options" id="xOpts"></div><div class="feedback" id="xFb"></div>';
    /* Hier steht das bosnische Wort gross da und die Bedeutung wird gesucht -
       ein Hoerknopf verraet also nichts. Kein Autoplay: erst lesen, dann auf
       Wunsch hoeren. Nach der Antwort spricht es von selbst, damit man die
       Aussprache mitnimmt, auch wenn man daneben lag.
       body.querySelector statt $(): die Kennung xListen gibt es in der
       Lektion UND im Test, und $() findet immer nur die erste im Dokument. */
    if(hoerbar(w.bs)) body.querySelector('.options').insertAdjacentHTML('beforebegin',
      '<button class="listen" data-hoer="1">'+mitSymbol('lautsprecher', t('task.hoeren'))+'</button>');
    const hoerKnopf = body.querySelector('[data-hoer]');
    if(hoerKnopf) hoerKnopf.addEventListener('click',()=>{ stilleBitte(); speak(w.bs); });
    renderChoice(body.querySelector('.options'), shuffle([w, ...distractors(w, pool, 3)]), w.de, o=>o.de, ok=>{ fb(ok, w.de, '', false); loesung(w.bs, w.de); spaeterSprechen(w.bs, nachAntwort(ok), ok); done({ok}); });
    return;
  }
  if(task.typ==='type'){
    body.innerHTML = kick(t('task.schreib'))+'<div class="prompt'+(w.de.length>18?' long':'')+'">'+esc(w.de)+'</div>'+
      '<input class="type-input" id="xIn" autocomplete="off" autocapitalize="off" spellcheck="false" placeholder="'+esc(t('task.schreib'))+'">'+
      '<div class="feedback" id="xFb"></div><div class="row"><button class="btn know" id="xCheck">'+t('task.pruefen')+'</button></div>';
    const inp=$$('xIn'); inp.focus(); let fin=false;
    const vertippt = tippHinweis(inp);
    const check=()=>{
      /* Traegt ein anderes Wort dieselbe Uebersetzung, ist es genauso
         richtig - der Bildschirm zeigt ja nur die Bedeutung. matches()
         trennt ohnehin bei " / ", deshalb genuegt es, die Antworten aus
         annehmbar() anzuhaengen. */
      if(fin) return;
      const auchOk = annehmbar(w).join(' / ');
      const r=matches(inp.value, auchOk);
      if(r==='leer'){ $$('xFb').textContent=t('task.tippe_wort'); $$('xFb').className='feedback no'; ansagen(esc(t('task.tippe_wort'))); return; }
      if(vertippt(r, auchOk, partnerAntworten(w))) return;   // ein Tippfehler oder das andere Verb des Paares: erst der Hinweis (24.10. / 31.10.2026)
      // Beantwortet: der Pruefen-Knopf hat nichts mehr zu tun und wuerde
      // nur neben dem Weiter-Knopf stehen. Ajdin am 18.09.2026.
      fin=true; inp.disabled=true;
      const pruefKnopf = $$('xCheck');
      if(pruefKnopf && pruefKnopf.parentElement) pruefKnopf.parentElement.hidden = true;
      const ok = r==='ok' || r==='almost';
      /* Falsch: die richtige Form, die dem Getippten am naechsten liegt, nicht
         immer w.bs (naechsteAntwort(), 17.11.2026). Ist es eine andere, sagt
         die Loesung darunter "Auch richtig:" zu w.bs. */
      const gezeigt = r==='ok' ? w.bs : r==='almost' ? gemeinteAntwort(inp.value, auchOk) : naechsteAntwort(inp.value, auchOk, w.bs);
      if(r==='ok') rueckmeldung('ok', 'task.richtig');
      else rueckmeldung(r==='almost' ? 'almost' : 'no', r==='almost' ? 'task.fast' : 'task.falsch', gezeigt);
      loesung(w.bs, w.de, andereForm(gezeigt, w.bs));
      sound(ok?'ok':'no'); spaeterSprechen(w.bs, nachAntwort(ok), ok); done({ok});
    };
    inp.addEventListener('keydown',e=>{ if(e.key==='Enter' && !e.repeat) check(); });   // festgehalten ist kein zweiter Versuch
    $$('xCheck').addEventListener('click',check);
    return;
  }
  if(task.typ==='listen'){
    body.innerHTML = kick(t('task.hoerfrage'))+'<button class="listen bigplay" id="xPlay" aria-label="'+t('task.abspielen')+'">'+symbol('lautsprecher')+'</button><div class="options" id="xOpts"></div><div class="feedback" id="xFb"></div>'+skipBtn(t('task.hoeren_skip'));
    $$('xPlay').addEventListener('click',()=>speak(w.bs)); spaeterSprechen(w.bs, BEIM_ERSCHEINEN);
    renderChoice($$('xOpts'), shuffle([w, ...distractors(w, pool, 3)]), w.bs, o=>o.bs, ok=>{ fb(ok, w.bs); loesung(w.bs, w.de); done({ok}); }, 'bs');
    wireSkip();
    return;
  }
  if(task.typ==='speak'){
    body.innerHTML = kick(t('task.sprechen'))+'<div class="big'+(w.bs.length>16?' long':'')+'" lang="bs">'+esc(w.bs)+'</div><div class="de">'+esc(w.de)+'</div>'+
      (canListen?'<button class="listen" id="xListen">'+mitSymbol('lautsprecher', t('task.vorsprechen'))+'</button>':'')+
      '<button class="mic" id="xMic" aria-label="'+t('task.mikro')+'"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/></svg></button>'+
      '<div class="heard" id="xHeard">'+t('task.mikro_tipp')+'</div><div class="feedback" id="xFb"></div>'+skipBtn(t('task.sprechen_skip'));
    if(canListen) $$('xListen').addEventListener('click',()=>speak(w.bs));
    const mic=$$('xMic'), heard=$$('xHeard'); let rec, listening=false, fin=false;
    // Laufende Erkennung abbrechen - beim Ueberspringen und ueber stilleBitte()
    const abhoeren = async ()=>{ const H = hoererPlugin(); try{ if(H) await H.stop(); else if(rec) rec.abort(); }catch(e){} };

    /* Ob in DIESER Aufgabe schon ein Versuch gescheitert ist: eine Meldung
       des Erkenners (No match, kein Netz, Didn't understand, Zeitgrenze)
       oder ein Ergebnis, das als falsch gewertet wurde. Dann kostet das
       Ueberspringen die Tagesaufgabe "ohne Fehler" nicht mehr - Ajdin am
       16.11.2026, nach einer Rueckmeldung ueber das Formular. Ueberspringen ohne
       jeden Versuch zaehlt wie bisher. Siehe Lx.skipNachFehler. */
    let gescheitert = false;
    const fehlerText = ()=> navigator.onLine ? 'task.mikro_fehler' : 'task.mikro_offline';
    /* Eine Meldung, wenn es nichts zu bewerten gibt - nur, solange die Aufgabe gilt. */
    const melde = (schluessel)=>{
      if(fin || meineAufgabe !== aufgabeMarke) return;
      gescheitert = true;
      heard.textContent = t(schluessel);
      ansagen(esc(heard.textContent));
    };
    /* Ein Ergebnis bewerten - egal, woher es kommt. Die Erkennung liefert
       mehrere Vorschläge; einer muss passen. */
    const bewerte = (liste)=>{
      // Zu spaet: die Aufgabe ist schon beantwortet, uebersprungen oder verlassen.
      if(fin || meineAufgabe !== aufgabeMarke) return;
      // Jede Schreibweise des Zielworts gilt: "Laku noc / Lahku noc" sind zwei,
      // bei "brat → braća" auch die Mehrzahl allein (passtGesprochen(), 16.11.2026)
      let treffer = false, erstes = '';
      for(const s of liste){
        if(!erstes) erstes = String(s).trim();
        if(passtGesprochen(s, w.bs)) treffer = true;
      }
      if(treffer){
        fin = true;
        heard.innerHTML = '<span style="color:var(--good-text)">'+t('task.gehoert_ok',{text:esc(erstes)})+'</span>';
        ansagen(esc(heard.textContent), WEITER_NACH + 80);   // wie bei den anderen Aufgaben (17.10.2026)
        sound('ok'); done({ok:true});
      } else if(!erstes){
        /* Die Erkennung hat nichts geliefert - geschwiegen, zu laut, Anruf,
           Mikrofon belegt. Vorher stand hier der Satz "Ich habe ‚‘
           verstanden" mit einem leeren Wort darin, dazu der Fehlerton. Der
           Nutzer bekam gesagt, er habe falsch gesprochen. */
        melde(fehlerText());
      } else {
        gescheitert = true;
        heard.textContent = t('task.gehoert_no',{text:erstes}); sound('no');
        ansagen(esc(heard.textContent));
      }
    };
    /* Vor dem Zuhoeren nur den Ton anhalten (16.11.2026, Analyse Punkt 15):
       Wer gleich nach "Vorsprechen" auf das Mikrofon tippte, nahm Emir mit
       auf. Die Aufnahme laeuft meist ueber WebAudio, und das richtet sich
       nicht sicher nach dem Audiofokus des Erkenners. NICHT stilleBitte():
       ohne true erhoeht es aufgabeMarke, und bewerte() verwuerfe danach
       jedes Ergebnis dieser Aufgabe. Das stumme Vorwaermen bleibt in Ruhe,
       wie in pufferSpielen(). */
    const tonAnhalten = ()=>{ waStopp(); if(!vorwaermen) try{ spieler.pause(); }catch(e){} };

    /* Sobald der Nutzer stoppt, ueberspringt oder die Aufgabe verlaesst,
       darf die Sprachschleife unten nicht die naechste Sprache anwerfen.
       Vorher lief das Mikrofon bis zu viermal weiter, auch auf der
       Levueluebersicht. Gefunden am 26.09.2026. */
    let stoppGewollt = false;
    /* Nur iPhone: mit welcher Sprache der naechste Tipp beginnt, siehe unten. */
    let sprachNr = 0;
    const abgebrochen = ()=> stoppGewollt || fin || meineAufgabe !== aufgabeMarke;
    /* Ein Tipp auf Android, siehe "---- Android: in welcher Sprache
       zugehoert wird" (16.11.2026). Gibt {erg} zurueck oder {art}, warum
       nichts kam. */
    const hoereAndroid = async (H)=>{
      const reihe = [sprechSprache || SPRECH_SPRACHEN[0]];
      const zweite = SPRECH_SPRACHEN.find(s => s !== reihe[0]);
      if(!sprechFehlt.has(zweite)) reihe.push(zweite);
      /* nochmal: die eine Wiederholung dieser Sprache ist verbraucht, gleich
         wofuer. fehltErst: ihr erster Start endete sofort mit "Sprache fehlt". */
      let art = null, nochmal = false, fehltErst = false;
      for(let i = 0; i < reihe.length; ){
        const sprache = reihe[i];
        let erg = null, text = '';
        art = null;
        const beginn = Date.now();
        try{ erg = await sprechStart(H, {maxResults:5, partialResults:false, popup:false, language:sprache}); }
        catch(e){ art = sprechFehlerArt(e); text = String((e && e.message) || e || ''); }
        if(erg && erg.zeitAus) return {art: 'zeit'};
        if(!art){
          if(erg && Array.isArray(erg.matches) && erg.matches.length){
            /* Nicht von bs-BA weg, wenn bs-BA schon geliefert hat: ein einzelnes
               "error from server" oder "Didn't understand" (darunter meldet das
               Plugin auch Androids Fehler 10 und 11) schickte sonst den Rest der
               Sitzung zu hr-HR, und hr-HR schreibt laut Analyse "Tko" und "Što"
               (Pruefung vom 16.11.2026). */
            if(sprache === SPRECH_SPRACHEN[0] || !sprechGeliefert.has(SPRECH_SPRACHEN[0])) sprechSprache = sprache;
            sprechGeliefert.add(sprache); sprechFehlt.delete(sprache);
            sprechStill = 0; sprechDienstAus = 0;
          }
          return {erg};
        }
        if(abgebrochen()) return {art: 'stopp'};   // gestoppt, uebersprungen, verlassen: keine weitere Sprache
        if(art === 'still' || (art === 'netz' && navigator.onLine)){
          if(art === 'still') sprechDienstAus = 0;   // der Erkenner laeuft, er hat nur nichts verstanden
          /* Zweimal in Folge mit bs-BA, und bs-BA hat in dieser Sitzung noch
             nichts geliefert: der naechste Tipp nimmt hr-HR. */
          if(sprache === SPRECH_SPRACHEN[0] && sprechSprache === null && !sprechGeliefert.has(sprache) && ++sprechStill >= 2){
            sprechSprache = SPRECH_SPRACHEN[1]; sprechStill = 0;
          }
          return {art};
        }
        if(art === 'netz') return {art};
        /* Hier bleiben "busy", "Client side error" und die Ablehnungen
           ("Didn't understand", "error from server", Unbekanntes). Ob es nach
           "Sprache fehlt" aussah: so ein Text und sofort, siehe SPRECH_SOFORT_MS. */
        const fehltJetzt = (art === 'client' || /Didn't understand/i.test(text)) && Date.now() - beginn < SPRECH_SOFORT_MS;
        if(!nochmal){
          nochmal = true; fehltErst = fehltJetzt;
          await new Promise(r => setTimeout(r, SPRECH_NOCHMAL_MS));
          if(abgebrochen()) return {art: 'stopp'};
          continue;   // dieselbe Sprache noch einmal, still im selben Tipp
        }
        if(art === 'belegt') return {art};
        /* Zweimal sofort "Sprache fehlt": fuer die Sitzung merken - es sei
           denn, diese Sprache hat schon etwas geliefert. Dann, und auch ohne
           Merkung, die andere Sprache im selben Tipp. */
        if(fehltErst && fehltJetzt && !sprechGeliefert.has(sprache)){
          sprechFehlt.add(sprache);
          const andere = SPRECH_SPRACHEN.find(s => s !== sprache);
          if(!sprechFehlt.has(andere) && (sprechSprache === null || sprechSprache === sprache)) sprechSprache = andere;
        }
        i++; nochmal = false; fehltErst = false;
      }
      /* Jede Sprache ist an Sprach- oder Dienstfehlern gescheitert. Mehrmals
         in Folge: Sprechaufgaben fallen ab der naechsten Lektion aus, wie bei
         abgelehntem Mikrofon - aber nur fuer diese Sitzung, ohne
         mikroAbsageMerken(). So bleibt die Tagesaufgabe "ohne Fehler"
         erreichbar. Seit dem 17.11.2026 auch in der laufenden Lektion, siehe
         sprechAufgabenRaus(). Eine Ablehnung, nach der die Wiederholung
         zuhoert, kommt hier nie an: der Tipp endet oben mit dem Ergebnis
         oder "No match", und ein Treffer wie ein "No match" setzt den Zaehler
         sogar zurueck. */
      if(++sprechDienstAus >= SPRECH_DIENST_GRENZE){ canSpeak = false; sprechAufgabenRaus(); }
      return {art};
    };
    mic.addEventListener('click', async ()=>{
      if(fin) return;
      const H = hoererPlugin();
      if(H){
        // Weg über das Plugin: Androids eigene Erkennung.
        if(listening){ stoppGewollt = true; try{ await H.stop(); }catch(e){} return; }
        try{
          let rechte = await H.checkPermissions();
          if(rechte.speechRecognition !== 'granted') rechte = await H.requestPermissions();
          if(rechte.speechRecognition !== 'granted'){
            /* canSpeak kam bisher allein aus H.available() - das sagt nur,
               dass ein Erkenner installiert ist, nicht dass die App ihn
               benutzen darf. Wer ablehnt, bekam trotzdem in jeder Lektion
               Sprechaufgaben, musste sie ueberspringen, und die Tagesaufgabe
               "ohne Fehler" verlangt Lx.skipped === 0 - sie war fuer ihn
               dauerhaft unerreichbar. Ab der naechsten Lektion faellt 'speak'
               jetzt aus dem Aufgabentopf. */
            canSpeak = false;
            mikroAbsageMerken(true);   // auch ueber den naechsten Start hinaus
            heard.textContent = t('task.mikro_blockiert');
            return;
          }
          listening = true; stoppGewollt = false;
          mic.classList.add('rec'); heard.textContent = t('task.hoert_zu');
          hoererAbbrechen = ()=>{ stoppGewollt = true; abhoeren(); };
          tonAnhalten();
          if(!sprechAufIOS()){
            const aus = await hoereAndroid(H);
            listening = false; mic.classList.remove('rec');
            if(aus.erg) bewerte(aus.erg.matches || []);
            else melde(aus.art === 'netz' ? 'task.mikro_offline' : fehlerText());
            return;
          }
          /* iPhone, unveraendert: ZmajSprache lehnt bs-BA sofort ab und nach dem
             Start nie mehr, die Schleife endet also bei hr-HR. */
          let erg = null;
          const sprachen = ['bs-BA','hr-HR','sr-RS', null];
          for(let nr = sprachNr; nr < sprachen.length; nr++){
            const sprache = sprachen[nr];
            try{
              erg = await H.start(Object.assign({maxResults:5, partialResults:false, popup:false},
                                                sprache ? {language:sprache} : {}));
              break;
            }catch(e){
              /* Frueher stand hier nur "diese Stimme fehlt auf dem Geraet".
                 Androids Erkenner wirft auf demselben Weg aber auch bei
                 "kein Treffer", Zeitueberlauf, belegtem Mikrofon und beim
                 Abbruch durch den Nutzer. Dann darf nicht die naechste
                 Sprache starten. */
              if(stoppGewollt || fin) break;
              /* Pruefbericht 1.3 (06.11.2026): Bei "kein Treffer" und Stille lief die
                 Schleife trotzdem weiter, bis zu dreimal, und auf dem Bildschirm
                 stand "Hoert zu ...". Jetzt ist hier Schluss und die Meldung kommt.
                 Ob ein Geraet ohne bs-BA genauso antwortet, ist am Handy noch nicht
                 geprueft. Deshalb bleibt der Rueckfall: Der naechste Tipp in dieser
                 Aufgabe nimmt die naechste Sprache. Andere Ablehnungen, darunter
                 Androids "Sprache fehlt", wandern wie bisher in einem Zug weiter. */
              if(/No match|No speech input/.test(String((e && e.message) || e))){
                sprachNr = (nr + 1) % sprachen.length;
                break;
              }
            }
          }
          listening = false; mic.classList.remove('rec');
          bewerte((erg && erg.matches) || []);
        }catch(e){
          listening = false; mic.classList.remove('rec');
          melde(fehlerText());
        }
        return;
      }
      // Weg über den Browser
      if(listening){ rec && rec.stop(); return; }
      rec=new SR(); rec.lang='hr-HR'; rec.interimResults=false; rec.maxAlternatives=3;
      /* Endet Chromes Erkennung ohne Ergebnis und ohne Fehler, stand bis zum
         16.11.2026 weiter "Hoert zu ..." da, obwohl nichts mehr zuhoerte
         (Analyse Punkt 16). Jetzt kommt die Meldung. */
      let geantwortet = false;
      rec.onstart=()=>{ listening=true; mic.classList.add('rec'); heard.textContent=t('task.hoert_zu'); hoererAbbrechen = abhoeren; };
      rec.onerror=(e)=>{
        geantwortet = true;
        if(e.error !== 'not-allowed') gescheitert = true;
        heard.textContent = e.error==='not-allowed' ? t('task.mikro_blockiert') : t(fehlerText());
      };
      rec.onend=()=>{ listening=false; mic.classList.remove('rec'); if(!geantwortet) melde('task.mikro_fehler'); };
      rec.onresult=(ev)=>{ geantwortet = true; bewerte([...ev.results[0]].map(r=>r.transcript)); };
      tonAnhalten();
      rec.start();
    });
    // Nicht wireSkip(): Ueberspringen muss hier auch die Erkennung beenden,
    // sonst kommt ihr Ergebnis Sekunden spaeter in die naechste Aufgabe.
    // nachFehler: siehe gescheitert oben (16.11.2026).
    const skipS = $$('xSkip');
    if(skipS) skipS.addEventListener('click', ()=>{ fin = true; abhoeren(); done({ok:false, skipped:true, nachFehler:gescheitert}); });
    return;
  }
  if(task.typ==='gap'){
    /* Die Fassung mit der gezogenen Zahl (25.10.2026): Satz, Loesung,
       Bedeutung und der gesprochene Satz passen damit zusammen. */
    const s = zahlFassung(task.s, task.v);
    /* Die Luecke ist ein Eingabefeld mitten im Satz. Seit dem 17.10.2026 hat
       es einen Namen, "Tippe das fehlende Wort ein" (WCAG 4.1.2) - vorher
       meldete ein Screenreader nur "Eingabefeld". Bosnisch sind nur die
       Satzteile davor und danach: laege das Feld selbst in lang="bs", hoerte
       man seinen Namen mit bosnischer Stimme. */
    const [vorLuecke, ...nachLuecke] = esc(s.text).split('___');
    const bsTeil = x => x ? '<span lang="bs">'+x+'</span>' : '';
    const lueckeHtml = '<input class="blank-input" id="xIn" autocomplete="off" autocapitalize="off" spellcheck="false" aria-label="'+esc(t('task.tippe_luecke'))+'">';
    body.innerHTML = kick(t('task.luecke'))+'<div class="sentence">'+bsTeil(vorLuecke)+(nachLuecke.length ? lueckeHtml+bsTeil(nachLuecke.join('___')) : '')+'</div>'+
      '<div class="translation">'+inZitat(esc(s.de))+'</div><div class="feedback" id="xFb"></div><div class="row"><button class="btn know" id="xCheck">'+t('task.pruefen')+'</button></div>';
    const inp=$$('xIn'); inp.focus(); let fin=false;
    const vertippt = tippHinweis(inp);
    const check=()=>{
      if(fin) return;
      /* "auch" am Lueckensatz (23.10.2026): weitere richtige Antworten, wie
         bei den Woertern. Bei "Moj ___ je pčelar." gelten auch stric und die
         Koseformen striko und adžo (WORTSCHATZ_KORREKTUREN.md). Gezeigt und
         gesprochen wird weiter s.answer. matches() trennt bei " / ".
         auch_var (12.11.2026, varianten.py): dieselbe Stelle mit dem anderen
         Wort in derselben Form - bei "Voda je u ___." auch boci, bei
         "Pijem ___." auch kafu. Bis dahin galt hier nicht einmal das "auch"
         des Wortes, nur flaši. */
      const antworten = [s.answer, ...(s.auch || []), ...(s.auch_var || [])].join(' / ');
      const r=matches(inp.value, antworten);
      if(r==='leer'){ $$('xFb').textContent=t('task.tippe_luecke'); $$('xFb').className='feedback no'; ansagen(esc(t('task.tippe_luecke'))); return; }
      if(vertippt(r, antworten)) return;   // wie in der Schreibaufgabe, dazu die andere Endung (27.10.2026)
      // Beantwortet: der Pruefen-Knopf hat nichts mehr zu tun und wuerde
      // nur neben dem Weiter-Knopf stehen. Ajdin am 18.09.2026.
      fin=true; inp.disabled=true;
      const pruefKnopf = $$('xCheck');
      if(pruefKnopf && pruefKnopf.parentElement) pruefKnopf.parentElement.hidden = true;
      const ok = r==='ok' || r==='almost';
      // Wie in der Schreibaufgabe (17.11.2026): die naechste richtige Form.
      const gezeigt = r==='ok' ? s.answer : r==='almost' ? gemeinteAntwort(inp.value, antworten) : naechsteAntwort(inp.value, antworten, s.answer);
      if(r==='ok') rueckmeldung('ok', 'task.richtig');
      else rueckmeldung(r==='almost' ? 'almost' : 'no', r==='almost' ? 'task.fast' : 'task.falsch', gezeigt);
      loesung(s.text.replace('___', s.answer), s.de, andereForm(gezeigt, s.answer));
      sound(ok?'ok':'no');
      /* Erst jetzt den FERTIGEN Satz sprechen - vorher waere die Loesung
         verraten. Gehoert wird der Satz mit eingesetztem Wort, nicht der
         mit der Luecke. */
      const gesagt = lueckeText(s);    // derselbe Text, den woerterVorladen() dekodiert hat (26.10.2026)
      if(gesagt) spaeterSprechen(gesagt, nachAntwort(ok), ok);
      done({ok});
    };
    inp.addEventListener('keydown',e=>{ if(e.key==='Enter' && !e.repeat) check(); });   // festgehalten ist kein zweiter Versuch
    $$('xCheck').addEventListener('click',check);
    return;
  }
  if(task.typ==='kacheln'){
    /* Einen Satz aus Kacheln legen - Wunsch einer Testerin vom 13.10.2026, siehe
       kachelnFuerLektion(). Oben die Bedeutung, darunter die Zeile, in die
       man legt, darunter der Vorrat. Antippen im Vorrat legt die Kachel ans
       Ende der Zeile, Antippen in der Zeile legt sie zurueck an ihren Platz.
       Gemischt wird erst hier und nicht beim Bauen der Lektion: eine falsche
       Antwort kommt als {...task, retry:true} ans Ende und soll dann nicht
       wieder genauso daliegen. */
    /* Mit der gezogenen Zahl (25.10.2026): Kacheln, falsche Kacheln
       (kachelAblenker), richtige Reihenfolgen und Ton von dieser Fassung. */
    const s = zahlFassung(task.s, task.v);
    const richtige = [s.bs, ...(s.auch || [])].map(kachelNorm);
    const teile = satzKacheln(s.bs);
    const bank = teile.map(x => ({x, satz:true}))
      .concat(kachelAblenker(s, teile.length >= 5 ? 3 : 2).map(x => ({x, satz:false})));
    /* Nicht schon richtig herum hinlegen: bei zwei Kacheln stuenden sie sonst
       jedes zweite Mal in der Reihenfolge des Satzes da. */
    for(let n = 0; n < 6; n++){
      shuffle(bank);
      if(bank.filter(k => k.satz).map(k => k.x).join(' ') !== teile.join(' ')) break;
    }
    /* Zeile und Vorrat sind benannte Gruppen (17.10.2026): "Dein Satz" und
       "Woerter". Vorher hiess die Zeile wie der Hinweis, und der Vorrat hatte
       gar keinen Namen - mit Screenreader war nicht zu hoeren, ob eine Kachel
       schon liegt oder noch wartet. Der Hinweis steht weiter in der leeren
       Zeile (data-leer) und wird dort mit vorgelesen. Die Gruppen selbst
       tragen kein lang="bs": ihr Name ist in der Sprache der App. */
    body.innerHTML = kick(t('task.kacheln'))+'<div class="prompt'+(s.de.length>18?' long':'')+'">'+esc(s.de)+'</div>'+
      '<div class="kachelzeile" id="xZeile" role="group" aria-label="'+esc(t('task.kacheln_zeile'))+'" data-leer="'+esc(t('task.kacheln_hinweis'))+'"></div>'+
      '<div class="options waagrecht kachelbank" id="xBank" role="group" aria-label="'+esc(t('task.kacheln_vorrat'))+'"></div>'+
      '<div class="feedback" id="xFb"></div><div class="row"><button class="btn know" id="xCheck" disabled>'+t('task.pruefen')+'</button></div>'+
      skipBtn(t('task.kacheln_skip'));
    const zeile = $$('xZeile'), vorrat = $$('xBank'), pruef = $$('xCheck');
    let fin = false;
    const gelegt = () => [...zeile.querySelectorAll('.kachel')];
    /* Nach jedem Legen und Zuruecklegen wird angesagt, wie der Satz jetzt
       dasteht - "Dein Satz: Ja sam" (17.10.2026). Ist die Zeile leer, der
       Hinweis, der dann auch auf dem Bildschirm steht. Die Kacheln sind
       bosnisch und kommen als lang="bs" mit. */
    const satzAnsagen = () => {
      const woerter = gelegt().map(k => k.textContent).join(' ');
      ansagen(esc(t('task.kacheln_zeile')) + ': '
        + (woerter ? '<span lang="bs">' + esc(woerter) + '</span>' : esc(t('task.kacheln_hinweis'))));
    };
    const legen = (b) => {
      if(fin) return;
      // Mit der Tastatur bleibt man in den Kacheln, statt nach dem Antippen
      // im Nichts zu stehen. Am Handy aendert das nichts Sichtbares.
      const hatteFokus = document.activeElement === b;
      /* Gleiten statt springen (Ajdin, 14.10.2026: "die kacheln
         teleportieren sich"). Vor dem Umhaengen merken, wo jede Kachel
         steht, danach jede von dort an ihren neuen Platz ziehen - die
         angetippte und alle, die dabei nachruecken oder mit der Zeile nach
         unten wandern. Mitten im Flug gemessen, startet ein zweiter Tipp dort,
         wo die Kachel gerade ist. */
      const vorher = new Map([...body.querySelectorAll('.kachel')].map(k => [k, k.getBoundingClientRect()]));
      let weiter = null;
      if(b.parentElement === vorrat){
        /* Ein unsichtbarer Platzhalter haelt die Stelle frei. Ohne ihn
           rueckten die anderen Kacheln nach, und der naechste Tipp traefe
           eine andere als die, auf die man gezielt hat. */
        const platz = b.cloneNode(true);
        platz.classList.add('platz'); platz.disabled = true; platz.tabIndex = -1;
        platz.setAttribute('aria-hidden', 'true');
        vorrat.replaceChild(platz, b);
        zeile.appendChild(b);
        /* Der Fokus geht zur naechsten Kachel rechts von der Luecke, gibt es
           keine mehr, zur naechsten links davon, und erst bei leerem Vorrat
           auf Pruefen (17.10.2026). Bis dahin sprang er immer auf die erste
           Kachel im Vorrat - wer mit Tastatur oder Screenreader von vorn nach
           hinten legt, stand nach jedem Legen wieder am Anfang. */
        const alle = [...vorrat.children], stelle = alle.indexOf(platz);
        const frei = k => !k.classList.contains('platz');
        weiter = alle.slice(stelle + 1).find(frei) || alle.slice(0, stelle).reverse().find(frei) || pruef;
      } else {
        const stelle = gelegt().indexOf(b);
        const platz = vorrat.querySelector('.platz[data-nr="'+b.dataset.nr+'"]');
        if(platz) vorrat.replaceChild(b, platz); else vorrat.appendChild(b);
        const rest = gelegt();
        weiter = rest[stelle] || rest[rest.length - 1] || b;
      }
      // Ohne Bewegung wird auch ein Gleiten von vorhin abgebrochen: die
      // Kachel steht dann gleich an ihrem Platz.
      const ruhig = kachelnRuhig();
      // translate rechnet in Punkten der Seite, siehe rectFaktor() (am Handy f = 1)
      const f = rectFaktor() / GROSS;
      vorher.forEach((r, k) => {
        if(!k.isConnected || !k.animate) return;
        if(k.getAnimations) k.getAnimations().forEach(a => a.cancel());
        if(ruhig) return;
        const n = k.getBoundingClientRect(), dx = (r.left - n.left) * f, dy = (r.top - n.top) * f;
        if(Math.abs(dx) < 1 && Math.abs(dy) < 1) return;
        k.animate([{transform:'translate('+dx+'px,'+dy+'px)'}, {transform:'none'}],
          {duration: k === b ? 260 : 200, easing:'cubic-bezier(.2,.8,.2,1)'});
      });
      pruef.disabled = !gelegt().length;
      if(hatteFokus && weiter && !weiter.disabled) try{ weiter.focus({preventScroll:true}); }catch(e){}
      satzAnsagen();
    };
    bank.forEach((k, nr) => {
      const b = document.createElement('button');
      b.type = 'button'; b.className = 'opt kachel'; b.textContent = k.x; b.dataset.nr = nr;
      b.lang = 'bs';   // die Kachel ist ein bosnisches Wort (17.10.2026); der Platzhalter erbt es beim Klonen
      b.addEventListener('click', () => legen(b));
      vorrat.appendChild(b);
    });
    const check = () => {
      if(fin || !gelegt().length) return;
      fin = true;
      const ok = richtige.includes(kachelNorm(gelegt().map(b => b.textContent).join(' ')));
      body.querySelectorAll('.kachel').forEach(b => { b.disabled = true; });
      zeile.classList.add(ok ? 'ok' : 'no');
      // Beantwortet: der Pruefen-Knopf hat nichts mehr zu tun (wie bei der Luecke).
      if(pruef.parentElement) pruef.parentElement.hidden = true;
      fb(ok, s.bs);
      loesung(s.bs, s.de);
      sound(ok?'ok':'no');
      // Erst jetzt vorlesen - vorher waere die Loesung verraten.
      if(hoerbar(s.bs)) spaeterSprechen(s.bs, nachAntwort(ok), ok);
      done({ok});
    };
    pruef.addEventListener('click', check);
    const skipK = $$('xSkip');
    if(skipK) skipK.addEventListener('click', () => { if(fin) return; fin = true; done({ok:false, skipped:true}); });
    return;
  }
  if(task.typ==='gram'){
    const g=task.g;
    body.innerHTML = kick(t('task.grammatik'))+gramFrageHtml(g.frage)+'<div class="options'+(g.optionen.some(o=>o.length>22)?' one':'')+'" id="xOpts"></div><div class="feedback" id="xFb"></div><div class="ex-tipp" id="xTipp"></div>';
    // Nach der Antwort die richtige Form sprechen, wenn es sie als Aufnahme
    // gibt - bei „imaš“ gegen „ima“ entscheidet die Aussprache mit.
    // lang="bs" nur an bosnischen Antworten, auch in der Rueckmeldung (17.10.2026).
    // Vorgelesen auch nur dann: "weiblich (ona)" sprach sonst die bosnische
    // Stimme der Sprachausgabe - ein deutsches Wort mit bosnischer Aussprache.
    const bsRichtig = gramAntwortBosnisch(g.richtig);
    renderChoice($$('xOpts'), shuffle(g.optionen.map(o=>({k:o}))), g.richtig, o=>o.k, ok=>{ fb(ok, g.richtig, '', bsRichtig ? undefined : false); const gl=gramLoesung(g); if(gl) loesung(gl[0], gl[1]); if(!ok && g.tipp) $$('xTipp').textContent=g.tipp; if(bsRichtig && vorlesbar(g.richtig)) spaeterSprechen(g.richtig, nachAntwort(ok), ok); done({ok, slow:!ok && !!g.tipp}); },
      o => gramAntwortBosnisch(o) ? 'bs' : '');
    return;
  }
}

var teileDa = (teileDa || 0) + 1;   // dieser Teil ist ganz gelaufen, siehe teileDa oben
