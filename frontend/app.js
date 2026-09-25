const DATA_URL="./data/ltt1445.json";
const NBODY_URL="./data/nbody-ensemble.json";
const BUNDLED_DATA={"generated_at":"2026-09-25T14:43:37.731510+00:00","status":"official-nasa-plus-literature","system":{"id":"LTT-1445-ABC","name":"LTT 1445 ABC","architecture":"hierarchical triple M-dwarf system","distance_pc":6.86,"epistemic_level":"LITERATURE","notes":"LTT 1445 A is orbited at large separation by the tighter B-C pair. Known planets orbit A."},"stars":[{"id":"A","name":"LTT 1445 A","mass_solar":0.257,"radius_solar":0.268,"luminosity_solar":0.00794,"epistemic_level":"LITERATURE"},{"id":"B","name":"LTT 1445 B","mass_solar":0.215,"radius_solar":0.236,"luminosity_solar":0.00596,"epistemic_level":"LITERATURE"},{"id":"C","name":"LTT 1445 C","mass_solar":0.161,"radius_solar":0.197,"luminosity_solar":0.00368,"epistemic_level":"LITERATURE"}],"hierarchy":{"outer_projected_separation_arcsec_approx":7,"outer_period_years_approx":250,"bc_projected_separation_arcsec_approx":1,"bc_period_years_approx":36,"epistemic_level":"LITERATURE"},"observed_planets":[{"name":"LTT 1445 A c","host":"LTT 1445 A","period_days":3.1239035,"semi_major_axis_au":0.02661,"eccentricity":0.223,"radius_earth":1.147,"mass_earth":1.54,"equilibrium_temperature_k":508,"discovery_year":2022,"epistemic_level":"OBSERVED","source":"NASA Exoplanet Archive / ps"},{"name":"LTT 1445 A b","host":"LTT 1445 A","period_days":5.3587635,"semi_major_axis_au":0.0381,"eccentricity":null,"radius_earth":1.34,"mass_earth":2.73,"equilibrium_temperature_k":431,"discovery_year":2019,"epistemic_level":"OBSERVED","source":"NASA Exoplanet Archive / ps"}],"hypothetical_experiment":{"id":"H-01","name":"TRISOLARIS H-01","host":"LTT 1445 A","semi_major_axis_au":0.09,"albedo":0.3,"greenhouse_k":33,"epistemic_level":"SPECULATIVE","notes":"Interactive test world only. Its orbit is not asserted to be stable; future REBOUND ensembles must evaluate stability against observed planets and stellar companions."},"literature":[{"title":"Three Red Suns in the Sky: A Transiting, Terrestrial Planet in a Triple M Dwarf System at 6.9 Parsecs","arxiv":"1906.10147","doi":"10.3847/1538-3881/ab364d"},{"title":"A Second Planet Transiting LTT 1445A and a Determination of the Masses of Both Worlds","arxiv":"2107.14737"}],"provenance":{"nasa_query":"select hostname,pl_name,default_flag,pl_orbper,pl_orbsmax,pl_orbeccen,\n       pl_rade,pl_bmasse,pl_eqt,st_teff,st_rad,st_mass,sy_dist,disc_year\nfrom ps\nwhere hostname='LTT 1445 A' and default_flag=1","nasa_endpoint":"https://exoplanetarchive.ipac.caltech.edu/TAP/sync","observed_planet_count":2,"epistemic_rule":"NASA planet rows are OBSERVED; triple-star properties are LITERATURE; H-01 is SPECULATIVE."}};
let nbodyResult=null;
let data=null;
let running=true;
let phase=0;
let candidateInitialized=false;
let orbitScanInitialized=false;
let lifeSeeded=localStorage.getItem("trisolaris-life-seeded")==="true";
let humanSeeded=localStorage.getItem("trisolaris-human-seeded")==="true";
let hitTargets=[];
let selectedFocus=null;

const $=s=>document.querySelector(s);
const $$=s=>[...document.querySelectorAll(s)];
const fmt=(v,d=2)=>v==null||Number.isNaN(Number(v))?"—":Number(v).toFixed(d);
const stat=(label,value,note="")=>`<div class="stat"><small>${label}</small><strong>${value}</strong>${note?`<em>${note}</em>`:""}</div>`;
const focusFact=(label,value)=>`<div class="focusFact"><span>${label}</span><strong>${value}</strong></div>`;
const EARTH_MASS_IN_SOLAR=3.0034896e-6;
const HILL_THRESHOLD=2*Math.sqrt(3);

function setMode(mode){
  document.body.dataset.mode=mode;
  $$(".modeBtn").forEach(btn=>btn.classList.toggle("active",btn.dataset.mode===mode));
  localStorage.setItem("trisolaris-detail-mode",mode);
  draw();
}

$$(".modeBtn").forEach(btn=>btn.addEventListener("click",()=>setMode(btn.dataset.mode)));
setMode(localStorage.getItem("trisolaris-detail-mode")||"simple");

async function load(){
  let runtimeSource="official-file";
  try{
    const response=await fetch(DATA_URL+"?v=phase5-20260925",{cache:"no-store"});
    if(!response.ok) throw new Error("No se pudo cargar el dataset científico");
    data=await response.json();
  }catch(err){
    console.warn("TRISOLARIS external dataset unavailable; using bundled snapshot",err);
    data=JSON.parse(JSON.stringify(BUNDLED_DATA));
    runtimeSource="bundled-snapshot";
  }

  data._runtime_source=runtimeSource;

  try{
    renderAll();
    requestAnimationFrame(loop);
    loadNbodyResult();
  }catch(err){
    console.error("TRISOLARIS interface render failed",err);
    $("#heroDataState").textContent="Error de interfaz";
    $("#syncBadge").textContent="Los datos están disponibles, pero una vista no pudo renderizarse";
  }
}

async function loadNbodyResult(){
  const headline=$("#nbodyHeadline");
  const summary=$("#nbodySummary");
  if(!headline||!summary)return;

  try{
    const response=await fetch(NBODY_URL+"?v=phase5-20260925",{cache:"no-store"});
    if(!response.ok) throw new Error("N-body result not published yet");
    nbodyResult=await response.json();
    renderNbodyResult(nbodyResult);
  }catch(err){
    console.info("Pilot N-body result not available yet",err);
    headline.textContent="El motor N-body está preparado";
    summary.textContent="El experimento numérico se publicará automáticamente cuando termine la primera corrida reproducible en GitHub Actions.";
    const meta=$("#nbodyMeta");
    if(meta) meta.textContent="Pendiente de primera corrida · el filtro Hill sigue disponible en vivo";
  }
}

function renderNbodyResult(result){
  const outcomes=result?.outcomes||{};
  const ensemble=result?.ensemble||{};
  const survived=outcomes.survived_pilot_interval??0;
  const total=ensemble.runs??0;
  const fraction=outcomes.survival_fraction;

  $("#nbodyHeadline").textContent=total
    ? `${survived} de ${total} escenarios sobrevivieron el intervalo piloto`
    : "Resultado N-body disponible";

  $("#nbodySummary").textContent=
    "REBOUND integró la estrella A, los planetas confirmados, H-01 y una aproximación del baricentro B+C. Sobrevivir este intervalo no significa estabilidad a largo plazo.";

  const meta=$("#nbodyMeta");
  if(meta){
    meta.textContent=`${ensemble.integration_years_per_run??"—"} años por corrida · ${result.engine??"REBOUND"} · supervivencia ${fraction==null?"—":Math.round(fraction*100)+"%"}`;
  }

  const detail=$("#nbodyDetail");
  if(detail){
    detail.innerHTML=
      stat("Corridas",total)+
      stat("Sobreviven piloto",survived)+
      stat("No sobreviven",outcomes.did_not_survive_pilot_interval??"—")+
      stat("e máx. H-01",fmt(outcomes.maximum_eccentricity_seen,3))+
      stat("Deriva a máx.",outcomes.maximum_semimajor_drift_fraction_seen==null?"—":fmt(outcomes.maximum_semimajor_drift_fraction_seen*100,2)+"%");
  }
}

function renderAll(){
  const official=data.status==="official-nasa-plus-literature";
  const s=data.system;
  const rows=data.observed_planets||[];

  $("#heroSystem").textContent=s.name;
  $("#heroDistance").textContent=fmt(s.distance_pc*3.26156,1)+" años luz";
  $("#heroPlanetCount").textContent=String(rows.length);
  $("#heroDataState").textContent=data._runtime_source==="bundled-snapshot"?"Snapshot integrado":(official?"NASA sincronizado":"Snapshot base");

  $("#syncBadge").textContent=data._runtime_source==="bundled-snapshot"
    ?"Snapshot científico integrado · modo resiliente"
    :(official?"NASA Exoplanet Archive · sincronizado":"Esperando sincronización oficial");

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

function orbitalScreen(candidateA,candidateMassEarth=1){
  const host=data?.stars?.find(s=>s.id==="A");
  if(!host||!candidateA) return {
    periodDays:null,minDelta:null,state:"unknown",
    label:"sin datos suficientes",
    simple:"Todavía no hay datos suficientes para un filtro orbital preliminar."
  };

  const periodDays=365.25*Math.sqrt(
    candidateA**3/(host.mass_solar+candidateMassEarth*EARTH_MASS_IN_SOLAR)
  );

  const pairwise=(data.observed_planets||[])
    .filter(p=>p.semi_major_axis_au!=null&&p.mass_earth!=null)
    .map(p=>{
      const meanA=(candidateA+p.semi_major_axis_au)/2;
      const massRatio=((candidateMassEarth+p.mass_earth)*EARTH_MASS_IN_SOLAR)/(3*host.mass_solar);
      const mutualHill=Math.cbrt(massRatio)*meanA;
      const delta=mutualHill>0?Math.abs(candidateA-p.semi_major_axis_au)/mutualHill:Infinity;
      return {name:p.name,delta};
    });

  const minDelta=pairwise.length?Math.min(...pairwise.map(p=>p.delta)):null;

  if(minDelta==null) return {
    periodDays,minDelta,state:"unknown",
    label:"sin comparación",
    simple:"Podemos estimar el período, pero faltan masas u órbitas comparables para el filtro Hill."
  };

  if(minDelta<HILL_THRESHOLD) return {
    periodDays,minDelta,state:"fail",
    label:"demasiado apretada",
    simple:"Esta posición queda demasiado cerca de una órbita conocida para pasar el filtro analítico preliminar."
  };

  if(minDelta<8) return {
    periodDays,minDelta,state:"caution",
    label:"pasa con cautela",
    simple:"Pasa el umbral analítico simple, pero la separación sigue siendo suficientemente estrecha como para exigir una integración N-body."
  };

  return {
    periodDays,minDelta,state:"pass",
    label:"bien separada",
    simple:"Está bien separada de los planetas confirmados en el filtro analítico. Aun así, esto no demuestra estabilidad a largo plazo."
  };
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
  const orbital=orbitalScreen(+$("#axis").value,1);
  return {
    kicker:"MUNDO EXPERIMENTAL",
    name:"TRISOLARIS H-01",
    narrative:"Este mundo existe únicamente dentro del laboratorio de TRISOLARIS. Sirve para preguntar qué condiciones podría necesitar un planeta antes de someterlo a pruebas orbitales y climáticas más exigentes.",
    facts:[
      ["Distancia actual",(+$("#axis").value).toFixed(3)+" AU"],
      ["Albedo",(+$("#albedo").value).toFixed(2)],
      ["Invernadero","+"+(+$("#greenhouse").value).toFixed(0)+" K"],
      ["Presión",(+$("#pressure").value).toFixed(2)+" bar"],
      ["Agua",(+$("#water").value).toFixed(2)+" océanos"],
      ["Filtro orbital",orbital.label],
      ["Evidencia","Hipótesis"]
    ],
    science:`Nivel epistemológico: SPECULATIVE. Configuración base del catálogo: a=${fmt(h.semi_major_axis_au,3)} AU, albedo=${fmt(h.albedo,2)}, greenhouse=${fmt(h.greenhouse_k,0)} K. Filtro Hill actual: Δmín=${orbital.minDelta==null?"—":fmt(orbital.minDelta,2)}; umbral analítico 2√3=${fmt(HILL_THRESHOLD,2)}. Esto sigue sin ser una prueba N-body de estabilidad.`
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
  $$(".world[data-focus-name]").forEach(card=>{
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
    if(!$("#pressure").value) $("#pressure").value="1.00";
    if(!$("#water").value) $("#water").value="1.00";
    ["axis","albedo","greenhouse","pressure","water","oxygen","nutrients"].forEach(id=>$("#"+id).addEventListener("input",renderCandidate));
    const seedBtn=$("#seedLifeBtn");
    seedBtn.setAttribute("aria-pressed",String(lifeSeeded));
    seedBtn.textContent=lifeSeeded?"Biosfera experimental activa":"Biosfera no asumida";
    seedBtn.addEventListener("click",()=>{
      lifeSeeded=!lifeSeeded;
      localStorage.setItem("trisolaris-life-seeded",String(lifeSeeded));
      seedBtn.setAttribute("aria-pressed",String(lifeSeeded));
      seedBtn.textContent=lifeSeeded?"Biosfera experimental activa":"Biosfera no asumida";
      renderCandidate();
    });
    $("#seedLifeBtn").setAttribute("aria-pressed",String(lifeSeeded));
    $("#seedLifeBtn").textContent=lifeSeeded?"Biosfera experimental activa":"Biosfera no asumida";
    $("#seedHumansBtn").setAttribute("aria-pressed",String(humanSeeded));
    $("#seedHumansBtn").textContent=humanSeeded?"Población experimental activa":"Población no introducida";
    initOrbitWindow();
    candidateInitialized=true;
  }
  renderCandidate();
}

function evaluateOrbitPoint(a,albedo,gh){
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
  return {fluxA,fluxBC,flux,teq,surface,celsius,liquid,fluxScore,proxy,orbital:orbitalScreen(a,1)};
}

function renderOrbitWindow(){
  const canvas=$("#orbitScanCanvas");
  if(!canvas||!data)return;
  const ctx=canvas.getContext("2d");
  const w=canvas.width;
  const h=canvas.height;
  const minA=0.04;
  const maxA=0.22;
  const albedo=+$("#albedo").value;
  const gh=+$("#greenhouse").value;
  const currentA=+$("#axis").value;

  ctx.clearRect(0,0,w,h);
  const bg=ctx.createLinearGradient(0,0,w,0);
  bg.addColorStop(0,"rgba(255,255,255,.015)");
  bg.addColorStop(1,"rgba(255,255,255,.035)");
  ctx.fillStyle=bg;
  ctx.fillRect(0,0,w,h);

  const samples=180;
  const stepW=w/samples;
  const candidateFlags=[];

  for(let i=0;i<samples;i++){
    const a=minA+(maxA-minA)*(i/(samples-1));
    const e=evaluateOrbitPoint(a,albedo,gh);
    let fill="rgba(92,112,124,.28)";
    if(e.orbital.state==="fail") fill="rgba(224,104,100,.48)";
    else if(e.proxy>=.76) fill="rgba(91,205,151,.62)";
    else if(e.proxy>=.55) fill="rgba(221,178,86,.48)";
    else if(e.proxy>=.35) fill="rgba(93,155,188,.40)";
    ctx.fillStyle=fill;
    ctx.fillRect(i*stepW,24,Math.ceil(stepW)+1,h-60);
    candidateFlags.push(e.orbital.state!=="fail"&&e.proxy>=.76);
  }

  // Current H-01 position.
  const x=(currentA-minA)/(maxA-minA)*w;
  ctx.strokeStyle="rgba(245,247,249,.92)";
  ctx.lineWidth=2;
  ctx.beginPath();
  ctx.moveTo(x,10);
  ctx.lineTo(x,h-18);
  ctx.stroke();

  ctx.fillStyle="rgba(245,247,249,.96)";
  ctx.beginPath();
  ctx.arc(x,18,6,0,Math.PI*2);
  ctx.fill();

  ctx.font="600 18px system-ui";
  ctx.fillStyle="rgba(239,244,247,.92)";
  ctx.fillText("H-01",Math.min(w-58,x+10),19);

  ctx.font="13px system-ui";
  ctx.fillStyle="rgba(170,183,191,.86)";
  ctx.fillText("más energía",14,h-14);
  const label="menos energía";
  const m=ctx.measureText(label);
  ctx.fillText(label,w-m.width-14,h-14);

  // Longest contiguous high-interest interval.
  let bestStart=-1,bestEnd=-1,runStart=-1;
  for(let i=0;i<=candidateFlags.length;i++){
    const on=i<candidateFlags.length&&candidateFlags[i];
    if(on&&runStart<0) runStart=i;
    if(!on&&runStart>=0){
      const end=i-1;
      if(bestStart<0||(end-runStart)>(bestEnd-bestStart)){
        bestStart=runStart;
        bestEnd=end;
      }
      runStart=-1;
    }
  }

  const labelNode=$("#orbitBestWindow");
  if(labelNode){
    if(bestStart>=0){
      const a0=minA+(maxA-minA)*(bestStart/(samples-1));
      const a1=minA+(maxA-minA)*(bestEnd/(samples-1));
      labelNode.textContent=`Ventana de interés actual · ${a0.toFixed(3)}–${a1.toFixed(3)} AU`;
    }else{
      labelNode.textContent="No aparece una ventana fuerte con los supuestos actuales";
    }
  }
}

function initOrbitWindow(){
  if(orbitScanInitialized)return;
  const canvas=$("#orbitScanCanvas");
  if(!canvas)return;
  canvas.addEventListener("click",event=>{
    const rect=canvas.getBoundingClientRect();
    const ratio=Math.max(0,Math.min(1,(event.clientX-rect.left)/rect.width));
    const a=0.04+ratio*(0.22-0.04);
    $("#axis").value=a.toFixed(3);
    renderCandidate();
  });
  orbitScanInitialized=true;
}

function solveClimateBands(stellarFluxEarth,albedo,greenhouseK,bands=36){
  const SOLAR=1361;
  const A=210;
  const B=2;
  const D=0.55;
  const S2=-0.482;
  const referenceGreenhouse=33;
  const lats=[];
  const targets=[];
  const absorbed=[];
  const greenhouseDelta=greenhouseK-referenceGreenhouse;

  const p2=x=>0.5*(3*x*x-1);
  for(let i=0;i<bands;i++){
    const lat=-90+(i+0.5)*(180/bands);
    const phi=lat*Math.PI/180;
    const shape=Math.max(.10,1+S2*p2(Math.sin(phi)));
    const incoming=(SOLAR/4)*stellarFluxEarth*shape;
    const abs=incoming*(1-albedo);
    lats.push(lat);
    absorbed.push(abs);
    targets.push((abs-A)/B+greenhouseDelta);
  }

  let temps=targets.slice();
  const mixing=D/B;
  for(let iter=0;iter<900;iter++){
    const next=temps.slice();
    for(let i=0;i<bands;i++){
      const south=i>0?temps[i-1]:temps[i];
      const north=i<bands-1?temps[i+1]:temps[i];
      const neighbor=.5*(south+north);
      const equilibrium=targets[i]+mixing*(neighbor-temps[i]);
      next[i]=temps[i]+.08*(equilibrium-temps[i]);
    }
    temps=next;
  }

  const rows=[];
  let weightSum=0;
  let mean=0;
  let windowWeight=0;
  for(let i=0;i<bands;i++){
    const weight=Math.max(0,Math.cos(lats[i]*Math.PI/180));
    weightSum+=weight;
    mean+=temps[i]*weight;
    if(temps[i]>=0&&temps[i]<=40)windowWeight+=weight;

    let state="temperate";
    if(temps[i]<-30)state="deep-freeze";
    else if(temps[i]<0)state="cold";
    else if(temps[i]>50)state="extreme-hot";
    else if(temps[i]>30)state="hot";

    rows.push({
      latitudeDeg:lats[i],
      temperatureC:temps[i],
      temperatureK:temps[i]+273.15,
      absorbedFluxWm2:absorbed[i],
      state
    });
  }

  const values=rows.map(r=>r.temperatureC);
  return {
    rows,
    summary:{
      globalMeanC:mean/(weightSum||1),
      minC:Math.min(...values),
      maxC:Math.max(...values),
      contrastK:Math.max(...values)-Math.min(...values),
      thermalWindowFraction:windowWeight/(weightSum||1)
    }
  };
}

function climateColor(tempC){
  if(tempC<-30)return "#7895aa";
  if(tempC<0)return "#7ab6d1";
  if(tempC<15)return "#58bfa6";
  if(tempC<30)return "#8bcf8a";
  if(tempC<45)return "#d5b66f";
  return "#d07b68";
}

function renderClimateWorld(){
  const canvas=$("#climateCanvas");
  if(!canvas||!data)return;

  const a=+$("#axis").value;
  const albedo=+$("#albedo").value;
  const gh=+$("#greenhouse").value;
  const point=evaluateOrbitPoint(a,albedo,gh);
  const climate=solveClimateBands(point.flux,albedo,gh,36);

  const ctx=canvas.getContext("2d");
  const w=canvas.width,h=canvas.height;
  ctx.clearRect(0,0,w,h);
  ctx.fillStyle="#070c11";
  ctx.fillRect(0,0,w,h);

  const cx=315,cy=h/2,r=165;

  // Ambient glow.
  const glow=ctx.createRadialGradient(cx,cy,30,cx,cy,r*1.7);
  glow.addColorStop(0,"rgba(99,178,208,.13)");
  glow.addColorStop(1,"rgba(0,0,0,0)");
  ctx.fillStyle=glow;
  ctx.beginPath();
  ctx.arc(cx,cy,r*1.7,0,Math.PI*2);
  ctx.fill();

  ctx.save();
  ctx.beginPath();
  ctx.arc(cx,cy,r,0,Math.PI*2);
  ctx.clip();

  // Latitude bands projected onto a disc.
  for(let y=Math.floor(cy-r);y<=Math.ceil(cy+r);y++){
    const normalized=(cy-y)/r;
    if(Math.abs(normalized)>1)continue;
    const lat=Math.asin(normalized)*180/Math.PI;
    const row=climate.rows.reduce((best,item)=>
      Math.abs(item.latitudeDeg-lat)<Math.abs(best.latitudeDeg-lat)?item:best
    );
    ctx.fillStyle=climateColor(row.temperatureC);
    const halfWidth=Math.sqrt(Math.max(0,r*r-(y-cy)*(y-cy)));
    ctx.fillRect(cx-halfWidth,y,halfWidth*2,2);
  }

  // Stylized land masses: visual context only.
  ctx.fillStyle="rgba(20,40,35,.32)";
  ctx.beginPath();
  ctx.moveTo(cx-95,cy-58);
  ctx.bezierCurveTo(cx-40,cy-100,cx+20,cy-75,cx+45,cy-28);
  ctx.bezierCurveTo(cx+70,cy+3,cx+35,cy+30,cx-15,cy+18);
  ctx.bezierCurveTo(cx-55,cy+10,cx-85,cy-10,cx-95,cy-58);
  ctx.fill();
  ctx.beginPath();
  ctx.moveTo(cx+45,cy+45);
  ctx.bezierCurveTo(cx+100,cy+20,cx+122,cy+72,cx+72,cy+108);
  ctx.bezierCurveTo(cx+30,cy+123,cx+10,cy+75,cx+45,cy+45);
  ctx.fill();

  // Soft atmospheric rim.
  const rim=ctx.createRadialGradient(cx,cy,r*.78,cx,cy,r);
  rim.addColorStop(0,"rgba(255,255,255,0)");
  rim.addColorStop(1,"rgba(192,229,244,.20)");
  ctx.fillStyle=rim;
  ctx.fillRect(cx-r,cy-r,r*2,r*2);

  ctx.restore();

  ctx.strokeStyle="rgba(220,239,247,.28)";
  ctx.lineWidth=1;
  ctx.beginPath();
  ctx.arc(cx,cy,r,0,Math.PI*2);
  ctx.stroke();

  // Narrative metrics to the right of the globe.
  const eq=climate.rows.reduce((best,item)=>
    Math.abs(item.latitudeDeg)<Math.abs(best.latitudeDeg)?item:best
  );
  const north=climate.rows[climate.rows.length-1];
  const south=climate.rows[0];
  const summary=climate.summary;

  ctx.fillStyle="rgba(244,247,249,.94)";
  ctx.font="700 26px system-ui";
  ctx.fillText("Clima por latitud",570,98);
  ctx.fillStyle="rgba(157,171,181,.92)";
  ctx.font="15px system-ui";
  ctx.fillText("Mismo planeta. Regiones térmicas diferentes.",570,127);

  const metrics=[
    ["Ecuador",eq.temperatureC],
    ["Polo norte",north.temperatureC],
    ["Polo sur",south.temperatureC],
    ["Media global",summary.globalMeanC]
  ];
  metrics.forEach((m,i)=>{
    const y=180+i*48;
    ctx.fillStyle="rgba(123,139,149,.92)";
    ctx.font="12px system-ui";
    ctx.fillText(m[0],570,y);
    ctx.fillStyle="rgba(236,242,245,.96)";
    ctx.font="700 20px system-ui";
    ctx.fillText(`${m[1].toFixed(1)} °C`,760,y);
  });

  const fraction=Math.round(summary.thermalWindowFraction*100);
  $("#climateHeadline").textContent=fraction>55
    ?"Aparece una franja térmica amplia"
    :fraction>20
      ?"La habitabilidad térmica se concentra en refugios"
      :"Las regiones térmicamente favorables son escasas";

  $("#climateText").textContent=
    `${fraction}% del área latitudinal cae entre 0 y 40 °C en este modelo anual simplificado. La diferencia entre las bandas más cálida y más fría es de ${summary.contrastK.toFixed(1)} K.`;

  $("#climateMetrics").innerHTML=
    stat("Media global",summary.globalMeanC.toFixed(1)+" °C","área ponderada")+
    stat("Banda más fría",summary.minC.toFixed(1)+" °C")+
    stat("Banda más cálida",summary.maxC.toFixed(1)+" °C")+
    stat("Contraste latitudinal",summary.contrastK.toFixed(1)+" K")+
    stat("Ventana térmica",fraction+"%","0–40 °C · proxy");
}

function boilingPointCApprox(pressureBar){
  const p=Math.max(.05,Math.min(5,pressureBar));
  return Math.max(45,Math.min(150,100+25*Math.log10(p)));
}

function temperatureProductivity(tempC){
  if(tempC<=-10||tempC>=50)return 0;
  if(tempC<=22)return Math.max(0,Math.min(1,(tempC+10)/32));
  return Math.max(0,Math.min(1,(50-tempC)/28));
}

function solveSurfaceSystems(climate,{pressureBar=1,waterOceans=1,stellarFluxEarth=1,spectralFactor=.55}={}){
  const boilingC=boilingPointCApprox(pressureBar);
  const waterFactor=1-Math.exp(-2.2*Math.max(0,waterOceans));
  const pressureCycleFactor=Math.max(0,Math.min(1,pressureBar/.7));
  const usableLightFactor=Math.max(0,Math.min(1,spectralFactor*Math.sqrt(Math.max(0,stellarFluxEarth))));

  let totalWeight=0;
  let liquidWeight=0;
  let iceWeight=0;
  let vaporWeight=0;
  let productivityWeight=0;
  let refugiaWeight=0;

  const rows=climate.rows.map(row=>{
    const lat=row.latitudeDeg;
    const tempC=row.temperatureC;
    const weight=Math.max(0,Math.cos(lat*Math.PI/180));
    totalWeight+=weight;

    let waterState="dry";
    let liquid=0,ice=0,vapor=0;

    if(waterOceans>.001){
      if(tempC<0){
        waterState="ice-dominated";
        ice=waterFactor;
        liquid=Math.max(0,waterFactor*(1-Math.min(1,Math.abs(tempC)/35))*.15);
      }else if(tempC<boilingC){
        waterState="liquid-permitted";
        liquid=waterFactor;
        vapor=waterFactor*Math.max(0,Math.min(1,(tempC-20)/Math.max(1,boilingC-20)))*.35;
      }else{
        waterState="vapor-stressed";
        vapor=waterFactor;
        liquid=waterFactor*.05;
      }
    }

    let hydroCycle=waterFactor*pressureCycleFactor;
    if(tempC>=0&&tempC<boilingC){
      hydroCycle*=.45+.55*Math.max(0,Math.min(1,(tempC+5)/35));
    }else{
      hydroCycle*=.2;
    }

    const productivity=
      temperatureProductivity(tempC)*
      Math.max(0,Math.min(1,liquid))*
      hydroCycle*
      usableLightFactor;

    const refugium=(tempC>=0&&tempC<=40&&liquid>.25&&pressureBar>=.2);

    liquidWeight+=weight*Math.max(0,Math.min(1,liquid));
    iceWeight+=weight*ice;
    vaporWeight+=weight*vapor;
    productivityWeight+=weight*productivity;
    if(refugium)refugiaWeight+=weight;

    return {
      latitudeDeg:lat,
      temperatureC:tempC,
      waterState,
      liquidWaterProxy:Math.max(0,Math.min(1,liquid)),
      iceProxy:ice,
      vaporStressProxy:vapor,
      hydrologicalCycleProxy:hydroCycle,
      productivityPotential:productivity,
      refugium
    };
  });

  totalWeight=totalWeight||1;
  const globalMean=climate.summary.globalMeanC;
  const thermalEscapeStress=Math.max(0,Math.min(1,(globalMean+20)/180));
  const retentionProxy=Math.max(0,Math.min(1,.72+.16*Math.log10(Math.max(.05,pressureBar))-.35*thermalEscapeStress));
  const bio=productivityWeight/totalWeight;
  const refugia=refugiaWeight/totalWeight;

  let biosphereState="little surface biosphere potential under current assumptions";
  if(bio>=.45&&refugia>=.5) biosphereState="broad primary-productivity potential";
  else if(bio>=.15&&refugia>=.15) biosphereState="regional biosphere potential";
  else if(refugia>0) biosphereState="limited thermal-hydrological refugia";

  return {
    rows,
    summary:{
      boilingC,
      liquidArea:liquidWeight/totalWeight,
      iceArea:iceWeight/totalWeight,
      vaporStressArea:vaporWeight/totalWeight,
      hydroCycle:waterFactor*pressureCycleFactor,
      retentionProxy,
      biospherePotential:bio,
      refugiaFraction:refugia,
      biosphereState
    }
  };
}

function surfaceBandColor(row){
  if(row.waterState==="ice-dominated")return "rgba(126,177,205,.92)";
  if(row.waterState==="vapor-stressed")return "rgba(187,119,89,.92)";
  if(row.productivityPotential>.35)return "rgba(93,170,111,.92)";
  if(row.liquidWaterProxy>.35)return "rgba(76,142,169,.94)";
  return "rgba(104,112,119,.80)";
}

function renderSurfaceWorld(){
  const canvas=$("#surfaceCanvas");
  if(!canvas||!data)return;

  const a=+$("#axis").value;
  const albedo=+$("#albedo").value;
  const gh=+$("#greenhouse").value;
  const pressure=+$("#pressure").value;
  const water=+$("#water").value;
  const point=evaluateOrbitPoint(a,albedo,gh);
  const climate=solveClimateBands(point.flux,albedo,gh,36);
  const surface=solveSurfaceSystems(climate,{
    pressureBar:pressure,
    waterOceans:water,
    stellarFluxEarth:point.flux,
    spectralFactor:.55
  });

  $("#pressureOut").textContent=pressure.toFixed(2)+" bar";
  $("#waterOut").textContent=water.toFixed(2)+" océanos";

  const s=surface.summary;
  const liquidPct=Math.round(s.liquidArea*100);
  const icePct=Math.round(s.iceArea*100);
  const refugiaPct=Math.round(s.refugiaFraction*100);
  const bioPct=Math.round(s.biospherePotential*100);
  const retainPct=Math.round(s.retentionProxy*100);

  $("#atmoNarrative").textContent=retainPct>=70
    ?`La atmósfera mantiene una retención preliminar favorable (${retainPct}%), aunque todavía falta química y escape atmosférico real.`
    :`La atmósfera aparece frágil en este filtro (${retainPct}% de retención proxy); conviene estudiar escape y composición.`;

  $("#waterNarrative").textContent=water<=.01
    ?"El escenario está prácticamente seco."
    :liquidPct>=45
      ?`El agua líquida es térmicamente permisible en una fracción amplia del planeta (${liquidPct}%).`
      :icePct>=50
        ?`Predomina el almacenamiento en hielo; las regiones líquidas quedan restringidas (${liquidPct}%).`
        :`El agua líquida aparece de forma regional (${liquidPct}%), con estrés por hielo o evaporación en otras latitudes.`;

  $("#bioNarrative").textContent=refugiaPct>=50
    ?`Las condiciones permiten refugios térmico-hidrológicos extensos (${refugiaPct}% del área latitudinal), con potencial de productividad de ${bioPct}%.`
    :refugiaPct>0
      ?`La biosfera potencial se concentraría en refugios (${refugiaPct}% del área latitudinal); fuera de ellos las condiciones son mucho más restrictivas.`
      :"No aparecen refugios superficiales robustos bajo estos supuestos.";

  const ctx=canvas.getContext("2d");
  const w=canvas.width,h=canvas.height;
  ctx.clearRect(0,0,w,h);
  ctx.fillStyle="#060b0f";
  ctx.fillRect(0,0,w,h);

  // Planet disc.
  const cx=300,cy=h/2,r=174;
  const glow=ctx.createRadialGradient(cx,cy,40,cx,cy,r*1.7);
  glow.addColorStop(0,"rgba(79,157,178,.13)");
  glow.addColorStop(1,"rgba(0,0,0,0)");
  ctx.fillStyle=glow;
  ctx.beginPath();ctx.arc(cx,cy,r*1.7,0,Math.PI*2);ctx.fill();

  ctx.save();
  ctx.beginPath();ctx.arc(cx,cy,r,0,Math.PI*2);ctx.clip();

  for(let y=Math.floor(cy-r);y<=Math.ceil(cy+r);y++){
    const norm=(cy-y)/r;
    if(Math.abs(norm)>1)continue;
    const lat=Math.asin(norm)*180/Math.PI;
    const row=surface.rows.reduce((best,item)=>
      Math.abs(item.latitudeDeg-lat)<Math.abs(best.latitudeDeg-lat)?item:best
    );
    ctx.fillStyle=surfaceBandColor(row);
    const half=Math.sqrt(Math.max(0,r*r-(y-cy)*(y-cy)));
    ctx.fillRect(cx-half,y,half*2,2);
  }

  // Land silhouettes.
  ctx.fillStyle="rgba(32,44,35,.42)";
  ctx.beginPath();
  ctx.moveTo(cx-110,cy-44);
  ctx.bezierCurveTo(cx-72,cy-102,cx-15,cy-91,cx+28,cy-52);
  ctx.bezierCurveTo(cx+58,cy-18,cx+30,cy+10,cx-20,cy+5);
  ctx.bezierCurveTo(cx-70,cy,cx-105,cy-10,cx-110,cy-44);
  ctx.fill();
  ctx.beginPath();
  ctx.moveTo(cx+45,cy+38);
  ctx.bezierCurveTo(cx+105,cy+18,cx+132,cy+72,cx+80,cy+112);
  ctx.bezierCurveTo(cx+40,cy+132,cx+12,cy+79,cx+45,cy+38);
  ctx.fill();

  // Atmosphere rim intensity varies with pressure.
  const rimAlpha=Math.max(.05,Math.min(.32,.08+pressure*.07));
  const rim=ctx.createRadialGradient(cx,cy,r*.76,cx,cy,r);
  rim.addColorStop(0,"rgba(255,255,255,0)");
  rim.addColorStop(1,`rgba(188,226,242,${rimAlpha})`);
  ctx.fillStyle=rim;ctx.fillRect(cx-r,cy-r,r*2,r*2);
  ctx.restore();

  ctx.strokeStyle="rgba(219,239,247,.25)";
  ctx.lineWidth=1;
  ctx.beginPath();ctx.arc(cx,cy,r,0,Math.PI*2);ctx.stroke();

  // Latitudinal surface profile.
  const left=570,right=w-55,top=86,bottom=h-72;
  ctx.strokeStyle="rgba(255,255,255,.08)";
  ctx.beginPath();ctx.moveTo(left,bottom);ctx.lineTo(right,bottom);ctx.stroke();

  const barW=(right-left)/surface.rows.length;
  surface.rows.forEach((row,i)=>{
    const x=left+i*barW;
    const height=Math.max(4,row.productivityPotential*(bottom-top));
    ctx.fillStyle=surfaceBandColor(row);
    ctx.fillRect(x,bottom-height,Math.ceil(barW)+1,height);
  });

  ctx.fillStyle="rgba(242,246,248,.94)";
  ctx.font="700 25px system-ui";
  ctx.fillText("Superficie viva — potencial",left,48);
  ctx.fillStyle="rgba(148,163,173,.9)";
  ctx.font="14px system-ui";
  ctx.fillText("Altura = productividad potencial por latitud",left,72);

  ctx.font="12px system-ui";
  ctx.fillStyle="rgba(119,134,144,.92)";
  ctx.fillText("90°S",left,bottom+26);
  ctx.fillText("Ecuador",(left+right)/2-24,bottom+26);
  ctx.fillText("90°N",right-34,bottom+26);

  $("#surfaceMetrics").innerHTML=
    stat("Presión",pressure.toFixed(2)+" bar")+
    stat("Ebullición H₂O",s.boilingC.toFixed(1)+" °C","aprox.")+
    stat("Agua líquida proxy",liquidPct+"%","área ponderada")+
    stat("Hielo proxy",icePct+"%","área ponderada")+
    stat("Retención atmosférica",retainPct+"%","screening")+
    stat("Refugios",refugiaPct+"%","térmico-hidrológicos")+
    stat("Productividad potencial",bioPct+"%","MODELED · no vida observada");
}

function oxygenSupport(oxygenFraction,midpoint,width){
  const x=(oxygenFraction-midpoint)/Math.max(width,1e-6);
  return 1/(1+Math.exp(-x));
}

function evaluateFoodWeb(surface,{oxygenFraction=.21,nutrientAvailability=1,seeded=false}={}){
  const clamp=v=>Math.max(0,Math.min(1,v));
  const s=surface.summary;
  const liquid=clamp(s.liquidArea);
  const productivity=clamp(s.biospherePotential);
  const refugia=clamp(s.refugiaFraction);
  const retention=clamp(s.retentionProxy);
  const hydro=clamp(s.hydroCycle);
  const nutrient=clamp(1-Math.exp(-Math.max(0,nutrientAvailability)));

  const anaerobic=clamp(.20+.35*refugia+.20*liquid+.15*retention+.10*nutrient);
  const photo=clamp(productivity*(.55+.45*nutrient)*(.55+.45*hydro));
  const aquaticPrimary=clamp(liquid*productivity*(.50+.50*nutrient));
  const decomposers=clamp(Math.sqrt(Math.max(0,photo*Math.max(.05,hydro)))*(.55+.45*nutrient));
  const aerobicMicrobes=clamp(anaerobic*oxygenSupport(oxygenFraction,.005,.004)*(.65+.35*retention));
  const grazers=clamp(photo*oxygenSupport(oxygenFraction,.025,.015)*(.60+.40*refugia));
  const aquaticConsumers=clamp(aquaticPrimary*oxygenSupport(oxygenFraction,.02,.012)*(.55+.45*liquid));
  const predators=clamp(Math.max(grazers,aquaticConsumers)*productivity*oxygenSupport(oxygenFraction,.10,.035));
  const largeAerobic=clamp(predators*oxygenSupport(oxygenFraction,.16,.025)*(.55+.45*retention));

  const guilds=[
    {id:"anaerobic_microbes",name:"Microbios anaerobios",level:0,support:anaerobic},
    {id:"aerobic_microbes",name:"Microbios aerobios",level:0,support:aerobicMicrobes},
    {id:"primary_producers",name:"Productores primarios",level:1,support:photo},
    {id:"aquatic_primary",name:"Productores acuáticos",level:1,support:aquaticPrimary},
    {id:"decomposers",name:"Descomponedores",level:1,support:decomposers},
    {id:"grazers",name:"Consumidores primarios",level:2,support:grazers},
    {id:"aquatic_consumers",name:"Consumidores acuáticos",level:2,support:aquaticConsumers},
    {id:"predators",name:"Depredadores",level:3,support:predators},
    {id:"large_aerobic",name:"Fauna aerobia grande",level:4,support:largeAerobic}
  ];

  let depth=-1;
  if(largeAerobic>=.35)depth=4;
  else if(predators>=.25)depth=3;
  else if(Math.max(grazers,aquaticConsumers)>=.25)depth=2;
  else if(Math.max(photo,aquaticPrimary,decomposers)>=.20)depth=1;
  else if(anaerobic>=.15)depth=0;

  const links=[
    ["primary_producers","grazers"],
    ["aquatic_primary","aquatic_consumers"],
    ["grazers","predators"],
    ["aquatic_consumers","predators"],
    ["predators","decomposers"],
    ["grazers","decomposers"],
    ["primary_producers","decomposers"]
  ];

  return {
    guilds,links,
    summary:{
      depth,
      supported:guilds.filter(g=>g.support>=.25),
      maxSupport:Math.max(...guilds.map(g=>g.support),0),
      seeded
    }
  };
}

function renderFoodWeb(){
  const canvas=$("#foodWebCanvas");
  if(!canvas||!data)return;

  const a=+$("#axis").value;
  const albedo=+$("#albedo").value;
  const gh=+$("#greenhouse").value;
  const pressure=+$("#pressure").value;
  const water=+$("#water").value;
  const oxygen=(+$("#oxygen").value)/100;
  const nutrients=+$("#nutrients").value;

  $("#oxygenOut").textContent=(oxygen*100).toFixed(1)+"%";
  $("#nutrientOut").textContent=nutrients.toFixed(2)+"×";

  const point=evaluateOrbitPoint(a,albedo,gh);
  const climate=solveClimateBands(point.flux,albedo,gh,36);
  const surface=solveSurfaceSystems(climate,{
    pressureBar:pressure,
    waterOceans:water,
    stellarFluxEarth:point.flux,
    spectralFactor:.55
  });
  const web=evaluateFoodWeb(surface,{
    oxygenFraction:oxygen,
    nutrientAvailability:nutrients,
    seeded:lifeSeeded
  });

  const supported=web.summary.supported;
  const depth=web.summary.depth;

  $("#ecologyHeadline").textContent=depth>=3
    ?"La energía alcanza niveles tróficos superiores"
    :depth>=1
      ?"La red potencial se sostiene cerca de la base"
      :depth===0
        ?"Solo aparece soporte microbiano robusto"
        :"La red ecológica superficial queda muy limitada";

  $("#ecologyText").textContent=lifeSeeded
    ?`La biosfera experimental está activa. Bajo estos supuestos, ${supported.length} de 9 gremios superan 25% de soporte ambiental.`
    :`El ambiente podría dar soporte significativo a ${supported.length} de 9 gremios, pero TRISOLARIS no asume que la vida haya surgido.`;

  $("#ecologyState").textContent=lifeSeeded
    ?"Biosfera experimental sembrada — escenario hipotético."
    :"Capacidad ambiental solamente — la vida no se asume.";

  $("#ecologyDetail").textContent=depth>=4
    ?"El ambiente permite explorar una cadena potencial desde productores hasta fauna aerobia grande. Esto no predice especies."
    :depth>=3
      ?"Existe soporte potencial para productores, consumidores y depredadores, pero la complejidad sigue condicionada por energía, oxígeno y agua."
      :depth>=1
        ?"La base productiva existe, pero los niveles consumidores superiores siguen restringidos."
        :"La energía ecológica disponible es demasiado limitada para construir una red trófica extensa.";

  const ctx=canvas.getContext("2d");
  const w=canvas.width,h=canvas.height;
  ctx.clearRect(0,0,w,h);
  ctx.fillStyle="#060b0f";
  ctx.fillRect(0,0,w,h);

  const positions={
    anaerobic_microbes:[125,130],
    aerobic_microbes:[125,360],
    primary_producers:[360,95],
    aquatic_primary:[360,250],
    decomposers:[360,405],
    grazers:[630,130],
    aquatic_consumers:[630,350],
    predators:[885,240],
    large_aerobic:[1080,240]
  };

  const guildMap=Object.fromEntries(web.guilds.map(g=>[g.id,g]));

  // links
  web.links.forEach(([source,target])=>{
    const s=guildMap[source],t=guildMap[target];
    const [x1,y1]=positions[source];
    const [x2,y2]=positions[target];
    const strength=Math.min(s.support,t.support);
    ctx.strokeStyle=lifeSeeded
      ?`rgba(118,183,143,${.10+.55*strength})`
      :`rgba(132,151,160,${.08+.28*strength})`;
    ctx.lineWidth=1+4*strength;
    ctx.beginPath();
    ctx.moveTo(x1,y1);
    const mx=(x1+x2)/2;
    ctx.bezierCurveTo(mx,y1,mx,y2,x2,y2);
    ctx.stroke();
  });

  // nodes
  web.guilds.forEach(g=>{
    const [x,y]=positions[g.id];
    const radius=20+28*g.support;
    const strong=g.support>=.25;
    const fill=strong
      ?(lifeSeeded?"rgba(88,165,112,.88)":"rgba(79,128,104,.52)")
      :"rgba(86,98,106,.38)";

    const glow=ctx.createRadialGradient(x,y,0,x,y,radius*2.1);
    glow.addColorStop(0,strong?"rgba(91,190,126,.16)":"rgba(120,135,145,.08)");
    glow.addColorStop(1,"rgba(0,0,0,0)");
    ctx.fillStyle=glow;
    ctx.beginPath();ctx.arc(x,y,radius*2.1,0,Math.PI*2);ctx.fill();

    ctx.fillStyle=fill;
    ctx.beginPath();ctx.arc(x,y,radius,0,Math.PI*2);ctx.fill();
    ctx.strokeStyle=strong?"rgba(183,224,197,.55)":"rgba(159,172,179,.24)";
    ctx.lineWidth=1;
    ctx.stroke();

    ctx.fillStyle="rgba(238,243,246,.94)";
    ctx.font="700 13px system-ui";
    ctx.textAlign="center";
    ctx.fillText(g.name,x,y+radius+22);

    ctx.fillStyle="rgba(153,168,177,.94)";
    ctx.font="12px system-ui";
    ctx.fillText(Math.round(g.support*100)+"%",x,y+5);
  });
  ctx.textAlign="left";

  ctx.fillStyle="rgba(129,143,152,.9)";
  ctx.font="11px system-ui";
  ctx.fillText("Base metabólica",60,30);
  ctx.fillText("Productores / reciclaje",290,30);
  ctx.fillText("Consumidores",595,30);
  ctx.fillText("Depredación",835,30);
  ctx.fillText("Alta demanda",1030,30);

  const maxPct=Math.round(web.summary.maxSupport*100);
  $("#ecologyMetrics").innerHTML=
    stat("Oxígeno", (oxygen*100).toFixed(1)+"%","supuesto")+
    stat("Nutrientes",nutrients.toFixed(2)+"×","control relativo")+
    stat("Gremios >25%",supported.length+" / 9")+
    stat("Profundidad trófica",depth<0?"—":"nivel "+depth,"potencial")+
    stat("Soporte máximo",maxPct+"%","MODELED")+
    stat("Estado de vida",lifeSeeded?"sembrada":"no asumida","SPECULATIVE");
}

function humanBell(value,center,width){
  return Math.exp(-.5*Math.pow((value-center)/Math.max(width,1e-6),2));
}

function humanOxygenSupport(partialPressureBar){
  if(partialPressureBar<=0)return 0;
  const low=1/(1+Math.exp(-(partialPressureBar-.13)/.025));
  const high=1/(1+Math.exp((partialPressureBar-.34)/.04));
  return Math.max(0,Math.min(1,low*high));
}

function humanPressureSupport(pressureBar){
  if(pressureBar<=0)return 0;
  const low=1/(1+Math.exp(-(pressureBar-.45)/.12));
  const high=1/(1+Math.exp((pressureBar-2.6)/.45));
  return Math.max(0,Math.min(1,low*high));
}

function evaluateSettlementSupport(surface,foodWeb,{pressureBar=1,oxygenFraction=.21,technologySupport=.4,nutrients=1}={}){
  const clamp=v=>Math.max(0,Math.min(1,v));
  const tech=clamp(technologySupport);
  const pO2=pressureBar*oxygenFraction;
  const oxygen=humanOxygenSupport(pO2);
  const pressure=humanPressureSupport(pressureBar);

  let producer=0,consumer=0;
  foodWeb.guilds.forEach(g=>{
    if(["primary_producers","aquatic_primary"].includes(g.id))producer=Math.max(producer,g.support);
    if(["grazers","aquatic_consumers"].includes(g.id))consumer=Math.max(consumer,g.support);
  });
  const nutrientFactor=clamp(1-Math.exp(-Math.max(0,nutrients)));
  const environmentalFood=clamp(.72*producer+.18*consumer+.10*nutrientFactor);

  const techBuffer=(base,ceiling)=>clamp(base+tech*(ceiling-base));
  let totalWeight=0,naturalSum=0,assistedSum=0,agricultureSum=0,viableWeight=0,naturalViableWeight=0;

  const bands=surface.rows.map(row=>{
    const lat=row.latitudeDeg;
    const tempC=row.temperatureC;
    const water=clamp(row.liquidWaterProxy);
    const hydro=clamp(row.hydrologicalCycleProxy);
    const productivity=clamp(row.productivityPotential);
    const weight=Math.max(0,Math.cos(lat*Math.PI/180));
    totalWeight+=weight;

    const thermal=clamp(humanBell(tempC,18,18));
    const naturalFood=clamp(.55*productivity+.30*environmentalFood+.15*hydro);

    const natural=Math.pow(
      Math.max(1e-6,thermal)*
      Math.max(1e-6,oxygen)*
      Math.max(1e-6,pressure)*
      Math.max(1e-6,water)*
      Math.max(1e-6,naturalFood),
      .2
    );

    const thermalA=techBuffer(thermal,.93);
    const oxygenA=techBuffer(oxygen,.90);
    const pressureA=techBuffer(pressure,.90);
    const waterA=techBuffer(water,.92);
    const foodA=techBuffer(naturalFood,.88);

    const assisted=Math.pow(
      Math.max(1e-6,thermalA)*
      Math.max(1e-6,oxygenA)*
      Math.max(1e-6,pressureA)*
      Math.max(1e-6,waterA)*
      Math.max(1e-6,foodA),
      .2
    );

    const agriculture=clamp(productivity*waterA*(.55+.45*nutrientFactor)*(.65+.35*thermalA));
    const dependency=clamp(assisted-natural);

    naturalSum+=weight*natural;
    assistedSum+=weight*assisted;
    agricultureSum+=weight*agriculture;
    if(assisted>=.50)viableWeight+=weight;
    if(natural>=.60)naturalViableWeight+=weight;

    return {
      latitudeDeg:lat,
      temperatureC:tempC,
      naturalSupport:natural,
      assistedSupport:assisted,
      technologyDependency:dependency,
      agriculturePotential:agriculture,
      stress:{
        thermal:1-thermal,
        oxygen:1-oxygen,
        pressure:1-pressure,
        water:1-water,
        food:1-naturalFood
      }
    };
  });

  totalWeight=totalWeight||1;
  const naturalMean=naturalSum/totalWeight;
  const assistedMean=assistedSum/totalWeight;
  const viableFraction=viableWeight/totalWeight;
  const naturalViableFraction=naturalViableWeight/totalWeight;

  let state="little settlement potential under current assumptions";
  if(naturalViableFraction>=.45)state="broad natural settlement potential";
  else if(viableFraction>=.45)state="broad technology-assisted settlement potential";
  else if(viableFraction>=.12)state="regional refugia with technology dependence";

  return {
    bands,
    summary:{
      naturalMean,
      assistedMean,
      dependencyMean:Math.max(0,assistedMean-naturalMean),
      agricultureMean:agricultureSum/totalWeight,
      viableFraction,
      naturalViableFraction,
      state,
      pO2
    }
  };
}

function renderSettlementWorld(){
  const canvas=$("#settlementCanvas");
  if(!canvas||!data)return;

  const a=+$("#axis").value;
  const albedo=+$("#albedo").value;
  const gh=+$("#greenhouse").value;
  const pressure=+$("#pressure").value;
  const water=+$("#water").value;
  const oxygen=(+$("#oxygen").value)/100;
  const nutrients=+$("#nutrients").value;
  const tech=(+$("#techSupport").value)/100;

  $("#techSupportOut").textContent=Math.round(tech*100)+"%";

  const point=evaluateOrbitPoint(a,albedo,gh);
  const climate=solveClimateBands(point.flux,albedo,gh,36);
  const surface=solveSurfaceSystems(climate,{
    pressureBar:pressure,
    waterOceans:water,
    stellarFluxEarth:point.flux,
    spectralFactor:.55
  });
  const web=evaluateFoodWeb(surface,{
    oxygenFraction:oxygen,
    nutrientAvailability:nutrients,
    seeded:lifeSeeded
  });
  const settlement=evaluateSettlementSupport(surface,web,{
    pressureBar:pressure,
    oxygenFraction:oxygen,
    technologySupport:tech,
    nutrients
  });

  const s=settlement.summary;
  const naturalPct=Math.round(s.naturalMean*100);
  const assistedPct=Math.round(s.assistedMean*100);
  const viablePct=Math.round(s.viableFraction*100);
  const naturalAreaPct=Math.round(s.naturalViableFraction*100);
  const depPct=Math.round(s.dependencyMean*100);
  const agPct=Math.round(s.agricultureMean*100);

  $("#settlementHeadline").textContent=s.naturalViableFraction>=.45
    ?"El planeta ofrece regiones naturalmente compatibles"
    :s.viableFraction>=.45
      ?"La población dependería de infraestructura"
      :s.viableFraction>=.12
        ?"La supervivencia se concentra en refugios"
        :"El planeta sigue siendo muy exigente para asentamientos";

  $("#settlementText").textContent=humanSeeded
    ?`Escenario poblacional activo: ${viablePct}% del área latitudinal supera el umbral de refugio asistido bajo el nivel tecnológico actual.`
    :`Capacidad ambiental solamente: ${viablePct}% del área latitudinal podría superar el umbral asistido, pero no se asume que exista una población.`;

  $("#naturalSettlementNarrative").textContent=naturalAreaPct>=45
    ?`Una fracción amplia (${naturalAreaPct}%) supera el soporte natural de referencia.`
    :naturalAreaPct>0
      ?`Solo ${naturalAreaPct}% del área latitudinal supera el soporte natural; el resto exige protección o adaptación conductual.`
      :"No aparecen regiones con soporte natural robusto bajo estos supuestos.";

  $("#assistedSettlementNarrative").textContent=viablePct>=45
    ?`Con infraestructura, ${viablePct}% del área latitudinal entra en la categoría de refugio compatible.`
    :viablePct>0
      ?`La tecnología abre refugios limitados (${viablePct}% del área), sin convertir todo el planeta en habitable.`
      :"Incluso con el soporte actual, los refugios siguen siendo insuficientes.";

  $("#dependencyNarrative").textContent=depPct>=25
    ?`El soporte tecnológico aporta ${depPct} puntos porcentuales medios: la continuidad de infraestructura sería crítica.`
    :depPct>8
      ?`Existe dependencia tecnológica moderada (${depPct} puntos de soporte medio adicional).`
      :"La diferencia entre soporte natural y asistido es relativamente pequeña.";

  const ctx=canvas.getContext("2d");
  const w=canvas.width,h=canvas.height;
  ctx.clearRect(0,0,w,h);
  ctx.fillStyle="#060b0f";ctx.fillRect(0,0,w,h);

  // Planet on left.
  const cx=250,cy=h/2,r=155;
  const glow=ctx.createRadialGradient(cx,cy,20,cx,cy,r*1.7);
  glow.addColorStop(0,"rgba(86,161,191,.12)");
  glow.addColorStop(1,"rgba(0,0,0,0)");
  ctx.fillStyle=glow;ctx.beginPath();ctx.arc(cx,cy,r*1.7,0,Math.PI*2);ctx.fill();

  ctx.save();
  ctx.beginPath();ctx.arc(cx,cy,r,0,Math.PI*2);ctx.clip();
  for(let y=Math.floor(cy-r);y<=Math.ceil(cy+r);y++){
    const norm=(cy-y)/r;
    if(Math.abs(norm)>1)continue;
    const lat=Math.asin(norm)*180/Math.PI;
    const row=settlement.bands.reduce((best,item)=>
      Math.abs(item.latitudeDeg-lat)<Math.abs(best.latitudeDeg-lat)?item:best
    );
    let fill="rgba(91,100,108,.75)";
    if(row.assistedSupport>=.70)fill="rgba(78,151,128,.92)";
    else if(row.assistedSupport>=.50)fill="rgba(91,137,157,.90)";
    else if(row.assistedSupport>=.30)fill="rgba(154,126,76,.86)";
    ctx.fillStyle=fill;
    const half=Math.sqrt(Math.max(0,r*r-(y-cy)*(y-cy)));
    ctx.fillRect(cx-half,y,half*2,2);
  }
  ctx.restore();
  ctx.strokeStyle="rgba(217,237,245,.25)";ctx.lineWidth=1;
  ctx.beginPath();ctx.arc(cx,cy,r,0,Math.PI*2);ctx.stroke();

  // Settlement points only when the scenario includes humans.
  if(humanSeeded){
    settlement.bands.filter(b=>b.assistedSupport>=.5).forEach((b,i)=>{
      if(i%3!==0)return;
      const yy=cy-r*Math.sin(b.latitudeDeg*Math.PI/180);
      const half=Math.sqrt(Math.max(0,r*r-(yy-cy)*(yy-cy)));
      const xx=cx+(i%2===0?.42:-.35)*half;
      ctx.fillStyle="rgba(239,244,247,.88)";
      ctx.beginPath();ctx.arc(xx,yy,2.4+2*b.assistedSupport,0,Math.PI*2);ctx.fill();
    });
  }

  // Regional support curves.
  const left=500,right=w-60,top=95,bottom=h-75;
  ctx.strokeStyle="rgba(255,255,255,.08)";
  ctx.beginPath();ctx.moveTo(left,bottom);ctx.lineTo(right,bottom);ctx.stroke();

  const xFor=i=>left+(right-left)*(i/(settlement.bands.length-1));
  const yFor=v=>bottom-v*(bottom-top);

  const drawCurve=(key,color)=>{
    ctx.strokeStyle=color;ctx.lineWidth=3;ctx.beginPath();
    settlement.bands.forEach((b,i)=>{
      const x=xFor(i),y=yFor(b[key]);
      if(i===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);
    });
    ctx.stroke();
  };
  drawCurve("naturalSupport","rgba(133,158,171,.85)");
  drawCurve("assistedSupport","rgba(106,205,166,.95)");

  ctx.setLineDash([4,6]);ctx.strokeStyle="rgba(255,255,255,.16)";ctx.lineWidth=1;
  ctx.beginPath();ctx.moveTo(left,yFor(.5));ctx.lineTo(right,yFor(.5));ctx.stroke();
  ctx.setLineDash([]);

  ctx.fillStyle="rgba(241,245,247,.94)";ctx.font="700 24px system-ui";
  ctx.fillText("Soporte regional",left,48);
  ctx.font="13px system-ui";ctx.fillStyle="rgba(151,165,174,.92)";
  ctx.fillText("natural",left,72);
  ctx.fillStyle="rgba(133,158,171,.85)";ctx.fillRect(left+50,63,34,3);
  ctx.fillStyle="rgba(151,165,174,.92)";ctx.fillText("asistido",left+110,72);
  ctx.fillStyle="rgba(106,205,166,.95)";ctx.fillRect(left+171,63,34,3);

  ctx.fillStyle="rgba(118,132,141,.9)";ctx.font="11px system-ui";
  ctx.fillText("90°S",left,bottom+25);
  ctx.fillText("Ecuador",(left+right)/2-22,bottom+25);
  ctx.fillText("90°N",right-34,bottom+25);

  $("#settlementMetrics").innerHTML=
    stat("Soporte natural",naturalPct+"%","media ponderada")+
    stat("Soporte asistido",assistedPct+"%","media ponderada")+
    stat("Área asistida viable",viablePct+"%","umbral ≥50%")+
    stat("Área natural viable",naturalAreaPct+"%","umbral ≥60%")+
    stat("Dependencia tecnológica",depPct+" pts")+
    stat("Agricultura potencial",agPct+"%","MODELED")+
    stat("pO₂ proxy",s.pO2.toFixed(3)+" bar","ambiental");
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
  $("#pressureOut").textContent=(+$("#pressure").value).toFixed(2)+" bar";
  $("#waterOut").textContent=(+$("#water").value).toFixed(2)+" océanos";

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
  const orbital=orbitalScreen(a,1);

  $("#habitScore").textContent=Math.round(proxy*100)+"%";
  $("#candidateHeadline").textContent=reading.title;
  $("#candidatePlain").textContent=reading.text;
  $("#confidenceSentence").textContent=reading.confidence;
  $("#orbitSentence").textContent="Órbita · "+orbital.simple;
  $("#orbitSentence").dataset.state=orbital.state;

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
    stat("Proxy de habitabilidad",Math.round(proxy*100)+"%","DERIVED · no GCM")+
    stat("Período H-01",orbital.periodDays==null?"—":fmt(orbital.periodDays,2)+" d","Kepleriano")+
    stat("Δ Hill mínimo",orbital.minDelta==null?"—":fmt(orbital.minDelta,2),"umbral 2√3 = "+fmt(HILL_THRESHOLD,2))+
    stat("Filtro orbital",orbital.label,"DERIVED · no N-body");

  $("#candidateWhy").innerHTML=
    "<b>Cadena climática rápida.</b> Luminosidad y distancia → flujo recibido → corrección por albedo → temperatura de equilibrio → calentamiento atmosférico simplificado → proxy de habitabilidad. "
    +"<br><br><b>Filtro orbital preliminar.</b> La órbita de H-01 se compara con los planetas confirmados mediante separación en radios de Hill mutuos. Si Δ < 2√3, el escenario falla este filtro idealizado. Incluso cuando pasa, TRISOLARIS todavía necesita integración N-body, incertidumbres orbitales y la órbita completa A–BC. "
    +"<br><br>No incluye escape atmosférico, actividad de llamaradas, circulación climática 3D, hidrología ni biosfera.";

  renderSettlementWorld();
  renderFoodWeb();
  renderSurfaceWorld();
  renderClimateWorld();
  renderOrbitWindow();

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

load();
