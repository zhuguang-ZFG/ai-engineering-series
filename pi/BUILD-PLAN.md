# Pi 分册接入 yuyu-book：实施记录

状态：**已接入**（v0.1.0-wip，2026-11-08）。`make book-pi` / `make book-pi-pdf` 可跑，CI 有独立 `pi` job。
本页保留施工时的改动清单，并记录实际落地与偏差。

## 目标产物

| 产物 | 文件名 | 说明 |
| --- | --- | --- |
| 中文 HTML | `yuyu-pi-zh.html` | 单文件离线，Mermaid 预渲染，图片 data-URI |
| 中文 PDF | `yuyu-pi-zh.pdf` | 同御舆/Omp 的 A4 后处理 |
| EPUB | `yuyu-pi-zh.epub` | 由 `scripts/build_epub.py` 从已验证 HTML 后处理，EPUBCheck 0 错误 |

- `product: "pi"`，`output_prefix: "yuyu-pi"`，`langs: ["zh"]`。
- 与 `yuyu-agent-harness-*`、`yuyu-omp-*` 不共用前缀，构建不会互相覆盖。

## 现有链路（复用，不改内核）

```text
make book-pi
  └─ scripts/bookctl.py build --product pi --lang zh [--pdf]
       └─ yuyu-book/build.py --manifest manifest-pi.json --sources sources-pi.json
            ├─ registry.load()          登记表读取 + schema 校验
            ├─ plain.load_plain()       术语层 / 分级阅读路径
            ├─ plain.load_notes()       每单元眉批
            ├─ units.load_unit()        H1 解析、图版、代码块
            ├─ render / style_*         屏幕与印刷样式
            └─ pdf.py                   浏览器打印 + 书签
```

Pi 分册只提供**数据**（manifest、glosses、notes、reading-paths、sources、revisions、插画），
共享构建器与图版管线。

## 必须改的地方

按依赖顺序；每一处都写清楚"为什么必须改"，施工时不要漏。

### 1. 登记表白名单

`yuyu-book/yuyu_book/registry.py` 的 `FILES` 元组是**显式白名单**，不在表里的文件名直接报
`unknown registry`。要加：

```text
manifest-pi.json
glosses-pi.json
sources-pi.json
notes-pi.json
reading-paths-pi.json
revisions-pi.json
```

`subject-index` 不排（manifest 里 `subject_index_registry: null`），所以不加 `subject-index-pi.json`。

### 2. 通俗层命名：不用改代码

`plain.registry_names()` 只按 `manifest["product"]` 加后缀：`book` → 裸名，其他 → `-<product>`。
`product: "pi"` 会自动去找 `glosses-pi.json` / `notes-pi.json` / `reading-paths-pi.json`。
**前提**是 manifest 里真的写 `"product": "pi"`；漏写会退回 `book` 的裸名，直接改坏御舆的登记表。

### 3. 章徽 / 篇题刻托盘

`yuyu-book/yuyu_book/art.py` 的 `_search_dirs()` 目前只搜 `illustrations-omp/` 和 `illustrations/`，
**没有产品参数**。做法：

- 新建 `yuyu-book/illustrations-pi/`，加进 `_search_dirs()` 的搜索列表；
- 所有 SVG 的 `id` 以 `pi-` 开头（与 `omp-` 同规则），保证一次搜索里不会撞号；
- 遵守既有门禁：无 `<script>` / `<style>` / `id=` / `href=` / `url()`，颜色一律 `currentColor`；
  单枚 ≤ `MAX_BYTES`（6000 B），篇题刻 ≤ `PLATE_BYTES`（20000 B）；
- 数量：25 章各一枚章徽 + 6 篇各一幅篇题刻 = **31 份**（篇数按 `outline.md`，成稿时对齐）。

### 4. CLI 产品开关

`scripts/bookctl.py` 有两处硬编码：

- `build()` 开头 `if args.product not in ("book", "omp")`；
- `argparse` 的 `choices=["book", "omp"]`。

加 `pi` 分支：中文单语（`lang == "en"` 直接拒绝），传 `--manifest manifest-pi.json
--sources sources-pi.json`。不要把 `omp` 分支复制一遍改字符串——抽一张
`{product: (manifest, sources, langs)}` 表更省事，但那是重构，单独提交。

### 5. Makefile

```make
book-pi:
	$(BOOKCTL) build --product pi --lang zh

book-pi-pdf:
	$(BOOKCTL) build --product pi --lang zh --pdf
```

同时更新 `.PHONY` 与 `help` 两行文案。

### 6. 五份登记表

| 文件 | 关键约束（来自现有校验器） |
| --- | --- |
| `manifest-pi.json` | `product: "pi"`、`output_prefix: "yuyu-pi"`、`langs: ["zh"]`、`plain_optional: false`、`revisions_registry: "revisions-pi.json"`、`subject_index_registry: null`；units 的 `zh` 路径指向 `pi/*.md` |
| `glosses-pi.json` | 每个词条要有 `file:line` 或稳定 block id 作证据，且该行真的出现注册形式；每单元新标词 ≤ `MAX_PANEL`（22） |
| `notes-pi.json` | 每个 unit 一条，中文 ≤ 36 字；眉批里必须出现该章正文用过的注册术语 |
| `reading-paths-pi.json` | 每章按 H2 给档位（起步 / 主干 / 进阶），H2 增删时同步 |
| `sources-pi.json` | 固定 tag 或完整 SHA；Pi 上游、文档页、本机验证记录分开登记 |
| `revisions-pi.json` | 版本修订说明；`build.py` 会把它渲染到书末 |

这五份表**等正文写完再生成**。现在预置空表，构建器会当成"有内容"去校验，然后失败——
这正是 Omp 分册当年踩过的坑，不重复。

### 7. 测试

- `yuyu-book/tests/test_product_isolation.py`：加 `pi` 的 manifest、前缀、语言、单元数断言；
  重点验证 `registry_names()` 不会把 pi 的通俗层写到御舆或 Omp 上。
- `yuyu-book/tests/test_mixed_art.py` / `test_art.py`：`pi-` 托盘的搜索顺序、字节预算、id 前缀。
- `tests/test_docclaims.py`：README / PRODUCTS 里"已构建/页数/体积"的说法必须与实测一致；
  在产物存在之前，文档只能写"未开始"。

### 8. CI

`.github/workflows/` 里 `book` 与 `omp` 是独立 job。加 `pi` job，复用同一套步骤：
结构门禁 → `build.py --check` → `bookctl build --product pi --pdf` → artifact `yuyu-pi-dist`。
**只有正文和产物都齐了才加**；先加 CI、后补登记表，会让远端一直红。

### 9. 文档面

- `yuyu-book/PRODUCTS.md`：加一行 `pi`，状态写"试章，构建未接入"；
- `docs/portal.html` 的产物卡片：等有可下载产物再加链接，否则就是死链；
- 根 `README.md` / `en/README.md`：登记第三分册时只写已有内容，不写页数与体积。

## 施工顺序与门禁

| 阶段 | 内容 | 通过条件 |
| --- | --- | --- |
| P0（done） | 钉版、目录、前言、第 1–3 章 | `check_book.py` 0 errors；本章证据进 `VERIFY.md` |
| P1（done） | 第 4–25 章 + 5 附录 + 每章证据 | 六要素逐章通过；`check_book.py` 0 errors |
| P2（done） | `manifest-pi.json` + glosses/notes/reading-paths/sources/revisions + 白名单 | `build.py --check` 成功，31 units / 218 glosses / 31 notes |
| P3（done） | `illustrations-pi/` 43 份（31 章徽 + 6 篇题刻 + 6 正文长图） | 43 份全部过 `art._read`；`PiArtTray` 3 项通过 |
| P4（done） | `bookctl` + Makefile + Pi 产品隔离测试 | `make book-pi` 产出 HTML；`unittest test_product_isolation` 21 项通过 |
| P5（done） | PDF + EPUB + CI + 产物核对 | 159 页 / 40 书签 / 9.00 MB；EPUB 1.05 MB，EPUBCheck 0 错误 |

施工顺序已按本表走完。唯一偏差：`plain_optional` 最终是 `false`，通俗层在 P2 一并接入，没有再留一版
`--no-plain` 的产物；`--no-plain` 仍是 `build.py` 的正式开关。

## 实际落地（2026-11-08）

- 登记表白名单：`manifest-pi.json`、`glosses-pi.json`、`sources-pi.json`、`notes-pi.json`、
  `reading-paths-pi.json`、`revisions-pi.json`。
- `art.py`：新增 `PI_ART_DIR`，搜索顺序 OMP → PI → 共享。
- `bookctl.py`：`pi` 分支（中文单语，`manifest-pi.json` + `sources-pi.json`）；`argparse` 三产品。
- `Makefile`：`book-pi` / `book-pi-pdf`。
- 登记表：31 unit、31 guide、12 词条、31 眉批、156 档位、2 个来源。
- 插画：`scripts/draw_pi_illustrations.py` 生成 43 份 SVG；6 幅正文长图经 ```ill 槽进入正文。
- 测试：`yuyu-book/tests/test_product_isolation.py` 新增 `PiProduct` / `PiArtTray`。
- CI：`book.yml` 新增独立 `pi` job；`check-book.yml` 新增 pi 源稿装配。
- 共享修复：print CSS 把 `.route-map .itinerary` 收至 88%，让 31 个 unit 的路线图在 A4 上保持一页。

## 明确不做

- 不复制 `omp` 的登记表内容改个名字（术语、注、路径都是按章写的，抄过来是错的证据）。
- 不共用 `illustrations-omp/`（章徽编号与 `omp-ch*` 前缀会串册）。
- 不把 pi 加进 `book` 的 manifest 走"一本大书"（产物前缀、语言、版本钉都不同）。
- 不在正文没写完时生成"占位 PDF"——页数和体积会被 `test_docclaims` 逮住，也不诚实。
