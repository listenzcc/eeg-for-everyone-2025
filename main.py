"""
File: main.py
Author: Chuncheng Zhang
Date: 2025-03-24
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    Main entry point for the project.

Functions:
    1. Requirements and constants
    2. Function and class
    3. Play ground
    4. Pending
    5. Pending
"""


# %% ---- 2025-03-24 ------------------------
# Requirements and constants
import os
from nicegui import ui
from pathlib import Path

import pandas as pd

from checkin import logger, CONF


class SelectedData:
    inventory_name: str
    inventory_type: str
    df: pd.DataFrame
    index: int


sd = SelectedData()

# %%
# Layout
# Root layout
ui.separator()
ui.label('Select inventory & data')
with ui.row():
    ui_select_inventory = ui.select([e.name for e in CONF.dataset.inventory])
    ui_select_data = ui.select([])

ui.separator()
ui.label('Data details')
ui_data_detail = ui.table(
    columns=[
        {'label': 'Name', 'field': 'name', 'required': True},
        {'label': 'Value', 'field': 'value', 'required': True},
        {'label': 'Size', 'field': 'size', 'required': False}
    ],
    rows=[
        {'name': 'index',
         'value': 'content',
         'size': '? kB'
         }
    ])

ui.separator()
ui.label('Operations')
ui_analysis_button = ui.button('Analysis')

# Analysis layout


@ui.page('/analysis')
def routine_analysis():
    ui.label('Analysis')

# %% ---- 2025-03-24 ------------------------
# Function and class


def on_value_change_select_inventory(value: str):
    '''
    Select inventory.

    :param value str: The inventory name.
    '''
    logger.info(f'Selected inventory: {value}')
    df = pd.read_json(f'files/{value}.json')

    # Update the selected data df immediately.
    sd.df = df
    sd.inventory_name = value
    sd.inventory_type = [
        e.type for e in CONF.dataset.inventory if e.name == value][0]

    # Make the options.
    n = len(df)
    options = {i: ': '.join([
        f'{i+1} | {n}',
        Path(se['storage'], se['subfolder'], se['path']).as_posix()])
        for i, se in df.iterrows()}

    # Reset the selected data as 0
    ui_select_data.set_options(options, value=0)
    on_value_change_select_data(0)
    return


def on_value_change_select_data(value: int):
    '''
    Select data recording.
    The data recording is from sd.df.

    :param value int: The selected data index.
    '''
    # Select the data recording.
    se = sd.df.loc[value]
    sd.index = value
    logger.info(f'Selected data: {se}')
    ui.notify(se)

    # Parse folder
    folder_parts = ['storage', 'subfolder', 'path']
    folder = Path(*[se[e] for e in folder_parts])
    rows = [
        {'name': 'inventory', 'value': sd.inventory_name},
        {'name': 'type', 'value': sd.inventory_type},
    ]
    for k, v in dict(se).items():
        if k in folder_parts:
            rows.append({'name': k, 'value': v})
        else:
            p = folder.joinpath(se[k])
            rows.append(
                {'name': k, 'value': v, 'size': '{} KB'.format(int(0.5+os.path.getsize(p)/1024))})
    ui_data_detail.update_rows(rows)
    return


def analysis():
    message = '\n'.join([str(e) for e in
                         [sd.inventory_name, sd.inventory_type, sd.df.loc[sd.index]]])
    ui.notify(message)
    print(message)
    ui.navigate.to('/analysis')


ui_select_inventory.set_value(ui_select_inventory.options[0])
on_value_change_select_inventory(ui_select_inventory.value)

ui_select_inventory.on_value_change(
    lambda event: on_value_change_select_inventory(event.value))

ui_select_data.on_value_change(
    lambda event: on_value_change_select_data(event.value))

ui_analysis_button.on_click(lambda event: analysis())


# %% ---- 2025-03-24 ------------------------
# Play ground


# %% ---- 2025-03-24 ------------------------
# Pending
ui.run(reload=True)


# %% ---- 2025-03-24 ------------------------
# Pending
