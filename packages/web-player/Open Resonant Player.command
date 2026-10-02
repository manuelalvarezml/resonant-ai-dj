#!/bin/zsh
set -eu
cd -- "$(dirname -- "$0")"
if ! command -v node >/dev/null 2>&1; then
  print 'Resonant requires Node.js 22 or newer. Install it, then reopen this launcher.'
  read -r '?Press Return to close.'
  exit 1
fi
print 'Open http://127.0.0.1:4173 in your browser. Keep this window open while listening.'
npm run dev
