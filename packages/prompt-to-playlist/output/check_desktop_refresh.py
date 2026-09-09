import json
from pathlib import Path
import time
import tkinter as tk
from prompt_to_playlist.adapters import load_catalog
from prompt_to_playlist.config import load_project_config
from prompt_to_playlist.desktop import PlaylistApp
from prompt_to_playlist.models import PlaylistRun
from prompt_to_playlist.vocabulary import load_vocabulary

config = load_project_config(Path('playlist.toml'))
catalog = load_catalog(Path(config.catalog))
vocabulary = load_vocabulary(Path(config.vocabulary))
report = json.loads(Path('output/openai-live-check-natural-language-v3.json').read_text())
run = PlaylistRun.model_validate(report['cases'][0]['run'])
class Replay:
    model = config.openai.model
    calls = 0
    def translate(self, prompt, vocabulary):
        self.calls += 1
        assert prompt == run.translation.request_text
        return run.translation

root = tk.Tk()
provider = Replay()
app = PlaylistApp(root, catalog, vocabulary, provider)
checks = {}
root.update()
app._clear_placeholder()
app.prompt.insert('1.0', run.translation.request_text)
app.find_button.invoke()
app.submit()
checks['busy_input_locked'] = str(app.prompt.cget('state')) == 'disabled'
checks['export_disabled_while_waiting'] = app.export_button.instate(['disabled'])
end = time.monotonic() + 5
while app.latest is None and time.monotonic() < end:
    root.update()
    time.sleep(0.02)
assert app.latest
checks['one_service_call_for_duplicate_submit'] = provider.calls == 1
checks['eight_result_rows'] = len(app.table.get_children()) == 8
checks['energy_gap_visible'] = 'High energy' in app.notice.cget('text')
checks['natural_language_preserved'] = app.prompt.get('1.0', 'end-1c') == 'house dj set energetic'
checks['house_required_visible'] = 'Must match  ·  House' in app.criteria.cget('text')
checks['input_ready_after_result'] = str(app.prompt.cget('state')) == 'normal'
checks['no_percent_confidence_column'] = 'coverage' not in app.table.cget('columns')
layouts = []
for geometry in ['1200x840', '1000x700']:
    root.geometry(geometry)
    root.update()
    for details in [False, True]:
        if app.details_visible != details:
            app.toggle_details()
        root.update()
        widgets = {'prompt': app.prompt, 'search': app.find_button, 'criteria': app.criteria,
                   'notice': app.notice, 'table': app.table, 'evidence_button': app.details_button,
                   'export': app.export_button}
        if details:
            widgets['details'] = app.details
        bounds = {name: [widget.winfo_rootx() - root.winfo_rootx(), widget.winfo_rooty() - root.winfo_rooty(), widget.winfo_width(), widget.winfo_height()] for name, widget in widgets.items()}
        visible = {name: x >= 0 and y >= 0 and x + width <= root.winfo_width() and y + height <= root.winfo_height() for name, (x, y, width, height) in bounds.items()}
        layouts.append({'geometry': geometry, 'details': details, 'bounds': bounds, 'visible': visible})
checks['all_controls_within_window'] = all(all(layout['visible'].values()) for layout in layouts)
long_run = run.model_copy(deep=True)
long_run.translation.unresolved = ['Explain this detail ' + 'x' * 200] * 20
long_run.status = 'needs_clarification'
long_run.result = None
app._complete(long_run, None)
root.update()
checks['long_clarification_compact_and_full_details'] = len(app.notice.cget('text')) < 410 and ('x' * 200) in app.details.get('1.0', 'end')
checks['long_clarification_controls_fit'] = app.details_button.winfo_rooty() + app.details_button.winfo_height() <= root.winfo_rooty() + root.winfo_height()
def fail(prompt, vocabulary):
    raise ValueError('The OpenAI request timed out. Try again.')
provider.translate = fail
app.submit()
end = time.monotonic() + 5
while app.busy and time.monotonic() < end:
    root.update()
    time.sleep(0.02)
checks['failed_new_request_clears_export_and_old_results'] = app.latest is None and app.export_button.instate(['disabled']) and not app.table.get_children()
checks['failure_visible_and_retry_enabled'] = 'timed out' in app.notice.cget('text') and not app.find_button.instate(['disabled'])
checks['full_error_available_in_details'] = 'timed out' in app.details.get('1.0', 'end')
app.close()
result = {'schema': 'prompt-playlist/desktop-check', 'passed': all(checks.values()), 'checks': checks, 'layouts': layouts, 'live_api_requests': 0, 'note': 'Real Tk widgets replaying the saved successful OpenAI translation. Geometry and state checks; not screenshot QA.'}
Path('output/desktop-refresh-check.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
raise SystemExit(0 if result['passed'] else 1)
