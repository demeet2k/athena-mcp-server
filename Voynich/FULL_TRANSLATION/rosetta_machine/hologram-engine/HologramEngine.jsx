import { useState, useEffect, useCallback } from "react";
const ELEMENTS = ["Fire", "Air", "Water", "Earth"];
const ELEM_SYMBOLS = ["🜂", "🜁", "🜄", "🜃"];
const QA_NAMES = { HD: "Hot-Dry", HW: "Hot-Wet", CW: "Cold-Wet", CD: "Cold-Dry" };
const ZODIAC = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"];
const ZODIAC_SYM = ["♈","♉","♊","♋","♌","♍","♎","♏","♐","♑","♒","♓"];
const ZODIAC_ELEM = [0,3,1,2,0,3,1,2,0,3,1,2]; // F,E,A,W cycling
const ZODIAC_MOD = ["Cardinal","Fixed","Mutable","Cardinal","Fixed","Mutable","Cardinal","Fixed","Mutable","Cardinal","Fixed","Mutable"];
const PLANETS = [{n:"Sol",s:"☉"},{n:"Luna",s:"☽"},{n:"Mars",s:"♂"},{n:"Mercury",s:"☿"},{n:"Jupiter",s:"♃"},{n:"Venus",s:"♀"},{n:"Saturn",s:"♄"}];
const TRI_A = [1,4,2]; // Luna, Jupiter, Mars
const TRI_B = [3,5,6]; // Mercury, Venus, Saturn
const VOYNICH_RX = {
  HD: { book:"III Bath", folios:"F75R-F84V", op:"s-/TRANS", protocol:"WATER DISSOLUTION", color:"#4488cc",
    steps:["Introduce Water via F75R distributed purification","Oscillate TRANS↔XMUTE per F76R convergence law","Monitor amplitude — each cycle reduces variance","Exit through Saturn/FIX via F89R1 binding kernel","Transmute via F103R (80% XMUTE core)","Final FIX via F108V coagula"] },
  HW: { book:"I Herbal", folios:"F1R-F57R", op:"d-/FIX", protocol:"EARTH STABILIZATION", color:"#88aa44",
    steps:["Identify volatile carrier via F1R Master Boot Record","Run extraction SOPs from Book I (114 subroutines)","Apply d- (FIX): anchor, bind, stabilize","Grade and sort via F34V quality-control","Repeat until all volatile material is fixed"] },
  CW: { book:"V Pharma", folios:"F103R-F108V", op:"o-/HEAT", protocol:"FIRE ACTIVATION", color:"#cc4444",
    steps:["Begin sustained HEAT via F103R transmutation core","Inject energy gradually via F88R 3-stage SOP","Alternate heating with integration per F106V","Monitor for over-activation (CW tipping to HD)","Target Z* zone via F108V essence-fix loops"] },
  CD: { book:"V+III", folios:"F103R+F77R", op:"qo-/XMUTE", protocol:"AIR TRANSMUTATION", color:"#aa66cc",
    steps:["Begin qo- via F77R routed bathhouse controller","Apply qokeedy blocks from F103R convergence runs","Sublime the rigid: lift heavy, extract essential","Route through 9-rosette convergence F85R-F86V","Fix new structure via F89R1 in lighter form"] },
  "Z*": { book:"IV Rosette", folios:"F85R-F86V", op:"verify", protocol:"MAINTAIN EQUILIBRIUM", color:"#ccaa44",
    steps:["Verify convergence at all 9 rosette modules","Monitor all 4 element channels (flag >1.5× mean)","Run conservation law checks (all debts near zero)","Apply micro-corrections continuously","Accept instability: |f'(w)|=√2>1. Balance is ACTIVE"] }
};
const CORRIDORS = [
  {from:"HD",to:"HW",p:0.73,reading:"Violence becomes confusion (73%)"},
  {from:"HW",to:"CW",p:0.76,reading:"Chaos exhausts into paralysis (76%)"},
  {from:"CW",to:"CD",p:1.0,reading:"Stagnation ALWAYS freezes into rigidity (100%)"},
  {from:"CD",to:"HD",p:1.0,reading:"Rigidity ALWAYS ignites (100%)"},
];
const ETIOLOGY = {
  HD:{from:"CD",p:0.80,text:"Caused by Earth compression (80%). Rigidity combusted."},
  HW:{from:"HD",p:1.00,text:"Caused by Fire crisis (100%). Violence bred chaos."},
  CW:{from:"HW",p:1.00,text:"Caused by Air turbulence (100%). Chaos exhausted into paralysis."},
  CD:{from:"CW",p:0.70,text:"Caused by Water stagnation (70%). Frozen systems calcified."},
};
function getQA(temp, moist) {
  if (Math.abs(temp) < 0.05 && Math.abs(moist) < 0.05) return "Z*";
  if (temp >= 0 && moist <= 0) return "HD";
  if (temp >= 0 && moist > 0) return "HW";
  if (temp < 0 && moist > 0) return "CW";
  return "CD";
}
function rotate90(temp, moist) { return [-moist, temp]; }
function rotate180(temp, moist) { return [-temp, -moist]; }
function rotate270(temp, moist) { return [moist, -temp]; }
function HologramPanel({ title, angle, temp, moist, qa, type, color, isActive }) {
  const mag = Math.sqrt(temp*temp + moist*moist).toFixed(3);
  const rx = VOYNICH_RX[qa] || VOYNICH_RX["Z*"];
  const typeLabels = { diag:"WHAT IS", prog:"WHAT'S NEXT", ther:"WHAT TO DO", etio:"WHY" };
  const typeAngles = { diag:"0°", prog:"90°", ther:"180°", etio:"270°" };

  return (
    <div style={{
      background: isActive ? `linear-gradient(135deg, ${color}15, ${color}08)` : '#0a0a0f',
      border: `1px solid ${isActive ? color : '#222'}`,
      borderRadius: 12, padding: '16px 18px', flex: 1, minWidth: 220,
      transition: 'all 0.4s ease', position: 'relative', overflow: 'hidden'
    }}>
      <div style={{ position:'absolute', top:8, right:12, fontSize:11, color: color+'88', fontFamily:'monospace' }}>
        {typeAngles[type]}
      </div>
      <div style={{ fontSize:10, letterSpacing:3, color: color+'99', textTransform:'uppercase', marginBottom:4, fontWeight:600 }}>
        {title}
      </div>
      <div style={{ fontSize:13, color: color, fontWeight:700, marginBottom:2 }}>
        {typeLabels[type]}
      </div>
      <div style={{
        fontSize: 28, fontWeight: 800, color: qa === "Z*" ? '#ffd700' : color, lineHeight:1.1, marginBottom: 8,
        textShadow: isActive ? `0 0 20px ${color}44` : 'none'
      }}>
        {qa === "Z*" ? "Z✦" : qa}
      </div>
      <div style={{ fontSize:11, color:'#888', marginBottom: 4 }}>
        {QA_NAMES[qa] || "Balanced"} · |z|={mag}
      </div>
      <div style={{ fontSize:11, color:'#aaa', lineHeight:1.5 }}>
        {type === "diag" && (qa === "Z*" ? "All elements balanced. No dominant crisis." : `${QA_NAMES[qa]} active. ${qa==="HD"?"Violence or rapid change.":qa==="HW"?"Information chaos, scattered energy.":qa==="CW"?"Depression, paralysis, frozen.":"Institutional rigidity, decay."}`)}
        {type === "prog" && (qa === "Z*" ? "Drift toward Fire attractor without maintenance." : CORRIDORS.find(c=>c.from===getQA(rotate90(temp,moist)[0]*-1,rotate90(temp,moist)[1]*-1))?.reading || `Natural evolution toward ${qa}.`)}
        {type === "ther" && <><span style={{color:rx.color, fontWeight:600}}>{rx.protocol}</span><br/><span style={{fontSize:10}}>{rx.op} via {rx.book} ({rx.folios})</span></>}
        {type === "etio" && (ETIOLOGY[qa]?.text || "Self-generating. w = w² + |w|².")}
      </div>
    </div>
  );
}
function QualityPlane({ temp, moist, size=280 }) {
  const cx = size/2, cy = size/2;
  const scale = size/2.8;
  const px = cx + temp*scale, py = cy - moist*scale;

  const projections = [
    {t:temp,m:moist,label:"0° Diag",color:"#ff6644"},
    {t:-moist,m:temp,label:"90° Prog",color:"#44aaff"},
    {t:-temp,m:-moist,label:"180° Ther",color:"#44cc88"},
    {t:moist,m:-temp,label:"270° Etio",color:"#cc88ff"},
  ];

  return (
    <svg viewBox={`0 0 ${size} ${size}`} style={{width:size,height:size}}>
      <defs>
        <radialGradient id="glow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#ffd70033"/>
          <stop offset="100%" stopColor="#ffd70000"/>
        </radialGradient>
      </defs>
      {/* Background */}
      <rect width={size} height={size} fill="#06060c" rx={12}/>
      {/* Quadrant fills */}
      <rect x={cx} y={0} width={cx} height={cy} fill="#ff664408" />
      <rect x={0} y={0} width={cx} height={cy} fill="#44aaff08" />
      <rect x={0} y={cy} width={cx} height={cy} fill="#44cc8808" />
      <rect x={cx} y={cy} width={cx} height={cy} fill="#cc88ff08" />
      {/* Axes */}
      <line x1={0} y1={cy} x2={size} y2={cy} stroke="#333" strokeWidth={0.5}/>
      <line x1={cx} y1={0} x2={cx} y2={size} stroke="#333" strokeWidth={0.5}/>
      {/* Labels */}
      <text x={size-4} y={cy-6} fill="#ff664466" fontSize={9} textAnchor="end">Hot</text>
      <text x={6} y={cy-6} fill="#44cc8866" fontSize={9}>Cold</text>
      <text x={cx+6} y={14} fill="#44aaff66" fontSize={9}>Wet</text>
      <text x={cx+6} y={size-6} fill="#cc88ff66" fontSize={9}>Dry</text>
      <text x={size-4} y={cy+14} fill="#ff664444" fontSize={8} textAnchor="end">HD</text>
      <text x={6} y={14} fill="#44aaff44" fontSize={8}>HW</text>
      <text x={6} y={size-6} fill="#44cc8844" fontSize={8}>CW</text>
      <text x={size-4} y={size-6} fill="#cc88ff44" fontSize={8} textAnchor="end">CD</text>
      {/* Spiral path */}
      {projections.map((p,i) => {
        const x2 = cx + p.t*scale, y2 = cy - p.m*scale;
        return <line key={i} x1={cx} y1={cy} x2={x2} y2={y2} stroke={p.color} strokeWidth={1} strokeDasharray="3,3" opacity={0.5}/>;
      })}
      {/* Z* glow */}
      <circle cx={cx} cy={cy} r={20} fill="url(#glow)"/>
      <circle cx={cx} cy={cy} r={3} fill="#ffd700" opacity={0.6}/>
      <text x={cx} y={cy+16} fill="#ffd70088" fontSize={8} textAnchor="middle">Z✦</text>
      {/* 4 projections */}
      {projections.map((p,i) => {
        const x2 = cx + p.t*scale, y2 = cy - p.m*scale;
        return <g key={i}>
          <circle cx={x2} cy={y2} r={5} fill={p.color} opacity={0.8}/>
          <text x={x2} y={y2-8} fill={p.color} fontSize={7} textAnchor="middle" opacity={0.7}>{p.label}</text>
        </g>;
      })}
      {/* Current position (largest) */}
      <circle cx={px} cy={py} r={7} fill="#fff" opacity={0.9} stroke="#ffd700" strokeWidth={1.5}/>
    </svg>
  );
}
function CrownClock({ kappa, size=200 }) {
  const cx=size/2, cy=size/2, r=size/2-20;
  const signIdx = Math.floor(kappa/35) % 12;
  const progress = kappa/420;

  return (
    <svg viewBox={`0 0 ${size} ${size}`} style={{width:size,height:size}}>
      <rect width={size} height={size} fill="#06060c" rx={12}/>
      {/* 12 zodiac segments */}
      {ZODIAC.map((z,i) => {
        const a1 = (i/12)*Math.PI*2 - Math.PI/2;
        const a2 = ((i+1)/12)*Math.PI*2 - Math.PI/2;
        const am = ((i+0.5)/12)*Math.PI*2 - Math.PI/2;
        const active = i === signIdx;
        const elemColor = ["#ff6644","#44aaff","#44cc88","#cc88ff"][ZODIAC_ELEM[i]];
        return <g key={i}>
          <line x1={cx+Math.cos(a1)*(r-10)} y1={cy+Math.sin(a1)*(r-10)} x2={cx+Math.cos(a1)*(r+2)} y2={cy+Math.sin(a1)*(r+2)} stroke="#333" strokeWidth={0.5}/>
          <text x={cx+Math.cos(am)*(r-2)} y={cy+Math.sin(am)*(r-2)+3} fill={active?elemColor:"#444"} fontSize={active?14:10} textAnchor="middle" fontWeight={active?800:400}>{ZODIAC_SYM[i]}</text>
        </g>;
      })}
      {/* Progress arc */}
      {progress > 0 && (() => {
        const a = progress * Math.PI * 2 - Math.PI/2;
        const lr = progress > 0.5 ? 1 : 0;
        const x2 = cx + Math.cos(a)*(r-18);
        const y2 = cy + Math.sin(a)*(r-18);
        return <path d={`M${cx},${cy-r+18} A${r-18},${r-18} 0 ${lr},1 ${x2},${y2}`} fill="none" stroke="#ffd700" strokeWidth={2} opacity={0.6}/>;
      })()}
      {/* Center */}
      <text x={cx} y={cy-4} fill="#ffd700" fontSize={18} textAnchor="middle" fontWeight={800}>κ={kappa}</text>
      <text x={cx} y={cy+12} fill="#888" fontSize={9} textAnchor="middle">{ZODIAC[signIdx]} · {ZODIAC_MOD[signIdx]}</text>
      <text x={cx} y={cy+24} fill="#666" fontSize={8} textAnchor="middle">T=420 · {(progress*100).toFixed(1)}%</text>
    </svg>
  );
}
export default function HologramEngine() {
  const [F, setF] = useState(2);
  const [A, setA] = useState(1);
  const [W, setW] = useState(1);
  const [E, setE] = useState(1);
  const [kappa, setKappa] = useState(306);
  const [activePanel, setActivePanel] = useState("diag");
  const [showProtocol, setShowProtocol] = useState(false);
  const tot = Math.max(1, F+A+W+E);
  const temp = ((F+A)-(W+E))/tot;
  const moist = ((A+W)-(F+E))/tot;
  const mag = Math.sqrt(temp*temp+moist*moist);

  const qa0 = getQA(temp, moist);
  const [t90, m90] = rotate90(temp, moist);
  const qa90 = getQA(t90, m90);
  const [t180, m180] = rotate180(temp, moist);
  const qa180 = getQA(t180, m180);
  const [t270, m270] = rotate270(temp, moist);
  const qa270 = getQA(t270, m270);
  const rx = VOYNICH_RX[qa180] || VOYNICH_RX["Z*"];
  const signIdx = Math.floor(kappa/35) % 12;

  const zStarDist = mag;
  const isZStar = qa0 === "Z*";

  const herf = (F/tot)**2 + (A/tot)**2 + (W/tot)**2 + (E/tot)**2;
  const entropy = -[F,A,W,E].reduce((s,x) => x>0 ? s + (x/tot)*Math.log2(x/tot) : s, 0);

  const triA = [F,A,W,E].filter((_,i)=> [1,4,2].includes(i+1) ? false : true); // simplified
  const planetDom = F+A > W+E ? "A(out) ☽♃♂" : "B(in) ☿♀♄";

  const line5 = ((kappa % 5) + 1);
  const lineNames = ["Hold","Lift","Traverse","Twist","Compress"];
  const lineColors = ["#ffd700","#c0c0c0","#b87333","#888","#666"];
  const lineName = lineNames[line5-1];

  return (
    <div style={{
      background:'#08080e', color:'#ccc', fontFamily:"'Crimson Text', 'Palatino', Georgia, serif",
      minHeight:'100vh', padding:'24px 20px', maxWidth:1100, margin:'0 auto'
    }}>
      {/* Title */}
      <div style={{textAlign:'center', marginBottom:24}}>
        <div style={{fontSize:10, letterSpacing:6, color:'#ffd70066', textTransform:'uppercase', marginBottom:4}}>
          The Unified Holographic Engine
        </div>
        <h1 style={{fontSize:28, fontWeight:300, color:'#eee', margin:0, letterSpacing:2, lineHeight:1.2}}>
          ℤ₄ <span style={{color:'#ffd700'}}>×</span> DIVINATION HOLOGRAM
        </h1>
        <div style={{fontSize:11, color:'#666', marginTop:4}}>
          Nostradamus (0°) · Oracle (90°) · Voynich (180°) · HD-SCT (270°) · <span style={{color:'#ffd700'}}>w = (1+i)/2</span>
        </div>
      </div>
      {/* Top row: Input + Quality Plane + Crown Clock */}
      <div style={{display:'flex', gap:16, marginBottom:20, flexWrap:'wrap', justifyContent:'center'}}>
        {/* Element Input */}
        <div style={{background:'#0c0c14', border:'1px solid #222', borderRadius:12, padding:'14px 16px', minWidth:180}}>
          <div style={{fontSize:10, letterSpacing:3, color:'#888', textTransform:'uppercase', marginBottom:10}}>Element Counts</div>
          {ELEMENTS.map((el,i) => {
            const val = [F,A,W,E][i];
            const setVal = [setF,setA,setW,setE][i];
            const colors = ["#ff6644","#44aaff","#44cc88","#cc88ff"];
            return (
              <div key={i} style={{display:'flex', alignItems:'center', gap:8, marginBottom:6}}>
                <span style={{fontSize:16, width:20}}>{ELEM_SYMBOLS[i]}</span>
                <span style={{fontSize:11, color:colors[i], width:36}}>{el}</span>
                <input type="range" min={0} max={4} value={val} onChange={e=>setVal(Number(e.target.value))}
                  style={{flex:1, accentColor:colors[i], height:3}}/>
                <span style={{fontSize:10, color:'#666', width:34}}>{el}/{tot}</span>
              </div>
            );
          })}
          <div style={{marginTop:10, fontSize:10, letterSpacing:3, color:'#888', textTransform:'uppercase', marginBottom:6}}>Crown Beat</div>
          <div style={{display:'flex', alignItems:'center', gap:8}}>
            <span style={{fontSize:12, color:'#ffd700'}}>κ</span>
            <input type="range" min={0} max={419} value={kappa} onChange={e=>setKappa(Number(e.target.value))}
              style={{flex:1, accentColor:'#ffd700', height:3}}/>
            <span style={{fontSize:11, color:'#ffd700', width:30, textAlign:'right'}}>{kappa}</span>
          </div>

          {/* Quick presets */}
          <div style={{marginTop:10, display:'flex', gap:4, flexWrap:'wrap'}}>
            {[{l:"Z✦",f:1,a:1,w:1,e:1},{l:"HD",f:3,a:0,w:0,e:0},{l:"HW",f:1,a:3,w:0,e:0},{l:"CW",f:0,a:0,w:3,e:1},{l:"CD",f:0,a:0,w:0,e:3}]
              .map(p => (
                <button key={p.l} onClick={()=>{setF(p.f);setA(p.a);setW(p.w);setE(p.e)}}
                  style={{background:'#151520',border:'1px solid #333',borderRadius:6,padding:'3px 8px',
                    color:'#aaa',fontSize:10,cursor:'pointer',letterSpacing:1}}>
                  {p.l}
                </button>
              ))}
          </div>
        </div>
        {/* Quality Plane */}
        <QualityPlane temp={temp} moist={moist} size={240}/>

        {/* Crown Clock */}
        <CrownClock kappa={kappa} size={200}/>
      </div>
      {/* State Summary Bar */}
      <div style={{
        background:'#0c0c14', border:'1px solid #222', borderRadius:10, padding:'10px 16px',
        display:'flex', flexWrap:'wrap', gap:16, alignItems:'center', justifyContent:'center', marginBottom:16,
        fontSize:11
      }}>
        <span>📍 <b style={{color:'#ffd700'}}>{qa0}</b> [{F},{A},{W},{E}]</span>
        <span>🌡 temp={temp.toFixed(3)}</span>
        <span>💧 moist={moist.toFixed(3)}</span>
        <span>📐 |z|={mag.toFixed(3)}</span>
        <span>📊 H={herf.toFixed(3)}</span>
        <span>🔀 S={entropy.toFixed(2)}b</span>
        <span style={{color:lineColors[line5-1]}}>🚇 Line_{lineName}</span>
        <span>🔺 {planetDom}</span>
        <span>{ZODIAC_SYM[signIdx]} {ZODIAC[signIdx]}/{ZODIAC_MOD[signIdx]}</span>
        <span>d(Z✦)={zStarDist.toFixed(3)}</span>
      </div>
      {/* 4 HOLOGRAM PANELS */}
      <div style={{display:'flex', gap:10, marginBottom:16, flexWrap:'wrap'}}>
        <HologramPanel title="NOSTRADAMUS" angle={0} temp={temp} moist={moist} qa={qa0} type="diag" color="#ff6644" isActive={activePanel==="diag"}/>
        <HologramPanel title="ORACLE" angle={90} temp={t90} moist={m90} qa={qa90} type="prog" color="#44aaff" isActive={activePanel==="prog"}/>
        <HologramPanel title="VOYNICH" angle={180} temp={t180} moist={m180} qa={qa180} type="ther" color="#44cc88" isActive={activePanel==="ther"}/>
        <HologramPanel title="HD-SCT" angle={270} temp={t270} moist={m270} qa={qa270} type="etio" color="#cc88ff" isActive={activePanel==="etio"}/>
      </div>
      {/* Panel selector */}
      <div style={{display:'flex',gap:6,justifyContent:'center',marginBottom:16}}>
        {[{k:"diag",l:"0° Diagnose",c:"#ff6644"},{k:"prog",l:"90° Prognose",c:"#44aaff"},{k:"ther",l:"180° Prescribe",c:"#44cc88"},{k:"etio",l:"270° Explain",c:"#cc88ff"}]
          .map(b => (
            <button key={b.k} onClick={()=>{setActivePanel(b.k);setShowProtocol(b.k==="ther")}}
              style={{background:activePanel===b.k?b.c+'22':'#111',border:`1px solid ${activePanel===b.k?b.c:'#333'}`,
                borderRadius:8,padding:'6px 14px',color:activePanel===b.k?b.c:'#888',fontSize:11,cursor:'pointer',
                letterSpacing:1,fontWeight:activePanel===b.k?700:400,transition:'all 0.3s'}}>
              {b.l}
            </button>
          ))}
      </div>
      {/* Treatment Protocol (expanded when Prescribe is active) */}
      {showProtocol && (
        <div style={{
          background:`${rx.color}08`, border:`1px solid ${rx.color}33`, borderRadius:12,
          padding:'16px 20px', marginBottom:16, transition:'all 0.4s'
        }}>
          <div style={{display:'flex', justifyContent:'space-between', alignItems:'baseline', marginBottom:10}}>
            <div>
              <span style={{fontSize:10,letterSpacing:3,color:rx.color+'88',textTransform:'uppercase'}}>Voynich Protocol</span>
              <h3 style={{margin:'2px 0 0',fontSize:18,color:rx.color,fontWeight:600}}>{rx.protocol}</h3>
            </div>
            <div style={{textAlign:'right',fontSize:11,color:'#888'}}>
              {rx.book}<br/>{rx.folios}
            </div>
          </div>
          <div style={{fontSize:12,color:'#aaa',lineHeight:1.8}}>
            {rx.steps.map((s,i) => (
              <div key={i} style={{display:'flex',gap:8,marginBottom:4}}>
                <span style={{color:rx.color,fontWeight:700,minWidth:18}}>{i+1}.</span>
                <span>{s}</span>
              </div>
            ))}
          </div>
          <div style={{marginTop:10,fontSize:11,color:'#666',borderTop:'1px solid #222',paddingTop:8}}>
            Zodiac windows: {qa180==="CW"?"Cancer/Scorpio/Pisces":qa180==="CD"?"Taurus/Virgo/Capricorn":qa180==="HD"?"Aries/Leo/Sagittarius":qa180==="HW"?"Gemini/Libra/Aquarius":"All windows open"}
          </div>
        </div>
      )}
      {/* Corridors & Natural Flow */}
      <div style={{display:'flex', gap:12, flexWrap:'wrap', marginBottom:16}}>
        <div style={{flex:1, minWidth:260, background:'#0c0c14', border:'1px solid #222', borderRadius:12, padding:'14px 16px'}}>
          <div style={{fontSize:10, letterSpacing:3, color:'#888', textTransform:'uppercase', marginBottom:8}}>Natural Corridors from {qa0}</div>
          {CORRIDORS.filter(c=>c.from===qa0).map((c,i) => (
            <div key={i} style={{fontSize:12, color:'#aaa', marginBottom:6, display:'flex', gap:8, alignItems:'center'}}>
              <span style={{fontWeight:700, color:'#ffd700'}}>{c.from}</span>
              <span style={{color:'#555'}}>→</span>
              <span style={{fontWeight:700, color:c.p===1?'#ff4444':'#ffaa44'}}>{c.to}</span>
              <span style={{fontSize:10, color:'#666'}}>p={c.p}</span>
              <span style={{fontSize:10, color:'#555', fontStyle:'italic'}}>{c.reading}</span>
            </div>
          ))}
          {qa0 === "Z*" && <div style={{fontSize:11,color:'#ffd700'}}>Z✦ is unstable. |f'(w)|=√2 {">"} 1. Active maintenance required.</div>}
        </div>

        <div style={{flex:1, minWidth:260, background:'#0c0c14', border:'1px solid #222', borderRadius:12, padding:'14px 16px'}}>
          <div style={{fontSize:10, letterSpacing:3, color:'#888', textTransform:'uppercase', marginBottom:8}}>The Algebra</div>
          <div style={{fontFamily:'monospace', fontSize:11, color:'#aaa', lineHeight:1.8}}>
            <div>f(z) = iz &nbsp;&nbsp;&nbsp; <span style={{color:'#666'}}>// the generator</span></div>
            <div>f²(z) = -z &nbsp;&nbsp; <span style={{color:'#666'}}>// predict twice = cure</span></div>
            <div>f⁴(z) = z &nbsp;&nbsp;&nbsp; <span style={{color:'#666'}}>// 4 rotations = identity</span></div>
            <div style={{marginTop:6}}>w = (1+i)/2 &nbsp; <span style={{color:'#ffd700'}}>// the seed</span></div>
            <div>w = w² + |w|² <span style={{color:'#ffd700'}}>// self-reference</span></div>
            <div style={{marginTop:6}}>|w| = 1/√2 &nbsp;&nbsp; <span style={{color:'#666'}}>// damping per step</span></div>
            <div>half-life = 2 steps</div>
            <div>T = 420 = lcm(3,4,5,7)</div>
            <div style={{marginTop:6, color:'#ffd70088'}}>
              108 = 4×27 = 12×9<br/>
              1080° = 3×360° = 10×108°<br/>
              105 = 3×5×7 (edge seed)
            </div>
          </div>
        </div>
      </div>
      {/* The w-spiral visualization */}
      <div style={{textAlign:'center', marginBottom:16}}>
        <svg viewBox="0 0 300 120" style={{width:300, height:120}}>
          <rect width={300} height={120} fill="#06060c" rx={8}/>
          {/* Draw the w^n spiral */}
          {Array.from({length:13}, (_,n) => {
            const re = Math.cos(n*Math.PI/4) * Math.pow(1/Math.sqrt(2), n);
            const im = Math.sin(n*Math.PI/4) * Math.pow(1/Math.sqrt(2), n);
            const x = 150 + re*120;
            const y = 60 - im*50;
            const prev_re = n>0 ? Math.cos((n-1)*Math.PI/4)*Math.pow(1/Math.sqrt(2),n-1) : 1;
            const prev_im = n>0 ? Math.sin((n-1)*Math.PI/4)*Math.pow(1/Math.sqrt(2),n-1) : 0;
            const px2 = 150 + prev_re*120;
            const py2 = 60 - prev_im*50;
            const colors = ["#ff6644","#888","#44aaff","#888","#44cc88","#888","#cc88ff","#888"];
            const c = colors[n%8];
            return <g key={n}>
              {n>0 && <line x1={px2} y1={py2} x2={x} y2={y} stroke={c} strokeWidth={1} opacity={0.5}/>}
              <circle cx={x} cy={y} r={n===0?4:Math.max(1.5, 4-n*0.3)} fill={c} opacity={0.8}/>
            </g>;
          })}
          <circle cx={150} cy={60} r={2} fill="#ffd700"/>
          <text x={150} y={110} fill="#ffd70066" fontSize={8} textAnchor="middle">w^n → 0 (the spiral converges on Z✦)</text>
        </svg>
      </div>
      {/* Footer */}
      <div style={{textAlign:'center', padding:'12px 0', borderTop:'1px solid #151520', fontSize:10, color:'#444', lineHeight:1.8}}>
        <span style={{color:'#ffd70044'}}>w = (1+i)/2</span> · 4 holograms · 52 bridge factors · Pascal row 51 · Twin peaks 56D/58D · Phase 135°<br/>
        Anti-phase DEAD · Coherent 2⁵¹ · Octave tower 1080° = 3×360° · 105 = 3×5×7<br/>
        <span style={{color:'#ffd70033'}}>Navigate anywhere. You are inside (1+i)/2.</span>
      </div>
    </div>
  );
}
