# Legacy / v2 structural comparison (P3.7)

## Frozen-worktree investigation — 2026-11-07

**Output contracts passed in the frozen working-tree experiment below.**
Its original provenance-test failure is retained as historical evidence.
The later isolated candidate is documented separately at the end of this report;
it does not mark the P3 Gate or the new test/policy baseline approved.

## Comparison boundary

- Frozen P0 report: `docs/baseline/baseline.json`, source commit
  `06bd6fbef73e28023035b9a3c01bb0c9e4c1eb6e`.
- Legacy kernel for the remaining cutover: HEAD
  `dcdc3950425178a4f4639901641d43161dc81b00`.
- Current kernel: a frozen copy of the uncommitted `feat/p3-style-split` working tree.
  This is not a claim that those working-tree changes have been committed or reviewed.
- Both kernels consumed the same 1,071 manuscript, registry and asset files.
  Their input SHA-256 inventory was compared before running either build.
- Input-inventory fingerprint:
  `62777f4b1cec7092f9658d14c96f0576ad6af677e4fd68ea7844ebad1e72c535`.
- Builds and machine-readable evidence are local to `.scratch/p3-resume-20261107/`;
  `yuyu-book/dist/` was not rebuilt or edited by this task.

The legacy side overlays only the committed `yuyu-book/build.py` and
`yuyu-book/yuyu_book/` implementation onto the frozen current inputs. It therefore
isolates kernel changes from P5 manuscript additions instead of comparing different books.
Each side ran this existing entry point in its own directory:

```text
npm.cmd ci
python -u yuyu-book/build.py --lang both --pdf --out-dir ../<side>-dist
```

Both builds completed with exit code 0. No release or fact-validation check was disabled.

## Structural and runtime results

The existing `baseline.normalized` and `compare_legacy.diff_reports` functions found
**zero structural differences** between the two same-input builds. No allowlist was
needed for that comparison.

| Measured contract | Chinese | English |
|---|---:|---:|
| Content units, both kernels | 20 | 20 |
| Mermaid plates, both kernels | 176 | 176 |
| PDF pages, both kernels | 525 | 577 |
| PDF bookmarks, both kernels | 28 | 28 |
| Landscape PDF pages, both kernels | 18 | 25 |
| Printed subject-index rows checked | 238 | 116 |
| Unique index targets checked | 14 | 14 |
| Index folio drift | 0 | 0 |
| Furniture-only blank pages | 0 | 0 |
| HTML scripts / external runtime resources | 0 / 0 | 0 / 0 |
| Broken HTML anchors / duplicate IDs | 0 / 0 | 0 / 0 |

For every PDF page, text hashes, dimensions and link targets matched between kernels;
the complete bookmark trees matched too. Embedded CJK subset fonts were found in both
editions. The normal PDF pipeline also completed its measuring-print, contents-row
stamping, index-folio and blank-page checks.

Both current editions were opened in a real browser with page JavaScript disabled and
network access offline. Chapter 2 remained readable, and clicking its source chip
navigated to `#source-docs-how-it-works`. PDF cover, chapter and backmatter pages were
rendered for inspection. These are manual runtime checks, not operator-configured checks.

## Differences that are not structural equality

Do not interpret the result as whole-file byte identity:

- The split stylesheet contains the separately implemented P4 reduced-motion SVG rule.
  It adds 223 bytes to the earlier aggregate; it is not a print-rule change or a pure
  file-split effect. The earlier CSS hash `fa65c59f…` describes the split before that addition.
- Cold Mermaid renders can change drawing coordinates. The Chinese bodies were identical
  outside SVG; eight SVGs differed, with 41 path-coordinate changes and one line's
  `x1`/`x2` values changing. Text, node structure and view boxes were unchanged.
- A one-diagram experiment using the same kernel and source with two empty caches
  produced different SVG hashes with the same view box. This establishes a renderer
  repeatability limitation, not evidence that a kernel split changed chapter structure.

The measured PDF text, destinations and pagination still matched. No assertion or
comparison policy was weakened to erase the SVG byte differences.

## P0 delta accounting is not provenance approval

Against the frozen P0 report, the fresh current report has 93 structural leaf
differences. All 93 match the existing `docs/baseline/legacy-v2-deltas.json` rules;
zero are unmatched. That matcher result does **not** make the rules traceable:

- 21 of the 34 rules use `working tree (P5…)` or combined descriptions instead of a
  7–40 character commit SHA. The pinned provenance test rejects the first such value.
- Four version/date rules use exact `legacy` / `fresh` values, which the production
  matcher supports, but the same fixed test also requires `delta` on every rule.
  This is a separate contract-review issue, not permission to alter the test here.
- Searching available commit history for the P5.5 chapter-11 exercise marker found
  no containing commit. An existing unrelated SHA cannot honestly replace its provenance.

Required next decision: separate and review the uncommitted P5 content changes, establish
their real commit provenance, and review how exact-value rules satisfy the fixed gate.
Do not fabricate SHAs, remove rules, weaken assertions or begin P6 under a GREEN claim.

## Executed verification

- `python -m unittest discover -s yuyu-book/tests -v`: **541 passed**.
- `python -m unittest tests.test_compare_legacy -v`: **9 passed, 1 failed**,
  `AllowlistFile.test_every_rule_is_traceable`.
- `python -u scripts/bookctl.py check --fast`: dependency consistency and both source
  assemblies passed; general tests were **126 passed, 1 failed**, at the same provenance
  assertion. Later steps of that command were not executed after the failure.
- Same-input rendered HTML/PDF comparison and offline browser smoke: **passed** as above.
- `task_verify(action=run)` returned **unverified**,
  `project-or-git-baseline-unavailable`, with `checks=[]`; no operator-configured
  checks ran. Manual checks do not replace that status.

The P3 Gate remains unchecked. The output-equivalence investigation is complete; the
provenance/test-contract review is still required before phase advancement.

## Isolated provenance candidate — review required

The local branch `feat/p5-provenance-gate` is rooted at `dcdc395` and lives in
`D:/Users/claude/.p5-provenance-wt`. The original branch, index and source files were
left unchanged. This candidate intentionally excludes the uncommitted P3 style split,
P4 product adapters and P6 video work from that original tree.

- Content provenance: `6d4e3c0475d28d2ebb7630518a2f6721c9a01620` contains 41 scoped P5
  files: both editions' runnable cases, claim markers, six paired ledger entries,
  ledger implementation, build admission and contribution guidance.
- The P5-only builder suite contains 538 tests, not the mixed tree's 541. The newest
  revision note reflects that scope; historical revision entries remain unchanged.
- Regression RED checkpoint: `ecc90c49eb9baa47cc6c74943fcb0729c40ce472`. Existing diff
  and matching cases passed; new rule-loading cases failed because no input-validation
  boundary existed. The same rule suite passed after that boundary was implemented.
- All 34 matching rules retain their paths, kinds, deltas and exact before/after values.
  Only 21 placeholder provenance fields now name the real P5 content commit. No rule
  was added or broadened to hide structural drift.
- The CLI validates non-empty rules, path/reason/kind, finite numeric increments,
  complete exact pairs and available commit objects before opening built artifacts.
  Invalid inputs return 2; uncovered structural drift still returns 1.

### Review scope and recurrence prevention

The old JSON-shape test conflated provenance with a requirement that every rule use a
numeric `delta`, even though the production matcher already supports exact values.
It is replaced with consumer-visible regressions, not a skipped assertion: source SHA
format and existence, both exact endpoints, numeric mismatch, one-sided/missing bounds,
ambiguous mixed bounds, malformed documents and the CLI failure path are exercised.
The known release is covered while a different release remains unmatched.

This is a cross-layer contract bug: file-shape checks lived only in tests while the CLI
trusted raw rules. Runtime admission now enforces the same constrained forms that the
matcher consumes. `CONTRIBUTING.md` §5.5 states that reviewers must still verify the
content explanation; a resolvable commit alone does not prove causation.

New or imported tests and the provenance policy file remain **unverified pending review**
under the turn-start baseline. The original source failure was not patched in place;
the candidate is neither pushed nor merged. The P3 and P5 acceptance gates remain
unchecked until this review and integration are complete.

### Exercised candidate checks

- Chapter exercises: 4 tests passed, including execution of all 15 examples and matching
  code across the two editions. Claim-ledger boundary tests: 17 passed.
- Isolated builder suite: 538 passed. Bilingual source assembly: CHECK OK.
- Comparator regressions: 19 passed after the fix. The CLI rejects the unchanged original
  placeholder policy with exit 2 before artifact loading, rather than reporting GREEN.
- CLI smoke against the retained `.scratch/p3-resume-20261107/current-dist` artifacts:
  93 differences, 93 constrained matches, 0 unexpected, exit 0. Those are explicitly
  reused prior-build artifacts; no new PDF build is claimed for this branch.
- A subsequent Fast run found the release readers still labelled 0.3.5. Both readers
  were regenerated with the existing committed generator, not P4 adapters; two runs
  produced identical hashes. The unchanged reader suite then passed all 8 tests.
- After that regeneration, the unchanged Fast runner completed all 6 steps: 90 general
  tests and 538 builder tests passed; content checked 187 Markdown files and 333 Mermaid
  diagrams with 0 errors; the Mermaid CLI separately checked 333 diagrams with 0 errors.
  Browser smoke opened both regenerated readers, confirmed version 0.3.6 and inspected
  the rendered Chinese opening and English layout without horizontal page overflow.
- `task_verify(action=run)`: unverified, `project-or-git-baseline-unavailable`, `checks=[]`.

## 2026-11-08 现状复核

上面「Isolated provenance candidate — review required」与「Required next decision」两节是
2026-11-07 的候选状态记录。`v0.3.6` 发布后前提已变，按 `origin/main`（`ffabfde`）复核：

- `6d4e3c0475d28d2ebb7630518a2f6721c9a01620` 已是 `origin/main` 的祖先，P5 内容、账本实现
  与运行案例都在主分支上。
- `docs/baseline/legacy-v2-deltas.json` 的 34 条规则全部带真实提交 SHA，没有
  `working tree (P5…)` 这类占位说明；加载器仍拒绝不存在的提交
  （`tests/test_compare_legacy.py::test_provenance_must_name_an_existing_commit`）。
- 34 条规则里 30 条用数字增量（`delta`），4 条用精确值对（`legacy`/`fresh`，分别是
  `/book/version`、`/book/date`、`/registries/manifest/version`、`/registries/manifest/date`）；
  两种形式都在 `compare_legacy.load_rules` 的读取边界校验：增量必须是有限数，精确对必须成对，
  `kind` 只接受 `value`/`len`，且规则不得同时给出增量与精确对。
- `tests/test_compare_legacy.py` 23 项全绿。
- `claims.validate(..., release=True)` 在 `ffabfde` 上返回 0 条告警（6 条 claim）。

这些是「来源字段可用」的现行证据，不是审阅结论：P3 Gate 与 P5 Gate 仍未勾选，测试与政策
变更的独立审阅仍由维护者完成。
