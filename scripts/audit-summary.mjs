// 用途：把 `npm audit --json` 的結果縮成一行摘要，給 security-auto-fix.yml 寫進 commit 訊息與報告。
//
// ```mermaid
// flowchart LR
//     A["npm audit --json（stdin）"] --> B[讀 metadata.vulnerabilities] --> C["critical N、high N、moderate N、low N（共 N）"]
//     A --> D[讀不到或格式不對] --> E["無法取得 npm audit 結果"]
// ```
//
// 輸入：stdin 的 npm audit JSON
// 輸出：一行繁中摘要（stdout）；永遠 exit 0，不讓摘要失敗擋住流程
// 副作用：無

let raw = "";
process.stdin.on("data", (chunk) => (raw += chunk));
process.stdin.on("end", () => {
  try {
    const v = JSON.parse(raw).metadata.vulnerabilities;
    console.log(`critical ${v.critical}、high ${v.high}、moderate ${v.moderate}、low ${v.low}（共 ${v.total}）`);
  } catch {
    console.log("無法取得 npm audit 結果");
  }
});
