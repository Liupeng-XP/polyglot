# 五语对照学习系统

母语中文，对照学习 **英语 / 西班牙语 / 日语 / 粤语**。单文件 Web 应用，零构建依赖。

## 启动

```bash
cd polyglot
python3 -m http.server 4321
# 浏览器打开 http://localhost:4321   （推荐 Chrome，语音识别评分需要）
```

直接双击 `index.html` 也能用，但**跟读录音/真人音频**在 `file://` 下会被浏览器拦截，建议用上面的本地服务器。

## 功能

| 模块 | 说明 |
|---|---|
| 📖 学习 | 五语对照全展开，逐行真人发音 |
| 🃏 卡片记忆 | 中文提示→模糊遮罩→翻面，SM-2 间隔重复评分 |
| 🎤 跟读比对 | 原声 vs 录音波形对比 + 🎙 发音测评（双引擎，见下） |
| ⏰ 今日复习 | 跨卡组自动汇集到期卡片，带待复习角标 |

内容规模：100 组 / 1143 卡 / 4572 真人音频。学习进度存浏览器 localStorage。手机访问自动切换为抽屉式侧栏（点 header ☰）。

新增导航：⏰今日复习 · 📕错题本（点过「再来」的卡，按错误次数排）· 📊统计（掌握度/进度条）。

## 导出 Anki（手机离线用）

```bash
python3 export_anki.py   # 生成 polyglot.apkg（约 45 MB，含全部音频）
```

依赖 `python3 -m pip install --user genanki`。生成的 `polyglot.apkg` 直接用 AnkiMobile/AnkiDroid 导入：按主题分 100 个子牌组，每卡正面中文、背面四语+音标+真人发音。

## 发音测评（音素级）

跟读模式的「发音测评」有两档：

- **词级（默认，免配置）**：浏览器语音识别(Web Speech，推荐 Chrome)把你念的转文字，与目标算相似度。
- **音素级（Azure）**：点 header 的 ⚙ 测评，填入 Azure Speech 密钥 + 区域 → 升级为 Azure Pronunciation Assessment：总分 / 准确度 / 流利度 / 完整度，外加**逐音素 0-100 着色**（绿≥80 / 黄≥50 / 红）和漏读/错读检测。密钥存本地 localStorage，Azure 有免费额度。

## 内容（`data.js`）

一个概念 = 五语并列。注音按语言习惯：中文拼音 / 英西 IPA / 日语假名+罗马音 / 粤拼。
新增卡片直接编辑 `data.js`，再跑一次音频脚本即可。

## 真人发音（`gen_audio.mjs`）

发音优先读 `audio/<卡组id>/<序号>_<语言>.mp3`，缺失则回退浏览器 TTS。
音频用 edge-tts（微软神经网络语音）批量生成：

```bash
node gen_audio.mjs          # 只补缺失的（幂等）
node gen_audio.mjs --force  # 全部重生成
```

依赖：`python3 -m pip install --user edge-tts`（已用 `python3 -m edge_tts` 调用，无需配 PATH）。
音色见脚本 `VOICES`。要换真人录制，直接用同名 mp3 覆盖对应文件即可。

## 升级方向（未做）

- 跟读音素级打分（接 Whisper / 讯飞，替代当前识别相似度）
- 账号 + 云端进度同步、移动端
- 内容大幅扩充到日常够用规模
