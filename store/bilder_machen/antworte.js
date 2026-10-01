window.__antworte = async (richtig, feld='eBody', X=()=>Ex) => {
  const x = X(); const q = (x.qs||x.queue)[x.i]; const body = document.getElementById(feld);
  const warte = ms => new Promise(r=>setTimeout(r,ms));
  const w0 = body.querySelector('.weiterbox .btn'); if(w0){ w0.click(); await warte(400); return 'weiter'; }
  if(q.typ==='intro'){ body.querySelector('#xNext').click(); await warte(300); return 'intro'; }
  if(q.typ==='speak' || (q.typ==='listen' && richtig===null)){ const s=body.querySelector('#xSkip'); s.click(); await warte(300); return 'skip'; }
  if(q.typ==='gap'){ const inp=body.querySelector('#xIn'); inp.value = richtig ? q.s.answer.split(' / ')[0] : 'zzzz'; body.querySelector('#xCheck').click(); }
  else if(q.typ==='type'){ const inp=body.querySelector('#xIn'); inp.value = richtig ? q.w.bs.split(' / ')[0] : 'zzzz'; body.querySelector('#xCheck').click(); }
  else { const soll = q.typ==='gram' ? q.g.richtig : (q.typ==='mcrev' ? q.w.de : q.w.bs);
    const opts=[...body.querySelectorAll('.opt')]; const b = richtig ? opts.find(o=>o.textContent===soll) : opts.find(o=>o.textContent!==soll); if(!b) return 'kein knopf '+soll; b.click(); }
  await warte(1200); const w = body.querySelector('.weiterbox .btn'); if(w) w.click(); await warte(400); return q.typ; };
return 'ok';
