// 手绘 token 对比度校验器 · 无依赖
// 色彩公式移植自歸藏 dsh-guizang-design / guizang-page-skill/scripts/gz-theme.mjs
// （MIT）：sRGB↔OKLab/OKLCH、WCAG 2、APCA(SAPC 0.0.98G-4g)。纯函数、无外部包。
// 用法：node design/system/contrast.mjs   任一角色对不达 ROLE_FLOORS 即非零退出（可入 CI）。

import { pathToFileURL } from 'node:url'

const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v))
const parseHex = (hex) => {
  const h = hex.replace('#', '')
  return [0, 2, 4].map((i) => parseInt(h.slice(i, i + 2), 16) / 255)
}
const toHex = (rgb) => '#' + rgb.map((c) => Math.round(clamp(c, 0, 1) * 255).toString(16).padStart(2, '0')).join('')

const toLinear = (c) => (c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4)
const fromLinear = (c) => (c <= 0.0031308 ? 12.92 * c : 1.055 * c ** (1 / 2.4) - 0.055)

function rgbToOklab([r, g, b]) {
  const R = toLinear(r), G = toLinear(g), B = toLinear(b)
  const l = Math.cbrt(0.4122214708 * R + 0.5363325363 * G + 0.0514459929 * B)
  const m = Math.cbrt(0.2119034982 * R + 0.6806995451 * G + 0.1073969566 * B)
  const s = Math.cbrt(0.0883024619 * R + 0.2817188376 * G + 0.6299787005 * B)
  return [
    0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
    1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
    0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s,
  ]
}
function oklabToRgb([L, a, b]) {
  const l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
  const m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
  const s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
  return [
    fromLinear(4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s),
    fromLinear(-1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s),
    fromLinear(-0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s),
  ]
}
const oklabToOklch = ([L, a, b]) => {
  const C = Math.hypot(a, b)
  let H = (Math.atan2(b, a) * 180) / Math.PI
  if (H < 0) H += 360
  return { l: L, c: C, h: C < 1e-4 ? 0 : H }
}
const oklchToOklab = ({ l, c, h }) => {
  const r = (h * Math.PI) / 180
  return [l, c * Math.cos(r), c * Math.sin(r)]
}
const hexToOklch = (hex) => oklabToOklch(rgbToOklab(parseHex(hex)))
const inGamut = (rgb, eps = 1e-6) => rgb.every((c) => c >= -eps && c <= 1 + eps)
function oklchToHex({ l, c, h }) {
  l = clamp(l, 0, 1)
  let rgb = oklabToRgb(oklchToOklab({ l, c, h }))
  if (!inGamut(rgb)) {
    let lo = 0, hi = c
    while (hi - lo > 1e-5) {
      const mid = (lo + hi) / 2
      if (inGamut(oklabToRgb(oklchToOklab({ l, c: mid, h })))) lo = mid; else hi = mid
    }
    rgb = oklabToRgb(oklchToOklab({ l, c: lo, h }))
  }
  return toHex(rgb)
}
function maxChroma(l, h) {
  let lo = 0, hi = 0.5
  while (hi - lo > 1e-5) {
    const mid = (lo + hi) / 2
    if (inGamut(oklabToRgb(oklchToOklab({ l, c: mid, h })))) lo = mid; else hi = mid
  }
  return lo
}
const luminance = (hex) => {
  const [r, g, b] = parseHex(hex).map(toLinear)
  return 0.2126 * r + 0.7152 * g + 0.0722 * b
}
function wcag(fg, bg) {
  const a = luminance(fg), b = luminance(bg)
  return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05)
}
function apca(fg, bg) {
  const y = (hex) => {
    const [r, g, b] = parseHex(hex).map((c) => c ** 2.4)
    let Y = 0.2126729 * r + 0.7151522 * g + 0.072175 * b
    if (Y < 0.022) Y += (0.022 - Y) ** 1.414
    return Y
  }
  const Yt = y(fg), Yb = y(bg)
  if (Math.abs(Yb - Yt) < 0.0005) return 0
  if (Yb > Yt) {
    const s = (Yb ** 0.56 - Yt ** 0.57) * 1.14
    return s < 0.1 ? 0 : (s - 0.027) * 100
  }
  const s = (Yb ** 0.65 - Yt ** 0.62) * 1.14
  return s > -0.1 ? 0 : (s + 0.027) * 100
}
const passes = (fg, bg, floor) => Math.abs(apca(fg, bg)) >= floor.apca && wcag(fg, bg) >= floor.wcag

// 沿色相降 L 求达标前景（彩度取色域上限），用于重算派生 token
function descend(h, startL, test) {
  for (let l = startL; l >= 0.20; l -= 0.005) {
    const hex = oklchToHex({ l, c: maxChroma(l, h), h })
    if (test(hex)) return hex
  }
  return null
}

export const ROLE_FLOORS = {
  textBody: { apca: 75, wcag: 7 },
  textSecondary: { apca: 60, wcag: 4.5 },
  textHelper: { apca: 60, wcag: 4.5 },
  accentInk: { apca: 60, wcag: 4.5 },
  onText: { apca: 45, wcag: 4.5 },
  accentDisplay: { apca: 45, wcag: 0 },
}

export const TOKENS = {
  paper: '#fbfaf6', card: '#fffdf8', ink: '#1f2328', inkSoft: '#57606a',
  marker: '#f0e9d8', markerWash: '#f7f3e8', rule: '#e6e1d4',
  accent: '#B4472F', persimmon: '#B4472F',
  accentInk: '#B4472F', persimmonInk: '#B4472F', accentBlock: '#B4472F', persimmonBlock: '#B4472F',
}

// 必须达标（PASS）的角色对——设计系统的可读性地基
export const ASSERTS = [
  ['ink / paper', 'ink', 'paper', 'textBody'],
  ['ink / card', 'ink', 'card', 'textBody'],
  ['ink / marker', 'ink', 'marker', 'textBody'],
  ['inkSoft / paper', 'inkSoft', 'paper', 'textSecondary'],
  ['inkSoft / card', 'inkSoft', 'card', 'textSecondary'],
  ['inkSoft / marker', 'inkSoft', 'marker', 'textSecondary'],
  ['ink / markerWash', 'ink', 'markerWash', 'textBody'],
  ['inkSoft / markerWash', 'inkSoft', 'markerWash', 'textSecondary'],
  ['accentInk / paper', 'accentInk', 'paper', 'accentInk'],
  ['accentInk / card', 'accentInk', 'card', 'accentInk'],
  ['paper / accentBlock', 'paper', 'accentBlock', 'onText'],
  ['paper / persimmonBlock', 'paper', 'persimmonBlock', 'onText'],
]
// 禁止组合（不是缺陷，是不许用）：绿字压绿底 APCA 仅 58，低于 60 线；marker 底上只允许 ink / inkSoft
export const FORBIDDEN = [['accentInk / marker', 'accentInk', 'marker', 60]]
// 原始 accent/persimmon 仅够“大号/展示/非阅读图形”（accentDisplay），记录为已知上限，不是缺陷
export const DISPLAY_ONLY = [
  ['accent (大字/图形) / paper', 'accent', 'paper'],
  ['persimmon (大字/图形，CTA 填充请用 --persimmon-block) / paper', 'persimmon', 'paper'],
]

if (process.argv[1] && pathToFileURL(process.argv[1]).href === import.meta.url) {
  let bad = 0
  const r2 = (x) => Math.round(x * 100) / 100
  console.log('token pair                         wcag   apca(Lc)  floor{apca,wcag}  verdict')
  for (const [name, fg, bg, role] of ASSERTS) {
    const f = ROLE_FLOORS[role], w = wcag(TOKENS[fg], TOKENS[bg]), a = apca(TOKENS[fg], TOKENS[bg])
    const ok = passes(TOKENS[fg], TOKENS[bg], f); if (!ok) bad++
    console.log(`${name.padEnd(32)} ${String(r2(w)).padEnd(7)} ${String(r2(a)).padEnd(10)} {${f.apca},${f.wcag}}`.padEnd(46) + (ok ? 'PASS' : 'FAIL'))
  }
  console.log('-- 原始强调色作展示/大字（accentDisplay 线，仅 APCA≥45）--')
  for (const [name, fg, bg] of DISPLAY_ONLY) {
    const a = apca(TOKENS[fg], TOKENS[bg]), w = wcag(TOKENS[fg], TOKENS[bg])
    console.log(`${name.padEnd(32)} ${String(r2(w)).padEnd(7)} ${String(r2(a)).padEnd(10)} (display only)`)
  }
  console.log('\n禁止组合（底色改了也不许把这类文字放上去）：')
  for (const [name, fg, bg, floor] of FORBIDDEN) {
    const a = apca(TOKENS[fg], TOKENS[bg])
    console.log(`${name.padEnd(32)} APCA ${String(r2(a)).padEnd(10)} (需 ≥${floor}，故禁用)`)
    if (a >= floor) { console.log('  ↑ 该组合现已达标，可从 FORBIDDEN 移除'); }
  }
  console.log('\nOKLCH 参考：')
  for (const [k, hex] of Object.entries(TOKENS)) { const o = hexToOklch(hex); console.log(`  ${k.padEnd(12)} ${hex}  L=${(o.l * 100).toFixed(1)}% C=${o.c.toFixed(4)} H=${o.h.toFixed(1)}`) }
  console.log('\n重算派生 token（若手绘原色改动后需再达标）：')
  console.log('  accent-ink    =', descend(34.0, 0.62, (hex) => passes(hex, TOKENS.paper, ROLE_FLOORS.accentInk) && passes(hex, TOKENS.card, ROLE_FLOORS.accentInk)))
  console.log('  persimmon-ink =', descend(34.0, 0.62, (hex) => passes(hex, TOKENS.paper, ROLE_FLOORS.accentInk)))
  process.exit(bad ? 1 : 0)
}

export { wcag, apca, passes, hexToOklch, oklchToHex, maxChroma, descend }
