# 插画重绘设计稿

2026-11-04：用户要求使用 yang0/handraw-style 提升美观度。此前局部遮盖补字稿仅存于 `.scratch/`，未替换正文插画；本轮按完整重绘处理。

## 统一方向

- 画风：FA-012，Minimal Visual-Pun Editorial；库内参考作者 Christoph Niemann。
- 主题色：C-25 爱马仕橙；浅底候选 C-30 象牙白。正式提示词当前只装配 C-25，底色由模型设计。
- 用途：知识图解。让图形承担层级、流程与对比，文字参与构图。
- 不改变已有知识、公式、版本边界和原始 Markdown；当前只设计三个替换点，不进行删文与全书重排。
- 图型：配置层级 IG-010；锚点修改 IG-004；来源核对 IG-008。
- 参考图策略：官方 resolver 对 gpt-image-2 / FA-012 返回 name+style 强激活，无需垫图。展示的库图仅用于选方向，不能当作本次生成结果。

## 样图队列

| 提示词 | 替换目标 | 验收重点 |
|--------|----------|----------|
| config-precedence.txt | images/fig23-1-config-layers.jpg | 六层顺序正确、profile 不独立成层、视觉方向明确 |
| anchored-edit.txt | images/fig9-2-hashline-vs-replace.jpg | 两处相同文本的歧义、目标行变化、过期重读 |
| source-verification.txt | images/fig12-3-web-github.jpg | 可追溯的来源路径、准确工具名、无虚构网址 |

提示词由安装版 `prompt_style.py` 装配，包含原生图型模板与图文模式后缀。画风与图型编号只写在元数据，不写进画面文案。

## 当前交付状态

三张样图提示词与可编辑 SVG 已完成；**2026-11-04 已用 Chrome headless 将 SVG 导出为 1440×960 JPG 并替换正文插画**（位图路线未跑 handraw / 未调用 imagegen；本机无 OPENAI_API_KEY）。

| 样张 SVG | 已替换正文 |
|----------|------------|
| config-precedence.svg | images/fig23-1-config-layers.jpg |
| anchored-edit.svg | images/fig9-2-hashline-vs-replace.jpg |
| source-verification.svg | images/fig12-3-web-github.jpg |

原 JPG 备份：`backup-jpg-20261104/`。中间渲染：`_render-*.png`。
导出质量 JPEG q=92。验收要点（六层顺序 / 锚点对比 / web_search+github 无虚构网址）已在导出图中保留。
后续问题图仍待整图重绘；有 API 时可按同套提示词跑 handraw 再覆盖这三张。


## 待复核的问题图

已关闭（SVG→JPG）：fig23-1、fig9-2、fig12-3（第一批）；以及 fig9-1、fig4-3、fig4-4、fig5-3、fig5-4、fig17-1、fig19-2、fig20-2、fig21-1、fig22-2、fig27-1、fig28-1、fig33-3（第二批手写）。

当前视觉改造问题图清单已清空；若正文后续新增插画再另开队列。

## 第二批手写 SVG（2026-11-04）

用户要求「你绘制」：未跑 handraw / 无 OPENAI_API_KEY。本批对齐样张风格手写 SVG → Chrome headless → JPG q=92。

| SVG | 正文 JPG |
|-----|----------|
| hashline-anchor.svg | fig9-1-hashline-anchor.jpg |
| alpine-pitfall.svg | fig4-3-alpine-pitfall.jpg |
| completions.svg | fig4-4-completions.jpg |
| login-flow.svg | fig5-3-login-flow.jpg |
| models-yml.svg | fig5-4-models-yml.jpg |
| model-roles.svg | fig17-1-model-roles.jpg |
| skill-invoke.svg | fig19-2-skill-invoke.jpg |
| mcp-transport.svg | fig20-2-mcp-transport.jpg |
| custom-tool.svg | fig21-1-custom-tool.jpg |
| ext-load.svg | fig22-2-ext-load.jpg |
| review-checklist.svg | fig27-1-review-checklist.jpg |
| sdk-embed.svg | fig28-1-sdk-embed.jpg |
| tool-registry.svg | fig33-3-tool-registry.jpg |

原 JPG 已写入 `backup-jpg-20261104/`。此前问题清单中的 13 项至此全部关闭（连同第一批 fig23-1 / fig9-2 / fig12-3）。
