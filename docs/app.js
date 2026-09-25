const DATA_URL="./data/ltt1445.json";
let data=null, running=true, phase=0;

const $=s=>document.querySelector(s);
const $$=s=>[...document.querySelectorAll(s)];
const fmt=(v,d=2)=>v==null||Number.isNaN(Number(v))?"—":Number(v).toFixed(d);
const stat=(label,value,note="")=>`<div class="stat"><small>${label}</small><strong>${value}</strong>${note?`<em>${note}</em>`:""}</div>`;

function setMode(mode){
  document.body.dataset.mode=mode;
  $$(".modeBtn").forEach(btn=>btn.classList.toggle("active",btn.dataset.mode===mode));
  localStorage.setItem("trisolaris-detail-mode",mode);
}
$$(".modeBtn").forEach(btn=>btn.addEventListener("click",()=>setMode(btn.dataset.mode)));
setMode(localStorage.getItem("trisolaris-detail-mode")||"simple");

async function load(){
  const response=await fetch(DATA_URL,{cache:"no-store"});
  if(!response.ok) throw new Error("No se pudo cargar el dataset científico");
  data=await response.json();
  renderAll();
  requestAnimationFrame(loop);
}

function renderAll(){
  const official=data.status==="official-nasa-plus-literature";
  $("#syncBadge").className="sourcePill "+(official?"observed":"literature");
  $("#syncBadge").textContent=official?"NASA EN VIVO":"DATOS BASE";

  const s=data.system;
  const planetCount=(data.observed_planets||[]).length;
  $("#storySystem").textContent=`${data.stars.length} estrellas · ${fmt(s.distance_pc*3.26156,1)} años luz`;
  $("#storySystemText").textContent="Un sistema triple real y cercano, con una arquitectura jerárquica que podemos reconstruir desde observaciones y literatura.";
  $("#storyPlanets").textContent=`${planetCount} planeta${planetCount===1?"":"s"} confirmado${planetCount===1?"":"s"}`;
  $("#storyPlanetsText").textContent=official
    ?"Los registros visibles provienen del NASA Exoplanet Archive y conservan su procedencia."
    :"La sincronización oficial aún no se ha ejecutado para esta copia.";
  $("#storyCandidate").textContent="H-01 · laboratorio de habitabilidad";

  $("#systemStats").innerHTML=
    stat("Sistema",s.name)+
    stat("Distancia",fmt(s.distance_pc,2)+" pc","≈ "+fmt(s.distance_pc*3.26156,1)+" años luz")+
    stat("Arquitectura",s.architecture)+
    stat("Estrellas",data.stars.length)+
    stat("Período exterior",fmt(data.hierarchy?.outer_period_years_approx,0)+" años","valor aprox. de literatura")+
    stat("Período B–C",fmt(data.hierarchy?.bc_period_years_approx,0)+" años","valor aprox. de literatura");

  $("#dataNote").innerHTML=official
    ?"<b>Datos planetarios oficiales presentes.</b> Las filas de planetas se generaron desde la consulta TAP registrada al NASA Exoplanet Archive. La geometría visual está comprimida y no representa una escala física exacta."
    :"<b>Sincronización pendiente.</b> La arquitectura triple está respaldada por literatura, pero los planetas observados todavía no fueron incorporados desde el archivo oficial.";

  renderPlanets();
  initCandidate();
}

function planetPlainLanguage(p){
  const teq=p.equilibrium_temperature_k;
  const c=teq==null?null:teq-273.15;
  let climate="Su temperatura de equilibrio aún no está disponible en este registro.";
  if(c!=null){
    if(c>180) climate="Recibe tanta energía que su entorno sería extremadamente caliente para la vida terrestre.";
    else if(c>80) climate="Es un mundo muy caliente bajo una estimación simple de equilibrio térmico.";
    else if(c>20) climate="Su temperatura de equilibrio es cálida, aunque una atmósfera real podría cambiar mucho el resultado.";
    else climate="Su equilibrio térmico es relativamente frío; la atmósfera sería decisiva.";
  }
  const size=p.radius_earth==null?"tamaño no determinado":p.radius_earth<1.5?"aproximadamente rocoso por tamaño":"más grande que la Tierra";
  return `${climate} Por radio, es ${size}.`;
}

function renderPlanets(){
  const rows=data.observed_planets||[];
  $("#planetCount").textContent=rows.length+" planeta"+(rows.length===1?"":"s");

  $("#planetCards").innerHTML=rows.length
    ? rows.map((p,i)=>`<article class="planetCard">
        <div class="planetVisual"><div class="planetOrb"></div></div>
        <span class="sourcePill observed">OBSERVED</span>
        <h3>${p.name}</h3>
        <p>${planetPlainLanguage(p)}</p>
        <div class="planetFacts">
          <span class="factChip">Año ${p.discovery_year==null?"—":Math.round(p.discovery_year)}</span>
          <span class="factChip">${fmt(p.radius_earth,2)} R⊕</span>
          <span class="factChip">${fmt(p.period_days,2)} días por órbita</span>
        </div>
      </article>`).join("")
    : '<article class="planetCard"><h3>Sin planetas cargados</h3><p>El dataset oficial todavía no está disponible en esta versión.</p></article>';

  if(!rows.length){
    $("#planetTable").innerHTML='<div class="evidenceNote">No hay filas OBSERVED disponibles en esta copia del dataset.</div>';
    return;
  }

  $("#planetTable").innerHTML=`<table><thead><tr>
    <th>Planeta</th><th>Período</th><th>Semieje mayor</th><th>Radio</th><th>Masa</th><th>Teq</th><th>Descubrimiento</th><th>Nivel</th>
  </tr></thead><tbody>${rows.map(p=>`<tr>
    <td><b>${p.name}</b></td>
    <td>${fmt(p.period_days,3)} d</td>
    <td>${fmt(p.semi_major_axis_au,4)} AU</td>
    <td>${fmt(p.radius_earth,2)} R⊕</td>
    <td>${fmt(p.mass_earth,2)} M⊕</td>
    <td>${p.equilibrium_temperature_k==null?"—":fmt(p.equilibrium_temperature_k,0)+" K"}</td>
    <td>${p.discovery_year==null?"—":Math.round(p.discovery_year)}</td>
    <td><span class="sourcePill observed">OBSERVED</span></td>
  </tr>`).join("")}</tbody></table>`;
}

let candidateInitialized=false;
function initCandidate(){
  const h=data.hypothetical_experiment;
  if(!candidateInitialized){
    $("#axis").value=h.semi_major_axis_au;
    $("#albedo").value=h.albedo;
    $("#greenhouse").value=h.greenhouse_k;
    ["axis","albedo","greenhouse"].forEach(id=>$("#"+id).addEventListener("input",renderCandidate));
    candidateInitialized=true;
  }
  renderCandidate();
}

function candidateLabel(score,celsius){
  if(score>.78) return {
    title:"Interesante para pruebas más profundas",
    text:`Con estas suposiciones, H-01 cae cerca de una ventana térmica favorable. La temperatura superficial simplificada sería de ${fmt(celsius,1)} °C.`,
    tone:"good"
  };
  if(score>.52) return {
    title:"Posible, pero depende mucho de la atmósfera",
    text:`El escenario es marginal. Una atmósfera real, el agua disponible y la actividad estelar podrían moverlo hacia condiciones mejores o peores.`,
    tone:"mid"
  };
  return {
    title:"Hostil bajo estas suposiciones",
    text:`La combinación actual queda lejos de una ventana sencilla de habitabilidad. Cambia la distancia, el albedo o el efecto invernadero para explorar otro escenario.`,
    tone:"low"
  };
}

function renderCandidate(){
  if(!data)return;
  const a=+$("#axis").value, albedo=+$("#albedo").value, gh=+$("#greenhouse").value;
  $("#axisOut").textContent=a.toFixed(3)+" AU";
  $("#albedoOut").textContent=albedo.toFixed(2);
  $("#greenhouseOut").textContent="+"+gh.toFixed(0)+" K";

  const A=data.stars.find(s=>s.id==="A");
  const B=data.stars.find(s=>s.id==="B");
  const C=data.stars.find(s=>s.id==="C");
  const outerAu=(data.hierarchy?.outer_projected_separation_arcsec_approx||7)*(data.system.distance_pc||6.86);
  const fluxA=A.luminosity_solar/(a*a);
  const fluxBC=(B.luminosity_solar+C.luminosity_solar)/(outerAu*outerAu);
  const flux=fluxA+fluxBC;
  const teq=278.5*Math.pow(Math.max(0.001,flux*(1-albedo)),0.25);
  const surface=teq+gh;
  const celsius=surface-273.15;
  const liquid=Math.max(0,Math.min(1,1-Math.abs(celsius-18)/55));
  const fluxScore=Math.max(0,Math.min(1,1-Math.abs(flux-1)/1.1));
  const proxy=(0.56*liquid+0.44*fluxScore);
  const reading=candidateLabel(proxy,celsius);

  $("#habitScore").textContent=Math.round(proxy*100)+"%";
  $("#candidateHeadline").textContent=reading.title;
  $("#candidatePlain").textContent=reading.text;
  $("#storyCandidateText").textContent=`${Math.round(proxy*100)}% en la heurística rápida actual. Este valor no es todavía una conclusión climática.`;

  const orb=$("#habitOrb");
  if(reading.tone==="good"){
    orb.style.background="radial-gradient(circle at 35% 28%,#8af0c6 0,#2b755a 42%,#0a1915 75%)";
    orb.style.boxShadow="0 0 62px rgba(73,197,149,.25), inset -18px -22px 34px rgba(0,0,0,.35)";
  }else if(reading.tone==="mid"){
    orb.style.background="radial-gradient(circle at 35% 28%,#f2cf7e 0,#7a6332 42%,#211a0c 75%)";
    orb.style.boxShadow="0 0 62px rgba(225,179,82,.20), inset -18px -22px 34px rgba(0,0,0,.35)";
  }else{
    orb.style.background="radial-gradient(circle at 35% 28%,#e68b86 0,#743b3b 42%,#20100f 75%)";
    orb.style.boxShadow="0 0 62px rgba(211,103,96,.18), inset -18px -22px 34px rgba(0,0,0,.35)";
  }

  $("#candidateStats").innerHTML=
    stat("Flujo combinado",fmt(flux,3)+" S⊕","A aporta "+fmt(100*fluxA/flux,1)+"%")+
    stat("Temperatura de equilibrio",fmt(teq,1)+" K")+
    stat("Proxy superficial",fmt(surface,1)+" K",fmt(celsius,1)+" °C")+
    stat("Proxy agua líquida",Math.round(liquid*100)+"%","heurística")+
    stat("Proxy habitabilidad",Math.round(proxy*100)+"%","DERIVED · no GCM");

  $("#candidateWhy").innerHTML=`<b>Cómo se obtuvo:</b> la lectura usa flujo estelar, albedo y un desplazamiento térmico de efecto invernadero. No establece estabilidad orbital, retención atmosférica, actividad de llamaradas, circulación oceánica ni biosfera. El siguiente motor científico debe resolver esas capas de forma separada.`;
}

function draw(){
  if(!data)return;
  const c=$("#systemCanvas"),x=c.getContext("2d"),w=c.width,h=c.height;
  x.clearRect(0,0,w,h);
  const cx=w*.48,cy=h*.47;
  x.fillStyle="#020609";x.fillRect(0,0,w,h);

  const bg=x.createRadialGradient(cx,cy,10,cx,cy,w*.62);
  bg.addColorStop(0,"rgba(20,39,52,.42)");
  bg.addColorStop(1,"rgba(2,6,9,0)");
  x.fillStyle=bg;x.fillRect(0,0,w,h);

  for(let i=0;i<170;i++){
    const px=(i*137.1)%w,py=(i*83.7)%h,a=.10+((i*17)%50)/100;
    x.fillStyle=`rgba(215,237,248,${a})`;
    x.fillRect(px,py,i%11===0?1.8:1,i%11===0?1.8:1);
  }

  const A=data.stars.find(s=>s.id==="A");
  const B=data.stars.find(s=>s.id==="B");
  const C=data.stars.find(s=>s.id==="C");

  const outerR=Math.min(w*.29,330);
  const bcCenter={x:cx+outerR*Math.cos(phase*.11),y:cy+outerR*.48*Math.sin(phase*.11)};
  const bcR=58;
  const apos={x:cx-150,y:cy};
  const bpos={x:bcCenter.x+bcR*Math.cos(phase*.65),y:bcCenter.y+bcR*.48*Math.sin(phase*.65)};
  const cpos={x:bcCenter.x-bcR*Math.cos(phase*.65),y:bcCenter.y-bcR*.48*Math.sin(phase*.65)};

  x.strokeStyle="rgba(120,171,199,.16)";x.lineWidth=1.1;
  x.beginPath();x.ellipse(cx+60,cy,outerR,outerR*.48,0,0,Math.PI*2);x.stroke();
  x.beginPath();x.ellipse(bcCenter.x,bcCenter.y,bcR,bcR*.48,0,0,Math.PI*2);x.stroke();

  drawStar(x,apos,28,"A","#ef8174",A);
  drawStar(x,bpos,21,"B","#e67770",B);
  drawStar(x,cpos,18,"C","#cf676d",C);

  const planets=data.observed_planets||[];
  planets.slice(0,5).forEach((p,i)=>{
    const r=62+i*31,ang=phase*(1.45/(i+1))+(i*1.4);
    x.strokeStyle="rgba(112,210,255,.13)";
    x.beginPath();x.ellipse(apos.x,apos.y,r,r*.42,0,0,Math.PI*2);x.stroke();
    const pp={x:apos.x+r*Math.cos(ang),y:apos.y+r*.42*Math.sin(ang)};
    x.fillStyle="#78d4ef";x.beginPath();x.arc(pp.x,pp.y,5.2,0,Math.PI*2);x.fill();
    x.fillStyle="#c4dbe4";x.font="12px system-ui";x.fillText(p.name,pp.x+10,pp.y-7);
  });

  const a=+($("#axis")?.value||data.hypothetical_experiment.semi_major_axis_au);
  const hr=132+((a-.04)/.18)*78,ha=phase*.52+1.2;
  x.setLineDash([6,7]);x.strokeStyle="rgba(196,163,255,.36)";
  x.beginPath();x.ellipse(apos.x,apos.y,hr,hr*.42,0,0,Math.PI*2);x.stroke();x.setLineDash([]);
  const hp={x:apos.x+hr*Math.cos(ha),y:apos.y+hr*.42*Math.sin(ha)};
  const hg=x.createRadialGradient(hp.x,hp.y,0,hp.x,hp.y,24);
  hg.addColorStop(0,"rgba(206,178,255,.8)");hg.addColorStop(1,"rgba(206,178,255,0)");
  x.fillStyle=hg;x.beginPath();x.arc(hp.x,hp.y,24,0,Math.PI*2);x.fill();
  x.fillStyle="#caa9ff";x.beginPath();x.arc(hp.x,hp.y,7,0,Math.PI*2);x.fill();
  x.fillStyle="#e4d6ff";x.font="600 12px system-ui";x.fillText("H-01",hp.x+11,hp.y-8);
}

function drawStar(x,p,r,label,color,s){
  const g=x.createRadialGradient(p.x,p.y,0,p.x,p.y,r*3.5);
  g.addColorStop(0,color);g.addColorStop(.28,color);g.addColorStop(1,"rgba(255,95,80,0)");
  x.fillStyle=g;x.beginPath();x.arc(p.x,p.y,r*3.5,0,Math.PI*2);x.fill();
  x.fillStyle=color;x.beginPath();x.arc(p.x,p.y,r,0,Math.PI*2);x.fill();
  x.fillStyle="#fff";x.font="800 13px system-ui";x.fillText(label,p.x-4,p.y+4);
  if(document.body.dataset.mode==="scientific"){
    x.fillStyle="#9fb3bd";x.font="11px system-ui";
    x.fillText(fmt(s.mass_solar,3)+" M☉",p.x-r,p.y+r+18);
  }
}

function loop(){
  if(running)phase+=.014;
  draw();
  requestAnimationFrame(loop);
}

$("#pauseBtn").addEventListener("click",()=>{
  running=!running;
  $("#pauseBtn").textContent=running?"Pausar":"Continuar";
});

load().catch(err=>{
  console.error(err);
  $("#syncBadge").className="sourcePill speculative";
  $("#syncBadge").textContent="ERROR DE DATOS";
  $("#storyPlanetsText").textContent="No fue posible cargar el dataset. Revisa el workflow de actualización científica.";
});
