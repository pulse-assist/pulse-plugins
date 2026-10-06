"""Проверка и сборка каталога: plugins/<id>.json → site/pulse-plugins.json (формат pulse-plugins 1).

    python scripts/build.py            # проверить и собрать в site/
    python scripts/build.py --check    # только проверить (CI на MR)

Без внешних зависимостей. Правила — те же, что у Пульса (backend/app/services/plugins/catalog.py).
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FORMAT = 1
NAME = "Pulse — публичный"
ID = re.compile(r"^[a-z][a-z0-9-]{1,39}$")
VERSION = re.compile(r"^\d+(\.\d+){0,2}([-+][0-9A-Za-z.-]+)?$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
SPEC = re.compile(r"^(>=|<=|==|>|<)?\s*(\d+(?:\.\d+)*)$")
PERMISSIONS = {"cards:read", "cards:write", "signals:create", "files", "jobs", "chat", "notify", "network"}
CHANNELS = {"stable", "beta"}


def check_plugin(path: Path) -> tuple[dict, list[str]]:
    errors: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        return {}, [f"{path.name}: не JSON ({exc})"]
    where = path.name
    pid = data.get("id")
    if not isinstance(pid, str) or not ID.match(pid):
        errors.append(f"{where}: id — латиница в нижнем регистре, цифры и «-», 2–40 символов")
    elif path.stem != pid:
        errors.append(f"{where}: имя файла должно совпадать с id ({pid}.json)")
    if not str(data.get("name", "")).strip():
        errors.append(f"{where}: нет name")
    if not str(data.get("homepage", "")).startswith("https://"):
        errors.append(f"{where}: homepage — https-ссылка на исходники плагина")
    if not str(data.get("license", "")).strip():
        errors.append(f"{where}: нет license")
    versions = data.get("versions")
    if not isinstance(versions, list) or not versions:
        errors.append(f"{where}: нет versions")
        versions = []
    seen = set()
    for n, v in enumerate(versions):
        at = f"{where}: versions[{n}]"
        if not isinstance(v, dict):
            errors.append(f"{at}: ожидается объект")
            continue
        version = v.get("version")
        if not isinstance(version, str) or not VERSION.match(version):
            errors.append(f"{at}: version — semver")
        elif version in seen:
            errors.append(f"{at}: версия {version} повторяется")
        seen.add(version)
        if v.get("channel", "stable") not in CHANNELS:
            errors.append(f"{at}: channel — stable или beta")
        if not all(SPEC.match(part.strip()) for part in str(v.get("pulse", ">=1.0")).split(",") if part.strip()):
            errors.append(f"{at}: pulse — условие версии, например >=1.1")
        if not str(v.get("url", "")).startswith("https://"):
            errors.append(f"{at}: url — https-ссылка на сборку tar.gz")
        if not isinstance(v.get("sha256"), str) or not SHA256.match(v["sha256"]):
            errors.append(f"{at}: sha256 — 64 шестнадцатеричных символа в нижнем регистре")
        unknown = set(v.get("permissions") or []) - PERMISSIONS
        if unknown:
            errors.append(f"{at}: неизвестные права: {', '.join(sorted(unknown))}")
    return data, errors


def main() -> int:
    files = sorted((ROOT / "plugins").glob("*.json"))
    plugins, errors = [], []
    for path in files:
        data, problems = check_plugin(path)
        errors += problems
        if not problems:
            plugins.append(data)
    if errors:
        print("Каталог не прошёл проверку:", *errors, sep="\n  ", file=sys.stderr)
        return 1
    print(f"Плагинов: {len(plugins)} — проверка пройдена")
    if "--check" in sys.argv:
        return 0
    site = ROOT / "site"
    site.mkdir(exist_ok=True)
    index = {"format": FORMAT, "name": NAME, "plugins": plugins}
    (site / "pulse-plugins.json").write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    (site / "index.html").write_text(
        "<!doctype html><meta charset=utf-8><title>Pulse — каталог плагинов</title>"
        "<p>Каталог плагинов «Пульса»: <a href=pulse-plugins.json>pulse-plugins.json</a>. "
        "Добавить плагин — MR в <a href=https://github.com/pulse-assist/pulse-plugins>pulse-assist/pulse-plugins</a>.</p>\n",
        encoding="utf-8")
    print(f"Собрано: {site / 'pulse-plugins.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
