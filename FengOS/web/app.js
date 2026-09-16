/* FengOS 前端（黑金帝国版）：金箔开场 + 鎏金版图 + 金线心电图。全部真实数据。 */
"use strict";
const $ = (s) => document.querySelector(s);
const isMobile = matchMedia("(max-width: 820px)").matches;
/* 回归门模式（?static=1）：固定随机种子 + 冻结动画/实时图表，保证截图逐像素可比 */
const STATIC = new URLSearchParams(location.search).has("static");
if (STATIC) {
  let _s = 42;
  Math.random = () => { _s = (_s * 1103515245 + 12345) & 0x7fffffff; return _s / 0x7fffffff; };
}

/* ================= 1. 开场：金箔粒子汇聚成"豐" → 宋体 FENG OS 逐字浮现 ================= */
function intro() {
  const cv = $("#introCanvas"), ctx = cv.getContext("2d");
  cv.width = innerWidth; cv.height = innerHeight;
  const W = cv.width, H = cv.height;

  // 目标点："豐"字轮廓采样（离屏 canvas 渲染后取不透明像素）
  const off = document.createElement("canvas");
  off.width = W; off.height = H;
  const octx = off.getContext("2d");
  const fs = Math.min(W * 0.42, H * 0.62);
  octx.fillStyle = "#fff";
  octx.font = `900 ${fs}px "Noto Serif SC","Songti SC","SimSun",serif`;
  octx.textAlign = "center"; octx.textBaseline = "middle";
  octx.fillText("豐", W / 2, H / 2 - H * 0.04);
  const img = octx.getImageData(0, 0, W, H).data;
  const targets = [];
  const step = isMobile ? 4 : 3;
  for (let y = 0; y < H; y += step) for (let x = 0; x < W; x += step) {
    if (img[(y * W + x) * 4 + 3] > 128) targets.push({ x, y });
  }

  // 金箔：圆片带高光，非像素方块
  const N = Math.min(targets.length, isMobile ? 900 : 2200);
  const foils = [];
  for (let i = 0; i < N; i++) {
    const t = targets[Math.floor(Math.random() * targets.length)];
    const ang = Math.random() * Math.PI * 2, rad = Math.max(W, H) * (0.4 + Math.random() * 0.5);
    foils.push({
      x: W / 2 + Math.cos(ang) * rad, y: H / 2 + Math.sin(ang) * rad * 0.7,
      tx: t.x + (Math.random() - .5) * 2.4, ty: t.y + (Math.random() - .5) * 2.4,
      s: Math.random() * 2.4 + 1.1, d: Math.random(), rot: Math.random() * Math.PI, vr: (Math.random() - .5) * 0.02,
      hi: Math.random() < 0.22, // 少量高光金箔
    });
  }

  const t0 = performance.now(), DUR = 2900;
  function drawFoil(f, alpha) {
    ctx.save();
    ctx.translate(f.x, f.y); ctx.rotate(f.rot);
    const g = ctx.createLinearGradient(-f.s, -f.s, f.s, f.s);
    if (f.hi) { g.addColorStop(0, `rgba(232,207,154,${alpha})`); g.addColorStop(1, `rgba(201,164,92,${alpha * .7})`); }
    else { g.addColorStop(0, `rgba(201,164,92,${alpha})`); g.addColorStop(1, `rgba(138,109,59,${alpha * .8})`); }
    ctx.fillStyle = g;
    ctx.beginPath(); ctx.ellipse(0, 0, f.s, f.s * 0.62, 0, 0, Math.PI * 2); ctx.fill();
    ctx.restore();
  }
  function frame(now) {
    const el = now - t0;
    ctx.fillStyle = "rgba(8,8,7,.24)"; ctx.fillRect(0, 0, W, H);
    const p = Math.min(1, el / 2100);
    const ease = 1 - Math.pow(1 - p, 3.4); // 长缓出
    const converge = Math.min(1, el / 2400);
    for (const f of foils) {
      const k = 0.028 * (0.5 + f.d);
      f.x += (f.tx * ease - f.x) * k;
      f.y += (f.ty * ease - f.y) * k;
      f.rot += f.vr * (1.4 - converge);
      drawFoil(f, 0.45 + 0.55 * converge);
    }
    if (el < DUR) requestAnimationFrame(frame);
    else { // 收束：粒子淡出，字交给 DOM 标题层
      const fade = setInterval(() => {
        ctx.fillStyle = "rgba(8,8,7,.12)"; ctx.fillRect(0, 0, W, H);
      }, 60);
      setTimeout(() => clearInterval(fade), 1600);
    }
  }
  requestAnimationFrame(frame);

  // GSAP：标题逐字浮现（慢稳贵）
  const title = $("#introTitle");
  "FENG OS".split("").forEach((ch) => {
    const sp = document.createElement("span"); sp.textContent = ch === " " ? "\u00a0" : ch; title.appendChild(sp);
  });
  const tl = gsap.timeline({ onComplete: enterMain });
  tl.to(title.children, { opacity: 1, y: 0, stagger: 0.12, duration: 0.9, ease: "power3.out", delay: 0.9 })
    .to("#introRule", { width: "42vw", duration: 0.9, ease: "power2.inOut" }, "-=0.5")
    .to("#introSub", { opacity: 1, duration: 0.8, ease: "power2.out" }, "-=0.4")
    .to("#introCanvas", { opacity: 0, duration: 1.0, ease: "power2.inOut", delay: 0.5 })
    .to("#introTitle", { scale: 1.2, opacity: 0, duration: 0.9, ease: "power2.in" }, "-=0.5")
    .to("#introRule,#introSub", { opacity: 0, duration: 0.6 }, "<")
    .to("#intro", { opacity: 0, duration: 0.8, onComplete: () => { $("#intro").style.display = "none"; } }, "-=0.3");
}

/* ================= 2. 主界面切换 ================= */
function enterMain() {
  const m = $("#main");
  m.style.display = "block";
  gsap.to(m, { opacity: 1, duration: 1.4, ease: "power2.out" });
  initGalaxy();
  if (!isMobile && !STATIC) initCharts(); // 手机端体征默认折叠，展开时再初始化图表；static 模式跳过实时图表
  refreshSystem();
  if (!STATIC) setInterval(refreshSystem, 5000);
  loadProjects();
  loadDaily();
  // 移动端：帝国生命体征折叠卡
  $("#vitalsToggle").addEventListener("click", () => {
    const body = $("#vitalsBody");
    const open = body.style.display !== "none" && body.style.display !== "";
    body.style.display = open ? "none" : "block";
    $("#vitalsToggle").classList.toggle("open", !open);
    if (!open && !chartInited) initCharts();
  });
  // D4 画册模式入口（仅移动端显示按钮；PC 可用 ?album=1 预览，默认关闭）
  $("#albumBtn").addEventListener("click", openAlbum);
  $("#albumClose").addEventListener("click", closeAlbum);
}

/* ================= 3. 数据加载 ================= */
let PROJECTS = [];
async function loadProjects() {
  try {
    const r = await fetch("/api/projects");
    const d = await r.json();
    PROJECTS = d.projects || [];
    buildGalaxy();
    $("#stProj").textContent = d.count;
    $("#stFiles").textContent = PROJECTS.reduce((a, p) => a + p.files, 0).toLocaleString();
    $("#stActive").textContent = PROJECTS.filter((p) => p.lastCommitDaysAgo !== null && p.lastCommitDaysAgo <= 30).length;
    // 今日战报大数字区
    $("#rpProj").textContent = d.count;
    $("#rpFiles").textContent = PROJECTS.reduce((a, p) => a + p.files, 0).toLocaleString();
    $("#rpActive").textContent = $("#stActive").textContent;
    // PC 预览入口（?album=1，默认关闭）：数据就绪后再开画册
    if (new URLSearchParams(location.search).has("album")) openAlbum();
  } catch (e) { console.error(e); }
}

/* ================= 3.5 今日帝国动态（D5）：金线卷宗 · 按项目分组 ================= */
async function loadDaily() {
  const body = $("#dailyBody"), note = $("#dailyNote"), title = $("#dailyTitle");
  try {
    const r = await fetch("/api/daily-report");
    const d = await r.json();
    const items = d.items || [];
    if (!items.length) {
      body.innerHTML = '<div class="act" style="font-size:11px;color:var(--dim)">疆域静默 · 暂无提交卷宗</div>';
      note.innerHTML = ""; return;
    }
    title.innerHTML = d.fallback
      ? `近 7 日帝国动态 <span style="font-size:10px;color:var(--dim);letter-spacing:.2em">（今日尚无御批，回退近 7 天）</span>`
      : `今日帝国动态`;
    body.innerHTML = items.map((it) => `
      <div class="dailyItem">
        <span class="dailyBadge">${it.count}</span>
        <span class="dn">${it.name}</span>
        <span class="dt">${it.time}</span>
        <span class="ds">${it.latest}</span>
      </div>`).join("");
    note.innerHTML = `<b>${d.activeProjects}</b> 疆域奏效 · 共 <b>${d.totalCommits}</b> 道御批 · 辖 ${d.scannedProjects} 疆域`;
    DAILY = d; // 供画册序言屏引用（真实御批总数）
  } catch (e) {
    body.innerHTML = '<div class="act" style="font-size:10px;color:var(--dim)">史官暂无法巡阅疆域</div>';
    console.error(e);
  }
}

/* ================= 4. three.js 鎏金帝国版图 ================= */
let scene, camera, renderer, raycaster, mouse, stars, planets = [], selected = null;
const _glowCache = {};
function glowTexture(color) {
  const key = color.getHexString();
  if (_glowCache[key]) return _glowCache[key];
  const c = document.createElement("canvas"); c.width = c.height = 128;
  const g = c.getContext("2d");
  const grad = g.createRadialGradient(64, 64, 0, 64, 64, 64);
  grad.addColorStop(0, "#" + key + "cc");
  grad.addColorStop(0.4, "#" + key + "33");
  grad.addColorStop(1, "rgba(0,0,0,0)");
  g.fillStyle = grad; g.fillRect(0, 0, 128, 128);
  const tex = new THREE.CanvasTexture(c);
  _glowCache[key] = tex;
  return tex;
}
function initGalaxy() {
  const cv = $("#galaxy");
  scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(0x0a0a0c, 0.0011);
  camera = new THREE.PerspectiveCamera(60, innerWidth / innerHeight, 1, 4000);
  // 相机对准居中主星（原点），版图整体垂直居中
  camera.position.set(0, isMobile ? 200 : 190, isMobile ? 1020 : 640);
  // T11 残余：开场动画落点 → 版图起始机位顺滑衔接（镜头从远处缓缓推近，长缓出，与开场 GSAP 同气质）
  // static 模式跳过（截图回归门要求机位即刻到位，保证基线确定性）
  if (!STATIC) {
    const camZ = camera.position.z;
    camera.position.z = camZ + (isMobile ? 380 : 300);
    gsap.to(camera.position, { z: camZ, duration: 2.6, ease: "power3.out" });
  }
  // 手机端：视线中心抬高（lookAt 更高），星系整体下沉到战报区与体征卡之间的中带，消化中下部死黑
  camera.lookAt(0, isMobile ? 120 : 0, 0);
  renderer = new THREE.WebGLRenderer({ canvas: cv, antialias: !isMobile });
  renderer.setSize(innerWidth, innerHeight);
  renderer.setPixelRatio(Math.min(devicePixelRatio, isMobile ? 1.5 : 2));
  // 远景金尘星野（暖调，非冷蓝）
  const sg = new THREE.BufferGeometry(), sc = [];
  for (let i = 0; i < (isMobile ? 1200 : 3000); i++) {
    sc.push((Math.random() - .5) * 4000, (Math.random() - .5) * 2400, (Math.random() - .5) * 4000);
  }
  sg.setAttribute("position", new THREE.Float32BufferAttribute(sc, 3));
  stars = new THREE.Points(sg, new THREE.PointsMaterial({ color: 0xc9a45c, size: 1.4, transparent: true, opacity: .28 }));
  scene.add(stars);
  // 金箔漂浮粒子层：消化左/下死黑区（近景大箔片，柔光金）
  const foilTex = (() => {
    const c = document.createElement("canvas"); c.width = c.height = 64;
    const g = c.getContext("2d");
    const rg = g.createRadialGradient(32, 32, 2, 32, 32, 30);
    rg.addColorStop(0, "rgba(232,207,154,.9)");
    rg.addColorStop(0.45, "rgba(201,164,92,.38)");
    rg.addColorStop(1, "rgba(201,164,92,0)");
    g.fillStyle = rg; g.fillRect(0, 0, 64, 64);
    return new THREE.CanvasTexture(c);
  })();
  const fg = new THREE.BufferGeometry(), fv = [];
  for (let i = 0; i < (isMobile ? 200 : 420); i++) {
    // 偏向画面左下与边缘（相机前方一层的近景箔片）
    const fx = (Math.random() - .5) * 1900 - (Math.random() < .45 ? 380 : 0);
    const fy = (Math.random() - .5) * 1000 - (Math.random() < .5 ? 260 : 0);
    const fz = 180 + Math.random() * 320;
    fv.push(fx, fy, fz);
  }
  fg.setAttribute("position", new THREE.Float32BufferAttribute(fv, 3));
  const foils = new THREE.Points(fg, new THREE.PointsMaterial({
    map: foilTex, color: 0xe8cf9a, size: isMobile ? 14 : 18, transparent: true, opacity: .5,
    depthWrite: false, blending: THREE.AdditiveBlending,
  }));
  scene.add(foils);
  window._foils = foils;
  // 暖调灯光
  scene.add(new THREE.AmbientLight(0x3a2f1c, 1.4));
  const key = new THREE.PointLight(0xe8cf9a, 1.5, 3200); key.position.set(0, 420, 200); scene.add(key);
  const fill = new THREE.PointLight(0x8a6d3b, 0.9, 2600); fill.position.set(-300, -150, 300); scene.add(fill);
  raycaster = new THREE.Raycaster(); mouse = new THREE.Vector2();
  window._cam = camera; window._planets = planets;
  let drag = false, px = 0, py = 0, moved = 0;
  const pivot = new THREE.Group(); scene.add(pivot);
  window._pivot = pivot;
  cv.addEventListener("pointerdown", (e) => { drag = true; px = e.clientX; py = e.clientY; moved = 0; cv.style.cursor = "grabbing"; });
  addEventListener("pointerup", (e) => { drag = false; cv.style.cursor = "grab"; if (moved < 5) pick(e); });
  addEventListener("pointermove", (e) => {
    if (drag) {
      const dx = e.clientX - px, dy = e.clientY - py; moved += Math.abs(dx) + Math.abs(dy);
      pivot.rotation.y += dx * 0.005;
      camera.position.y = Math.max(40, Math.min(900, camera.position.y + dy * 0.6));
      px = e.clientX; py = e.clientY;
    }
  });
  cv.addEventListener("wheel", (e) => {
    e.preventDefault();
    camera.position.z = Math.max(150, Math.min(1600, camera.position.z + e.deltaY * 0.6));
  }, { passive: false });
  addEventListener("resize", () => {
    camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix();
    renderer.setSize(innerWidth, innerHeight);
  });
  (function loop() {
    requestAnimationFrame(loop);
    if (!STATIC) { // static 模式冻结动画（截图回归门），仅渲染
      stars.rotation.y += 0.00015; // 慢
      if (window._foils) { window._foils.rotation.y += 0.00007; window._foils.position.y = Math.sin(performance.now() / 9000) * 8; }
      for (const p of planets) { p.mesh.rotation.y += 0.0025; }
      if (selected) { selected.ring.scale.setScalar(1 + Math.sin(performance.now() / 700) * 0.1); }
    }
    renderer.render(scene, camera);
  })();
}

function buildGalaxy() {
  if (!scene || !PROJECTS.length) return;
  const pivot = window._pivot;
  planets.forEach((p) => { pivot.remove(p.group); });
  planets = [];

  /* 帝国式构图：代码量最大的项目 = 居中鎏金主星；其余按体量/活跃度分配到 3 圈金轨，外圈星体递减 */
  const sorted = [...PROJECTS].sort((a, b) => (b.files + b.codeKB / 512) - (a.files + a.codeKB / 512));
  const maxFiles = sorted[0].files || 1;
  const n = sorted.length;
  const RINGS = [isMobile ? 195 : 210, isMobile ? 290 : 310, isMobile ? 385 : 410]; // 三圈金轨半径（手机放大一档填满中带）
  const main = sorted[0];
  const mainSize = isMobile ? 30 : 36;

  const mkPlanet = (p, x, y, z, size, isMain) => {
    const act = Math.min(1, p.activity / 100);
    const color = new THREE.Color().setHSL(0.095 - act * 0.018, 0.58 - act * 0.08, 0.34 + act * 0.26);
    const group = new THREE.Group();
    const mesh = new THREE.Mesh(
      new THREE.SphereGeometry(size, isMobile ? 14 : 24, isMobile ? 12 : 18),
      new THREE.MeshStandardMaterial({
        // 主星：高光压暗 + 暖金 tint（消蛋白石感，偏鎏金铸锭）
        color: isMain ? new THREE.Color(0xb08a44) : color,
        emissive: isMain ? new THREE.Color(0xc99b52) : color,
        emissiveIntensity: isMain ? 0.55 : 0.2 + act * 0.75,
        roughness: isMain ? .42 : .42, metalness: isMain ? .85 : .55,
      })
    );
    group.add(mesh);
    if (isMain || act > 0.6) {
      const glow = new THREE.Sprite(new THREE.SpriteMaterial({
        map: glowTexture(color), transparent: true, opacity: isMain ? .7 : .45,
        blending: THREE.AdditiveBlending, depthWrite: false,
      }));
      glow.material.color = new THREE.Color(isMain ? 0xc9a45c : color.getHex()); // 主星光晕也压回暖金
      glow.scale.setScalar(size * (isMain ? 6 : 5)); group.add(glow);
    }
    const ring = new THREE.Mesh(ringGeo, new THREE.MeshBasicMaterial({ color: 0xe8cf9a, transparent: true, opacity: 0, side: THREE.DoubleSide }));
    ring.rotation.x = Math.PI / 2; ring.scale.setScalar(size * 1.8); group.add(ring);
    group.position.set(x, y, z);
    group.userData = p;
    pivot.add(group);
    planets.push({ mesh, group, ring, proj: p });
  };

  const ringGeo = new THREE.RingGeometry(1.6, 2.0, 32);
  // 主星居中
  mkPlanet(main, 0, 0, 0, mainSize, true);

  // 其余星球：按体量递减分配到三圈（内圈强、外圈弱），圈内均布+黄金角抖动
  const rest = sorted.slice(1);
  const band = [Math.ceil(rest.length * 0.38), Math.ceil(rest.length * 0.34), rest.length];
  let k = 0; let placed = 0;
  for (let ri = 0; ri < 3; ri++) {
    const cnt = band[ri] - placed; placed = band[ri];
    for (let j = 0; j < cnt && k < rest.length; j++, k++) {
      const p = rest[k];
      const a = (j / cnt) * Math.PI * 2 + ri * 2.39996 + (Math.random() - .5) * 0.22;
      const r = RINGS[ri] * (0.96 + Math.random() * 0.1);
      const y = (Math.random() - .5) * (28 + ri * 16);
      const size = Math.max(3, (isMobile ? 3.2 : 4.5) + Math.sqrt(p.files / maxFiles) * (isMobile ? 11 : 15) * (1 - ri * 0.18));
      mkPlanet(p, Math.cos(a) * r, y, Math.sin(a) * r, size, false);
    }
  }
  window._planets = planets;

  // 金轨：细金环轨道线（三圈，外圈逐档提亮，强化帝国星环层次）
  const RING_OP = [0.15, 0.26, 0.38]; // 第二、三圈各提一档
  RINGS.forEach((r, ri) => {
    const pts = [];
    for (let i = 0; i <= 128; i++) {
      const a = (i / 128) * Math.PI * 2;
      pts.push(new THREE.Vector3(Math.cos(a) * r, 0, Math.sin(a) * r));
    }
    const geo = new THREE.BufferGeometry().setFromPoints(pts);
    pivot.add(new THREE.Line(geo, new THREE.LineBasicMaterial({ color: ri === 0 ? 0xc9a45c : 0xd9b878, transparent: true, opacity: RING_OP[ri] })));
  });

  // 依赖连线：细金线（近主星优先，限制数量防乱）
  const lg = new THREE.BufferGeometry(), lv = [];
  const byDep = {};
  PROJECTS.forEach((p) => p.deps.forEach((d) => (byDep[d] = byDep[d] || []).push(planets.findIndex((q) => q.proj === p))));
  const seen = new Set();
  Object.values(byDep).forEach((idxs) => {
    for (let i = 0; i < idxs.length - 1 && i < 4; i++) {
      const A = idxs[i], B = idxs[i + 1];
      if (A < 0 || B < 0) continue;
      const key = Math.min(A, B) + "-" + Math.max(A, B);
      if (seen.has(key)) continue; seen.add(key);
      const a = planets[A].group.position, b = planets[B].group.position;
      lv.push(a.x, a.y, a.z, b.x, b.y, b.z);
    }
  });
  lg.setAttribute("position", new THREE.Float32BufferAttribute(lv, 3));
  pivot.add(new THREE.LineSegments(lg, new THREE.LineBasicMaterial({ color: 0xc9a45c, transparent: true, opacity: .14 })));
}

function pick(e) {
  if (!planets.length) return;
  mouse.x = (e.clientX / innerWidth) * 2 - 1;
  mouse.y = -(e.clientY / innerHeight) * 2 + 1;
  raycaster.setFromCamera(mouse, camera);
  const hits = raycaster.intersectObjects(planets.map((p) => p.mesh));
  if (hits.length) {
    const hit = planets.find((p) => p.mesh === hits[0].object);
    planets.forEach((q) => (q.ring.material.opacity = 0));
    selected = hit; hit.ring.material.opacity = 0.85;
    showCard(hit.proj);
  }
}

function showCard(p) {
  const days = p.lastCommitDaysAgo === null ? "无 git" :
    p.lastCommitDaysAgo === 0 ? "今天" : p.lastCommitDaysAgo + " 天前";
  $("#cardBody").innerHTML = `
    <h2>${p.name}</h2>
    <div class="type">${p.type} · ${p.lang} · 活跃度 ${p.activity} / 100</div>
    <div class="rule"></div>
    <p>${p.desc}</p>
    <div class="nums">
      <div><b>${p.files}</b><i>代码文件</i></div>
      <div><b>${p.codeKB > 1024 ? (p.codeKB / 1024).toFixed(1) + "MB" : p.codeKB + "KB"}</b><i>代码体积</i></div>
      <div><b>${days}</b><i>最近提交</i></div>
    </div>
    <div>${p.deps.map((d) => `<span class="tag">${d}</span>`).join("") || '<span class="tag">独立项目</span>'}</div>
    <div class="rule"></div>
    <div id="cardCommits"><div class="act">史官查阅卷宗中…</div></div>
    <div class="act">路径：${p.path}</div>`;
  $("#cardCommits").dataset.proj = p.name; // 标记当前卡，防异步竞态
  $("#card").style.display = "block";
  gsap.fromTo("#card", { y: 24, opacity: 0 }, { y: 0, opacity: 1, duration: .7, ease: "power3.out" }); // 慢稳贵
  // 懒加载该仓库最近提交（真实 git log，后端 /api/project/<name>/commits）
  loadCommits(p.name);
}

async function loadCommits(name) {
  try {
    const r = await fetch(`/api/project/${encodeURIComponent(name)}/commits`);
    const d = await r.json();
    const box = $("#cardCommits");
    if (!box || box.dataset.proj !== name) return; // 卡片已切换到别的星球
    const cs = d.commits || [];
    if (!cs.length) { box.innerHTML = '<div class="act">此疆域暂无 git 卷宗</div>'; return; }
    box.dataset.proj = name;
    box.innerHTML = `<h3>最近御批</h3>` + cs.map((c) =>
      `<div class="commit"><b>${c.date}</b><span>${c.summary}</span></div>`).join("");
  } catch (e) { console.error(e); }
}

/* ================= 5. ECharts 金色细线心电图 + 服务金系区分色 ================= */
let chart, cpuData = [], memData = [], timeData = [], chartInited = false;
function initCharts() {
  if (chartInited) return; chartInited = true;
  chart = echarts.init($("#charts"), null, { renderer: "canvas" });
  chart.setOption({
    backgroundColor: "#0a0a0c", // 纯墨黑底，去绿灰
    grid: { left: 34, right: 8, top: 26, bottom: 18 },
    legend: { textStyle: { color: "#9a8a63", fontSize: 10, fontFamily: "Noto Sans SC" }, top: 0, itemWidth: 12 },
    xAxis: { type: "category", data: timeData, axisLine: { lineStyle: { color: "rgba(201,164,92,.35)" } }, axisLabel: { show: false } },
    yAxis: {
      type: "value", max: 100,
      splitLine: { lineStyle: { color: "rgba(201,164,92,.14)" } }, // 金网格线
      axisLabel: { color: "#9a8a63", fontSize: 9 },
    },
    series: [
      { name: "CPU%", type: "line", data: cpuData, smooth: true, showSymbol: false, color: "#e8cf9a", lineStyle: { color: "#e8cf9a", width: 1.5 }, itemStyle: { color: "#e8cf9a" }, areaStyle: { color: "rgba(232,207,154,.12)" } }, // 亮金
      { name: "内存%", type: "line", data: memData, smooth: true, showSymbol: false, color: "#c9a45c", lineStyle: { color: "#c9a45c", width: 1.5 }, itemStyle: { color: "#c9a45c" }, areaStyle: { color: "rgba(201,164,92,.10)" } }, // 主金
    ],
  });
}
async function refreshSystem() {
  try {
    const r = await fetch("/api/system");
    const d = await r.json();
    const t = new Date(d.ts).toLocaleTimeString("zh-CN", { hour12: false });
    if (d.history && d.history.cpu.length > 3) {
      const h = d.history;
      timeData = h.ts.map((x) => new Date(x).toLocaleTimeString("zh-CN", { hour12: false }));
      cpuData = h.cpu.slice(); memData = h.mem.slice();
      if (timeData[timeData.length - 1] === t) {
        cpuData[cpuData.length - 1] = d.cpu; memData[memData.length - 1] = d.mem;
      } else { timeData.push(t); cpuData.push(d.cpu); memData.push(d.mem); }
    } else {
      timeData.push(t); cpuData.push(d.cpu); memData.push(d.mem);
    }
    while (timeData.length > 30) { timeData.shift(); cpuData.shift(); memData.shift(); }
    chart && chart.setOption({ xAxis: { data: timeData }, series: [{ data: cpuData }, { data: memData }] });
    // 四服务区分色，均在金色体系内（暗金/香槟/高光金），朱砂仅用于离线
    const SVC_COLOR = { Immich: "#e8cf9a", Jellyfin: "#c9a45c", PostgreSQL: "#8a6d3b", Tailscale: "#a8874a" };
    const svc = d.services || {};
    $("#lights").innerHTML = Object.entries(svc).map(([k, v]) => {
      const c = SVC_COLOR[k] || "#c9a45c";
      const dot = v
        ? `<span class="dot on" style="background:${c};box-shadow:0 0 7px ${c}66"></span>`
        : `<span class="dot off"></span>`;
      return `<div class="light">${dot}<span style="color:${v ? c : "var(--dim)"}">${k}</span></div>`;
    }).join("") +
      `<div class="light">端口 <b style="color:var(--gold)">${d.portCount}</b></div>` +
      `<div class="light">进程 <b style="color:var(--gold)">${d.procCount}</b></div>`;
  } catch (e) { console.error(e); }
}

/* 启动 */
intro();

/* ================= 6. D4 画册模式：帝国族谱（手机竖屏一屏一战报，奢侈品画册） ================= */
let DAILY = null;            // 今日帝国动态（序言屏引用真实御批数）
let albumPages = [], albumIdx = 0, albumBusy = false;

function buildAlbumPages() {
  const sorted = [...PROJECTS].sort((a, b) => (b.activity - a.activity) || (b.files - a.files)); // 高活跃在前
  albumPages = [{ t: "prelude" }].concat(sorted.map((p) => ({ t: "proj", p }))).concat([{ t: "epilogue" }]);
}
function fmtSize(kb) { return kb > 1024 ? (kb / 1024).toFixed(1) + "MB" : kb + "KB"; }
function fmtDays(p) {
  return p.lastCommitDaysAgo === null ? "无 git" : p.lastCommitDaysAgo === 0 ? "今天" : p.lastCommitDaysAgo + " 天";
}
function albumPageHTML(pg) {
  if (pg.t === "prelude") {
    const files = PROJECTS.reduce((a, p) => a + p.files, 0).toLocaleString();
    const commits = DAILY ? DAILY.totalCommits.toLocaleString() : "—";
    return `
      <div class="kicker">序 · PREFACE</div>
      <h2>帝国族谱</h2>
      <div class="arule"></div>
      <div class="adesc">本册收录 ${PROJECTS.length} 疆域，皆本机真实扫描之产业。逐页翻阅，一域一页，如展上市公司年报。</div>
      <div class="arule"></div>
      <div class="anums">
        <div><b>${PROJECTS.length}</b><i>项目疆域</i></div>
        <div><b>${files}</b><i>代码文件</i></div>
        <div><b>${commits}</b><i>近七日御批</i></div>
      </div>
      <div class="ahint">上滑或左滑 · 翻阅下一页</div>`;
  }
  if (pg.t === "proj") {
    const p = pg.p;
    return `
      <div class="kicker">${p.type} · ${p.lang}</div>
      <h2>${p.name}</h2>
      <div class="arule"></div>
      <div class="adesc">${p.desc || "此疆域暂无描述"}</div>
      <div class="arule"></div>
      <div class="anums">
        <div><b>${p.files.toLocaleString()}</b><i>代码文件</i></div>
        <div><b>${fmtSize(p.codeKB)}</b><i>代码体积</i></div>
        <div><b>${fmtDays(p)}</b><i>最近提交</i></div>
      </div>
      <div class="abar"><i style="width:${Math.max(2, Math.min(100, p.activity))}%"></i></div>
      <div class="aact">活跃度 ${p.activity} / 100</div>
      <div class="atags">${p.deps.map((d) => `<span class="atag">${d}</span>`).join("") || '<span class="atag">独立项目</span>'}</div>
      <div class="acommits" data-proj="${p.name}"><h3>最近御批</h3><div class="commit"><span>史官查阅卷宗中…</span></div></div>
      <div class="ahint">上滑或左滑 · 继续</div>`;
  }
  // 跋：帝国生命体征摘要
  const active = PROJECTS.filter((p) => p.lastCommitDaysAgo !== null && p.lastCommitDaysAgo <= 30).length;
  const files = PROJECTS.reduce((a, p) => a + p.files, 0).toLocaleString();
  return `
    <div class="kicker">跋 · EPILOGUE</div>
    <h2>帝国生命体征</h2>
    <div class="arule"></div>
    <div class="anums">
      <div><b>${PROJECTS.length}</b><i>疆域</i></div>
      <div><b>${files}</b><i>代码文件</i></div>
      <div><b>${active}</b><i>近30天活跃</i></div>
    </div>
    <div class="arule"></div>
    <div class="adesc">数据皆来自本机实时探针与 git 御批实录。族谱终卷，静候下一次开笔。</div>
    <span class="aend" id="albumEnd">合上族谱 · 返回版图</span>`;
}
async function albumLoadCommits(box) {
  const name = box.dataset.proj;
  try {
    const r = await fetch(`/api/project/${encodeURIComponent(name)}/commits`);
    const d = await r.json();
    if (box.dataset.proj !== name) return; // 已翻页，竞态丢弃
    const cs = d.commits || [];
    box.innerHTML = "<h3>最近御批</h3>" + (cs.length
      ? cs.map((c) => `<div class="commit"><b>${c.date}</b><span>${c.summary}</span></div>`).join("")
      : '<div class="commit"><span>此疆域暂无 git 卷宗</span></div>');
  } catch (e) { console.error(e); }
}
function showAlbumPage(i, dir) {
  if (albumBusy || i < 0 || i >= albumPages.length) return;
  albumBusy = true;
  albumIdx = i;
  const stage = $("#albumStage");
  const old = stage.querySelector(".apage");
  const pg = document.createElement("div");
  pg.className = "apage";
  pg.innerHTML = albumPageHTML(albumPages[i]);
  stage.appendChild(pg);
  // 进度：细金线 + 页码（如 12/60）
  $("#albumBar").style.width = ((i + 1) / albumPages.length * 100) + "%";
  $("#albumIdx").textContent = `${i + 1} / ${albumPages.length}`;
  const off = dir < 0 ? -60 : 60;
  gsap.fromTo(pg, { y: off, opacity: 0 }, { y: 0, opacity: 1, duration: 1.1, ease: "power3.out" }); // 慢稳贵
  if (old) gsap.to(old, { y: -off * 0.6, opacity: 0, duration: 0.9, ease: "power2.in", onComplete: () => old.remove() });
  gsap.delayedCall(1.05, () => { albumBusy = false; });
  const end = pg.querySelector("#albumEnd");
  if (end) end.addEventListener("click", closeAlbum);
  const commits = pg.querySelector(".acommits");
  if (commits) albumLoadCommits(commits); // 提交摘要懒加载
  if (pg.t === undefined && albumPages[i].t === "prelude" && !DAILY) { // 御批数晚到，回填序言屏
    fetch("/api/daily-report").then((r) => r.json()).then((d) => {
      DAILY = d;
      if (albumIdx === 0 && $("#album").style.display !== "none") {
        const b = pg.querySelector(".anums div:last-child b");
        if (b) b.textContent = d.totalCommits.toLocaleString();
      }
    }).catch(() => {});
  }
}
function openAlbum() {
  if (!PROJECTS.length) return;
  buildAlbumPages();
  albumIdx = 0;
  $("#albumStage").innerHTML = "";
  $("#album").style.display = "flex";
  gsap.fromTo("#album", { opacity: 0 }, { opacity: 1, duration: 0.9, ease: "power2.out" });
  showAlbumPage(0);
}
function closeAlbum() {
  if (albumBusy) return;
  albumBusy = true;
  gsap.to("#album", { opacity: 0, duration: 0.7, ease: "power2.in", onComplete: () => {
    $("#album").style.display = "none";
    $("#albumStage").innerHTML = "";
    albumBusy = false;
  } });
}
/* 翻页手势：上下或左右滑动均可（纯戳），阈值 46px */
(() => {
  let sx = 0, sy = 0, on = false;
  const el = $("#album");
  el.addEventListener("pointerdown", (e) => { on = true; sx = e.clientX; sy = e.clientY; });
  addEventListener("pointerup", (e) => {
    if (!on) return; on = false;
    if ($("#album").style.display === "none") return;
    const dx = e.clientX - sx, dy = e.clientY - sy;
    if (dy < -46 || dx < -46) showAlbumPage(albumIdx + 1, 1);        // 上/左滑 → 下一页
    else if (dy > 46 || dx > 46) showAlbumPage(albumIdx - 1, -1);    // 下/右滑 → 上一页
  });
})();
