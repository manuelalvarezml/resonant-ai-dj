"""Canonical key names plus derived Camelot and Open Key codes."""

from __future__ import annotations

TONIC_ALIASES = {
    "C": "C",
    "B#": "C",
    "C#": "C#",
    "DB": "C#",
    "D": "D",
    "D#": "D#",
    "EB": "D#",
    "E": "E",
    "FB": "E",
    "F": "F",
    "E#": "F",
    "F#": "F#",
    "GB": "F#",
    "G": "G",
    "G#": "G#",
    "AB": "G#",
    "A": "A",
    "A#": "A#",
    "BB": "A#",
    "B": "B",
    "CB": "B",
}

# Display tonic prefers common DJ spellings for major/minor.
DISPLAY_TONIC = {
    ("C", "major"): "C",
    ("C", "minor"): "C",
    ("C#", "major"): "Db",
    ("C#", "minor"): "C#",
    ("D", "major"): "D",
    ("D", "minor"): "D",
    ("D#", "major"): "Eb",
    ("D#", "minor"): "Eb",
    ("E", "major"): "E",
    ("E", "minor"): "E",
    ("F", "major"): "F",
    ("F", "minor"): "F",
    ("F#", "major"): "F#",
    ("F#", "minor"): "F#",
    ("G", "major"): "G",
    ("G", "minor"): "G",
    ("G#", "major"): "Ab",
    ("G#", "minor"): "G#",
    ("A", "major"): "A",
    ("A", "minor"): "A",
    ("A#", "major"): "Bb",
    ("A#", "minor"): "Bb",
    ("B", "major"): "B",
    ("B", "minor"): "B",
}

CAMELOT_BY_PITCH_MODE = {
    ("C", "major"): "8B",
    ("A", "minor"): "8A",
    ("G", "major"): "9B",
    ("E", "minor"): "9A",
    ("D", "major"): "10B",
    ("B", "minor"): "10A",
    ("A", "major"): "11B",
    ("F#", "minor"): "11A",
    ("E", "major"): "12B",
    ("C#", "minor"): "12A",
    ("B", "major"): "1B",
    ("G#", "minor"): "1A",
    ("F#", "major"): "2B",
    ("D#", "minor"): "2A",
    ("C#", "major"): "3B",
    ("A#", "minor"): "3A",
    ("G#", "major"): "4B",
    ("F", "minor"): "4A",
    ("D#", "major"): "5B",
    ("C", "minor"): "5A",
    ("A#", "major"): "6B",
    ("G", "minor"): "6A",
    ("F", "major"): "7B",
    ("D", "minor"): "7A",
}


def normalize_tonic(tonic: str) -> str | None:
    token = tonic.strip().upper().replace("♯", "#").replace("♭", "B")
    token = token.replace("SHARP", "#").replace("FLAT", "B")
    return TONIC_ALIASES.get(token)


def normalize_mode(mode: str) -> str | None:
    token = mode.strip().lower()
    if token in {"major", "maj", "ionian"}:
        return "major"
    if token in {"minor", "min", "aeolian"}:
        return "minor"
    return None


def camelot_code(tonic: str, mode: str) -> str | None:
    pitch = normalize_tonic(tonic)
    scale = normalize_mode(mode)
    if pitch is None or scale is None:
        return None
    return CAMELOT_BY_PITCH_MODE.get((pitch, scale))


def open_key_code(camelot: str | None) -> str | None:
    if not camelot or len(camelot) < 2:
        return None
    letter = camelot[-1].upper()
    try:
        number = int(camelot[:-1])
    except ValueError:
        return None
    if letter not in {"A", "B"} or not 1 <= number <= 12:
        return None
    open_number = ((number - 8) % 12) + 1
    suffix = "m" if letter == "A" else "d"
    return f"{open_number}{suffix}"


def standard_key_name(tonic: str, mode: str) -> str | None:
    pitch = normalize_tonic(tonic)
    scale = normalize_mode(mode)
    if pitch is None or scale is None:
        return None
    display = DISPLAY_TONIC.get((pitch, scale), pitch)
    return f"{display} {scale}"


def notation_bundle(tonic: str, mode: str) -> tuple[str | None, str | None, str | None, str | None]:
    pitch = normalize_tonic(tonic)
    scale = normalize_mode(mode)
    if pitch is None or scale is None:
        return None, None, None, None
    display = DISPLAY_TONIC.get((pitch, scale), pitch)
    camelot = CAMELOT_BY_PITCH_MODE.get((pitch, scale))
    return display, f"{display} {scale}", camelot, open_key_code(camelot)
