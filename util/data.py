"""
File: data.py
Author: Chuncheng Zhang
Date: 2025-03-24
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    Data types and options.

Functions:
    1. Requirements and constants
    2. Function and class
    3. Play ground
    4. Pending
    5. Pending
"""


# %% ---- 2025-03-24 ------------------------
# Requirements and constants
import mne
import pandas as pd

from pathlib import Path
from .logging import logger


# %% ---- 2025-03-24 ------------------------
# Function and class

class SelectedData:
    inventory_name: str
    inventory_type: str
    df: pd.DataFrame
    index: int
    folder_parts = ['storage', 'subfolder', 'path']

    def get_folder(self):
        '''
        Get the working directory.
        '''
        se = self.df.loc[self.index]
        return Path(*[se[e] for e in self.folder_parts])


class EEGData:
    # Files
    data_file_path: Path
    event_file_path: Path

    # Objects
    raw = None
    info: mne.Info
    annotations: mne.Annotations

    # Montage
    montage = None
    standard_montage_name = 'standard_1020'

    def init_from_selected_data(self, sd: SelectedData):
        '''
        Initialize from SelectedData object.

        :param sd: SelectedData object.
        '''
        se = sd.df.loc[sd.index]
        folder = sd.get_folder()
        data_path = folder.joinpath(se['data'])
        event_path = folder.joinpath(se['event'])
        self.init_from_path(data_path, event_path)
        logger.info(f'Initialized from SelectedData: {sd}')
        return

    def init_from_path(self, data_path: Path, event_path: Path):
        '''
        Initialize from file paths.

        :param data_path: Path to the data file.
        :param event_path: Path to the event file.
        '''
        self.data_file_path = data_path
        self.event_file_path = event_path
        logger.info(f'Initialized from paths: {data_path}, {event_path}')
        return

    def load_raw(self):
        '''
        Load raw

        :return raw: the raw object.
        :return annotations: the annotations.
        :return info: the info dictionary.
        '''
        # Read event from self.event_path as .bdf file
        annotations = mne.read_annotations(self.event_file_path)

        # Read data from self.data_path as .bdf file
        raw = mne.io.read_raw_bdf(self.data_file_path, preload=False)
        raw.set_annotations(annotations)

        # Get info
        info = raw.info

        self.raw = raw
        self.info = info
        self.annotations = annotations

        logger.debug(
            f'Loaded raw: {raw}, info: {info} and annotations: {annotations}')

        return raw, annotations, info

    def reload_montage(self, standard_montage_name: str, rename_channels: dict = None):
        '''
        Reload the montage to self.raw.

        :param standard_montage_name str: name of the standard montage.
        :param rename_channels dict: change names of channels.

        :return self.raw: the updated raw object.
        '''
        montage = mne.channels.make_standard_montage(standard_montage_name)
        logger.debug(f'Using standard montage: {standard_montage_name}')

        # Rename standard montage's channel names
        if rename_channels is not None:
            montage.rename_channels(rename_channels)
            logger.debug(
                f'Renamed standard montage channel names: {rename_channels}')

        # Rename the channel names into upper case
        self.raw.rename_channels({n: n.upper() for n in self.raw.ch_names})
        montage.rename_channels({n: n.upper() for n in montage.ch_names})

        # Set the montage to the raw
        self.raw.set_montage(montage, on_missing='warn')
        self.montage = montage

        return self.raw

# %% ---- 2025-03-24 ------------------------
# Play ground


# %% ---- 2025-03-24 ------------------------
# Pending


# %% ---- 2025-03-24 ------------------------
# Pending
