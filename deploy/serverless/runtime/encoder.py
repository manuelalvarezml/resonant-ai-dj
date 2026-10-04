"""Warm, text-only MuQ adapter using the original embedding/cache implementation."""
import hashlib
import json
from pathlib import Path

from prompt_to_playlist import semantic_audio
from prompt_to_playlist.models import SemanticQuery
from .model_loader import load_packaged_model


class WarmEncoder:
    def __init__(self, model_dir, loader=None):
        self.model_dir = Path(model_dir)
        self.encoder_id = semantic_audio.identity(self.model_dir)
        self.loader = loader or load_packaged_model
        self.model = None
        self.loads = 0

    def __call__(self, **kwargs):
        # text_embeddings invokes this only on a cache miss, after the job claim.
        if self.model is None:
            self.model = self.loader(self.model_dir)
            self.loads += 1
        return self.model(**kwargs)

    def embeddings(self, texts, cache_dir, objects=None):
        if not isinstance(texts, list) or not 1 <= len(texts) <= 4:
            raise ValueError('Expected one to four descriptions')
        cache_dir = Path(cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)
        keys = []
        for text in texts:
            if not isinstance(text, str) or not text.strip() or len(text) > 500:
                raise ValueError('Invalid semantic description')
            key = hashlib.sha256((self.encoder_id + '\n' + text).encode()).hexdigest()
            file = cache_dir / (key + '.json')
            remote_key = 'text-cache/' + key + '.json'
            if objects is not None and not file.exists():
                cached = objects.optional_json(remote_key, 65536)
                if cached is not None:
                    if cached.get('encoder') != self.encoder_id or cached.get('text') != text:
                        raise ValueError('Incompatible durable text cache')
                    semantic_audio.normalized(cached['embedding'])
                    file.write_text(json.dumps(cached, allow_nan=False))
            keys.append((file, remote_key))
        # Original sentence-by-sentence forward passes, precision and normalization.
        result = semantic_audio.text_embeddings(texts, model=self, model_dir=self.model_dir,
                                               cache_dir=cache_dir)
        if objects is not None:
            for file, key in keys:
                objects.put_json(key, json.loads(file.read_text()))
        return {'encoder_id': self.encoder_id, 'embeddings': result}

    def query_encoder(self, cache_dir, objects=None):
        from prompt_to_playlist.search import search_tracks

        def encode(query, catalog, vocabulary):
            candidates = set(search_tracks(catalog, query.model_copy(update={'semantic': None}),
                                           vocabulary, ranking_version='maest-intent-v1').eligible_track_ids)
            tracks = [track for track in catalog.tracks if track.track_id in candidates]
            if len(tracks) < 2:
                return query, []
            try:
                if any(track.semantic_audio is None
                       or track.semantic_audio.encoder_id != self.encoder_id
                       or track.semantic_audio.sampling_policy != semantic_audio.POLICY for track in tracks):
                    return query, ['Upgrade analysis for all eligible tracks to enable semantic ranking.']
                texts = [query.semantic.description, *query.semantic.avoid]
                result = self.embeddings(texts, cache_dir, objects)
                semantic = SemanticQuery(description=texts[0], avoid=texts[1:], **result)
                return query.model_copy(update={'semantic': semantic}), []
            except (ValueError, OSError):
                return query, ['Semantic text encoding unavailable; structured ranking retained.']
        return encode
