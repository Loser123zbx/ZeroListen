// ZeroListen 本地 TTS 批处理引擎
// 用法: node tts_cli.js <manifest.json>
//
// manifest.json 结构:
// {
//   "model_id": "onnx-community/Kokoro-82M-ONNX",
//   "dtype": "fp32",            // fp32 | fp16 | q8 | q4 | q4f16
//   "output_dir": "C:/.../audio",
//   "items": [
//     { "filename": "0001.wav", "text": "hello", "voice": "af_heart", "speed": 1.0 }
//   ]
// }
//
// 该脚本把 kokoro-js 生成的 32 位浮点音频转成 16 位 PCM WAV,
// 这样浏览器里的 <audio> 标签就能直接播放。
// 进度通过 stdout 输出 "PROGRESS i/n", 完成输出 "DONE", 错误输出 "ERROR ..."。

import { KokoroTTS } from "kokoro-js";
import { env } from "@huggingface/transformers";
import fs from "fs";
import path from "path";

// huggingface.co 在此网络不可达, 走 hf-mirror.com 镜像。
env.remoteHost = process.env.HF_ENDPOINT || "https://hf-mirror.com/";

function fail(msg) {
  console.error("ERROR " + msg);
  process.exit(1);
}

function floatToWav16(samples, rate) {
  const n = samples.length;
  const buf = Buffer.alloc(44 + n * 2);
  buf.write("RIFF", 0, "ascii");
  buf.writeUInt32LE(36 + n * 2, 4);
  buf.write("WAVE", 8, "ascii");
  buf.write("fmt ", 12, "ascii");
  buf.writeUInt32LE(16, 16);          // fmt chunk size
  buf.writeUInt16LE(1, 20);           // PCM (linear)
  buf.writeUInt16LE(1, 22);           // mono
  buf.writeUInt32LE(rate, 24);        // sample rate
  buf.writeUInt32LE(rate * 2, 28);    // byte rate
  buf.writeUInt16LE(2, 32);           // block align
  buf.writeUInt16LE(16, 34);          // bits per sample
  buf.write("data", 36, "ascii");
  buf.writeUInt32LE(n * 2, 40);
  let offset = 44;
  for (let i = 0; i < n; i++, offset += 2) {
    let s = samples[i];
    if (s > 1) s = 1;
    else if (s < -1) s = -1;
    buf.writeInt16LE(s < 0 ? s * 0x8000 : s * 0x7fff, offset);
  }
  return buf;
}

async function main() {
  const manifestPath = process.argv[2];
  if (!manifestPath) fail("缺少 manifest.json 参数");

  let manifest;
  try {
    let raw = fs.readFileSync(manifestPath, "utf8");
    if (raw.charCodeAt(0) === 0xfeff) raw = raw.slice(1); // 去掉 UTF-8 BOM
    manifest = JSON.parse(raw);
  } catch (e) {
    fail("无法读取 manifest: " + e.message);
  }

  const items = Array.isArray(manifest.items) ? manifest.items : [];
  const outputDir = manifest.output_dir;
  const modelId = manifest.model_id || "onnx-community/Kokoro-82M-ONNX";
  const dtype = manifest.dtype || "fp32";

  if (!outputDir) fail("manifest 缺少 output_dir");
  fs.mkdirSync(outputDir, { recursive: true });

  console.error("[tts] 正在加载模型 " + modelId + " (dtype=" + dtype + ")");
  let tts;
  try {
    tts = await KokoroTTS.from_pretrained(modelId, {
      dtype,
      progress_callback: (p) => {
        if (p && p.status) {
          const loaded = p.loaded != null ? p.loaded : 0;
          const total = p.total != null ? p.total : 0;
          const pct = total > 0 ? Math.round((loaded / total) * 100) : 0;
          console.error(`[tts] ${p.status} ${p.file || ""} ${pct}%`);
        }
      },
    });
  } catch (e) {
    fail("模型加载失败: " + (e && e.message ? e.message : e));
  }

  const total = items.length;
  for (let i = 0; i < total; i++) {
    const item = items[i];
    const text = String(item.text || "").trim();
    if (!text) {
      console.log(`PROGRESS ${i + 1}/${total}`);
      continue;
    }
    try {
      const audio = await tts.generate(text, {
        voice: item.voice || "af_heart",
        speed: typeof item.speed === "number" ? item.speed : 1.0,
      });
      const wav = floatToWav16(audio.audio, audio.sampling_rate || 24000);
      const outPath = path.join(outputDir, item.filename);
      fs.writeFileSync(outPath, wav);
    } catch (e) {
      console.error(`[tts] 第 ${i + 1} 项生成失败: ${text} -> ${e && e.message ? e.message : e}`);
    }
    console.log(`PROGRESS ${i + 1}/${total}`);
  }

  console.log("DONE");
}

main().catch((e) => fail(e && e.message ? e.message : String(e)));
