"""
TO-CS-02: EEG Data Loading Module
Loads Chennu et al. 2016 EEGLAB (.set/.fdt) files and maps to 8 ROIs.
"""

import json
import os
import glob
import re
import numpy as np
import mne


def load_roi_mapping(config_path=None):
    """Load ROI mapping from JSON config."""
    if config_path is None:
        config_path = os.path.join(
            os.path.dirname(__file__), '..', 'config', 'roi_mapping.json'
        )
    with open(config_path) as f:
        return json.load(f)


def find_subject_files(data_dir):
    """
    Scan data directory and return a dict:
      {subject_number: [file_path_baseline, file_path_mild, file_path_moderate, file_path_recovery]}

    Files are sorted by condition code (ascending) within each subject.
    Subjects are identified by the XX prefix in 'XX-2010-anest'.
    """
    set_files = sorted(glob.glob(os.path.join(data_dir, '*.set')))

    subjects = {}
    for fpath in set_files:
        fname = os.path.basename(fpath)
        # Extract subject number from start of filename
        match = re.match(r'(\d+)-2010-anest', fname)
        if not match:
            continue
        sub_num = int(match.group(1))
        if sub_num not in subjects:
            subjects[sub_num] = []
        subjects[sub_num].append(fpath)

    # Sort each subject's files by the condition code (last 3 digits before extension)
    for sub_num in subjects:
        subjects[sub_num].sort(
            key=lambda p: int(re.search(r'\.(\d{3})\.set$', os.path.basename(p)).group(1))
        )

    return subjects


def load_eeglab_file(filepath):
    """Load a single EEGLAB .set file, return MNE Raw object."""
    raw = mne.io.read_raw_eeglab(filepath, preload=True, verbose=False)
    return raw


def get_roi_channel_indices(raw, roi_mapping):
    """
    Map ROI definitions to channel indices in the loaded EEG data.

    Returns dict: {roi_name: [list of channel indices]}
    """
    ch_names = raw.ch_names
    ch_name_upper = {ch.upper(): i for i, ch in enumerate(ch_names)}

    roi_indices = {}
    for roi_name, roi_info in roi_mapping['rois'].items():
        indices = []
        for ch in roi_info['channels']:
            ch_up = ch.upper()
            if ch_up in ch_name_upper:
                indices.append(ch_name_upper[ch_up])
            else:
                # Try without 'E' prefix for numbered channels
                for raw_ch in ch_names:
                    if raw_ch.upper() == ch_up or raw_ch.upper() == 'E' + ch_up.lstrip('E'):
                        indices.append(ch_names.index(raw_ch))
                        break
        roi_indices[roi_name] = indices

    return roi_indices


def epoch_data(raw, epoch_length=10.0):
    """
    Create fixed-length epochs (non-overlapping) from continuous data.

    Parameters
    ----------
    raw : mne.io.Raw
        The continuous EEG data.
    epoch_length : float
        Length of each epoch in seconds.

    Returns
    -------
    epochs_data : np.ndarray, shape (n_epochs, n_channels, n_samples)
    """
    sfreq = raw.info['sfreq']
    n_samples_per_epoch = int(epoch_length * sfreq)
    data = raw.get_data()  # (n_channels, n_total_samples)
    n_total = data.shape[1]
    n_epochs = n_total // n_samples_per_epoch

    epochs = np.array([
        data[:, i * n_samples_per_epoch:(i + 1) * n_samples_per_epoch]
        for i in range(n_epochs)
    ])
    return epochs


def get_roi_signals(epochs_data, roi_indices):
    """
    Average channels within each ROI to get ROI-level signals.

    Parameters
    ----------
    epochs_data : np.ndarray, shape (n_epochs, n_channels, n_samples)
    roi_indices : dict, {roi_name: [channel indices]}

    Returns
    -------
    roi_signals : dict, {roi_name: np.ndarray shape (n_epochs, n_samples)}
    """
    roi_signals = {}
    for roi_name, indices in roi_indices.items():
        if len(indices) > 0:
            roi_signals[roi_name] = np.mean(epochs_data[:, indices, :], axis=1)
        else:
            print(f"  WARNING: No channels found for ROI {roi_name}")
            roi_signals[roi_name] = np.zeros((epochs_data.shape[0], epochs_data.shape[2]))
    return roi_signals


def load_subject_all_conditions(subject_files, roi_mapping, epoch_length=10.0,
                                 bandpass_full=(0.5, 45.0), bandpass_deltafree=(4.0, 40.0)):
    """
    Load all conditions for a subject, return ROI signals for each condition
    at two frequency bands.

    Returns
    -------
    results : dict with keys:
        'full': {condition_idx: {roi_name: (n_epochs, n_samples)}}
        'deltafree': {condition_idx: {roi_name: (n_epochs, n_samples)}}
        'sfreq': sampling frequency
        'n_channels': original channel count
    """
    condition_names = ['baseline', 'mild', 'moderate', 'recovery']
    results = {'full': {}, 'deltafree': {}, 'condition_names': condition_names}

    for cond_idx, fpath in enumerate(subject_files):
        cond_name = condition_names[cond_idx] if cond_idx < 4 else f'cond_{cond_idx}'

        # Load raw
        raw = load_eeglab_file(fpath)
        results['sfreq'] = raw.info['sfreq']
        results['n_channels'] = len(raw.ch_names)

        # Get ROI indices
        roi_indices = get_roi_channel_indices(raw, roi_mapping)

        # Full band (0.5-45 Hz)
        raw_full = raw.copy().filter(
            l_freq=bandpass_full[0], h_freq=bandpass_full[1], verbose=False
        )
        epochs_full = epoch_data(raw_full, epoch_length)
        results['full'][cond_name] = get_roi_signals(epochs_full, roi_indices)

        # Delta-free band (4-40 Hz)
        raw_df = raw.copy().filter(
            l_freq=bandpass_deltafree[0], h_freq=bandpass_deltafree[1], verbose=False
        )
        epochs_df = epoch_data(raw_df, epoch_length)
        results['deltafree'][cond_name] = get_roi_signals(epochs_df, roi_indices)

    return results
