import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
import platform

# --- START MODIFICATION ---
# ◆◆◆ 設定箇所 ◆◆◆
# グラフの種類をここで切り替えます
# True:  両対数グラフ (傾きで拡散の種類を分析するのに適しています)
# False: 片対数グラフ (縦軸のみ対数。移動距離の大きさの変化を見やすいです)
USE_LOGLOG_PLOT = True
# --- END MODIFICATION ---


# 【文字化け対策】日本語フォントを設定
try:
    if platform.system() == 'Windows':
        plt.rcParams['font.family'] = 'Meiryo'
    elif platform.system() == 'Darwin': # macOS
        plt.rcParams['font.family'] = 'Hiragino Sans'
    else: # Linux
        # 利用可能な日本語フォントに適宜変更してください
        plt.rcParams['font.family'] = 'IPAexGothic'
except Exception as e:
    print(f"日本語フォントの設定中にエラーが発生しました: {e}")
    print("グラフの日本語が文字化けする可能性があります。")


def calculate_average_msd(filename, num_runs=10, max_lag_ratio=1.0):
    """
    CSVファイルを読み込み、ファイル内の全実行回数にわたる
    触媒の平均MSD（Mean Squared Displacement）を計算する。
    """
    try:
        df = pd.read_csv(filename)
    except FileNotFoundError:
        # ファイルが見つからない場合、ここでエラーメッセージを出してNoneを返す
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
        # 各ラグタイムに対してMSDを計算
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
    'initial': 'simulation_results(initial).csv',
    'ex_1': 'simulation_results(ex_1).csv',
    'ex_2': 'simulation_results(ex_2).csv'
}

# --- START MODIFICATION ---
# グラフの種類に応じて設定を分岐
if USE_LOGLOG_PLOT:
    # --- 両対数グラフ用の設定 ---
    fig, ax = plt.subplots(figsize=(8, 8))
    plot_title = 'Catalyst MSD Comparison (Log-Log Plot)'
    xlabel = 'Lag Time, t (x10 steps) [log-scale]'
    ylabel = 'Mean Squared Displacement (MSD) [log-scale]'
else:
    # --- 片対数グラフ用の設定 ---
    fig, ax = plt.subplots(figsize=(10, 6))
    plot_title = 'catalyst_MSD (semilog_scale)'
    xlabel = 'Steps, t (x10 steps)'
    ylabel = 'Mean Squared Displacement (MSD) [log-scale]'

plt.style.use('seaborn-v0_8-whitegrid')
# --- END MODIFICATION ---

ref_data = None
plot_data_exists = False
for label, filename in files_to_analyze.items():
    print(f"分析中: {filename}")
    lag_times, avg_msd = calculate_average_msd(filename)
    
    if lag_times is not None and avg_msd is not None:
        # --- START MODIFICATION ---
        # グラフの種類に応じてプロット関数を使い分ける
        if USE_LOGLOG_PLOT:
            ax.loglog(lag_times, avg_msd, 'o-', markersize=4, alpha=0.8, label=f'MSD ({label})')
        else:
            ax.semilogy(lag_times, avg_msd, 'o-', markersize=4, alpha=0.8, label=f'MSD ({label})')
        # --- END MODIFICATION ---
        
        plot_data_exists = True
        if ref_data is None:
            ref_data = (lag_times, avg_msd)

# --- START MODIFICATION ---
# グラフの体裁を設定
ax.set_title(plot_title, fontsize=14)
ax.set_xlabel(xlabel, fontsize=12)
ax.set_ylabel(ylabel, fontsize=12)

# 両対数グラフの場合のみ、参照線と軸の調整を行う
if USE_LOGLOG_PLOT:
    if ref_data is not None:
        lag_times_ref, avg_msd_ref = ref_data
        if len(lag_times_ref) > 10:
            c = avg_msd_ref[10] / lag_times_ref[10]
            ax.loglog(lag_times_ref, c * lag_times_ref**1.0, 'r--', label=r'Normal Diffusion ($\alpha=1$)')
    ax.axis('equal')
# --- END MODIFICATION ---

if plot_data_exists:
    ax.legend()
ax.grid(True, which="both", ls="--")

plt.show()
