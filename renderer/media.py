#!/usr/bin/env python3
"""Videos, posters, and footage on Cloudflare R2 (served at https://media.ww2dispatches.com).

Since Nov 2026 every finished video, poster, and trimmed clip lives in the R2 bucket under the same paths
the old ww2dispatches-videos repo used (videos/dispatch-NNN-x.mp4, footage/<id>.mp4, ...). Nothing is
committed to that repo any more, and this repo still ignores .mp4 files in videos/ and footage/.

Never overwrite: a key that already holds different bytes is never replaced. A re-render goes up under the
next free name with -r2, -r3, ... before the extension (videos/dispatch-057-x-r2.mp4), and media-keys.json
(repo root, committed) maps the original path to the newest copy, so the site, the Declass catalog, and
Living Press always link the current file. Uploading identical bytes again is a no-op.

Credentials come from the environment: R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_ENDPOINT, R2_BUCKET,
R2_PUBLIC_URL. Never print them. Uploads need boto3 (pip install boto3); reading needs nothing extra.

Usage (from the repo root):
  python3 renderer/media.py put <file> [...]    upload repo-relative files (videos/..., footage/...); prints each URL
  python3 renderer/media.py get <path> [...]    make each local file match the current copy on R2 (downloads if needed)
  python3 renderer/media.py url <path> [...]    print the public URL of the current copy
  python3 renderer/media.py exists <path>       exit 0 if the current copy is reachable at the public URL
"""
import hashlib, json, mimetypes, os, re, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC = (os.environ.get("R2_PUBLIC_URL") or "https://media.ww2dispatches.com").rstrip("/")
KEYS_FILE = os.path.join(ROOT, "media-keys.json")
UA = "ww2dispatches-media/1.0"
TYPES = {".mp4": "video/mp4", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".mp3": "audio/mpeg",
         ".webm": "video/webm", ".mov": "video/quicktime", ".gif": "image/gif", ".webp": "image/webp",
         ".wav": "audio/wav", ".m4a": "audio/mp4"}


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


def key_for(path):
    """The bucket key of the newest copy of a repo-relative path."""
    path = path.lstrip("/")
    return _keys().get(path, path)


def url(path):
    """Public URL of the newest copy, e.g. url("videos/dispatch-057-instagram.mp4")."""
    return f"{PUBLIC}/{key_for(path)}"


def _remote_size(path):
    """Size in bytes of the newest copy at the public URL, or None if it is not there."""
    try:
        req = urllib.request.Request(url(path), method="HEAD", headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=20) as r:
            return int(r.headers.get("Content-Length", -1)) if r.status == 200 else None
    except Exception:
        return None


def exists(path):
    return _remote_size(path) is not None


CACHE = os.path.join(os.path.expanduser("~"), ".cache", "ww2dispatches-media")


def get(path, dest=None, cache=False):
    """Return a local copy of the newest R2 copy of a repo-relative path, downloading it if needed.
    A local file of the same size at the same path in the repo is used as it is. Otherwise the file is
    downloaded into the repo at that path, or, with cache=True, into ~/.cache/ww2dispatches-media/ so
    that files tracked in this repo (a few old posters) are never overwritten.
    Returns None when the path is not on R2."""
    size = _remote_size(path)
    if size is None:
        return None
    here = os.path.join(ROOT, path)
    if dest is None and os.path.exists(here) and os.path.getsize(here) == size:
        return here
    dest = dest or (os.path.join(CACHE, key_for(path)) if cache else here)
    if os.path.exists(dest) and os.path.getsize(dest) == size:
        return dest
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    req = urllib.request.Request(url(path), headers={"User-Agent": UA})
    tmp = dest + ".part"
    with urllib.request.urlopen(req, timeout=120) as r, open(tmp, "wb") as f:
        while chunk := r.read(1 << 20):
            f.write(chunk)
    if os.path.getsize(tmp) != size:
        os.remove(tmp)
        raise IOError(f"{path}: download was cut short")
    os.replace(tmp, dest)
    return dest


def _client():
    try:
        import boto3
    except ImportError:
        sys.exit("boto3 is missing: pip install boto3")
    from botocore.config import Config
    missing = [v for v in ("R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY", "R2_ENDPOINT", "R2_BUCKET") if not os.environ.get(v)]
    if missing:
        sys.exit("Missing environment variables: " + ", ".join(missing))
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
    if "-" in etag:  # multipart upload (files over 64 MB in the first move)
        return _multipart_etag(full, etag) == etag
    return etag == md5  # single part uploads: the ETag is the MD5


def _revision(key, n):
    stem, ext = os.path.splitext(key)
    return f"{re.sub(r'-r[0-9]+$', '', stem)}-r{n}{ext}"


def put(file):
    """Upload one repo-relative file without ever overwriting. Returns the public URL of the copy in the bucket."""
    full = os.path.join(ROOT, file) if not os.path.isabs(file) else file
    path = os.path.relpath(full, ROOT).replace(os.sep, "/")
    if not re.match(r"^(videos|footage)/", path):
        sys.exit(f"{path}: only files under videos/ or footage/ go to R2")
    ext = os.path.splitext(path)[1].lower()
    ctype = TYPES.get(ext) or mimetypes.guess_type(path)[0]
    if not ctype:
        sys.exit(f"{path}: unknown content type")
    data_md5, data_sha = hashlib.md5(), hashlib.sha256()
    with open(full, "rb") as f:
        while chunk := f.read(1 << 20):
            data_md5.update(chunk); data_sha.update(chunk)
    size, md5, sha = os.path.getsize(full), data_md5.hexdigest(), data_sha.hexdigest()

    s3 = _client()
    keys = _keys()
    # Try the original path, then -r2, -r3, ...; reuse a key that already holds these bytes. The write itself
    # is conditional (If-None-Match: *), so R2 refuses it if anything appeared under the key meanwhile.
    key, n = path, 1
    while True:
        head = _head(s3, key)
        if head is not None:
            if _same(head, full, size, md5, sha):
                print(f"already there  {PUBLIC}/{key}", file=sys.stderr)
                break
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
            print(f"uploaded       {PUBLIC}/{key}", file=sys.stderr)
            break
        n += 1
        key = _revision(path, n)
    if key != path:
        keys[path] = key
        _save_keys(keys)
    elif path in keys:  # these bytes are the original file again; point back at it
        del keys[path]
        _save_keys(keys)
    return f"{PUBLIC}/{key}"


def main(argv):
    if len(argv) < 2 or argv[0] not in ("put", "get", "url", "exists"):
        sys.exit(__doc__)
    cmd, paths = argv[0], argv[1:]
    if cmd == "put":
        for p in paths:
            print(put(p))
    elif cmd == "get":
        for p in paths:
            got = get(p)
            if not got:
                sys.exit(f"{p}: not on R2 ({url(p)})")
            print(got)
    elif cmd == "url":
        for p in paths:
            print(url(p))
    else:
        sys.exit(0 if all(exists(p) for p in paths) else 1)


if __name__ == "__main__":
    main(sys.argv[1:])
