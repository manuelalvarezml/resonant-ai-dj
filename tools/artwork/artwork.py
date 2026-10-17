"""Independent artwork sidecars. Never decode, modify, or analyze source audio."""
from __future__ import annotations

import base64
import contextlib
import fcntl
import hashlib
import io
import json
import os
from pathlib import Path
import re
import sqlite3
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from email.utils import parsedate_to_datetime

import mutagen
from mutagen.flac import Picture
from mutagen.id3 import ID3
from PIL import Image, ImageOps

VERSION = "resonant/artwork/1"
MAX_IMAGE = 12 * 1024 * 1024
Image.MAX_IMAGE_PIXELS = 24_000_000
UUID = re.compile(r"^[a-f0-9]{8}-(?:[a-f0-9]{4}-){3}[a-f0-9]{12}$")
NEGATIVE_TTL = 30 * 86400


def normalized(value):
    return " ".join(unicodedata.normalize("NFC", str(value or "")).casefold().split())


def digest(value):
    return hashlib.sha256(value).hexdigest()


def file_digest(path):
    with open(path, "rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def album_key(scope, metadata, source_hash):
    artist = normalized(metadata.get("albumartist") or metadata.get("artist"))
    album = normalized(metadata.get("album"))
    missing = not artist or not album or artist in {"unknown artist", "unknown", "various artists"} or album in {"local files", "unknown album", "unknown"}
    identity = [scope, artist, album] if not missing else [scope, "source", source_hash]
    return digest(json.dumps(identity, ensure_ascii=False).encode()), not missing


def read_embedded(path):
    """Mutagen reads tags, not PCM. Prefer an explicit front; reject back-only art."""
    audio = mutagen.File(path)
    tags = audio.tags if audio is not None else None
    if tags is None:
        try:
            tags = ID3(path)
        except mutagen.MutagenError:
            return {}, []
    metadata = {}
    for field, keys in {"artist": ("TPE1", "ARTIST", "artist", "\xa9ART"), "albumartist": ("TPE2", "ALBUMARTIST", "albumartist", "aART"), "album": ("TALB", "ALBUM", "album", "\xa9alb")}.items():
        for key in keys:
            value = tags.get(key)
            if value:
                value = getattr(value, "text", value)
                metadata[field] = str(value[0] if isinstance(value, (list, tuple)) else value).strip()[:500]
                break
    pictures = []
    if hasattr(tags, "getall"):
        pictures += [(int(p.type), p.data) for p in tags.getall("APIC")]
    pictures += [(int(p.type), p.data) for p in getattr(audio, "pictures", [])]
    pictures += [(3, bytes(p)) for p in tags.get("covr", [])]
    for encoded in tags.get("metadata_block_picture", []):
        if len(encoded) <= MAX_IMAGE * 2:
            try:
                p = Picture(base64.b64decode(encoded, validate=True))
                pictures.append((int(p.type), p.data))
            except (ValueError, mutagen.MutagenError):
                pass
    fronts = [data for kind, data in pictures if kind == 3 and len(data) <= MAX_IMAGE]
    # An untyped single image is common in older files; never use a labelled back.
    if not fronts and len(pictures) == 1 and pictures[0][0] == 0:
        fronts = [pictures[0][1]]
    return metadata, fronts


def write_images(raw, root):
    if not raw or len(raw) > MAX_IMAGE:
        raise ValueError("image_size_limit")
    with Image.open(io.BytesIO(raw)) as image:
        if image.format not in {"JPEG", "PNG", "WEBP", "GIF"}:
            raise ValueError("unsupported_image")
        if image.width * image.height > Image.MAX_IMAGE_PIXELS:
            raise ValueError("image_pixel_limit")
        image.seek(0)
        image = ImageOps.exif_transpose(image).convert("RGBA")
        background = Image.new("RGB", image.size, "#202020")
        background.paste(image, mask=image.getchannel("A"))
        assets = {}
        for label, bound in (("cover", 500), ("thumbnail", 96)):
            copy = background.copy()
            copy.thumbnail((bound, bound), Image.Resampling.LANCZOS)
            data = io.BytesIO()
            copy.save(data, "JPEG", quality=86, optimize=True)
            value = data.getvalue()
            name = digest(value) + ".jpg"
            target = Path(root) / "images" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            temp = target.with_suffix(f".{os.getpid()}.tmp")
            temp.write_bytes(value)
            temp.replace(target)
            assets[label] = {"file": name, "width": copy.width, "height": copy.height, "sha256": digest(value)}
        return assets


class ProviderError(Exception):
    def __init__(self, reason, retry_after=0):
        super().__init__(reason)
        self.retry_after = retry_after


def safe_provider_url(url):
    if not isinstance(url, str):
        raise ProviderError("untrusted_provider_url")
    value = urllib.parse.urlsplit(url)
    host = value.hostname or ""
    if value.scheme not in {"http", "https"} or value.username or value.password or value.port not in {None, 443} or not (host in {"musicbrainz.org", "coverartarchive.org", "archive.org"} or host.endswith(".archive.org")):
        raise ProviderError("untrusted_provider_url")
    return urllib.parse.urlunsplit(("https", value.netloc, value.path, value.query, ""))


class SafeRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return super().redirect_request(req, fp, code, msg, headers, safe_provider_url(newurl))


def retry_delay(header, now=None):
    now = time.time() if now is None else now
    try:
        return max(0, float(header))
    except (TypeError, ValueError):
        try:
            return max(0, parsedate_to_datetime(header).timestamp() - now)
        except (TypeError, ValueError, OverflowError):
            return 0


class MusicBrainzCAA:
    def __init__(self, store, user_agent=None):
        self.store = store
        self.user_agent = user_agent or os.environ.get("RESONANT_ARTWORK_USER_AGENT", "ResonantArtwork/1.0 (+https://resonant.lat)")
        self.opener = urllib.request.build_opener(SafeRedirect())

    def get(self, url, *, image=False):
        url = safe_provider_url(url)
        # One shared clock across workers/restarts. The worker holds the process lock.
        now = time.time()
        due = self.store.next_request()
        if due - now > 2:
            raise ProviderError("provider_cooldown", due - now)
        time.sleep(max(0, due - now))
        self.store.set_next_request(time.time() + 1.1)
        request = urllib.request.Request(url, headers={"User-Agent": self.user_agent, "Accept": "image/*" if image else "application/json"})
        try:
            with self.opener.open(request, timeout=20) as response:
                data = response.read((MAX_IMAGE if image else 2 * 1024 * 1024) + 1)
                if len(data) > (MAX_IMAGE if image else 2 * 1024 * 1024):
                    raise ProviderError("provider_response_too_large")
                return data if image else json.loads(data)
        except urllib.error.HTTPError as error:
            if error.code == 404:
                return None
            delay = retry_delay(error.headers.get("Retry-After"))
            if error.code in {429, 503}:
                delay = max(delay, 60)
            self.store.set_next_request(time.time() + max(delay, 1.1))
            raise ProviderError(f"provider_http_{error.code}", delay) from error
        except (OSError, ValueError) as error:
            self.store.set_next_request(time.time() + 60)
            raise ProviderError("provider_unavailable") from error

    def resolve(self, metadata):
        artist = metadata.get("albumartist") or metadata.get("artist")
        album = metadata["album"]
        escape = lambda s: re.sub(r'([+\-!(){}\[\]^"~*?:\\/|&])', r'\\\1', s)
        query = f'releasegroup:"{escape(album)}" AND artist:"{escape(artist)}"'
        result = self.get("https://musicbrainz.org/ws/2/release-group/?" + urllib.parse.urlencode({"query": query, "fmt": "json", "limit": 100}))
        if not isinstance(result, dict) or not isinstance(result.get("release-groups"), list) or not isinstance(result.get("count"), int):
            raise ProviderError("invalid_musicbrainz_response")
        groups = (result or {}).get("release-groups", [])
        if (result or {}).get("count", 0) > len(groups):
            return {"status": "ambiguous", "reason": "truncated_search", "confidence": "none"}, None
        exact = {}
        for group in groups:
            if not isinstance(group, dict) or not isinstance(group.get("artist-credit"), list) or any(not isinstance(c, dict) for c in group["artist-credit"]):
                raise ProviderError("invalid_musicbrainz_response")
            credit = "".join(str(c.get("name") or c.get("artist", {}).get("name", "")) + c.get("joinphrase", "") for c in group.get("artist-credit", []))
            if normalized(group.get("title")) == normalized(album) and normalized(credit) == normalized(artist) and UUID.fullmatch(group.get("id", "")):
                exact[group["id"]] = group
        if len(exact) != 1:
            return {"status": "ambiguous" if exact else "missing", "reason": "multiple_exact_groups" if exact else "no_exact_group", "confidence": "none"}, None
        group_id, group = next(iter(exact.items()))
        listing_url = f"https://coverartarchive.org/release-group/{group_id}/"
        listing = self.get(listing_url)
        if listing is not None and (not isinstance(listing, dict) or not isinstance(listing.get("images"), list) or any(not isinstance(p, dict) for p in listing["images"])):
            raise ProviderError("invalid_caa_response")
        fronts = [p for p in (listing or {}).get("images", []) if p.get("front") is True and p.get("approved") is True]
        provenance = {"provider": "musicbrainz-caa", "release_group": group_id, "page_url": f"https://musicbrainz.org/release-group/{group_id}", "listing_url": listing_url, "release_url": (listing or {}).get("release"), "matched_artist": artist, "matched_album": group["title"], "match_rule": "unique_exact_normalized_artist_and_album_v1", "confidence": "high", "authority": "benchmark_estimate", "attribution": "Cover Art Archive / MusicBrainz; artwork copyright remains with its owners"}
        if len(fronts) != 1:
            return {**provenance, "status": "ambiguous" if fronts else "missing", "reason": "multiple_fronts" if fronts else "no_approved_front"}, None
        front = fronts[0]
        if not isinstance(front.get("thumbnails"), dict):
            raise ProviderError("invalid_caa_response")
        url = front.get("thumbnails", {}).get("500") or front.get("thumbnails", {}).get("large")
        if not url:
            return {**provenance, "status": "missing", "reason": "no_500_thumbnail"}, None
        raw = self.get(url, image=True)
        return {**provenance, "status": "ready" if raw else "missing", "reason": "matched" if raw else "image_missing", "source_url": safe_provider_url(url), "image_id": str(front.get("id", ""))}, raw


class Store:
    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.root / "artwork.sqlite", timeout=30)
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS albums (key TEXT PRIMARY KEY, record TEXT NOT NULL, expires REAL NOT NULL);
            CREATE TABLE IF NOT EXISTS jobs (scope TEXT, id TEXT, version TEXT, hash TEXT, path TEXT, metadata TEXT, album TEXT, eligible INTEGER, embedded TEXT, state TEXT, attempts INTEGER DEFAULT 0, due REAL DEFAULT 0, error TEXT, PRIMARY KEY(scope,id));
            CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value REAL);
        """)

    def next_request(self):
        row = self.db.execute("SELECT value FROM settings WHERE key='next_request'").fetchone()
        return row[0] if row else 0

    def set_next_request(self, value):
        with self.db:
            self.db.execute("INSERT OR REPLACE INTO settings VALUES ('next_request',?)", (value,))

    def enqueue_stored(self, *, scope, track_id, source_version, source_hash, source_path, metadata=None):
        """Call ONLY after verified immutable storage commits. No network/analysis here.

        Cloud caller must derive scope and path from its authorized stored object,
        never from a client path. This local hook does not implement cloud uploads.
        """
        if not all(isinstance(v, str) and 0 < len(v) <= 128 for v in (scope, track_id, source_version)) or not re.fullmatch(r"[a-f0-9]{64}", source_hash):
            raise ValueError("invalid_stored_identity")
        path = Path(source_path).resolve()
        if not path.is_file() or not 0 < path.stat().st_size <= 512 * 1024 * 1024:
            raise ValueError("invalid_stored_file")
        metadata = {k: str(v)[:500] for k, v in (metadata or {}).items() if k in {"artist", "albumartist", "album"} and v}
        with self.db:
            self.db.execute("""INSERT INTO jobs(scope,id,version,hash,path,metadata,state) VALUES(?,?,?,?,?,?,'pending')
                ON CONFLICT(scope,id) DO UPDATE SET version=excluded.version,hash=excluded.hash,path=excluded.path,metadata=excluded.metadata,album=NULL,embedded=NULL,state='pending',attempts=0,due=0,error=NULL
                WHERE jobs.version<>excluded.version OR jobs.hash<>excluded.hash""", (scope, track_id, source_version, source_hash, str(path), json.dumps(metadata)))

    def cache(self, key, record, expires=0):
        record = {"contract_version": VERSION, "updated_at": time.time(), **record}
        with self.db:
            self.db.execute("INSERT OR REPLACE INTO albums VALUES (?,?,?)", (key, json.dumps(record), expires))
        return record

    def cached(self, key):
        row = self.db.execute("SELECT * FROM albums WHERE key=?", (key,)).fetchone()
        if not row or (row["expires"] and row["expires"] <= time.time()):
            return None
        record = json.loads(row["record"])
        if record.get("status") == "ready" and any(not (self.root / "images" / record[label]["file"]).is_file() for label in ("cover", "thumbnail")):
            return None
        return record

    @contextlib.contextmanager
    def worker_lock(self):
        with open(self.root / "worker.lock", "a") as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                yield False
                return
            try:
                yield True
            finally:
                fcntl.flock(lock, fcntl.LOCK_UN)

    def work(self, provider=None, offline=False, limit=0):
        provider = provider or MusicBrainzCAA(self)
        completed = 0
        attempted = 0
        with self.worker_lock() as acquired:
            if not acquired:
                return {"busy": True}
            # Extract every pending source first, so a sibling's embedded cover wins.
            for job in self.db.execute("SELECT * FROM jobs WHERE state='pending'").fetchall():
                try:
                    if file_digest(job["path"]) != job["hash"]:
                        raise ValueError("source_hash_mismatch")
                    tags, pictures = read_embedded(job["path"])
                    metadata = {**json.loads(job["metadata"]), **tags}
                    key, eligible = album_key(job["scope"], metadata, job["hash"])
                    embedded = None
                    for raw in pictures:
                        try:
                            embedded = {"status": "ready", "provider": "embedded", "confidence": "encoded", "authority": "encoded_fact", "source_sha256": job["hash"], "match_rule": "embedded_front_v1", **write_images(raw, self.root)}
                            break
                        except (ValueError, OSError, Image.DecompressionBombError):
                            continue
                    if embedded:
                        embedded = {"contract_version": VERSION, "updated_at": time.time(), **embedded}
                        previous = self.cached(key)
                        if previous and (previous.get("reason") == "conflicting_embedded_covers" or (previous.get("provider") == "embedded" and previous["thumbnail"]["sha256"] != embedded["thumbnail"]["sha256"])):
                            self.cache(key, {"status": "ambiguous", "reason": "conflicting_embedded_covers", "confidence": "none"})
                        else:
                            self.cache(key, embedded)
                    with self.db:
                        self.db.execute("UPDATE jobs SET metadata=?,album=?,eligible=?,embedded=?,state='extracted',error=NULL WHERE scope=? AND id=? AND version=?", (json.dumps(metadata), key, eligible, json.dumps(embedded) if embedded else None, job["scope"], job["id"], job["version"]))
                except (OSError, ValueError, mutagen.MutagenError) as error:
                    with self.db:
                        self.db.execute("UPDATE jobs SET state='failed',error=? WHERE scope=? AND id=? AND version=?", (type(error).__name__ + ": " + str(error)[:150], job["scope"], job["id"], job["version"]))
            jobs = self.db.execute("SELECT * FROM jobs WHERE state IN ('extracted','done','retry') AND due<=?", (time.time(),)).fetchall()
            for job in jobs:
                cached = self.cached(job["album"])
                if not cached:
                    if limit and attempted >= limit:
                        break
                    attempted += 1
                    if not job["eligible"]:
                        self.cache(job["album"], {"status": "missing", "reason": "insufficient_metadata", "confidence": "none"}, time.time() + NEGATIVE_TTL)
                    elif offline:
                        continue
                    else:
                        try:
                            record, raw = provider.resolve(json.loads(job["metadata"]))
                            if raw:
                                record.update(write_images(raw, self.root))
                            self.cache(job["album"], record, 0 if record["status"] == "ready" else time.time() + NEGATIVE_TTL)
                        except (ProviderError, ValueError, OSError, Image.DecompressionBombError) as error:
                            attempts = job["attempts"] + 1
                            delay = max(getattr(error, "retry_after", 0), min(86400, 60 * 2 ** min(attempts, 10)))
                            exhausted = attempts >= 6
                            self.cache(job["album"], {"status": "unavailable" if exhausted else "retry", "reason": str(error)[:100], "confidence": "none", "retry_at": None if exhausted else time.time() + delay}, 0 if exhausted else time.time() + delay)
                            with self.db:
                                self.db.execute("UPDATE jobs SET state=?,attempts=?,due=?,error=? WHERE album=?", ('unavailable' if exhausted else 'retry', attempts, time.time() + delay, str(error)[:100], job["album"]))
                            continue
                    completed += 1
                with self.db:
                    self.db.execute("UPDATE jobs SET state='done',error=NULL WHERE scope=? AND id=? AND version=?", (job["scope"], job["id"], job["version"]))
            # Disposable loopback copies only; original sources are never deleted.
            pending_paths = {r[0] for r in self.db.execute("SELECT path FROM jobs WHERE state='pending'")}
            for row in self.db.execute("SELECT path FROM jobs WHERE state<>'pending'"):
                source = Path(row[0])
                if source.parent == self.root.resolve() / "inbox" and str(source) not in pending_paths:
                    source.unlink(missing_ok=True)
        return {"resolved_albums": completed, "attempted_albums": attempted}

    def retry_unavailable(self):
        with self.db:
            self.db.execute("DELETE FROM albums WHERE key IN (SELECT album FROM jobs WHERE state='unavailable')")
            self.db.execute("UPDATE jobs SET state='extracted',due=0,attempts=0,error=NULL WHERE state='unavailable'")

    def manifest(self, scope):
        tracks = {}
        for job in self.db.execute("SELECT * FROM jobs WHERE scope=?", (scope,)):
            record = json.loads(job["embedded"]) if job["embedded"] else self.cached(job["album"])
            record = dict(record or {"status": job["state"], "confidence": "none"})
            if job["state"] == "failed":
                record = {"status": "failed", "reason": job["error"], "confidence": "none"}
            tracks[job["id"]] = {**record, "source_version": job["version"], "source_hash": job["hash"], "album_key": job["album"]}
        return {"contract_version": VERSION, "tracks": tracks}
