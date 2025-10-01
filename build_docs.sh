#!/usr/bin/env bash
set -euo pipefail

# run before using (for mermaid graphs compiling)
# sudo npm i -g @mermaid-js/mermaid-cli

SRCDIR="docs"
OUTPDFDIR="pdf"
TEMPLATE="templates/eis.gost.tex"
METADATA="refs.yaml"
FILTERS_DIR="filters"
MERMAID_LUA="${FILTERS_DIR}/mermaid.lua"

MERMAID_OUTDIR_ABS="${SRCDIR}/static/mermaid"
MERMAID_OUTDIR_REL="static/mermaid"

FILES=( "spec.md" "pmi.md" "test_report.md" "acceptance_act.md" "admin_manual.md" "user_manual.md" )

command -v pandoc  >/dev/null || { echo "pandoc not found"; exit 1; }
command -v xelatex >/dev/null || { echo "xelatex not found"; exit 1; }
command -v mmdc    >/dev/null || { echo "mermaid-cli (mmdc) not found. Install: npm i -g @mermaid-js/mermaid-cli"; exit 1; }

mkdir -p "$MERMAID_OUTDIR_ABS"

cd "$SRCDIR"
[[ -f "$TEMPLATE" ]] || { echo "Template not found: $TEMPLATE"; exit 1; }
[[ -f "$METADATA" ]] || { echo "Metadata not found: $METADATA"; exit 1; }
[[ -f "$MERMAID_LUA" ]] || { echo "Lua filter not found: $MERMAID_LUA"; exit 1; }

mkdir -p "$OUTPDFDIR" "$MERMAID_OUTDIR_REL"

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

  MERMAID_OUTDIR="$MERMAID_OUTDIR_REL" pandoc \
    --from=markdown+table_captions+footnotes \
    --metadata-file="$METADATA" \
    --number-sections --toc \
    --template="$TEMPLATE" \
    --pdf-engine=xelatex \
    --lua-filter="$MERMAID_LUA" \
    --listings \
    --quiet \
    -o "$pdf" "$md"

  cleanup_aux "$stem"
  if [[ -f "$pdf" ]]; then
    echo "✔  $(pwd)/${pdf}"
  else
    echo "✖  PDF not produced for $md"
    return 1
  fi
}

rc=0
for f in "${FILES[@]}"; do
  build_one "$f" || rc=1
done
exit "$rc"