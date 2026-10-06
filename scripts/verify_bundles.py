"""Каждая сборка из каталога скачивается и совпадает с записью: sha256 и размер. Запускается в CI после build.py."""

import hashlib
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    index = json.loads((ROOT / "site" / "pulse-plugins.json").read_text(encoding="utf-8"))
    errors = []
    for plugin in index["plugins"]:
        for version in plugin["versions"]:
            where = f"{plugin['id']} {version['version']}"
            try:
                with urllib.request.urlopen(version["url"], timeout=60) as response:   # noqa: S310 — https по проверке
                    data = response.read()
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{where}: не скачалась ({exc})")
                continue
            if hashlib.sha256(data).hexdigest() != version["sha256"]:
                errors.append(f"{where}: sha256 не совпадает")
            if version.get("size") is not None and version["size"] != len(data):
                errors.append(f"{where}: размер {len(data)}, а в каталоге {version['size']}")
    if errors:
        print("Сборки не прошли проверку:", *errors, sep="\n  ", file=sys.stderr)
        return 1
    print("Сборки проверены")
    return 0


if __name__ == "__main__":
    sys.exit(main())
