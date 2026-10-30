"""Narration for WW2 Dispatches Story Cards (Kokoro TTS, Apache 2.0).
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
# Pronunciation dictionary: words the phonemizer gets wrong, with the exact sounds to use (renderer/pron.json).
import re
PRON=json.load(open(f"{ROOT}/renderer/pron.json"))
PRON={w:v for w,v in PRON.items() if not w.startswith("_")}
from kokoro_onnx.tokenizer import Tokenizer
tok=Tokenizer()
def phon(text):
    if not PRON: return tok.phonemize(text,lang)
    pat=re.compile(r"\b("+"|".join(re.escape(w) for w in sorted(PRON,key=len,reverse=True))+r")\b")
    out=[]; last=0
    for m in pat.finditer(text):
        if text[last:m.start()].strip(): out.append(tok.phonemize(text[last:m.start()],lang))
        out.append(PRON[m.group(1)]); last=m.end()
    if text[last:].strip(): out.append(tok.phonemize(text[last:],lang))
    return re.sub(r" +([.,;:!?])",r"\1"," ".join(o.strip() for o in out))
out=f"{ROOT}/stories/audio/{sid}/{voice}"; os.makedirs(out,exist_ok=True); d={}
for s in story["segments"]:
    a,sr=k.create(phon(s["say"]),voice=voice,speed=speed,lang=lang,is_phonemes=True); sf.write(f"{out}/{s['id']}.wav",a,sr); d[s["id"]]=round(len(a)/sr,3)
json.dump(d,open(f"{out}/dur.json","w"),indent=1); print(voice,round(sum(d.values()),1),"s")
