"""Render Map Room clips for a series, format 2. Usage:
  render_series.py <series folder> <work dir> <out dir> [--days 11,12] [--samples N] [--stills t1,t2] [--force]
Steps: check the whole series (nothing renders if any day has an error); for each day compile it, draw the focus map,
render the close table's plate, block and rake sprites (cached in the work dir by focus), then composite the zoom clip.
A day without moves (a quiet day) gets a balcony only clip: the line is redrawn and the camera never comes down to the table."""
import os, sys, json, argparse, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import series as S
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('series'); ap.add_argument('work'); ap.add_argument('out')
    ap.add_argument('--days'); ap.add_argument('--samples', type=int, default=128); ap.add_argument('--stills'); ap.add_argument('--force', action='store_true')
    a = ap.parse_args(); work = os.path.abspath(a.work); os.makedirs(a.out, exist_ok=True)
    r = subprocess.run([sys.executable, os.path.join(HERE, 'check_series.py'), a.series]); test = os.sep + 'test' + os.sep in os.path.abspath(a.series) + os.sep
    if r.returncode and not (a.force and test): raise SystemExit('the series fails the check; fix it first')
    s = S.Series(a.series); want = [int(x) for x in a.days.split(',')] if a.days else None
    import draw_map, zoomclip
    for i, d in enumerate(s.days):
        if want and d['n'] not in want: continue
        res = s.compile(i, work); name = os.path.splitext(os.path.basename(d['file']))[0]
        vdir = os.path.join(work, 'views', res['vname']); os.makedirs(vdir, exist_ok=True); mapimg = os.path.join(vdir, 'map.png')
        if not os.path.exists(mapimg): draw_map.draw(s.campaign, 'main', mapimg, res['table'])
        env = {**os.environ, 'MAPROOM_TABLE': res['table'], 'MAPROOM_VNAME': res['vname'], 'MAPROOM_MAPIMG': mapimg, 'MAPROOM_STAMP': 'TEST' if test else ''}
        rr = subprocess.run([sys.executable, os.path.join(HERE, 'render_day.py'), res['close'], work, os.path.join(a.out, name + '.mp4'),
                             '--assets-only', '--no-check', '--samples', str(a.samples)], env=env, capture_output=True, text=True)
        if rr.returncode: print(rr.stdout[-1500:], rr.stderr[-1500:]); raise SystemExit(f'{name}: table render failed')
        zc = zoomclip.ZoomClip(s, res, work); out = os.path.join(a.out, name + '.mp4')
        if a.stills:
            for t in [float(x) for x in a.stills.split(',')]: zoomclip.still(zc, t, f'{os.path.splitext(out)[0]}-{t:05.2f}.png')
        else: zoomclip.write(zc, out)
if __name__ == '__main__': main()
