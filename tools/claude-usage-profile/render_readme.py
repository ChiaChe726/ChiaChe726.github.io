#!/usr/bin/env python3
"""
render_readme.py — 讀取 data/usage/ 裡所有機器的彙總,加總後渲染成一張
                   「AI 使用量」卡片(含 GitHub 貢獻圖風格的每日熱力圖 SVG),
                   並替換 README.md 中 <!-- CLAUDE-USAGE:START/END --> 之間的內容。

用法:
    python3 render_readme.py            # 更新 ./README.md(+ assets/ 熱力圖)
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
SVG_REL = "assets/ai-usage-heatmap.svg"  # 相對於 README 的熱力圖路徑

# 重點色(橘),呼應個人網站
ACCENT = "FF7A45"

# ── 熱力圖配色(深色卡片 + 橘色漸層)──
HM_CARD = "#0d1117"
HM_EMPTY = "#161b22"
HM_LEVELS = ["#3a1d05", "#7a3a0a", "#c26016", "#ff7a45", "#ffae80"]  # 由少到多
HM_TEXT = "#c9d1d9"
HM_MUTED = "#8b949e"
HM_CELL = 11
HM_GAP = 3
PITCH = HM_CELL + HM_GAP
# 各來源的圓點顏色 + 顯示名(SVG 內用英文,任何瀏覽器都穩)
PROV_DOT = {
    "claude": ("Claude", "#ff7a45"),
    "codex": ("Codex", "#36c5a0"),
    "gemini": ("Gemini", "#5b8def"),
}
PROVIDER_LABEL = {
    "claude": "🟣 Claude",
    "codex": "🟢 OpenAI Codex",
    "gemini": "🔵 Gemini",
}


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


def build_heatmap_svg(by_day, total_tokens=0, sources=None, weeks=53):
    """產生 GitHub 貢獻圖風格的每日用量熱力圖 SVG(純標準庫,零依賴)。

    by_day: {'YYYY-MM-DD': tokens};sources: [(name, color, tokens), ...]。
    SVG 內文字一律用英文 / 數字,確保任何訪客的瀏覽器都不會變方塊。
    """
    today = dt.date.today()
    start = today - dt.timedelta(days=weeks * 7 - 1)
    start -= dt.timedelta(days=(start.weekday() + 1) % 7)  # 退到當週週日

    vals = [v for v in by_day.values() if v]
    mx = max(vals) if vals else 1

    def level(v):
        if not v or v <= 0:
            return 0
        r = v / mx
        return 4 if r >= 1 else 1 + min(3, int(r * 4))

    pad, left, top = 16, 30, 48
    grid_w = weeks * PITCH
    W = pad * 2 + left + grid_w
    H = top + 7 * PITCH + 40

    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif">',
        f'<rect width="{W}" height="{H}" rx="12" fill="{HM_CARD}"/>',
        f'<text x="{pad}" y="29" fill="#ff7a45" font-size="16" font-weight="700">{human(total_tokens)} tokens</text>',
    ]
    if sources:
        sx = pad + 140
        for name, color, tok in sources:
            p.append(f'<circle cx="{sx+4}" cy="25" r="4" fill="{color}"/>')
            p.append(f'<text x="{sx+12}" y="29" fill="{HM_MUTED}" font-size="11">{name} {human(tok)}</text>')
            sx += 34 + (len(name) + len(human(tok))) * 7

    gx, gy = pad + left, top
    for i, lbl in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
        p.append(f'<text x="{pad}" y="{gy + i*PITCH + HM_CELL}" fill="{HM_MUTED}" font-size="9">{lbl}</text>')

    last_month, last_label_col = None, -99
    d = start
    while d <= today:
        row = (d.weekday() + 1) % 7  # 週日=0
        col = (d - start).days // 7
        x, y = gx + col * PITCH, gy + row * PITCH
        lv = level(by_day.get(d.isoformat(), 0))
        fill = HM_EMPTY if lv == 0 else HM_LEVELS[lv]
        p.append(f'<rect x="{x}" y="{y}" width="{HM_CELL}" height="{HM_CELL}" rx="2" fill="{fill}"/>')
        if row == 0 and d.month != last_month and (col - last_label_col) >= 3:
            p.append(f'<text x="{x}" y="{gy-6}" fill="{HM_MUTED}" font-size="9">{d.strftime("%b")}</text>')
            last_month, last_label_col = d.month, col
        d += dt.timedelta(days=1)

    # 圖例(Less ▢▢▢▢▢ More)
    ly = gy + 7 * PITCH + 16
    lx = gx + grid_w - 5 * PITCH - 60
    p.append(f'<text x="{lx-30}" y="{ly+HM_CELL-1}" fill="{HM_MUTED}" font-size="9">Less</text>')
    p.append(f'<rect x="{lx}" y="{ly}" width="{HM_CELL}" height="{HM_CELL}" rx="2" fill="{HM_EMPTY}"/>')
    for i in range(5):
        p.append(f'<rect x="{lx + (i+1)*PITCH}" y="{ly}" width="{HM_CELL}" height="{HM_CELL}" rx="2" fill="{HM_LEVELS[i]}"/>')
    p.append(f'<text x="{lx + 6*PITCH + 4}" y="{ly+HM_CELL-1}" fill="{HM_MUTED}" font-size="9">More</text>')
    p.append("</svg>")
    return "\n".join(p)


def load_all():
    by_model = defaultdict(lambda: {"in": 0, "out": 0, "cw": 0, "cr": 0, "msgs": 0, "est_cost_usd": 0.0, "provider": "claude"})
    machines = []
    total_tokens = 0
    total_msgs = 0
    total_cost = 0.0
    by_day = defaultdict(int)
    for fp in sorted(glob.glob(os.path.join(HERE, "data", "usage", "usage-*.json"))):
        try:
            with open(fp, encoding="utf-8") as f:
                d = json.load(f)
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
            t["provider"] = b.get("provider", "claude")
            for k in ["in", "out", "cw", "cr", "msgs"]:
                t[k] += b.get(k, 0)
            t["est_cost_usd"] += b.get("est_cost_usd", 0.0)
        for day, tok in (d.get("by_day") or {}).items():
            by_day[day] += tok
    return by_model, machines, total_tokens, total_msgs, total_cost, by_day


def render(svg_rel=SVG_REL):
    """回傳 (卡片 markdown, 熱力圖 svg 字串)。無資料時 svg 為 None。"""
    by_model, machines, total_tokens, total_msgs, total_cost, by_day = load_all()

    if not machines:
        return (f"{START}\n\n_尚無使用量資料。請先在本機跑 `collect_usage.py`。_\n\n{END}", None)

    def mtok(b):
        return b["in"] + b["out"] + b["cw"] + b["cr"]

    badges = " ".join([
        badge("Total Tokens", human(total_tokens), ACCENT),
        badge("Messages", f"{total_msgs:,}", "1C1C1E"),
        badge("Est. API Value", f"${total_cost:,.0f}", "555555"),
    ])

    # 各 AI 來源加總 → 給熱力圖頂部的圓點
    prov = defaultdict(lambda: {"tok": 0})
    for model, b in by_model.items():
        prov[b.get("provider", "claude")]["tok"] += mtok(b)
    source_list = []
    for k, v in sorted(prov.items(), key=lambda x: -x[1]["tok"]):
        name, color = PROV_DOT.get(k, (k.title(), "#888888"))
        source_list.append((name, color, v["tok"]))

    svg = build_heatmap_svg(by_day, total_tokens, source_list)
    heatmap_img = f"![AI 每日使用量熱力圖]({svg_rel})"

    # 各模型表格(依 token 由多到少,標出來源)
    rows = []
    for model, b in sorted(by_model.items(), key=lambda x: -mtok(x[1])):
        label = PROVIDER_LABEL.get(b.get("provider", "claude"), b.get("provider", "claude"))
        short = label.split(" ", 1)[-1]
        rows.append(
            f"| `{model}` | {short} | {human(mtok(b))} | {b['msgs']:,} | ${b['est_cost_usd']:,.0f} |"
        )
    model_table = (
        "**各模型**\n\n"
        "| 模型 | 來源 | Tokens | 訊息 | 估算 API 等值 |\n"
        "|------|------|-------:|------:|------:|\n" + "\n".join(rows)
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

    updated = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    card = f"""{START}

### 🤖 My AI Usage

{badges}

{heatmap_img}

{model_table}{machine_block}

<sub>📊 由本機各 AI CLI 用量自動產生 · 熱力圖為每日 token 量 · 成本為 <b>API 等值估算</b>(訂閱制非按 token 計費)· 最後更新 {updated}</sub>

{END}"""
    return card, svg


def main():
    args = sys.argv[1:]
    card, svg = render()

    if "--print" in args:
        print(card)
        return

    readme = "README.md"
    if "--readme" in args:
        readme = args[args.index("--readme") + 1]
    readme = os.path.abspath(readme)

    # 寫熱力圖 SVG 到 README 同目錄的 assets/
    if svg:
        svg_path = os.path.join(os.path.dirname(readme), SVG_REL)
        os.makedirs(os.path.dirname(svg_path), exist_ok=True)
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"✅ 已更新熱力圖 {svg_path}")

    if not os.path.exists(readme):
        # 沒有 README 就建一個基本的
        content = f"# Hi 👋\n\n{card}\n"
        with open(readme, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ 已建立 {readme}")
        return

    with open(readme, encoding="utf-8") as f:
        text = f.read()
    if START in text and END in text:
        before = text[: text.index(START)]
        after = text[text.index(END) + len(END):]
        new = before + card + after
    else:
        # 沒有標記就附加在最後
        new = text.rstrip() + "\n\n" + card + "\n"

    if new != text:
        with open(readme, "w", encoding="utf-8") as f:
            f.write(new)
        print(f"✅ 已更新 {readme}")
    else:
        print("（無變更)")


if __name__ == "__main__":
    main()
