// 把 workflow 产出的新词组合并进 data.js
// 用法: node merge.mjs <workflow-output-file>
import { readFileSync, writeFileSync } from "node:fs";

const outPath = process.argv[2];
const raw = readFileSync(outPath, "utf8").trim();
let parsed;
try { parsed = JSON.parse(raw); }
catch { const i = raw.indexOf("{"), j = raw.lastIndexOf("}"); parsed = JSON.parse(raw.slice(i, j + 1)); }
const newDecks = (parsed.result && parsed.result.decks) || parsed.decks;
if (!Array.isArray(newDecks) || !newDecks.length) { console.error("没有 decks"); process.exit(1); }

// 读现有 data.js，提取已有 id 防重复
const dataPath = new URL("./data.js", import.meta.url);
let src = readFileSync(dataPath, "utf8");
const win = {}; new Function("window", src)(win);
const existingIds = new Set(win.DECKS.map(d => d.id));
const toAdd = newDecks.filter(d => !existingIds.has(d.id));
const skipped = newDecks.filter(d => existingIds.has(d.id)).map(d => d.id);

// 字段完整性校验
let bad = 0;
for (const d of toAdd) for (const c of d.cards) for (const l of ["en", "es", "ja", "yue"]) {
  if (!c[l] || !c[l].text) { console.error("缺字段", d.id, c.zh, l); bad++; }
}
if (bad) { console.error(`字段缺失 ${bad} 处，中止`); process.exit(1); }

// 在最后的 `];` 前插入新 deck 字面量
const marker = "\n];";
const at = src.lastIndexOf(marker);
const insert = toAdd.map(d => "  " + JSON.stringify(d) + ",").join("\n") + "\n";
src = src.slice(0, at) + "\n" + insert + src.slice(at + 1);
writeFileSync(dataPath, src, "utf8");

// 回读校验能否解析
const win2 = {}; new Function("window", readFileSync(dataPath, "utf8"))(win2);
const total = win2.DECKS.reduce((a, d) => a + d.cards.length, 0);
console.log(`合并完成：新增 ${toAdd.length} 组 / ${toAdd.reduce((a,d)=>a+d.cards.length,0)} 张卡${skipped.length ? "，跳过已存在: " + skipped.join(",") : ""}`);
console.log(`现在共 ${win2.DECKS.length} 组 / ${total} 张卡`);
