// BEAR TEST, cartoon cut-out version: hiker alone, a grizzly steps onto the trail, it charges, "don't run", 55 km/h.
import * as THREE from 'three';
import { ctx, W, H, clamp, lerp, seg, eo, eio, eob } from './core/lib.js';
import { L, Le, Wd, T } from './core/timing.js';
import { camera } from './core/engine.js';
import { Toon } from './core/toon.js';
import { BearToon, forestSet, trailX, headline } from './core/bear2d.js';

const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const mix = (a, b, k) => a.clone().lerp(b, k);
const sm = (a, b, x) => { const t = clamp((x - a) / (b - a)); return t * t * (3 - 2 * t); };
const blink = (t, off = 0) => (((t + off) % 3.1) < 0.12 ? 1 : 0);
function screen(p, cam) { const v = p.clone().project(cam); return [(v.x + 1) / 2 * W, (1 - v.y) / 2 * H]; }

function tag(text, x, y, tx, ty, sc, col = '#FFFFFF') {
  if (sc <= 0) return; ctx.save(); ctx.globalAlpha = Math.min(1, sc);
  ctx.strokeStyle = '#1A1226'; ctx.lineWidth = 7; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(tx, ty); ctx.stroke();
  ctx.translate(x, y); ctx.scale(sc, sc); ctx.font = '900 54px Inter'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.lineJoin = 'round';
  ctx.lineWidth = 12; ctx.strokeText(text, 0, 0); ctx.fillStyle = col; ctx.fillText(text, 0, 0); ctx.restore();
}

export function buildShots(E) {
  const S = [], CUES = [], add = (o) => (S.push(o), o), cue = (t, type, o = {}) => CUES.push({ t: +t.toFixed(3), type, ...o });
  const cut = (i) => (i === 0 ? 0 : L(i) - 0.08);
  const cam = camera(36);
  const LOOK = { bloom: 0.2, aperture: 0.0009, maxblur: 0.006 };
  const F = forestSet(E), scene = F.scene;
  const hero = new Toon({ body: '#1E9E9B', head: '#C08A62', hat: 'hair', hatCol: '#2A1B12', kid: true, neck: 'collar', neckCol: '#E8E2D6' }, { height: 1.45 });
  const runner = new Toon({ body: '#F2C230', pattern: 'stripes', patCol: '#D8343F', head: '#F7F7FA', hat: 'visor', hatCol: '#D8343F' }, { height: 1.8 });
  const bear = new BearToon({ size: 2.5 });
  scene.add(hero.group, runner.group, bear.group); runner.group.visible = false;
  const shoot = (people, from, to, at, at2, k, fov = 36, extra = {}) => {
    if (cam.fov !== fov) { cam.fov = fov; cam.updateProjectionMatrix(); }
    cam.position.copy(mix(from, to, k)); const a = at2 ? mix(at, at2, k) : at; cam.lookAt(a);
    people.forEach((p) => p.face(cam)); F.aim(V3(a.x, 0, a.z));
    E.render(scene, cam, { ...LOOK, focus: cam.position.distanceTo(a), ...extra });
  };
  // is a thing moving along `dir` going left on screen? (side-view drawings face right)
  const goesLeft = (p, dir) => { const a = screen(p, cam)[0], b = screen(p.clone().add(dir), cam)[0]; return b < a; };

  // ── story timeline ──────────────────────────────────────────────
  const tStop = Wd('bear', 1) + 0.3, HZ0 = 3.2, HV = 1.1;
  const heroZ = (t) => HZ0 - HV * Math.min(t, tStop);
  const BZ = -10, BX0 = trailX(BZ) - 3.2, BX1 = trailX(BZ) - 0.2;
  const tOut0 = Wd('steps', 1) - 0.35, tOut1 = Le(1) + 0.2;
  const tTurn = Wd('charges', 3) - 0.3, tGo = tTurn + 0.35;
  const bearZ = (t) => (t < tGo ? BZ : BZ + 7.2 * (1 - Math.exp(-((t - tGo) ** 1.4) * 0.45)));
  function place(t) {
    const hz = heroZ(t); hero.at(trailX(hz) + 0.25, 0, hz);
    const walking = t < tStop;
    hero.set({ legs: walking ? 'walk' : 'stand', phase: t * 9, mood: t < Wd('bear', 1) ? 'happy' : 'shock', blink: blink(t), sweat: t > Wd('charges', 3) ? 1 : 0, look: [0.4, 0], armL: [10, 8], armR: [10, 8] });
    if (t < tTurn) { const k = sm(tOut0, tOut1, t); bear.at(lerp(BX0, BX1, k), 0, BZ); }
    else bear.at(lerp(BX1, trailX(bearZ(t)), sm(tGo, tGo + 0.5, t)), 0, bearZ(t));
    if (t < tTurn) bear.set({ view: 'side', gait: t > tOut0 && t < tOut1 ? 'walk' : 'stand', phase: t * 7, mood: 'alert' });
    else bear.set({ view: 'front', gait: t > tGo ? 'run' : 'stand', phase: (t - tGo) * 14, mouth: 0.25, mood: 'angry' });
  }

  // 1 · "You're hiking alone…" high wide over the pines, tiny hiker on the trail
  { const st = cut(0);
    add({ id: 'S01', at: st, note: 'high wide crane-down: lone hiker on a winding trail', draw(lt, d, t, blit) {
      place(t); const hp = hero.group.position.clone(); bear.group.visible = false;
      shoot([hero], V3(hp.x + 2.5, 14, hp.z + 16), V3(hp.x + 2.0, 4.6, hp.z + 8.5), V3(hp.x - 1, 1.2, hp.z - 6), V3(hp.x - 0.4, 1.0, hp.z - 2), eio(clamp(lt / d)), 40); blit();
      bear.group.visible = true;
    } });
    cue(st + 0.05, 'chirp', { gain: 0.5 }); cue(st + 0.6, 'chirp', { gain: 0.4 }); cue(st + 0.1, 'whoosh', { gain: 0.5 }); }

  // 2 · "…and a bear steps onto the trail." hiker foreground, bear walks out of the bushes behind
  { const st = cut(1), tb = Wd('bear', 1);
    add({ id: 'S02', at: st, note: 'hiker foreground right, bear steps out of bushes onto trail', draw(lt, d, t, blit) {
      place(t); const hp = hero.group.position.clone(), k = eio(clamp(lt / d));
      const walkB = t > tOut0 && t < tOut1;
      cam.position.copy(mix(V3(hp.x + 2.6, 1.5, hp.z + 3.4), V3(hp.x + 2.2, 1.35, hp.z + 2.9), k));
      bear.set({ view: 'side', gait: walkB ? 'walk' : 'stand', phase: t * 7, mood: t > tOut1 ? 'alert' : 'calm', flip: goesLeft(bear.group.position, V3(1, 0, 0)) });
      shoot([hero, bear], V3(hp.x + 2.6, 1.5, hp.z + 3.4), V3(hp.x + 2.2, 1.35, hp.z + 2.9), V3(trailX(BZ) - 0.6, 1.0, (hp.z + BZ) / 2 - 1), null, k, 34, { focus: cam.position.distanceTo(bear.group.position) * 0.7 }); blit();
    } });
    for (let k = 0; k < 4; k++) cue(Wd('steps', 1) + k * 0.32, 'plop', { gain: 0.35 });
    cue(tb, 'boing', { gain: 0.5 }); }

  // 3 · "It sees you." bear close-up, front on; eyes narrow on "you"
  { const st = cut(2), ty = Wd('you', 2);
    add({ id: 'S03', at: st, note: 'bear face close-up, push in, eyes go angry on "you"', draw(lt, d, t, blit) {
      place(t); const bp = bear.group.position.clone(), k = eio(clamp(lt / d));
      bear.set({ view: 'front', mood: t < ty - 0.05 ? 'alert' : 'angry', bob: Math.sin(t * 3) * 4 });
      shoot([hero, bear], V3(bp.x + 0.5, 1.3, bp.z + 4.4), V3(bp.x + 0.25, 1.28, bp.z + 2.9), V3(bp.x, 1.2, bp.z), null, k, 34); blit();
    } });
    cue(ty, 'stamp', { gain: 0.6 }); }

  // 4a · "And it charges." roar, then it runs at the lens
  { const st = cut(3), t2 = tGo + 0.75;
    add({ id: 'S04a', at: st, note: 'bear roars (mouth wide), then gallops straight at the camera', draw(lt, d, t, blit) {
      place(t); const bp = bear.group.position.clone(), k = eio(clamp(lt / d));
      const roar = sm(tTurn - 0.05, tTurn + 0.15, t) * (1 - sm(tGo + 0.3, tGo + 0.5, t));
      bear.set({ view: 'front', gait: t > tGo ? 'run' : 'stand', phase: (t - tGo) * 14, mouth: roar * 0.9 + 0.1 * (t > tGo), mood: 'angry' });
      const cz = BZ + 5.2 + 1.6 * k;
      shoot([hero, bear], V3(trailX(cz) + 0.6, 0.75, cz), V3(trailX(cz) + 0.4, 0.7, cz), V3(bp.x, 0.95, bp.z), null, 0, 38, { focus: cam.position.distanceTo(bp) }); blit();
    } });
    add({ id: 'S04b', at: t2, note: 'wide: sweating hiker foreground, bear charging up the trail at him', draw(lt, d, t, blit) {
      place(t); const hp = hero.group.position.clone(), k = eio(clamp(lt / d));
      bear.set({ view: 'front', gait: 'run', phase: (t - tGo) * 14, mouth: 0.25, mood: 'angry' });
      shoot([hero, bear], V3(hp.x - 1.3, 1.25, hp.z + 3.2), V3(hp.x - 1.0, 1.15, hp.z + 2.5), V3(hp.x + 0.3, 1.0, hp.z - 3), null, k, 40, { focus: 3.2 }); blit();
    } });
    cue(tTurn - 0.05, 'growl', { dur: 1.1, gain: 1.0 }); cue(tGo, 'slam', { gain: 0.5 }); for (let k = 0; k < 8; k++) cue(tGo + 0.12 + k * 0.3, 'thud', { gain: 0.3 + k * 0.04 }); }

  // 5 · "Your brain screams run." hiker close-up, shock + sweat, RUN! pops on the word
  { const st = cut(4), tr = Wd('run', 4);
    add({ id: 'S05', at: st, note: 'hiker close-up shock, RUN! header pops, he flips to flee', draw(lt, d, t, blit) {
      place(t); const hp = hero.group.position.clone(), k = eio(clamp(lt / d));
      const go = t > tr + 0.15;
      hero.set({ legs: go ? 'run' : 'stand', phase: t * 14, mood: 'shock', sweat: 1, blink: 0, look: go ? [-0.8, 0] : [0.6, -0.2], lean: go ? -10 : 0, flip: go, armL: go ? [60, 70] : [25, 40], armR: go ? [60, 70] : [25, 40] });
      shoot([hero, bear], V3(hp.x + 0.5, 1.15, hp.z + 3.0), V3(hp.x + 0.25, 1.15, hp.z + 1.7), V3(hp.x, 1.05, hp.z), null, k, 36); blit();
      headline(ctx, 'RUN!', null, 380, eob(seg(t, tr - 0.05, tr + 0.2)) * (1 + 0.04 * Math.sin(t * 30)), '#FF4A3D');
    } });
    cue(tr - 0.03, 'boing', { gain: 0.6 }); cue(st + 0.1, 'heartbeat', { gain: 0.7 }); }

  // 6 · "Don't." freeze: hiker mid-run, bear behind, colour drains, red X, DON'T RUN
  { const st = cut(5), tf = st;
    add({ id: 'S06', at: st, note: 'freeze frame, desaturated, red X over the runner, DON\'T RUN header', draw(lt, d, t, blit) {
      place(tf); const hp = hero.group.position.clone(), k = eio(clamp(lt / d));
      hero.set({ legs: 'run', phase: 1.2, mood: 'shock', sweat: 1, lean: -12, flip: true, armL: [60, 70], armR: [60, 70] });
      bear.at(trailX(hp.z - 3.6) - 0.2, 0, hp.z - 3.6); bear.set({ view: 'front', gait: 'run', phase: 1.0, mouth: 0.3, mood: 'angry' });
      shoot([hero, bear], V3(hp.x + 2.4, 1.4, hp.z + 4.2), V3(hp.x + 2.1, 1.35, hp.z + 3.7), V3(hp.x - 0.4, 1.0, hp.z - 1.4), null, k, 40, { sat: 0.08, focus: 4.5 }); blit();
      const [sx, sy] = screen(hp.clone().add(V3(0, 0.75, 0)), cam), s = eob(seg(lt, 0.02, 0.2));
      if (s > 0) { ctx.save(); ctx.translate(sx, sy); ctx.scale(s, s); ctx.lineCap = 'round'; for (const [w, c] of [[64, '#1A1226'], [42, '#E8323C']]) { ctx.lineWidth = w; ctx.strokeStyle = c; ctx.beginPath(); ctx.moveTo(-160, -160); ctx.lineTo(160, 160); ctx.moveTo(160, -160); ctx.lineTo(-160, 160); ctx.stroke(); } ctx.restore(); }
      headline(ctx, "DON'T RUN", 'IT TRIGGERS THE CHASE', 360, eob(seg(lt, 0.05, 0.3)));
    } });
    cue(st + 0.02, 'stamp', { gain: 0.9 }); }

  // 7 · "A bear can hit around 55 km/h" side tracking at full gallop, 55 KM/H header counts up
  { const st = cut(6), tn = Wd('fifty', 6), Z0 = -58, V = 9;
    add({ id: 'S07', at: st, note: 'side tracking: bear full gallop past pines, 55 KM/H counter header', draw(lt, d, t, blit) {
      place(t); hero.group.visible = false;
      const z = Z0 + V * lt, k = eio(clamp(lt / d)); bear.at(trailX(z), 0, z);
      cam.position.set(trailX(z) + 7.2, 1.3, z - 1.5);
      bear.set({ view: 'side', gait: 'run', phase: lt * 15, mouth: 0.15, mood: 'angry', flip: goesLeft(bear.group.position, V3(0, 0, 1)) });
      shoot([bear], V3(trailX(z) + 7.2, 1.35, z - 1.4), V3(trailX(z) + 6.4, 1.2, z - 0.4), V3(trailX(z), 0.95, z), null, k, 36); blit(); hero.group.visible = true;
      const v = Math.round(55 * eo(clamp((t - tn + 0.1) / 0.7)));
      if (t > tn - 0.25) headline(ctx, `${v} KM/H`, 'GRIZZLY TOP SPEED', 360, eob(seg(t, tn - 0.25, tn + 0.05)));
    } });
    cue(tn - 0.2, 'zip', { gain: 0.8 }); for (let k = 0; k < 9; k++) cue(st + 0.1 + k * 0.32, 'thud', { gain: 0.35 }); }

  // 8 · "…faster than any human alive." side race: bear vs a sprinter, the bear pulls away
  { const st = cut(7), Z0 = -52, VB = 7, VH = 7 * 45 / 55;
    add({ id: 'S08', at: st, note: 'side race: bear vs sprinter, bear pulls ahead, speed tags', draw(lt, d, t, blit) {
      place(t); hero.group.visible = false; runner.group.visible = true;
      const zb = Z0 + 0.6 + VB * lt, zh = Z0 - 0.6 + VH * lt, k = eio(clamp(lt / d)), zm = (zb + zh) / 2 + 0.3;
      bear.at(trailX(zb) + 0.5, 0, zb); runner.at(trailX(zh) - 0.9, 0, zh);
      cam.position.set(trailX(zm) + 11.5, 1.6, zm - 1);
      const left = goesLeft(V3(trailX(zm), 0, zm), V3(0, 0, 1));
      bear.set({ view: 'side', gait: 'run', phase: lt * 15, mouth: 0.15, mood: 'angry', flip: left });
      runner.set({ legs: 'run', phase: lt * 16, mood: lt > 1.2 ? 'worried' : 'proud', sweat: lt > 1.2 ? 1 : 0, lean: left ? -12 : 12, flip: left, armL: [50, 80], armR: [50, 80] });
      shoot([bear, runner], V3(trailX(zm) + 11.5, 1.6, zm - 1), V3(trailX(zm) + 10.8, 1.45, zm - 0.4), V3(trailX(zm), 1.0, zm), null, k, 40); blit();
      hero.group.visible = true; runner.group.visible = false;
      const [bx, by] = screen(V3(trailX(zb) + 0.5, 1.55, zb), cam), [rx, ry] = screen(V3(trailX(zh) - 0.9, 1.9, zh), cam);
      tag('55 KM/H', Math.max(200, Math.min(800, bx)), Math.max(600, by - 130), bx, by - 20, eob(seg(lt, 0.15, 0.4)), '#FFD43B');
      tag('~45 KM/H', Math.max(200, Math.min(800, rx)), Math.max(600, ry - 110), rx, ry - 10, eob(seg(lt, 0.35, 0.6)), '#FFFFFF');
      headline(ctx, 'FASTER THAN', 'ANY HUMAN ALIVE', 360, eob(seg(lt, 0.0, 0.25)));
    } });
    cue(st, 'whoosh', { gain: 0.7 }); for (let k = 0; k < 8; k++) cue(st + 0.1 + k * 0.33, 'thud', { gain: 0.35 }); }

  return { shots: S, cues: CUES };
}
