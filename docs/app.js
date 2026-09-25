const DATA_URL="./data/ltt1445.json";
let data=null, running=true, phase=0;

const $=s=>document.querySelector(s);
const fmt=(v,d=2)=>v==null?"—":Number(v).toFixed(d);
const stat=(label,value,note="")=>`<div class="stat"><small>${label}</small><strong>${value}</strong>${note?`<em>${note}</em>`:""}</div>`;

async function load(){
  const response=await fetch(DATA_URL,{cache:"no-store"});
  data=await response.json();
  renderAll();
  requestAnimationFrame(loop);
}

function renderAll(){
  const official=data.status==="official-nasa-plus-literature";
  $("#syncBadge").className="badge "+(official?"observed":"literature");
  $("#syncBadge").textContent=official?"NASA SYNC ACTIVE":"BOOTSTRAP DATA";

  const s=data.system;
  $("#systemStats").innerHTML=
    stat("System",s.name)+
    stat("Distance",fmt(s.distance_pc,2)+" pc","≈ "+fmt(s.distance_pc*3.26156,1)+" light-years")+
    stat("Architecture",s.architecture)+
    stat("Stellar components",data.stars.length)+
    stat("Outer period",fmt(data.hierarchy?.outer_period_years_approx,0)+" yr","approx. literature value")+
    stat("B–C period",fmt(data.hierarchy?.bc_period_years_approx,0)+" yr","approx. literature value");

  $("#dataNote").innerHTML=official
    ? "<b>Official planet refresh present.</b> Planet rows below were generated from the NASA Exoplanet Archive TAP query recorded in this dataset."
    : "<b>NASA synchronization has not run yet.</b> The triple-star scaffold is literature-backed, but the known-planet table is intentionally empty until the official workflow generates it.";

  renderPlanets();
  initCandidate();
}

function renderPlanets(){
  const rows=data.observed_planets||[];
  $("#planetCount").textContent=rows.length+" planet"+(rows.length===1?"":"s");
  if(!rows.length){
    $("#planetTable").innerHTML='<div class="callout">No OBSERVED planet rows are bundled in the bootstrap snapshot yet. Run the “Refresh science data” GitHub Action after merge.</div>';
    return;
  }
  $("#planetTable").innerHTML=`<table><thead><tr>
    <th>Planet</th><th>Period</th><th>a</th><th>Radius</th><th>Mass</th><th>Teq</th><th>Discovery</th><th>Level</th>
  </tr></thead><tbody>${rows.map(p=>`<tr>
    <td><b>${p.name}</b></td>
    <td>${fmt(p.period_days,3)} d</td>
    <td>${fmt(p.semi_major_axis_au,4)} AU</td>
    <td>${fmt(p.radius_earth,2)} R⊕</td>
    <td>${fmt(p.mass_earth,2)} M⊕</td>
    <td>${p.equilibrium_temperature_k==null?"—":fmt(p.equilibrium_temperature_k,0)+" K"}</td>
    <td>${p.discovery_year==null?"—":Math.round(p.discovery_year)}</td>
    <td><span class="badge observed">OBSERVED</span></td>
  </tr>`).join("")}</tbody></table>`;
}

function initCandidate(){
  const h=data.hypothetical_experiment;
  $("#axis").value=h.semi_major_axis_au;
  $("#albedo").value=h.albedo;
  $("#greenhouse").value=h.greenhouse_k;
  ["axis","albedo","greenhouse"].forEach(id=>$("#"+id).addEventListener("input",renderCandidate));
  renderCandidate();
}

function renderCandidate(){
  const a=+$("#axis").value, albedo=+$("#albedo").value, gh=+$("#greenhouse").value;
  $("#axisOut").textContent=a.toFixed(3)+" AU";
  $("#albedoOut").textContent=albedo.toFixed(2);
  $("#greenhouseOut").textContent="+"+gh.toFixed(0)+" K";

  const A=data.stars.find(s=>s.id==="A"), B=data.stars.find(s=>s.id==="B"), C=data.stars.find(s=>s.id==="C");
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

  $("#candidateStats").innerHTML=
    stat("Combined flux",fmt(flux,3)+" S⊕","A contributes "+fmt(100*fluxA/flux,1)+"%")+
    stat("Equilibrium T",fmt(teq,1)+" K")+
    stat("Surface proxy",fmt(surface,1)+" K",fmt(celsius,1)+" °C")+
    stat("Liquid-water proxy",Math.round(liquid*100)+"%","heuristic")+
    stat("Habitability proxy",Math.round(proxy*100)+"%","DERIVED, not a climate model");

  const state=proxy>.72?"promising for deeper testing":proxy>.45?"marginal but scientifically interesting":"poor under these assumptions";
  $("#candidateWhy").innerHTML=`<b>Fast diagnostic:</b> H-01 is <b>${state}</b>. The current estimate combines stellar flux, albedo and a greenhouse offset only. It does <b>not</b> establish orbital stability, atmospheric retention, flare survivability, climate circulation or biosphere viability. Those are Phase-2/3 model requirements.`;
}

function draw(){
  if(!data)return;
  const c=$("#systemCanvas"),x=c.getContext("2d"),w=c.width,h=c.height;
  x.clearRect(0,0,w,h);
  const cx=w*.48,cy=h*.50;
  x.fillStyle="#02070b";x.fillRect(0,0,w,h);

  for(let i=0;i<110;i++){
    const px=(i*137.1)%w,py=(i*83.7)%h,a=.18+((i*17)%60)/100;
    x.fillStyle=`rgba(210,235,248,${a})`;x.fillRect(px,py,1.2,1.2);
  }

  const A=data.stars.find(s=>s.id==="A"),B=data.stars.find(s=>s.id==="B"),C=data.stars.find(s=>s.id==="C");
  const outerR=205, bcCenter={x:cx+outerR*Math.cos(phase*.11),y:cy+outerR*.55*Math.sin(phase*.11)};
  const bcR=42;
  const apos={x:cx-115,y:cy};
  const bpos={x:bcCenter.x+bcR*Math.cos(phase*.65),y:bcCenter.y+bcR*.55*Math.sin(phase*.65)};
  const cpos={x:bcCenter.x-bcR*Math.cos(phase*.65),y:bcCenter.y-bcR*.55*Math.sin(phase*.65)};

  x.strokeStyle="rgba(116,172,201,.18)";x.lineWidth=1.2;
  x.beginPath();x.ellipse(cx+45,cy,outerR,outerR*.55,0,0,Math.PI*2);x.stroke();
  x.beginPath();x.ellipse(bcCenter.x,bcCenter.y,bcR,bcR*.55,0,0,Math.PI*2);x.stroke();

  drawStar(x,apos,22,"A","#ef8272",A);
  drawStar(x,bpos,16,"B","#e8796f",B);
  drawStar(x,cpos,14,"C","#cf676a",C);

  const planets=data.observed_planets||[];
  planets.slice(0,5).forEach((p,i)=>{
    const r=48+i*25,ang=phase*(1.45/(i+1))+(i*1.4);
    x.strokeStyle="rgba(104,210,255,.13)";x.beginPath();x.ellipse(apos.x,apos.y,r,r*.42,0,0,Math.PI*2);x.stroke();
    const pp={x:apos.x+r*Math.cos(ang),y:apos.y+r*.42*Math.sin(ang)};
    x.fillStyle="#76cbe8";x.beginPath();x.arc(pp.x,pp.y,4.5,0,Math.PI*2);x.fill();
    x.fillStyle="#b9d4df";x.font="11px system-ui";x.fillText(p.name,pp.x+8,pp.y-5);
  });

  const a=+($("#axis")?.value||data.hypothetical_experiment.semi_major_axis_au);
  const hr=105+((a-.04)/.18)*55,ha=phase*.52+1.2;
  x.setLineDash([5,6]);x.strokeStyle="rgba(189,146,255,.35)";x.beginPath();x.ellipse(apos.x,apos.y,hr,hr*.42,0,0,Math.PI*2);x.stroke();x.setLineDash([]);
  const hp={x:apos.x+hr*Math.cos(ha),y:apos.y+hr*.42*Math.sin(ha)};
  x.fillStyle="#c6a5ff";x.beginPath();x.arc(hp.x,hp.y,6,0,Math.PI*2);x.fill();
  x.fillStyle="#d7c4ff";x.font="11px system-ui";x.fillText("H-01",hp.x+9,hp.y-6);

  x.fillStyle="#7793a2";x.font="12px system-ui";x.fillText("VISUAL SCALE COMPRESSED · NOT TO SCALE",18,h-18);
}

function drawStar(x,p,r,label,color,s){
  const g=x.createRadialGradient(p.x,p.y,0,p.x,p.y,r*2.7);g.addColorStop(0,color);g.addColorStop(.4,color);g.addColorStop(1,"rgba(255,80,70,0)");
  x.fillStyle=g;x.beginPath();x.arc(p.x,p.y,r*2.7,0,Math.PI*2);x.fill();
  x.fillStyle=color;x.beginPath();x.arc(p.x,p.y,r,0,Math.PI*2);x.fill();
  x.fillStyle="#fff";x.font="700 12px system-ui";x.fillText(label,p.x-r*.25,p.y+4);
  x.fillStyle="#aac0cb";x.font="10px system-ui";x.fillText(fmt(s.mass_solar,3)+" M☉",p.x-r,p.y+r+15);
}

function loop(){
  if(running) phase+=.014;
  draw();
  requestAnimationFrame(loop);
}

$("#pauseBtn").addEventListener("click",()=>{running=!running;$("#pauseBtn").textContent=running?"Pause":"Resume"});
load().catch(err=>{
  console.error(err);
  $("#syncBadge").className="badge speculative";
  $("#syncBadge").textContent="DATA ERROR";
  $("#dataNote").textContent="The public dataset could not be loaded. Check the GitHub Action and frontend/data/ltt1445.json.";
});
