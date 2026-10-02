import os, re, requests

CSS_DIR = "frontend/mirrored_site/camtech.edu.kh"
BASE_URL = "https://camtech.edu.kh"

for root, _, files in os.walk(CSS_DIR):
    for f in files:
        if not f.endswith(".css"):
            continue
        path = os.path.join(root, f)
        text = open(path, encoding="utf-8", errors="ignore").read()
        for match in re.findall(
            r'url\(["\']?([^"\')]+\.(?:woff2?|ttf|eot|svg))[^)]*\)', text
        ):
            if match.startswith("http") or match.startswith("data:"):
                continue  # already absolute or data URI
            local_path = os.path.normpath(os.path.join(root, match))
            if not os.path.exists(local_path):
                # Ensure correct URL path separators
                rel_path = os.path.relpath(local_path, CSS_DIR).replace("\\", "/")
                remote_url = BASE_URL + "/" + rel_path
                try:
                    r = requests.get(remote_url, timeout=10)
                    if r.status_code == 200:
                        os.makedirs(os.path.dirname(local_path), exist_ok=True)
                        open(local_path, "wb").write(r.content)
                        print("fixed:", local_path)
                except Exception as e:
                    print("still missing:", remote_url, e)
