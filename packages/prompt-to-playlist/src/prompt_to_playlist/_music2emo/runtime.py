"""Offline CPU loading for the audited Music2Emo inference subset."""
import json
from types import SimpleNamespace
import numpy as np
import torch


class HParams:
    @staticmethod
    def load(path):
        import yaml
        return SimpleNamespace(**yaml.safe_load(path.read_text()))


def load_btc(path):
    # This official legacy checkpoint includes two NumPy normalization scalars.
    # Allow only those concrete numeric constructors, never arbitrary unpickling.
    with torch.serialization.safe_globals([
        (np.core.multiarray.scalar, 'numpy.core.multiarray.scalar'),
        np.dtype, type(np.dtype('float64')), type(np.dtype('float32')),
    ]):
        return torch.load(path, map_location='cpu', weights_only=True)


class MERTFeatures:
    def __init__(self, assets):
        from transformers import HubertConfig, HubertModel, Wav2Vec2FeatureExtractor
        path = assets / 'mert'
        config = json.loads((path / 'config.json').read_text())
        # This pinned MERT checkpoint is exactly the plain HuBERT architecture:
        # no CQT projection, no deepnorm/custom attention. Refuse future variants.
        if config['feature_extractor_cqt'] or config['deepnorm'] or config['attention_relax'] != -1:
            raise ValueError('Unsupported MERT architecture; do not substitute a HuBERT model')
        self.model, info = HubertModel.from_pretrained(
            path, config=HubertConfig(**config), local_files_only=True,
            output_loading_info=True, attn_implementation='eager',
        )
        if any(info.get(k) for k in ('missing_keys', 'unexpected_keys', 'mismatched_keys', 'error_msgs')):
            raise ValueError(f'MERT checkpoint did not load exactly: {info}')
        self.model.eval()
        self.processor = Wav2Vec2FeatureExtractor.from_pretrained(path, local_files_only=True)

    def extract_features_from_segment(self, segment, sample_rate, save_path):
        inputs = self.processor(segment.float(), sampling_rate=sample_rate, return_tensors='pt')
        with torch.inference_mode():
            hidden = self.model(**inputs, output_hidden_states=True).hidden_states
            # Upstream drops embedding layer, then selects indices 5 and 6.
            layers = torch.stack([h.mean(dim=1) for h in hidden[1:]], dim=1)
        np.save(save_path, layers.numpy(), allow_pickle=False)


def create_runtime(assets):
    from .head import FeedforwardModelMTAttnCK
    from .preprocess import Preprocessor
    runtime = Preprocessor()
    runtime.assets = assets
    runtime.device = torch.device('cpu')
    runtime.feature_extractor = MERTFeatures(assets)
    runtime.music2emo_model = FeedforwardModelMTAttnCK(1536, 56, 2)
    checkpoint = torch.load(assets / 'J_all.ckpt', map_location='cpu', weights_only=True)
    state = checkpoint['state_dict']
    training_only = {f'loss_fn_classification{suffix}.{name}' for suffix in ('', '_eval') for name in ('weight', 'pos_weight')}
    if {k for k in state if not k.startswith('model.')} != training_only:
        raise ValueError('Unexpected Music2Emo state keys')
    runtime.music2emo_model.load_state_dict({k.removeprefix('model.'): v for k, v in state.items() if k not in training_only}, strict=True)
    runtime.music2emo_model.eval()
    return runtime
