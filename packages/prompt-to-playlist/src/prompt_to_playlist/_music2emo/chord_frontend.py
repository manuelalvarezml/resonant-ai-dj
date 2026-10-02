# Adapted from Music2Emotion, MIT.
import numpy as np
import librosa
import mir_eval
import torch
import os
idx2chord = ['C', 'C:min', 'C#', 'C#:min', 'D', 'D:min', 'D#', 'D#:min', 'E', 'E:min', 'F', 'F:min', 'F#', 'F#:min', 'G', 'G:min', 'G#', 'G#:min', 'A', 'A:min', 'A#', 'A#:min', 'B', 'B:min', 'N']
root_list = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
quality_list = ['min', 'maj', 'dim', 'aug', 'min6', 'maj6', 'min7', 'minmaj7', 'maj7', '7', 'dim7', 'hdim7', 'sus2', 'sus4']

def idx2voca_chord():
    idx2voca_chord = {}
    idx2voca_chord[169] = 'N'
    idx2voca_chord[168] = 'X'
    for i in range(168):
        root = i // 14
        root = root_list[root]
        quality = i % 14
        quality = quality_list[quality]
        if i % 14 != 1:
            chord = root + ':' + quality
        else:
            chord = root
        idx2voca_chord[i] = chord
    return idx2voca_chord

def audio_file_to_features(audio_file, config):
    original_wav, sr = librosa.load(audio_file, sr=config.mp3['song_hz'], mono=True)
    song_length_second = len(original_wav) / sr
    inst_samples = int(sr * config.mp3['inst_len'])
    currunt_sec_hz = 0
    feature = None
    while currunt_sec_hz + inst_samples <= len(original_wav):
        start_idx = int(currunt_sec_hz)
        end_idx = int(currunt_sec_hz + inst_samples)
        tmp = librosa.cqt(original_wav[start_idx:end_idx], sr=sr, n_bins=config.feature['n_bins'], bins_per_octave=config.feature['bins_per_octave'], hop_length=config.feature['hop_length'])
        feature = tmp if feature is None else np.concatenate((feature, tmp), axis=1)
        currunt_sec_hz = end_idx
    if currunt_sec_hz < len(original_wav):
        tmp = librosa.cqt(original_wav[currunt_sec_hz:], sr=sr, n_bins=config.feature['n_bins'], bins_per_octave=config.feature['bins_per_octave'], hop_length=config.feature['hop_length'])
        feature = tmp if feature is None else np.concatenate((feature, tmp), axis=1)
    feature = np.log(np.abs(feature) + 1e-06)
    feature_per_second = config.mp3['inst_len'] / config.model['timestep']
    return (feature, feature_per_second, song_length_second)
