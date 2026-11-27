// A tiny deterministic pen wobble for generated hand-drawn figures.
//
// The drawings are still ordinary SVG paths: endpoints, viewBox, text and
// colours stay where the generator put them. Long straight segments and
// shallow existing curves get a small deterministic pen bow, so ruler-straight
// or uniformly bent edges read as pen strokes without moving anything a
// reader relies on. Dashes and short arrow geometry are left alone.
//
// Bowed segments become Q commands with a quantised control point. Applying
// the transform again to an already inked figure leaves it untouched.

import { createHash } from "node:crypto";

const COMMANDS = { M: 2, L: 2, H: 1, V: 1, Q: 4, C: 6, Z: 0 };
const TOKEN = /[MLHVCQZ]|-?\d+(?:\.\d+)?/g;
const MIN_SEGMENT = 60;

const fmt = value => String(Math.round(value * 50) / 50);

function pen(x0, y0, x1, y1) {
  const digest = createHash("sha256").update(`${fmt(x0)},${fmt(y0)},${fmt(x1)},${fmt(y1)}`).digest();
  return { amplitude: 0.9 + (digest[1] / 255) * 1.4, direction: digest[0] % 2 ? 1 : -1 };
}

function segment(x0, y0, x1, y1) {
  const dx = x1 - x0;
  const dy = y1 - y0;
  const length = Math.hypot(dx, dy);
  if (length < MIN_SEGMENT) return null;
  const { amplitude, direction } = pen(x0, y0, x1, y1);
  const offset = amplitude * direction;
  return ["Q", (x0 + x1) / 2 - (dy / length) * offset, (y0 + y1) / 2 + (dx / length) * offset, x1, y1];
}

// Shallow hand-drawn curves already carry a control point a few pixels off
// their chord. Give those a slightly uneven, deterministic offset instead of
// the generator's identical 3px everywhere; deeper intended arcs are left as
// they are. Normalising to a fixed amplitude keeps this idempotent.
function curve(x0, y0, cx, cy, x1, y1) {
  const dx = x1 - x0;
  const dy = y1 - y0;
  const length = Math.hypot(dx, dy);
  if (length < MIN_SEGMENT) return null;
  const mx = (x0 + x1) / 2;
  const my = (y0 + y1) / 2;
  const px = -dy / length;
  const py = dx / length;
  const vx = cx - mx;
  const vy = cy - my;
  const across = vx * px + vy * py;
  if (Math.abs(across) > 8) return null;
  const projection = vx * (dx / length) + vy * (dy / length);
  const along = Math.abs(projection) < 0.05 ? 0 : Math.round(projection * 10) / 10;
  const { amplitude, direction: penDirection } = pen(x0, y0, x1, y1);
  const direction = across === 0 ? penDirection : Math.sign(across);
  return [mx + px * amplitude * direction + (dx / length) * along, my + py * amplitude * direction + (dy / length) * along, x1, y1];
}

function bowPath(d) {
  const tokens = d.match(TOKEN);
  if (!tokens) return d;
  const out = [];
  let changed = false;
  let x = 0;
  let y = 0;
  let startX = 0;
  let startY = 0;
  for (let i = 0; i < tokens.length;) {
    const command = tokens[i++];
    const arity = COMMANDS[command];
    if (arity === undefined || i + arity > tokens.length) return d;
    const values = tokens.slice(i, i + arity).map(Number);
    if (values.some(value => !Number.isFinite(value))) return d;
    i += arity;
    if (command === "M") {
      [x, y] = values;
      [startX, startY] = values;
      out.push("M", fmt(x), fmt(y));
    } else if (command === "L" || command === "H" || command === "V") {
      const [nx, ny] = command === "L" ? values
        : command === "H" ? [values[0], y]
          : [x, values[0]];
      const bowed = segment(x, y, nx, ny);
      if (bowed) {
        changed = true;
        out.push(...bowed.map(value => typeof value === "number" ? fmt(value) : value));
      } else out.push("L", fmt(nx), fmt(ny));
      x = nx;
      y = ny;
    } else if (command === "Q") {
      const [cx, cy, ex, ey] = values;
      const curved = curve(x, y, cx, cy, ex, ey);
      if (curved) {
        changed = true;
        out.push("Q", ...curved.map(fmt));
      } else out.push("Q", ...values.map(fmt));
      x = ex;
      y = ey;
    } else if (command === "C") {
      out.push("C", ...values.map(fmt));
      x = values[4];
      y = values[5];
    } else {
      out.push("Z");
      [x, y] = [startX, startY];
    }
  }
  return changed ? out.join(" ") : d;
}

export function inkifySvg(svg) {
  return svg.replace(/<path\b[^>]*\/>/g, tag => {
    if (!/\bstroke="[^"]+"/.test(tag) || /\bstroke-dasharray=/.test(tag)) return tag;
    const match = /\bd="([^"]*)"/.exec(tag);
    if (!match) return tag;
    const d = bowPath(match[1]);
    return d === match[1] ? tag : tag.replace(match[1], d);
  });
}
