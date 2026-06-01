#!/usr/bin/env python3
"""
collect_usage.py — 掃描本機 Claude Code 的用量紀錄,彙總成一個 JSON 檔。

隱私:這個腳本「只取數字」(token 數、model 名稱、訊息數、日期),
      絕對不會讀取或外流你的對話內容、檔案路徑或專案名稱。

用法:
    python3 collect_usage.py
    # 會在 data/usage/usage-<機器代號>.json 產生這台電腦的彙總

機器代號預設用主機名(hostname),可用環境變數覆寫:
    CLAUDE_USAGE_MACHINE="我的MacBook" python3 collect_usage.py
"""
import json
import glob
import os
import re
import socket
import datetime as dt
from collections import defaultdict

# ── Claude Code 用量紀錄的位置(會掃描這幾個) ──
SEARCH_GLOBS = [
    os.path.expanduser("~/.claude/projects/**/*.jsonl"),
    # macOS 的 Xcode Claude 整合(若有)
    os.path.expanduser(
        "~/Library/Developer/Xcode/CodingAssistant/ClaudeAgentConfig/projects/**/*.jsonl"
    ),
]

# ── API「等值」價格(USD / 每百萬 token,約 2026 價位,僅供估算) ──
# 注意:Max/Pro 訂閱制不是按 token 計費,這只是換算成 API 會花多少,當參考。
PRICES = {
    "opus":   {"in": 15.0, "out": 75.0, "cw": 18.75, "cr": 1.5},
    "sonnet": {"in": 3.0,  "out": 15.0, "cw": 3.75,  "cr": 0.3},
    "haiku":  {"in": 0.8,  "out": 4.0,  "cw": 1.0,   "cr": 0.08},
}


def price_for(model: str):
    m = (model or "").lower()
    for key in PRICES:
        if key in m:
            return PRICES[key]
    return PRICES["sonnet"]  # 預設用 sonnet 價位估


def machine_id() -> str:
    name = os.environ.get("CLAUDE_USAGE_MACHINE") or socket.gethostname() or "unknown"
    # 清成適合當檔名的字串
    return re.sub(r"[^A-Za-z0-9_.-]", "-", name).strip("-") or "unknown"


def is_real_model(model: str) -> bool:
    # 過濾掉 <synthetic> 之類的非真實 model
    return bool(model) and not model.startswith("<") and "claude" in model.lower()


def main():
    by_model = defaultdict(lambda: {"in": 0, "out": 0, "cw": 0, "cr": 0, "msgs": 0})
    by_day = defaultdict(int)  # 日期 -> token 總數(供「最近活躍」用)
    files = []
    for g in SEARCH_GLOBS:
        files.extend(glob.glob(g, recursive=True))

    for fp in files:
        try:
            with open(fp, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        d = json.loads(line)
                    except Exception:
                        continue
                    if not isinstance(d, dict):
                        continue
                    if d.get("type") != "assistant":
                        continue
                    msg = d.get("message", {})
                    if not isinstance(msg, dict):
                        continue
                    u = msg.get("usage") or {}
                    model = msg.get("model", "")
                    if not u or not is_real_model(model):
                        continue
                    b = by_model[model]
                    b["in"] += u.get("input_tokens", 0) or 0
                    b["out"] += u.get("output_tokens", 0) or 0
                    b["cw"] += u.get("cache_creation_input_tokens", 0) or 0
                    b["cr"] += u.get("cache_read_input_tokens", 0) or 0
                    b["msgs"] += 1
                    # 日期(只取數字用,不含任何內容)
                    ts = d.get("timestamp")
                    if isinstance(ts, str) and len(ts) >= 10:
                        day = ts[:10]
                        tot = (
                            (u.get("input_tokens", 0) or 0)
                            + (u.get("output_tokens", 0) or 0)
                            + (u.get("cache_creation_input_tokens", 0) or 0)
                            + (u.get("cache_read_input_tokens", 0) or 0)
                        )
                        by_day[day] += tot
        except Exception:
            continue

    # 彙總
    total = {"in": 0, "out": 0, "cw": 0, "cr": 0, "msgs": 0}
    cost = 0.0
    models_out = {}
    for model, b in by_model.items():
        p = price_for(model)
        c = (
            b["in"] * p["in"]
            + b["out"] * p["out"]
            + b["cw"] * p["cw"]
            + b["cr"] * p["cr"]
        ) / 1_000_000
        cost += c
        for k in total:
            total[k] += b[k]
        models_out[model] = {**b, "est_cost_usd": round(c, 2)}

    result = {
        "machine": machine_id(),
        "updated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "files_scanned": len(files),
        "total_tokens": total["in"] + total["out"] + total["cw"] + total["cr"],
        "total_messages": total["msgs"],
        "est_cost_usd": round(cost, 2),
        "by_model": models_out,
        "by_day": dict(sorted(by_day.items())),
    }

    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "usage")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"usage-{machine_id()}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"✅ 已寫入 {out_path}")
    print(f"   機器: {result['machine']} · 掃描 {result['files_scanned']} 檔")
    print(f"   總 tokens: {result['total_tokens']:,} · 訊息: {result['total_messages']:,}")
    print(f"   估算 API 等值成本: ${result['est_cost_usd']:,.2f}")


if __name__ == "__main__":
    main()
