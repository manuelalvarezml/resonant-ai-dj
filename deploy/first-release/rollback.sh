#!/usr/bin/env bash
set -euo pipefail
# Rollback is the same verified activation path using a previous immutable
# release, its exact image and that release/image's Linux acceptance evidence.
exec python3 "$(dirname "$0")/activate.py" "$@"
