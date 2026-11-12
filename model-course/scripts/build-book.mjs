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
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><title>开始阅读 · 大模型：从入门到精通</title><style>
:root{--paper:#FBF7EF;--ink:#26221B;--soft:#5C5448;--pine:#1f5c45;--rule:#E3D8C1;--sand:#F6F0E2}
*{box-sizing:border-box}html{background:var(--paper)}body{margin:0 auto;max-width:1080px;padding:56px 28px 88px;background:var(--paper);color:var(--ink);font-family:'Noto Serif SC','Songti SC','SimSun',serif;font-size:16px;line-height:1.9}
a{color:var(--pine);text-underline-offset:.22em}.skip{position:absolute;left:-999px}.skip:focus{left:24px;top:16px;padding:8px 14px;background:var(--sand);z-index:2}
.hero{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(220px,.65fr);gap:56px;align-items:center}
.eyebrow{margin:0 0 1rem;color:var(--pine);font-family:'Noto Sans SC','Microsoft YaHei',sans-serif;font-size:.8rem;letter-spacing:.2em}
h1{margin:.1em 0 .35em;font-size:clamp(2.3rem,5vw,4.2rem);line-height:1.12;font-weight:600;letter-spacing:.04em}
.lead{margin:0 0 1rem;font-size:1.22rem;line-height:1.8;color:var(--ink)}
.intro{margin:0 0 1.6rem;color:var(--soft);max-width:36em}
.actions{display:flex;flex-wrap:wrap;gap:.7rem;align-items:center;margin:1.6rem 0 1rem}
.primary{display:inline-block;padding:11px 20px;background:var(--pine);border:1px solid var(--pine);color:#fffdf8;text-decoration:none;font-family:'Noto Sans SC','Microsoft YaHei',sans-serif;font-weight:600;letter-spacing:.02em}
.ghost{display:inline-block;padding:10px 18px;border:1px solid var(--ink);color:var(--ink);text-decoration:none;font-family:'Noto Sans SC','Microsoft YaHei',sans-serif}
.quick{margin:0;color:var(--soft);font-size:.92rem}
.cover{margin:0;text-align:center}.cover img{display:block;width:100%;max-width:290px;height:auto;margin:0 auto;box-shadow:0 22px 38px rgba(31,35,40,.16)}
.cover figcaption{margin-top:1rem;color:var(--soft);font-size:.8rem;letter-spacing:.06em}
.stage-strip{display:grid;grid-template-columns:repeat(5,1fr);gap:1px;margin:4rem 0 0;border-top:2px solid var(--ink);border-bottom:2px solid var(--ink);background:var(--rule)}
.stage-card{display:block;padding:1.15rem .95rem 1.25rem;background:var(--paper);color:var(--ink);text-decoration:none}
.stage-card:hover{background:#f4efe4}.stage-card b{display:block;color:var(--pine);font-family:'Noto Sans SC','Microsoft YaHei',sans-serif;font-size:.75rem;letter-spacing:.14em;font-weight:600}
.stage-card strong{display:block;margin:.35rem 0 .25rem;font-size:1.08rem;font-weight:600}.stage-card span{display:block;color:var(--soft);font-size:.86rem;line-height:1.7}
section{margin-top:3.4rem;padding-top:1.3rem;border-top:1px solid var(--rule)}
h2{font-size:1.35rem;font-weight:600;margin:.2rem 0 1rem}h3{font-size:1rem;margin:1.4rem 0 .4rem}
ol,ul{padding-left:1.4em}li{margin:.35rem 0}.muted{color:var(--soft);font-size:.92rem}
footer{margin-top:3.4rem;padding-top:1.2rem;border-top:1px solid var(--rule);color:var(--soft);font-size:.84rem}
@media(max-width:760px){body{padding:32px 20px 64px}.hero{grid-template-columns:1fr;gap:2.2rem}.cover{order:-1}.stage-strip{grid-template-columns:1fr 1fr}.cover img{max-width:230px}}
</style></head>
<body><a class="skip" href="#main">跳到正文</a><main id="main" tabindex="-1"><header class="hero"><div><p class="eyebrow">五阶段 · 三十章 · 五道能力门</p><h1>大模型：<br>从入门到精通</h1><p class="lead">先做出有依据的结果，再理解原理、实现应用、评测改进，最后独立交付。</p><p class="intro">从零基础开始，逐步补齐数学与 Python。完成路线时，应能解释模型怎样生成和学习，搭建可核验的资料助手，训练与适配一个小模型，并交付可复做的新项目。</p><div class="actions"><a class="primary" href="exports/llm/course.html">打开五阶段学习路线 →</a><a class="ghost" href="deliverables/llm-course.pdf">正文 PDF</a><a class="ghost" href="deliverables/llm-course.epub">EPUB</a></div><p class="quick"><a href="exports/llm/c01.html">从 C01 开始</a> · <a href="exports/llm/map.html">全书地图</a> · <a href="exports/llm/deep-reading.html">五个深读问题</a> · <a href="exports/llm/glossary.html">术语与能力门</a> · <a href="deliverables/llm-course-answers.pdf">分离答案</a></p></div><figure class="cover"><img src="book/assets/handdraw/llm/cover-course.svg" alt="《大模型：从入门到精通》封面：五阶段叠成阶梯，其中一块被抽出"><figcaption>实施试读版 1.1.2 · 2026.11</figcaption></figure></header>
<nav class="stage-strip" aria-label="五个阶段"><a class="stage-card" href="exports/llm/stage-s1.html"><b>S1 / K1</b><strong>会使用</strong><span>带原文依据的报告</span></a><a class="stage-card" href="exports/llm/stage-s2.html"><b>S2 / K2</b><strong>懂原理</strong><span>能手算的生成与注意力</span></a><a class="stage-card" href="exports/llm/stage-s3.html"><b>S3 / K3</b><strong>能实现</strong><span>真实模型、检索与工具</span></a><a class="stage-card" href="exports/llm/stage-s4.html"><b>S4 / K4</b><strong>会改进</strong><span>冻结评测与训练证据</span></a><a class="stage-card" href="exports/llm/stage-s5.html"><b>S5 / K5</b><strong>独立交付</strong><span>别人能启动、能回退</span></a></nav>
<section><h2>每一阶段，留下一个能检查的成果</h2><p>读完不是目的。五个阶段各留下一个可核验的成果：一份带证据的资料报告、一组能手算的机制、一个接上真实模型的助手、一份有样本数和失败解释的评测、一个别人能复做的交付包。</p><p class="muted">每章有独立题与分离答案。先作答，再核对；书末五篇深读分别讨论证据链、注意力算术、输出契约、小样本评测和回退边界。</p></section>
<section><h2>开始前知道这些</h2><p>S1/S2 的正文与本地实验无需账号；S3 起需要合法可用的模型和相应环境。本书提供真实失败记录与排查方法，目前仍是试读版，尚未完成真人全程验收。读完三十章本身不代表已通过五道能力门。</p><p><a href="exports/llm/index.html">十二课交互实验与原理回查</a> · <a href="book/llm/examples/assistant/README.md">资料助手运行说明</a> · <a href="specs/STATUS.md">当前完成情况与剩余工作</a></p></section>
<section><h2>补充学习：Vibe Coding 编程实践</h2><p>需要补设计、数据库、部署与编程工具时，查阅<a id="original-book-link" href="exports/book/index.html">原《Vibe Coding 101》Stage 1–3 与附录</a>，或打开<a href="exports/landing.html">配套视频</a>。</p></section>
<footer>实施试读版 · 真实读者学习效果、独立复做与读屏验收尚待完成 · <a href="specs/llm-learning-redesign/BOOK-CRAFT-05.md">本版书籍工艺记录</a></footer></main></body></html>\n`);
write('manifest.json',JSON.stringify({title:chunks[0].title,source:'book/book.md',sourceSha256:createHash('sha256').update(source).digest('hex'),chapters:chunks.slice(1).map(({file,title,stage,headings})=>({file,title,stage,headings})),headingCount:destinations.size},null,2)+'\n');
console.log(`${checking?'Verified':'Built'} original book: ${chunks.length-1} chapters, ${destinations.size} heading targets; local links resolved`);
