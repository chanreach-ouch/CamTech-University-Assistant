import os
import requests
from urllib.parse import urlparse


def mirror_pages():
    urls = [
        "https://camtech.edu.kh/",
        "https://camtech.edu.kh/about-us/",
        "https://camtech.edu.kh/admissions/",
        "https://camtech.edu.kh/faculties/",
        "https://camtech.edu.kh/research-innovation/",
        "https://camtech.edu.kh/collaboration/",
    ]

    base_dir = "frontend/mirrored_site/camtech.edu.kh"
    os.makedirs(base_dir, exist_ok=True)

    headers = {"User-Agent": "Mozilla/5.0 (student research project)"}

    for url in urls:
        print(f"Mirroring {url}...")
        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                parsed = urlparse(url)
                path = parsed.path.strip("/")
                if not path:
                    file_path = os.path.join(base_dir, "index.html")
                else:
                    dir_path = os.path.join(base_dir, path)
                    os.makedirs(dir_path, exist_ok=True)
                    file_path = os.path.join(dir_path, "index.html")

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(r.text)
        except Exception as e:
            print(f"Failed to mirror {url}: {e}")

    print("Mirror complete.")


if __name__ == "__main__":
    mirror_pages()
