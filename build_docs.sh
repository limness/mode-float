#!/usr/bin/env bash
set -euo pipefail

SRCDIR="docs"
OUTPDFDIR="pdf"
TEMPLATE="templates/eis.gost.tex"
METADATA="refs.yaml"
FILES=(
  "spec.md"
  "pmi.md"
  "test_report.md"
  "acceptance_act.md"
  "admin_manual.md"
  "user_manual.md"
)

command -v pandoc >/dev/null || { echo "pandoc not found"; exit 1; }
command -v xelatex >/dev/null || { echo "xelatex not found"; exit 1; }

cd "$SRCDIR"
[[ -f "$TEMPLATE" ]] || { echo "Template not found: $TEMPLATE"; exit 1; }
[[ -f "$METADATA" ]] || { echo "Metadata not found: $METADATA"; exit 1; }
mkdir -p "$OUTPDFDIR"

cleanup_aux () {
  local stem="$1"
  rm -f \
    "${OUTPDFDIR}/${stem}.aux" "${OUTPDFDIR}/${stem}.log" "${OUTPDFDIR}/${stem}.out" \
    "${OUTPDFDIR}/${stem}.toc" "${OUTPDFDIR}/${stem}.lot" "${OUTPDFDIR}/${stem}.lof" \
    "${OUTPDFDIR}/${stem}.bbl" "${OUTPDFDIR}/${stem}.blg" "${OUTPDFDIR}/${stem}.fls" \
    "${OUTPDFDIR}/${stem}.fdb_latexmk" "${OUTPDFDIR}/${stem}.run.xml" || true
}

build_one () {
  local md="$1"
  [[ -f "$md" ]] || { echo "Missing: $md"; return 1; }
  local stem="${md%.md}"
  local pdf="${OUTPDFDIR}/${stem}.pdf"

  echo "→ $md"

  rm -f "$pdf"

  cleanup_aux "$stem"

  pandoc \
    --from=markdown+table_captions+footnotes \
    --metadata-file="$METADATA" \
    --number-sections --toc \
    --template="$TEMPLATE" \
    --pdf-engine=xelatex \
    --quiet \
    -o "$pdf" "$md"

  cleanup_aux "$stem"

  [[ -f "$pdf" ]] && echo "✔  $(pwd)/${pdf}" || { echo "✖  PDF not produced for $md"; return 1; }
}

rc=0
for f in "${FILES[@]}"; do
  build_one "$f" || rc=1
done
exit "$rc"
