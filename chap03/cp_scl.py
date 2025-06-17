#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
sys.path.append(os.pardir)  # 親ディレクトリのファイルをインポートするための設定
import numpy as np
from alifebook_lib.visualizers import SCLVisualizer
from cp_scl_interaction_functions import *
"""
データの取得、計算を関数化して呼び出し
"""
from cp_scl_datas import get_catalyst_positions, get_catalyst_manhattan_distances
import csv



# visualizerの初期化 (Appendix参照)
# visualizer = SCLVisualizer()
VISUALIZE = False  # 可視化を行うかどうか

SPACE_SIZE = 16

# 初期化設定に関するパラメタ
INITIAL_SUBSTRATE_DENSITY = 0.8
INITIAL_CATALYST_POSITIONS = [(8,8)]

"""
実験2:触媒の数を2つに増やす
"""
# INITIAL_CATALYST_POSITIONS = [(4,4), (12,12)] # 実験1_a:触媒の数を2つに増やす(ある程度離す)
# INITIAL_CATALYST_POSITIONS = [(7,7), (9,9)] # 実験1_b:触媒の数を2つに増やす(隣り合わせ)
INITIAL_BONDED_LINK_POSITIONS = [
    (5,6,6,5),    (6,5,7,5),   (7,5,8,5),  (8,5,9,5),  (9,5,10,5),
    (10,5,11,6),  (11,6,11,7), (11,7,11,8),(11,8,11,9),(11,9,11,10),
    (11,10,10,11),(10,11,9,11),(9,11,8,11),(8,11,7,11),(7,11,6,11),
    (6,11,5,10),  (5,10,5,9),  (5,9,5,8),  (5,8,5,7),  (5,7,5,6)]

# モデルのパラメタ
# 各分子の移動しやすさ
MOBILITY_FACTOR = {
    'HOLE':           0.1,
    'SUBSTRATE':      0.1,
    'CATALYST':       0.0001,
    'LINK':           0.05,
    'LINK_SUBSTRATE': 0.05,}
PRODUCTION_PROBABILITY             = 0.95
DISINTEGRATION_PROBABILITY         = 0.0005
BONDING_CHAIN_INITIATE_PROBABILITY = 0.1
BONDING_CHAIN_EXTEND_PROBABILITY   = 0.6
BONDING_CHAIN_SPLICE_PROBABILITY   = 0.9
BOND_DECAY_PROBABILITY             = 0.0005
ABSORPTION_PROBABILITY             = 0.5
EMISSION_PROBABILITY               = 0.5

# 初期化
particles = np.empty((SPACE_SIZE, SPACE_SIZE), dtype=object)
# INITIAL_SUBSTRATE_DENSITYに従って、SUBSTRATEとHOLEを配置する。
for x in range(SPACE_SIZE):
    for y in range(SPACE_SIZE):
        if evaluate_probability(INITIAL_SUBSTRATE_DENSITY):
            p = {'type': 'SUBSTRATE', 'disintegrating_flag': False, 'bonds': []}
        else:
            p = {'type': 'HOLE', 'disintegrating_flag': False, 'bonds': []}
        particles[x,y] = p
# INITIAL_CATALYST_POSITIONSにCATALYSTを配置する。
for x, y in INITIAL_CATALYST_POSITIONS:
    particles[x, y]['type'] = 'CATALYST'

"""
実験1:膜がある状態からスタートする
"""

# 膜がある状態からスタートするには、コメントアウトしてください
for x0, y0, x1, y1 in INITIAL_BONDED_LINK_POSITIONS:
    particles[x0, y0]['type'] = 'LINK'
    particles[x0, y0]['bonds'].append((x1, y1))
    particles[x1, y1]['bonds'].append((x0, y0))


"""
触媒の位置座標の取得(ステップ数の定義)
"""
# ---- ここから追記 ----
def catalyst_position_history():
        
    VISUALIZE = False
    
    if VISUALIZE:
        visualizer = SCLVisualizer()
    else:
        # 描画しない場合は、visualizerをNone(空)にしておく
        visualizer = None

    catalyst_positions = []  # 触媒の座標履歴リスト
    catalyst_distances = []  # 触媒の初期位置からの距離履歴リスト
    RECORD_INTERVAL = 10    # 何ステップごとに記録するか
    step = 0
    max_steps = 10000
    # 初期触媒位置を保存（複数触媒対応）
    initial_catalyst_positions = list(INITIAL_CATALYST_POSITIONS)
# ---- ここまで追記 ----

    while step < max_steps:
        # 移動
        moved = np.full(particles.shape, False, dtype=bool)
        for x in range(SPACE_SIZE):
            for y in range(SPACE_SIZE):
                p = particles[x,y]
                n_x, n_y = get_random_neumann_neighborhood(x, y, SPACE_SIZE)
                n_p = particles[n_x, n_y]
                mobility_factor = np.sqrt(MOBILITY_FACTOR[p['type']] * MOBILITY_FACTOR[n_p['type']])
                if not moved[x, y] and not moved[n_x, n_y] and \
                len(p['bonds']) == 0 and len(n_p['bonds']) == 0 and \
                evaluate_probability(mobility_factor):
                        particles[x,y], particles[n_x,n_y] = n_p, p
                        moved[x, y] = moved[n_x, n_y] = True
        # 反応
        for x in range(SPACE_SIZE):
            for y in range(SPACE_SIZE):
                production(particles, x, y, PRODUCTION_PROBABILITY)
                disintegration(particles, x, y, DISINTEGRATION_PROBABILITY)
                bonding(particles, x, y, BONDING_CHAIN_INITIATE_PROBABILITY,
                                        BONDING_CHAIN_SPLICE_PROBABILITY,
                                        BONDING_CHAIN_EXTEND_PROBABILITY)
                bond_decay(particles, x, y, BOND_DECAY_PROBABILITY)
                absorption(particles, x, y, ABSORPTION_PROBABILITY)
                emission(particles, x, y, EMISSION_PROBABILITY)

        """
        触媒の位置座標の取得,計算
        """
        # --- ここから追記（記録処理） ---
        if step % RECORD_INTERVAL == 0:
            positions = get_catalyst_positions(particles)
            distances = get_catalyst_manhattan_distances(positions, initial_catalyst_positions)
            # 触媒の位置と初期位置からの距離を記録
            catalyst_positions.append(positions)
            catalyst_distances.append(distances)
        # step += 1
        # --- ここまで追記 ---

        # visualizer.update(particles)
        # 可視化を行う場合、visualizerに現在のparticlesを更新
        if visualizer:
            visualizer.update(particles)
        step += 1

    formatted_data = []
    for i, _ in enumerate(initial_catalyst_positions):
        for step_index, (positions, distances) in enumerate(zip(catalyst_positions, catalyst_distances)):
            if i < len(positions):
                sim_step = step_index * RECORD_INTERVAL
                pos_x, pos_y = positions[i]
                distance = distances[i]
                formatted_data.append([sim_step, i, pos_x, pos_y, distance])
    
    return formatted_data

if __name__ == '__main__':
    # --- START MODIFICATION ---
    # メインの処理をご提示の形式に合わせて、csvモジュールで書き出すように変更

    num_runs = 10
    output_filename = 'simulation_results.csv'
    header = ['Run', 'Step', 'Catalyst_ID', 'Position_X', 'Position_Y', 'Manhattan_Distance']

    print(f"Starting {num_runs} simulation runs...")

    # 'with open'でファイルを開き、処理が終わったら自動で閉じる
    # newline='' は、CSV書き込み時に不要な空行が入るのを防ぐためのおまじない
    with open(output_filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)

        # 最初にヘッダー（列名）を書き込む
        writer.writerow(header)

        # シミュレーションを指定回数ループ実行
        for i in range(num_runs):
            run_number = i + 1
            print(f"--- Running simulation {run_number}/{num_runs} ---")

            # 1回分のシミュレーションを実行し、結果リストを取得
            simulation_data = catalyst_position_history()

            # 取得したデータを1行ずつループで処理
            for row in simulation_data:
                # [実行回番号] と [ステップ, ID, X, Y, 距離] を結合して1行分のデータを作成
                csv_row = [run_number] + row
                # 作成した1行をファイルに書き込む
                writer.writerow(csv_row)

    print(f"--- All simulations finished. Results saved to '{output_filename}' ---")
    # --- END MODIFICATION ---

