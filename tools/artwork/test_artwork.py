import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock
import wave

from mutagen.wave import WAVE
from mutagen.id3 import APIC, TALB, TPE1, TPE2
from PIL import Image
from artwork import Store, MusicBrainzCAA, ProviderError, album_key, file_digest, normalized, read_embedded, retry_delay, safe_provider_url, write_images

GROUP = "12345678-1234-1234-1234-123456789012"
OTHER = "12345678-1234-1234-1234-123456789013"

def picture(color="red"):
    out = io.BytesIO()
    Image.new("RGB", (800, 600), color).save(out, "PNG")
    return out.getvalue()


class ArtworkTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.store = Store(self.root / "cache")

    def tearDown(self):
        self.store.db.close()
        self.temp.cleanup()

    def source(self, name="song", cover=None, artist="Artist", album="Album", kind=3):
        path = self.root / (name + ".wav")
        with wave.open(str(path), "wb") as audio:
            audio.setparams((1, 2, 8000, 0, "NONE", "not compressed"))
            audio.writeframes(b"\0\0" * 800)
        audio = WAVE(path)
        audio.add_tags()
        audio.tags.add(TPE1(encoding=3, text=artist))
        audio.tags.add(TALB(encoding=3, text=album))
        if cover:
            audio.tags.add(APIC(encoding=3, mime="image/png", type=kind, data=cover))
        audio.save()
        return path

    def enqueue(self, source, id="track", version="v1", scope="default"):
        self.store.enqueue_stored(scope=scope, track_id=id, source_version=version, source_hash=file_digest(source), source_path=source)

    def test_embedded_precedes_provider_and_preserves_source(self):
        path = self.source(cover=picture())
        before = path.read_bytes()
        self.enqueue(path)
        provider = Mock()
        self.store.work(provider)
        provider.resolve.assert_not_called()
        record = self.store.manifest("default")["tracks"]["track"]
        self.assertEqual(record["provider"], "embedded")
        self.assertEqual(record["cover"]["width"], 500)
        self.assertEqual(record["cover"]["height"], 375)
        self.assertEqual(record["thumbnail"]["width"], 96)
        self.assertEqual(before, path.read_bytes())

    def test_sibling_embedded_cover_wins_before_network_and_is_reused(self):
        self.enqueue(self.source("no-art"), "one")
        self.enqueue(self.source("with-art", picture()), "two")
        provider = Mock()
        self.store.work(provider)
        provider.resolve.assert_not_called()
        rows = self.store.manifest("default")["tracks"]
        self.assertEqual(rows["one"]["thumbnail"], rows["two"]["thumbnail"])

    def test_conflicting_embedded_covers_keep_each_original_but_dont_guess_for_sibling(self):
        self.enqueue(self.source("one", picture("red")), "one")
        self.enqueue(self.source("two", picture("blue")), "two")
        self.enqueue(self.source("three"), "three")
        provider = Mock()
        self.store.work(provider)
        rows = self.store.manifest("default")["tracks"]
        self.assertEqual(rows["one"]["status"], "ready")
        self.assertEqual(rows["two"]["status"], "ready")
        self.assertEqual(rows["three"]["status"], "ambiguous")
        self.assertNotEqual(rows["one"]["thumbnail"], rows["two"]["thumbnail"])
        provider.resolve.assert_not_called()

    def test_negative_cache_and_duplicate_album_resolution_survive_restart(self):
        path = self.source()
        self.enqueue(path, "one")
        self.enqueue(path, "two")
        provider = Mock()
        provider.resolve.return_value = ({"status": "missing", "confidence": "none"}, None)
        self.store.work(provider)
        self.store.db.close()
        self.store = Store(self.root / "cache")
        self.enqueue(path, "three")
        self.store.work(provider)
        self.assertEqual(provider.resolve.call_count, 1)

    def test_unavailable_provider_retries_later_without_negative_poisoning(self):
        self.enqueue(self.source(), "one")
        self.enqueue(self.source("two"), "two")
        provider = Mock()
        provider.resolve.side_effect = ProviderError("provider_http_429", 900)
        self.store.work(provider)
        self.store.work(provider)
        self.assertEqual(provider.resolve.call_count, 1)
        self.assertEqual(self.store.manifest("default")["tracks"]["one"]["status"], "retry")
        with self.store.db:
            self.store.db.execute("UPDATE albums SET expires=1")
            self.store.db.execute("UPDATE jobs SET due=0")
        provider.resolve.side_effect = None
        provider.resolve.return_value = ({"status": "ready", "provider": "fake"}, picture())
        self.store.work(provider)
        self.assertEqual(self.store.manifest("default")["tracks"]["one"]["status"], "ready")

    def test_retry_budget_exhaustion_is_explicitly_resumable(self):
        self.enqueue(self.source())
        provider = Mock()
        provider.resolve.side_effect = ProviderError("down")
        for _ in range(6):
            self.store.work(provider)
            with self.store.db:
                self.store.db.execute("UPDATE albums SET expires=1 WHERE expires>0")
                self.store.db.execute("UPDATE jobs SET due=0")
        self.store.work(provider)
        self.assertEqual(provider.resolve.call_count, 6)
        self.assertEqual(self.store.manifest("default")["tracks"]["track"]["status"], "unavailable")
        self.store.retry_unavailable()
        self.store.work(provider)
        self.assertEqual(provider.resolve.call_count, 7)

    def test_missing_metadata_never_searches_and_unknown_albums_dont_collide(self):
        self.enqueue(self.source(artist="", album=""))
        provider = Mock()
        self.store.work(provider)
        provider.resolve.assert_not_called()
        self.assertNotEqual(album_key("a", {}, "1")[0], album_key("a", {}, "2")[0])
        self.assertFalse(album_key("a", {"artist": "Various Artists", "album": "Hits"}, "1")[1])

    def test_source_mismatch_fails_closed(self):
        path = self.source()
        self.enqueue(path)
        path.write_bytes(b"changed")
        provider = Mock()
        self.store.work(provider)
        provider.resolve.assert_not_called()
        self.assertEqual(self.store.manifest("default")["tracks"]["track"]["status"], "failed")

    def test_replacement_does_not_serve_old_cover_and_scopes_are_separate(self):
        self.enqueue(self.source("one", picture()))
        self.store.work(offline=True)
        self.enqueue(self.source("two", None, album="Other"), version="v2")
        record = self.store.manifest("default")["tracks"]["track"]
        self.assertNotIn("thumbnail", record)
        self.assertEqual(record["source_version"], "v2")
        self.assertEqual(self.store.manifest("someone-else")["tracks"], {})

    def test_album_artist_and_back_only(self):
        path = self.source(cover=picture(), kind=4)
        audio = WAVE(path)
        audio.tags.add(TPE2(encoding=3, text="Album artist"))
        audio.save()
        tags, images = read_embedded(path)
        self.assertEqual(tags["albumartist"], "Album artist")
        self.assertEqual(images, [])

    def test_invalid_image_and_oversize_are_rejected(self):
        with self.assertRaises(OSError):
            write_images(b"not an image", self.root)
        with self.assertRaises(ValueError):
            write_images(b"x" * (12 * 1024 * 1024 + 1), self.root)

    def test_embedded_corrupt_falls_back_without_breaking_job(self):
        self.enqueue(self.source(cover=b"not-an-image"))
        provider = Mock()
        provider.resolve.return_value = ({"status": "missing"}, None)
        self.store.work(provider)
        provider.resolve.assert_called_once()

    def test_lock_prevents_duplicate_workers(self):
        self.enqueue(self.source())
        other = Store(self.root / "cache")
        try:
            with self.store.worker_lock() as locked:
                self.assertTrue(locked)
                self.assertEqual(other.work(), {"busy": True})
        finally:
            other.db.close()

    def test_offline_does_not_create_permanent_negative(self):
        self.enqueue(self.source())
        self.store.work(offline=True)
        self.assertEqual(self.store.manifest("default")["tracks"]["track"]["status"], "extracted")

    def test_normalization_is_conservative(self):
        self.assertEqual(normalized(" ÉTÉ  "), normalized("E\u0301te\u0301"))
        self.assertNotEqual(normalized("Album (Remastered)"), normalized("Album"))
        self.assertNotEqual(normalized("AC/DC"), normalized("ACDC"))

    def provider(self, groups, count=None, fronts=None):
        provider = MusicBrainzCAA(self.store)
        provider.get = Mock(side_effect=[{"count": len(groups) if count is None else count, "release-groups": groups}, {"release": "https://musicbrainz.org/release/" + OTHER, "images": fronts if fronts is not None else [{"front": True, "approved": True, "id": "123", "thumbnails": {"500": "https://coverartarchive.org/release/" + OTHER + "/123-500.jpg"}}]}, picture()])
        return provider

    def group(self, id=GROUP, artist="Artist", title="Album"):
        return {"id": id, "title": title, "artist-credit": [{"name": artist}]}

    def test_unique_exact_provider_match_records_provenance(self):
        provider = self.provider([self.group(), self.group(OTHER, title="Album (Deluxe)")])
        record, image = provider.resolve({"artist": "Artist", "album": "Album"})
        self.assertEqual(record["status"], "ready")
        self.assertEqual(record["confidence"], "high")
        self.assertEqual(record["release_group"], GROUP)
        self.assertEqual(image, picture())
        self.assertIn("coverartarchive.org", provider.get.call_args_list[1].args[0])

    def test_ambiguous_missing_and_truncated_searches_do_not_download(self):
        for groups, count, status in (([self.group(), self.group(OTHER)], 2, "ambiguous"), ([self.group(artist="Other")], 1, "missing"), ([self.group()], 101, "ambiguous")):
            provider = self.provider(groups, count)
            record, image = provider.resolve({"artist": "Artist", "album": "Album"})
            self.assertEqual(record["status"], status)
            self.assertIsNone(image)
            self.assertEqual(provider.get.call_count, 1)

    def test_unapproved_or_back_caa_art_is_not_used(self):
        provider = self.provider([self.group()], fronts=[{"front": True, "approved": False}])
        self.assertEqual(provider.resolve({"artist": "Artist", "album": "Album"})[0]["status"], "missing")
        self.assertEqual(provider.get.call_count, 2)

    def test_provider_urls_and_retry_after(self):
        for url in ("http://localhost/", "https://archive.org.evil.test/x", "https://evil.test/", "file:///etc/passwd", "https://archive.org:8443/x"):
            with self.assertRaises(ProviderError):
                safe_provider_url(url)
        self.assertEqual(safe_provider_url("http://ia800000.us.archive.org/image.jpg"), "https://ia800000.us.archive.org/image.jpg")
        self.assertEqual(retry_delay("600"), 600)
        self.assertEqual(retry_delay("Thu, 01 Jan 1970 00:02:00 GMT", now=60), 60)
        self.assertEqual(retry_delay("junk"), 0)

    def test_malformed_provider_payloads_fail_as_retryable_errors(self):
        for response in ([], {"release-groups": [], "count": "many"}, {"release-groups": ["bad"], "count": 1}):
            provider = MusicBrainzCAA(self.store)
            provider.get = Mock(return_value=response)
            with self.assertRaises(ProviderError):
                provider.resolve({"artist": "Artist", "album": "Album"})

    def test_work_limit_includes_failed_album_attempts(self):
        self.enqueue(self.source("one", album="One"), "one")
        self.enqueue(self.source("two", album="Two"), "two")
        provider = Mock()
        provider.resolve.side_effect = ProviderError("down")
        self.store.work(provider, limit=1)
        self.assertEqual(provider.resolve.call_count, 1)

if __name__ == "__main__":
    unittest.main()
