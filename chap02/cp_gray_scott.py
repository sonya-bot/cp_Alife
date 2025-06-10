#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
sys.path.append(os.pardir)  # 親ディレクトリのファイルをインポートするための設定
import numpy as np
import time
import matplotlib.pyplot as plt
from alifebook_lib.visualizers import MatrixVisualizer  # 追加

# シミュレーションの各パラメタ
SPACE_GRID_SIZE = 256
dx = 0.01
VISUALIZATION_STEP = 8  # 何ステップごとに画面を更新するか。

# モデルの各パラメタ
Du = 2e-5
Dv = 1e-5
f, k = 0.04, 0.06  # amorphous

def run_simulation(dt, max_time=10, show_pattern=True):
    # 初期化
    u = np.ones((SPACE_GRID_SIZE, SPACE_GRID_SIZE))
    v = np.zeros((SPACE_GRID_SIZE, SPACE_GRID_SIZE))
    SQUARE_SIZE = 20
    u[SPACE_GRID_SIZE//2-SQUARE_SIZE//2:SPACE_GRID_SIZE//2+SQUARE_SIZE//2,
      SPACE_GRID_SIZE//2-SQUARE_SIZE//2:SPACE_GRID_SIZE//2+SQUARE_SIZE//2] = 0.5
    v[SPACE_GRID_SIZE//2-SQUARE_SIZE//2:SPACE_GRID_SIZE//2+SQUARE_SIZE//2,
      SPACE_GRID_SIZE//2-SQUARE_SIZE//2:SPACE_GRID_SIZE//2+SQUARE_SIZE//2] = 0.25
    u += np.random.rand(SPACE_GRID_SIZE, SPACE_GRID_SIZE)*0.1
    v += np.random.rand(SPACE_GRID_SIZE, SPACE_GRID_SIZE)*0.1

    times = []
    total_time = 0
    visualizer = MatrixVisualizer() if show_pattern else None  # 追加

    while total_time < max_time and (visualizer is None or visualizer):
        start = time.time()
        for i in range(VISUALIZATION_STEP):
            # ラプラシアンの計算
            laplacian_u = (np.roll(u, 1, axis=0) + np.roll(u, -1, axis=0) +
                           np.roll(u, 1, axis=1) + np.roll(u, -1, axis=1) - 4*u) / (dx*dx)
            laplacian_v = (np.roll(v, 1, axis=0) + np.roll(v, -1, axis=0) +
                           np.roll(v, 1, axis=1) + np.roll(v, -1, axis=1) - 4*v) / (dx*dx)
            # Gray-Scottモデル方程式
            dudt = Du*laplacian_u - u*v*v + f*(1.0-u)
            dvdt = Dv*laplacian_v + u*v*v - (f+k)*v
            u += dt * dudt
            v += dt * dvdt
        end = time.time()
        times.append(end - start)
        total_time += (end - start)
        if visualizer is not None:
            visualizer.update(u)  # 追加: パターンの進化を可視化
    return times

# dt=1, dt=0.1の2パターンでそれぞれ実行
print("dt=1でシミュレーションを開始します。")
times_dt1 = run_simulation(dt=1, max_time=10, show_pattern=True)
input("10秒経過しました。続けるにはEnterを押してください。")
print("dt=0.1でシミュレーションを開始します。")
times_dt01 = run_simulation(dt=0.1, max_time=10, show_pattern=True)
input("10秒経過しました。続けるにはEnterを押してください。")

# 計算量の可視化
plt.plot(times_dt1, label='dt=1')
plt.plot(times_dt01, label='dt=0.1')
plt.xlabel('Step')
plt.ylabel('Computation Time (s)')
plt.title('Computation Time per Step (10 seconds)')
plt.legend()
plt.grid(True)
plt.show()

