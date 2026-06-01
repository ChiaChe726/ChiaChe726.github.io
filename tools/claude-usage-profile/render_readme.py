#!/usr/bin/env python3
"""
render_readme.py — 讀取 data/usage/ 裡所有機器的彙總,加總後渲染成一張
                   「Claude Code 使用量」卡片,並替換 README.md 中
                   <!-- CLAUDE-USAGE:START --> 和 <!-- CLAUDE-USAGE:END --> 之間的內容。

用法:
    python3 render_readme.py            # 更新 ./README.md
    python3 render_readme.py --print    # 只印出卡片,不改檔案(dry-run)
    python3 render_readme.py --readme path/to/README.md
"""
import json
import glob
import os
import sys
import datetime as dt
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
START = "<!-- CLAUDE-USAGE:START -->"
END = "<!-- CLAUDE-USAGE:END -->"

# 重點色(橘),呼應個人網站
ACCENT = "FF7A45"


def human(n: float) -> str:
    n = float(n)
    for unit in ["", "K", "M", "B"]:
        if abs(n) < 1000:
            return f"{n:.0f}{unit}" if unit == "" else f"{n:.1f}{unit}"
        n /= 1000
    return f"{n:.1f}T"


def badge(label: str, value: str, color: str) -> str:
    # shields.io 的字串要 escape 空格與 dash
    def esc(s):
        return str(s).replace("_", "__").replace(" ", "_").replace("-", "--")
    return f"![{label}](https://img.shields.io/badge/{esc(label)}-{esc(value)}-{color}?style=for-the-badge)"


def load_all():
    by_model = defaultdict(lambda: {"in": 0, "out": 0, "cw": 0, "cr": 0, "msgs": 0, "est_cost_usd": 0.0})
    machines = []
    total_tokens = 0
    total_msgs = 0
    total_cost = 0.0
    by_day = defaultdict(int)
    for fp in sorted(glob.glob(os.path.join(HERE, "data", "usage", "usage-*.json"))):
        try:
            d = json.load(open(fp, encoding="utf-8"))
        except Exception:
            continue
        machines.append({
            "machine": d.get("machine", "?"),
            "tokens": d.get("total_tokens", 0),
            "cost": d.get("est_cost_usd", 0.0),
            "updated_at": d.get("updated_at", ""),
        })
        total_tokens += d.get("total_tokens", 0)
        total_msgs += d.get("total_messages", 0)
        total_cost += d.get("est_cost_usd", 0.0)
        for model, b in (d.get("by_model") or {}).items():
            t = by_model[model]
            for k in ["in", "out", "cw", "cr", "msgs"]:
                t[k] += b.get(k, 0)
            t["est_cost_usd"] += b.get("est_cost_usd", 0.0)
        for day, tok in (d.get("by_day") or {}).items():
            by_day[day] += tok
    return by_model, machines, total_tokens, total_msgs, total_cost, by_day


def render():
    by_model, machines, total_tokens, total_msgs, total_cost, by_day = load_all()

    if not machines:
        return (
            f"{START}\n\n_尚無使用量資料。請先在本機跑 `collect_usage.py`。_\n\n{END}"
        )

    # 徽章
    badges = " ".join([
        badge("Total Tokens", human(total_tokens), ACCENT),
        badge("Messages", f"{total_msgs:,}", "1C1C1E"),
        badge("Est. API Value", f"${total_cost:,.0f}", "555555"),
    ])

    # 各 model 表格(依 token 由多到少)
    def mtok(b):
        return b["in"] + b["out"] + b["cw"] + b["cr"]
    rows = []
    for model, b in sorted(by_model.items(), key=lambda x: -mtok(x[1])):
        rows.append(
            f"| `{model}` | {human(mtok(b))} | {b['msgs']:,} | ${b['est_cost_usd']:,.0f} |"
        )
    model_table = (
        "| 模型 | Tokens | 訊息數 | 估算 API 等值 |\n"
        "|------|-------:|------:|------:|\n" + "\n".join(rows)
    )

    # 多台電腦時,列出各台
    machine_block = ""
    if len(machines) > 1:
        mrows = "\n".join(
            f"| `{m['machine']}` | {human(m['tokens'])} | ${m['cost']:,.0f} |"
            for m in sorted(machines, key=lambda x: -x["tokens"])
        )
        machine_block = (
            "\n\n**各裝置**\n\n| 裝置 | Tokens | 估算 API 等值 |\n"
            "|------|-------:|------:|\n" + mrows
        )

    # 最近 7 天活躍(小長條)
    spark = ""
    if by_day:
        days = sorted(by_day.items())[-7:]
        if days:
            mx = max(v for _, v in days) or 1
            blocks = "▁▂▃▄▅▆▇█"
            bar = "".join(blocks[min(7, int((v / mx) * 7))] for _, v in days)
            spark = f"\n\n**最近 7 天** `{bar}`  ({days[0][0]} → {days[-1][0]})"

    updated = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    card = f"""{START}

### 🤖 我的 Claude Code 使用量

{badges}

{model_table}{machine_block}{spark}

<sub>📊 由 Claude Code 本機用量自動產生 · 成本為 <b>API 等值估算</b>(訂閱制非按 token 計費)· 最後更新 {updated}</sub>

{END}"""
    return card


def main():
    args = sys.argv[1:]
    card = render()

    if "--print" in args:
        print(card)
        return

    readme = "README.md"
    if "--readme" in args:
        readme = args[args.index("--readme") + 1]
    readme = os.path.abspath(readme)

    if not os.path.exists(readme):
        # 沒有 README 就建一個基本的
        content = f"# Hi 👋\n\n{card}\n"
        open(readme, "w", encoding="utf-8").write(content)
        print(f"✅ 已建立 {readme}")
        return

    text = open(readme, encoding="utf-8").read()
    if START in text and END in text:
        before = text[: text.index(START)]
        after = text[text.index(END) + len(END):]
        new = before + card + after
    else:
        # 沒有標記就附加在最後
        new = text.rstrip() + "\n\n" + card + "\n"

    if new != text:
        open(readme, "w", encoding="utf-8").write(new)
        print(f"✅ 已更新 {readme}")
    else:
        print("（無變更)")


if __name__ == "__main__":
    main()
