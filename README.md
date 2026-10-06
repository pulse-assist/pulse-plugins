# Pulse — публичный каталог плагинов

Каталог плагинов «Пульса», встроенный в платформу по умолчанию:
`https://pulse-assist.github.io/pulse-plugins/pulse-plugins.json`.

Каталог — это репозиторий плагинов в формате `pulse-plugins` (format 1). Любой может держать свой репозиторий
(любой адрес, отдающий такой JSON) и добавить его в Пульс: Настройки → Плагины → «Репозитории». Сюда, в
публичный каталог, плагины попадают через MR.

## Как устроен

```
plugins/<id>.json         # один плагин — один файл; имя файла = id плагина
scripts/build.py          # проверка и сборка site/pulse-plugins.json
scripts/verify_bundles.py # каждая сборка скачивается и сверяется по sha256 и размеру
.github/workflows/        # CI: проверка на каждый MR, публикация на GitHub Pages из main
```

Запись плагина:

```jsonc
{
  "id": "itmo",                                    // как в pulse-plugin.json плагина
  "name": "my.itmo",
  "description": "Расписание ИТМО: вход через ITMO.ID, неделя по дням",
  "author": "pulse-assist",
  "license": "MIT",
  "homepage": "https://github.com/…/pulse-itmo",  // исходники
  "icon": "bi-calendar-week",                      // значок Bootstrap Icons
  "tags": ["учёба"],
  "versions": [{
    "version": "0.2.0",
    "channel": "stable",                           // stable | beta
    "pulse": ">=1.1",                              // контракт плагинов
    "url": "https://github.com/…/releases/download/v0.2.0/itmo-0.2.0.tar.gz",
    "sha256": "…", "size": 48213,
    "permissions": ["signals:create", "network"],  // как в манифесте этой версии
    "released_at": "2026-10-06",
    "changes": "Что нового — для владельца, по-русски"
  }]
}
```

## Добавить плагин или версию

1. Сборка — `tar.gz` с `pulse-plugin.json` (в корне или в единственной папке), кодом и собранным интерфейсом.
   В шаблоне плагина её собирает CI по тегу `vX.Y.Z` и прикладывает к релизу вместе с sha256.
2. MR в этот репозиторий: новый `plugins/<id>.json` или новая версия в начале `versions`.
3. CI проверит формат и скачает сборку. Ревью смотрит: исходники открыты, права в записи совпадают с манифестом
   и объяснены в README плагина, `changes` понятны владельцу.

Проверить локально: `python scripts/build.py`.

Частные плагины в публичный каталог не добавляются — держите для них свой репозиторий плагинов.
