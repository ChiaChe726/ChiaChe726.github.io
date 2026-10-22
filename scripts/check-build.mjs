// 用途：部署前檢查 Docusaurus 的 build 輸出是否完整，CI 與 CD 共用的測試點（npm test）。
//
// ```mermaid
// flowchart TD
//     A[npm run build 產生 build/] --> B[必要檔案都在?<br/>首頁、英文首頁、部落格、404、sitemap]
//     B --> C[頁面數量 ≥ 下限?]
//     C --> D[每個 HTML 都有非空的 title?]
//     D --> E[HTML 引用的站內 JS／CSS／圖片<br/>在 build/ 裡都找得到?]
//     E --> F{有任何失敗?}
//     F -- 有 --> G[列出失敗項目，exit 1<br/>CI 變紅、自動合併與部署都會停]
//     F -- 沒有 --> H[印出摘要，exit 0]
// ```
//
// 輸入：build/ 資料夾（可用第一個參數改路徑）
// 輸出：檢查摘要；有失敗時 exit code 1
// 副作用：無（只讀檔案）

import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { join, relative } from "node:path";

const BUILD = process.argv[2] ?? "build";
const REQUIRED = ["index.html", "404.html", "sitemap.xml", "blog/index.html", "en/index.html", "en/404.html"];
const MIN_PAGES = 10;
// 只檢查這幾個資料夾底下的站內資源；其他站內連結由 Docusaurus 的 onBrokenLinks: 'throw' 把關
const ASSET_PREFIXES = ["/assets/", "/img/", "/en/assets/", "/en/img/", "/obsidian-images/", "/en/obsidian-images/"];

const failures = [];
const fail = (msg) => failures.push(msg);

function walk(dir) {
  const out = [];
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) out.push(...walk(p));
    else out.push(p);
  }
  return out;
}

if (!existsSync(BUILD)) {
  console.error(`✘ 找不到 ${BUILD}/，請先跑 npm run build`);
  process.exit(1);
}

// 1. 必要檔案
for (const f of REQUIRED) {
  if (!existsSync(join(BUILD, f))) fail(`缺少必要檔案：${f}`);
}

// 2. 頁面數量
const htmlFiles = walk(BUILD).filter((p) => p.endsWith(".html"));
if (htmlFiles.length < MIN_PAGES) fail(`頁面只有 ${htmlFiles.length} 個，少於下限 ${MIN_PAGES}`);

// 3. 標題與 4. 站內資源
let assetRefs = 0;
for (const file of htmlFiles) {
  const rel = relative(BUILD, file);
  const html = readFileSync(file, "utf8");
  const title = html.match(/<title[^>]*>([^<]*)<\/title>/);
  if (!title || !title[1].trim()) fail(`沒有標題：${rel}`);
  for (const m of html.matchAll(/(?:src|href)="(\/[^"#?]*)/g)) {
    const url = m[1];
    if (!ASSET_PREFIXES.some((p) => url.startsWith(p))) continue;
    assetRefs++;
    if (!existsSync(join(BUILD, decodeURIComponent(url)))) fail(`${rel} 引用的資源不存在：${url}`);
  }
}

if (failures.length) {
  console.error(`✘ build 檢查失敗（${failures.length} 項）：`);
  for (const f of failures.slice(0, 50)) console.error(`  - ${f}`);
  process.exit(1);
}
console.log(`✔ build 檢查通過：${htmlFiles.length} 個頁面、${assetRefs} 個站內資源引用都存在、必要檔案 ${REQUIRED.length} 個都在`);
