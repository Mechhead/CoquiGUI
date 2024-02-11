from TTS.api import TTS
import torch

input('Please enter YES when asked, hit enter to continue!')

device = "cuda" if torch.cuda.is_available() else "cpu"
TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
print('Done!')