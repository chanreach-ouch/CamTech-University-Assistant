import os
import glob


def inject_widget():
    base_dir = "frontend/mirrored_site"
    html_files = glob.glob(os.path.join(base_dir, "**", "*.html"), recursive=True)

    injected_count = 0

    widget_code = """
<!-- CamTech Assistant Widget -->
<link rel="stylesheet" href="/widget.css">
<script src="/widget.js"></script>
"""

    for file_path in html_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            if "<!-- CamTech Assistant Widget -->" in content:
                continue  # Already injected

            # Inject right before </body>
            if "</body>" in content:
                new_content = content.replace("</body>", f"{widget_code}\n</body>")
            else:
                # If no body tag, append to end
                new_content = content + widget_code

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            injected_count += 1
        except Exception as e:
            print(f"Failed to inject into {file_path}: {e}")

    print(f"Successfully injected widget into {injected_count} HTML pages.")


if __name__ == "__main__":
    inject_widget()
