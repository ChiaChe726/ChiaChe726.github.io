#!/usr/bin/env bash
#
# push_usage.sh — 一鍵更新並推送 Claude Code 使用量到你的 GitHub Profile repo。
#
# 它會:
#   1) 跑 collect_usage.py  → 產生這台電腦的 data/usage/usage-<機器>.json
#   2) 跑 render_readme.py   → 更新 README.md 的使用量卡片
#   3) git add / commit / push(只動這個 repo;失敗會自動重試)
#
# 用法:在這個 repo 目錄下執行
#     ./push_usage.sh
#
# 前置:這台電腦已經 git clone 你的 profile repo,且已設好可以 push 的認證。

set -euo pipefail
cd "$(dirname "$0")"

PY="$(command -v python3 || command -v python)"
if [ -z "$PY" ]; then
  echo "❌ 找不到 python3,請先安裝 Python 3.8+。" >&2
  exit 1
fi

echo "▶ 收集本機使用量…"
"$PY" collect_usage.py

echo "▶ 更新 README 卡片…"
"$PY" render_readme.py

# 只有真的有變更才 commit
if git diff --quiet -- README.md data/usage 2>/dev/null; then
  echo "ℹ️ 使用量沒有變化,不需要推送。"
  exit 0
fi

echo "▶ 提交並推送…"
git add README.md data/usage
git commit -q -m "chore: update Claude Code usage stats" || true

# 推送 + 網路失敗時退避重試(2s,4s,8s,16s)
branch="$(git rev-parse --abbrev-ref HEAD)"
delay=2
for attempt in 1 2 3 4 5; do
  if git push origin "$branch"; then
    echo "✅ 已推送,使用量已更新到 GitHub。"
    exit 0
  fi
  if [ "$attempt" -lt 5 ]; then
    echo "⚠️ 推送失敗,${delay}s 後重試…" >&2
    sleep "$delay"
    delay=$((delay * 2))
  fi
done

echo "❌ 多次重試後仍無法推送,請檢查網路或 git 認證。" >&2
exit 1
