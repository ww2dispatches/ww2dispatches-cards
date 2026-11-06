#!/usr/bin/env python3
"""Videos, posters, and footage on Cloudflare R2 (served at https://media.ww2dispatches.com).

Since 6 Nov 2026 every finished video, poster, and trimmed clip lives in the R2 bucket under the same paths the
ww2dispatches-videos repo used (videos/dispatch-NNN-x.mp4, footage/<id>.mp4, ...). This repo ignores .mp4 files
in videos/ and footage/.

Never overwrite: a key that already holds different bytes is never replaced. A re-render goes up under the next
free name with -r2, -r3, ... before the extension (videos/dispatch-057-x-r2.mp4), and media-keys.json (repo root,
committed) maps the original path to the newest copy, so the site, the Declass catalog, and Living Press always
link the current file. Uploading identical bytes again is a no-op. Commit and push media-keys.json when it changes.

The videos repo stays live as an INBOX: a claude.ai Project chat (no R2 credentials) commits a hand cut clip to
inbox/<filename> there. `sweep`, which every run calls first, uploads each inbox file to R2 as footage/<filename>
(same never overwrite rule), checks it at the public URL, then git rm's it from inbox/ and pushes. It also uploads
anything in the videos repo's videos/ or footage/ that R2 lacks (fallback commits, Project chat renders).

FALLBACK: if any of R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_ENDPOINT, R2_BUCKET, R2_PUBLIC_URL is missing,
nothing fails silently. Every command prints a WARNING line, and `put` commits the file to the videos repo the old
way (same path, same -rN rule, never overwriting) and records its GitHub link in media-keys.json. The run's summary
must report the WARNING to Brian. The next sweep with credentials moves those files to R2.

Credentials come from the environment. Never print them. Uploads need boto3 (pip install boto3).
The videos repo is cloned (sparse: only inbox/ is checked out) to $VIDEOS_REPO_DIR, by default
../ww2dispatches-videos beside this repo.

Usage (from the repo root):
  python3 renderer/media.py sweep               start of every run: inbox to R2, catch up, check credentials
  python3 renderer/media.py put <file> [...]    upload repo-relative files (videos/..., footage/...); prints each link
  python3 renderer/media.py get <path> [...]    make each local file match the current copy (downloads if needed)
  python3 renderer/media.py url <path> [...]    print the public link of the current copy
  python3 renderer/media.py exists <path>       exit 0 if the current copy is reachable
"""
import hashlib, json, mimetypes, os, re, shutil, subprocess, sys, tempfile, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R2_VARS = ("R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY", "R2_ENDPOINT", "R2_BUCKET", "R2_PUBLIC_URL")
PUBLIC = (os.environ.get("R2_PUBLIC_URL") or "https://media.ww2dispatches.com").rstrip("/")
KEYS_FILE = os.path.join(ROOT, "media-keys.json")
# The videos repo (inbox and fallback). The two MEDIA_VIDEOS_* overrides exist only for tests.
VIDEOS_REPO_URL = os.environ.get("MEDIA_VIDEOS_REPO_URL", "https://github.com/ww2dispatches/ww2dispatches-videos")
VIDEOS_RAW = os.environ.get("MEDIA_VIDEOS_RAW", "https://raw.githubusercontent.com/ww2dispatches/ww2dispatches-videos/main/")
VIDEOS_DIR = os.environ.get("VIDEOS_REPO_DIR") or os.path.join(os.path.dirname(ROOT), "ww2dispatches-videos")
CACHE = os.path.join(os.path.expanduser("~"), ".cache", "ww2dispatches-media")
UA = "ww2dispatches-media/1.0"
TYPES = {".mp4": "video/mp4", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".mp3": "audio/mpeg",
         ".webm": "video/webm", ".mov": "video/quicktime", ".gif": "image/gif", ".webp": "image/webp",
         ".wav": "audio/wav", ".m4a": "audio/mp4"}


def log(msg):
    print(msg, file=sys.stderr, flush=True)


# ---------- credentials and the loud fallback warning ----------

def missing_r2():
    return [v for v in R2_VARS if not os.environ.get(v)]


_warned = False


def warn_fallback(missing):
    global _warned
    if _warned:
        return
    _warned = True
    bar = "!" * 100
    log(bar)
    log(f"WARNING: R2 STORAGE UNAVAILABLE, missing environment variable(s): {', '.join(missing)}.")
    log("WARNING: videos, posters, and footage are being COMMITTED TO ww2dispatches/ww2dispatches-videos the old way.")
    log("WARNING: REPORT THIS WARNING TO BRIAN IN THE RUN SUMMARY. The next run with R2 credentials moves the files to R2.")
    log(bar)


# ---------- media-keys.json: which copy of each path is current ----------

def _keys():
    try:
        with open(KEYS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def _save_keys(keys):
    with open(KEYS_FILE, "w", encoding="utf-8") as f:
        json.dump(dict(sorted(keys.items())), f, indent=1)
        f.write("\n")


def _set_key(path, value):
    """Record the current copy of a path: an R2 key, or a full GitHub link for a fallback file."""
    keys = _keys()
    if value == path:
        if keys.pop(path, None) is None:
            return
    elif keys.get(path) == value:
        return
    else:
        keys[path] = value
    _save_keys(keys)
    log(f"media-keys.json updated ({path}); commit and push it")


def key_for(path):
    """The bucket key of the newest copy of a repo-relative path (or a GitHub link for a fallback file)."""
    path = path.lstrip("/")
    return _keys().get(path, path)


def url(path):
    """Public link of the newest copy, e.g. url("videos/dispatch-057-instagram.mp4")."""
    k = key_for(path)
    return k if k.startswith("http") else f"{PUBLIC}/{k}"


def _size_at(link):
    """Size in bytes at a public link, or None if it is not there."""
    try:
        req = urllib.request.Request(link, method="HEAD", headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=20) as r:
            return int(r.headers.get("Content-Length", -1)) if r.status == 200 else None
    except Exception:
        return None


def exists(path):
    return _size_at(url(path)) is not None


def get(path, dest=None, cache=False):
    """Return a local copy of the newest copy of a repo-relative path, downloading it if needed.
    A local file of the same size at the same path in the repo is used as it is. Otherwise the file is
    downloaded into the repo at that path, or, with cache=True, into ~/.cache/ww2dispatches-media/ so that
    files tracked in this repo (a few old posters) are never overwritten. If R2 lacks the path, the videos
    repo's copy is used (a fallback commit). Returns None when neither has it."""
    link, size = url(path), None
    for link in dict.fromkeys([url(path), VIDEOS_RAW + path]):  # R2 (or the recorded copy), then the videos repo
        size = _size_at(link)
        if size is not None:
            break
    if size is None:
        return None
    here = os.path.join(ROOT, path)
    if dest is None and os.path.exists(here) and os.path.getsize(here) == size:
        return here
    name = link.split("://", 1)[1].split("/", 1)[1].split("?")[0]
    dest = dest or (os.path.join(CACHE, name) if cache else here)
    if os.path.exists(dest) and os.path.getsize(dest) == size:
        return dest
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    tmp = dest + ".part"
    with urllib.request.urlopen(urllib.request.Request(link, headers={"User-Agent": UA}), timeout=120) as r, \
            open(tmp, "wb") as f:
        while chunk := r.read(1 << 20):
            f.write(chunk)
    if os.path.getsize(tmp) != size:
        os.remove(tmp)
        raise IOError(f"{path}: download was cut short")
    os.replace(tmp, dest)
    return dest


# ---------- R2 ----------

def _client():
    try:
        import boto3
    except ImportError:
        sys.exit("boto3 is missing: pip install boto3")
    from botocore.config import Config
    return boto3.client("s3", endpoint_url=os.environ["R2_ENDPOINT"], region_name="auto",
                        aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
                        aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
                        config=Config(retries={"max_attempts": 5, "mode": "standard"}))


def _head(s3, key):
    try:
        return s3.head_object(Bucket=os.environ["R2_BUCKET"], Key=key)
    except s3.exceptions.ClientError as e:
        if e.response["Error"]["Code"] in ("404", "NoSuchKey", "NotFound"):
            return None
        raise


def _multipart_etag(full, etag):
    """The ETag a multipart upload of this file would have, for the part size implied by the bucket's ETag."""
    parts = int(etag.split("-")[1])
    size = os.path.getsize(full)
    for mib in (8, 16, 5, 10, 32, 64, 100):  # common part sizes; the Nov 2026 move used 16 MiB
        chunk = mib << 20
        if -(-size // chunk) != parts:
            continue
        digests = b""
        with open(full, "rb") as f:
            while block := f.read(chunk):
                digests += hashlib.md5(block).digest()
        if f"{hashlib.md5(digests).hexdigest()}-{parts}" == etag:
            return etag
    return None


def _same(head, full, size, md5, sha):
    """True when the object in the bucket already holds these bytes."""
    if head is None or head["ContentLength"] != size:
        return False
    meta = head.get("Metadata") or {}
    if meta.get("sha256"):
        return meta["sha256"] == sha
    etag = head.get("ETag", "").strip('"')
    if "-" in etag:  # multipart upload
        return _multipart_etag(full, etag) == etag
    return etag == md5  # single part uploads: the ETag is the MD5


def _revision(key, n):
    stem, ext = os.path.splitext(key)
    return f"{re.sub(r'-r[0-9]+$', '', stem)}-r{n}{ext}"


def _content_type(path):
    ctype = TYPES.get(os.path.splitext(path)[1].lower()) or mimetypes.guess_type(path)[0]
    if not ctype:
        sys.exit(f"{path}: unknown content type")
    return ctype


def _upload(full, path):
    """Upload to R2 at path, or the next free -rN name; never overwrite. Returns the key used."""
    ctype = _content_type(path)
    data_md5, data_sha = hashlib.md5(), hashlib.sha256()
    with open(full, "rb") as f:
        while chunk := f.read(1 << 20):
            data_md5.update(chunk); data_sha.update(chunk)
    size, md5, sha = os.path.getsize(full), data_md5.hexdigest(), data_sha.hexdigest()
    s3 = _client()
    # Try the path, then -r2, -r3, ...; reuse a key that already holds these bytes. The write itself is
    # conditional (If-None-Match: *), so R2 refuses it if anything appeared under the key meanwhile.
    key, n = path, 1
    while True:
        head = _head(s3, key)
        if head is not None:
            if _same(head, full, size, md5, sha):
                log(f"already there  {PUBLIC}/{key}")
                return key
        else:
            try:
                with open(full, "rb") as f:
                    s3.put_object(Bucket=os.environ["R2_BUCKET"], Key=key, Body=f, ContentType=ctype,
                                  Metadata={"sha256": sha}, IfNoneMatch="*")
            except s3.exceptions.ClientError as e:
                if e.response["Error"]["Code"] not in ("PreconditionFailed", "412"):
                    raise
                continue  # someone else wrote this key a moment ago; look at it again
            if not _same(_head(s3, key), full, size, md5, sha):
                sys.exit(f"{key}: upload check failed")
            log(f"uploaded       {PUBLIC}/{key}")
            return key
        n += 1
        key = _revision(path, n)


# ---------- the videos repo (inbox and fallback) ----------

def _git(*args, capture=True, check=True):
    r = subprocess.run(["git", "-C", VIDEOS_DIR, *args], capture_output=capture, text=True)
    if check and r.returncode:
        raise RuntimeError(f"git {' '.join(args)} failed: {(r.stderr or '').strip()[:500]}")
    return (r.stdout or "").strip()


def _repo():
    """A current clone of the videos repo. New clones are blobless and sparse (only inbox/ checked out)."""
    if not os.path.isdir(os.path.join(VIDEOS_DIR, ".git")):
        subprocess.run(["git", "clone", "-q", "--depth", "1", "--filter=blob:none", "--no-checkout",
                        VIDEOS_REPO_URL, VIDEOS_DIR], check=True)
        _git("sparse-checkout", "set", "--no-cone", "/inbox/")
        _git("checkout", "-q")
    else:
        _git("pull", "-q", "--rebase", "origin", "HEAD")
    return VIDEOS_DIR


def _tree():
    """{path: (size, blob sha)} for every file in the videos repo, without downloading any file."""
    out = {}
    for line in _git("ls-tree", "-r", "-l", "HEAD").splitlines():
        meta, path = line.split("\t", 1)
        _, kind, sha, size = meta.split()
        if kind == "blob":
            out[path] = (int(size), sha)
    return out


def _sparse_add(path):
    if _git("config", "--get", "core.sparseCheckout", check=False) == "true":
        _git("sparse-checkout", "add", "/" + path)


def _commit_push(message):
    _git("commit", "-q", "-m", message)
    for wait in (0, 2, 4, 8, 16):
        time.sleep(wait)
        r = subprocess.run(["git", "-C", VIDEOS_DIR, "push", "-q", "origin", "HEAD"], capture_output=True, text=True)
        if r.returncode == 0:
            return
        subprocess.run(["git", "-C", VIDEOS_DIR, "pull", "-q", "--rebase", "origin", "HEAD"], capture_output=True)
    raise RuntimeError(f"push to the videos repo failed: {r.stderr.strip()[:500]}")


def _repo_name(full, path, tree):
    """The repo path to commit a file under: path or the next free -rN name, free in the repo and on R2.
    Returns (name, already_committed)."""
    sha = subprocess.run(["git", "hash-object", full], capture_output=True, text=True, check=True).stdout.strip()
    name, n = path, 1
    while True:
        if name in tree:
            if tree[name][1] == sha:
                return name, True
        elif _size_at(f"{PUBLIC}/{name}") is None:
            return name, False
        n += 1
        name = _revision(path, n)


def _fallback_put(full, path):
    """Commit a file to the videos repo the old way (never overwriting) and record its GitHub link."""
    warn_fallback(missing_r2())
    _repo()
    name, done = _repo_name(full, path, _tree())
    if not done:
        _sparse_add(name)
        dest = os.path.join(VIDEOS_DIR, name)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copyfile(full, dest)
        _git("add", "--sparse", name)
        _commit_push(f"Fallback (R2 unavailable): {name}")
        log(f"WARNING: committed {name} to ww2dispatches/ww2dispatches-videos instead of R2")
    link = VIDEOS_RAW + name
    _set_key(path, link)
    return link


def put(file, path=None):
    """Store one file without ever overwriting and return its public link. `path` is where it belongs
    (videos/... or footage/...); by default the file's own path in this repo."""
    full = file if os.path.isabs(file) else os.path.join(ROOT, file)
    path = (path or os.path.relpath(full, ROOT)).replace(os.sep, "/")
    if not re.match(r"^(videos|footage)/[^/]", path):
        sys.exit(f"{path}: only files under videos/ or footage/ are media")
    _content_type(path)
    if missing_r2():
        return _fallback_put(full, path)
    key = _upload(full, path)
    _set_key(path, key)
    return f"{PUBLIC}/{key}"


# ---------- sweep: every run calls this first ----------

def sweep():
    missing = missing_r2()
    if missing:
        warn_fallback(missing)
    _repo()
    tree = _tree()
    problems, done = [], []

    # 1. The inbox: hand cut clips from Project chats become footage/<filename>.
    inbox = sorted(p for p in tree if p.startswith("inbox/") and not os.path.basename(p).startswith((".", "README")))
    for p in inbox:
        name = os.path.basename(p)
        local = os.path.join(VIDEOS_DIR, p)
        if not os.path.exists(local):
            _sparse_add(p)
        size = os.path.getsize(local)
        if missing:
            # Fallback: footage/ in the videos repo, the old way.
            target, dup = _repo_name(local, f"footage/{name}", tree)
            if not dup:
                _sparse_add(target)
                os.makedirs(os.path.join(VIDEOS_DIR, "footage"), exist_ok=True)
                shutil.copyfile(local, os.path.join(VIDEOS_DIR, target))
                _git("add", "--sparse", target)
            _git("rm", "-q", "--sparse", p)
            _commit_push(f"Inbox (R2 unavailable): {p} -> {target}")
            _set_key(f"footage/{name}", VIDEOS_RAW + target)
            done.append(f"{p} -> {target} in the videos repo (FALLBACK)")
            tree = _tree()
            continue
        link = put(local, f"footage/{name}")
        if _size_at(link) != size:
            problems.append(f"{p}: {link} does not return the file; left in the inbox")
            continue
        _git("rm", "-q", "--sparse", p)
        _commit_push(f"Inbox: {p} moved to R2 ({link})")
        done.append(f"{p} -> {link}")
        tree = _tree()

    # 2. Catch up: anything committed to the videos repo that R2 lacks (fallback commits, Project chat renders).
    if not missing:
        s3, have = _client(), {}
        for prefix in ("videos/", "footage/"):
            for page in s3.get_paginator("list_objects_v2").paginate(Bucket=os.environ["R2_BUCKET"], Prefix=prefix):
                for o in page.get("Contents", []):
                    have[o["Key"]] = o["Size"]
        keys = _keys()
        todo = [p for p in sorted(tree) if p.startswith(("videos/", "footage/")) and os.path.splitext(p)[1].lower() in TYPES
                and have.get(p) != tree[p][0] and have.get(keys.get(p, "")) != tree[p][0]]  # not already caught up
        for p in todo:
            with tempfile.TemporaryDirectory() as td:
                tmp = os.path.join(td, os.path.basename(p))
                with open(tmp, "wb") as f:
                    subprocess.run(["git", "-C", VIDEOS_DIR, "cat-file", "blob", tree[p][1]], stdout=f, check=True)
                key = _upload(tmp, p)
                link = f"{PUBLIC}/{key}"
                if _size_at(link) != tree[p][0]:
                    problems.append(f"{p}: {link} does not return the file")
                    continue
            # Point any fallback entry for this file at R2; a changed file under an old name is a new copy.
            keys = _keys()
            for logical, value in keys.items():
                if value == VIDEOS_RAW + p:
                    _set_key(logical, key)
            if key != p:
                _set_key(p, key)
            done.append(f"caught up {p} -> {link}")

    print(f"sweep: R2 {'UNAVAILABLE (fallback, see WARNING)' if missing else 'ok'}; "
          f"{len(inbox)} inbox file(s); {len(done)} moved; {len(problems)} problem(s)")
    for line in done:
        print("  " + line)
    for line in problems:
        print("  PROBLEM: " + line)
    if missing:
        print(f"WARNING: R2 STORAGE UNAVAILABLE (missing {', '.join(missing)}). REPORT THIS TO BRIAN IN THE RUN SUMMARY.")
    return 1 if problems else 0


def main(argv):
    if not argv or argv[0] not in ("sweep", "put", "get", "url", "exists") or (argv[0] != "sweep" and len(argv) < 2):
        sys.exit(__doc__)
    cmd, paths = argv[0], argv[1:]
    if missing_r2():
        warn_fallback(missing_r2())
    if cmd == "sweep":
        sys.exit(sweep())
    if cmd == "put":
        for p in paths:
            print(put(p))
    elif cmd == "get":
        for p in paths:
            got = get(p)
            if not got:
                sys.exit(f"{p}: not on R2 or in the videos repo ({url(p)})")
            print(got)
    elif cmd == "url":
        for p in paths:
            print(url(p))
    else:
        sys.exit(0 if all(exists(p) for p in paths) else 1)


if __name__ == "__main__":
    main(sys.argv[1:])
