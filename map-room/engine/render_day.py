"""Render one day's Map Room clip, start to finish.
Usage: render_day.py <day.json> <work dir> <out.mp4> [--samples N] [--photo still.jpg] [--stills t1,t2] [--silent]
Steps: check the record; make missing faces, plates, block and rake sprites (cached in the work dir, so later days reuse
them); draw the overlays; composite; build sound C from the day's events; join them.
Maps: map-room/series/<campaign>/maps/<view>.png once traced (step 4); until then a watermarked placeholder."""
import json, os, sys, subprocess, argparse, hashlib
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import day as D

def run(cmd, env=None):
    r = subprocess.run(cmd, env={**os.environ, **(env or {})}, capture_output=True, text=True)
    if r.returncode: print(r.stdout[-2000:], r.stderr[-2000:]); raise SystemExit(f'failed: {" ".join(cmd[:3])}')
def scene(mode, spec, out, samples, mapimg):
    if os.path.exists(out): return
    os.makedirs(os.path.dirname(out), exist_ok=True)
    run([sys.executable, os.path.join(HERE, 'scene.py'), mode, json.dumps(spec), '1080', '1920', str(samples), out], {'MAPROOM_MAP': mapimg})
    print('rendered', os.path.relpath(out))

def view_assets(d, table, vname, work, samples):
    vdir = os.path.join(work, 'views', vname); os.makedirs(vdir, exist_ok=True)
    traced = os.environ.get('MAPROOM_MAPIMG') or os.path.join(HERE, '..', 'series', str(d.rec.get('campaign')), 'maps', f'{vname}.png')
    mapimg = traced if os.path.exists(traced) else os.path.join(vdir, 'map-placeholder.png')
    if mapimg.endswith('placeholder.png') and not os.path.exists(mapimg):
        run([sys.executable, os.path.join(HERE, 'placeholder_map.py'), table.path, mapimg])
    # a new map means new plates: the cache key carries the map's fingerprint
    fp = hashlib.md5(open(mapimg, 'rb').read()).hexdigest()[:8]; stamp = os.path.join(vdir, 'map.fp')
    if os.path.exists(stamp) and open(stamp).read() != fp:
        for f in ('plate.png', 'platepad.png'): os.path.exists(os.path.join(vdir, f)) and os.remove(os.path.join(vdir, f))
    open(stamp, 'w').write(fp)
    scene('plate', {}, os.path.join(vdir, 'plate.png'), samples, mapimg)
    scene('platepad', {}, os.path.join(vdir, 'platepad.png'), samples, mapimg)
    return vdir, mapimg

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('day'); ap.add_argument('work'); ap.add_argument('out')
    ap.add_argument('--samples', type=int, default=128); ap.add_argument('--photo'); ap.add_argument('--stills'); ap.add_argument('--silent', action='store_true'); ap.add_argument('--assets-only', action='store_true'); ap.add_argument('--no-check', action='store_true')
    a = ap.parse_args(); work = os.path.abspath(a.work); os.makedirs(work, exist_ok=True)
    r = subprocess.run([sys.executable, os.path.join(HERE, 'check_record.py'), a.day], capture_output=True, text=True)
    if a.no_check: r.returncode = 0          # format 2: check_series.py has already passed the series
    else: print(r.stdout.strip())
    if r.returncode and not (os.environ.get('MAPROOM_FORCE') and '/test/' in os.path.abspath(a.day)):
        raise SystemExit('the record fails the check; fix it first')   # MAPROOM_FORCE renders a failing test record anyway
    d = D.Day(a.day); vname = os.environ.get('MAPROOM_VNAME') or d.view or 'main'
    vdir, mapimg = view_assets(d, d.table, vname, work, a.samples)
    if d.view: view_assets(d, d.main, 'main', work, a.samples)
    # faces
    fdir = os.path.join(work, 'faces'); os.makedirs(fdir, exist_ok=True)
    import faces
    for p in d.pieces:
        fp = os.path.join(fdir, f'face-{D.face_id(p)}.png')
        if not os.path.exists(fp): faces.face(p['nation'], p['type'], p['label'], fp, heavy=p.get('heavy', False), variant=p.get('variant'))
    # block sprites, one per face and table cell
    for p in d.pieces:
        c = d.anchor(p); key = f"{D.face_id(p)}_{c[0]:+.1f}_{c[1]:+.1f}"
        spec = {'face': os.path.join(fdir, f'face-{D.face_id(p)}.png'), 'x': c[0], 'y': c[1], 'rot': D.rot_deg(p['id'])}
        scene('block', spec, os.path.join(vdir, 'sprites', f'blk-{key}.png'), a.samples, mapimg)
        scene('mask', spec, os.path.join(vdir, 'sprites', f'msk-{key}.png'), a.samples, mapimg)
    # rake sprites, one per angle used
    import clip
    ra = clip.rake_anchor()
    for ang in d.rake_angles():
        spec = {'angle': ang, 'x': ra[0], 'y': ra[1]}
        if not os.path.exists(os.path.join(vdir, 'rake', f"rake-{ang}.png")):
            scene('rake', spec, os.path.join(vdir, 'rake', f"rake-{ang}.png"), a.samples, mapimg)
            scene('rakemask', spec, os.path.join(vdir, 'rake', f"rmsk-{ang}.png"), a.samples, mapimg)
    # overlays
    ov = os.path.join(work, 'ov', os.path.splitext(os.path.basename(a.day))[0])
    cmd = [sys.executable, os.path.join(HERE, 'ov_shoot.py'), a.day, ov] + ([a.photo] if a.photo else [])
    run(cmd, {'MAPROOM_STAMP': os.environ.get('MAPROOM_STAMP', 'TEST' if d.test or 'map-placeholder' in mapimg else '')})
    if a.assets_only: print('assets done'); return
    # composite
    out = os.path.abspath(a.out)
    if a.stills: run([sys.executable, os.path.join(HERE, 'clip.py'), a.day, work, out, a.stills]); print('stills done'); return
    silent = out + '.silent.mp4'; run([sys.executable, os.path.join(HERE, 'clip.py'), a.day, work, silent])
    if a.silent: os.replace(silent, out); print('OK', out); return
    import maproom_sound as snd
    wav = out + '.wav'; snd.build(d.events, d.T, wav, seed=d.rec['day'])
    run(['ffmpeg', '-v', 'error', '-y', '-i', silent, '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', out])
    os.remove(silent); os.remove(wav); print('OK', out, f'{d.T:.1f} s')
if __name__ == '__main__': main()
