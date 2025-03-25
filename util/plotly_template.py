"""
File: plotly_template.py
Author: Chuncheng Zhang
Date: 2025-03-25
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    Plotly template.

Functions:
    1. Requirements and constants
    2. Function and class
    3. Play ground
    4. Pending
    5. Pending
"""


# %% ---- 2025-03-25 ------------------------
# Requirements and constants
import plotly.io as pio
import plotly.graph_objects as go


# %% ---- 2025-03-25 ------------------------
# Function and class


# %% ---- 2025-03-25 ------------------------
# Play ground
pio.templates['custom'] = go.layout.Template(
    layout={
        'margin_t': 10
    },
    layout_annotations=[
        dict(
            name="watermark",
            text="脑机接口专项",
            textangle=-30,
            opacity=0.1,
            font=dict(color="black", size=80),
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
    ]
)
pio.templates.default = 'custom+plotly_white'


# %% ---- 2025-03-25 ------------------------
# Pending


# %% ---- 2025-03-25 ------------------------
# Pending
