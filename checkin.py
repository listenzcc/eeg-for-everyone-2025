"""
File: checkin.py
Author: Chuncheng Zhang
Date: 2025-03-24
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    Check-in all the files.

Functions:
    1. Requirements and constants
    2. Function and class
    3. Play ground
    4. Pending
    5. Pending
"""


# %% ---- 2025-03-24 ------------------------
# Requirements and constants
import pandas as pd
from pathlib import Path
from omegaconf import OmegaConf

from rich import print

from util.logging import logger


# %% ---- 2025-03-24 ------------------------
# Function and class
CONF = OmegaConf.load('config.yaml')


# %% ---- 2025-03-24 ------------------------
# Play ground
storage = {}
[storage.update(e) for e in CONF.dataset.storage]
storage = {k: Path(v) for k, v in storage.items()}

for obj in CONF.dataset.inventory:
    # Going for certain data.
    print('-'*80)
    print(obj.name, obj.file)
    logger.info(f'Check-in inventory: {obj.name}')

    # Get the inventory folder.
    folder = storage[obj.storage].joinpath(obj.subfolder)
    logger.info(f'Inventory folder: {folder}')

    # Find the files.
    files = {}
    [files.update(e) for e in obj.file]
    dfs = []
    for k, v in files.items():
        found = list(folder.rglob(v))
        df = pd.DataFrame()
        df[k] = [e.name for e in found]
        df['path'] = [e.relative_to(folder).parent for e in found]
        df['storage'] = storage[obj.storage]
        df['subfolder'] = obj.subfolder
        dfs.append(df)

    # Merge the files.
    df = dfs[0]
    for j in range(1, len(dfs)):
        df = pd.merge(left=df,
                      right=dfs[j],
                      how='outer',
                      on=['storage', 'subfolder', 'path'])
    table = df[['storage', 'subfolder', 'path']+list(files.keys())]
    for c in ['storage', 'subfolder', 'path']:
        table[c] = table[c].map(lambda e: Path(e).as_posix())
    print(table)

    # Save the table to JSON file.
    dst = Path(f'files/{obj.name}.json')
    dst.parent.mkdir(exist_ok=True)
    table.to_json(dst)
    logger.info(f'Saved json file: {dst}')


# %% ---- 2025-03-24 ------------------------
# Pending

# %% ---- 2025-03-24 ------------------------
# Pending


# %%
