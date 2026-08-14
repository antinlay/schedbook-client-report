#!/usr/bin/env python3
"""Собирает страницу отчёта из исходника в самостоятельный HTML.

Исходник `source/report.html` — фрагмент: заголовок, стили, разметка и данные.
Здесь к нему добавляется то, чего в нём нет: doctype, charset, viewport, favicon
и сброс стилей. Без charset кириллица превращается в кракозябры, без viewport
телефон рисует страницу в десктопной ширине.

    python3 build.py
"""

import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
SOURCE = HERE / "source" / "report.html"
TARGET = HERE / "site" / "index.html"

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
    print(f"{TARGET.relative_to(HERE)}: {len(html) // 1024} КБ, финансовых данных нет")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
