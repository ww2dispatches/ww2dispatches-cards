Finished videos, posters, and trimmed footage live on Cloudflare R2 at https://media.ww2dispatches.com (since 6 Nov 2026), under the same paths: videos/<file> and footage/<file>.

renderer/living.js and renderer/story.js write their output here (git ignores new .mp4 files in this folder) and upload each file to R2 through renderer/media.py, which prints the public link to give Buffer, for example https://media.ww2dispatches.com/videos/dispatch-NNN-vertical.mp4. media.py never overwrites: a re-render goes up as dispatch-NNN-vertical-r2.mp4 and so on, recorded in media-keys.json at the repo root (commit it).

Never commit videos to ww2dispatches/ww2dispatches-videos any more; it is a frozen copy from 18 Oct to 6 Nov 2026.

The .mp4 files still committed here stay until the posts already scheduled from them (20, 22 and 23 Oct 2026) have gone out; then they are removed from this repo.
