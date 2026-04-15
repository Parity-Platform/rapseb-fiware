#!/usr/bin/env python3
"""Render RAPSEB Grafana-style dashboard panels as PNG images."""

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
IMG_DIR = os.path.join(os.path.dirname(__file__), '..', 'docs')
os.makedirs(IMG_DIR, exist_ok=True)

# Grafana dark theme colors
BG = '#181b1f'
PANEL_BG = '#1f2329'
TEXT = '#d8dee9'
GRID = '#2c3038'
ACCENT = '#73bf69'  # green
ACCENT2 = '#5794f2'  # blue
ACCENT3 = '#ff9830'  # orange
RED = '#f2495c'

plt.rcParams.update({
    'figure.facecolor': BG,
    'axes.facecolor': PANEL_BG,
    'axes.edgecolor': GRID,
    'axes.labelcolor': TEXT,
    'xtick.color': TEXT,
    'ytick.color': TEXT,
    'text.color': TEXT,
    'grid.color': GRID,
    'grid.alpha': 0.4,
    'font.size': 11,
    'font.family': 'sans-serif',
})

sessions = pd.read_csv(os.path.join(DATA_DIR, 'spraying_sessions.csv'))
passes = pd.read_csv(os.path.join(DATA_DIR, 'spray_passes.csv'))
sessions['start_dt'] = pd.to_datetime(sessions['start_time'].str.replace('Z', '', regex=False), format='mixed')
passes['ts'] = pd.to_datetime(passes['timestamp'].str.replace('Z', '', regex=False), format='mixed')

# -- Full dashboard composite --
fig, axes = plt.subplots(2, 2, figsize=(16, 9))
fig.suptitle('RAPSEB Spraying Overview', fontsize=16, fontweight='bold', color=TEXT, y=0.97)

# Panel 1: Coverage per Pass
ax = axes[0, 0]
for sid in sessions['session_id'].unique():
    sp = passes[passes['session_id'] == sid]
    color = RED if sessions[sessions['session_id'] == sid]['status'].values[0] == 'aborted' else ACCENT
    ax.plot(sp['ts'], sp['coverage_pct'], 'o-', color=color, alpha=0.7, markersize=3, linewidth=1.2)
ax.set_ylabel('Coverage %')
ax.set_title('Coverage per Pass', fontsize=12, color=TEXT)
ax.set_ylim(30, 105)
ax.axhline(y=95, color=ACCENT3, linestyle='--', alpha=0.5, linewidth=0.8)
ax.grid(True, alpha=0.3)
ax.tick_params(axis='x', rotation=25, labelsize=8)

# Panel 2: Epoxy Usage per Session
ax = axes[0, 1]
colors = [RED if s == 'aborted' else ACCENT2 for s in sessions['status']]
ax.bar(range(len(sessions)), sessions['total_epoxy_g'], color=colors, alpha=0.85)
ax.set_ylabel('Epoxy (g)')
ax.set_title('Epoxy Usage per Session', fontsize=12, color=TEXT)
ax.set_xlabel('Session #')
ax.set_xticks(range(0, len(sessions), 5))
ax.set_xticklabels([f'{i+1}' for i in range(0, len(sessions), 5)])
ax.grid(True, axis='y', alpha=0.3)

# Panel 3: Passes per Board
ax = axes[1, 0]
colors = [RED if s == 'aborted' else ACCENT for s in sessions['status']]
ax.bar(range(len(sessions)), sessions['total_passes'], color=colors, alpha=0.85)
ax.set_ylabel('Passes')
ax.set_title('Passes Required per Board', fontsize=12, color=TEXT)
ax.set_xlabel('Session #')
ax.set_yticks([1, 2, 3, 4])
ax.set_xticks(range(0, len(sessions), 5))
ax.set_xticklabels([f'{i+1}' for i in range(0, len(sessions), 5)])
ax.grid(True, axis='y', alpha=0.3)

# Panel 4: Session Duration
ax = axes[1, 1]
completed = sessions[sessions['status'] == 'completed']
aborted = sessions[sessions['status'] == 'aborted']
ax.plot(completed['start_dt'], completed['duration_s'], 'o-',
        color=ACCENT2, alpha=0.8, markersize=4, linewidth=1.2, label='Completed')
if len(aborted) > 0:
    ax.plot(aborted['start_dt'], aborted['duration_s'], 'x',
            color=RED, markersize=8, markeredgewidth=2, label='Aborted')
ax.set_ylabel('Duration (s)')
ax.set_title('Session Duration', fontsize=12, color=TEXT)
ax.legend(fontsize=9, facecolor=PANEL_BG, edgecolor=GRID)
ax.grid(True, alpha=0.3)
ax.tick_params(axis='x', rotation=25, labelsize=8)

plt.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig(os.path.join(IMG_DIR, 'dashboard_overview.png'), dpi=150, bbox_inches='tight')
print(f'Saved dashboard_overview.png')

# -- Individual panels for README embedding --
for panel_name, plot_fn in [
    ('coverage_per_pass', lambda ax: (
        [ax.plot(passes[passes['session_id'] == sid]['ts'],
                 passes[passes['session_id'] == sid]['coverage_pct'],
                 'o-', color=ACCENT if sessions[sessions['session_id'] == sid]['status'].values[0] != 'aborted' else RED,
                 alpha=0.7, markersize=3, linewidth=1.2)
         for sid in sessions['session_id'].unique()],
        ax.set_ylabel('Coverage %'), ax.set_title('Coverage per Pass'),
        ax.set_ylim(30, 105), ax.axhline(y=95, color=ACCENT3, linestyle='--', alpha=0.5),
        ax.grid(True, alpha=0.3), ax.tick_params(axis='x', rotation=25, labelsize=8)
    )),
]:
    fig2, ax2 = plt.subplots(figsize=(10, 4))
    plot_fn(ax2)
    fig2.savefig(os.path.join(IMG_DIR, f'{panel_name}.png'), dpi=150, bbox_inches='tight')
    print(f'Saved {panel_name}.png')

plt.close('all')
print('Done.')
