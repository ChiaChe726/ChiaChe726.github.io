#!/usr/bin/env bash
#
# push_usage.sh — 一鍵更新並推送 Claude Code 使用量到你的 GitHub Profile repo。
#
# 它會:
#   1) 跑 collect_usage.py  → 產生這台電腦的 data/usage/usage-<機器>.json
#   2) 跑 render_readme.py   → 更新「專案根目錄」的 README.md 使用量卡片
#   3) git add / commit / push(只動這個 repo;失敗會自動重試)
#
# 用法:可從任何目錄執行
#     /路徑/tools/claude-usage-profile/push_usage.sh
#
# 前置:這台電腦已經 git clone 你的 profile repo,且已設好可以 push 的認證。

set -euo pipefail

# 腳本所在目錄(絕對路徑),以及它所屬的 git repo 根目錄
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)"

PY="$(command -v python3 || command -v python || true)"
if [ -z "$PY" ]; then
  echo "❌ 找不到 python3,請先安裝 Python 3.8+。" >&2
  exit 1
fi

echo "▶ 收集本機使用量…"
"$PY" "$SCRIPT_DIR/collect_usage.py"

echo "▶ 更新 README 卡片(專案根目錄)…"
"$PY" "$SCRIPT_DIR/render_readme.py" --readme "$REPO_ROOT/README.md"

# 之後的 git 操作都在 repo 根目錄進行
cd "$REPO_ROOT"

# 使用量資料夾:支援「保留 tools/ 結構」或「直接放根目錄」兩種放法
if [ -d "tools/claude-usage-profile/data/usage" ]; then
  USAGE_DIR="tools/claude-usage-profile/data/usage"
else
  USAGE_DIR="data/usage"
fi

# 只有真的有變更才 commit
if git diff --quiet -- README.md "$USAGE_DIR" 2>/dev/null; then
  echo "ℹ️ 使用量沒有變化,不需要推送。"
  exit 0
fi

echo "▶ 提交並推送…"
git add README.md "$USAGE_DIR"
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
