#!/usr/bin/env bash
# 采集 omp 本机实跑证据，供书稿引用。
# 铁律：凭证类子命令只取 --help，绝不跑 omp token / auth export / usage（会打印密钥或账号信息）。
set -u
OUT="$(dirname "$0")/../facts/live-18.16.0"
mkdir -p "$OUT"
INDEX="$OUT/_manifest.tsv"
: > "$INDEX"
printf "command\texit\tbytes\tcaptured_at\n" >> "$INDEX"

run() { # run <slug> <timeout_secs> <args...>
  local slug="$1"; shift
  local tmo="$1"; shift
  local f="$OUT/$slug.txt"
  local start; start=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  timeout "$tmo" omp "$@" > "$f" 2>&1
  local code=$?
  local size; size=$(wc -c < "$f")
  printf "%s\t%s\t%s\t%s\n" "omp $*" "$code" "$size" "$start" >> "$INDEX"
  [ "$size" -eq 0 ] && rm -f "$f"
}

# ---- 元信息（无模型、无密钥） ----
run version 30 --version
run help-top 60 --help

# ---- 子命令 help（只读，安全） ----
for c in acp agents auth auth-broker bench browser-relay cleanse clip collab commit \
         completions compress config dry-balance find gallery gc git grievances if-bench \
         images install join login models play plugin predict ps read render say \
         search session setup share shell skill ssh stats stream tiny-models token toks \
         ttsr update usage worktree; do
  run "help-$c" 45 "$c" --help
done

# ---- 无模型可跑的真实子命令 ----
run models-list 90 models
run toks-self 60 toks omp/README.md
run completions-bash 45 completions bash
run config-list 60 config --help

echo "captured $(wc -l < "$INDEX") manifest rows into $INDEX"
