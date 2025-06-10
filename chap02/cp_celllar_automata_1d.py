#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
sys.path.append(os.pardir)  # 親ディレクトリのファイルをインポートするための設定
import numpy as np
from alifebook_lib.visualizers import ArrayVisualizer
import matplotlib.pyplot as plt

# visualizerの初期化 (Appendix参照)
visualizer = ArrayVisualizer()

SPACE_SIZE = 600

# CAのバイナリコーディングされたルール (Wolfram code)
RULE = 30

# CAの状態空間
state = np.zeros(SPACE_SIZE, dtype=np.int8)
next_state = np.empty(SPACE_SIZE, dtype=np.int8)

# 最初の状態を初期化
### ランダム ###
# state[:] = np.random.randint(2, size=len(state))
### 中央の１ピクセルのみ１、後は０ ###
state[len(state)//2] = 1

plt.ion()  # インタラクティブモードをオンにする

fig, ax = plt.subplots()  # FigureとAxesオブジェクトを作成
im = ax.imshow(state.reshape(1, -1), cmap='gray', aspect='auto')  # 初期状態をimshowで表示
plt.tight_layout()
plt.show()

while plt.fignum_exists(fig.number):  # pltはウィンドウが閉じられるとFalseを返す
    # stateから計算した次の結果をnext_stateに保存
    for i in range(SPACE_SIZE):
        # left, center, right cellの状態を取得
        l = state[i-1]
        c = state[i]
        r = state[(i+1)%SPACE_SIZE]
        # neighbor_cell_codeは現在の状態のバイナリコーディング
        # ex) 現在が[1 1 0]の場合
        #     neighbor_cell_codeは 1*2^2 + 1*2^1 + 0*2^0 = 6となるので、
        #     RULEの６番目のビットが１ならば、次の状態は１となるので、
        #     RULEをneighbor_cell_code分だけビットシフトして１と論理積をとる。
        neighbor_cell_code = 2**2 * l + 2**1 * c + 2**0 * r
        if (RULE >> neighbor_cell_code) & 1:
            next_state[i] = 1
        else:
            next_state[i] = 0
    # 最後に入れ替え
    state, next_state = next_state, state
    # 表示をアップデート
    # visualizer.update(1-state) # visualizerは使用しない
    im.set_data(next_state.reshape(1, -1)) # matplotlibのimshowを更新
    plt.pause(0.01) # 0.01秒pauseを入れて、アニメーションを更新

plt.ioff()  # インタラクティブモードをオフにする