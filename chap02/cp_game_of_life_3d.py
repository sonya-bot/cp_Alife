#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
sys.path.append(os.pardir)
import numpy as np
from alifebook_lib.visualizers import MatrixVisualizer
import time  # アニメーション速度調整のため

# visualizerの初期化
visualizer = MatrixVisualizer()

WIDTH = 50
HEIGHT = 50

def initialize_state(pattern_type="random"):
    """
    ライフゲームの状態を初期化する関数。

    引数:
    pattern_type (str): 初期パターンの種類 ("random", "static", "oscillator", "glider", "glider_gun")。
                        デフォルトは "random"。
    """
    state = np.zeros((HEIGHT, WIDTH), dtype=np.int8)
    if pattern_type == "random":
        state = np.random.randint(2, size=(HEIGHT, WIDTH), dtype=np.int8)
    elif pattern_type == "static":
        pattern = STATIC
        x_offset = (WIDTH - pattern.shape[1]) // 2  # 中央に配置
        y_offset = (HEIGHT - pattern.shape[0]) // 2 # 中央に配置
        state[y_offset:y_offset+pattern.shape[0], x_offset:x_offset+pattern.shape[1]] = pattern
    elif pattern_type == "oscillator":
        pattern = OSCILLATOR
        x_offset = (WIDTH - pattern.shape[1]) // 2
        y_offset = (HEIGHT - pattern.shape[0]) // 2
        state[y_offset:y_offset+pattern.shape[0], x_offset:x_offset+pattern.shape[1]] = pattern
    elif pattern_type == "glider":
        pattern = GLIDER
        x_offset = (WIDTH - pattern.shape[1]) // 2
        y_offset = (HEIGHT - pattern.shape[0]) // 2
        state[y_offset:y_offset+pattern.shape[0], x_offset:x_offset+pattern.shape[1]] = pattern
    elif pattern_type == "glider_gun":
        pattern = GLIDER_GUN
        x_offset = (WIDTH - pattern.shape[1]) // 2
        y_offset = (HEIGHT - pattern.shape[0]) // 2
        state[y_offset:y_offset+pattern.shape[0], x_offset:x_offset+pattern.shape[1]] = pattern
    else:
        print("Invalid pattern_type. Initializing with random pattern.")
        state = np.random.randint(2, size=(HEIGHT, WIDTH), dtype=np.int8)
    return state

# 初期パターンの定義 (まとめて記述)
STATIC = np.array(
    [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
     [1,1,0,0,0,1,1,0,0,0,0,1,1,0,0,0,1,1,0],
     [1,1,0,0,1,0,0,1,0,0,1,0,0,1,0,0,1,0,1],
     [0,0,0,0,0,1,1,0,0,0,0,1,0,1,0,0,0,1,0],
     [0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0],
    ])

OSCILLATOR = np.array(
    [[1,0,0,0,0,1,0,0],
     [1,0,0,0,1,0,0,1],
     [1,0,0,0,1,0,0,1],
     [0,0,0,0,0,0,1,0]])

GLIDER = np.array(
    [[0,0,0,0],
     [0,0,1,0],
     [0,0,0,1],
     [0,1,1,1]])

GLIDER_GUN = np.array(
    [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0],
     [0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
     [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
     [1,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
     [1,1,0,0,0,0,0,0,0,0,1,0,0,0,1,0,1,1,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0],
     [0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
     [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
     [0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]])


if __name__ == "__main__": # おまじない。このファイルを直接実行した場合のみ以下のコードが実行される
    # 初期状態を選択 (例: "random", "static", "oscillator", "glider", "glider_gun")
    initial_pattern = "glider"  # ここで初期パターンを選択
    state = initialize_state(initial_pattern)
    next_state = np.empty((HEIGHT, WIDTH), dtype=np.int8)

    while visualizer:
        for i in range(HEIGHT):
            for j in range(WIDTH):
                nw = state[i-1,j-1]
                n  = state[i-1,j]
                ne = state[i-1,(j+1)%WIDTH]
                w  = state[i,j-1]
                c  = state[i,j]
                e  = state[i,(j+1)%WIDTH]
                sw = state[(i+1)%HEIGHT,j-1]
                s  = state[(i+1)%HEIGHT,j]
                se = state[(i+1)%HEIGHT,(j+1)%WIDTH]
                neighbor_cell_sum = nw + n + ne + w + e + sw + s + se
                if c == 0 and neighbor_cell_sum == 3:
                    next_state[i,j] = 1
                elif c == 1 and neighbor_cell_sum in (2,3):
                    next_state[i,j] = 1
                else:
                    next_state[i,j] = 0
        state, next_state = next_state, state
        visualizer.update(1-state)
        time.sleep(0.1)  # アニメーション速度を調整 (0.1秒間隔)
