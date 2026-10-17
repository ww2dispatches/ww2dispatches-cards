"""Narration for WW2 Dispatches story videos (Kokoro TTS, Apache 2.0).
Usage: python3 renderer/story_tts.py <story-id> [voice] [speed]
Reads stories/<id>.json, writes stories/audio/<id>/<voice>/<seg>.wav and dur.json.
Model files live in $KOKORO_DIR (model.onnx, voices.npz). Default voice am_onyx at 0.95 (chosen 16 Oct 2026)."""
import sys,os,json,soundfile as sf
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sid=sys.argv[1]; voice=sys.argv[2] if len(sys.argv)>2 else "am_onyx"; speed=float(sys.argv[3]) if len(sys.argv)>3 else 0.95
story=json.load(open(f"{ROOT}/stories/{sid}.json"))
from kokoro_onnx import Kokoro
kd=os.environ.get("KOKORO_DIR","/home/claude/tts")
k=Kokoro(f"{kd}/model.onnx",f"{kd}/voices.npz")
lang="en-gb" if voice.startswith("b") else "en-us"
out=f"{ROOT}/stories/audio/{sid}/{voice}"; os.makedirs(out,exist_ok=True); d={}
for s in story["segments"]:
    a,sr=k.create(s["say"],voice=voice,speed=speed,lang=lang); sf.write(f"{out}/{s['id']}.wav",a,sr); d[s["id"]]=round(len(a)/sr,3)
json.dump(d,open(f"{out}/dur.json","w"),indent=1); print(voice,round(sum(d.values()),1),"s")
