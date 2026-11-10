# SITE-LINKS · 门户链接检查表

Y-M5 Step 3 的产物。检查对象是 `scripts/build_site_portal.py` 生成的那张门户页，
提交在仓库里的预览副本是 `docs/portal.html`（`tests/test_site_portal.py` 把它钉成与
`build_site_portal.PAGE` 一致，所以本页任何结论都要靠再生成脚本、不靠手改这一份）。

## 基准：链接是相对**站点根**解析的，不是相对 `docs/`

`.github/workflows/pages.yml` 的 `Assemble the site` 把产物摆进 `site/` 后才部署，
门户自己也是在那一步现生的（`python scripts/build_site_portal.py site/index.html`，pages.yml:103）。
所以「`docs/portal.html` 用 `file://` 打开时报 3 个 `ERR_FILE_NOT_FOUND`」**不是缺陷**：
那三个引用在 `site/` 根有实体，在 `docs/` 旁边没有。判死链必须以站点根为准。

## 逐条（2026-11-04 实测）

| 门户里的引用 | 卡片 | 站点根上由谁给 | `docs/` 里 `file://` | 结论 |
|---|---|---|---|---|
| `book.html` | 御舆（`div.card` + `.go`） | `cp yuyu-book/dist/yuyu-agent-harness-zh.html`（pages.yml:95） | MISS | 部署后 OK |
| `yuyu-agent-harness-en.html` | 御舆卡 `English edition` | `cp dist/…-en.html`（pages.yml:97） | MISS | 部署后 OK |
| `cover.png` | 页头封面 `<img>` | `cp cover.png`（pages.yml:102；仓库根实有 863,198 B） | MISS | 部署后 OK |
| `beginner-reader.html` | 入门分册（中文） | `cp docs/…`（pages.yml:98） | OK | 两侧都 OK |
| `beginner-reader.en.html` | Beginner reader | `cp docs/…`（pages.yml:99） | OK | 两侧都 OK |
| `illustration-gallery.html` | 插画画廊 | `cp docs/…`（pages.yml:100） | OK | 两侧都 OK |
| `illustration-prompts.md` | 画廊卡内 | `cp docs/…`（pages.yml:101） | OK | 两侧都 OK |
| `https://github.com/yang0/handraw-style` | 画廊卡「画风体系来自」 | 外链 | — | `curl -sL -o /dev/null -w "%{http_code}"` → **200** |
| —— 第二分册 Omp 卡 | `div.card`，**整张没有 href** | 不部署（见下） | 无链接可坏 | 设计如此 |

`<link rel="icon">` 是 `data:image/svg+xml`，不外网取；页内除了 handraw-style 那一条外链，
再没有第二个 `http(s)://` 字面量（`http://www.w3.org/2000/svg` 只出现在 data-URI 的命名空间里，不是请求）。

## 为什么 Omp 那张卡故意不给链接

SPEC 的 M5 Step 2 要求「门户至少两张卡 … **无死链**」，而 G5 明确本阶段不要求 omp 已进 pages matrix。
omp 产物（`yuyu-omp-zh.html` / `.pdf`）只在 Book CI 的 `yuyu-omp-dist` 工件里，站点上取不到；
`omp/` 也还没进 HEAD（`git ls-tree HEAD omp/` 为空，GitHub 上点 `omp/README.md` 会是 404）。
两条路里选死路少的那条：**做成没有链接的 `div.card`**，卡上直接写「施工中」和本地构建命令
（`make book-omp` / `make book-omp-pdf`），说明书稿在仓库内的 `omp/` 目录。
上线时的正确做法与 `book.yml` 口径一致 —— 独立 workflow 出 omp 站点，
**不要**往 pages.yml 这条 deploy-pages 单产物链里加 `cp`（pages.yml:86–91 已写了这条 TODO 和理由）。

## 顺手抓到并修掉的一个真缺陷

门户原来把御舆卡写成 `<a class="card">`（指向 `book.html`），卡内又嵌了一个指向
`yuyu-agent-harness-en.html` 的 `<a>`——
HTML 不允许 `a` 套 `a`，解析器会提前闭合外层，浏览器 DOM 探针显示英文那条链接的父节点是 `.cards` 而不是卡片。
御舆卡因此改成 `div.card` + 显式 `.go` 链接。复测：`nested <a> inside <a>` = **0**，
5 张卡全部落在网格上（截图 3+2 两行）。

同一次改造还删掉了御舆卡上写死的「318 张图版」。真实口径是**每份书 176 张图版**，
出处不是人数的，是构建自己那一行统计（`logs/ci-local-yuyu-20261104-100401.log:58`/`:61`：
`… 20 units, 176 plates, …`，zh 与 en 各一行）；卡上那句保留的 `@@PLATES@@` 是另一个数 —— 42，
来自 `scripts/build_beginner_reader.py` 的 `PLATES`（手绘插图），它同时喂画廊卡那句「42 幅手绘插图」。
两个数混在一个句子里抄过一次，就再抄一次错；按仓库规则「derive or omit」，图版那半句改成不带数。

顺带记一个同源的小口径坑：`build_site_portal.py:139` 打印 `f"{out} ({len(PAGE)} bytes)"`，
`len()` 数是**字符**，UTF-8 落盘是字节 —— 同一份 `docs/portal.html` 它报 5,995，`wc -c` 是 7,297。
数字本身没错，单位标错了；这一页任何"多少字节"的结论都以 `wc -c` 为准。

## 复核命令

```powershell
python docs/yuyu-overhaul/check_site_links.py            # 离线，确定性
python docs/yuyu-overhaul/check_site_links.py --online   # 额外对每条外链发一次 HEAD
python -m unittest discover -s tests -p "test_site_portal.py" -v   # 钉 PAGE 与提交副本一致
python scripts/build_site_portal.py .scratch/site-preview/index.html   # 忠实预览（旁边缺那三个部署产物）
```

`check_site_links.py` 的判据不是「文件在不在 `docs/` 旁边」，而是「**站点根上有没有人放它**」：
发布清单直接解析 `.github/workflows/pages.yml` 的 `cp … site/…` 行（现测 9 个名字），
门户里任何本地引用不在清单里就是死链。它同时盯：`@@TOKEN@@` 有没有漏开、
`<a>` 有没有套 `<a>`、卡片数够不够两张分册、门文档（`README.md` / `en/README.md` / `STRUCTURE.md` /
`omp/BUILD.md`，M7 起再加 `docs/COMPARE-OMP.md`，现测 5 份）的相对链接落不落得在磁盘上。
五条负例都是实跑过的（临时副本 + 临时改 README 再还原，还原后逐字节相同）：
假发布目标 `omp-book.html` → exit 1；把御舆卡改回 `a` 造出嵌套 → exit 1；塞一个 `@@PLATES@@` 不展开 → exit 1；
把 README 里 `omp/README.md` 改成不存在的名字 → exit 1；在 `docs/` 下一份文档里写 `[x](SHARED-TERMS.md)`
（即「按仓库根想路径、按所在目录解析」这个最容易犯的错）→ 报 `dead relative link`。正例 exit 0 就是上面那张表。

顺带说明为什么这里不放一条 `powershell -Command` 的一行式：本轮试过，`\"` 在 PS 5.1 的传参层会被拆坏，
`data:` URI 会被 `href` 正则误抓成引用，`Join-Path` 遇到空值刷 27 行红字 —— 三个都是噪声源，不是判据。
判据放 Python，跨平台且可复跑。

`docs/` 侧的门面文档链接同轮扫过（按出现次数计，含重复引用）：`README.md` 36 处相对链接**全部**解析到磁盘上的实体、
11 处外链，0 死链（含 `omp/README.md`、`omp/BUILD.md`、`omp/VERIFY.md`、`STRUCTURE.md`）；
`en/README.md` 37 处相对链接同样全 OK、10 处外链、0 死链。
