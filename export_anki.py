#!/usr/bin/env python3
# 把五语卡片 + 真人音频导出成 Anki .apkg
# 用法: python3 export_anki.py  ->  生成 polyglot.apkg
import json, subprocess, os, shutil, hashlib
import genanki

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)

# 1) 读 data.js -> DECKS
js = 'const fs=require("fs");const w={};new Function("window",fs.readFileSync("data.js","utf8"))(w);process.stdout.write(JSON.stringify(w.DECKS))'
DECKS = json.loads(subprocess.check_output(["node", "-e", js]))

CAT = {"daily": "日常用语", "dialogue": "场景对话", "vocab": "主题单词", "pattern": "固定句式", "grammar": "语法"}
def sid(s):  # 由字符串生成稳定 int id
    return int(hashlib.md5(s.encode()).hexdigest()[:8], 16)

MODEL = genanki.Model(
    sid("polyglot-model-v1"), "五语对照卡",
    fields=[{"name": n} for n in
        ["zh","py","en","en_ipa","es","es_ipa","ja","ja_kana","ja_romaji","yue","yue_jp","a_en","a_es","a_ja","a_yue"]],
    templates=[{
        "name": "中→四语",
        "qfmt": '<div class="zh">{{zh}}</div><div class="py">{{py}}</div>',
        "afmt": '{{FrontSide}}<hr>'
            '<div class="lang"><span class="tag en">英</span><b>{{en}}</b><span class="ph">{{en_ipa}}</span>{{a_en}}</div>'
            '<div class="lang"><span class="tag es">西</span><b>{{es}}</b><span class="ph">{{es_ipa}}</span>{{a_es}}</div>'
            '<div class="lang"><span class="tag ja">日</span><b>{{ja}}</b><span class="ph">{{ja_kana}} · {{ja_romaji}}</span>{{a_ja}}</div>'
            '<div class="lang"><span class="tag yue">粤</span><b>{{yue}}</b><span class="ph">{{yue_jp}}</span>{{a_yue}}</div>',
    }],
    css="""
.card{font-family:-apple-system,"PingFang SC",sans-serif;font-size:20px;text-align:center;color:#e8ebf0;background:#15171c}
.zh{font-size:38px;font-weight:700;color:#ffd166}
.py{font-size:16px;color:#9aa3b2;margin-top:2px}
hr{border:none;border-top:1px solid #2a2f3a;margin:16px 0}
.lang{display:flex;align-items:center;gap:10px;flex-wrap:wrap;justify-content:center;background:#20242e;border-radius:10px;padding:10px 12px;margin:8px 0}
.lang b{font-size:22px}
.tag{font-size:12px;font-weight:700;color:#11141a;border-radius:6px;padding:2px 8px}
.tag.en{background:#6fb1ff}.tag.es{background:#ff9b54}.tag.ja{background:#ff7eb6}.tag.yue{background:#7ee0c0}
.ph{font-size:13px;color:#9aa3b2}
""")

MEDIA_DIR = os.path.join(HERE, "._apkg_media")
shutil.rmtree(MEDIA_DIR, ignore_errors=True)
os.makedirs(MEDIA_DIR)
media_files = []

def audio_field(deck_id, idx, lang):
    src = os.path.join(HERE, "audio", deck_id, f"{idx}_{lang}.mp3")
    if not os.path.exists(src):
        return ""
    name = f"poly_{deck_id}_{idx}_{lang}.mp3"
    dst = os.path.join(MEDIA_DIR, name)
    shutil.copyfile(src, dst)
    media_files.append(dst)
    return f"[sound:{name}]"

anki_decks = []
total = 0
for d in DECKS:
    deck = genanki.Deck(sid("polyglot::" + d["id"]),
                        f"五语对照::{CAT.get(d['cat'], d['cat'])}::{d['title']}")
    for i, c in enumerate(d["cards"]):
        ja = c["ja"]; yue = c["yue"]
        note = genanki.Note(model=MODEL, guid=genanki.guid_for("poly", d["id"], i), fields=[
            c["zh"], c["py"],
            c["en"]["text"], c["en"].get("ipa", ""),
            c["es"]["text"], c["es"].get("ipa", ""),
            ja["text"], ja.get("kana", ""), ja.get("romaji", ""),
            yue["text"], yue.get("jp", ""),
            audio_field(d["id"], i, "en"), audio_field(d["id"], i, "es"),
            audio_field(d["id"], i, "ja"), audio_field(d["id"], i, "yue"),
        ])
        deck.add_note(note); total += 1
    anki_decks.append(deck)

pkg = genanki.Package(anki_decks)
pkg.media_files = media_files
out = os.path.join(HERE, "polyglot.apkg")
pkg.write_to_file(out)
shutil.rmtree(MEDIA_DIR, ignore_errors=True)
mb = os.path.getsize(out) / 1024 / 1024
print(f"导出完成: {out}")
print(f"{len(anki_decks)} 个子牌组 · {total} 张卡 · {len(media_files)} 条音频 · {mb:.1f} MB")
