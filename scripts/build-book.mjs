import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { resolve, dirname, relative } from 'node:path';
import { createHash } from 'node:crypto';
import { marked, Renderer } from 'marked';

const root = resolve(import.meta.dirname, '..');
const out = resolve(root, 'exports/book');
const checking = process.argv.includes('--check');
const source = readFileSync(resolve(root, 'book/book.md'), 'utf8');
const h = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const plain = value => value.replace(/<[^>]*>/g,'').replace(/&amp;/g,'&').replace(/[`*_]/g,'');
const slug = value => plain(value).toLowerCase().replace(/[^\p{L}\p{N}\p{M}_\s-]/gu,'').trim().replace(/\s/g,'-');
const tokens = marked.lexer(source);
const chunks = [{file:'index.html', title:'Vibe Coding 101：从一句需求到第一个可用作品', stage:'导读', tokens:[], headings:[]}];
let stage='指南', pending=[];
for (const token of tokens) {
  if (token.type === 'heading' && token.depth === 1 && /^(Stage [123]|附录|指南)$/.test(token.text)) {
    stage = token.text;
    pending.push(token);
  } else if (token.type === 'heading' && token.depth === 3) {
    chunks.push({file:`chapter-${String(chunks.length).padStart(3,'0')}.html`, title:plain(token.text), stage, tokens:[...pending,token], headings:[]});
    pending=[];
  } else if (pending.length) pending.push(token);
  else chunks.at(-1).tokens.push(token);
}
chunks.at(-1).tokens.push(...pending);
const destinations = new Map(), used = new Set();
for (const chunk of chunks) {
  const levels = [{source: 3, rendered: 1}];
  let firstSection = true;
  marked.walkTokens(chunk.tokens, token => {
    if (token.type === 'html') {
      for (const match of token.text.matchAll(/\bid="([^"]+)"/g)) {
        if (!destinations.has(match[1])) destinations.set(match[1], chunk.file);
      }
    }
    if (token.type !== 'heading') return;
    let base=slug(token.text) || 'section', id=base, n=0;
    while(used.has(id)) id=`${base}-${++n}`;
    used.add(id);token.bookId=id;
    if (token.depth >= 4) {
      token.bookAlias = firstSection && plain(token.text) === chunk.title;
      firstSection = false;
      if (!token.bookAlias) {
        while (levels.length > 1 && levels.at(-1).source >= token.depth) levels.pop();
        token.bookDepth = Math.min(6, levels.at(-1).rendered + 1);
        levels.push({source: token.depth, rendered: token.bookDepth});
      }
    }
    destinations.set(id,chunk.file);
    chunk.headings.push({id, depth:token.depth, text:plain(token.text), renderedDepth:token.bookDepth, alias:token.bookAlias});
  });
}
const failures=[];
function link(href, file) {
  if (!href || /^(?:[a-z][a-z\d+.-]*:|\/\/)/i.test(href)) return href;
  if (href.startsWith('#')) {
    const id=decodeURIComponent(href.slice(1)), target=destinations.get(id);
    if (!target) failures.push(`${file}: missing anchor ${href}`);
    return target ? `${target===file?'':target}#${id}` : href;
  }
  const [path, hash] = href.split('#');
  const target=resolve(root,'book',decodeURIComponent(path));
  if (!existsSync(target)) failures.push(`${file}: missing file ${href}`);
  return relative(out,target).replaceAll('\\','/')+(hash?`#${hash}`:'');
}
const write = (name, content) => {
  const file=resolve(out,name);
  if(checking) { if(!existsSync(file)||readFileSync(file,'utf8')!==content) throw new Error(`${name} is stale; run npm run build:book`); }
  else {mkdirSync(dirname(file),{recursive:true});writeFileSync(file,content);}
};
for(const [index,chunk] of chunks.entries()) {
  const titleToken = index ? chunk.tokens.find(token=>token.type==='heading' && token.depth===3) : null;
  const renderer = new Renderer();
  renderer.heading = function(token) {
    if (token === titleToken) return '';
    if (token.bookAlias || (index && token.depth===1 && /^(Stage [123]|附录|指南)$/.test(token.text))) {
      return `<span class="heading-anchor" id="${h(token.bookId)}"></span>\n`;
    }
    const depth = token.bookDepth || (token.depth===3 || (index===0 && token.depth===1) ? 1 : Math.min(6,Math.max(2,token.depth-2)));
    return `<h${depth} id="${h(token.bookId)}">${this.parser.parseInline(token.tokens)}</h${depth}>\n`;
  };
  const defaultCode = renderer.code;
  renderer.code = function(token) {
    const language = (token.lang || '').split(/\s/)[0].toLowerCase();
    // Wrap prose fences, but preserve spacing in diagrams, tables and source code.
    const aligned = /[\u2500-\u257f]|\S[ \t]{2,}\S|^[ \t]*[|+].*[|+]|\u3000{2}/m.test(token.text);
    const prose = ['text','plain','plaintext','prompt','markdown','md'].includes(language) && !aligned;
    return defaultCode.call(this, token).replace('<pre>', prose
      ? '<pre class="prose-block">'
      : '<pre tabindex="0" role="region" aria-label="代码或文本，可横向滚动">');
  };
  renderer.link = function(token) {return `<a href="${h(link(token.href,chunk.file))}">${this.parser.parseInline(token.tokens)}</a>`;};
  renderer.image = token => `<img src="${h(link(token.href,chunk.file))}" alt="${h(token.text)}" loading="lazy" decoding="async">`;
  renderer.html = token => token.text
    .replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi,'')
    .replace(/<style\b[^>]*>[\s\S]*?<\/style>/gi,'')
    .replace(/\s+on\w+="[^"]*"/gi,'')
    .replace(/\b(href|src)="([^"]+)"/g,(_,attr,value)=>`${attr}="${h(link(value,chunk.file))}"`);
  let body=marked.parser(chunk.tokens,{renderer});
  // A normal image link works offline, with keyboard navigation and without JS.
  body=body.replace(/<figure\b([^>]*)>([\s\S]*?)<\/figure>/g,(figure,attrs,content)=>{
    const match=content.match(/^\s*(<img\b[^>]*\bsrc="([^"]*\/handdraw\/[^"]+)"[^>]*>)/);
    if (!match) return figure;
    const alt=match[1].match(/\balt="([^"]*)"/)?.[1] || '手绘图解';
    const linked=content.replace(match[1],`<a class="figure-zoom" href="${match[2]}" aria-label="打开大图：${alt}">${match[1]}</a>`)
      .replace('</figcaption>','<span class="figure-hint">点图查看原尺寸</span></figcaption>');
    return `<figure${attrs}>${linked}</figure>`;
  });
  // All tables scroll within the text column; prose remains reflowable.
  body=body.replace(/<table\b/g,'<div class="table-scroll" tabindex="0" role="region" aria-label="表格，可横向滚动"><table').replaceAll('</table>','</table></div>');
  const sections=chunk.headings.filter(item=>!item.alias && item.renderedDepth>=2 && item.renderedDepth<=3);
  const groups=[];
  for (const item of sections) {
    if (item.renderedDepth===3 && groups.length) groups.at(-1).children.push(item);
    else groups.push({...item,children:[]});
  }
  const tocLink=item=>`<a href="#${h(item.id)}">${h(item.text)}</a>`;
  const contents=groups.length?`<details class="contents"><summary>本章目录 <span>· ${groups.length} 节</span></summary><nav aria-label="本章目录"><ul>${groups.map(item=>`<li>${tocLink(item)}${item.children.length?`<ul>${item.children.map(child=>`<li>${tocLink(child)}</li>`).join('')}</ul>`:''}</li>`).join('')}</ul></nav></details>`:'';
  const chapterOpening=titleToken?`<h1 id="${h(titleToken.bookId)}">${marked.parseInline(titleToken.text,{renderer})}</h1>${contents}`:'';
  const navigation=`<nav class="paging" aria-label="章节导航">${index?`<a rel="prev" href="${chunks[index-1].file}">← ${h(index===1?'全书导读':chunks[index-1].title)}</a>`:''}${chunks[index+1]?`<a rel="next" href="${chunks[index+1].file}">${h(chunks[index+1].title)} →</a>`:''}</nav>`;
  write(chunk.file,`<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${h(chunk.title)} · Vibe Coding 101</title><link rel="stylesheet" href="book.css"></head>
<body><a class="skip" href="#main">跳到正文</a><header><a href="index.html">Vibe Coding 101 · 全书目录</a><a href="../../开始阅读.html">阅读入口</a></header>
<main id="main" tabindex="-1"><p class="stage">${h(chunk.stage)}${index?` · ${index} / ${chunks.length-1}`:''}</p><article>${chapterOpening}${body}</article>${navigation}</main>
<footer><a href="../../book/book.md">原书 Markdown</a> · <a href="https://github.com/datawhalechina/easy-vibe">原课程与网页交互示例</a></footer></body></html>\n`);
}
if(failures.length) throw new Error([...new Set(failures)].join('\n'));
write('book.css',readFileSync(resolve(root,'scripts/book.css'),'utf8'));
write('../../开始阅读.html', `<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>开始阅读 · 大模型：从入门到精通</title><link rel="stylesheet" href="exports/book/book.css"><style>.intro{font-size:1.15rem}.primary{display:inline-block;padding:12px 22px;background:#d3efd9;border:2px solid #1f2328;border-radius:7px 12px 6px 10px;color:#1f2328;font-weight:700}section{margin-top:40px}h1{font-size:2rem}</style></head>
<body><a class="skip" href="#main">跳到正文</a><main id="main" tabindex="-1"><p class="stage">五阶段 · 三十章 · 从会用到独立交付</p><h1>大模型：从入门到精通</h1><p class="intro">先做出有依据的结果，再理解原理、实现应用、评测改进，最后独立交付。</p><p>从零基础开始，逐步补齐数学与 Python。完成路线时，应能解释模型怎样生成和学习，搭建可核验的资料助手，训练与适配一个小模型，并交付可复做的新项目。</p><p><a class="primary" href="exports/llm/course.html">打开五阶段学习路线 →</a></p><p><a href="exports/llm/c01.html">从 C01 开始</a> · <a href="deliverables/llm-course.pdf">正文 PDF</a> · <a href="deliverables/llm-course.epub">正文 EPUB</a></p>
<section><h2>每一阶段，留下一个能检查的成果</h2><ol><li><strong>S1 会使用：</strong>完成带原文依据的资料报告，保留缺失与冲突。</li><li><strong>S2 懂原理：</strong>复算分词、生成、注意力与一次参数更新。</li><li><strong>S3 能实现：</strong>接入真实模型，串起检索、引用和有限工具调用。</li><li><strong>S4 会改进：</strong>先冻结评测，再对照方案；训练小型 decoder，验证 SFT、LoRA 和蒸馏。</li><li><strong>S5 独立交付：</strong>处理陌生题材，交付环境、代码、评测与故障回退，让另一人复做。</li></ol><p>每章有独立题与<a href="deliverables/llm-course-answers.pdf">分离答案 PDF</a> / <a href="deliverables/llm-course-answers.epub">EPUB</a>。先作答，再核对。</p></section>
<section><h2>开始前知道这些</h2><p>S1/S2 的正文与本地实验无需账号；S3 起需要合法可用的模型和相应环境。本书提供真实失败记录与排查方法，目前仍是试读版，尚未完成真人全程验收。读完三十章本身不代表已通过五道能力门。</p><p><a href="exports/llm/index.html">十二课交互实验与原理回查</a> · <a href="book/llm/examples/assistant/README.md">资料助手运行说明</a> · <a href="specs/STATUS.md">当前完成情况与剩余工作</a></p></section>
<section><h2>补充学习：Vibe Coding 编程实践</h2><p>需要补设计、数据库、部署与编程工具时，查阅<a id="original-book-link" href="exports/book/index.html">原《Vibe Coding 101》Stage 1–3 与附录</a>，或打开<a href="exports/landing.html">配套视频</a>。</p></section></main></body></html>\n`);
write('manifest.json',JSON.stringify({title:chunks[0].title,source:'book/book.md',sourceSha256:createHash('sha256').update(source).digest('hex'),chapters:chunks.slice(1).map(({file,title,stage,headings})=>({file,title,stage,headings})),headingCount:destinations.size},null,2)+'\n');
console.log(`${checking?'Verified':'Built'} original book: ${chunks.length-1} chapters, ${destinations.size} heading targets; local links resolved`);
