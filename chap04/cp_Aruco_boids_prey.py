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
import cv2
import csv  

# visualizerの初期化 (Appendix参照)
# visualizer = SwarmVisualizer()

# シミュレーションパラメタ
N = 10 # Boidの数
# boid間の距離(検出精度向上の為、重ならないように)
BOID_SEPARATION_DISTANCE = 0.4  # この距離より近づくと反発力が働く
# 力の強さ
COHESION_FORCE = 0.008
SEPARATION_FORCE = BOID_SEPARATION_DISTANCE
ALIGNMENT_FORCE = 0.06
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
MAX_VEL = 0.03
# 境界で働く力（0にすると自由境界）
BOUNDARY_FORCE = 0.001
# エサに吸引される力と動かす間隔
PREY_FORCE = 0.0005
PREY_MOVEMENT_STEP = 150
# エサを避けるためのパラメタ(餌に重ならないようにする)
PREY_SEPARATION_DISTANCE = BOID_SEPARATION_DISTANCE  # この距離より近づくと反発力が働く
PREY_SEPARATION_FORCE = 0.01   # エサから離れようとする力の強さ

# 位置と速度
# x = np.random.rand(N, 3) * 2 - 1
# v = (np.random.rand(N, 3) * 2 - 1 ) * MIN_VEL
# エサの位置
# prey_x = np.random.rand(1, 3) * 2 - 1

# 位置と速度(2次元化)
x = np.random.rand(N, 2) * 2 - 1
v = (np.random.rand(N, 2) * 2 - 1 ) * MIN_VEL
# エサの位置と速度(2次元化)
prey_x = np.random.rand(1, 2) * 2 - 1
prey_v = (np.random.rand(1, 2) * 2 - 1 ) * MIN_VEL

# ARUCOマーカーの生成
# マーカーサイズに関する設定
ARUCO_PIXEL_SIZE = 100  # マーカーのサイズ
BASE_PIXEL_SIZE = int(ARUCO_PIXEL_SIZE * 1.5)  # 土台となる白い正方形のサイズ
ARUCO_DRAW_SIZE = 0.4   # 画面に描画する際のサイズ

# ArUco辞書の準備
dict = aruco.DICT_4X4_50 # 使用する辞書の指定
dict_aruco=aruco.getPredefinedDictionary(dict)
# マーカーサイズの指定
size_aruco_marker = 10

# マーカー画像を保存するリスト
img = []
ids = []

# マーカーの軌跡を保存するリスト
boids_trajectory = [[] for _ in range(N)]

# 餌のマーカーidはid=0に設定
prey_id = 0
# 餌のマーカー画像を生成
prey_marker_img = aruco.generateImageMarker(dict_aruco, prey_id, ARUCO_PIXEL_SIZE)
prey_marker_img_rgb = cv2.cvtColor(prey_marker_img, cv2.COLOR_GRAY2RGB) # マーカー画像をRGBに変換
# 餌のマーカー色を指定
COLOR_PREY = (255, 255 , 0)  # cyan
prey_marker_color = COLOR_PREY
# 土台の中央に餌のマーカーを貼り付け
base_prey_img = np.full((BASE_PIXEL_SIZE, BASE_PIXEL_SIZE,3), prey_marker_color, dtype=np.uint8) #色はmagenta
offset = (BASE_PIXEL_SIZE - ARUCO_PIXEL_SIZE) // 2
base_prey_img[offset:offset+ARUCO_PIXEL_SIZE, offset:offset+ARUCO_PIXEL_SIZE] = prey_marker_img_rgb
# 完成した「土台付き餌マーカー」をリストに追加
img.append(base_prey_img)   
ids.append(prey_id)  # 餌のIDを追加
#デバッグ用
# plt.imshow(base_prey_img)
# plt.title(f"id={prey_id}")
# plt.show()

# 各Boidに固有のIDを一度だけ割り当てる(0以外)
for i in range(N):
    marker_id = random.randint(1, 49)  # 1から49の範囲でランダムなIDを生成(0は餌用に固定)
    # marker_img = aruco.generateImageMarker(dict_aruco, marker_id, ARUCO_PIXEL_SIZE)
    ids.append(marker_id)  # IDをリストに追加
    # img.append(marker_img)
    # 真っ白な土台画像をRGBで作成
    base_img = np.full((BASE_PIXEL_SIZE, BASE_PIXEL_SIZE, 3), (255, 255, 255), dtype=np.uint8)
    # ArUcoマーカーを生成し、RGBに変換
    marker_img = aruco.generateImageMarker(dict_aruco, marker_id, ARUCO_PIXEL_SIZE)
    marker_img_rgb = cv2.cvtColor(marker_img, cv2.COLOR_GRAY2RGB)
    # 土台の中央にマーカーを貼り付け
    offset = (BASE_PIXEL_SIZE - ARUCO_PIXEL_SIZE) // 2
    base_img[offset:offset+ARUCO_PIXEL_SIZE, offset:offset+ARUCO_PIXEL_SIZE] = marker_img_rgb
    # 完成した「土台付きマーカー」をリストに追加
    img.append(base_img)
print(f"Prey ID: {ids[0]}, Boid IDs: {ids[1:]}")  # 各BoidのIDを表示

# 可視化のための設定
plt.ion()  # インタラクティブモードをオンにする
fig, ax = plt.subplots()

# 描画の設定
def update(frame):
    ax.clear()  # 前のフレームを消去
    global x, v, dv_coh, dv_sep, dv_ali, dv_boundary, prey_x
    # cohesion, separation, alignmentの３つの力を代入する変数
    dv_coh = np.empty((N,2))
    dv_sep = np.empty((N,2))
    dv_ali = np.empty((N,2))
    # 境界で働く力を代入する変数
    dv_boundary = np.empty((N,2))

    # 速度と力をもとに画像を回転させる関数
    def rotate_image(image, angle):
        angle_deg = np.degrees(angle)
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        rot_mat = cv2.getRotationMatrix2D(center, angle_deg, 1.0)
        border_color = tuple(int(c) for c in image[0, 0])
        rotated = cv2.warpAffine(image, rot_mat, (w, h), flags=cv2.INTER_NEAREST, borderValue=border_color)
        return rotated
    
    # t = 0
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
        # angle = np.arccos(np.dot(v_this, (x_that-x_this).T) / (np.linalg.norm(v_this) * np.linalg.norm((x_that-x_this), axis=1)))
        norm_v_this = np.linalg.norm(v_this) or 1e-6
        norm_x_diff = np.linalg.norm(x_that - x_this, axis=1)
        norm_x_diff[norm_x_diff == 0] = 1e-6 # 距離が0の個体は1e-6に
        cos_vals = np.dot(v_this, (x_that - x_this).T) / (norm_v_this * norm_x_diff)
        # np.clipで値を-1.0から1.0の範囲に強制的に収める
        angle = np.arccos(np.clip(cos_vals, -1.0, 1.0))
        # 各力が働く範囲内の個体のリスト
        coh_agents_x = x_that[ (distance < COHESION_DISTANCE) & (angle < COHESION_ANGLE) ]
        sep_agents_x = x_that[ (distance < SEPARATION_DISTANCE) & (angle < SEPARATION_ANGLE) ]
        ali_agents_v = v_that[ (distance < ALIGNMENT_DISTANCE) & (angle < ALIGNMENT_ANGLE) ]
        # 各力の計算
        dv_coh[i] = COHESION_FORCE * (np.average(coh_agents_x, axis=0) - x_this) if (len(coh_agents_x) > 0) else 0
        dv_sep[i] = SEPARATION_FORCE * np.sum(x_this - sep_agents_x, axis=0) if (len(sep_agents_x) > 0) else 0
        dv_ali[i] = ALIGNMENT_FORCE * (np.average(ali_agents_v, axis=0) - v_this) if (len(ali_agents_v) > 0) else 0
        dist_center = np.linalg.norm(x_this) # 原点からの距離
        dist_from_center = 2 #中心から境界までの距離
        dv_boundary[i] = - BOUNDARY_FORCE * x_this * (dist_center - dist_from_center) / dist_center if (dist_center > dist_from_center) else 0

        dist_to_prey = np.linalg.norm(x_this - prey_x[0])
        if dist_to_prey < PREY_SEPARATION_DISTANCE:
        # エサから離れる方向のベクトルを計算し、分離力に加える
            dv_sep[i] += PREY_SEPARATION_FORCE * (x_this - prey_x[0]) / (dist_to_prey**2)

        # 境界を表す円を描画
        circle = plt.Circle((0, 0), dist_from_center, color='gray', fill=False, linestyle='dashed')
    # 速度のアップデートと上限/下限のチェック
    v += dv_coh + dv_sep + dv_ali + dv_boundary
    # エサへの吸引力を加える
    v += PREY_FORCE * (prey_x - x) / np.linalg.norm((prey_x - x), axis=1, keepdims=True)**2
    if frame % PREY_MOVEMENT_STEP == 0 and frame > 0:
        prey_x = np.random.rand(1, 2) * 2 - 1
        # visualizer.set_markers(prey_x) # エサの位置を表示する（Appendix参照）
        # ax.imshow(prey_x, cmap='gray', vmin=0, vmax=1)  # エサの位置を更新

    # t += 1
    for i in range(N):
        v_abs = np.linalg.norm(v[i])
        if (v_abs < MIN_VEL):
            v[i] = MIN_VEL * v[i] / v_abs
        elif (v_abs > MAX_VEL):
            v[i] = MAX_VEL * v[i] / v_abs
    # 位置のアップデート
    x += v
    # visualizer.update(x, v)

    # 描画の設定
    # エサのマーカーを描画
    prey_pos = prey_x[0]
    prey_img_to_draw = img[0] # img[0]がエサのマーカー
    size = ARUCO_DRAW_SIZE / 2
    extent_prey = [prey_pos[0] - size, prey_pos[0] + size, prey_pos[1] - size, prey_pos[1] + size]
    ax.imshow(prey_img_to_draw, extent=extent_prey, interpolation='nearest')

    rotated_imgs = []
    for i in range(N):
        # 個体を進行方向に回転
        angle = np.arctan2(v[i, 1], v[i, 0])
        rotated_img = rotate_image(img[i+1], angle)
        rotated_imgs.append(rotated_img)

        # マーカーの位置を更新
        pos = x[i]
        marker_img = rotated_imgs[i]
        
        size = ARUCO_DRAW_SIZE / 2
        extent = [pos[0] - size, pos[0] + size, pos[1] - size, pos[1] + size]
        
        # interpolation='nearest'を追加して、マーカーをくっきり表示
        ax.imshow(marker_img, cmap='gray', extent=extent, interpolation='nearest')

        # 軌跡の保存・描画
        boids_state = {
            "frame": frame,
            "id": ids[i],
            "position": x[i].tolist(),
            "velocity": v[i].tolist()
        }
        boids_trajectory[i].append(boids_state)

        # 軌跡を描画
        # trajectory = np.array([state["position"] for state in boids_trajectory[i]])
        # if len(trajectory) > 1:
        #     ax.plot(trajectory[:, 0], trajectory[:, 1], color='gray', alpha=0.5, linewidth=0.5)

# matplotlibでの可視化
    ax.add_artist(circle)  # 境界を描画
    ax.set_xlim(-3.0, 3.0) # 描画範囲の設定
    ax.set_ylim(-3.0, 3.0) # 描画範囲の設定
    ax.set_aspect('equal', adjustable='box')
    plt.axis('off')  # 軸を非表示にする
    plt.pause(0.01) # 短い時間停止して描画を更新
# アニメーションを生成
ani = animation.FuncAnimation(fig, update, frames=1000, interval=20)

plt.ioff()  # インタラクティブモードをオフにする
# ani.save("boids_prey_animation.mp4", writer="ffmpeg")
plt.show()  # 最後に全てのフレームを表示