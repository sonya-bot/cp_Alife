#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
sys.path.append(os.pardir)  # 親ディレクトリのファイルをインポートするための設定
import numpy as np
# from alifebook_lib.visualizers import SwarmVisualizer
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from cv2 import aruco
import random
plt.style.available



# visualizerの初期化 (Appendix参照)
# visualizer = SwarmVisualizer()

# シミュレーションパラメタ
N = 10
# 力の強さ
COHESION_FORCE = 0.008
SEPARATION_FORCE = 0.5
ALIGNMENT_FORCE = 0.06
# 力の働く距離
COHESION_DISTANCE = 0.5
SEPARATION_DISTANCE = 0.3
ALIGNMENT_DISTANCE = 0.1
# 力の働く角度
COHESION_ANGLE = np.pi / 2
SEPARATION_ANGLE = np.pi / 2
ALIGNMENT_ANGLE = np.pi / 3
# 速度の上限/下限
MIN_VEL = 0.005
MAX_VEL = 0.03
# 境界で働く力（0にすると自由境界）
BOUNDARY_FORCE = 0.001

# 位置と速度
# x = np.random.rand(N, 3) * 2 - 1
# v = (np.random.rand(N, 3) * 2 - 1 ) * MIN_VEL
# 位置と速度(2次元化)
x = np.random.rand(N, 2) * 2 - 1
v = (np.random.rand(N, 2) * 2 - 1 ) * MIN_VEL

#matplotlibでの可視化用
plt.ion()  # インタラクティブモードをオンにする
fig, ax = plt.subplots()

# --- START MODIFICATION ---
# マーカー生成処理をループの外に移動
# マーカーサイズに関する設定
ARUCO_PIXEL_SIZE = 100 # マーカー生成時のピクセルサイズ
ARUCO_DRAW_SIZE = 0.3  # 画面に描画する際のサイズ

# ArUco辞書の準備
dict_aruco=aruco.getPredefinedDictionary(aruco.DICT_4X4_50)

# マーカー画像を保存するリスト
img = []
ids = []
# 各Boidに固有のIDを一度だけ割り当てる
for i in range(N):
    marker_id = random.randint(0, 49)  # 0から49の範囲でランダムなIDを生成
    marker_img = aruco.generateImageMarker(dict_aruco, marker_id, ARUCO_PIXEL_SIZE)
    ids.append(marker_id)
    img.append(marker_img)
print(ids)  # 各BoidのIDを表示
# --- END MODIFICATION ---

def update(frame):
    global x, v, dv_coh, dv_sep, dv_ali, dv_boundary
# for i in range(1000):
# # cohesion, separation, alignmentの３つの力を代入する変数
# dv_coh = np.empty((N,3))
# dv_sep = np.empty((N,3))
# dv_ali = np.empty((N,3))
# # 境界で働く力を代入する変数
# dv_boundary = np.empty((N,3))
    # cohesion, separation, alignmentの３つの力を代入する変数(2次元化)
    dv_coh = np.empty((N,2))
    dv_sep = np.empty((N,2))
    dv_ali = np.empty((N,2))
    # 境界で働く力を代入する変数(2次元化)
    dv_boundary = np.empty((N,2))

# while visualizer:
    for i in range(N):
        # ここで計算する個体の位置と速度
        x_this = x[i]
        v_this = v[i]
        # それ以外の個体の位置と速度の配列
        x_that = np.delete(x, i, axis=0)
        v_that = np.delete(v, i, axis=0)
        # 個体間の距離と角度
        distance = np.linalg.norm(x_that - x_this, axis=1)
        angle = np.arccos(np.dot(v_this, (x_that-x_this).T) / (np.linalg.norm(v_this) * np.linalg.norm((x_that-x_this), axis=1)))
        # 各力が働く範囲内の個体のリスト
        coh_agents_x = x_that[ (distance < COHESION_DISTANCE) & (angle < COHESION_ANGLE) ]
        sep_agents_x = x_that[ (distance < SEPARATION_DISTANCE) & (angle < SEPARATION_ANGLE) ]
        ali_agents_v = v_that[ (distance < ALIGNMENT_DISTANCE) & (angle < ALIGNMENT_ANGLE) ]
        # 各力の計算
        dv_coh[i] = COHESION_FORCE * (np.average(coh_agents_x, axis=0) - x_this) if (len(coh_agents_x) > 0) else 0
        dv_sep[i] = SEPARATION_FORCE * np.sum(x_this - sep_agents_x, axis=0) if (len(sep_agents_x) > 0) else 0
        dv_ali[i] = ALIGNMENT_FORCE * (np.average(ali_agents_v, axis=0) - v_this) if (len(ali_agents_v) > 0) else 0
        dist_center = np.linalg.norm(x_this) # 原点からの距離
        dv_boundary[i] = - BOUNDARY_FORCE * x_this * (dist_center - 1) / dist_center if (dist_center > 1) else 0
    # 速度のアップデートと上限/下限のチェック
    v += dv_coh + dv_sep + dv_ali + dv_boundary
    for i in range(N):
        v_abs = np.linalg.norm(v[i])
        if (v_abs < MIN_VEL):
            v[i] = MIN_VEL * v[i] / v_abs
        elif (v_abs > MAX_VEL):
            v[i] = MAX_VEL * v[i] / v_abs
    # 位置のアップデート
    x += v
    # visualizer.update(x, v)



    # matplotlibでの可視化
    ax.clear()  # 前のフレームを消去
        
    # 各Boidの位置にマーカー画像を描画する
    #aruco辞書の生成
    dict_aruco=aruco.getPredefinedDictionary(aruco.DICT_4X4_50)

    #マーカーサイズ
    size_mark=10

    #arucoマーカーの生成(10個)
    for i in range(N):
        pos = x[i]
        marker_img = img[i]
        
        size = ARUCO_DRAW_SIZE / 2
        extent = [pos[0] - size, pos[0] + size, pos[1] - size, pos[1] + size]
        
        # interpolation='nearest'を追加して、マーカーをくっきり表示
        ax.imshow(marker_img, cmap='gray', extent=extent, interpolation='nearest')

    ax.set_xlim(-2.0, 2.0) # 描画範囲の設定
    ax.set_ylim(-2.0, 2.0) # 描画範囲の設定
    ax.set_aspect('equal', adjustable='box')
    plt.axis('off')  # 軸を非表示にする
    plt.pause(0.01) # 短い時間停止して描画を更新
# アニメーションを生成
ani = animation.FuncAnimation(fig, update, frames=1000, interval=20)

plt.ioff()  # インタラクティブモードをオフにする
ani.save("animation.mp4", writer="ffmpeg")
plt.show()  # 最後に全てのフレームを表示  
