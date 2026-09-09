"""Open the current view with the verified live result; future searches use OpenAI."""
import json
from pathlib import Path
import tkinter as tk
from prompt_to_playlist.adapters import load_catalog
from prompt_to_playlist.config import load_project_config, read_api_key
from prompt_to_playlist.desktop import PlaylistApp
from prompt_to_playlist.models import PlaylistRun
from prompt_to_playlist.translators import OpenAITranslator
from prompt_to_playlist.vocabulary import load_vocabulary

config = load_project_config(Path('playlist.toml'))
catalog = load_catalog(Path(config.catalog))
vocabulary = load_vocabulary(Path(config.vocabulary))
translator = OpenAITranslator(api_key=read_api_key(config.openai), model=config.openai.model, timeout_s=config.openai.timeout_s)
run = PlaylistRun.model_validate(json.loads(Path('output/openai-live-check-natural-language-v3.json').read_text())['cases'][0]['run'])
root = tk.Tk()
app = PlaylistApp(root, catalog, vocabulary, translator)
app._clear_placeholder()
app.prompt.insert('1.0', run.translation.request_text)
app._complete(run, None)
app.status.set('8 candidates · Saved result from the verified OpenAI request')
root.mainloop()
