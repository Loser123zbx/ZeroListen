import os
import numpy as np
from onnxruntime import InferenceSession

# You can generate token ids as follows:
#   1. Convert input text to phonemes using https://github.com/hexgrad/misaki
#   2. Map phonemes to ids using https://hf-mirror.com/hexgrad/Kokoro-82M/blob/785407d1adfa7ae8fbef8ffd85f34ca127da3039/config.json#L34-L148
tokens = [50, 157, 43, 135, 16, 53, 135, 46, 16, 43, 102, 16, 56, 156, 57, 135, 6, 16, 102, 62, 61, 16, 70, 56, 16, 138, 56, 156, 72, 56, 61, 85, 123, 83, 44, 83, 54, 16, 53, 65, 156, 86, 61, 62, 131, 83, 56, 4, 16, 54, 156, 43, 102, 53, 16, 156, 72, 61, 53, 102, 112, 16, 70, 56, 16, 138, 56, 44, 156, 76, 158, 123, 56, 16, 62, 131, 156, 43, 102, 54, 46, 16, 102, 48, 16, 81, 47, 102, 54, 16, 54, 156, 51, 158, 46, 16, 70, 16, 92, 156, 135, 46, 16, 54, 156, 43, 102, 48, 4, 16, 81, 47, 102, 16, 50, 156, 72, 64, 83, 56, 62, 16, 156, 51, 158, 64, 83, 56, 16, 44, 157, 102, 56, 16, 44, 156, 76, 158, 123, 56, 4]

# Context length is 512, but leave room for the pad token 0 at the start & end
assert len(tokens) <= 510, len(tokens)

# Style vector based on len(tokens), ref_s has shape (1, 256)
voices = np.fromfile('af.bin', dtype=np.float32).reshape(-1, 1, 256)
ref_s = voices[len(tokens)]

# Add the pad ids, and reshape tokens, should now have shape (1, <=512)
tokens = [[0, *tokens, 0]]

model_name = 'model.onnx' # Options: model.onnx, model_fp16.onnx, model_quantized.onnx, model_q8f16.onnx, model_uint8.onnx, model_uint8f16.onnx, model_q4.onnx, model_q4f16.onnx
sess = InferenceSession(os.path.join('', model_name))

audio = sess.run(None, dict(
    input_ids=tokens,
    style=ref_s,
    speed=np.ones(1, dtype=np.float32),
))[0]

import scipy.io.wavfile as wavfile
wavfile.write('audio.wav', 24000, audio[0])
