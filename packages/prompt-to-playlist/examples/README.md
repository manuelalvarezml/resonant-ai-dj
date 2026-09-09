# Fictional demonstration catalog

`demo-catalog.json` contains six **fictional** tracks and artists. All tempo,
duration, genre, mood, energy, and vocal values were authored as fixtures. There
is no underlying audio and no real song has been analyzed or tagged here.
`user_verified` identifies authored fixture metadata in this example only;
its source and warnings explicitly describe the synthetic origin. Never copy
these tags onto imported real tracks.

`house-query.json` asks for house tracks at 120–130 BPM, prefers dark mood, and
excludes vocals. It returns **Night Grid** and **Warehouse Lantern** with the
default vocabulary. The complete tag axes are explicit because the fictional
catalog has been exhaustively annotated on those axes; incomplete real catalogs
must not claim the same coverage.

From the package folder:

```sh
uv run prompt-playlist search --catalog examples/demo-catalog.json --query examples/house-query.json
uv run prompt-playlist prompt --catalog examples/demo-catalog.json --text 'require house; prefer dark; exclude vocal; bpm 120-130; count 5'
```

Omitting `--text` prompts in the terminal. JSON results go to stdout unless
`--out` names a new output file outside music folders. An existing file is never
overwritten. Rules mode understands a deliberately limited clause grammar;
unsupported wording produces `needs_clarification`, without searching.

The DJ importer reads only stored JSON. It checks the stored source hashes for
internal consistency and preserves numeric authority/status; it does not hash,
open, decode, or alter source audio. It imports no semantic tags. Therefore,
real DJ imports can support a BPM query immediately, while genre/mood/energy
queries require separately sourced annotations before they can match reliably.
