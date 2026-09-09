"""Optional local desktop form. Tkinter is imported only when launched.

The view calls the same service as the CLI. Network interpretation runs in one
daemon worker; all widget access stays on the main thread. No local HTTP server,
hosted site, browser permissions, or additional UI dependency is needed.
"""

from __future__ import annotations

from queue import Empty, Queue
from threading import Thread
from typing import TYPE_CHECKING

from .models import Catalog, PlaylistRun, Vocabulary
from .service import build_playlist

if TYPE_CHECKING:
    from .translators import Translator


def catalog_coverage(catalog: Catalog) -> str:
    usable = {"passed", "warning"}
    genre = sum(any(t.tag.startswith("genre:") and t.status in usable for t in track.tags) for track in catalog.tracks)
    bpm = sum(track.bpm is not None and track.bpm.status in usable for track in catalog.tracks)
    semantics = sum(any(t.tag.split(":")[0] in {"mood", "energy", "vocals"} and t.status in usable for t in track.tags) for track in catalog.tracks)
    return f"Available evidence: {genre} tracks with genre tags · {bpm} with BPM · {semantics} with mood, energy or vocal tags."


def initial_prompt(catalog: Catalog, *, rules: bool) -> str:
    usable = {"passed", "warning"}
    has_house = any(tag.tag == "genre:house" and tag.status in usable for track in catalog.tracks for tag in track.tags)
    if has_house:
        return "require house; count 5" if rules else "Find up to five tracks. Only include tracks tagged as house."
    has_bpm = any(track.bpm and track.bpm.status in usable for track in catalog.tracks)
    if has_bpm:
        return "bpm 120-135; count 5" if rules else "Find up to five tracks between 120 and 135 BPM."
    return "count 5" if rules else "Return five tracks from the catalog without genre or tempo restrictions."


def describe_run(run: PlaylistRun) -> str:
    """Human-readable criteria and evidence, also useful to other interfaces."""
    query = run.translation.query
    lines = ["Interpreted criteria (proposal)",
             "Required: " + (", ".join(query.required_tags) or "none"),
             "Preferred: " + (", ".join(query.preferred_tags) or "none"),
             "Excluded: " + (", ".join(query.excluded_tags) or "none"),
             f"BPM bounds: {query.min_bpm if query.min_bpm is not None else 'open'} to {query.max_bpm if query.max_bpm is not None else 'open'}",
             f"Up to {query.limit} tracks · Order: {query.order}"]
    if query.excluded_track_ids:
        lines.append("Excluded IDs: " + ", ".join(query.excluded_track_ids))
    if run.translation.unresolved:
        lines += ["", "Please clarify:", *["• " + item for item in run.translation.unresolved]]
    if run.result:
        lines += ["", "Match evidence"]
        for index, match in enumerate(run.result.matches, 1):
            lines.append(f"{index}. {match.track.title}")
            lines.extend("   " + reason for reason in match.reasons)
            for evidence in match.track.tags:
                if evidence.tag in match.matched_tags:
                    lines.append(f"   {evidence.tag}: {evidence.authority} · {evidence.status} · {evidence.source}")
            if match.track.bpm:
                lines.append(f"   Tempo: {match.track.bpm.authority} · {match.track.bpm.status} · {match.track.bpm.source}")
            lines.extend("   Note: " + note for note in match.track.warnings)
    notes = [*run.translation.warnings, *run.warnings, *(run.result.warnings if run.result else [])]
    if notes:
        lines += ["", "Notes", *["• " + note for note in dict.fromkeys(notes)]]
    return "\n".join(lines)


def tag_label(tag: str) -> str:
    """Readable labels derived only from the requested descriptor ID."""
    axis, value = tag.split(":", 1)
    label = value.replace("_", " ").replace("-", " ")
    return f"{label.capitalize()} energy" if axis == "energy" else label.capitalize()


def compact_text(text: str, limit: int = 320) -> str:
    """Keep the overview bounded; the full interpretation remains in details."""
    return text if len(text) <= limit else text[:limit].rstrip() + "… See details for more."


def criteria_summary(run: PlaylistRun) -> str:
    query = run.translation.query
    lines = []
    for label, tags in (("Must match", query.required_tags), ("Prefer", query.preferred_tags), ("Avoid", query.excluded_tags)):
        if tags:
            lines.append(f"{label}  ·  " + ", ".join(map(tag_label, tags)))
    if query.min_bpm is not None or query.max_bpm is not None:
        low, high = query.min_bpm, query.max_bpm
        tempo = f"{low:g}–{high:g}" if low is not None and high is not None else (f"{low:g}+" if low is not None else f"Up to {high:g}")
        lines.append(f"Tempo  ·  {tempo} BPM")
    if query.excluded_track_ids:
        lines.append(f"Avoid  ·  {len(query.excluded_track_ids)} specified track(s)")
    order = {"relevance": "Best descriptor match first", "bpm_ascending": "Slower to faster", "bpm_descending": "Faster to slower"}[query.order]
    lines.append(f"Up to {query.limit} tracks  ·  {order}")
    return "\n\n".join(lines)


def result_notice(run: PlaylistRun, catalog: Catalog) -> str:
    """Keep consequential evidence gaps visible even with details collapsed."""
    if run.translation.unresolved:
        return "Please clarify: " + " · ".join(run.translation.unresolved)
    usable_tags = {e.tag for track in catalog.tracks for e in track.tags if e.status in {"passed", "warning"}}
    query = run.translation.query
    unavailable = sorted((set(query.required_tags) | set(query.preferred_tags)) - usable_tags)
    notes = []
    if unavailable:
        notes.append("Not evidenced in this library: " + ", ".join(map(tag_label, unavailable)) + ".")
    if run.status == "no_matches":
        notes.append("No tracks satisfy every required filter. Try a broader description.")
    elif run.result and any(match.missing_preferred_tags for match in run.result.matches):
        notes.append("These candidates meet the required filters; some preferences are not evidenced.")
    if query.excluded_tags:
        axes = {tag.split(":", 1)[0] for tag in query.excluded_tags}
        if not any(axes <= set(track.complete_tag_axes) for track in catalog.tracks):
            notes.append("This library cannot verify the requested exclusions from missing tags.")
    if (query.min_bpm is not None or query.max_bpm is not None) and run.result:
        notes.append("Tracks without usable BPM are omitted.")
    if not notes:
        notes.append("Matched using the requested filters and recorded library evidence." if query.required_tags or query.preferred_tags or query.excluded_tags or query.min_bpm is not None or query.max_bpm is not None else "No style or tempo filters requested. These are eligible library candidates.")
    return "\n".join(notes)


def match_summary(match) -> str:
    """A selected row explains positive matches without treating scores as confidence."""
    track = match.track
    lines = [track.title + (f"  —  {track.artist}" if track.artist else "")]
    if match.matched_tags:
        lines.append("Matched: " + ", ".join(map(tag_label, match.matched_tags)))
    if match.missing_preferred_tags:
        lines.append("Not evidenced: " + ", ".join(map(tag_label, match.missing_preferred_tags)))
    if track.bpm and track.bpm.status in {"passed", "warning"}:
        lines.append(f"BPM {track.bpm.value:g} · {track.bpm.authority.replace('_', ' ')} · {track.bpm.status}")
    return "\n".join(lines)


class PlaylistApp:
    """Thin native view over the playlist service; no network work on the UI thread."""

    def __init__(self, root, catalog: Catalog, vocabulary: Vocabulary, translator: "Translator"):
        import tkinter as tk
        from tkinter import ttk
        from tkinter.scrolledtext import ScrolledText

        if hasattr(translator, "grammar"):
            raise ValueError("The playlist interface requires OpenAI for natural language. Use the prompt command with --provider rules for offline developer checks.")
        self.root, self.catalog, self.vocabulary, self.translator = root, catalog, vocabulary, translator
        self.completion: Queue = Queue()
        self.latest: PlaylistRun | None = None
        self.busy = False
        self.closed = False
        self.details_visible = False
        self.placeholder = "e.g. house dj set energetic"
        self.has_placeholder = True
        self.colors = c = dict(bg="#F3F5F6", card="#FFFFFF", ink="#172B32", muted="#60747B", line="#DFE6E8", accent="#087F72", soft="#E7F3EF", amber="#FFF3D8")
        root.title(f"Prompt to Playlist · OpenAI · {len(catalog.tracks)} tracks")
        root.geometry("1200x840")
        root.minsize(1000, 700)
        root.configure(bg=c["bg"])
        root.option_add("*Font", "Helvetica 13")
        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure("Playlist.Treeview", background=c["card"], fieldbackground=c["card"], foreground=c["ink"], borderwidth=0, rowheight=48, font=("Helvetica", 13))
        style.map("Playlist.Treeview", background=[("selected", c["soft"])], foreground=[("selected", c["ink"])])
        style.configure("Playlist.Treeview.Heading", background=c["card"], foreground=c["muted"], borderwidth=0, relief="flat", padding=(10, 12), font=("Helvetica", 11, "bold"))
        style.map("Playlist.Treeview.Heading", background=[("active", c["bg"])])
        style.configure("Playlist.Vertical.TScrollbar", troughcolor=c["card"], background=c["line"], borderwidth=0, arrowsize=10)
        style.configure("Accent.TButton", background=c["accent"], foreground="white", borderwidth=0, padding=(18, 13), font=("Helvetica", 14, "bold"))
        style.map("Accent.TButton", background=[("disabled", "#B6C7C6"), ("active", "#066B61")], foreground=[("disabled", "#FFFFFF")])
        style.configure("Quiet.TButton", background=c["card"], foreground=c["accent"], borderwidth=1, bordercolor=c["line"], padding=(12, 9), font=("Helvetica", 12))
        style.map("Quiet.TButton", background=[("active", c["soft"])], foreground=[("disabled", "#96A3A7")])
        style.configure("Playlist.Horizontal.TProgressbar", background=c["accent"], troughcolor=c["bg"], borderwidth=0, thickness=3)

        def label(parent, text="", *, size=13, color=None, bold=False, bg=None, **kwargs):
            return tk.Label(parent, text=text, font=("Helvetica", size, "bold" if bold else "normal"), fg=color or c["ink"], bg=bg or parent.cget("bg"), anchor="w", justify="left", **kwargs)

        shell = tk.Frame(root, bg=c["bg"], padx=30, pady=24)
        shell.pack(fill="both", expand=True)
        shell.columnconfigure(0, weight=1)
        shell.rowconfigure(1, weight=1)
        header = tk.Frame(shell, bg=c["bg"])
        header.grid(row=0, column=0, sticky="ew", pady=(0, 24))
        brand = tk.Canvas(header, width=32, height=32, bg=c["bg"], highlightthickness=0)
        brand.pack(side="left", padx=(0, 12))
        for x, y in [(2, 12), (9, 5), (16, 1), (23, 9)]:
            brand.create_line(x + 2, y + 2, x + 2, 30 - y // 2, width=4, fill=c["accent"], capstyle="round")
        label(header, "Prompt to Playlist", size=21, bold=True).pack(side="left")
        label(header, "OpenAI", size=12, color=c["accent"], bg=c["soft"], padx=12, pady=7).pack(side="right")
        label(header, f"{len(catalog.tracks)} TRACKS  /  LOCAL LIBRARY", size=10, color=c["muted"]).pack(side="right", padx=18)

        content = tk.Frame(shell, bg=c["bg"])
        content.grid(row=1, column=0, sticky="nsew")
        content.columnconfigure(1, weight=1)
        content.rowconfigure(0, weight=1)
        compose = tk.Frame(content, bg=c["card"], width=340, padx=22, pady=22, highlightbackground=c["line"], highlightthickness=1)
        compose.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        compose.grid_propagate(False)
        compose.columnconfigure(0, weight=1)
        label(compose, "YOUR SOUND", size=10, bold=True, color=c["muted"]).grid(row=0, column=0, sticky="w")
        label(compose, "Describe your set", size=23, bold=True).grid(row=1, column=0, sticky="w", pady=(12, 8))
        label(compose, "Use your own words. Include a genre,\na feeling, a tempo or a track count.", size=12, color=c["muted"]).grid(row=2, column=0, sticky="w", pady=(0, 20))
        self.prompt = tk.Text(compose, height=6, width=24, wrap="word", font=("Helvetica", 16), bg="#F8FAFA", fg=c["muted"], insertbackground=c["accent"], selectbackground=c["soft"], relief="flat", highlightthickness=1, highlightbackground=c["line"], highlightcolor=c["accent"], padx=12, pady=14, undo=True)
        self.prompt.grid(row=3, column=0, sticky="ew")
        self.prompt.insert("1.0", self.placeholder)
        self.prompt.bind("<FocusIn>", self._clear_placeholder)
        self.prompt.bind("<FocusOut>", self._restore_placeholder)
        self.find_button = ttk.Button(compose, text="Find tracks  →", style="Accent.TButton", command=self.submit)
        self.find_button.grid(row=4, column=0, sticky="ew", pady=(12, 8))
        label(compose, "⌘ Return to search", size=10, color=c["muted"]).grid(row=5, column=0, sticky="w")
        tk.Frame(compose, bg=c["line"], height=1).grid(row=6, column=0, sticky="ew", pady=16)
        label(compose, "YOUR REQUEST, INTERPRETED", size=10, bold=True, color=c["muted"]).grid(row=7, column=0, sticky="w")
        self.criteria = label(compose, "Your criteria will appear here\nafter you find tracks.", size=12, color=c["muted"], wraplength=292)
        self.criteria.grid(row=8, column=0, sticky="nw", pady=(12, 0))
        compose.rowconfigure(9, weight=1)
        label(compose, "Only your words and the tag vocabulary\ngo to OpenAI. Your audio stays local.", size=11, color=c["muted"]).grid(row=10, column=0, sticky="sw", pady=(16, 0))

        results = tk.Frame(content, bg=c["card"], padx=22, pady=22, highlightbackground=c["line"], highlightthickness=1)
        results.grid(row=0, column=1, sticky="nsew")
        results.columnconfigure(0, weight=1)
        results.rowconfigure(4, weight=1)
        toolbar = tk.Frame(results, bg=c["card"])
        toolbar.grid(row=0, column=0, sticky="ew")
        label(toolbar, "Your playlist", size=21, bold=True).pack(side="left")
        self.count = label(toolbar, "", size=11, color=c["muted"])
        self.count.pack(side="left", padx=12)
        self.export_button = ttk.Button(toolbar, text="Export JSON", style="Quiet.TButton", command=self.export_result, state="disabled")
        self.export_button.pack(side="right")
        self.status = tk.StringVar(value="Ready when you are.")
        self.status_label = label(results, size=12, color=c["muted"], textvariable=self.status, wraplength=670)
        self.status_label.grid(row=1, column=0, sticky="ew", pady=(12, 4))
        self.progress = ttk.Progressbar(results, mode="indeterminate", style="Playlist.Horizontal.TProgressbar")
        self.progress.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        self.notice = label(results, "Search your library using a description.\nMatches will reflect the tags and tempo available in your files.", size=12, bg=c["soft"], padx=12, pady=12, wraplength=630)
        self.notice.grid(row=3, column=0, sticky="ew", pady=(0, 12))
        table_frame = tk.Frame(results, bg=c["card"])
        table_frame.grid(row=4, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        self.table = ttk.Treeview(table_frame, columns=("number", "title", "artist", "bpm"), show="headings", selectmode="browse", height=7, style="Playlist.Treeview")
        for column, title, width, stretch in [("number", "#", 34, False), ("title", "TRACK", 260, True), ("artist", "ARTIST", 175, True), ("bpm", "BPM¹", 62, False)]:
            self.table.heading(column, text=title, anchor="w")
            self.table.column(column, width=width, minwidth=width if not stretch else 90, stretch=stretch, anchor="w")
        self.table.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview, style="Playlist.Vertical.TScrollbar")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.table.configure(yscrollcommand=scrollbar.set)
        self.table.tag_configure("even", background="#F7F9F9")
        self.table.bind("<<TreeviewSelect>>", self._select_track)
        self.selection = label(results, "Select a track to see what matched.", size=11, color=c["muted"], wraplength=660)
        self.selection.grid(row=5, column=0, sticky="ew", pady=(14, 10))
        evidence_toolbar = tk.Frame(results, bg=c["card"])
        evidence_toolbar.grid(row=6, column=0, sticky="ew")
        self.details_button = ttk.Button(evidence_toolbar, text="Show criteria & evidence", style="Quiet.TButton", command=self.toggle_details, state="disabled")
        self.details_button.pack(side="left")
        label(evidence_toolbar, "¹ Source BPM, not verified here", size=10, color=c["muted"]).pack(side="right")
        self.details = ScrolledText(results, height=9, wrap="word", font=("Helvetica", 11), padx=12, pady=12, background="#F8FAFA", foreground=c["ink"], relief="flat", borderwidth=0, state="disabled")
        self.details.grid(row=7, column=0, sticky="ew", pady=(12, 0))
        self.details.grid_remove()
        footer = tk.Frame(shell, bg=c["bg"])
        footer.grid(row=2, column=0, sticky="ew", pady=(16, 0))
        label(footer, catalog_coverage(catalog), size=10, color=c["muted"]).pack(side="left")
        label(footer, "Playlist selection · Mix planning is separate", size=10, color=c["muted"]).pack(side="right")
        results.bind("<Configure>", lambda event: self._resize_results(event.width))
        root.bind("<Command-Return>", self._keyboard_submit)
        root.bind("<Control-Return>", self._keyboard_submit)
        root.protocol("WM_DELETE_WINDOW", self.close)
        self.poll_id = root.after(100, self._poll)
        root.after_idle(self.find_button.focus_set)

    def _resize_results(self, width):
        width = max(280, width - 70)
        self.notice.configure(wraplength=width)
        self.status_label.configure(wraplength=width)
        self.selection.configure(wraplength=width)

    def _clear_placeholder(self, event=None):
        if self.has_placeholder:
            self.prompt.delete("1.0", "end")
            self.prompt.configure(fg=self.colors["ink"])
            self.has_placeholder = False

    def _restore_placeholder(self, event=None):
        if not self.busy and not self.prompt.get("1.0", "end-1c").strip():
            self.has_placeholder = True
            self.prompt.insert("1.0", self.placeholder)
            self.prompt.configure(fg=self.colors["muted"])

    def _keyboard_submit(self, event=None):
        self.submit()
        return "break"

    def _set_details(self, text):
        self.details.configure(state="normal")
        self.details.delete("1.0", "end")
        self.details.insert("1.0", text)
        self.details.configure(state="disabled")

    def _worker(self, text):
        try:
            self.completion.put((build_playlist(text, self.catalog, self.vocabulary, self.translator), None))
        except (ValueError, OSError) as exc:
            self.completion.put((None, str(exc)))
        except Exception:
            self.completion.put((None, "The request could not be completed. Please try again."))

    def submit(self):
        if self.busy:
            return
        text = "" if self.has_placeholder else self.prompt.get("1.0", "end-1c")
        if not text.strip() or len(text) > 4000:
            self.status.set("Describe your playlist in 1–4000 characters.")
            self.prompt.focus_set()
            return
        self.busy = True
        self.latest = None
        self.prompt.configure(state="disabled")
        self.export_button.configure(state="disabled")
        self.details_button.configure(state="disabled")
        self.find_button.configure(state="disabled", text="Finding tracks…")
        self.table.delete(*self.table.get_children())
        self.count.configure(text="")
        self.selection.configure(text="")
        self.criteria.configure(text="Reading your description…")
        self.notice.configure(text="OpenAI is translating your words into search criteria.\nYour library will be searched locally.", bg=self.colors["soft"])
        self._set_details("")
        self.status.set("Interpreting your request…")
        self.progress.start(12)
        Thread(target=self._worker, args=(text,), daemon=True).start()

    def _poll(self):
        try:
            run, error = self.completion.get_nowait()
        except Empty:
            pass
        else:
            self._complete(run, error)
        if not self.closed:
            self.poll_id = self.root.after(100, self._poll)

    def _complete(self, run, error):
        self.busy = False
        self.progress.stop()
        self.progress.configure(value=0)
        self.prompt.configure(state="normal")
        self.find_button.configure(state="normal", text="Find tracks  →")
        if error:
            self.status.set("Couldn’t complete this request.")
            self.notice.configure(text=compact_text(error, 380), bg=self.colors["amber"])
            self._set_details(error)
            self.details_button.configure(state="normal")
            self.criteria.configure(text="No interpretation was accepted.\nYour description is ready to retry.")
            return
        self.latest = run
        self.export_button.configure(state="normal")
        self.details_button.configure(state="normal")
        self.criteria.configure(text=compact_text(criteria_summary(run)), fg=self.colors["ink"])
        self.notice.configure(text=compact_text(result_notice(run, self.catalog), 380), bg=self.colors["amber"] if run.status != "matched" or (run.result and any(m.missing_preferred_tags for m in run.result.matches)) else self.colors["soft"])
        if run.result:
            for index, match in enumerate(run.result.matches):
                track = match.track
                bpm = f"{track.bpm.value:g}" if track.bpm and track.bpm.status in {"passed", "warning"} else "—"
                self.table.insert("", "end", iid=str(index), values=(f"{index + 1:02}", track.title, track.artist or "—", bpm), tags=("even",) if index % 2 == 0 else ())
            count = len(run.result.matches)
            self.count.configure(text=f"{count} tracks")
            self.status.set(f"{count} candidates from {len(self.catalog.tracks)} tracks · Based on your submitted description")
            if count:
                self.table.selection_set("0")
                self.table.focus("0")
        if run.status == "no_matches":
            self.status.set("No matches with the available evidence.")
        elif run.status == "needs_clarification":
            self.status.set("A little more detail is needed. Edit your description and try again.")
        self._set_details('Submitted description\n' + run.translation.request_text + '\n\n' + describe_run(run))

    def _select_track(self, event=None):
        selected = self.table.selection()
        if selected and self.latest and self.latest.result:
            self.selection.configure(text=match_summary(self.latest.result.matches[int(selected[0])]))

    def toggle_details(self):
        self.details_visible = not self.details_visible
        if self.details_visible:
            self.details.grid()
        else:
            self.details.grid_remove()
        self.details_button.configure(text="Hide criteria & evidence" if self.details_visible else "Show criteria & evidence")

    def export_result(self):
        if not self.latest:
            return
        from pathlib import Path
        from tkinter import filedialog
        from .adapters import save_json
        destination = filedialog.asksaveasfilename(parent=self.root, title="Export playlist result", defaultextension=".json", filetypes=[("JSON", "*.json")])
        if destination:
            try:
                save_json(self.latest, Path(destination))
            except (ValueError, OSError) as exc:
                self.status.set(str(exc))
            else:
                self.status.set("Playlist result exported.")

    def close(self):
        self.closed = True
        self.root.after_cancel(self.poll_id)
        self.root.destroy()


def launch(catalog: Catalog, vocabulary: Vocabulary, translator: "Translator") -> None:
    try:
        import tkinter as tk
    except ImportError:
        raise ValueError("The desktop form needs a Python build with Tkinter. The prompt and search commands still work.") from None
    try:
        root = tk.Tk()
    except tk.TclError:
        raise ValueError("The desktop form needs a graphical desktop and working Tkinter installation.") from None
    try:
        PlaylistApp(root, catalog, vocabulary, translator)
    except Exception:
        root.destroy()
        raise
    root.mainloop()
