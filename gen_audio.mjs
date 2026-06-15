// 批量生成真人级发音 mp3 —— 读 data.js，调用 edge-tts
// 用法: node gen_audio.mjs            (只补缺失的)
//       node gen_audio.mjs --force    (全部重生成)
import { spawn } from "node:child_process";
import { mkdir, stat, readFile } from "node:fs/promises";
import { dirname } from "node:path";

const FORCE = process.argv.includes("--force");
const VOICES = {
  en:  "en-US-AriaNeural",
  es:  "es-ES-ElviraNeural",
  ja:  "ja-JP-NanamiNeural",
  yue: "zh-HK-HiuMaanNeural",
};
const CONCURRENCY = 8;

// 载入 data.js（伪造 window）
const src = await readFile(new URL("./data.js", import.meta.url), "utf8");
const window = {};
new Function("window", src)(window);
const DECKS = window.DECKS;

// 收集任务
const jobs = [];
for (const deck of DECKS) {
  deck.cards.forEach((card, idx) => {
    for (const lang of Object.keys(VOICES)) {
      const d = card[lang];
      if (!d || !d.text) continue;
      jobs.push({ path: `audio/${deck.id}/${idx}_${lang}.mp3`, text: d.text, voice: VOICES[lang] });
    }
  });
}

const exists = async p => { try { return (await stat(p)).size > 0; } catch { return false; } };

function synth(job) {
  return new Promise(async (resolve) => {
    if (!FORCE && await exists(job.path)) { resolve({ ...job, skipped: true }); return; }
    await mkdir(dirname(job.path), { recursive: true });
    const p = spawn("python3", ["-m", "edge_tts", "--voice", job.voice, "--text", job.text, "--write-media", job.path]);
    let err = "";
    p.stderr.on("data", d => err += d);
    p.on("close", code => resolve({ ...job, ok: code === 0, err: err.trim() }));
  });
}

// 并发池
let done = 0, failed = 0, skipped = 0;
const queue = [...jobs];
async function worker() {
  while (queue.length) {
    const r = await synth(queue.shift());
    if (r.skipped) { skipped++; }
    else if (r.ok) { done++; process.stdout.write(`✓ ${r.path}\n`); }
    else { failed++; process.stdout.write(`✗ ${r.path}  ${r.err}\n`); }
  }
}
console.log(`共 ${jobs.length} 条音频任务，并发 ${CONCURRENCY}${FORCE ? "，强制重生成" : ""}`);
await Promise.all(Array.from({ length: CONCURRENCY }, worker));
console.log(`\n完成：新生成 ${done} · 跳过(已存在) ${skipped} · 失败 ${failed}`);
