import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

try:
    df = pd.read_csv('results_pathfinding.csv')
    df['time_ms'] = df['time_sec'] * 1000
    avg = df.groupby(['heuristic','size','density']).mean().reset_index()
    # Làm tròn path_length về số nguyên (vì số bước phải là số nguyên)
    avg['path_length'] = avg['path_length'].round(0).astype(int)
    avg['nodes_expanded'] = avg['nodes_expanded'].round(0).astype(int)
    avg['time_ms'] = avg['time_ms'].round(2)
    print("Data loaded from CSV.")
except:
    # fallback: tạo dữ liệu mẫu (chỉ dùng nếu chưa chạy thực nghiệm)
    print("No CSV found, using synthetic data.")
    np.random.seed(42)
    heuristics = ['Manhattan','Euclidean','Diagonal']
    sizes = ['20x15','30x20']
    densities = [0.2,0.3,0.4]
    data=[]
    for h in heuristics:
        for sz in sizes:
            base_len = 25 if sz=='20x15' else 45
            base_nodes=40 if sz=='20x15' else 220
            base_time=0.5 if sz=='20x15' else 2.2
            for d in densities:
                path_len = base_len + (d-0.2)*30 + np.random.randint(-3,4)
                nodes = base_nodes * (1+(d-0.2)*2) + np.random.randint(-15,15)
                time_sec= base_time * (1+(d-0.2)*3) + np.random.uniform(-0.1,0.1)
                data.append([h,sz,d,path_len,nodes,time_sec])
    df=pd.DataFrame(data,columns=['heuristic','size','density','path_length','nodes_expanded','time_sec'])
    df['time_ms']=df['time_sec']*1000
    avg=df.groupby(['heuristic','size','density']).mean().reset_index()
    avg['path_length'] = avg['path_length'].round(0).astype(int)
    avg['nodes_expanded'] = avg['nodes_expanded'].round(0).astype(int)
    avg['time_ms'] = avg['time_ms'].round(2)

heuristic_order = ['Manhattan','Euclidean','Diagonal']
sizes = sorted(df['size'].unique())
plt.rcParams['font.sans-serif']=['Arial']
plt.rcParams['axes.unicode_minus']=False

# Hình 3.4
fig, axes = plt.subplots(1,2,figsize=(12,5))
for ax, sz in zip(axes, sizes):
    sub = avg[avg['size']==sz]
    for h in heuristic_order:
        data = sub[sub['heuristic']==h].sort_values('density')
        ax.plot(data['density'], data['path_length'], marker='o', label=h)
    ax.set_title(f'Kích thước {sz}')
    ax.set_xlabel('Mật độ vật cản')
    ax.set_ylabel('Độ dài đường đi (bước)')
    ax.legend(); ax.grid(True, linestyle='--', alpha=0.6)
plt.suptitle('Hình 3.4: So sánh độ dài lời giải trung bình')
plt.tight_layout(); plt.savefig('Hinh3_4_path_length.png', dpi=150); plt.show()

# Hình 3.5 (linear y, không log)
fig, axes = plt.subplots(1,2,figsize=(12,5))
for ax, sz in zip(axes, sizes):
    sub = avg[avg['size']==sz]
    for h in heuristic_order:
        data = sub[sub['heuristic']==h].sort_values('density')
        ax.plot(data['density'], data['nodes_expanded'], marker='s', label=h)
    ax.set_title(f'Kích thước {sz}')
    ax.set_xlabel('Mật độ vật cản')
    ax.set_ylabel('Số trạng thái đã duyệt')
    ax.legend(); ax.grid(True, linestyle='--', alpha=0.6)
plt.suptitle('Hình 3.5: Đánh giá số trạng thái được duyệt')
plt.tight_layout(); plt.savefig('Hinh3_5_nodes_expanded.png', dpi=150); plt.show()

# Hình 3.6
fig, axes = plt.subplots(1,2,figsize=(12,5))
for ax, sz in zip(axes, sizes):
    sub = avg[avg['size']==sz]
    for h in heuristic_order:
        data = sub[sub['heuristic']==h].sort_values('density')
        ax.plot(data['density'], data['time_ms'], marker='^', label=h)
    ax.set_title(f'Kích thước {sz}')
    ax.set_xlabel('Mật độ vật cản')
    ax.set_ylabel('Thời gian (ms)')
    ax.legend(); ax.grid(True, linestyle='--', alpha=0.6)
plt.suptitle('Hình 3.6: So sánh thời gian thực thi trung bình')
plt.tight_layout(); plt.savefig('Hinh3_6_time.png', dpi=150); plt.show()

# Hình 3.7
fix_dens = 0.3
avg_fix = avg[avg['density']==fix_dens]
x = np.arange(len(heuristic_order)); width = 0.35
plt.figure(figsize=(10,6))
for i, sz in enumerate(sizes):
    sub = avg_fix[avg_fix['size']==sz]
    values = sub.set_index('heuristic').reindex(heuristic_order)['time_ms'].values
    plt.bar(x + i*width, values, width, label=sz)
plt.xticks(x + width/2, heuristic_order)
plt.ylabel('Thời gian (ms)')
plt.title(f'Hình 3.7: Ảnh hưởng của kích thước bản đồ (mật độ {fix_dens})')
plt.legend(); plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.tight_layout(); plt.savefig('Hinh3_7_size_effect.png', dpi=150); plt.show()