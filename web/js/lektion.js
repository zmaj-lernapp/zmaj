/* =================== LEKTION =================== */
let Lx = null;
/* ---- Lueckensaetze nur mit Woertern, die schon dran waren ----
   Bis zum 06.10.2026 nahm buildLesson() zwei beliebige Saetze des Levels.
   In der ersten Lektion eines Levels fragte die Luecke dann meist nach
   einem Wort, das noch nie zu sehen war - in Level 1 bei drei von vier
   Luecken, ueber alle Level bei fast zwei von dreien -, und jeder Fehler
   kostet ein Leben. Gefunden bei der Pruefung am 06.10.2026.
   Jetzt kommt ein Satz nur dran, wenn seine Antwort in einer Vokabel
   steht, die schon gewusst ist oder in dieser Lektion neu vorgestellt
   wird: als ganze Vokabel ("kiša") oder als Teil einer Wendung, die genau
   so im fertigen Satz steht ("Dobar ___" mit "Dobar dan"). Verglichen wird
   wie in matches(): Gross/klein, Satzzeichen und Haekchen zaehlen nicht
   ("fast richtig" kostet dort kein Leben), jede Variante hinter " / " gilt,
   und Zahlen gelten ueber ihren Wert - wer "dva" kennt, darf bei "Dvije"
   auch "dva" schreiben. Gebeugte Formen wie "kruške" zu "kruška" zaehlen
   nicht als gesehen. Reicht es im Level nicht fuer LEKTION_LUECKEN Saetze,
   kommen welche aus frueheren, bestandenen Leveln dazu, sonst eben
   weniger Luecken. Der Level-Test fragt keine Luecken, die Einstufung
   kostet keine Leben, und der Fehlertopf holt nur Saetze zurueck, die
   schon dran waren - dort bleibt alles, wie es ist. */
const lueckeTeile = s => ' ' + strip(String(s || '')).split(/[^a-z0-9]+/).filter(Boolean).join(' ') + ' ';
/* zahlWert() ueber alle Vokabeln dauert so lange, dass man es beim Start
   jeder Lektion merken wuerde. Also nur, wenn eine Antwort eine Zahl ist,
   und je Form nur einmal. */
const _zahlJeForm = new Map();
const zahlDerForm = f => { if(!_zahlJeForm.has(f)) _zahlJeForm.set(f, zahlWert(f)); return _zahlJeForm.get(f); };
function gesehenFormen(ids){
  const formen = [];
  CATEGORIES.forEach(c => c.words.forEach(w => {
    if(!ids.has(w.id)) return;
    [w.bs, ...(w.auch || [])].forEach(x => String(x).split(' / ').forEach(f => {
      const teile = lueckeTeile(f);
      if(teile.trim()) formen.push(teile);
    }));
  }));
  return {formen, zahlen: null};
}
function lueckeGesehen(s, g){
  return String(s.answer).split(' / ').some(a => {
    const z = zahlWert(a);
    if(z !== null){
      if(!g.zahlen) g.zahlen = new Set(g.formen.map(zahlDerForm));
      if(g.zahlen.has(z)) return true;
    }
    const kern = lueckeTeile(a), satz = lueckeTeile(s.text.replace('___', a));
    return !!kern.trim() && g.formen.some(f => f.includes(kern) && satz.includes(f));
  });
}
function lueckenFuerLektion(ids){
  if(imZa()) return [];     // Beim Zahnarzt: keine Luecken, und keine aus dem Lernpfad
  const g = gesehenFormen(ids), schon = new Set(), out = [];
  const nimm = liste => shuffle(liste.filter(s => lueckeGesehen(s, g))).forEach(s => {
    const k = s.text + '|' + s.answer;   // derselbe Satz steht in manchen Leveln doppelt
    if(out.length < LEKTION_LUECKEN && !schon.has(k)){ schon.add(k); out.push(s); }
  });
  nimm(curSentences());
  if(out.length < LEKTION_LUECKEN){
    const frueher = new Set(CATEGORIES.slice(0, catIdx).filter(x => passed.has(x.id)).map(x => x.id));
    nimm(SENTENCES.filter(s => frueher.has(s.kat)));
  }
  return out;
}
/* ---- Saetze aus Kacheln bauen (13.10.2026) ----
   Eine Testerin (Muttersprachlerin) am 13.10.2026: neue Woerter kommen
   und gehen und bleiben nicht haengen. Sie wollte wie bei Duolingo ganze
   Saetze aus Wort-Kacheln legen statt nur eine Luecke zu fuellen, ab Level 1
   und mit den Woertern, die gerade dran waren. Ajdin dazu: mehrere
   Reihenfolgen duerfen richtig sein (SATZBAU "auch"), und ein Satz kommt
   erst, wenn alle seine Woerter schon da waren.
   Die Kacheln sind die Woerter von bs, an Leerzeichen getrennt, ohne
   Satzzeichen am Rand - genau wie satz_kacheln() in inhalt.py. Beide
   muessen gleich zerlegen, sonst prueft der Test etwas anderes, als die
   App zeigt.
   Intern heisst die Aufgabe 'kacheln', nicht 'satzbau': ein Level mit der
   id 'satzbau' gibt es schon. Im Level-Test und in der Einstufung kommt
   sie bewusst nicht vor - dort gibt es auch keine Luecken. */
const KACHEL_RAND = /^[.,!?¿¡:;"„“”«»…()]+|[.,!?¿¡:;"„“”«»…()]+$/g;
const kachelRoh = s => String(s || '').split(/\s+/).map(x => x.replace(KACHEL_RAND, '')).filter(Boolean);
const kachelNorm = s => kachelRoh(s).map(x => x.toLowerCase()).join(' ');
/* Endet das Wort einen Satz, faengt mit dem naechsten ein neuer an. */
const kachelSatzEnde = roh => /[.!?…]["“”»)]*$/.test(roh);
/* Nie als falsche Kachel: Woerter, die sich zu aehnlich sehen oder fast
   ueberall grammatisch hineinpassen. Mit "ti" neben "Kako si" waere auch
   "Kako si ti" ein richtiger Satz - die App wertete ihn aber als falsch,
   und das kostet ein Leben. */
const KACHEL_VERWECHSELBAR = new Set(('si ste ti vi te vas tvoj tvoja tvoje vaš vaša vaše izvini izvinite ' +
  'ja mi on ona ono oni je su sam smo li se me mu joj ga ih nam vam im da ne').split(' '));
/* Kacheln stehen klein da, sonst verraet der Grossbuchstabe das erste Wort.
   Namen bleiben gross: die festen hier und jedes Wort, das irgendwo mitten
   im Satz gross steht ("Idem u Mostar", "Hvala Bogu"). Die Pronomen aus
   KACHEL_VERWECHSELBAR zaehlen dabei nicht - "molim Vas" ist Hoeflichkeit,
   kein Name. Gesammelt wird einmal je Inhalt, ladeDaten() setzt zurueck.
   Laender, Staedte und Nationalitaeten stehen oft nur allein im Wortschatz
   ("Švicarska") und am Satzanfang ("Švicarska je mala država."), nie
   mitten im Satz - die Kachel stand deshalb klein da, als Ablenker auch
   "njemačka" oder "tuzla". Jedes grosse Wort aus dem Wortschatz als Namen
   zu nehmen geht nicht: "Hvala", "Kako", "Gdje", "Šta" stehen dort genauso
   gross, weil sie allein stehen, und blieben dann am Satzanfang gross - in
   rund 60 Saetzen verriete das das erste Wort. Deshalb nur die Level, in
   denen ein grosses Wort immer ein Name ist, und die Feste von Hand.
   Gefunden im Review am 14.10.2026. */
const KACHEL_NAMEN_LEVEL = new Set(['einkauf_orte', 'laender', 'nationalitaeten']);
let _kachelNamen = null;
function kachelNamen(){
  if(_kachelNamen) return _kachelNamen;
  const namen = new Set(['amina', 'ajdin', 'emir', 'lejla', 'sarajevo', 'mostar', 'bosna',
    'bajram', 'kurban-bajram', 'ramazan', 'božić', 'uskrs']);
  const sammle = satz => {
    let anfang = true;
    String(satz || '').split(/\s+/).forEach(roh => {
      const wort = roh.replace(KACHEL_RAND, '');
      if(!wort) return;
      const klein = wort.toLowerCase();
      if(!anfang && /^\p{Lu}/u.test(wort) && !KACHEL_VERWECHSELBAR.has(klein)) namen.add(klein);
      anfang = kachelSatzEnde(roh);
    });
  };
  SATZBAU.forEach(s => sammle(s.bs));
  CATEGORIES.forEach(c => c.words.forEach(w => String(w.bs).split(' / ').forEach(sammle)));
  CATEGORIES.filter(c => KACHEL_NAMEN_LEVEL.has(c.id)).forEach(c => c.words.forEach(w => kachelFormen(w).forEach(f => {
    const teile = kachelRoh(f);
    const klein = teile.length === 1 ? teile[0].toLowerCase() : '';
    if(klein && /^\p{Lu}/u.test(teile[0]) && !KACHEL_VERWECHSELBAR.has(klein)) namen.add(klein);
  })));
  return (_kachelNamen = namen);
}
/* Die Kacheln eines Satzes, wie sie dastehen: das erste Wort klein, ausser
   es ist ein Name, alles andere wie geschrieben. Auch das erste Wort nach
   einem Punkt oder Fragezeichen mitten im Satz ist klein - es wuerde sonst
   genauso verraten, wo der zweite Satz anfaengt. */
function satzKacheln(bs){
  const out = [];
  let anfang = true;
  String(bs || '').split(/\s+/).forEach(roh => {
    const wort = roh.replace(KACHEL_RAND, '');
    if(!wort) return;
    out.push(anfang && !kachelNamen().has(wort.toLowerCase()) ? wort.toLowerCase() : wort);
    anfang = kachelSatzEnde(roh);
  });
  return out;
}
/* Jede Schreibweise eines Wortes einzeln: bs und auch, Varianten hinter " / " getrennt. */
const kachelFormen = w => [w.bs, ...(w.auch || [])].flatMap(x => String(x).split(' / ')).map(x => x.trim()).filter(Boolean);
/* Falsche Kacheln dazu: einzelne Woerter aus den Leveln bis zu dem des
   Satzes. Nie eine, die im Satz oder in einer erlaubten Variante steht, nie
   eine andere Form desselben Wortes (wer "kahva" legen soll, bekommt kein
   "kafa" daneben - "Hallo" ist Merhaba UND Zdravo), und nichts aus
   KACHEL_VERWECHSELBAR. Reicht der Vorrat nicht, sind es eben weniger.
   Was das Review am 14.10.2026 dazu noch fand - jedes davon machte aus
   einer richtigen Uebersetzung einen Fehler, der ein Leben kostet:
   - Andere Personen desselben Verbs: neben "Imate li ajvar?" lag "imaš",
     neben "Kada ćeš doći?" lag "ćete", und "Do you have ajvar?" ist beides.
     Gesperrt ist jedes Wort, das nach KACHEL_ENDUNG denselben Stamm hat wie
     eine Kachel des Satzes. Das trifft auch ein paar unschuldige Woerter
     ("samo" neben "sam", "dan" neben "danas") - nachgemessen fallen ueber
     alle Saetze gut 100 von 243.000 moeglichen Ablenkern weg.
   - s/sa und k/ka sind dieselbe Praeposition, die App lehrt beide.
   - Die Grundform einer gebeugten Kachel und ihre anderen Formen: neben
     "Uzet ću pogaču." lag "somun", das beim selben Wort steht.
   - s.ohne: was die Autoren fuer diesen Satz von Hand sperren, meist
     Synonyme, die kein Wort miteinander teilen (ćao neben Merhaba). */
const KACHEL_ENDUNG = /(ate|ete|ite|amo|emo|imo|aju|ju|as|es|is|am|em|im)$/;
const kachelStamm = x => strip(String(x)).replace(KACHEL_ENDUNG, '');
const KACHEL_PAARE = [['s', 'sa'], ['k', 'ka']];
function kachelAblenker(s, anzahl){
  const bis = CATEGORIES.findIndex(c => c.id === s.kat);
  const eigene = new Set([s.bs, ...(s.auch || [])].flatMap(x => kachelRoh(x).map(k => k.toLowerCase())));
  const grund = new Set((s.grund || []).map(kachelNorm));
  const gesperrt = new Set([...eigene, ...KACHEL_VERWECHSELBAR, ...(s.ohne || []).map(kachelNorm)]);
  KACHEL_PAARE.forEach(p => { if(p.some(x => eigene.has(x))) p.forEach(x => gesperrt.add(x)); });
  CATEGORIES.forEach(c => c.words.forEach(w => {
    const formen = kachelFormen(w).map(kachelNorm);
    if(formen.some(f => eigene.has(f) || grund.has(f))) formen.forEach(f => gesperrt.add(f));
  }));
  const staemme = new Set([...eigene].map(kachelStamm).filter(Boolean));
  const vorrat = new Map();
  CATEGORIES.slice(0, (bis < 0 ? catIdx : bis) + 1).forEach(c => c.words.forEach(w => kachelFormen(w).forEach(f => {
    const teile = kachelRoh(f);
    if(teile.length !== 1) return;
    const klein = teile[0].toLowerCase();
    if(gesperrt.has(klein) || vorrat.has(klein) || !/^\p{L}+(-\p{L}+)*$/u.test(klein)) return;
    if(staemme.has(kachelStamm(klein))) return;
    vorrat.set(klein, kachelNamen().has(klein) ? teile[0] : klein);
  })));
  return shuffle([...vorrat.values()]).slice(0, anzahl);
}
/* Welche Saetze in diese Lektion kommen. Zuerst die des Levels, bei denen
   jede Kachel, die zu einem Wort DIESES Levels gehoert, schon gesehen ist
   (gewusst oder in dieser Lektion neu vorgestellt, wie bei den Luecken).
   Woerter aus frueheren Leveln gelten als begegnet. Verglichen wird wie in
   lueckeTeile(): ohne Haekchen, Gross/klein egal. Gebeugte Formen
   ("kahvu") kennt die App nicht als Form eines Wortes - die stehen nur in
   vokabeln.py unter "formen" und werden dort geprueft. Reicht es nicht,
   kommen Saetze aus frueheren, bestandenen Leveln dazu.
   belegt: fertige Saetze der Luecken dieser Lektion (lueckeFertig()). Ein
   Satz, der dort schon steht, kommt nicht noch einmal als Kacheln - sonst
   zeigt die eine Aufgabe die Loesung der anderen samt Bedeutung, und in
   gut jeder dritten Lektion war eine der Satzaufgaben nur Abschreiben
   ("Drago ___ je." und "Drago mi je."). Gefunden im Review am 14.10.2026. */
const lueckeFertig = s => String(s.answer).split(' / ').map(a => kachelNorm(String(s.text).replace('___', a.trim())));
function kachelnFuerLektion(ids, belegt){
  if(imZa()) return [];     // Beim Zahnarzt: keine Kacheln, und keine aus dem Lernpfad
  const c = cur();
  const teileVon = w => kachelFormen(w).flatMap(f => lueckeTeile(f).trim().split(' ')).filter(Boolean);
  const hier = new Set(c.words.flatMap(teileVon));
  const vorher = new Set(CATEGORIES.slice(0, catIdx).flatMap(k => k.words.flatMap(teileVon)));
  const gesehen = new Set(gesehenFormen(ids).formen.flatMap(f => f.trim().split(' ')));
  /* grund: Grundformen gebeugter Kacheln ("kahvu" -> "kahva"). Auch sie
     muessen in dieser Lektion schon dran gewesen sein, sonst kaeme der Satz
     vor seinem Wort. */
  const bereit = s => kachelRoh(s.bs).concat(s.grund || []).every(k => lueckeTeile(k).trim().split(' ').filter(Boolean)
    .every(x => !hier.has(x) || gesehen.has(x) || vorher.has(x)));
  const schon = new Set(), out = [];
  const nimm = liste => shuffle(liste.slice()).forEach(s => {
    const k = kachelNorm(s.bs);
    if(belegt && [s.bs, ...(s.auch || [])].some(x => belegt.has(kachelNorm(x)))) return;
    if(out.length < LEKTION_KACHELN && !schon.has(k)){ schon.add(k); out.push(s); }
  });
  nimm(SATZBAU.filter(s => s.kat === c.id && bereit(s)));
  if(out.length < LEKTION_KACHELN){
    const frueher = new Set(CATEGORIES.slice(0, catIdx).filter(x => passed.has(x.id)).map(x => x.id));
    nimm(SATZBAU.filter(s => frueher.has(s.kat)));
  }
  return out;
}
/* Die Aufgabenart eines Wortes reihum, ab einer zufaelligen Stelle;
   Schreiben nur bei Woertern, die sich tippen lassen. Seit 19.10.2026 ein
   eigenes Stueck: die Markiert-Runde (sternRunde) waehlt genauso. */
function artenReihum(types){
  let ti = Math.floor(Math.random()*types.length);
  return w => { for(let k=0;k<types.length;k++){ const t=types[(ti+k)%types.length]; if(t==='type' && !typable(w)) continue; ti=(ti+k+1)%types.length; return t; } return 'mc'; };
}
function buildLesson(){
  const c = cur();
  /* Ajdin am 26.10.2026: "bei der zahlen sektion am besten die zahlen in
     reihenfolge lernen sowie wochentage und wo es noch passt". Ein Level
     mit "reihenfolge" (vokabeln.py: zahlen, wochentage, monate,
     mengen, seit 26.10.2026 abends auch konjugation, zukunft und routine,
     seit 27.10.2026 vergangenheit, modal und adjektive - von Ajdin auf
     Rueckfrage zu diesem Wunsch ausgewaehlt)
     stellt seine neuen Woerter in der Reihenfolge der Liste vor -
     jedan bis deset und dann nula (Ajdin: Zahlen fangen mit jedan an),
     ja sam, ti si ... oni su, bio sam, bio si, bio je, bila je, bili smo,
     morati, moram, moraš, moramo, velik, veći, najveći,
     ponedjeljak bis nedjelja, jedan brat vor dva
     brata vor pet braće -, die Einfuehrungskarten (intros unten) also
     auch. Wer schon mitten im Level ist, bekommt die
     noch fehlenden ebenso der Reihe nach, und ein Wort, das in einer
     Lektion nicht richtig beantwortet wurde, ist noch nicht gewusst und
     steht in der naechsten wieder vorn. Gemischt bleiben die Aufgaben
     (shuffle(tasks)), die Wiederholung bekannter Woerter, der Level-Test,
     die Einstufung, Fehler-Topf und Markiert. Gespeichert wird nichts
     Neues: es haengt nur an known, wie bisher. */
  const offen = c.words.filter(w=>!known.has(w.id));
  let unknown = c.reihenfolge === true ? offen : shuffle(offen);
  /* Teil-Reihen (26.10.2026), Ajdin: "und auch reihenfolge
     beruecksichtigen wo es noch sinn ergibt geh durch die app durch".
     In einem sonst gemischten Level steht eine kurze Reihe ("reihe" in
     vokabeln.py: die Tageszeiten in zeit, die Jahreszeiten in wetter,
     seit 27.10.2026 die Gruesse nach Tageszeit in basics: Dobro jutro,
     Dobar dan, Dobro veče, Laku noć).
     Regel: Die uebrigen Woerter werden gemischt gezogen wie bisher. Die
     noch offenen Reihen-Woerter bilden einen Block in ihrer Folge und
     nehmen den Platz des ersten Reihen-Worts ein, das beim Mischen
     gezogen wurde. Wann die Reihe drankommt, bleibt so zufaellig wie
     vorher, nur kommt sie geschlossen und geordnet. Ist sie schon
     angefangen (ein Reihen-Wort gewusst), kommt der Rest ganz vorn: eine
     Reihe, die an der Lektionsgrenze abgeschnitten wurde, geht in der
     naechsten Lektion gleich weiter. Nichts Neues gespeichert. */
  const reihe = c.reihenfolge !== true && Array.isArray(c.reihe) ? c.reihe : [];
  const inReihe = w => reihe.indexOf(w.bs) >= 0;
  const block = offen.filter(inReihe).sort((a, b) => reihe.indexOf(a.bs) - reihe.indexOf(b.bs));
  if(block.length){
    const stelle = c.words.some(w => inReihe(w) && known.has(w.id)) ? 0 : unknown.findIndex(inReihe);
    unknown = unknown.filter(w => !inReihe(w));
    unknown.splice(stelle, 0, ...block);
  }
  // Die Wiederholung bleibt gemischt, auch bei "reihenfolge" - sonst kaemen
  // in zahlen nur jedan, dva ... dran und spaetere Zahlen nie wieder
  // (26.10.2026, tests_e2e/test_reihenfolge.py: test_wiederholung_bleibt_gemischt).
  const knownW = shuffle(c.words.filter(w=>known.has(w.id)));
  let nNew = Math.min(LEKTION_NEU_MAX, unknown.length);
  let nRev = Math.min(LEKTION_WOERTER - nNew, knownW.length);
  if(nRev < LEKTION_WOERTER - nNew) nNew = Math.min(unknown.length, Math.max(nNew, Math.min(8, LEKTION_WOERTER - nRev)));
  /* Faellige Woerter aus der Lernkartei (Ajdin am 28.10.2026): bis zu
     KARTEI_IN_LEKTION der Wortplaetze, aus jedem Level, in der Reihenfolge
     von karteiHeute(). Sie nehmen nur Plaetze bekannter
     Woerter dieses Levels ein - nNew steht oben schon fest, neue Woerter
     bleiben gleich viele. Aus einem anderen Level mit dem Hinweis
     "Wiederholung: <Level>" und dessen Woertern als Auswahl, wie die
     Rueckblick-Fragen im Level-Test; aus diesem Level wie jedes andere
     bekannte Wort. Ein Wort kommt nie zweimal. */
  const faellig = (imZa() ? [] : karteiHeute()).map(wortNachId).filter(Boolean)
    .slice(0, Math.min(KARTEI_IN_LEKTION, LEKTION_WOERTER - nNew));
  const faelligIds = new Set(faellig.map(f => f.w.id));
  const bekannt = knownW.filter(w => !faelligIds.has(w.id));
  nRev = Math.min(LEKTION_WOERTER - nNew - faellig.length, bekannt.length);
  const newW = unknown.slice(0,nNew), revW = bekannt.slice(0,nRev);
  const types = ['mc','mcrev','type']; if(canListen) types.push('listen'); if(canSpeak) types.push('speak');
  const pick = artenReihum(types);
  const tasks = [];
  [...newW, ...revW].forEach(w=> tasks.push({typ:pick(w), w, neu:!known.has(w.id)}));
  /* Faellige Woerter ohne Sprechen, wie in karteiRunde() und sternRunde():
     Sprechen laesst sich ueberspringen, dann zaehlt die Antwort nicht, und
     das Wort belegte einen der KARTEI_IN_LEKTION Plaetze umsonst
     (29.10.2026, Pruefung). */
  const pickF = artenReihum(types.filter(x => x !== 'speak'));
  faellig.forEach(f => tasks.push(Object.assign({typ:pickF(f.w), w:f.w, neu:false, faellig:true},
    f.c.id === c.id ? {} : {pool:f.c.words, rep:f.c.label})));
  const gesehenIds = new Set([...known, ...newW.map(w=>w.id)]);
  const luecken = lueckenFuerLektion(gesehenIds);
  luecken.forEach(s=> tasks.push({typ:'gap', s}));
  // Ohne w: showLessonTask() traegt task.w als gewusst ein, ein Satz ist kein Wort.
  // Die Luecken zuerst: ihre Saetze kommen nicht noch einmal als Kacheln.
  kachelnFuerLektion(gesehenIds, new Set(luecken.flatMap(lueckeFertig))).forEach(s=> tasks.push({typ:'kacheln', s}));
  shuffle(((GRAMMAR[c.id]||{}).uebungen||[]).slice()).slice(0, LEKTION_GRAMMATIK).forEach(g=> tasks.push({typ:'gram', g}));
  shuffle(tasks);
  const intros = newW.map(w=>({typ:'intro', w}));
  /* testVorher: ob der Level-Test schon VOR dieser Lektion frei war. Neue
     Woerter kommen schon waehrend der Lektion in known (showLessonTask);
     erst in lessonEnd() gemessen, war "vorher" also immer schon dasselbe
     wie "nachher", und der Hinweis "Der Level-Test ist jetzt
     freigeschaltet!" kam nie. Hier gemerkt, erscheint er genau in der
     Lektion, die ihn freischaltet.
     Gefunden bei der Pruefung am 07.10.2026. */
  Lx = {queue:[...intros, ...tasks], i:0, results:[], right:0, total:tasks.length, skipped:0, skipNachFehler:0, newWords:new Set(), retried:new Set(),
        testVorher: testAllowed(c)};
}
/* Die Punktereihe ueber einer Aufgabe (Lektion, Level-Test, Einstufung) ist
   fuer Screenreader eine Fortschrittsanzeige (17.10.2026, WCAG 1.1.1) -
   vorher waren es nur leere Punkte ohne jeden Text. Der Name ist
   "Frage 3 von 12", der Text aus den Geschichten: es braucht keinen neuen.
   aria-valuenow zaehlt die schon beantworteten. Die Punkte darin liest
   niemand einzeln vor: eine Fortschrittsanzeige hat keine Kinder. */
function punkteStand(el, i, n){
  if(!el) return;
  if(!n){ ['role', 'aria-valuemin', 'aria-valuemax', 'aria-valuenow', 'aria-label'].forEach(a => el.removeAttribute(a)); return; }
  el.setAttribute('role', 'progressbar');
  el.setAttribute('aria-valuemin', '0');
  el.setAttribute('aria-valuemax', String(n));
  el.setAttribute('aria-valuenow', String(Math.min(i, n)));
  el.setAttribute('aria-label', t('gesch.frage_n', {i: Math.min(i + 1, n), n}));
}
function lessonBar(){
  $('lBar').innerHTML = Lx.queue.map((t,i)=>'<i class="'+(i<Lx.i ? (Lx.results[i]==='intro'?'intro':(Lx.results[i]==='skip'?'skip':(Lx.results[i]?'ok':'no'))) : (i===Lx.i?'cur':''))+'"></i>').join('');
  punkteStand($('lBar'), Lx.i, Lx.queue.length);
}
function showLessonTask(){
  lessonBar();
  // Der Stern gilt der Aufgabe, die jetzt kommt - auf dem Ergebnis keiner (19.10.2026)
  sternKnopf('lStern', Lx.i < Lx.queue.length ? Lx.queue[Lx.i] : null);
  if(Lx.i >= Lx.queue.length){ lessonEnd(); return; }
  const task = Lx.queue[Lx.i];
  $('lBody').dataset.i = Lx.i;
  renderTask(task, $('lBody'), res=>{
    if(res.intro){ Lx.results[Lx.i]='intro'; }
    else if(res.skipped){ Lx.results[Lx.i]='skip'; Lx.skipped++; if(res.nachFehler) Lx.skipNachFehler = (Lx.skipNachFehler || 0) + 1; }
    else {
      Lx.results[Lx.i]=res.ok; zmajReact(res.ok); uhrTakt(true); zaehle('auf');
      topfMerken(task, res.ok);
      if(Lx.quelle === 'stern') sternGeuebt(task);
      if(res.ok){
        Lx.right++; zaehle('ric');
        if(task.typ==='gap') zaehle('lue');
        if(task.typ==='listen') zaehle('hoer');
        // Neue Wörter hier zählen, nicht in lessonEnd: wer mitten in der
        // Lektion die Leben verliert, kommt dort nie an.
        if(task.w && !known.has(task.w.id)){ known.add(task.w.id); Lx.newWords.add(task.w.id); zaehle('neu'); }
        karteiAntwort(task, true);    // nach known.add: ein neues Wort bekommt hier seine erste Stufe
      }
      else {
        karteiAntwort(task, false);   // vor loseLife(), das speichert
        loseLife();
        if(!task.retry) Lx.queue.push({...task, retry:true});
        if(livesNow()===0){ Lx.i++; weiterBeiTipp('lBody', lessonOutOfLives); return; }
      }
    }
    Lx.i++;
    // Einleitung und Uebersprungenes sind keine Antworten - da gibt es
    // nichts nachzusehen, also gleich weiter.
    if(res.intro || res.skipped) showLessonTask();
    else weiterBeiTipp('lBody', showLessonTask);
  });
}
/* Zeigt eine Werbung und ruft danach `fertig(angesehen)` auf.
   `belohnt`: Der Nutzer hat sie freiwillig gestartet und bekommt etwas dafür.
   Hier steckt später das SDK. Bis dahin ein Platzhalter, der sich genauso
   verhält – mit Wartezeit und Schließen-Knopf.
   Beim echten SDK muss werbungPersonalisiert() mitgegeben werden: false
   bedeutet "nur allgemeine Werbung", bei AdMob das Feld npa=1. */
/* Ist AdMob beim Start gescheitert, faellt sonst jede Anzeige fuer den ganzen
   Lauf aus. Einmal nachfassen - danach geht es weiter wie immer, notfalls
   ueber den Platzhalter. */
/* Eine kurze Meldung, die nach drei Sekunden von selbst verschwindet.
   Die App hatte dafuer bisher keine Stelle - gebraucht wird sie erst,
   seit eine Anzeige ohne Ersatz ausfallen kann. */
let kurzUhr = 0;
function kurzMeldung(text){
  let el = document.querySelector('.kurznote');
  if(!el){
    el = document.createElement('div');
    el.className = 'kurznote';
    el.setAttribute('role', 'status');
    document.body.appendChild(el);
  }
  el.textContent = text;
  setTimeout(()=> el.classList.add('an'), 20);
  clearTimeout(kurzUhr);
  kurzUhr = setTimeout(()=>{
    el.classList.remove('an');
    setTimeout(()=>{ if(!el.classList.contains('an')) el.remove(); }, 400);
  }, 3200);
}

/* Punkt 9 und 13 aus WERBUNG_PRUEFUNG.md: es gab keinen Riegel gegen den
   zweiten Tipp. Ein zweiter Tipp startete einen zweiten Ladevorgang; kam
   der erst zurueck, nachdem das erste Video zu war, schob sich ein
   unangefordertes Vollbild-Video ueber die inzwischen geoeffnete
   Startseite - mit einem zweiten Leben und einem zweiten Abzug vom
   Tageskontingent.
   Der Riegel heisst anzeigeLaeuft: werbungLaeuft gibt es schon, das
   riegelt Googles Einwilligungsfenster ab. Er sitzt in zeigeWerbung()
   und nicht in zeigeWerbungJetzt():
   auch der Zweitversuch ueber admobStart() geht durch diese Tuer. Jeder
   Ausgang laeuft ueber fertigEinmal(), damit er wieder aufgeht. */
let anzeigeLaeuft = false;
/* Zwei Merker vom 07.10.2026. anzeigeZuletzt: wann zuletzt eine Anzeige
   zu Ende ging - daran haelt kartenNachreichen() die Bewertungskarte von
   ihr fern. lohnAbgebrochen: das belohnte Video stand, wurde aber vor der
   Belohnung weggedrueckt - dann meldet werbungFuerLeben() nicht „keine
   Anzeige“. */
let anzeigeZuletzt = 0;
let lohnAbgebrochen = false;
function zeigeWerbung(belohnt, fertig, darfNoch){
  if(anzeigeLaeuft){ fertig(false); return; }
  anzeigeLaeuft = true;
  lohnAbgebrochen = false;
  let erledigt = false;
  /* Sicherheitsleine. Ohne sie bliebe der Riegel fuer immer zu, wenn ein
     Weg sein fertig() nie ruft - und die App koennte bis zum Neustart
     keine Anzeige mehr zeigen. Die Frist liegt ueber der laengsten
     inneren Frist von 120 Sekunden, greift also nur, wenn wirklich
     niemand mehr antwortet. */
  let wacht = setTimeout(()=> fertigEinmal(false), 150000);
  const fertigEinmal = lief => {
    if(erledigt) return;          // ein Ausgang, einmal
    erledigt = true; anzeigeLaeuft = false;
    clearTimeout(wacht);
    if(lief || lohnAbgebrochen) anzeigeZuletzt = Date.now();   // fuer die Bewertungskarte
    fertig(lief);
  };
  /* Dieselbe Bedingung wie in werbungErlaubt(), siehe admobNachholbar().
     Danach Googles Antwort abgleichen wie in werbungVorbereiten() - wer
     erst im nachgeholten Fenster zugestimmt hat, bekaeme sonst bis zum
     Neustart nur npa-Anzeigen. 07.10.2026. */
  if(admobNachholbar()){
    admobZweitversuch = true;
    const weiter = ()=> zeigeWerbungJetzt(belohnt, fertigEinmal, darfNoch);
    admobStart().then(()=> admobDa() ? werbungAbgleichen() : null).then(weiter, weiter);
    return;
  }
  zeigeWerbungJetzt(belohnt, fertigEinmal, darfNoch);
}

function zeigeWerbungJetzt(belohnt, fertig, darfNoch){
  if(!werbungErlaubt(belohnt)){ fertig(false); return; }
  stilleBitte();   // kein Wort unter der Anzeige - egal ob echte oder Platzhalter

  // Auf dem Handy die echte Anzeige. Gezählt wird erst, wenn sie auch lief –
  // eine Anzeige, die nicht kam, darf kein Tageskontingent verbrauchen.
  // Und jede Art auf ihr eigenes Kontingent (Ajdin am 26.09.2026).
  if(admobDa()){
    admobZeigen(belohnt, darfNoch).then(lief => {
      if(lief) werbungGezaehlt(belohnt);
      // Auch ein vor der Belohnung weggedruecktes Video war eine Anzeige.
      if(lief || lohnAbgebrochen){ anzeigeMerken(belohnt); anzeigeMeldenAnbieten(); }
      fertig(lief);
    });
    return;
  }
  /* Auf dem Geraet gibt es keinen Platzhalter. Der ist fuer den PC
     gedacht, wo es AdMob gar nicht gibt. Ist das Plugin da und die
     Anzeige kann trotzdem nicht starten - ohne Netz zum Beispiel -,
     faellt sie aus: kein Kontingent verbraucht, und vor allem kein Leben
     fuer eine Anzeige, die nie lief. Gefunden bei P8 am 28.09.2026 im
     Flugmodus, wo auf dem Handy wirklich „Hier erscheint die Werbung“
     stand. */
  if(window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.AdMob){
    fertig(false); return;
  }
  werbungGezaehlt(belohnt);

  const kasten = document.createElement('div');
  kasten.className = 'werbung';
  kasten.innerHTML =
    '<div class="werbebox">' +
      '<div class="werbemarke">' + esc(t('werbung.marke')) + '</div>' +
      '<div class="werbeflaeche" id="werbePlatz">' + esc(t('werbung.platzhalter')) + '</div>' +
      '<div class="werbenote" id="werbeNote"></div>' +
      '<button class="btn know" id="werbeZu" disabled></button>' +
      (belohnt ? '' : '<button class="skip" id="werbePremium">' + esc(t('werbung.ohne')) + '</button>') +
    '</div>';
  document.body.appendChild(kasten);

  // Fünf Sekunden warten, dann darf man schließen - so machen es die SDKs auch
  let rest = 5;
  const knopf = kasten.querySelector('#werbeZu');
  const note = kasten.querySelector('#werbeNote');
  note.textContent = belohnt ? t('werbung.lohn_laeuft') : '';
  const tick = () => {
    if(rest > 0) knopf.textContent = t('werbung.warten', {n: rest});
    else if(belohnt) knopf.innerHTML = mitSymbol('herz', esc(t('werbung.lohn_abholen')));
    else knopf.textContent = t('werbung.weiter');
    knopf.disabled = rest > 0;
    if(rest-- > 0) return;
    clearInterval(uhr);
  };
  tick();
  const uhr = setInterval(tick, 1000);

  const schliessen = (angesehen) => {
    clearInterval(uhr);
    kasten.remove();
    fertig(angesehen);
  };
  knopf.addEventListener('click', () => schliessen(true));
  const pk = kasten.querySelector('#werbePremium');
  // Direkt zum Kaufkasten, siehe vollKaufOeffnen(). 07.10.2026
  if(pk) pk.addEventListener('click', () => { schliessen(false); vollKaufOeffnen(); });
}

/* ---- Anzeige melden (nur iOS, 30.10.2026) ----
   Apple verlangt in Apps mit Werbung eine Moeglichkeit, unpassende Anzeigen
   zu melden (Richtlinie 2.5.18). Die App hat keinen Server, also derselbe
   Weg wie beim Feedback: das Mailprogramm geht mit fertiger Nachricht an
   uns auf - mit Zeitpunkt und Art der letzten Anzeige, damit Ajdin sie in
   der AdMob-Konsole (Anzeigenpruefung) findet und sperren kann. Angeboten
   wird es sechs Sekunden lang nach jeder Vollbildanzeige und immer in den
   Einstellungen unter Werbung. Auf Android verlangt Google das nicht, dort
   bleibt alles, wie es war. */
let letzteAnzeige = null;      // {zeit: Date, belohnt}, nur im Arbeitsspeicher
function anzeigeMerken(belohnt){ letzteAnzeige = {zeit: new Date(), belohnt: !!belohnt}; }
/* Die fertige Mail als mailto-Link - eigene Funktion, damit die Tests sie
   lesen koennen, ohne ein Mailprogramm zu oeffnen. */
function anzeigeMeldenLink(){
  const a = letzteAnzeige;
  const wann = a ? a.zeit.toISOString().replace('T', ' ').slice(0, 19) + ' UTC'
                   + ' · ' + (a.belohnt ? 'rewarded' : 'interstitial') : '-';
  const betreff = 'Zmaj – ' + t('werbung.melden');
  const rumpf = t('werbung.melden_text') + '\n\n' + t('werbung.melden_wann') + ' ' + wann
              + '\n\n--\n' + (SPRACHE || '') + ' · ' + PLATTFORM + ' · ' + APP_VERSION;
  return 'mailto:' + ZMAJ_MAIL + '?subject=' + encodeURIComponent(betreff)
         + '&body=' + encodeURIComponent(rumpf);
}
function anzeigeMeldenMail(){
  try{ location.href = anzeigeMeldenLink(); }catch(e){}
}
let meldeUhr = 0;
function anzeigeMeldenAnbieten(){
  if(!IST_IOS) return;
  const alt = document.querySelector('.meldenote');
  if(alt) alt.remove();
  const el = document.createElement('div');
  el.className = 'meldenote';
  const b = document.createElement('button');
  b.type = 'button'; b.className = 'abolink'; b.id = 'anzeigeMeldenKurz';
  b.textContent = t('werbung.melden');
  b.addEventListener('click', ()=>{ el.remove(); anzeigeMeldenMail(); });
  el.appendChild(b);
  document.body.appendChild(el);
  setTimeout(()=> el.classList.add('an'), 20);
  clearTimeout(meldeUhr);
  meldeUhr = setTimeout(()=>{ el.classList.remove('an'); setTimeout(()=> el.remove(), 400); }, 6000);
}
$('anzeigeMelden').addEventListener('click', anzeigeMeldenMail);
/* Was auf iPhone und iPad in den Einstellungen anders ist, an einer Stelle.
   Beim Start (init) und nach dem Laden des Inhalts (ladeDaten). 30.10.2026 */
function einstellungenFuerPlattform(){
  if(!IST_IOS) return;
  const vib = $('setVibrationZeile'); if(vib) vib.style.display = 'none';   // Entscheidung 13
  // Anzeige melden nur, wo ueberhaupt Werbung laufen kann.
  const melden = $('setAnzeigeMelden');
  if(melden) melden.style.display = (WERBUNG_ECHT && !!(window.Capacitor && window.Capacitor.Plugins
                                       && window.Capacitor.Plugins.AdMob)) ? '' : 'none';
  // Ohne Apple-ID der App fuehren Bewerten und Empfehlen nirgendwohin.
  if(!appStoreDa()){ $('setBewerten').style.display = 'none'; $('setEmpfehlen').style.display = 'none'; }
}

/* Ein belohntes Video: freiwillig, gibt ein Leben zurück. */
function werbungFuerLeben(e){
  /* Punkt 9 und 13: den Knopf sperren, solange etwas laeuft. Der Riegel
     in zeigeWerbung() haelt ohnehin, aber ein Knopf, der sich nicht
     ruehrt, laedt zum zweiten Tipp ein. */
  /* Aus der Levelansicht und aus dem Wiederholen-Reiter kommt der Knopf
     selbst mit. Der Laden bleibt beim alten Weg - sein Knopf traegt
     eigenes Innenleben, das textContent unten zerstoeren wuerde. */
  /* Laeuft schon ein Video, still aussteigen (19.10.2026): Im Reiter
     Wiederholen gibt es ohne Leben zwei Video-Knoepfe (topfAd, sternAd).
     Der zweite Tipp lief sonst in den Riegel von zeigeWerbung() und
     meldete "keine Anzeige", waehrend das Video schon lud. */
  if(anzeigeLaeuft) return;
  const quelle = e && e.currentTarget;
  /* Der Laden-Knopf (data-videoleben, ohne id) fiel bis v96 auf $('lAd')
     durch: im Laden meist null, also wurde nichts gesperrt - ein zweiter
     Tipp lief in den Riegel und meldete „keine Anzeige“, waehrend das
     Video schon lud. Er wird jetzt selbst gesperrt, aber nur ueber
     disabled, sein Text bleibt. Pruefung vom 07.10.2026. */
  const ladenKnopf = (quelle && quelle.hasAttribute && quelle.hasAttribute('data-videoleben')) ? quelle : null;
  const knopf = ladenKnopf ? null
              : (quelle && (quelle.id === 'lvAd' || quelle.id === 'topfAd' || quelle.id === 'sternAd' || quelle.id === 'karteiAd' || istSprungAd(quelle))) ? quelle : $('lAd');
  /* Gefunden bei der Pruefung am 06.10.2026: der Knopf bleibt stehen,
     waehrend die Leben nachwachsen - der Schirm ohne Leben wartet die zwei
     Stunden ja gerade ab. Bei vollen Leben brachte das Video kein Herz,
     verbrauchte aber eines der freiwilligen Videos des Tages. Dann gar
     nicht erst starten, nur den Schirm auf den neuen Stand bringen. */
  if(livesNow() >= LEBEN_MAX){
    renderLives(); lebenWege(); topfNachziehen();
    if(sichtbar('shopView')) renderLaden();
    else if(knopf && knopf.id === 'lAd') ohneLebenVerlassen();
    else if(istSprungAd(knopf)) sprungLebenDa();
    return;
  }
  /* Punkt 17: bis zum ersten Bild der Anzeige vergehen Sekunden, in denen
     der AdMob-Weg gar keine Oberflaeche baut. Ohne ein Wort sieht die App
     unbeteiligt aus - und genau das loest den zweiten Tipp aus. */
  if(knopf){ knopf.disabled = true; knopf.innerHTML = mitSymbol('herz', esc(t('werbung.laedt'))); }
  if(ladenKnopf) ladenKnopf.disabled = true;
  lohnAbgebrochen = false;
  zeigeWerbung(true, angesehen => {
    if(knopf){ knopf.disabled = false; knopf.innerHTML = mitSymbol('herz', esc(t('werbung.leben_holen'))); }
    if(ladenKnopf) ladenKnopf.disabled = false;
    /* Ohne Anzeige kein Leben - und ein Wort dazu, sonst wirkt der Knopf
       kaputt. Wer das Video vor der Belohnung wegdrueckt, hatte aber eine
       Anzeige: dann sagt die Meldung, warum es kein Leben gab. 07.10.2026. */
    if(!angesehen){
      kurzMeldung(lohnAbgebrochen ? t('werbung.lohn_abgebrochen') : t('werbung.keine_anzeige'));
      return;
    }
    /* Die Zeit geht wie beim Kauf nach oben (Pruefbericht 1.4, B15,
       14.11.2026). Bis dahin blieb sie stehen: Beim naechsten Abgleich mit
       einem zweiten Geraet gewann bei gleicher Zeit die kleinere Zahl, und
       das Herz aus dem Video war weg (siehe zeitNachKauf()). Vorher
       abgleichen, was inzwischen nachgewachsen ist - auch wie beim Kauf. */
    syncLives();
    lives.anzahl = Math.min(LEBEN_MAX, lives.anzahl + WERBUNG_LEBEN_LOHN);
    lives.zeit = zeitNachKauf(lives.zeit, lives.anzahl >= LEBEN_MAX);
    saveProgress(); renderLives(); sound('ok');
    /* Punkt 14: nur aufraeumen, wenn der Bildschirm ohne Leben ueberhaupt
       noch steht. Wer waehrend des Ladens mit Muenzen ein Herz gekauft und
       eine neue Lektion angefangen hat, verlor sie sonst - showLevelHome()
       leert lBody, und lessonEnd() wird nie erreicht: keine Lektion
       gezaehlt, kein Bonus, kein Lerntag.
       Geprueft wird der Knopf selbst, nicht seine Kennung: nur wenn genau
       dieser Knoten noch im Dokument haengt, steht auch der alte Schirm
       noch. Dieselbe Vorsicht wie beim Interstitial seit dem 29.09.2026. */
    const danach = ()=>{
      if(knopf && (knopf.id === 'topfAd' || knopf.id === 'sternAd' || knopf.id === 'karteiAd')) showTopf();   // sternAd: Kasten "Markiert", 19.10.2026; karteiAd: "Heute faellig", 29.10.2026
      else if(knopf && knopf.id === 'lAd') ohneLebenVerlassen();
      else if(istSprungAd(knopf)) sprungLebenDa();   // Sprung-Test, 13.11.2026
      /* Aus dem Laden: den Laden neu zeichnen, damit Preis und Video zum
         neuen Herz passen. showLevelHome() traf hier nur die unsichtbare
         Levelansicht. 07.10.2026. */
      else if(ladenKnopf){ if(sichtbar('shopView')) renderLaden(); }
      else showLevelHome();
    };
    if(!knopf || document.body.contains(knopf)) danach();
    else topfNachziehen();
  }, ()=> !document.hidden);   // Punkt 1: App noch vorne?
}

/* Hier steht bewusst wenig: die Null, die Wartezeit, und was man jetzt tun
   kann. Kein Hinweis aufs Speichern, keine Tagesaufgaben – beides steht
   ohnehin auf der Startseite. Und unten nur ein Knopf, denn ohne Leben
   gibt es nur einen Weg.
   Die Vollversion kommt nicht jedes Mal, sondern bei jedem dritten Mal.
   Ein Hinweis, der immer da steht, wird nicht gelesen, sondern lästig.
   Seit dem 19.10.2026 derselbe Schirm fuer den Level-Test (imTest): er
   kostet jetzt Leben wie die Lektion, und bei null ist er genauso vorbei -
   nicht bestanden, ohne Ergebnis und ohne Anzeige danach. Wer ueber Video
   oder Muenzen ein Leben holt, landet wie in der Lektion auf der
   Level-Uebersicht und faengt den Test von vorn an. Anders als in der
   Lektion steht oben der Name des Levels wie auf dem Testergebnis, denn
   "Lektion abgebrochen" stimmt hier nicht. */
let ohneLeben = 0;
/* Pruefbericht 1.4, S18: Auf dem Ergebnisschirm von Lektion, Runde und
   Level-Test - und auf dem Schirm ohne Leben - gibt es nichts mehr
   abzubrechen. "✕ Lektion abbrechen" bzw. "✕ Test abbrechen" fuehrte dort
   nur noch zurueck, und dafuer hat der Schirm seine eigenen Knoepfe. Also
   weg wie bei sprungEnde() (eQuit). Die Zurueck-Taste des Handys klickt den
   versteckten Knopf weiter (zurueckTaste) und landet wie bisher in der
   Uebersicht. startLesson(), rundeStarten() und startTest() zeigen ihn
   wieder. */
function abbrechenZeigen(id, an){ const k = $(id); if(k) k.style.display = an ? '' : 'none'; }
function testOutOfLives(){ lessonOutOfLives(true); }
function lessonOutOfLives(imTest){
  stilleBitte(); uhrAus();   // das letzte Wort nicht in den Ergebnisschirm reden lassen
  /* Hier ist die Lektion zu Ende - das muss auch Lx sagen. Bei der letzten
     falschen Antwort wuchs die Warteschlange um die Wiederholung,
     Lx.i blieb also darunter. Folge: die Zurueck-Taste fragte auf diesem
     Schirm "Lektion abbrechen?", und "Weitermachen" setzte nichts fort, weil
     showLessonTask() nie wieder gerufen wird - der Nutzer musste zweimal
     zurueck. Gefunden am 26.09.2026. Dasselbe traf Muenzen, Laden und Zahnrad
     oben, die in lektionDarfWeg() dieselbe Bedingung pruefen.
     Beim Test dasselbe mit Tx: tQuit und lektionDarfWeg() fragen sonst
     "Test abbrechen?" fuer einen Test, der schon vorbei ist. */
  if(imTest) Tx.i = Tx.qs.length; else Lx.i = Lx.queue.length;
  /* Aus dem Test geht es immer zur Level-Uebersicht. lektionVerlassen()
     schaut auf Lx.topf - und Lx kann noch die Wiederholen-Runde von vorhin
     sein. */
  const weg = imTest ? showLevelHome : lektionVerlassen;
  const k = imTest ? {bar:'tBar', drache:'zmajTest', herz:'tHerz', body:'tBody'}
                   : {bar:'lBar', drache:'zmajLesson', herz:'lHerz', body:'lBody'};
  sternKnopf(imTest ? 'tStern' : 'lStern', null);   // keine Aufgabe mehr, also kein Stern (19.10.2026)
  // Der Tag zählt hier NICHT für die Lernserie. Das war früher anders
  // gedacht - wer übt, hat geübt -, aber Ajdin am 17.09.2026: die Serie
  // war gestiegen, obwohl die Lektion nicht geschafft war. Eine Serie, die
  // auch beim Scheitern wächst, sagt nichts mehr aus.
  saveProgress(); sound('no');
  ohneLeben++;
  /* Gefunden bei der Pruefung am 06.10.2026: gefragt wurde nur in
     lessonEnd(). Wer schon in der ersten Lektion alle Leben verliert, kam
     dort nie an - und gerade ihm gilt die Nachricht, wenn die Leben wieder
     voll sind. Dieselbe Zeile wie dort; gezeigt wird ganz unten. Zweimal
     gefragt wird nicht: benDran faellt beim Zeigen, gefragt bei der
     Antwort. */
  if(benPlugin() && !benStand().gefragt) benDran = true;
  const herz = VERBRAUCH.find(w => w.id === 'herz');
  const perVideo = werbungErlaubt(true);   // das freiwillige Video, eigenes Kontingent
  const perMuenzen = muenzen() >= herz.preis && herz.geht();
  $(k.bar).innerHTML=''; $(k.drache).style.display='none'; $(k.drache).innerHTML=''; $(k.herz).style.display='none';   // kleiner Drache abgebaut, nicht nur versteckt - siehe showLevelHome (19.10.2026)
  abbrechenZeigen(imTest ? 'tQuit' : 'lQuit', false);   // S18
  const titel = imTest ? t('level.titel', {i:levelNummer(catIdx), label:esc(cur().label)}) : t('lektion.aus');
  /* .ohneleben: daran erkennt ohneLebenVorbei() diesen Schirm. Im Test
     reicht .result-big.fail nicht, das traegt auch ein nicht bestandenes
     Ergebnis. */
  $(k.body).innerHTML =
    '<div class="ergebnis-titel">'+titel+'</div><div class="celebrate"><div class="zmaj sad">'+zmaj('cry')+'</div></div>'+
    '<div class="result-big fail ohneleben">'+symbol('herz', t('stat.leben'))+' 0</div>'+
    '<div class="feedback no">'+t('lektion.keine_leben')+'</div>'+
    '<div class="stats"><div class="stat"><b>'+fmtMin(nextLifeIn())+'</b>'+t('lektion.bis_naechstes')+'</div></div>'+
    // Zwei Wege zu einem Leben, nebeneinander und klein: ansehen oder zahlen
    ((perVideo || perMuenzen) ?
      '<div class="row schmal">'+
        (perVideo   ? '<button class="btn ghost" id="lAd">'+mitSymbol('herz', t('werbung.leben_holen'))+'</button>' : '')+
        (perMuenzen ? '<button class="btn ghost" id="lCoin">'+t('lektion.leben_muenzen', symbolTexte({n:herz.preis}))+'</button>' : '')+
      '</div>' : '')+
    vollZeileLeben('lVoll')+
    /* Platz fuer die Rueckmeldung des Video-Knopfs (Ajdin am 26.09.2026).
       Unsichtbar, solange nichts zu sagen ist: .feedback hat eine
       Mindesthoehe und einen Abstand oben, ein leerer Kasten risse sonst
       eine Luecke in den Schirm. */
    (perVideo ? '<div class="feedback" id="lAdNote" style="display:none; color:var(--muted)"></div>' : '')+
    (ohneLeben % 3 === 0 ? '<div class="feedback" style="color:var(--muted)">'+t('lektion.vollversion')+'</div>' : '')+
    '<div class="row"><button class="btn know" id="lHome">'+t(!imTest && Lx.topf ? 'topf.zurueck' : 'lektion.zurueck')+'</button></div>';
  /* Die Knoepfe heissen auch im Test lAd, lCoin und lHome: werbungFuerLeben()
     kennt den Video-Knopf unter lAd, und es steht immer nur einer dieser
     Schirme im Dokument - startTest() und startLesson() leeren das andere
     Feld. */
  $('lHome').addEventListener('click', ()=> weg());
  if($('lAd')) $('lAd').addEventListener('click', werbungFuerLeben);
  vollZeileHorchen('lVoll');
  /* Nur kaufen, wenn wirklich noch kein Leben da ist: der Schirm wird nicht
     nachgezogen, und wer nach Stunden zurueckkam, sah noch "♥ 0" und zahlte
     100 Muenzen fuer ein Leben, das schon nachgewachsen war. Gefunden bei der
     Pruefung am 06.10.2026. */
  if($('lCoin')) $('lCoin').addEventListener('click', ()=>{ if(livesNow() === 0) kaufe('herz'); weg(); });
  renderLives();
  /* Die Karte gleich hier und nicht erst auf der Startseite: auf diesem
     Schirm kommt keine Anzeige nach dem Ergebnis, und wer ohne Leben die
     App zumacht, saehe sie sonst nie. Nur fuer die Benachrichtigungen -
     die Bitte um eine Bewertung passt nicht zu einer verlorenen Lektion
     und wartet weiter auf die Startseite. */
  if(benDran) kartenNachreichen();
}
/* Der Schirm ohne Leben wird einmal gebaut und nie nachgezogen. Sind
   inzwischen Leben nachgewachsen - etwa nach der Nachricht "Leben wieder
   voll", die seit Build 95 genau von hier aus angeboten wird -, stimmt er
   nicht mehr: zurueck zur Uebersicht, wie werbungFuerLeben() es bei vollen
   Leben schon tut. Neu aufbauen ginge nicht, lessonOutOfLives() zaehlt und
   spielt den Fehlton. Gefunden bei der Pruefung am 06.10.2026.
   Seit dem 19.10.2026 auch fuer den Schirm im Level-Test. */
function ohneLebenVorbei(){
  if(!anzeigeLaeuft && livesNow() > 0 && sichtbar('levelView')
     && ((sichtbar('lesson') && $('lBody').querySelector('.ohneleben')) ||
         (sichtbar('test')   && $('tBody').querySelector('.ohneleben')))) ohneLebenVerlassen();
  /* Seit 13.11.2026 ebenso beim Sprung-Test: sein Schirm ohne Leben und der
     Hinweis auf der Karte des Reiters */
  if(!anzeigeLaeuft && livesNow() > 0
     && ((sichtbar('einstufungView') && Sx && Sx.fertig && $('eBody').querySelector('.ohneleben')) ||
         ($('sprungNote') && $('sprungNote').textContent))) sprungLebenDa();
}
/* Weg vom Schirm ohne Leben, sofern er noch steht: aus der Lektion (oder
   Wiederholen-Runde) wie bisher ueber lektionVerlassen(), aus dem
   Level-Test zur Level-Uebersicht (siehe lessonOutOfLives). */
function ohneLebenVerlassen(){
  if(!sichtbar('levelView')) return;
  if(sichtbar('lesson')) lektionVerlassen();
  else if(sichtbar('test')) showLevelHome();
}
/* Fuer die Tagesaufgabe "ohne Fehler": nichts uebersprungen - ausser
   Sprechaufgaben, an denen der Erkenner schon gescheitert war (16.11.2026,
   Ajdin nach einer Rueckmeldung ueber das Formular; res.nachFehler in der
   Sprechaufgabe). Lx.skipped selbst bleibt, wie es war: Statistik,
   Ergebnis und Wiederholung zaehlen jedes Ueberspringen. */
const ohneUebersprungen = () => Lx.skipped - (Lx.skipNachFehler || 0) === 0;
/* Faellt das Sprechen fuer die Sitzung aus, weil auf Android jede Sprache
   wiederholt an Sprach- oder Dienstfehlern scheitert (hoereAndroid(),
   SPRECH_DIENST_GRENZE), kam bis zum 17.11.2026 erst ab der naechsten Lektion
   keine Sprechaufgabe mehr. In der laufenden blieben die uebrigen stehen und
   liessen sich nur ueberspringen, und Ueberspringen ohne eigenen Versuch
   kostete die Tagesaufgabe "ohne Fehler". Jetzt nimmt die Seite die noch
   kommenden Sprechaufgaben aus der Lektion: ihr Wort hat in dieser Lektion
   dann keine Aufgabe, wie nach dem Ueberspringen, nur ohne Tipp und ohne
   Ueberspringen-Zaehler. Die Aufgabe, an der es gerade gescheitert ist, bleibt
   stehen; ihr Ueberspringen kostet nichts (gescheitert, Lx.skipNachFehler).
   Nur hier, nicht bei abgelehntem Mikrofon: dort bleibt es, wie es war.
   Sprechaufgaben gibt es nur in Lektionen (buildLesson()). */
function sprechAufgabenRaus(){
  if(!Lx || !Array.isArray(Lx.queue)) return;
  let raus = 0;
  for(let i = Lx.queue.length - 1; i > Lx.i; i--){
    if(Lx.queue[i] && Lx.queue[i].typ === 'speak'){ Lx.queue.splice(i, 1); raus++; }
  }
  if(raus && sichtbar('lesson')) lessonBar();
}
function lessonEnd(){
  if(Lx && Lx.topf){ topfEnde(); return; }
  stilleBitte(); uhrAus();   // das letzte Wort nicht in den Ergebnisschirm reden lassen
  const c=cur(); const wasAllowed = Lx.testVorher !== false;   // siehe buildLesson, 07.10.2026
  const scored = Lx.results.filter(r=>r!=='intro' && r!=='skip').length;
  zaehle('lek');
  // "Ohne Fehler" nur, wenn auch nichts übersprungen wurde – sonst holt man
  // sie sich, indem man jede Hör- und Sprechaufgabe wegdrückt.
  if(Lx.right === scored && scored > 0 && ohneUebersprungen()) zaehle('per');
  /* Beim Zahnarzt: kein Lerntag, die Wegmarken bleiben beim Lernpfad. */
  const newDay = imZa() ? false : markToday();
  const erfolgLob = erfolgZeile();   // Erfolge (13.11.2026): hakt ab, also vor dem Speichern
  saveProgress(); sound('done');
  cloudNachLernen();   // 17.11.2026, siehe dort
  /* Die gruenen Zeilen fuer erledigte Tagesaufgaben. Sie waren seit dem
     Umbau des Ladens verschwunden: questZeilen() stand fertig da und wurde
     von niemandem mehr aufgerufen, die Muenzen erschienen wortlos in der
     Kopfzeile. questZeilen() LEERT questFrisch, darf also nur einmal je
     Ergebnisschirm laufen - deshalb hier in eine Variable und unten nur
     noch eingesetzt. Ajdin am 18.09.2026. */
  const questLob = questZeilen();
  if(questLob) setTimeout(()=>sound('quest'), 850);   // nach der Fanfare, nicht darueber
  if(benPlugin() && !benStand().gefragt) benDran = true;
  const pct=levelPct(c), nowAllowed=testAllowed(c);
  $('lBar').innerHTML=''; $('zmajLesson').style.display='none'; $('zmajLesson').innerHTML=''; $('lHerz').style.display='none';   // kleiner Drache abgebaut, nicht nur versteckt - siehe showLevelHome (19.10.2026)
  abbrechenZeigen('lQuit', false);   // S18, siehe abbrechenZeigen
  $('lBody').innerHTML =
    '<div class="ergebnis-titel">'+mitKonfetti(t('lektion.geschafft'))+'</div><div class="celebrate"><div class="zmaj cheer">'+zmaj('cheer')+'</div></div>'+
    '<div class="result-big">'+Lx.right+' / '+scored+'</div>'+
    '<div class="stats"><div class="stat"><b>+'+Lx.newWords.size+'</b>'+tp('stat.neue_woerter', Lx.newWords.size)+'</div><div class="stat"><b>'+pct+' %</b>'+t('stat.fortschritt')+'</div><div class="stat"><b>'+flammeHtml()+' '+streak()+'</b>'+tp('stat.tage_folge', streak())+'</div><div class="stat"><b>'+herzSymbol()+' '+(unlimited()?'∞':livesNow())+'</b>'+t('stat.leben')+'</div></div>'+
    (nowAllowed && !wasAllowed && !passed.has(c.id) ? '<div class="feedback ok">'+t('lektion.test_frei')+'</div>' : '')+
    (newDay ? '<div class="feedback ok">'+t('lektion.heute_geuebt')+'</div>' : '')+
    questLob+erfolgLob+
    '<div class="row"><button class="btn ghost" id="lHome">'+t('lektion.zurueck')+'</button><button class="btn know" id="lMore">'+t('lektion.noch_eine')+'</button></div>'+
    /* Zweite, leise Reihe: der Weg ganz heraus. "Zurueck zum Level" fuehrt
       nur in die Uebersicht DIESES Levels - auf dem Handy ist der
       Zurueck-Knopf oben ausgeblendet, und ohne diesen Knopf sitzt man
       nach jeder Lektion fest. Gemeldet am 24.09.2026. */
    '<div class="row schmal"><button class="btn ghost" id="lPfad">'+t('btn.zurueck_pfad')+'</button></div>';
  $('lHome').addEventListener('click', lektionVerlassen);
  $('lMore').addEventListener('click', startLesson);
  $('lPfad').addEventListener('click', ()=>{ homeMode='words'; showHome(); });
  /* Pflicht-Anmeldung (28.10.2026): nach der ersten Lektion steht statt
     der drei Knoepfe nur "Weiter" da, und der fuehrt zur Anmeldung. */
  if(anmeldungFaellig()) torStattKnoepfe(['lHome', 'lMore', 'lPfad']);

  // Werbung erst nach dem Ergebnis, nie mittendrin. Die ersten Lektionen
  // bleiben frei, danach jede WERBUNG_JEDE_X-te.
  werbungZaehler++;
  werbungNachDemErgebnis('lesson', ()=> Lx);
}

/* Die Anzeige nach einem Ergebnisschirm - nach der Lektion und nach dem Test.
   feld: 'lesson' oder 'test', beide liegen in levelView.
   marke: liefert das Objekt, das mit dem naechsten Durchgang wechselt (Lx bzw.
   Tx) - daran erkennt man, ob der Nutzer weitergegangen ist.

   Zwei Dinge, die Ajdin am 27.09.2026 gemeldet hat ("also es kommt nicht immer
   werbung nach der lektion und nach dem test auch nicht"):
   - Nach dem TEST kam gar keine. Das war keine Entscheidung, sondern eine
     Luecke: showTestResult() hat den Auslöser einfach nie gerufen.
   - Wer in den 1,2 Sekunden weitertippt, verlor die Anzeige ganz. Der Zaehler
     stand schon hoeher, also war sie weg. Jetzt wird sie geschuldet und beim
     naechsten Ergebnisschirm nachgeholt. */
let werbungSchuldig = !!werbungHeute.offen;
/* Immer hierueber setzen, nie direkt: der Merker muss in denselben
   Eintrag wie die Tageszaehler, sonst ueberlebt er das Schliessen der
   App nicht. */
function schuldigSetzen(ja){
  werbungSchuldig = ja;
  werbungHeute.offen = ja;
  try{ localStorage.setItem('zmaj_werbung', JSON.stringify(werbungHeute)); }catch(e){}
}
/* Der Wecker aus werbungNachDemErgebnis. Er muss abraeumbar sein: geht
   die App in den 1,2 Sekunden in den Hintergrund - Home-Taste, Anruf -,
   duerfte die Anzeige sonst beim Zurueckkommen erscheinen, ohne dass
   jemand etwas getan hat. Genau das verbietet Google.
   Punkt 2 aus WERBUNG_PRUEFUNG.md, behoben am 29.09.2026. */
let werbungWecker = 0;
function werbungNachDemErgebnis(feld, marke){
  const dran = werbungSchuldig ||
               (werbungZaehler >= WERBUNG_AB_LEKTION &&
                (werbungZaehler - WERBUNG_AB_LEKTION) % WERBUNG_JEDE_X === 0);
  if(!dran || !werbungErlaubt()) return;
  /* Nur, wenn der Ergebnisschirm noch steht. Sonst stuende die Anzeige ueber
     dem Lernpfad, den Einstellungen oder schon ueber der ersten Aufgabe der
     naechsten Lektion. */
  const dieser = marke();
  /* Dieselbe Bedingung zweimal gebraucht: einmal jetzt, wenn der Wecker
     klingelt, und noch einmal unten in admobZeigen(), kurz bevor die
     Anzeige wirklich kommt. document.hidden gehoert dazu - sichtbar()
     fragt nur das CSS, nicht ob die App ueberhaupt noch vorne ist. */
  const darfNoch = ()=> marke() === dieser && !wegmarkeLaeuft
                        && sichtbar('levelView') && sichtbar(feld)
                        && !document.hidden;
  clearTimeout(werbungWecker);
  werbungWecker = setTimeout(()=>{
    werbungWecker = 0;
    /* wegmarkeLaeuft: eine Anzeige ueber dem 100. Lerntag waere die
       schlechteste Minute, die sich die App aussuchen koennte. */
    if(darfNoch()){
      schuldigSetzen(false);
      zeigeWerbung(false, lief => { if(!lief) schuldigSetzen(true); }, darfNoch);
    } else {
      schuldigSetzen(true);     // nicht verloren, nur verschoben
    }
  }, 1200);
}
/* Android fragt erst beim allerersten Zugriff nach dem Mikrofon – und die
   Spracherkennung bricht in derselben Sekunde mit „nicht erlaubt" ab,
   bevor jemand antworten konnte. Deshalb holen wir die Erlaubnis schon
   beim Start der Lektion ein, sobald darin eine Sprechaufgabe steckt:
   Wir öffnen kurz das Mikrofon und schließen es sofort wieder – uns geht
   es nur um die Rückfrage. Sagt jemand Nein, passiert nichts Schlimmes,
   die Sprechaufgabe lässt sich überspringen.
   Gefragt wird nur einmal je Sitzung; Android merkt sich die Antwort. */
let mikroGefragt = false;
async function mikroVorbereiten(){
  if(mikroGefragt) return;
  mikroGefragt = true;
  const H = hoererPlugin();
  if(H){
    // Das Plugin fragt selbst und zeigt dabei Androids Abfrage.
    try{
      const r = await H.checkPermissions();
      if(r.speechRecognition !== 'granted') await H.requestPermissions();
    }catch(e){}
    return;
  }
  const md = navigator.mediaDevices;
  if(!md || !md.getUserMedia) return;
  try{
    const strom = await md.getUserMedia({audio:true});
    strom.getTracks().forEach(s=>s.stop());
  }catch(e){}
}

/* Die zwei Wege zu einem Leben, in der Levelansicht.
   Bis zum 27.09.2026 gab es den Weg ueber das freiwillige Video NUR auf dem
   Schirm, der kommt, wenn die Leben mitten in der Lektion ausgehen. Wer die
   App zwischendurch geschlossen hatte und mit 0 Leben zurueckkam, tippte auf
   ein Level und las "warte zwei Stunden" - ohne einen einzigen Knopf. Eine
   Sackgasse, und der Laden bot nur das Herz fuer Muenzen.
   Ajdin: "wie soll man mit werbung auffuellen es gibt keinen button". */
/* Die leise Zeile unter den zwei Wegen: wer keine Leben mehr hat, ist
   genau der, dem unbegrenzte Leben etwas nuetzen. Sie erscheint nur,
   wenn es die Vollversion hier ueberhaupt zu kaufen gibt, und nie bei
   jemandem, der sie schon hat. Ajdin am 29.09.2026: „nicht jeder geht
   in die Einstellungen“. */
function vollZeileLeben(id){
  if(unlimited() || !aboPlugin() || aboProdukteFehlen) return '';
  /* Bewusst die leise Zeile, auch auf dem Sperrschirm: als richtiger
     Knopf zwischen den zwei Herz-Wegen sah sie nach Bettelei aus.
     Ajdin am 29.09.2026: „neee das sieht nicht gut aus, im laden schon
     aber da nicht“. Im Laden bleibt die eigene Zeile. */
  /* Die Testwoche als leise zweite Zeile, nur wenn Google sie anbietet -
     siehe vollZeileLaden(). 07.10.2026 */
  const gratis = gratisText(aboGratisPlan);
  return '<div class="abohinweis" style="text-align:center">'
       + '<button type="button" class="abolink" id="' + id + '">'
       + esc(t('voll.nie_warten')) + '</button>'
       + (gratis ? '<div>' + esc(gratis) + '</div>' : '') + '</div>';
}
function vollZeileHorchen(id){
  const k = document.getElementById(id);
  if(k) k.addEventListener('click', ()=>{ vollKaufOeffnen(); });   // 07.10.2026
}
function lebenWege(){
  const kasten = $('lvLeben');
  if(!kasten) return;
  const herz = VERBRAUCH.find(w => w.id === 'herz');
  const perVideo   = werbungErlaubt(true);
  const perMuenzen = muenzen() >= herz.preis && herz.geht();
  const vollZeile = vollZeileLeben('lvVoll');
  if(livesNow() > 0 || (!perVideo && !perMuenzen && !vollZeile)){
    kasten.style.display = 'none'; kasten.innerHTML = ''; return;
  }
  kasten.innerHTML =
      (perVideo   ? '<button class="btn ghost" id="lvAd">'+mitSymbol('herz', t('werbung.leben_holen'))+'</button>' : '')
    + (perMuenzen ? '<button class="btn ghost" id="lvCoin">'+t('lektion.leben_muenzen', symbolTexte({n:herz.preis}))+'</button>' : '')
    + vollZeile;
  kasten.style.display = 'flex';
  if($('lvAd'))   $('lvAd').addEventListener('click', werbungFuerLeben);
  if($('lvCoin')) $('lvCoin').addEventListener('click', ()=>{ kaufe('herz'); renderLives(); updateProgress(); });
  vollZeileHorchen('lvVoll');
}

function startLesson(){
  if(anmeldungSperre()) return;
  if(livesNow()===0){ renderLives(); $('lvNote').textContent=t('level.keine_leben',{zeit:fmtMin(nextLifeIn())}); lebenWege(); return; }
  buildLesson();
  interstitialVorladen();   // liegt am Ende der Lektion bereit, siehe interstitialVorladen
  if(Lx.queue.some(a=>a.typ==='speak')) mikroVorbereiten();
  stilleBitte();   // Unteransicht, laeuft nicht ueber showView() - siehe showLevelHome
  $('levelHome').style.display='none'; $('test').style.display='none'; $('lesson').style.display='block';
  nurHerz(true);
  $('tBody').innerHTML='';   // siehe showLevelHome: gleiche ids in beiden Feldern
  /* Der Drache des Tests (seit 19.10.2026) liefe sonst unsichtbar in
     Schleife weiter: zmajRuht() kennt nur ausgeblendete Ansichten, und
     #test ist keine. Leer geraeumt baut der Beobachter ihn ab. */
  $('zmajTest').innerHTML='';
  uhrNeu();
  const zl=$('zmajLesson'); zl.style.display='block'; $('lHerz').style.display=''; zl.innerHTML=zmaj('happy'); setMood(zl,'happy');
  abbrechenZeigen('lQuit', true);   // das Ergebnis davor blendet ihn aus (S18)
  showLessonTask(); window.scrollTo({top:0, behavior:'smooth'});
}
$('btnLesson').addEventListener('click', startLesson);
/* Abbrechen kostet die halbe Lektion - deshalb einmal nachfragen, solange
   noch Aufgaben offen sind. Nach dem Ergebnis fragt es nicht mehr. */
$('lQuit').addEventListener('click', async ()=>{
  if(Lx && Lx.i < Lx.queue.length &&
     !await frage(t('lektion.abbrechen_frage'), t('lektion.abbrechen_hinweis'),
                  t('btn.abbrechen'), t('btn.weitermachen'))) return;
  saveProgress(); lektionVerlassen();
});

var teileDa = (teileDa || 0) + 1;   // dieser Teil ist ganz gelaufen, siehe teileDa oben
