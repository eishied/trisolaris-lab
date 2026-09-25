const DATA_URL="./data/ltt1445.json";
let data=null;
let running=true;
let phase=0;
let candidateInitialized=false;
let hitTargets=[];
let selectedFocus=null;

const $=s=>document.querySelector(s);
const $$=s=>[...document.querySelectorAll(s)];
const fmt=(v,d=2)=>v==null||Number.isNaN(Number(v))?"—":Number(v).toFixed(d);
const stat=(label,value,note="")=>`<div class="stat"><small>${label}</small><strong>${value}</strong>${note?`<em>${note}</em>`:""}</div>`;
const focusFact=(label,value)=>`<div class="focusFact"><span>${label}</span><strong>${value}</strong></div>`;

function setMode(mode){
  document.body.dataset.mode=mode;
  $$(".modeBtn").forEach(btn=>btn.classList.toggle("active",btn.dataset.mode===mode));
  localStorage.setItem("trisolaris-detail-mode",mode);
  draw();
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
  const s=data.system;
  const rows=data.observed_planets||[];

  $("#heroSystem").textContent=s.name;
  $("#heroDistance").textContent=fmt(s.distance_pc*3.26156,1)+" años luz";
  $("#heroPlanetCount").textContent=String(rows.length);
  $("#heroDataState").textContent=official?"NASA sincronizado":"Snapshot base";

  $("#syncBadge").textContent=official
    ?"NASA Exoplanet Archive · sincronizado"
    :"Esperando sincronización oficial";

  $("#systemStats").innerHTML=
    stat("Sistema",s.name)+
    stat("Distancia",fmt(s.distance_pc,2)+" pc","≈ "+fmt(s.distance_pc*3.26156,1)+" años luz")+
    stat("Arquitectura",s.architecture)+
    stat("Componentes estelares",data.stars.length)+
    stat("Período exterior",fmt(data.hierarchy?.outer_period_years_approx,0)+" años","aprox. literatura")+
    stat("Período B–C",fmt(data.hierarchy?.bc_period_years_approx,0)+" años","aprox. literatura");

  $("#dataNote").innerHTML=official
    ?"<b>Procedencia activa.</b> Los planetas visibles se generaron desde la consulta TAP almacenada para NASA Exoplanet Archive. La arquitectura triple usa valores de literatura y debe seguir refinándose con Gaia y soluciones orbitales posteriores."
    :"<b>Snapshot de arranque.</b> La arquitectura triple está sustentada en literatura; esta copia todavía no contiene la última actualización de planetas observados.";

  renderPlanets();
  initCandidate();
}

function planetPlainLanguage(p){
  const teq=p.equilibrium_temperature_k;
  const c=teq==null?null:teq-273.15;
  let thermal="La temperatura de equilibrio no está disponible en este registro.";
  if(c!=null){
    if(c>180) thermal="Recibe una cantidad de energía extrema para condiciones terrestres.";
    else if(c>80) thermal="Es un mundo muy caliente bajo una estimación térmica simple.";
    else if(c>25) thermal="Su equilibrio térmico es cálido; una atmósfera real puede modificarlo bastante.";
    else if(c>-25) thermal="Su equilibrio térmico cae en un rango relativamente templado o frío.";
    else thermal="Es frío bajo esta aproximación; la atmósfera sería decisiva.";
  }

  let scale="Su tamaño todavía no está bien definido.";
  if(p.radius_earth!=null){
    scale=p.radius_earth<1.25
      ?"Su radio es cercano al terrestre."
      :p.radius_earth<1.6
        ?"Es algo mayor que la Tierra, todavía dentro del régimen de mundos pequeños."
        :"Su radio supera claramente al terrestre.";
  }
  return thermal+" "+scale;
}

function focusKey(target){
  return target.kind==="star" ? "star:"+target.id
    : target.kind==="planet" ? "planet:"+target.name
      : "hypothetical:H-01";
}

function focusContent(target){
  if(target.kind==="star"){
    const s=data.stars.find(x=>x.id===target.id);
    const isA=target.id==="A";
    return {
      kicker:isA?"ESTRELLA ANFITRIONA":"ESTRELLA COMPAÑERA",
      name:s.name,
      narrative:isA
        ?"Es la estrella alrededor de la cual orbitan los dos planetas confirmados del sistema. Para cualquier mundo cercano a A, su luz domina el presupuesto energético."
        :"Forma parte de la pareja B–C. Aunque está mucho más lejos de los planetas conocidos que A, su gravedad y radiación pertenecen al entorno completo que TRISOLARIS debe modelar.",
      facts:[
        ["Masa",fmt(s.mass_solar,3)+" M☉"],
        ["Radio",fmt(s.radius_solar,3)+" R☉"],
        ["Luminosidad",fmt(s.luminosity_solar,5)+" L☉"],
        ["Evidencia","Literatura científica"]
      ],
      science:"Nivel epistemológico: LITERATURE. Estos valores no deben confundirse con una solución orbital completa del sistema triple. La siguiente fase añadirá refinamiento astrométrico y dinámica N-body."
    };
  }

  if(target.kind==="planet"){
    const p=data.observed_planets.find(x=>x.name===target.name);
    return {
      kicker:"PLANETA CONFIRMADO",
      name:p.name,
      narrative:planetPlainLanguage(p)+" Este objeto sí pertenece al inventario observado; cualquier escenario de habitabilidad humana es una pregunta distinta.",
      facts:[
        ["Órbita",fmt(p.period_days,2)+" días"],
        ["Radio",fmt(p.radius_earth,2)+" R⊕"],
        ["Masa",fmt(p.mass_earth,2)+" M⊕"],
        ["Teq",p.equilibrium_temperature_k==null?"—":fmt(p.equilibrium_temperature_k,0)+" K"]
      ],
      science:`Nivel epistemológico: OBSERVED. Semieje mayor ${fmt(p.semi_major_axis_au,4)} AU · excentricidad ${p.eccentricity==null?"sin valor por defecto":fmt(p.eccentricity,3)} · fuente: NASA Exoplanet Archive / ps.`
    };
  }

  const h=data.hypothetical_experiment;
  return {
    kicker:"MUNDO EXPERIMENTAL",
    name:"TRISOLARIS H-01",
    narrative:"Este mundo existe únicamente dentro del laboratorio de TRISOLARIS. Sirve para preguntar qué condiciones podría necesitar un planeta antes de someterlo a pruebas orbitales y climáticas más exigentes.",
    facts:[
      ["Distancia actual",(+$("#axis").value).toFixed(3)+" AU"],
      ["Albedo",(+$("#albedo").value).toFixed(2)],
      ["Invernadero","+"+(+$("#greenhouse").value).toFixed(0)+" K"],
      ["Evidencia","Hipótesis"]
    ],
    science:`Nivel epistemológico: SPECULATIVE. Configuración base del catálogo: a=${fmt(h.semi_major_axis_au,3)} AU, albedo=${fmt(h.albedo,2)}, greenhouse=${fmt(h.greenhouse_k,0)} K. Aún no existe una prueba N-body de estabilidad.`
  };
}

function openFocus(target,{scroll=true}={}){
  selectedFocus=target;
  const content=focusContent(target);
  $("#focusKicker").textContent=content.kicker;
  $("#focusName").textContent=content.name;
  $("#focusNarrative").textContent=content.narrative;
  $("#focusFacts").innerHTML=content.facts.map(([a,b])=>focusFact(a,b)).join("");
  $("#focusScience").textContent=content.science;
  $("#objectFocus").hidden=false;
  $(".systemVisual").classList.add("isFocused");
  const hint=$(".canvasHint");
  if(hint) hint.remove();
  if(scroll){
    $("#sistema").scrollIntoView({behavior:"smooth",block:"start"});
  }
}

function closeFocus(){
  selectedFocus=null;
  $("#objectFocus").hidden=true;
  $(".systemVisual").classList.remove("isFocused");
}

function activateWorldFocus(){
  $(".world[data-focus-name]").forEach(card=>{
    const activate=()=>{
      openFocus({kind:"planet",name:card.dataset.focusName});
    };
    card.addEventListener("click",activate);
    card.addEventListener("keydown",event=>{
      if(event.key==="Enter"||event.key===" "){
        event.preventDefault();
        activate();
      }
    });
  });
}

function installCanvasFocus(){
  const canvas=$("#systemCanvas");
  const visual=canvas.closest(".systemVisual");
  if(!visual.querySelector(".canvasHint")){
    const hint=document.createElement("div");
    hint.className="canvasHint";
    hint.textContent="Toca una estrella o mundo";
    visual.appendChild(hint);
  }

  canvas.addEventListener("click",event=>{
    if(!hitTargets.length)return;
    const rect=canvas.getBoundingClientRect();
    const px=(event.clientX-rect.left)*(canvas.width/rect.width);
    const py=(event.clientY-rect.top)*(canvas.height/rect.height);
    const hits=hitTargets
      .map(t=>({...t,d:Math.hypot(px-t.x,py-t.y)}))
      .filter(t=>t.d<=t.hitRadius)
      .sort((a,b)=>a.d-b.d);
    if(hits[0]) openFocus(hits[0].target,{scroll:false});
  });

  $("#focusClose").addEventListener("click",closeFocus);
}

function renderPlanets(){
  const rows=data.observed_planets||[];
  $("#planetCount").textContent=rows.length+" planeta"+(rows.length===1?"":"s")+" confirmado"+(rows.length===1?"":"s");

  if(!rows.length){
    $("#planetCards").innerHTML=`
      <article class="world">
        <div class="worldBody">
          <span class="worldKicker">Sin datos planetarios</span>
          <h3>Esperando el archivo oficial</h3>
          <p>La estructura de la página permanece disponible, pero esta copia todavía no contiene planetas observados.</p>
        </div>
      </article>`;
    $("#planetTable").innerHTML='<div class="methodNote">No hay filas observadas disponibles en esta copia del dataset.</div>';
    return;
  }

  $("#planetCards").innerHTML=rows.map((p,i)=>`
    <article class="world reveal" data-focus-name="${p.name}" tabindex="0" role="button" aria-label="Explorar ${p.name} en el sistema">
      <div class="worldHero" aria-hidden="true"><div class="worldSphere"></div></div>
      <div class="worldBody">
        <span class="worldKicker">Planeta confirmado · NASA</span>
        <h3>${p.name}</h3>
        <p>${planetPlainLanguage(p)}</p>
        <div class="worldFacts">
          <span>${fmt(p.period_days,2)} días por órbita</span>
          <span>${fmt(p.radius_earth,2)} R⊕</span>
          <span>desc. ${p.discovery_year==null?"—":Math.round(p.discovery_year)}</span>
        </div>
        <div class="worldExplore">Entrar al mundo <span>↗</span></div>
      </div>
    </article>
  `).join("");

  $("#planetTable").innerHTML=`<table><thead><tr>
    <th>Planeta</th><th>Período</th><th>Semieje mayor</th><th>Radio</th><th>Masa</th><th>Teq</th><th>Descubrimiento</th><th>Procedencia</th>
  </tr></thead><tbody>${rows.map(p=>`<tr>
    <td><b>${p.name}</b></td>
    <td>${fmt(p.period_days,3)} d</td>
    <td>${fmt(p.semi_major_axis_au,4)} AU</td>
    <td>${fmt(p.radius_earth,2)} R⊕</td>
    <td>${fmt(p.mass_earth,2)} M⊕</td>
    <td>${p.equilibrium_temperature_k==null?"—":fmt(p.equilibrium_temperature_k,0)+" K"}</td>
    <td>${p.discovery_year==null?"—":Math.round(p.discovery_year)}</td>
    <td>OBSERVED · NASA</td>
  </tr>`).join("")}</tbody></table>`;

  activateRevealObserver();
  activateWorldFocus();
}

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
  if(score>.78){
    return {
      title:"Vale la pena investigarlo",
      text:`Con estas suposiciones, H-01 cae cerca de una ventana térmica interesante. El proxy superficial es de ${fmt(celsius,1)} °C.`,
      confidence:"Señal favorable en un modelo rápido; todavía requiere dinámica orbital y clima.",
      tone:"good"
    };
  }
  if(score>.52){
    return {
      title:"Es un escenario marginal",
      text:"Pequeños cambios en atmósfera, agua o actividad estelar podrían mover el resultado hacia condiciones mejores o peores.",
      confidence:"Incertidumbre alta: este escenario sirve para explorar, no para concluir.",
      tone:"mid"
    };
  }
  return {
    title:"Bajo estas condiciones sería hostil",
    text:"La combinación actual queda lejos de una ventana térmica sencilla para habitabilidad terrestre.",
    confidence:"Resultado exploratorio. Cambia los controles para examinar otra configuración.",
    tone:"low"
  };
}

function renderCandidate(){
  if(!data)return;
  const a=+$("#axis").value;
  const albedo=+$("#albedo").value;
  const gh=+$("#greenhouse").value;

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
  const proxy=0.56*liquid+0.44*fluxScore;
  const reading=candidateLabel(proxy,celsius);

  $("#habitScore").textContent=Math.round(proxy*100)+"%";
  $("#candidateHeadline").textContent=reading.title;
  $("#candidatePlain").textContent=reading.text;
  $("#confidenceSentence").textContent=reading.confidence;

  const orb=$("#habitOrb");
  const schemes={
    good:[
      "radial-gradient(circle at 34% 28%,#8aefc5 0,#2b755a 42%,#0a1915 74%)",
      "0 0 80px rgba(73,197,149,.24), inset -22px -28px 36px rgba(0,0,0,.36)"
    ],
    mid:[
      "radial-gradient(circle at 34% 28%,#f1cc77 0,#79612f 42%,#211a0c 74%)",
      "0 0 80px rgba(225,179,82,.20), inset -22px -28px 36px rgba(0,0,0,.36)"
    ],
    low:[
      "radial-gradient(circle at 34% 28%,#e5938d 0,#763e3c 42%,#20100f 74%)",
      "0 0 80px rgba(211,103,96,.18), inset -22px -28px 36px rgba(0,0,0,.36)"
    ]
  };
  orb.style.background=schemes[reading.tone][0];
  orb.style.boxShadow=schemes[reading.tone][1];

  $("#candidateStats").innerHTML=
    stat("Flujo combinado",fmt(flux,3)+" S⊕","A aporta "+fmt(100*fluxA/flux,1)+"%")+
    stat("Temperatura de equilibrio",fmt(teq,1)+" K")+
    stat("Proxy superficial",fmt(surface,1)+" K",fmt(celsius,1)+" °C")+
    stat("Proxy de agua líquida",Math.round(liquid*100)+"%","heurística")+
    stat("Proxy de habitabilidad",Math.round(proxy*100)+"%","DERIVED · no GCM");

  $("#candidateWhy").innerHTML=
    "<b>Cadena de cálculo.</b> Luminosidad y distancia → flujo recibido → corrección por albedo → temperatura de equilibrio → calentamiento atmosférico simplificado → proxy de habitabilidad. "
    +"No incluye estabilidad N-body, escape atmosférico, actividad de llamaradas, circulación climática 3D, hidrología ni biosfera.";

  if(selectedFocus?.kind==="hypothetical"){
    openFocus(selectedFocus,{scroll:false});
  }
}

function draw(){
  if(!data)return;

  const c=$("#systemCanvas");
  const x=c.getContext("2d");
  const w=c.width;
  const h=c.height;
  x.clearRect(0,0,w,h);

  const cx=w*.47;
  const cy=h*.46;
  x.fillStyle="#020609";
  x.fillRect(0,0,w,h);

  const field=x.createRadialGradient(cx,cy,20,cx,cy,w*.64);
  field.addColorStop(0,"rgba(22,43,58,.44)");
  field.addColorStop(.45,"rgba(7,18,25,.20)");
  field.addColorStop(1,"rgba(2,6,9,0)");
  x.fillStyle=field;
  x.fillRect(0,0,w,h);

  for(let i=0;i<180;i++){
    const px=(i*137.1)%w;
    const py=(i*83.7)%h;
    const a=.09+((i*17)%48)/100;
    x.fillStyle=`rgba(215,237,248,${a})`;
    const s=i%13===0?1.7:1;
    x.fillRect(px,py,s,s);
  }

  const A=data.stars.find(s=>s.id==="A");
  const B=data.stars.find(s=>s.id==="B");
  const C=data.stars.find(s=>s.id==="C");

  const outerR=Math.min(w*.29,345);
  const bcCenter={
    x:cx+outerR*Math.cos(phase*.11),
    y:cy+outerR*.48*Math.sin(phase*.11)
  };
  const bcR=62;
  const apos={x:cx-160,y:cy};
  const bpos={
    x:bcCenter.x+bcR*Math.cos(phase*.65),
    y:bcCenter.y+bcR*.48*Math.sin(phase*.65)
  };
  const cpos={
    x:bcCenter.x-bcR*Math.cos(phase*.65),
    y:bcCenter.y-bcR*.48*Math.sin(phase*.65)
  };

  x.strokeStyle="rgba(128,177,203,.145)";
  x.lineWidth=1.1;
  x.beginPath();
  x.ellipse(cx+65,cy,outerR,outerR*.48,0,0,Math.PI*2);
  x.stroke();
  x.beginPath();
  x.ellipse(bcCenter.x,bcCenter.y,bcR,bcR*.48,0,0,Math.PI*2);
  x.stroke();

  hitTargets=[
    {x:apos.x,y:apos.y,hitRadius:58,target:{kind:"star",id:"A"}},
    {x:bpos.x,y:bpos.y,hitRadius:48,target:{kind:"star",id:"B"}},
    {x:cpos.x,y:cpos.y,hitRadius:46,target:{kind:"star",id:"C"}}
  ];

  drawStar(x,apos,30,"A","#ef8174",A);
  drawStar(x,bpos,22,"B","#e67770",B);
  drawStar(x,cpos,19,"C","#cf676d",C);

  const planets=data.observed_planets||[];
  planets.slice(0,5).forEach((p,i)=>{
    const r=66+i*34;
    const ang=phase*(1.45/(i+1))+(i*1.4);
    x.strokeStyle="rgba(112,210,255,.115)";
    x.beginPath();
    x.ellipse(apos.x,apos.y,r,r*.42,0,0,Math.PI*2);
    x.stroke();

    const pp={
      x:apos.x+r*Math.cos(ang),
      y:apos.y+r*.42*Math.sin(ang)
    };
    x.fillStyle="#79d4ef";
    x.beginPath();
    x.arc(pp.x,pp.y,5.3,0,Math.PI*2);
    x.fill();

    hitTargets.push({
      x:pp.x,y:pp.y,hitRadius:26,
      target:{kind:"planet",name:p.name}
    });

    if(document.body.dataset.mode==="scientific"){
      x.fillStyle="#bfd5df";
      x.font="11px system-ui";
      x.fillText(p.name,pp.x+10,pp.y-7);
    }
  });

  const a=+($("#axis")?.value||data.hypothetical_experiment.semi_major_axis_au);
  const hr=140+((a-.04)/.18)*82;
  const ha=phase*.52+1.2;
  x.setLineDash([6,8]);
  x.strokeStyle="rgba(196,163,255,.31)";
  x.beginPath();
  x.ellipse(apos.x,apos.y,hr,hr*.42,0,0,Math.PI*2);
  x.stroke();
  x.setLineDash([]);

  const hp={
    x:apos.x+hr*Math.cos(ha),
    y:apos.y+hr*.42*Math.sin(ha)
  };
  const hg=x.createRadialGradient(hp.x,hp.y,0,hp.x,hp.y,28);
  hg.addColorStop(0,"rgba(206,178,255,.78)");
  hg.addColorStop(1,"rgba(206,178,255,0)");
  x.fillStyle=hg;
  x.beginPath();
  x.arc(hp.x,hp.y,28,0,Math.PI*2);
  x.fill();
  x.fillStyle="#caa9ff";
  x.beginPath();
  x.arc(hp.x,hp.y,7,0,Math.PI*2);
  x.fill();

  hitTargets.push({
    x:hp.x,y:hp.y,hitRadius:30,
    target:{kind:"hypothetical",name:"H-01"}
  });

  if(selectedFocus){
    const key=focusKey(selectedFocus);
    const selected=hitTargets.find(t=>focusKey(t.target)===key);
    if(selected){
      x.save();
      x.strokeStyle=selectedFocus.kind==="hypothetical"?"rgba(206,178,255,.82)":"rgba(142,224,255,.78)";
      x.lineWidth=1.6;
      x.setLineDash([5,6]);
      x.beginPath();
      x.arc(selected.x,selected.y,selectedFocus.kind==="star"?44:22,0,Math.PI*2);
      x.stroke();
      x.setLineDash([]);
      x.restore();
    }
  }

  if(document.body.dataset.mode==="scientific"){
    x.fillStyle="#e4d6ff";
    x.font="600 11px system-ui";
    x.fillText("H-01 · HYPOTHETICAL",hp.x+12,hp.y-8);
  }
}

function drawStar(x,p,r,label,color,s){
  const g=x.createRadialGradient(p.x,p.y,0,p.x,p.y,r*3.6);
  g.addColorStop(0,color);
  g.addColorStop(.27,color);
  g.addColorStop(1,"rgba(255,95,80,0)");
  x.fillStyle=g;
  x.beginPath();
  x.arc(p.x,p.y,r*3.6,0,Math.PI*2);
  x.fill();

  x.fillStyle=color;
  x.beginPath();
  x.arc(p.x,p.y,r,0,Math.PI*2);
  x.fill();

  x.fillStyle="#fff";
  x.font="800 13px system-ui";
  x.fillText(label,p.x-4,p.y+4);

  if(document.body.dataset.mode==="scientific"){
    x.fillStyle="#91a5af";
    x.font="10px system-ui";
    x.fillText(fmt(s.mass_solar,3)+" M☉",p.x-r,p.y+r+17);
  }
}

function loop(){
  if(running)phase+=.014;
  draw();
  requestAnimationFrame(loop);
}

installCanvasFocus();

$("#pauseBtn").addEventListener("click",()=>{
  running=!running;
  $("#pauseBtn").textContent=running?"Pausar":"Continuar";
});

function activateRevealObserver(){
  const items=$$(".reveal:not([data-observed])");
  if(!items.length)return;

  const observer=new IntersectionObserver(entries=>{
    entries.forEach(entry=>{
      if(entry.isIntersecting){
        entry.target.classList.add("in");
        observer.unobserve(entry.target);
      }
    });
  },{threshold:.12});

  items.forEach(item=>{
    item.dataset.observed="1";
    observer.observe(item);
  });
}

$$(".chapter").forEach(el=>el.classList.add("reveal"));
activateRevealObserver();

const logo=$(".noodboxLogo");
if(logo){
  logo.addEventListener("error",()=>logo.style.display="none");
}

load().catch(err=>{
  console.error(err);
  $("#heroDataState").textContent="Error de datos";
  $("#syncBadge").textContent="No fue posible cargar el dataset";
  $("#planetCards").innerHTML='<article class="world"><div class="worldBody"><h3>No se pudo cargar el archivo científico</h3><p>Revisa la actualización automática del repositorio.</p></div></article>';
});
