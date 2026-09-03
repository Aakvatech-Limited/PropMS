#!/usr/bin/env bash
# Installs pre-commit and wires up the commit and push hooks for this clone.
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

if ! command -v pre-commit >/dev/null 2>&1; then
	echo "pre-commit not found, installing..."
	if command -v uv >/dev/null 2>&1; then
		uv tool install pre-commit
	elif command -v pipx >/dev/null 2>&1; then
		pipx install pre-commit
	else
		python3 -m pip install --user pre-commit
	fi
fi

pre-commit install --install-hooks --overwrite

echo
echo "Hooks installed:"
echo "  pre-commit  staged files only, fast"
echo "  commit-msg  conventional commit message check"
echo "  pre-push    pre-commit run --all-files, blocks the push on any failure"
