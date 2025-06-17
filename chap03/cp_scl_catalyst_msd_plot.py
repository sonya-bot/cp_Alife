import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys

def calculate_average_msd(filename, num_runs=10, max_lag_ratio=0.25):
    """
    CSVファイルを読み込み、ファイル内の全実行回数にわたる
    触媒の平均MSD（Mean Squared Displacement）を計算する。
    """
    try:
        df = pd.read_csv(filename)
    except FileNotFoundError:
        print(f"エラー: ファイルが見つかりません - {filename}")
        return None, None

    list_of_msds = []
    min_run_length = float('inf')

    for i in range(1, num_runs + 1):
        run_df = df[df['Run'] == i]
        if run_df.empty:
            continue
        
        trajectory = run_df[['Position_X', 'Position_Y']].values
        if len(trajectory) < 2:
            continue

        min_run_length = min(min_run_length, len(trajectory))
        
        max_lag = int(len(trajectory) * max_lag_ratio)
        if max_lag < 1:
            continue
            
        lag_times = np.arange(1, max_lag)
        msds = np.zeros(len(lag_times))
        
        for j, dt in enumerate(lag_times):
            diff = trajectory[dt:] - trajectory[:-dt]
            squared_disp = np.sum(diff**2, axis=1)
            msds[j] = np.mean(squared_disp)
            
        list_of_msds.append(msds)

    if not list_of_msds:
        print(f"警告: {filename} から有効な軌跡データを取得できませんでした。")
        return None, None

    final_max_lag = int(min_run_length * max_lag_ratio)
    if final_max_lag < 2:
        print(f"警告: {filename} のシミュレーション長が短すぎてMSDを計算できません。")
        return None, None

    truncated_msds = [msd[:final_max_lag - 1] for msd in list_of_msds if len(msd) >= final_max_lag - 1]
    if not truncated_msds:
        return None, None

    average_msd = np.mean(np.array(truncated_msds), axis=0)
    final_lag_times = np.arange(1, final_max_lag)
    
    return final_lag_times, average_msd

# --- メイン処理 ---
files_to_analyze = {
    '初期状態': 'simulation_results(initial).csv',
}

# --- START MODIFICATION ---
# グラフ描画の準備 (figsizeを横長に調整)
plt.style.use('seaborn-v0_8-whitegrid')
fig, ax = plt.subplots(figsize=(10, 6))

# 各ファイルについてMSDを計算しプロット
for label, filename in files_to_analyze.items():
    print(f"分析中: {filename}")
    lag_times, avg_msd = calculate_average_msd(filename)
    
    if lag_times is not None and avg_msd is not None:
        # 描画関数を ax.loglog から ax.semilogy に変更
        ax.semilogy(lag_times, avg_msd, 'o-', markersize=4, alpha=0.8, label=f'MSD ({label})')

# グラフの体裁を片対数グラフ用に変更
ax.set_xlabel('Lag Time, Δt (x10 steps)', fontsize=12)
ax.set_ylabel('Mean Squared Displacement (MSD) [log-scale]', fontsize=12)
ax.set_title('触媒のMSD比較 (片対数グラフ)', fontsize=14)
ax.legend()
# 片対数グラフでは参照線とaxis('equal')は意味合いが変わるため、ここでは省略します
ax.grid(True, which="both", ls="--") # グリッド線を表示

plt.show()
# --- END MODIFICATION ---