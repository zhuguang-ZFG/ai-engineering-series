import { createHash } from "node:crypto";
import { Marked } from "marked";

// IDs follow the heading text, so inserting an earlier section does not move
// existing reading links. The lesson prefix also keeps the assembled PDF unique.
export function renderReading(markdown, lessonId) {
  const outline = [];
  const occurrences = new Map();
  const parser = new Marked({
    renderer: {
      heading({ tokens, depth, text }) {
        const content = this.parser.parseInline(tokens);
        const stem = lessonId === "L05" && text.startsWith("蒸馏：")
          ? "distillation"
          : `${lessonId}-section-${createHash("sha256").update(text).digest("hex").slice(0, 10)}`;
        const occurrence = (occurrences.get(stem) ?? 0) + 1;
        occurrences.set(stem, occurrence);
        const id = occurrence === 1 ? stem : `${stem}-${occurrence}`;
        if (depth === 2 || depth === 3) outline.push({ id, depth, content });
        return `<h${depth} id="${id}" tabindex="-1">${content}</h${depth}>\n`;
      }
    }
  });
  return { html: parser.parse(markdown), outline };
}

export function readingContents(outline) {
  return `<nav class="lesson-toc" aria-label="本课目录"><ol>${outline.map(({ id, depth, content }) => `<li class="toc-level-${depth}"><a href="#${id}">${content}</a></li>`).join("")}</ol></nav>`;
}
