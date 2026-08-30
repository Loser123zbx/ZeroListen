import { KokoroTTS } from "kokoro-js";
import { env } from "@huggingface/transformers";

// huggingface.co is unreachable from this network (connect timeout).
// Route all model downloads through the hf-mirror.com mirror instead.
env.remoteHost = "https://hf-mirror.com/";

const model_id = "onnx-community/Kokoro-82M-ONNX";
const tts = await KokoroTTS.from_pretrained(model_id, {
  dtype: "fp32", // Options: "fp32", "fp16", "q8", "q4", "q4f16"
});

const text = "Take a breath, now. Take another. Feel air in your lungs. Let your limbs return. Yes, move your fingers. Have a body again, under gravity, in air. Respawn in the long dream. There you are. Your body touching the universe again at every point, as though you were separate things. As though we were separate things.";
const audio = await tts.generate(text, {
  // Use `tts.list_voices()` to list all available voices
  voice: "af_jessica",
  speed:"0.7"
});
audio.save("audio.wav");
