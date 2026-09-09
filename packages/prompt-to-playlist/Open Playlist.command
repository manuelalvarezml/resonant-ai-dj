#!/bin/zsh
# Local launcher; Python reads only the configured key assignment, never sources zshrc.
set -eu
playlist_dir=${0:A:h}
cd "$playlist_dir"
playlist_uv=$(command -v uv || true)
if [[ -z "$playlist_uv" && -x "$HOME/.local/bin/uv" ]]; then
  playlist_uv="$HOME/.local/bin/uv"
fi
if [[ -z "$playlist_uv" ]]; then
  print -u2 "The playlist launcher needs uv installed. See README.md."
  exit 2
fi
exec "$playlist_uv" run --locked prompt-playlist ui --config "$playlist_dir/playlist.toml"
