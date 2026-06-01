# 安裝說明 — 在 GitHub 首頁顯示 Claude Code 使用量

這套工具會把你**每台電腦**的 Claude Code 使用量,自動彙總成一張卡片,
顯示在你的 GitHub 個人首頁(像 GitHub 統計卡那樣)。

> 🔐 **隱私**:腳本只取「數字」(token 數、model 名稱、日期),
> **不會**讀取或上傳你的對話內容、檔案路徑或專案名稱。

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

# 把工具檔案放進來(collect_usage.py / render_readme.py / push_usage.sh)
# 然後用 README.template.md 當作你的 README.md 起點
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
```bash
cd ChiaChe726          # 你的 profile repo
python3 tools/claude-usage-profile/collect_usage.py
python3 tools/claude-usage-profile/render_readme.py
```
打開 `README.md`,應該看到使用量卡片。沒問題就 push:
```bash
git add . && git commit -m "Add Claude usage card" && git push
```
然後打開 https://github.com/ChiaChe726 ,卡片就出現了 🎉

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
A：先確認 `~/.claude/projects/` 裡有 `.jsonl` 檔(用過 Claude Code 就會有)。

**Q：成本是真的花費嗎？**
A：**不是**。如果你用 Max/Pro 訂閱,是固定月費、不是按 token 計費。
卡片上的金額是「如果用 API 會花多少」的估算,只是好玩的參考。

**Q：會洩漏我的程式碼或對話嗎？**
A：不會。只上傳彙總後的數字(總共幾個 token、用哪個 model)。
