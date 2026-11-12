import { readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';

// FA-040: paper, variable ink contours and marker washes. Deterministic SVG
// keeps the mechanisms editable and the labels searchable.
const root = resolve(import.meta.dirname, '..');
const checking = process.argv.includes('--check');
const ink = '#1f2328', soft = '#57606a', green = '#B4472F';
const marker = '#f0e9d8', wash = '#f7f3e8', paper = '#fbfaf6', card = '#fffdf8';
const esc = s => String(s).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('"', '&quot;');
const text = (x, y, s, size = 26, options = '') => `<text x="${x}" y="${y}" font-size="${size}" ${options}>${esc(s)}</text>`;
const mid = (x,y,s,size=26,options='') => text(x,y,s,size,`text-anchor="middle" ${options}`);
const strong = (x,y,s,size=28) => text(x,y,s,size,'font-weight="700"');
const path = (d, fill='none', color=ink, width=2.5, options='') => `<path d="${d}" fill="${fill}" stroke="${color}" stroke-width="${width}" stroke-linecap="round" stroke-linejoin="round" ${options}/>`;
const arrow = (d, color=ink, dashed=false) => path(d,'none',color,2.7,`marker-end="url(#${color===green?'green-arrow':'arrow'})"${dashed?' stroke-dasharray="5 7"':''}`);
const circle = (x,y,r,fill=card,color=ink) => `<circle cx="${x}" cy="${y}" r="${r}" fill="${fill}" stroke="${color}" stroke-width="2.5"/>`;
const rect = (x,y,w,h,fill=card) => path(`M${x+6} ${y+1} Q${x+w*.46} ${y-2} ${x+w-4} ${y+2} L${x+w-1} ${y+h-4} Q${x+w*.6} ${y+h+2} ${x+2} ${y+h-1} Z`,fill);
const highlight = (x,y,w,h=12) => path(`M${x} ${y+2} Q${x+w*.4} ${y-3} ${x+w} ${y} L${x+w-5} ${y+h} Q${x+w*.5} ${y+h-1} ${x+2} ${y+h+3} Z`,marker,'none');
const number = (x,y,n) => circle(x,y,18,marker)+mid(x,y+9,n,26);
const icon = (name,x,y,size=72) => `<use href="#icon-${name}" x="${x}" y="${y}" width="${size}" height="${size}"/>`;
const symbols = {
  search: path('M49 47L69 69','none',ink,5)+circle(31,29,22,wash)+path('M19 19Q28 11 38 17','none',soft,2)+path('M19 34L26 27L32 32L43 22','none',green,3),
  filter: path('M8 12Q39 8 72 13L47 43L45 66L32 71L32 43Z',wash)+path('M14 17Q40 24 65 17')+circle(25,18,3,marker)+circle(40,18,3,marker)+circle(55,18,3,marker),
  task: rect(15,8,51,65)+path('M27 8V3H52V9',marker)+[23,40,57].map(y=>path(`M23 ${y}l4 4 7-9`,'none',green,3)+path(`M41 ${y}h15`)).join(''),
  talk: path('M8 15Q38 5 68 16L66 49L39 50L24 67L25 49L8 46Z',wash)+path('M21 27H54M21 37H44')+path('M53 53L65 63L64 52','none',soft,2),
  diamond: path('M6 38L23 12L40 38L23 64Z',wash)+path('M40 38L57 12L74 38L57 64Z',marker)+path('M23 13V63M57 13V63','none',soft,1.5,'stroke-dasharray="3 5"'),
  browser: rect(5,9,70,61)+path('M6 24H74')+circle(14,17,2,marker)+circle(22,17,2,marker)+path('M14 34H34V60H14Z',wash)+path('M43 36H64M43 45H60M43 57H66','none',green,4),
  plug: path('M24 4V21M49 4V21','none',ink,4)+path('M15 23Q38 19 59 23L56 43L45 51V60H30V50L19 43Z',marker)+path('M38 60V69Q38 76 53 75')+path('M31 29L27 38H41L37 45','none',ink,2),
  deliver: path('M11 17L38 6L68 18L40 31Z',marker)+path('M11 17V58L40 73L68 58V18M40 31V73M25 12L54 24V42')+path('M50 51L56 57L67 43','none',green,3),
  error: rect(5,7,69,62)+path('M6 22H73')+circle(14,15,2,marker)+path('M40 31L59 58H21Z',wash)+path('M40 39V47M40 53V54','none','#B4472F',4),
  evidence: rect(9,6,46,63)+path('M18 19H43M18 29H43M18 39H30','none',soft,2)+circle(51,49,17,marker)+path('M63 62L74 74','none',ink,4)+path('M44 49L49 54L58 44','none',green,3),
  patch: rect(7,7,66,64)+path('M8 23H72')+path('M17 35H51','none',soft,3)+highlight(14,43,49,8)+path('M20 44V54M15 49H25M33 49H61','none',green,3)+path('M18 62H53','none',soft,2),
  passed: rect(6,8,68,62)+path('M7 24H73')+path('M23 47L34 58L59 34','none',green,5),
  laptop: path('M13 7Q40 4 67 8L65 54H15Z',card)+path('M19 14H60V47H19Z',wash)+path('M15 54L4 68Q40 75 76 68L65 54M30 63H50')+path('M28 27L22 32L28 37M50 27L56 32L50 37','none',green,3),
  build: rect(6,7,69,65)+path('M7 23H74')+path('M15 34L22 39L15 44M29 44H44')+path('M43 56L51 64L66 47','none',green,4),
  cloud: path('M16 58C-1 57 0 32 18 31C13 8 44 0 53 22C73 13 88 45 67 56Z',wash)+path('M28 38L39 27L50 38M39 29V62','none',green,3),
  phone: path('M22 4Q41 1 59 5L60 74L21 74Z',card)+path('M28 13H53V62H28Z',wash)+path('M35 8H46')+circle(41,68,2,marker)+path('M32 38L39 45L50 28','none',green,3),
  database: path('M12 18C12 2 68 2 68 18V62C68 77 12 77 12 62Z',wash)+path('M12 18C12 32 68 32 68 18M12 40C12 54 68 54 68 40')+path('M21 60Q39 68 59 60','none',green,3),
  sheets: rect(17,5,48,60,wash)+rect(9,14,48,60)+path('M19 27H45M19 39H45M19 51H36'),
  clock: circle(39,39,29,wash)+path('M39 19V39L54 48','none',ink,3)+path('M18 7L9 16M60 7L70 16')+circle(39,39,3,marker),
  bolt: path('M43 5L18 42H35L29 75L65 30H45Z',marker),
};
function svg(title, subtitle, content, description) {
  const defs=Object.entries(symbols).map(([name,body])=>`<symbol id="icon-${name}" viewBox="0 0 80 80">${body}</symbol>`).join('');
  return `<svg xmlns="http://www.w3.org/2000/svg" width="480" height="640" viewBox="0 0 480 640" role="img" aria-labelledby="title desc">
<title id="title">${esc(title)}</title><desc id="desc">${esc(description)}</desc>
<defs>${[ink,green].map(color=>`<marker id="${color===green?'green-arrow':'arrow'}" viewBox="0 0 12 12" refX="10" refY="6" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M2 2L10 6L2 10" fill="none" stroke="${color}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></marker>`).join('')}
<pattern id="grain" width="47" height="43" patternUnits="userSpaceOnUse"><circle cx="5" cy="12" r=".65" fill="${ink}" opacity=".045"/><circle cx="31" cy="33" r=".5" fill="${ink}" opacity=".04"/></pattern>${defs}</defs>
<rect width="480" height="640" rx="10" fill="${paper}"/><rect width="480" height="640" fill="url(#grain)"/>
<g fill="${ink}" font-family="'Microsoft YaHei','Noto Sans CJK SC',sans-serif">
${highlight(26,48,128,9)}${strong(24,48,title,32)}${text(24,91,subtitle,26,`fill="${soft}"`)}
${content}
</g></svg>\n`;
}
const figures = {};

// IG-008: the route carries the order, and the icons represent the work.
const route = [
  ['找问题','真实困扰','search'],['筛方向','选择对象','filter'],
  ['做访谈','核对经历','talk'],['看需求','明确任务','task'],
  ['收敛方案','定下边界','diamond'],['做原型','走通流程','browser'],
  ['打磨交付','作品与反馈','deliver'],['接 AI 能力','检查回执','plug'],
];
figures['learn-path'] = svg('八步，做出第一个作品','每一站，都留下一份可检查的结果。',
  route.map(([title,result,symbol],i)=>{
    const col=i%2,row=Math.floor(i/2),x=col?270:26,y=119+row*108,n=[1,2,4,3,5,6,8,7][i];
    return icon(symbol,x,y,46)+strong(x+53,y+31,`${n} ${title}`,26)+text(x+4,y+76,result,26);
  }).join('')+
  arrow('M224 149Q242 146 254 149',green)+arrow('M367 203Q372 215 367 225',green)+
  arrow('M254 257Q239 261 224 257',green)+arrow('M120 312Q116 325 120 333',green)+
  arrow('M224 365Q241 362 254 365',green)+arrow('M367 420Q372 431 367 441',green)+
  arrow('M254 473Q239 477 224 473',green)+
  highlight(26,570,426,42)+text(40,602,'反馈推翻假设，就回到对应步骤。'),
  '八个步骤按蛇形路径排列：找问题、筛方向、看需求、做访谈、收敛方案、做原型、接 AI 能力、打磨交付。反馈可以使流程回到前面的步骤。');

// IG-008: evidence and a visible test result are the anchors of the loop.
figures['error-flow'] = svg('排错，把猜测变成证据','同一输入、同一操作，比较前后结果。',
  [['复现问题','记下实际与预期','error'],['收集证据','错误原文与请求','evidence'],['只改一处','保存旧版再修改','patch'],['原步骤复测','再查相邻功能','passed']].map(([title,note,symbol],i)=>{
    const y=116+i*99;
    return number(44,y+38,i+1)+icon(symbol,83,y,75)+strong(178,y+35,title)+text(178,y+73,note,26)+(i<3?arrow(`M44 ${y+61}Q40 ${y+78} 44 ${y+112}`,green):'');
  }).join('')+
  path('M157 507L157 527L357 527L357 540')+arrow('M157 527L157 540',green)+
  highlight(27,551,204,38)+text(40,581,'通过：保留修改')+text(257,581,'失败：撤回修改')+
  arrow('M428 548L453 548L453 244Q454 221 429 229',ink,true)+text(24,620,'带着新证据，再验证一个原因。',26,`fill="${soft}"`),
  '四步排错：复现、收集证据、最小修改、复测。复测通过则保留修改，失败则撤回并返回收集证据，不把 AI 的建议直接当作结论。');

// IG-004: same data, two access paths. Green marks a path, not timing.
figures['db-index'] = svg('索引，先缩小查找范围','同样找编号 6，访问路径怎样变？',
  strong(24,143,'扫描：逐条判断')+
  path('M22 170L454 168L458 260L26 262Z',wash,'none')+
  Array.from({length:8},(_,i)=>rect(26+i*54,184,46,49,i===5?marker:card)+mid(49+i*54,218,i+1,28)).join('')+
  arrow('M34 251Q240 256 444 251')+text(24,297,'是否提前停止，由查询计划决定。',26,`fill="${soft}"`)+
  strong(24,354,'索引：按范围找到叶子')+rect(148,381,184,55,marker)+mid(240,418,'3  |  5  |  7',28)+
  [0,1,2,3].map(i=>arrow(`M${180+i*40} 442Q${74+i*110} 462 ${74+i*110} 483`,i===2?green:soft,i!==2)+
    rect(26+i*110,492,96,50,i===2?marker:card)+mid(74+i*110,527,`${1+i*2}  ${2+i*2}`,28)).join('')+
  path('M304 508Q322 502 324 518Q324 537 307 535','none',green,2.8)+
  text(24,575,'定位 6 后，按需读取完整记录。')+text(24,616,'树高不等于磁盘读取次数或耗时。',26,`fill="${soft}"`),
  '上半图八条记录依次扫描，编号 6 被标出。下半图用分隔键 3、5、7 指向四组叶子，绿色路径选择 5、6，再定位 6。形状只示意访问路径，不承诺性能。');

// IG-008 + IG-004: a release travels from source to another device.
figures['deploy'] = svg('上线，要走到真实设备','前提：仓库与部署平台已经连接。',
  icon('laptop',63,126,106)+icon('build',306,126,106)+
  mid(116,270,'1 提交推送',28,'font-weight="700"')+mid(360,270,'2 构建检查',28,'font-weight="700"')+
  arrow('M192 179Q238 172 285 179',green)+arrow('M360 289Q366 304 360 318',green)+
  icon('phone',66,325,103)+icon('cloud',306,325,106)+
  mid(116,459,'4 真机验收',28,'font-weight="700"')+mid(360,459,'3 部署版本',28,'font-weight="700"')+
  arrow('M286 378Q237 386 190 378',green)+
  path('M24 491Q239 487 456 492','none','#e6e1d4',2)+text(24,532,'构建失败，先看日志再重试。')+
  icon('sheets',30,552,42)+text(83,581,'代码回滚')+icon('database',267,552,42)+text(320,581,'数据恢复')+
  text(24,620,'恢复数据要另查迁移与备份。',26,`fill="${soft}"`),
  '电脑上的代码经过提交推送、平台构建检查、版本部署，再在另一台手机上验收。底部区分代码回滚和数据恢复；失败先看日志，数据恢复需查迁移与备份。');

// IG-002: containers and network boundaries do the explanatory work.
figures['web-framework'] = svg('架构，先看部署的边界','同一个业务，可以有不同组织方式。',
  strong(24,142,'单体')+text(255,142,'一起发布与扩缩')+
  rect(28,160,424,102)+path('M30 183H450')+
  [0,1,2].map(i=>circle(40+i*10,172,2,marker)).join('')+
  ['订单','库存','用户'].map((label,i)=>rect(45+i*137,197,114,47,marker)+mid(102+i*137,229,label,26)).join('')+
  strong(24,309,'服务')+text(255,309,'各自发布与扩缩')+
  rect(28,333,156,74)+rect(296,333,156,74)+path('M30 352H182M298 352H450')+
  mid(106,387,'订单',28)+mid(374,387,'库存',28)+mid(240,350,'网络',26,`fill="${soft}"`)+arrow('M198 379L281 379',green)+
  text(24,448,'跨服务调用：处理超时与一致性。',26,`fill="${soft}"`)+
  strong(24,493,'函数')+text(255,493,'由事件触发执行')+
  icon('bolt',24,516,65)+arrow('M100 547L165 547',green)+rect(180,519,117,58,marker)+mid(238,558,'函数',28)+
  arrow('M311 547L366 547',green)+icon('database',381,514,68)+
  text(24,616,'托管环境后，权限与数据仍要管理。',26,`fill="${soft}"`),
  '单体将三个模块放在一个部署边界内；服务将订单与库存分开放置并通过网络通信；函数由事件触发并访问数据。三种方式可以并存。');

// IG-008: changes become snapshots, and branch names point at commits.
figures['git-history'] = svg('Git，给修改留一条来路','先看状态，再选内容，最后提交。',
  icon('sheets',44,120,69)+icon('task',204,120,69)+icon('deliver',367,120,69)+
  mid(80,224,'工作区',26)+mid(240,224,'暂存区',26)+mid(400,224,'仓库',26)+
  arrow('M128 151L182 151',green)+arrow('M287 151L344 151',green)+
  mid(157,184,'add',26,`fill="${soft}"`)+mid(318,184,'commit',26,`fill="${soft}"`)+
  arrow('M100 338L216 338')+arrow('M265 338L375 338')+
  arrow('M93 356Q144 421 213 424',green)+arrow('M266 424Q350 423 386 362',green)+
  [[77,338,'A'],[240,338,'B'],[400,338,'D'],[240,424,'C']].map(([x,y,label])=>circle(x,y,23,label==='D'?marker:card)+mid(x,y+10,label,28)).join('')+
  highlight(347,267,106,30)+text(360,292,'main',26)+arrow('M400 300L400 308')+
  text(51,459,'feature',26)+arrow('M152 452Q177 452 208 434')+
  text(24,504,'分支名指向提交；D 合并 B 与 C。')+
  rect(24,543,153,50)+rect(303,543,153,50)+mid(100,577,'本地',26)+mid(380,577,'远程',26)+
  arrow('M189 554L290 554',green)+arrow('M291 582L189 582')+
  mid(240,538,'push',26)+mid(240,618,'fetch',26),
  '文件修改经过 add 进入暂存区，经 commit 保存为提交。A 分出 B、C，D 合并两条历史；main 指向 D，feature 指向 C。push 从本地到远程，fetch 从远程到本地。');

// IG-013: narrowing qualitative criteria, not a numerical score.
figures['funnel'] = svg('筛方向，先给点子找证据','从一组想法，收敛到可验证的选择。',
  icon('talk',53,119,42)+icon('task',179,111,45)+icon('browser',304,120,46)+
  path('M24 177Q238 165 456 177L409 265H71Z',card)+
  path('M71 277Q240 270 409 277L370 365H110Z',wash)+
  path('M110 377Q240 370 370 377L330 465H150Z',marker)+
  mid(240,214,'最近真的遇到过？',28,'font-weight="700"')+mid(240,250,'问一次具体经历',26)+
  mid(240,314,'已经投入了什么？',28,'font-weight="700"')+mid(240,350,'看时间、钱与行动',26)+
  mid(240,414,'愿意换做法？',28,'font-weight="700"')+mid(240,450,'差异与代价',26)+
  arrow('M240 475Q236 491 240 505',green)+
  highlight(71,526,338,37)+mid(240,554,'留下 1–2 个方向做实验',28,'font-weight="700"')+
  text(24,609,'暂时缺证据，可以退回去继续问。',26,`fill="${soft}"`),
  '想法经过三个逐层收窄的筛选：真实发生的经历、已有投入、相对现有做法的差异与切换代价。最后选择一两个方向做实验，图形宽度不是数量或转化率。');

// IG-002: one concrete meeting artifact, annotated with interview lenses.
figures['jtbd'] = svg('先问清，用户要完成什么','用一场会后的工作，理解 JTBD。',
  icon('clock',29,119,58)+strong(102,146,'具体情境')+text(102,183,'会刚开完，信息还很零散。',26)+
  arrow('M63 189Q65 217 115 239',green)+
  rect(139,225,201,196)+path('M158 285H320','none',soft,2)+
  highlight(156,246,166,26)+mid(239,269,'会后行动清单',28,'font-weight="700"')+
  [323,361,399].map((y,i)=>path(`M159 ${y-9}l5 5 9-12`,'none',green,2.7)+text(185,y,['任务','责任人','截止时间'][i],26)).join('')+
  arrow('M349 311Q421 308 422 391',green)+strong(26,452,'期望结果')+text(26,492,'明确谁在何时完成什么。',26)+
  icon('sheets',367,427,65)+path('M24 519Q240 515 456 520','none','#e6e1d4',2)+
  strong(26,557,'现有做法')+text(26,598,'靠回忆、翻录音、逐个追问。',26),
  '具体情境是一场会议结束，信息零散。中心画出会后行动清单的任务、责任人和截止时间。期望结果是明确谁何时完成什么，现有做法是靠回忆、翻录音与逐个追问。');

for (const [name, content] of Object.entries(figures)) {
  const file = resolve(root, 'book/assets/handdraw', `${name}.svg`);
  if (checking) {
    if (readFileSync(file, 'utf8') !== content) throw new Error(`Stale original figure: ${name}`);
  } else writeFileSync(file, content);
}
const gallery = `<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>原书手绘图解 · Vibe Coding 101</title><style>
*{box-sizing:border-box}body{margin:0;background:${paper};color:${ink};font:18px/1.8 "Microsoft YaHei",sans-serif}main{max-width:1060px;margin:auto;padding:32px 24px}h1{font-size:32px;line-height:1.4}a{color:${green};text-underline-offset:4px}a:focus-visible{outline:3px solid ${green};outline-offset:4px}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:48px 32px;margin-top:32px}figure{margin:0;min-width:0}img{display:block;width:100%;height:auto;max-width:480px;margin:auto}figcaption{padding-top:12px;border-top:1px solid #e6e1d4;font-size:16px;color:${soft}}.grid a{display:block;cursor:zoom-in}@media(max-width:650px){main{padding:20px 16px}.grid{grid-template-columns:1fr;gap:32px}}
</style></head><body><main><p><a href="../../开始阅读.html">返回原书</a></p><h1>Vibe Coding 101 · 手绘图解</h1><p>沿箭头看顺序，沿绿色看当前路径。点击插图，可查看原尺寸。</p><div class="grid">${Object.entries(figures).map(([name,content])=>{
  const title=content.match(/<title id="title">([^<]+)<\/title>/)[1];
  const description=content.match(/<desc id="desc">([^<]+)<\/desc>/)[1];
  return `<figure><a href="../../book/assets/handdraw/${name}.svg" aria-label="打开大图：${title}"><img src="../../book/assets/handdraw/${name}.svg" width="480" height="640" alt="${description}" loading="lazy"></a><figcaption>${title}</figcaption></figure>`;
}).join('')}</div></main></body></html>\n`;
const galleryPath=resolve(root,'design/handdraw/book-figures.html');
if (checking) {
  if (readFileSync(galleryPath,'utf8')!==gallery) throw new Error('Original-book illustration gallery is stale');
} else writeFileSync(galleryPath,gallery);
console.log(`${checking ? 'Verified' : 'Built'} ${Object.keys(figures).length} original-book figures`);
