
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
import cv2



# visualizerの初期化 (Appendix参照)
# visualizer = SwarmVisualizer()

# シミュレーションパラメタ
N = 30
# グループ数の指定.
N_GROUPS = 2
# グループの設定
group_ids = np.arange(N) % N_GROUPS
# グループごとの色の設定
COLOR_MAP_RGB = {
    'red': (255, 0, 0), 'blue': (0, 0, 255), 'green': (0, 255, 0),
    'orange': (255, 165, 0), 'purple': (128, 0, 128), 'cyan': (0, 255, 255)
}
COLORS = list(COLOR_MAP_RGB.values())
group_colors = [COLORS[i % len(COLORS)] for i in range(N_GROUPS)]

# 力の強さ
COHESION_FORCE = 0.008
SEPARATION_FORCE = 0.05
ALIGNMENT_FORCE = 0.06
# グループ間に働く力の強さ
SAME_GROUP_COHESION_FORCE = COHESION_FORCE * 1.1
OTHER_GROUP_COHESION_FORCE = COHESION_FORCE * 1
SAME_GROUP_SEPARATION_FORCE = SEPARATION_FORCE * 1
OTHER_GROUP_SEPARATION_FORCE = SEPARATION_FORCE * 1.1
# 力の働く距離
COHESION_DISTANCE = 0.5
SEPARATION_DISTANCE = 0.4
ALIGNMENT_DISTANCE = 0.1
# 力の働く角度
COHESION_ANGLE = np.pi / 2
SEPARATION_ANGLE = np.pi / 2
ALIGNMENT_ANGLE = np.pi / 3
# 速度の上限/下限
MIN_VEL = 0.005
MAX_VEL = 0.1
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

# ARUCOマーカーの生成
# マーカーサイズに関する設定
ARUCO_PIXEL_SIZE = 100  # マーカーのサイズ
BASE_PIXEL_SIZE = int(ARUCO_PIXEL_SIZE * 1.5)  # 土台となる白い正方形のサイズ
ARUCO_DRAW_SIZE = 0.4   # 画面に描画する際のサイズ


# ArUco辞書の準備
dict_aruco=aruco.getPredefinedDictionary(aruco.DICT_4X4_50)

# マーカー画像を保存するリスト
img = []
ids = []
# 各Boidに固有のIDを一度だけ割り当てる
for i in range(N):
    # 個体が属するグループの計算
    group_id = group_ids[i]
    marker_color = group_colors[group_id]
    # マーカーの作成
    marker_id = random.randint(0, 49)  # 0から49の範囲でランダムなIDを生成
    # marker_img = aruco.generateImageMarker(dict_aruco, marker_id, ARUCO_PIXEL_SIZE)
    ids.append(marker_id)
    # img.append(marker_img)
     # 1. 真っ白な土台画像を作成
    base_img = np.full((BASE_PIXEL_SIZE, BASE_PIXEL_SIZE, 3), marker_color, dtype=np.uint8)
    # 2. ArUcoマーカーを生成
    marker_img = aruco.generateImageMarker(dict_aruco, marker_id, ARUCO_PIXEL_SIZE)
    marker_img_rgb = cv2.cvtColor(marker_img, cv2.COLOR_GRAY2RGB) # マーカー画像をRGBに変換
    # 3. 土台の中央にマーカーを貼り付け
    offset = (BASE_PIXEL_SIZE - ARUCO_PIXEL_SIZE) // 2
    base_img[offset:offset+ARUCO_PIXEL_SIZE, offset:offset+ARUCO_PIXEL_SIZE] = marker_img_rgb
    # 4. 完成した「土台付きマーカー」をリストに追加
    img.append(base_img)
print(ids)  # 各BoidのIDを表示

def update(frame):
    global x, v, dv_coh, dv_sep, dv_ali, dv_boundary
# for i in range(1000):
# cohesion, separation, alignmentの３つの力を代入する変数
#     dv_coh = np.empty((N,3))
#     dv_sep = np.empty((N,3))
#     dv_ali = np.empty((N,3))
# 境界で働く力を代入する変数
#     dv_boundary = np.empty((N,3))
# cohesion, separation, alignmentの３つの力を代入する変数(2次元化)
    dv_coh = np.empty((N,2))
    dv_sep = np.empty((N,2))
    dv_ali = np.empty((N,2))
    # 境界で働く力を代入する変数(2次元化)
    dv_boundary = np.empty((N,2))

    # 画像を回転させる関数
    def rotate_image(image, angle):
        angle_deg = np.degrees(angle)
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        rot_mat = cv2.getRotationMatrix2D(center, angle_deg, 1.0)
        border_color = tuple(int(c) for c in image[0, 0])
        rotated = cv2.warpAffine(image, rot_mat, (w, h), flags=cv2.INTER_NEAREST, borderValue=border_color)
        return rotated
    
# while visualizer:
    for i in range(N):
        # 個体が属するグループの識別
        group_this = group_ids[i]
        group_that = np.delete(group_ids, i, axis=0)

        # グループごとにマスク
        same_group = (group_that == group_this)
        other_group = (group_that != group_this)

        # ここで計算する個体の位置と速度
        x_this = x[i]
        v_this = v[i]
        # それ以外の個体の位置と速度の配列
        x_that = np.delete(x, i, axis=0)
        v_that = np.delete(v, i, axis=0)
        # 個体間の距離と角度
        distance = np.linalg.norm(x_that - x_this, axis=1)
        # angle = np.arccos(np.dot(v_this, (x_that-x_this).T) / (np.linalg.norm(v_this) * np.linalg.norm((x_that-x_this), axis=1)))
        norm_v_this = np.linalg.norm(v_this) or 1e-6
        norm_x_diff = np.linalg.norm(x_that - x_this, axis=1)
        norm_x_diff[norm_x_diff == 0] = 1e-6 # 距離が0の個体は1e-6に

        cos_vals = np.dot(v_this, (x_that - x_this).T) / (norm_v_this * norm_x_diff)
        # np.clipで値を-1.0から1.0の範囲に強制的に収める
        angle = np.arccos(np.clip(cos_vals, -1.0, 1.0))
        # 各力が働く範囲内の個体のリスト
        coh_same_agents_x = x_that[ (distance < COHESION_DISTANCE) & (angle < COHESION_ANGLE) & same_group]
        coh_other_agents_x = x_that[ (distance < COHESION_DISTANCE) & (angle < COHESION_ANGLE) & other_group]
        sep_same_agents_x = x_that[ (distance < SEPARATION_DISTANCE) & (angle < SEPARATION_ANGLE) & same_group]
        sep_other_agents_x = x_that[ (distance < SEPARATION_DISTANCE) & (angle < SEPARATION_ANGLE) & other_group]
        ali_agents_v = v_that[ (distance < ALIGNMENT_DISTANCE) & (angle < ALIGNMENT_ANGLE) ]
        # 各力の計算
        # dv_coh[i] = COHESION_FORCE * (np.average(coh_agents_x, axis=0) - x_this) if (len(coh_agents_x) > 0) else 0
        # dv_sep[i] = SEPARATION_FORCE * (np.sum(x_this - sep_agents_x, axis=0) if (len(sep_agents_x) > 0) else 0)
        force_coh_from_same = SAME_GROUP_COHESION_FORCE * (np.average(coh_same_agents_x, axis=0) - x_this) if len(coh_same_agents_x) > 0 else 0
        force_coh_from_other = OTHER_GROUP_COHESION_FORCE * (np.average(coh_other_agents_x, axis=0) - x_this) if len(coh_other_agents_x ) > 0 else 0
        force_sep_from_same = SAME_GROUP_SEPARATION_FORCE * np.sum(x_this - sep_same_agents_x, axis=0) if len(sep_same_agents_x) > 0 else 0
        force_sep_from_other = OTHER_GROUP_SEPARATION_FORCE * np.sum(x_this - sep_other_agents_x, axis=0) if len(sep_other_agents_x) > 0 else 0
        # 結合力：同じ仲間からの力はブーストし、違う仲間からの力は基本値を適用
        dv_coh[i] = force_coh_from_same + force_coh_from_other
        # 分離力：違う仲間からの力はブーストし、同じ仲間からの力は基本値を適用
        dv_sep[i] = force_sep_from_other + force_sep_from_same
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

    # 個体を進行方向に回転
    rotated_imgs = []
    for i in range(N):
        angle = np.arctan2(v[i, 1], v[i, 0])
        rotated_img = rotate_image(img[i], angle)
        rotated_imgs.append(rotated_img)

    # matplotlibでの可視化
    ax.clear()  # 前のフレームを消去
        
    # 各Boidの位置にマーカー画像を描画する
    #aruco辞書の生成
    dict_aruco=aruco.getPredefinedDictionary(aruco.DICT_4X4_50)

    #マーカーサイズ
    size_mark=10

    #arucoマーカーの描画(10個)
    for i in range(N):
        pos = x[i]
        marker_img = rotated_imgs[i]
        
        size = ARUCO_DRAW_SIZE / 2
        extent = [pos[0] - size, pos[0] + size, pos[1] - size, pos[1] + size]
        
        # interpolation='nearest'を追加して、マーカーをくっきり表示
        ax.imshow(marker_img, cmap='gray', extent=extent, interpolation='nearest')

    ax.set_xlim(-4.0, 4.0) # 描画範囲の設定
    ax.set_ylim(-4.0, 4.0) # 描画範囲の設定
    ax.set_aspect('equal', adjustable='box')
    plt.axis('off')  # 軸を非表示にする
    plt.pause(0.01) # 短い時間停止して描画を更新
# アニメーションを生成
ani = animation.FuncAnimation(fig, update, frames=None, interval=20)

# plt.ioff()  # インタラクティブモードをオフにする
# アニメーションを保存しない場合は以下の行をコメントアウト
ani.save("animation.mp4", writer="ffmpeg")
plt.show()  # 最後に全てのフレームを表示  
