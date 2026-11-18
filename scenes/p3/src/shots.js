// BEAR TEST (15 s): hiker alone, a grizzly steps onto the trail, it charges, "don't run", 55 km/h race.
import * as THREE from 'three';
import { ctx, W, H, clamp, lerp, seg, eo, eio, eob } from './core/lib.js';
import { L, Le, Wd, T } from './core/timing.js';
import { camera } from './core/engine.js';
import { Human } from './core/human.js';
import { xrayMaterial } from './core/sets.js';
import { forest, Bear, trailX, dustPuffs } from './core/wild.js';
import { rbox, capsule, smin, mesh, rgb } from './core/sdf.js';
function wpill(text, x, y, sc = 1, size = 64, tx = null, ty = null) {
  if (sc <= 0) return; ctx.save();
  if (tx !== null) { ctx.strokeStyle = 'rgba(255,255,255,0.9)'; ctx.lineWidth = 5; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(tx, ty); ctx.stroke(); ctx.fillStyle = '#FF4F9A'; ctx.beginPath(); ctx.arc(tx, ty, 9, 0, 7); ctx.fill(); }
  ctx.translate(x, y); ctx.scale(sc, sc); ctx.font = `700 ${size}px Fredoka`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  const w = ctx.measureText(text).width + size * 0.9, h = size * 1.45;
  ctx.fillStyle = 'rgba(18,8,54,0.9)'; ctx.strokeStyle = '#FF4F9A'; ctx.lineWidth = 6; ctx.beginPath(); ctx.roundRect(-w / 2, -h / 2, w, h, h / 2); ctx.fill(); ctx.stroke();
  ctx.fillStyle = '#FFFFFF'; ctx.fillText(text, 0, size * 0.04); ctx.restore();
}

const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const lerpV = (a, b, k) => a.clone().lerp(b, k);
const D = THREE.MathUtils.degToRad;
function screen(p, cam) { const v = p.clone().project(cam); return [(v.x + 1) / 2 * W, (1 - v.y) / 2 * H]; }
const sm = (a, b, x) => { const t = clamp((x - a) / (b - a)); return t * t * (3 - 2 * t); };

/** running pose for a Human, ph in cycles */
function run(h, ph, amt = 1) {
  const a = ph * Math.PI * 2, s = Math.sin(a);
  h.pose({ hipL: [s * 48 * amt + 8, 0, 2], hipR: [-s * 48 * amt + 8, 0, 2], knL: (Math.max(0, -Math.sin(a + 0.9)) * 100 + 12) * amt, knR: (Math.max(0, Math.sin(a + 0.9)) * 100 + 12) * amt,
    shL: [-s * 55 * amt, 0, 10], shR: [s * 55 * amt, 0, 10], elL: 80 * amt + 10, elR: 80 * amt + 10, spine: [14 * amt, s * 6, 0], head: [-8 * amt, -s * 3, 0], lid: -0.2 });
  h.hips.position.y = 0.93 - 0.04 * amt + Math.abs(Math.cos(a)) * 0.05 * amt;
}
function backpack() {
  const g = mesh((p) => smin(rbox(p, [0, 0.3, -0.16], [0.11, 0.14, 0.05], 0.035), capsule(p, [-0.11, 0.4, -0.17], [0.11, 0.4, -0.17], 0.022), 0.02), [[-0.22, 0.08, -0.3], [0.22, 0.52, -0.08]], 0.008, () => rgb('#C2552D'));
  const m = new THREE.Mesh(g, new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.7 })); m.castShadow = m.receiveShadow = true; return m;
}

export function buildShots(E) {
  const S = [], CUES = [], add = (o) => (S.push(o), o), cue = (t, type, o = {}) => CUES.push({ t: +t.toFixed(3), type, ...o });
  const cut = (i) => (i === 0 ? 0 : L(i) - 0.08);
  const cam = camera(30);
  const LOOK = { aperture: 0.002, maxblur: 0.008, bloom: 0.12, bloomThreshold: 0.9, warm: 0.0, vignette: 0.3, grain: 0.015 };

  // ── world ──────────────────────────────────────────────────────────
  const F = forest(E), scene = F.scene;
  const hero = new Human({ skin: '#C08458', shirt: '#6FA4C2', pants: '#4B2F5A', shoes: '#F2EEF4', hair: '#3B2420', iris: '#2A1A10' });
  hero.spine.add(backpack()); scene.add(hero.group);
  const mouthO = new THREE.Mesh(new THREE.SphereGeometry(0.02, 24, 16), new THREE.MeshStandardMaterial({ color: '#3A1420', roughness: 0.6 })); mouthO.position.set(0, 0.054, 0.121); mouthO.scale.set(1, 0.01, 0.5); hero.head.add(mouthO);
  const gasp = (k) => { mouthO.visible = k > 0.02; mouthO.scale.set(1.0 + 0.3 * k, 0.2 + 1.0 * k, 0.5); };
  const bear = new Bear(); scene.add(bear.group);
  const ghost = new Human({ face: false }); ghost.setAllMaterial(xrayMaterial('#57D8F0', 1.25)); ghost.group.visible = false; scene.add(ghost.group);
  const dust = dustPuffs(scene, 48);
  const render = (focus, extra = {}) => E.render(scene, cam, { ...LOOK, focus, ...extra });

  // ── story timeline (pure functions of film time t) ──────────────────
  const tStop = Wd('bear', 1) + 0.35;
  const HZ0 = 3.2, HV = 1.05;
  const heroZ = (t) => HZ0 - HV * Math.min(t, tStop) - HV * 0.25 * clamp((t - tStop) / 0.5) ** 0.5;
  const placeHero = (t) => { const z = heroZ(t); hero.group.position.set(trailX(z) + 0.15, 0, z); hero.group.rotation.set(0, Math.PI, 0); };
  const BZ = -10, BX0 = trailX(BZ) - 3.1, BX1 = trailX(BZ) - 0.15;
  const tOut0 = Wd('steps', 1) - 0.35, tOut1 = Le(1) + 0.15;
  const tTurn = Wd('charges', 3) - 0.3, tGo = tTurn + 0.35;
  const bearZ = (t) => { if (t < tGo) return BZ; const u = t - tGo; return BZ + 3.6 * u * u / (1 + u); };
  function placeBear(t) {
    bear.headYaw = 0; bear.headPitch = 0; bear.jaw = 0;
    if (t < tTurn) {
      const k = sm(tOut0, tOut1, t); bear.group.position.set(lerp(BX0, BX1, k), 0, BZ); bear.group.rotation.set(0, Math.PI / 2, 0);
      const look = sm(Wd('sees', 2) - 0.25, Wd('you', 2) + 0.1, t);
      bear.headYaw = -62 * look; bear.headPitch = 6 * look - 4 * (1 - look);
      if (t > tOut0 && t < tOut1 + 0.3) bear.walk((t - tOut0) * 0.85, sm(tOut0, tOut0 + 0.3, t) * (1 - sm(tOut1, tOut1 + 0.3, t))); else bear.stand();
    } else {
      const k = sm(tTurn, tGo, t), z = bearZ(t); bear.group.position.set(lerp(BX1, trailX(z), sm(tGo, tGo + 0.6, t)), 0, z); bear.group.rotation.set(0, Math.PI / 2 * (1 - k), 0);
      bear.headYaw = -62 * (1 - k); bear.headPitch = -6; bear.jaw = 0.6 * sm(tTurn - 0.1, tTurn + 0.15, t) * (1 - sm(tGo + 0.4, tGo + 0.7, t)) + 0.15;
      if (t < tGo) { bear.stand(); bear.body.position.y = 0.9 - 0.08 * k; bear.body.rotation.x = D(6 * k); } else bear.gallop((t - tGo) * 1.45, sm(tGo, tGo + 0.25, t));
    }
  }
  function placeAll(t) { placeHero(t); placeBear(t); F.update(t, cam); gasp(sm(Wd('bear', 1), Wd('bear', 1) + 0.3, t)); }
  const heroWalk = (t) => { if (t < tStop) hero.walk(t * 1.75 * Math.PI, 1); else { const k = sm(tStop, tStop + 0.4, t); hero.pose({ spine: [-4 * k, 0, 0], head: [-5 * k, 0, 0], shL: [8 * k, 0, 8], shR: [8 * k, 0, 8], elL: 20, elR: 20, lid: -0.3 * k }); hero.hips.position.y = 0.93; } };
  const dustEv = (z0, v, t0) => Array.from({ length: 48 }, (_, i) => { const tt = t0 + i * 0.07, zz = z0(tt); return { t0: tt, x: trailX(zz) + (i % 2 ? 0.25 : -0.25), z: zz - 0.4 }; });

  // 1 · "You're hiking alone…" aerial drop over the pines onto the tiny hiker
  { const st = cut(0);
    add({ id: 'S01', at: st, note: 'aerial: descend through pines onto lone hiker', draw(lt, d, t, blit) {
      placeAll(t); heroWalk(t); const hp = hero.group.position.clone();
      const k = eio(clamp(lt / d)); cam.fov = 34; cam.updateProjectionMatrix();
      cam.position.copy(lerpV(V3(hp.x + 7, 26, hp.z + 15), V3(hp.x + 3.2, 10, hp.z + 8.5), k)); cam.lookAt(hp.x - 0.6, 0.4, hp.z - 4 + 2 * k);
      F.aim(hp, 16); render(cam.position.distanceTo(hp), { aperture: 0.0012 }); blit();
    } });
    cue(st + 0.05, 'wind', { dur: 3.8, gain: 0.9 }); cue(st + 0.1, 'whoosh', { gain: 0.6 }); }

  // 2 · "…and a bear steps onto the trail." low over-the-shoulder, focus pulls from hiker to bear
  { const st = cut(1), tb = Wd('bear', 1);
    add({ id: 'S02', at: st, note: 'over-shoulder: bear steps out of bushes, focus pull', draw(lt, d, t, blit) {
      placeAll(t); heroWalk(t); const hp = hero.group.position.clone();
      cam.fov = 24; cam.updateProjectionMatrix();
      cam.position.set(hp.x + 0.95 - 0.12 * eio(lt / d), 1.55 - 0.06 * eio(lt / d), hp.z + 2.5 - 0.35 * eio(lt / d)); cam.lookAt(trailX(BZ) - 1.0, 0.85, BZ);
      const fk = sm(tb - 0.1, tb + 0.45, t), fd = lerp(1.6, cam.position.distanceTo(bear.group.position), fk);
      F.aim(V3(hp.x - 0.5, 0, (hp.z + BZ) / 2), 10); render(fd, { aperture: 0.004, maxblur: 0.014 }); blit();
    } });
    for (let k = 0; k < 4; k++) cue(Wd('steps', 1) + k * 0.3, 'step', { gain: 0.45, pan: -0.3 });
    cue(tb + 0.05, 'heartbeat', { gain: 0.5 }); }

  // 3 · "It sees you." bear head close-up; head swings round and locks on
  { const st = cut(2);
    add({ id: 'S03', at: st, note: 'bear head close-up, head turns to camera, eyes lock', draw(lt, d, t, blit) {
      placeAll(t); heroWalk(t); bear.group.updateMatrixWorld(true);
      const H0 = new THREE.Vector3(); bear.head.getWorldPosition(H0); const k = eio(clamp(lt / d));
      cam.fov = 22; cam.updateProjectionMatrix();
      cam.position.copy(lerpV(V3(H0.x + 1.7, H0.y + 0.15, H0.z + 3.8), V3(H0.x + 1.1, H0.y + 0.1, H0.z + 2.8), k)); cam.lookAt(H0.x + 0.1, H0.y - 0.02, H0.z + 0.05);
      F.aim(H0, 4); render(cam.position.distanceTo(H0) - 0.1, { aperture: 0.006, maxblur: 0.016 }); blit();
    } });
    cue(Wd('sees', 2), 'growl', { dur: 1.3, gain: 0.55 }); }

  // 4 · "And it charges." ground-level front (roar + launch), then telephoto behind the hiker
  { const st = cut(3), t2 = tGo + 0.75;
    add({ id: 'S04a', at: st, note: 'ground-level front: bear turns, roars, launches toward lens', draw(lt, d, t, blit) {
      placeAll(t); heroWalk(t); const bp = bear.group.position.clone();
      cam.fov = 30; cam.updateProjectionMatrix(); const k = eio(clamp(lt / d));
      cam.position.set(trailX(BZ + 3.2) + 0.9 - 0.3 * k, 0.32 + 0.05 * k, BZ + 3.6 + 0.8 * k); cam.lookAt(bp.x, 0.75, bp.z);
      dust(t, dustEv(bearZ, 0, tGo));
      F.aim(bp, 6); render(cam.position.distanceTo(bp) - 0.4, { aperture: 0.004 }); blit();
    } });
    add({ id: 'S04b', at: t2, note: 'telephoto behind hiker: bear charging straight at him', draw(lt, d, t, blit) {
      placeAll(t); heroWalk(t); const hp = hero.group.position.clone(), bp = bear.group.position.clone();
      cam.fov = 17; cam.updateProjectionMatrix(); const k = eio(clamp(lt / d));
      cam.position.set(hp.x + 1.7 - 0.25 * k, 1.3, hp.z + 4.6 - 0.9 * k); cam.lookAt(bp.x + 0.2, 0.9, bp.z);
      dust(t, dustEv(bearZ, 0, tGo));
      F.aim(V3(hp.x, 0, (hp.z + bp.z) / 2), 8); render(cam.position.distanceTo(bp), { aperture: 0.0025 }); blit();
    } });
    cue(tTurn, 'growl', { dur: 1.1, gain: 1.0 }); cue(tGo, 'slam', { gain: 0.5 });
    for (let k = 0; k < 9; k++) cue(tGo + 0.1 + k * 0.34, 'thud', { gain: 0.35 + k * 0.05 }); }

  // 5 · "Your brain screams run." face close-up, dolly zoom, eyes wide, he twists to run
  { const st = cut(4), tr = Wd('run', 4);
    add({ id: 'S05', at: st, note: 'hiker face dolly-zoom, eyes wide, twists to flee on "run"', draw(lt, d, t, blit) {
      placeAll(t); const hp = hero.group.position.clone(); const tw = sm(tr - 0.2, tr + 0.35, t);
      hero.pose({ spine: [-4, 25 * tw, 0], head: [-6, 55 * tw, 0], shL: [10, 0, 10 + 10 * tw], shR: [10 + 25 * tw, 0, 10], elL: 30, elR: 30 + 50 * tw, lid: -0.32, look: [40 * tw, 2], hipR: [12 * tw, 0, 2], knR: 20 * tw });
      const FACE = hp.clone().add(V3(0, 1.66, 0)); const k = eio(clamp(lt / d)), dist = lerp(2.6, 0.75, k);
      cam.fov = 2 * Math.atan(0.42 / dist) * 180 / Math.PI; cam.updateProjectionMatrix();
      cam.position.set(FACE.x - 0.12, FACE.y + 0.02, FACE.z - dist); cam.lookAt(FACE.x, FACE.y - 0.04, FACE.z);
      F.aim(hp, 4); render(dist, { aperture: 0.004 }); blit();
    } });
    cue(st, 'heartbeat', { gain: 0.9 }); cue(st + 0.85, 'heartbeat', { gain: 1.0 }); cue(tr - 0.2, 'whoosh', { gain: 0.8 }); }

  // 6 · "Don't." bullet-time freeze: hiker mid-turn, bear mid-stride, world drains of colour, red X
  { const st = cut(5), tf = st;
    add({ id: 'S06', at: st, note: 'freeze frame side orbit, desaturated, red X over the runner', draw(lt, d, t, blit) {
      placeAll(tf); const hp = hero.group.position.clone();
      hero.group.rotation.y = Math.PI * 0.4; run(hero, 0.2, 1);
      bear.group.position.z = Math.min(bear.group.position.z, hp.z - 4.2); bear.gallop(0.35, 1);
      const mid = V3(hp.x - 0.1, 1.0, hp.z - 1.4), k = eio(clamp(lt / d));
      cam.fov = 34; cam.updateProjectionMatrix(); const a = lerp(0.2, 0.38, k);
      cam.position.set(mid.x + Math.sin(a) * 6.0, 1.45, mid.z + Math.cos(a) * 6.0); cam.lookAt(mid);
      F.aim(mid, 7); render(cam.position.distanceTo(hp), { aperture: 0.0012 });
      ctx.filter = 'saturate(0.12) contrast(1.15) brightness(0.92)'; blit(); ctx.filter = 'none';
      const g = ctx.createRadialGradient(540, 900, 300, 540, 960, 1150); g.addColorStop(0, 'rgba(120,0,0,0)'); g.addColorStop(1, 'rgba(150,10,10,0.35)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
      const [sx, sy] = screen(hp.clone().add(V3(0, 0.95, 0)), cam), s = eob(seg(lt, 0.02, 0.22));
      if (s > 0) { ctx.save(); ctx.translate(sx, sy); ctx.scale(s, s); ctx.lineCap = 'round'; for (const [w, c] of [[60, 'rgba(0,0,0,0.5)'], [40, '#E0242F']]) { ctx.lineWidth = w; ctx.strokeStyle = c; ctx.beginPath(); ctx.moveTo(-150, -150); ctx.lineTo(150, 150); ctx.moveTo(150, -150); ctx.lineTo(-150, 150); ctx.stroke(); } ctx.restore(); }
    } });
    cue(st + 0.02, 'slam', { gain: 0.9 }); }

  // 7 · "A bear can hit around 55 km/h" side tracking shot at full gallop, speed counter
  { const st = cut(6), tn = Wd('fifty', 6), Z0 = -44, V = 11;
    add({ id: 'S07', at: st, note: 'side tracking: full gallop through pines, 55 km/h counter', draw(lt, d, t, blit) {
      placeAll(t); hero.group.visible = false;
      const z = Z0 + V * lt; bear.group.position.set(trailX(z), 0, z); bear.group.rotation.set(0, Math.atan(0.05 * Math.cos(z * 0.07)), 0); bear.headYaw = 0; bear.headPitch = -4; bear.jaw = 0.25; bear.gallop(lt * 1.9, 1);
      const k = eio(clamp(lt / d)); cam.fov = 40 - 6 * k; cam.updateProjectionMatrix();
      cam.position.set(trailX(z) + 3.9 - 0.4 * k, 0.8 + 0.15 * Math.sin(lt * 2), z + 2.2 - 1.2 * k); cam.lookAt(trailX(z) + 0.1, 0.95, z + 0.55);
      dust(t, dustEv((tt) => Z0 + V * (tt - st), 0, st));
      F.aim(bear.group.position, 6); render(cam.position.distanceTo(bear.group.position), { aperture: 0.003 }); blit(); hero.group.visible = true;
      const v = Math.round(55 * eo(clamp((t - tn + 0.15) / 0.75)));
      if (t > tn - 0.3) wpill(`${v === 55 ? '~' : ''}${v} KM/H`, 540, 420, eob(seg(t, tn - 0.3, tn)), 84);
    } });
    cue(tn - 0.3, 'zip', { gain: 0.9 }); for (let k = 0; k < 8; k++) cue(st + 0.1 + k * 0.36, 'thud', { gain: 0.45 }); }

  // 8 · "…faster than any human alive." race: bear vs a glowing ghost of the fastest human; the bear pulls away
  { const st = cut(7), Z0 = -40, VB = 9.6, VH = 9.6 * 45 / 55;
    add({ id: 'S08', at: st, note: 'race: bear vs cyan ghost sprinter, bear pulls ahead, labels', draw(lt, d, t, blit) {
      placeAll(t); hero.group.visible = false; ghost.group.visible = true;
      const zb = Z0 + 0.4 + VB * lt, zh = Z0 + 1.2 + VH * lt;
      bear.group.position.set(trailX(zb) - 0.5, 0, zb); bear.group.rotation.set(0, 0, 0); bear.headYaw = 0; bear.headPitch = -4; bear.jaw = 0.2; bear.gallop(lt * 1.75, 1);
      ghost.group.position.set(trailX(zh) + 0.6, 0, zh); ghost.group.rotation.set(0, 0, 0); ghost.group.scale.setScalar(1.05); run(ghost, lt * 2.3, 1);
      const zm = zb - 1.6, k = eio(clamp(lt / d)); cam.fov = 36; cam.updateProjectionMatrix();
      cam.position.set(trailX(zb + 6) + 1.3 - 0.4 * k, 1.05, zb + 6.4 - 0.6 * k); cam.lookAt(trailX(zm) - 0.05, 0.95, zm);
      F.aim(V3(trailX(zm), 0, zm), 7); render(cam.position.distanceTo(bear.group.position), { aperture: 0.002 }); blit();
      hero.group.visible = true; ghost.group.visible = false;
      const a = eob(seg(lt, 0.15, 0.45)), b = eob(seg(lt, 0.3, 0.6));
      const [bx, by] = screen(V3(trailX(zb) - 0.5, 1.45, zb + 0.3), cam), [gx, gy] = screen(V3(trailX(zh) + 0.6, 1.95, zh), cam);
      wpill('BEAR ~55 KM/H', 330, 420, a, 50, bx, by);
      wpill('FASTEST HUMAN ~45', 690, 600, b, 46, gx, gy);
    } });
    cue(st, 'whoosh', { gain: 0.8 }); for (let k = 0; k < 8; k++) cue(st + 0.1 + k * 0.36, 'thud', { gain: 0.4 }); }

  return { shots: S, cues: CUES };
}
