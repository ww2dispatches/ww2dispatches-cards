"""Download a Wikimedia Commons photo (1920 px wide, a standard Wikimedia thumbnail step) for a dispatch.

Usage: python3 fetch_photo.py <commons file page URL or File: title> <output.jpg>
"""
import json
import sys
import time
import urllib.parse
import urllib.request

UA = "WW2DispatchesCards/1.0 (ww2dispatches@gmail.com)"


def get(url):
    for attempt in range(4):
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 3:
                time.sleep(10 * (attempt + 1))
                continue
            raise


def title_from(arg):
    if "/wiki/" in arg:
        arg = urllib.parse.unquote(arg.split("/wiki/", 1)[1])
    return arg if arg.startswith("File:") else "File:" + arg


def main(src, out, width=1920):
    title = title_from(src)
    api = ("https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo"
           f"&iiprop=url|size&iiurlwidth={width}&format=json&titles=" + urllib.parse.quote(title))
    info = json.loads(get(api))
    page = next(iter(info["query"]["pages"].values()))
    ii = page["imageinfo"][0]
    url = ii["url"] if ii.get("width", 0) <= width else ii.get("thumburl", ii["url"])
    # thumb.wikimedia.org is not reachable from every network; the same path works on upload.
    url = url.replace("://thumb.wikimedia.org/", "://upload.wikimedia.org/").split("?")[0]
    data = get(url)
    with open(out, "wb") as f:
        f.write(data)
    print(f"{title} -> {out} ({len(data)//1024} KB)")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
