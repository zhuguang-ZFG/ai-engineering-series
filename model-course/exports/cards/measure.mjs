// Measure vertical fill of every .poster board in a card deck.
// Usage: node measure.mjs <deck-dir>   (prints per-board content bottom, fill %, biggest gap)
import { createRequire } from 'node:module';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const SKILL = path.join(os.homedir(), '.agents/skills/guizang-social-card-skill');
const require = createRequire(path.join(SKILL, 'package.json'));
const { chromium } = require('playwright');

const dir = path.resolve(process.argv[2] || '.');
const file = pathToFileURL(path.join(dir, 'index.html')).href;

const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 2400, height: 1600 }, deviceScaleFactor: 1 });
await page.goto(file, { waitUntil: 'networkidle' });
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(800);

const rows = await page.evaluate(() => {
  const out = [];
  for (const poster of document.querySelectorAll('.poster')) {
    if (poster.closest('.pair-preview')) continue;
    const pr = poster.getBoundingClientRect();
    const content = poster.querySelector('.content');
    if (!content) { out.push({ id: poster.id, w: Math.round(pr.width), h: Math.round(pr.height), note: 'no .content' }); continue; }
    const cs = getComputedStyle(content);
    const padTop = parseFloat(cs.paddingTop), padBottom = parseFloat(cs.paddingBottom);
    const kids = [...content.children]
      .map((el) => {
        const r = el.getBoundingClientRect();
        const st = getComputedStyle(el);
        return { tag: el.tagName.toLowerCase(), cls: el.className.toString().split(' ')[0], top: r.top - pr.top, bottom: r.bottom - pr.top, h: r.height, pos: st.position };
      })
      .filter((k) => k.pos !== 'absolute' && k.pos !== 'fixed' && k.h > 0);
    kids.sort((a, b) => a.top - b.top);
    const bottom = kids.length ? Math.max(...kids.map((k) => k.bottom)) : padTop;
    const gaps = [];
    for (let i = 1; i < kids.length; i++) {
      const g = kids[i].top - kids[i - 1].bottom;
      if (g > 0) gaps.push({ between: `${kids[i - 1].cls || kids[i - 1].tag}→${kids[i].cls || kids[i].tag}`, px: Math.round(g) });
    }
    gaps.sort((a, b) => b.px - a.px);
    out.push({
      id: poster.id, w: Math.round(pr.width), h: Math.round(pr.height),
      pad: `${padTop}/${padBottom}`, limit: Math.round(pr.height - padBottom),
      bottom: Math.round(bottom), fill: +(bottom / pr.height).toFixed(3),
      overflow: Math.round(bottom - (pr.height - padBottom)),
      maxGap: gaps[0] || null,
      lastKids: kids.slice(-2).map((k) => `${k.cls || k.tag}@${Math.round(k.top)}-${Math.round(k.bottom)}`),
    });
  }
  return out;
});
await browser.close();

for (const r of rows) {
  console.log(`${r.id.padEnd(20)} ${r.w}x${r.h}  bottom=${String(r.bottom).padStart(5)} limit=${String(r.limit).padStart(5)} fill=${r.fill}  overflow=${r.overflow}  maxGap=${r.maxGap ? r.maxGap.between + ' ' + r.maxGap.px + 'px' : '-'}  tail=${(r.lastKids || []).join(' | ')}`);
}
