# Документация — сборка PDF

Этот файл описывает, как подготовить окружение и собрать PDF-документы из Markdown через Pandoc + LaTeX. Диаграммы
Mermaid рендерятся заранее через `@mermaid-js/mermaid-cli`.

## Что собирается

* **Исходники**: `./docs/*.md`
* **Шаблон LaTeX**: `./docs/templates/eis.gost.tex`
* **Метаданные**: `./docs/refs.yaml`
* **Фильтры**: `./docs/filters/*` (например, `mermaid.lua`)
* **Выходные PDF**: `./docs/pdf/*.pdf`
* **Кэш Mermaid**: `./docs/static/mermaid/*`
* **Скрипт сборки**: `../scripts/build_docs.sh` (из каталога `docs` смещён на уровень выше)

## Требования

1. **Pandoc** ≥ 3.x
2. **XeLaTeX** (TeX Live / MiKTeX / MacTeX)
3. **Node.js + npm**
4. **Mermaid CLI** — обязательно:

   ```bash
   sudo npm i -g @mermaid-js/mermaid-cli
   ```

5. **Bash** (скрипт написан под POSIX shell)

### Быстрая установка

#### macOS

```bash
brew install pandoc
brew install --cask mactex-no-gui
sudo npm i -g @mermaid-js/mermaid-cli
```

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install -y pandoc texlive-full
sudo npm i -g @mermaid-js/mermaid-cli
```

#### Windows

* Установи Pandoc, MiKTeX/TeX Live, Node.js.
* Затем:

  ```powershell
  npm install -g @mermaid-js/mermaid-cli
  ```
* Запускай скрипт в Git Bash/WSL/PowerShell (пути при необходимости поправь).

## Структура каталога

```
repo-root/
├─ docs/
│  ├─ *.md
│  ├─ refs.yaml
│  ├─ templates/
│  │  └─ eis.gost.tex
│  ├─ filters/
│  │  └─ mermaid.lua
│  └─ static/
│     └─ mermaid/
└─ scripts/
   └─ build_docs.sh
```

## Как собрать

Из корня репозитория:

```bash
chmod +x scripts/build_docs.sh     # один раз
./scripts/build_docs.sh
```

Из каталога `docs/` (если скрипт ожидает относительные пути как `../docs`):

```bash
bash ../scripts/build_docs.sh
```

Скрипт:

* проверяет `pandoc`, `xelatex`, `mmdc`;
* рендерит диаграммы Mermaid в `docs/static/mermaid/`;
* вызывает `pandoc` с шаблоном `eis.gost.tex`;
* складывает PDF в `docs/pdf/`.

## Переменные окружения

* `KEEP_TEX=1` — **сохранить** промежуточные `*.tex` (по умолчанию удаляются).
* `DEBUG=1` — подробный лог `pandoc`/`xelatex`.
* `SRCDIR` — каталог исходников (по умолчанию `docs` или `../docs`).
* `OUTPDFDIR` — каталог для PDF (обычно `pdf` внутри `docs`).

Примеры:

```bash
KEEP_TEX=1 ./scripts/build_docs.sh
DEBUG=1 ./scripts/build_docs.sh
SRCDIR="../docs" OUTPDFDIR="pdf" ./scripts/build_docs.sh
```

## Добавление файлов в сборку

В `build_docs.sh` есть массив вида:

```bash
FILES=( "spec.md" "pmi.md" "test_report.md" ... )
```

Добавь туда нужные `*.md` — они попадут в сборку.

## Частые проблемы

* **`mmdc: command not found`**
  Установи Mermaid CLI и проверь `PATH`:

  ```bash
  sudo npm i -g @mermaid-js/mermaid-cli
  mmdc --version
  ```

* **`xelatex: command not found` / ошибки пакетов**
  Установи TeX Live / MacTeX / MiKTeX. Для Debian/Ubuntu надёжнее `texlive-full`.

* **Ошибки шрифтов (`fontspec`)**
  Убедись, что XeLaTeX видит системные шрифты. На macOS путь `/Library/TeX/texbin` должен быть в `PATH`.

* **`Permission denied` при запуске**
  Выдай права: `chmod +x scripts/build_docs.sh`.

* **Мусорные `.log/.aux`**
  Если скрипт не чистит:

  ```bash
  find docs -type f -name "*.log" -delete
  find docs -type f -name "*.aux" -delete
  ```
