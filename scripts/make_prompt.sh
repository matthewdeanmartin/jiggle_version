#!/usr/bin/env bash
set -euo pipefail

# readonly SCRIPT_NS="bash2gitlab_proc"
readonly SRC_DIR="./jiggle_version"
readonly TMP_ROOT="/tmp"
readonly TMP_DIR="${TMP_ROOT}/jiggle_version"
readonly OUTPUT_MD_BASENAME="jiggle_version.flat.md"

# Copy directory safely
bash2gitlab_proc::copy_to_tmp() {
  if [[ ! -d "${SRC_DIR}" ]]; then
    echo "Error: Source directory '${SRC_DIR}' not found." >&2
    exit 1
  fi

  echo "Copying '${SRC_DIR}' to '${TMP_DIR}'..."
  rm -rf "${TMP_DIR}"
  cp -a "${SRC_DIR}" "${TMP_DIR}"
}

# Run strip-docs for each subdirectory of tmp/jiggle_version
bash2gitlab_proc::run_strip_docs() {
  local dir
  echo "Running strip-docs on '${TMP_DIR}' and subdirectories..."

  while IFS= read -r -d '' dir; do
    echo "→ strip-docs on '${dir}'"
    strip-docs "${dir}"
  done < <(find "${TMP_DIR}" -type d -print0)
}

# Ask for confirmation before proceeding
bash2gitlab_proc::confirm() {
  local prompt="$1"

  if [[ -z "${CAUTION:-}" ]]; then
    echo "Skipping prompt: CAUTION not set."
    return 0
  fi

  read -rp "${prompt} [y/N] " response
  if [[ "${response}" =~ ^[Yy]$ ]]; then
    return 0
  else
    echo "Aborted." >&2
    exit 1
  fi
}

# Remove temporary strip markers and flatten the repo to a single Markdown file
bash2gitlab_proc::flatten_repo() {
  echo "Removing marker lines from .py files in '${TMP_DIR}'..."

  find "${TMP_DIR}" -type f -name '*.py' -print0 | while IFS= read -r -d '' file; do
    # Remove lines that are exactly "        ##" or "   #--" (whitespace-sensitive)
    sed -i '/^[[:space:]]*##[[:space:]]*$/d;/^[[:space:]]*#--[[:space:]]*$/d' "$file"
  done

  echo "Running black on '${TMP_DIR}'..."
  set +e
  black "${TMP_DIR}"
  set -e

  echo "Running coderoller-flatten-repo on '${TMP_DIR}'..."
  coderoller-flatten-repo "${TMP_DIR}"
}

# Clean trailing '##' that appear at the END of lines inside ```python code fences
# in the generated Markdown (jiggle_version.flat.md). Other code fences remain untouched.
bash2gitlab_proc::clean_flat_md_trailing_double_hash() {
  local output_md
  # Prefer TMP_DIR if the file is written there; fallback to CWD; else try to find it
  if [[ -f "${TMP_DIR}/${OUTPUT_MD_BASENAME}" ]]; then
    output_md="${TMP_DIR}/${OUTPUT_MD_BASENAME}"
  elif [[ -f "${OUTPUT_MD_BASENAME}" ]]; then
    output_md="${OUTPUT_MD_BASENAME}"
  else
    local found
    found="$(find "${TMP_DIR}" . -maxdepth 2 -type f -name "${OUTPUT_MD_BASENAME}" 2>/dev/null | head -n1 || true)"
    if [[ -n "${found}" ]]; then
      output_md="${found}"
    else
      echo "Note: ${OUTPUT_MD_BASENAME} not found; skipping cleanup."
      return 0
    fi
  fi

  echo "Cleaning trailing '##' inside Python code blocks in '${output_md}'..."

  # Use awk to track when we're inside a fenced code block and what the language is.
  # Only modify lines within ```python or ```py blocks. We strip a trailing '##' plus any surrounding whitespace.
  awk '
  BEGIN { in_code=0; lang="" }
  /^```/ {
    if (in_code==0) {
      in_code=1
      if (match($0, /^```[ \t]*([A-Za-z0-9_+\-]+)/, m)) { lang=m[1] } else { lang="" }
    } else {
      in_code=0; lang=""
    }
    print; next
  }
  {
    if (in_code==1 && (lang=="python" || lang=="py")) {
      sub(/[ \t]*##[ \t]*$/, "")
    }
    print
  }' "${output_md}" > "${output_md}.tmp" && mv "${output_md}.tmp" "${output_md}"
}

# Cleanup tmp directory
bash2gitlab_proc::cleanup_tmp() {
  echo "Cleaning up '${TMP_DIR}'..."
  rm -rf "${TMP_DIR}"
}

main() {
  bash2gitlab_proc::copy_to_tmp
  bash2gitlab_proc::run_strip_docs
  bash2gitlab_proc::confirm "Run coderoller-flatten-repo?"
  bash2gitlab_proc::flatten_repo
  # Post-process the flattened Markdown to remove trailing '##' in Python code blocks only
  bash2gitlab_proc::clean_flat_md_trailing_double_hash
  bash2gitlab_proc::confirm "Delete temporary files in '${TMP_DIR}'?"
  bash2gitlab_proc::cleanup_tmp
}

[[ "${BASH_SOURCE[0]}" == "$0" ]] && main "$@"
