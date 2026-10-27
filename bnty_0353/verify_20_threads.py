import json, urllib.request
from pathlib import Path
threads = json.loads((Path(__file__).parent / "threads_verified.json").read_text(encoding="utf-8"))
for i, t in enumerate(threads, 1):
    req = urllib.request.Request(t["url"], headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        print(f"{i:02d}. HTTP {resp.status} | {t['url']}")
        assert resp.status == 200
print("ALL 20 THREADS VERIFIED HTTP 200 OK")
