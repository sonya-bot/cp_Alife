#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
sys.path.append(os.pardir)  # 親ディレクトリのファイルをインポートするための設定
import numpy as np
import matplotlib.pyplot as plt
# from cp_scl import*

# catalyst_data.npz からデータを読み込み、データを扱いやすいように分離
data = np.load('catalyst_data.npz', allow_pickle=True)
positions_log = data['positions']   # 各記録タイミングごとの触媒座標リスト
distances_log = data['distances']   # 各記録タイミングごとのマンハッタン距離リスト

print(f"{len(distances_log)} steps recorded.")

#距離の値ごとに出現回数をカウント
distances_flattened = distances_log.flatten() # 1次元配列に変換
if distances_flattened.size == 0:
    distances_count = np.array([])
else:
    distances_count = np.bincount(distances_flattened.astype(int)) # 整数型に変換してからbincount

#各距離ごとの出現回数をリストの長さで割って割合を計算
if len(distances_log) > 0 and distances_count.size > 0 :
    distances_ratio  = distances_count / len(distances_log) #
else:
    distances_ratio = np.array([])

#ヒートマップの作成
def plot_catalyst_heatmap_on_ax(ax, positions_log, space_size, num_total_steps):
    all_x_coords, all_y_coords = [], []

    # 全ステップで空チェック
    # if positions_log.size == 0 or all(len(step) == 0 for step in positions_log if isinstance(step, (list, np.ndarray))):
    #     print("警告: 触媒の位置データが空です。ヒートマップは描画できません。")
    #     ax.text(0.5, 0.5, "No position data for heatmap", ha='center', va='center', transform=ax.transAxes)
    #     return

    # 有効な座標を収集
    for step in positions_log:
        for coord in step:
            if len(coord) == 2:
                x, y = coord
                all_x_coords.append(x)
                all_y_coords.append(y)

    if not all_x_coords:
        print("警告: 有効な触媒の座標データが見つかりません。")
        ax.text(0.5, 0.5, "No valid catalyst coordinates", ha='center', va='center', transform=ax.transAxes)
        return


    plt.sca(ax) 
    counts, xedges, yedges, image = plt.hist2d(
        all_x_coords,
        all_y_coords,
        bins=space_size, 
        range=[[0, space_size], [0, space_size]], 
        cmap='Blues', 
    )

    cbar = plt.colorbar(image, ax=ax, label='Frequency (Number of times catalyst present)', fraction=0.046, pad=0.04) 
    ax.set_title(f'Catalyst Position Heatmap\n(Steps: {num_total_steps}, Space: {space_size}x{space_size})') 
    ax.set_xlabel('X Coordinate') 
    ax.set_ylabel('Y Coordinate') 

    tick_positions = np.arange(space_size) + 0.5 
    ax.set_xticks(tick_positions) 
    ax.set_xticklabels(np.arange(space_size)) 
    ax.set_yticks(tick_positions) 
    ax.set_yticklabels(np.arange(space_size)) 

    ax.set_xlim(0, space_size) 
    ax.set_ylim(0, space_size) 

    ax.set_aspect('equal', adjustable='box') 
    ax.grid(True, linestyle=':', linewidth=0.5, color='black', alpha=0.3) 

    (init_x,init_y) = (8,8) # 初期位置の中心座標 (例: 8,8)
    ax.plot(init_x +0.5, init_y+0.5, 'o',color='magenta', markersize=8, label='Initial Catalyst Position') # 初期位置を赤い点で表示
    ax.legend() # 凡例を追加

# // --- START MODIFICATION ---
# // 機能: マンハッタン距離の時系列変化を描画する関数をサブプロット対応で追加
# // 目的: 指定されたAxesオブジェクトに距離の時系列グラフを描画するため
def plot_distance_timeseries_on_ax(ax, distances_log, record_interval):
    if distances_log.size == 0:
        print("警告: 距離データが空です。時系列グラフは描画できません。")
        ax.text(0.5, 0.5, "No distance data", ha='center', va='center', transform=ax.transAxes)
        return

    distances_log = np.atleast_2d(distances_log)
    num_steps, num_catalysts = distances_log.shape
    steps = np.arange(num_steps) * record_interval
    max_dist = 0

    for i in range(num_catalysts):
        dist_data = distances_log[:, i]
        ax.plot(steps, dist_data, label=f'Catalyst {i+1}', linewidth=1.5)
        max_dist = max(max_dist, dist_data.max())

    ax.set_xlabel(f'Simulation Step (every {record_interval})')
    ax.set_ylabel('Manhattan Distance')
    ax.set_title('Manhattan Distance over Time')
    ax.set_xticks(steps[::max(1, num_steps // 10)])
    ax.set_yticks(np.arange(0, int(max_dist) + 2, max(1, int(max_dist) // 10)))
    if num_catalysts > 1:
        ax.legend()
    ax.grid(True, linestyle='--', alpha=0.7)

# // --- END MODIFICATION ---


# // --- START MODIFICATION ---
# // 変更: 3つのグラフを横に並べて表示する処理
# // 目的: マンハッタン距離の分布、ヒートマップ、距離の時系列グラフを1つのウィンドウに表示する

# 3つのサブプロットを1行3列で作成。figsizeで全体のサイズを調整。
fig, axes = plt.subplots(1, 3, figsize=(24, 7)) # 幅をさらに広げる (例: 24インチ)

# --- グラフ1: マンハッタン距離の棒グラフ (左側: axes[0]) ---
ax1 = axes[0] 
if distances_ratio.size > 0: 
    ax1.bar(np.arange(len(distances_ratio)), distances_ratio, color='blue', alpha=0.7) 
    ax1.set_xlabel('Manhattan Distance') 
    ax1.set_ylabel('Probability') 
    ax1.set_title(f'Manhattan Distance Distribution\n(N={len(distances_log)})') 
    ax1.set_xticks(np.arange(len(distances_ratio))) 
    ax1.set_xticklabels(np.arange(len(distances_ratio))) 
    ax1.set_ylim(0, 1) 
    ax1.grid(axis='y', linestyle='--', alpha=0.7) 
else:
    print("マンハッタン距離のデータがないため、分布グラフは描画されません。")
    ax1.text(0.5, 0.5, "No data for Manhattan distance distribution", horizontalalignment='center', verticalalignment='center', transform=ax1.transAxes)


# --- グラフ2: 触媒位置のヒートマップ (中央: axes[1]) ---
ax2 = axes[1] 
SIMULATION_SPACE_SIZE = 16 # from cp_scl.py
plot_catalyst_heatmap_on_ax(ax2, positions_log, SIMULATION_SPACE_SIZE, len(distances_log)) 

# --- グラフ3: マンハッタン距離の時系列変化 (右側: axes[2]) ---
ax3 = axes[2]
RECORD_INTERVAL = 10 # cp_scl.py での記録間隔
# distances_log は (num_steps, num_catalysts) の形状を期待。現状は触媒1つなので (num_steps, 1) または (num_steps,)
# np.arrayに変換して形状を確実にする
distances_log_np = np.array(distances_log)
plot_distance_timeseries_on_ax(ax3, distances_log_np, RECORD_INTERVAL)


# レイアウトの調整と全体の表示
plt.tight_layout(pad=3.0) 
plt.suptitle("Catalyst Behavior Analysis", fontsize=16, y=1.02) 
plt.show() 

# // --- END MODIFICATION ---