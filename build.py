#!/usr/bin/env python3
"""Собирает страницу отчёта из исходника в самостоятельный HTML.

Исходник `source/report.html` — шаблон: заголовок, стили, разметка и скрипт.
Данные подставляются сюда из `source/report-data.json` в присваивание
`const DATA`, поэтому единственный источник правды — json, а не копия массива
внутри шаблона.

Здесь к нему добавляется то, чего в нём нет: doctype, charset, viewport, favicon
и сброс стилей. Без charset кириллица превращается в кракозябры, без viewport
телефон рисует страницу в десктопной ширине.

    python3 build.py
"""

import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
SOURCE = HERE / "source" / "report.html"
DATA = HERE / "source" / "report-data.json"
TARGET = HERE / "site" / "index.html"

# Присваивание, в которое подставляются данные. Хвост `;` остаётся в шаблоне.
DATA_RE = re.compile(r"(const DATA = )(\[.*?\])(;\n)", re.S)

EMOJI = "📗"
DESCRIPTION = "Отчёт о выполненных работах по неделям."

RESET = """
  *, *::before, *::after { box-sizing: border-box; }
  html { -webkit-text-size-adjust: 100%; }
  body { margin: 0; }
  img, svg, video { max-width: 100%; }
  button, input, select, textarea { font: inherit; color: inherit; }
"""

# Страница уходит заказчику: ставок, стоимостей и сумм в ней быть не должно.
FORBIDDEN = re.compile(r"₽|\bруб[а-я.]*\b", re.IGNORECASE)


def favicon(emoji: str) -> str:
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'>"
        f"<text y='.9em' font-size='90'>{emoji}</text></svg>"
    )
    return "data:image/svg+xml," + svg.replace("<", "%3C").replace(">", "%3E").replace("#", "%23")


def main() -> int:
    body = SOURCE.read_text(encoding="utf-8")

    try:
        data = json.loads(DATA.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"{DATA.name}: файла нет", file=sys.stderr)
        return 1
    except json.JSONDecodeError as error:
        print(f"{DATA.name}: сломан json — {error}", file=sys.stderr)
        return 1

    if not DATA_RE.search(body):
        print(f"{SOURCE.name}: не найдено присваивание `const DATA = [...];`", file=sys.stderr)
        return 1

    rendered = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    body = DATA_RE.sub(lambda m: m.group(1) + rendered + m.group(3), body, count=1)

    match = re.search(r"<title>(.*?)</title>", body)
    if not match:
        print(f"{SOURCE.name}: нет <title>", file=sys.stderr)
        return 1
    title = match.group(1)
    body = body.replace(match.group(0), "", 1).lstrip("\n")

    found = FORBIDDEN.findall(body)
    if found:
        print(f"В отчёте найдены денежные значения ({', '.join(sorted(set(found))[:5])}) — "
              f"сборка остановлена.", file=sys.stderr)
        return 1

    html = (
        '<!doctype html>\n<html lang="ru">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<meta name="robots" content="noindex, nofollow">\n'
        f'<meta name="description" content="{DESCRIPTION}">\n'
        f"<title>{title}</title>\n"
        f'<link rel="icon" href="{favicon(EMOJI)}">\n'
        f"<style>{RESET}</style>\n"
        f"</head>\n<body>\n{body}\n</body>\n</html>\n"
    )

    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(html, encoding="utf-8")
    print(
        f"{TARGET.relative_to(HERE)}: {len(html) // 1024} КБ, "
        f"соглашений {len(data)}, финансовых данных нет"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
