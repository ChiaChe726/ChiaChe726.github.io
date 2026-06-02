#!/usr/bin/env python3
"""
collect_usage.py — 掃描本機各家 AI CLI 的用量紀錄,彙總成一個 JSON 檔。

目前支援的來源:
  • Claude Code   — ~/.claude/projects/**/*.jsonl                    (穩定)
  • OpenAI Codex  — ~/.codex/sessions/**/rollout-*.jsonl             (穩定)
  • Gemini CLI    — ~/.gemini/telemetry.log(需先開啟 local telemetry) (盡力解析)

隱私:這個腳本「只取數字」(token 數、model 名稱、回合數、日期),
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

# ── 各來源用量紀錄的位置 ──
CLAUDE_GLOBS = [
    os.path.expanduser("~/.claude/projects/**/*.jsonl"),
    # macOS 的 Xcode Claude 整合(若有)
    os.path.expanduser(
        "~/Library/Developer/Xcode/CodingAssistant/ClaudeAgentConfig/projects/**/*.jsonl"
    ),
]
CODEX_GLOBS = [
    os.path.expanduser("~/.codex/sessions/**/*.jsonl"),
]
GEMINI_GLOBS = [
    os.path.expanduser("~/.gemini/telemetry.log"),
    os.path.expanduser("~/.gemini/tmp/**/otel/collector.log"),
]

# ── API「等值」價格(USD / 每百萬 token,約 2026 價位,僅供估算) ──
# 注意:訂閱制(Claude Max/Pro、ChatGPT Plus 等)不是按 token 計費,
#       這只是換算成「若走 API 會花多少」,當參考用,且各家價格會變動。
PRICES = {
    "claude": {
        "opus":    {"in": 15.0, "out": 75.0, "cw": 18.75, "cr": 1.5},
        "sonnet":  {"in": 3.0,  "out": 15.0, "cw": 3.75,  "cr": 0.3},
        "haiku":   {"in": 0.8,  "out": 4.0,  "cw": 1.0,   "cr": 0.08},
        "default": {"in": 3.0,  "out": 15.0, "cw": 3.75,  "cr": 0.3},
    },
    "codex": {  # OpenAI(in 為未命中快取的 input;cr 為 cached_input)
        "gpt-5":   {"in": 1.25, "out": 10.0, "cr": 0.125},
        "o3":      {"in": 2.0,  "out": 8.0,  "cr": 0.5},
        "o4":      {"in": 1.1,  "out": 4.4,  "cr": 0.275},
        "default": {"in": 1.25, "out": 10.0, "cr": 0.125},
    },
    "gemini": {
        "pro":     {"in": 1.25, "out": 10.0, "cr": 0.31},
        "flash":   {"in": 0.30, "out": 2.5,  "cr": 0.075},
        "default": {"in": 1.25, "out": 10.0, "cr": 0.31},
    },
}


def price_for(provider: str, model: str):
    table = PRICES.get(provider, PRICES["claude"])
    m = (model or "").lower()
    for key, p in table.items():
        if key != "default" and key in m:
            return p
    return table["default"]


def machine_id() -> str:
    name = os.environ.get("CLAUDE_USAGE_MACHINE") or socket.gethostname() or "unknown"
    # 清成適合當檔名的字串
    return re.sub(r"[^A-Za-z0-9_.-]", "-", name).strip("-") or "unknown"


def new_bucket():
    return {"in": 0, "out": 0, "cw": 0, "cr": 0, "msgs": 0, "provider": "claude"}


def _files(globs):
    out = []
    for g in globs:
        out.extend(glob.glob(g, recursive=True))
    return out


def _add_day(by_day, ts, tokens):
    if isinstance(ts, str) and len(ts) >= 10 and tokens:
        by_day[ts[:10]] += tokens


def _find_model(obj):
    """在任意巢狀 dict/list 裡找第一個看起來像 model 名稱的字串。"""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "model" and isinstance(v, str) and v:
                return v
            if isinstance(v, (dict, list)):
                r = _find_model(v)
                if r:
                    return r
    elif isinstance(obj, list):
        for v in obj:
            if isinstance(v, (dict, list)):
                r = _find_model(v)
                if r:
                    return r
    return None


# ─────────────────────────── Claude Code ───────────────────────────
def collect_claude(by_model, by_day):
    files = _files(CLAUDE_GLOBS)
    for fp in files:
        try:
            with open(fp, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        d = json.loads(line)
                    except Exception:
                        continue
                    if not isinstance(d, dict) or d.get("type") != "assistant":
                        continue
                    msg = d.get("message", {})
                    if not isinstance(msg, dict):
                        continue
                    u = msg.get("usage") or {}
                    model = msg.get("model", "")
                    # 過濾 <synthetic> 之類的非真實 model
                    if not u or not model or model.startswith("<") or "claude" not in model.lower():
                        continue
                    b = by_model[model]
                    b["provider"] = "claude"
                    b["in"] += u.get("input_tokens", 0) or 0
                    b["out"] += u.get("output_tokens", 0) or 0
                    b["cw"] += u.get("cache_creation_input_tokens", 0) or 0
                    b["cr"] += u.get("cache_read_input_tokens", 0) or 0
                    b["msgs"] += 1
                    tot = (
                        (u.get("input_tokens", 0) or 0)
                        + (u.get("output_tokens", 0) or 0)
                        + (u.get("cache_creation_input_tokens", 0) or 0)
                        + (u.get("cache_read_input_tokens", 0) or 0)
                    )
                    _add_day(by_day, d.get("timestamp"), tot)
        except Exception:
            continue
    return len(files)


# ─────────────────────────── OpenAI Codex ───────────────────────────
def collect_codex(by_model, by_day):
    """
    Codex 每個 session 檔案是 ~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl。
    其中 payload.type == "token_count" 的事件,info.total_token_usage 是「累計」總量,
    所以取每個檔案「最後一筆」即該 session 的總用量。model 由 turn_context 帶出。
    """
    files = _files(CODEX_GLOBS)
    for fp in files:
        last_ttu = None
        last_ts = None
        turns = 0
        model = None
        try:
            with open(fp, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        d = json.loads(line)
                    except Exception:
                        continue
                    if not isinstance(d, dict):
                        continue
                    if not model:  # 單一 session 通常單一 model,找到就不必再找
                        m = _find_model(d)
                        if m and ("gpt" in m.lower() or "codex" in m.lower() or m.lower().startswith("o")):
                            model = m
                    payload = d.get("payload")
                    if isinstance(payload, dict) and payload.get("type") == "token_count":
                        info = payload.get("info") or {}
                        ttu = info.get("total_token_usage")
                        if isinstance(ttu, dict):
                            last_ttu = ttu
                            last_ts = d.get("timestamp") or last_ts
                            turns += 1
        except Exception:
            continue

        if not last_ttu:
            continue
        model = model or "codex"
        input_tokens = last_ttu.get("input_tokens", 0) or 0
        cached = last_ttu.get("cached_input_tokens", 0) or 0
        output = last_ttu.get("output_tokens", 0) or 0
        non_cached_in = max(0, input_tokens - cached)
        b = by_model[model]
        b["provider"] = "codex"
        b["in"] += non_cached_in
        b["cr"] += cached
        b["out"] += output
        b["msgs"] += max(1, turns)
        _add_day(by_day, last_ts, input_tokens + output)
    return len(files)


# ─────────────────────────── Gemini CLI ───────────────────────────
def _otlp_points(obj, out):
    """
    從 OTLP/JSON(OpenTelemetry)結構遞迴抓出 gemini_cli.token.usage 的資料點。
    結構大致為:
      resourceMetrics[].scopeMetrics[].metrics[]{name, sum/gauge.dataPoints[]{attributes, asInt}}
    每筆回傳 (model, type, group, val);group 用 startTimeUnixNano 或 session.id,
    用來區分「不同次 CLI 執行」的累計過程。盡力容錯,抓不到就回傳空。
    """
    if isinstance(obj, dict):
        if obj.get("name") == "gemini_cli.token.usage":
            agg = obj.get("sum") or obj.get("gauge") or {}
            for dp in agg.get("dataPoints", []) or []:
                attrs = {}
                for a in dp.get("attributes", []) or []:
                    v = a.get("value", {})
                    attrs[a.get("key")] = (
                        v.get("stringValue")
                        if "stringValue" in v
                        else v.get("intValue", v.get("asInt"))
                    )
                val = dp.get("asInt", dp.get("asDouble", 0))
                try:
                    val = int(val)
                except Exception:
                    val = 0
                # 分組鍵:同一次 CLI 執行(process)的累計,startTime 相同
                group = dp.get("startTimeUnixNano") or attrs.get("session.id") or "_"
                out.append((attrs.get("model"), attrs.get("type"), group, val))
        for v in obj.values():
            if isinstance(v, (dict, list)):
                _otlp_points(v, out)
    elif isinstance(obj, list):
        for v in obj:
            if isinstance(v, (dict, list)):
                _otlp_points(v, out)


def collect_gemini(by_model, by_day):
    """
    讀 ~/.gemini/telemetry.log(需使用者先開啟 local telemetry)。
    ⚠️ Gemini 的 OTEL 輸出格式較多變,本函式盡力解析;若你的 log 解析不到,
       請貼一段樣本給我校正。抓不到時不會報錯,只是這塊為 0。
    """
    files = _files(GEMINI_GLOBS)
    points = []
    for fp in files:
        try:
            with open(fp, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception:
            continue
        # 優先整檔解析(單一 OTLP JSON);失敗再逐行(OTLP json-lines)。
        # 不可兩種都做 — 單行單一 JSON 會被解析兩次而重複計算。
        try:
            _otlp_points(json.loads(text), points)
        except Exception:
            for line in text.splitlines():
                line = line.strip()
                if not line or line[0] not in "[{":
                    continue
                try:
                    _otlp_points(json.loads(line), points)
                except Exception:
                    continue

    # gemini_cli.token.usage 是累計型 Counter:同一次執行(同 group)內取最大值(最後累計),
    # 不同次執行(不同 group)則相加 — 既不在單次內重複累加、也不漏掉其他執行回合。
    # (此塊為實驗性:OTEL temporality/格式會因版本而異,數字若不對請回報樣本校正)
    per_group = {}  # (model, type, group) -> 該次累計最大值
    for model, typ, group, val in points:
        if not val:
            continue
        key = (model or "gemini", (typ or "").lower(), group)
        per_group[key] = max(per_group.get(key, 0), val)
    agg = defaultdict(int)  # (model, type) -> 各次執行最大值之和
    for (model, t, _group), val in per_group.items():
        agg[(model, t)] += val
    for (model, t), val in agg.items():
        b = by_model[model]
        b["provider"] = "gemini"
        if t == "input":
            b["in"] += val
        elif t in ("output", "thought"):  # thinking 算進產出
            b["out"] += val
        elif t in ("cache", "cached"):
            b["cr"] += val
        elif t == "tool":
            b["out"] += val
        else:
            b["in"] += val
    return len(files)


def main():
    by_model = defaultdict(new_bucket)
    by_day = defaultdict(int)

    sources = {
        "claude": collect_claude(by_model, by_day),
        "codex": collect_codex(by_model, by_day),
        "gemini": collect_gemini(by_model, by_day),
    }

    # 彙總 + 估算成本
    total = {"in": 0, "out": 0, "cw": 0, "cr": 0, "msgs": 0}
    cost = 0.0
    models_out = {}
    for model, b in by_model.items():
        p = price_for(b["provider"], model)
        c = (
            b["in"] * p.get("in", 0)
            + b["out"] * p.get("out", 0)
            + b["cw"] * p.get("cw", 0)
            + b["cr"] * p.get("cr", 0)
        ) / 1_000_000
        cost += c
        for k in total:
            total[k] += b[k]
        models_out[model] = {**b, "est_cost_usd": round(c, 2)}

    result = {
        "machine": machine_id(),
        "updated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "sources": sources,
        "files_scanned": sum(sources.values()),
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
    print(f"   機器: {result['machine']}")
    print(
        f"   來源: Claude {sources['claude']} 檔 · "
        f"Codex {sources['codex']} 檔 · Gemini {sources['gemini']} 檔"
    )
    print(f"   總 tokens: {result['total_tokens']:,} · 訊息/回合: {result['total_messages']:,}")
    print(f"   估算 API 等值成本: ${result['est_cost_usd']:,.2f}")
    if sources["codex"] == 0 and sources["gemini"] == 0:
        print("   ℹ️ 沒掃到 Codex/Gemini 資料(沒裝、或 Gemini 還沒開 telemetry)。")


if __name__ == "__main__":
    main()
