# 安裝說明 — 在 GitHub 首頁顯示你的 AI 使用量

這套工具會把你**每台電腦**的 AI CLI 使用量,自動彙總成一張卡片,
顯示在你的 GitHub 個人首頁(像 GitHub 統計卡那樣)。

**支援的來源:**
- 🟣 **Claude Code**(`~/.claude`)— 自動,無需設定
- 🟢 **OpenAI Codex CLI**(`~/.codex`)— 自動,無需設定
- 🔵 **Gemini CLI**(`~/.gemini`)— 需先開啟 local telemetry(見二之 4)

> 🔐 **隱私**:腳本只取「數字」(token 數、model 名稱、日期),
> **不會**讀取或上傳你的對話內容、檔案路徑或專案名稱。
>
> ℹ️ 純網頁/App 版(ChatGPT、Claude.ai、Gemini 網頁)官方**不提供**個人逐 token
> 用量、也沒有本機紀錄,所以無法統計 — 只有「命令列工具」的用量收得到。

---

## 一、只做一次的事(在 GitHub 網頁)

### 1. 建立你的 Profile repo
- 到 https://github.com/new
- **Repository name** 填你的帳號名稱:**`ChiaChe726`**(一定要一模一樣)
- 選 **Public**(公開)
- 勾選 **Add a README file**
- 按 Create repository

> GitHub 有個隱藏功能:名稱跟你帳號相同的 repo,它的 README 會顯示在你的個人首頁。

### 2. 把你的 profile 改成公開
- 你的 profile 目前是「私人」,別人看不到。
- 到 **Settings → Public profile**(或 profile 頁的提示連結),取消「private profile」。

---

## 二、每台電腦做一次

### 1. 下載這套工具
把 `tools/claude-usage-profile/` 這個資料夾裡的檔案,複製到你剛建立的
`ChiaChe726` repo。最簡單的方式:

```bash
# 在你電腦上 clone 你的 profile repo
git clone https://github.com/ChiaChe726/ChiaChe726.git
cd ChiaChe726

# 把「整個」 tools/ 資料夾複製進來(保留資料夾結構,後面的指令才對得上)
#   結果應該是:ChiaChe726/tools/claude-usage-profile/collect_usage.py ...
# 然後用 tools/claude-usage-profile/README.template.md 當作你的 README.md 起點:
cp tools/claude-usage-profile/README.template.md README.md
```

### 2. 給這台電腦取個名字(選用,但建議)
這樣多台電腦才不會互相蓋掉。打開終端機設定一個環境變數,例如:

```bash
# Mac:加到 ~/.zshrc
echo 'export CLAUDE_USAGE_MACHINE="ChiaChe-MacBook"' >> ~/.zshrc
source ~/.zshrc
```

不設也可以,預設會用電腦的主機名稱。

### 3. 跑一次試試看
最簡單的方式是直接用一鍵腳本(它會自動處理路徑、更新根目錄 README 並推送):
```bash
cd ChiaChe726          # 你的 profile repo
./tools/claude-usage-profile/push_usage.sh
```

或想分步手動跑也可以:
```bash
cd ChiaChe726
python3 tools/claude-usage-profile/collect_usage.py
python3 tools/claude-usage-profile/render_readme.py --readme README.md
git add . && git commit -m "Add Claude usage card" && git push
```
打開 https://github.com/ChiaChe726 ,卡片就出現了 🎉

### 4.(選用)想一起統計 Gemini CLI?
Claude Code 和 Codex 本來就會記錄用量,**不用做任何設定**。
但 Gemini CLI 預設不記 token,要手動開啟「本機 telemetry」。
編輯 `~/.gemini/settings.json`,加入:

```json
{
  "telemetry": {
    "enabled": true,
    "target": "local",
    "outfile": "~/.gemini/telemetry.log"
  }
}
```

之後用 Gemini CLI 時就會把用量寫進 `~/.gemini/telemetry.log`,
`collect_usage.py` 會自動讀取彙總。

> ⚠️ Gemini 的 log 是 OpenTelemetry 格式、版本間略有差異。若卡片上的 Gemini
> 數字看起來不對,把 `~/.gemini/telemetry.log` 前幾行貼出來,就能校正解析邏輯。

---

## 三、讓它「每次用完自動更新」(選用)

不想每次手動跑?設定一個 Claude Code 的 **Stop hook**,每次工作結束自動推。

編輯 `~/.claude/settings.json`,加入(把路徑換成你 repo 的實際位置):

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "cd /你的路徑/ChiaChe726 && ./tools/claude-usage-profile/push_usage.sh >/dev/null 2>&1 &"
          }
        ]
      }
    ]
  }
}
```

> 結尾的 `&` 讓它在背景跑、不拖慢你;失敗也不會影響你正在做的事。

設好之後,你每次用完 Claude Code,使用量就會自動更新到 GitHub。完全不用管。

---

## 常見問題

**Q：卡片數字沒變？**
A：先確認對應來源有資料 — Claude 看 `~/.claude/projects/`、Codex 看 `~/.codex/sessions/`
是否有 `.jsonl` 檔;Gemini 要先開 telemetry(二之 4)並確認 `~/.gemini/telemetry.log` 有內容。

**Q：我只用其中幾種 AI,可以嗎？**
A：可以。沒裝的來源會自動略過、不影響其他。例如只用 Claude + Codex,
Gemini 那塊就是 0、卡片上也不會列出來。

**Q：成本是真的花費嗎？**
A：**不是**。如果你用 Max/Pro 訂閱,是固定月費、不是按 token 計費。
卡片上的金額是「如果用 API 會花多少」的估算,只是好玩的參考。

**Q：會洩漏我的程式碼或對話嗎？**
A：不會。只上傳彙總後的數字(總共幾個 token、用哪個 model)。
