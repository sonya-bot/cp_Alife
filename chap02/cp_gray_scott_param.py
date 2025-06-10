# #!/usr/bin/env python
# # -*- coding: utf-8 -*-

# import sys, os
# sys.path.append(os.pardir)  # 親ディレクトリのファイルをインポートするための設定
# import numpy as np
# from alifebook_lib.visualizers import MatrixVisualizer

# # visualizerの初期化 (Appendix参照)
# visualizer = MatrixVisualizer()

# # シミュレーションの各パラメタ
# SPACE_GRID_SIZE = 256
# dx = 0.01
# dt = 1
# VISUALIZATION_STEP = 8  # 何ステップごとに画面を更新するか。

# # モデルの各パラメタ
# Du = 2e-5
# Dv = 1e-5
# f_min = 0.01
# f_max = 0.05
# k_min = 0.05
# k_max = 0.07

# f_lin = np.linspace(f_min, f_max, SPACE_GRID_SIZE)
# k_lin = np.linspace(k_min, k_max, SPACE_GRID_SIZE)
# f, k = np.meshgrid(f_lin, k_lin)

# # 初期化
# u = np.ones((SPACE_GRID_SIZE, SPACE_GRID_SIZE))
# v = np.zeros((SPACE_GRID_SIZE, SPACE_GRID_SIZE))
# # 中央にSQUARE_SIZE四方の正方形を置く
# SQUARE_SIZE = 20
# u[SPACE_GRID_SIZE//2-SQUARE_SIZE//2:SPACE_GRID_SIZE//2+SQUARE_SIZE//2,
#   SPACE_GRID_SIZE//2-SQUARE_SIZE//2:SPACE_GRID_SIZE//2+SQUARE_SIZE//2] = 0.5
# v[SPACE_GRID_SIZE//2-SQUARE_SIZE//2:SPACE_GRID_SIZE//2+SQUARE_SIZE//2,
#   SPACE_GRID_SIZE//2-SQUARE_SIZE//2:SPACE_GRID_SIZE//2+SQUARE_SIZE//2] = 0.25
# # 対称性を壊すために、少しノイズを入れる
# u = u + u*np.random.rand(SPACE_GRID_SIZE, SPACE_GRID_SIZE)*0.01
# v = v + u*np.random.rand(SPACE_GRID_SIZE, SPACE_GRID_SIZE)*0.01

# while visualizer:  # visualizerはウィンドウが閉じられるとFalseを返す
#     for i in range(VISUALIZATION_STEP):
#         # ラプラシアンの計算
#         # 空間の両境界でパラメタが急に変化するため周期境界条件は不適切なので、対称境界条件を使う
#         # まず外側に1つ大きくした行列(u_pad, v_pad)をつくり、それによってラプラシアンを計算する
#         u_pad = np.pad(u, 1, 'edge')
#         v_pad = np.pad(v, 1, 'edge')
#         laplacian_u = (np.roll(u_pad, 1, axis=0) + np.roll(u_pad, -1, axis=0) +
#                        np.roll(u_pad, 1, axis=1) + np.roll(u_pad, -1, axis=1) - 4*u_pad) / (dx*dx)
#         laplacian_v = (np.roll(v_pad, 1, axis=0) + np.roll(v_pad, -1, axis=0) +
#                        np.roll(v_pad, 1, axis=1) + np.roll(v_pad, -1, axis=1) - 4*v_pad) / (dx*dx)
#         # その後、サイズを揃える
#         laplacian_u = laplacian_u[1:-1,1:-1]
#         laplacian_v = laplacian_v[1:-1,1:-1]
#         # Gray-Scottモデル方程式
#         dudt = Du*laplacian_u - u*v*v + f*(1.0-u)
#         dvdt = Dv*laplacian_v + u*v*v - (f+k)*v
#         u += dt * dudt
#         v += dt * dvdt
#     # 表示をアップデート
#     visualizer.update(u)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
sys.path.append(os.pardir)
import numpy as np
# import matplotlib.pyplot as plt


# シミュレーションの各パラメタ
SPACE_GRID_SIZE = 256
dx = 0.01
dt = 1
VISUALIZATION_STEP = 8

# モデルの各パラメタ
Du = 2e-5
Dv = 1e-5
# f_min = 0.01
# f_max = 0.05
# k_min = 0.05
# k_max = 0.07
f_min = 0.01
f_max = 0.05
k_min = 0.05
k_max = 0.07

f_lin = np.linspace(f_min, f_max, SPACE_GRID_SIZE)
k_lin = np.linspace(k_min, k_max, SPACE_GRID_SIZE)
f, k = np.meshgrid(f_lin, k_lin)

# 初期化
u = np.ones((SPACE_GRID_SIZE, SPACE_GRID_SIZE))
v = np.zeros((SPACE_GRID_SIZE, SPACE_GRID_SIZE))
# 中央に正方形を置く
SQUARE_SIZE = 20
u[SPACE_GRID_SIZE//2-SQUARE_SIZE//2:SPACE_GRID_SIZE//2+SQUARE_SIZE//2,
  SPACE_GRID_SIZE//2-SQUARE_SIZE//2:SPACE_GRID_SIZE//2+SQUARE_SIZE//2] = 0.5
v[SPACE_GRID_SIZE//2-SQUARE_SIZE//2:SPACE_GRID_SIZE//2+SQUARE_SIZE//2,
  SPACE_GRID_SIZE//2-SQUARE_SIZE//2:SPACE_GRID_SIZE//2+SQUARE_SIZE//2] = 0.25
# ノイズを加える
u = u + u*np.random.rand(SPACE_GRID_SIZE, SPACE_GRID_SIZE)*0.01
v = v + u*np.random.rand(SPACE_GRID_SIZE, SPACE_GRID_SIZE)*0.01

plt.ion()  # インタラクティブモードをオン

fig, axes = plt.subplots(1, 3, figsize=(15, 5))
im_u = axes[0].imshow(u, cmap='gray', vmin=0, vmax=1)
axes[0].set_title('Concentration of U')
fig.colorbar(im_u, ax=axes[0], label='Concentration')

im_f = axes[1].imshow(f, cmap='viridis', interpolation='nearest')
axes[1].set_title('Parameter f (Supply Rate)')
fig.colorbar(im_f, ax=axes[1], label='f value')

im_k = axes[2].imshow(k, cmap='magma', interpolation='nearest')
axes[2].set_title('Parameter k (Removal Rate)')
fig.colorbar(im_k, ax=axes[2], label='k value')

# f, k の値をUのグラフにテキストで表示するための設定
text_f_min = axes[0].text(0.05, 0.95, f'f_min={f_min:.3f}', color='white', transform=axes[0].transAxes, ha='left', va='top', fontsize=8)
text_f_max = axes[0].text(0.95, 0.95, f'f_max={f_max:.3f}', color='white', transform=axes[0].transAxes, ha='right', va='top', fontsize=8)
text_k_min = axes[0].text(0.05, 0.05, f'k_min={k_min:.3f}', color='white', transform=axes[0].transAxes, ha='left', va='bottom', fontsize=8)
text_k_max = axes[0].text(0.05, 0.05, f'k_max={k_max:.3f}', color='white', transform=axes[0].transAxes, ha='left', va='bottom', fontsize=8)


plt.tight_layout()
plt.show()

while plt.fignum_exists(fig.number):
    for i in range(VISUALIZATION_STEP):
        # ラプラシアンの計算
        u_pad = np.pad(u, 1, 'edge')
        v_pad = np.pad(v, 1, 'edge')
        laplacian_u = (np.roll(u_pad, 1, axis=0) + np.roll(u_pad, -1, axis=0) +
                       np.roll(u_pad, 1, axis=1) + np.roll(u_pad, -1, axis=1) - 4*u_pad) / (dx*dx)
        laplacian_v = (np.roll(v_pad, 1, axis=0) + np.roll(v_pad, -1, axis=0) +
                       np.roll(v_pad, 1, axis=1) + np.roll(v_pad, -1, axis=1) - 4*v_pad) / (dx*dx)
        laplacian_u = laplacian_u[1:-1,1:-1]
        laplacian_v = laplacian_v[1:-1,1:-1]
        # Gray-Scottモデル方程式
        dudt = Du*laplacian_u - u*v*v + f*(1.0-u)
        dvdt = Dv*laplacian_v + u*v*v - (f+k)*v
        u += dt * dudt
        v += dt * dvdt

    # 表示をアップデート
    im_u.set_array(u)
    fig.canvas.draw()
    fig.canvas.flush_events()

plt.ioff()



