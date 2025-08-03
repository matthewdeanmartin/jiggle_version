#!/usr/bin/env bash
set -euo pipefail

# readonly SCRIPT_NS="prompt"
readonly SRC_DIR="./jiggle_version"
readonly TMP_ROOT="/tmp"
readonly TMP_DIR="${TMP_ROOT}/jiggle_version"

# Copy directory safely
prompt::copy_to_tmp() {
  if [[ ! -d "${SRC_DIR}" ]]; then
    echo "Error: Source directory '${SRC_DIR}' not found." >&2
    exit 1
  fi

  echo "Copying '${SRC_DIR}' to '${TMP_DIR}'..."
  rm -rf "${TMP_DIR}"
  cp -a "${SRC_DIR}" "${TMP_DIR}"
}

# Run strip-docs for each subdirectory of tmp/jiggle_version./
prompt::run_strip_docs() {
  local dir
  echo "Running strip-docs on '${TMP_DIR}' and subdirectories..."

  while IFS= read -r -d '' dir; do
    echo "→ strip-docs on '${dir}'"
    strip-docs "${dir}"
  done < <(find "${TMP_DIR}" -type d -print0)
}

# Ask for confirmation before proceeding
prompt::confirm() {
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


# Run coderoller-flatten-repo
prompt::flatten_repo() {
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

# Cleanup tmp directory
prompt::cleanup_tmp() {
  echo "Cleaning up '${TMP_DIR}'..."
  rm -rf "${TMP_DIR}"
}

main() {
  prompt::copy_to_tmp
  prompt::run_strip_docs
  prompt::confirm "Run coderoller-flatten-repo?"
  prompt::flatten_repo
  prompt::confirm "Delete temporary files in '${TMP_DIR}'?"
  prompt::cleanup_tmp
}

[[ "${BASH_SOURCE[0]}" == "$0" ]] && main "$@"
