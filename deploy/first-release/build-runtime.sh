#!/usr/bin/env bash
set -euo pipefail
if [[ $# != 2 ]]; then
  echo 'Usage: build-runtime.sh ALLOWLISTED_CONTEXT IMAGE_TAG' >&2
  exit 2
fi
context=$1
image_tag=$2
[[ -f "$context/runtime-source.json" ]] || { echo 'Missing allowlisted runtime manifest' >&2; exit 1; }
python3 "$(dirname "$0")/verify-runtime.py" "$context"
[[ "$image_tag" =~ ^resonant:[a-zA-Z0-9._-]+$ ]] || { echo 'Use an explicit resonant:version tag' >&2; exit 1; }
docker build --platform linux/amd64 --pull --tag "$image_tag" "$context"
docker run --rm --network none --entrypoint python "$image_tag" /opt/resonant/runtime-smoke.py --imports-only
docker image inspect --format '{{.Id}}' "$image_tag"
