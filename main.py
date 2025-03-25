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
import mne
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go

from nicegui import ui
from pathlib import Path
from nilearn import plotting

from checkin import logger, CONF
from util.data import SelectedData, EEGData
import util.plotly_template

# %%

sd = SelectedData()


def read_sensor_positions() -> dict:
    csv_path = Path('asset/MNI/eeg-1010-positions.csv')
    df = pd.read_csv(csv_path, header=0, index_col=None)
    sensor_positions = {}
    for i, se in df.iterrows():
        xyz = (se['X'], se['Y'], se['Z'])
        sensor_positions[se['Name'].upper()] = xyz
    logger.info(
        f'Read known channel positions: {sensor_positions}, file path is {csv_path}')
    return sensor_positions


known_sensor_positions = read_sensor_positions()

# %%
# Root layout
# ----------------------------------------
# ---- Select inventory and data ----
ui.separator()
ui.label('Select inventory & data')
with ui.row():
    ui_select_inventory = ui.select([e.name for e in CONF.dataset.inventory])
    ui_select_data = ui.select([])

# ----------------------------------------
# ---- Details of selected data ----
ui.separator()
ui.label('Data details')
ui_data_detail = ui.table(
    columns=[{'label': 'Name', 'field': 'name', 'required': True},
             {'label': 'Value', 'field': 'value', 'required': True},
             {'label': 'Size', 'field': 'size', 'required': False}],
    rows=[{'name': 'index',
           'value': 'content',
           'size': '? KB'}],
    column_defaults={'align': 'left',
                     'headerClasses': 'uppercase text-primary'})

# ----------------------------------------
# ---- Operations ----
ui.separator()
ui.label('Operations')
ui_analysis_button = ui.button('Overlook')

# %%
# Analysis layout


@ui.page('/overlook')
def routine_analysis():
    eeg_data = EEGData()
    eeg_data.init_from_selected_data(sd)
    print(eeg_data.load_raw())
    eeg_data.reload_montage(eeg_data.standard_montage_name)

    # ----------------------------------------
    # ---- Header bar ----
    with ui.row().classes('w-full'):
        ui.button(icon='home', on_click=lambda: ui.navigate.to('/'))
        ui.label('Working directory:')
        ui.label(sd.get_folder().as_posix())
        ui.space()
        with ui.button(icon='menu'):
            with ui.menu() as menu:
                ui.menu_item('Root', lambda: ui.navigate.to('/'))
                ui.menu_item('Overlook', lambda: ui.navigate.to('/overlook'))
                ui.separator()
                ui.menu_item(
                    'Menu item 2', lambda: ui.notify('Selected item 2'))
                ui.menu_item('Menu item 3 (keep open)',
                             lambda: ui.notify('Selected item 3'), auto_close=False)
                ui.separator()
                ui.menu_item('Close', menu.close)
    ui.separator()

    with ui.row().classes('w-full flex justify-around'):
        # Make the cards layout in flex center
        # ----------------------------------------
        # ---- Sensors plot ----

        with ui.card():
            ui.label('Sensors plot')
            ch_names = eeg_data.raw.ch_names
            found = {k: v for k, v in known_sensor_positions.items()
                     if k in ch_names}
            names = list(found.keys())
            coords = list(found.values())
            view = plotting.view_markers(
                coords, 'black', marker_labels=names, marker_size=5)
            ui.html(view.get_iframe(width=600, height=400))

        # ----------------------------------------
        # ---- Events plot ----
        with ui.card():
            ui.label('Events plot')
            events, event_id = mne.events_from_annotations(eeg_data.raw)
            sfreq = eeg_data.info['sfreq']
            print(events, event_id)
            fig = go.Figure()
            for k, v in event_id.items():
                d = [e for e in events if e[2] == v]
                if len(d) > 0:
                    fig.add_trace(go.Scatter(
                        x=[e[0] / sfreq for e in d],
                        y=[e[2] for e in d],
                        mode='markers',
                        name=f'{k} ({len(d)})'
                    ))
            fig.update_layout(
                width=600,
                height=400,
                xaxis_title='Time (s)',
                yaxis_title='Event ID',
                showlegend=True)
            ui.plotly(fig)
    ui.separator()

    # ----------------------------------------
    # ---- Info card ----
    with ui.card().classes('w-full'):
        ui.label('Info')
        ui.table(
            columns=[{'label': 'Name', 'field': 'name', 'required': True},
                     {'label': 'Content', 'field': 'content', 'required': True}],
            rows=[{'name': k, 'content': str(v)}
                  for k, v in eeg_data.info.items() if v],
            column_defaults={'align': 'left',
                             'headerClasses': 'uppercase text-primary'}
        ).classes('w-full')


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
    folder = sd.get_folder()
    rows = [
        {'name': 'inventory', 'value': sd.inventory_name},
        {'name': 'type', 'value': sd.inventory_type},
    ]
    for k, v in dict(se).items():
        if k in sd.folder_parts:
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
    ui.navigate.to('/overlook')


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
