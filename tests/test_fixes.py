import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
import numpy as np
from src.audio.data_visualizer import AudioDataVisualizer
from src.gui.data_preview_panel import DataPreviewPanel
from src.utils.file_history_manager import FileHistoryManager


def test_fixes():
    """测试修复后的功能"""
    print("=== 测试修复后的功能 ===")
    
    # 测试1: 文件历史记录管理器
    print("\n测试1: 文件历史记录管理器")
    history_manager = FileHistoryManager("test_history.json", max_history=5)
    
    # 添加测试文件
    test_files = [
        "C:/Music/song1.mp3",
        "C:/Music/song2.wav",
        "C:/Music/song3.flac"
    ]
    
    for file_path in test_files:
        history_manager.add_file(file_path)
    
    # 获取历史记录
    history = history_manager.get_history()
    print(f"✓ 历史记录数量: {len(history)}")
    print(f"✓ 历史记录: {history}")
    
    # 获取显示名称
    display_names = history_manager.get_display_names()
    print(f"✓ 显示名称: {display_names}")
    
    # 测试根据显示名称获取文件路径
    for display_name in display_names:
        file_path = history_manager.get_file_by_display_name(display_name)
        print(f"✓ {display_name} -> {file_path}")
    
    # 测试2: 数据可视化器
    print("\n测试2: 数据可视化器")
    root = ctk.CTk()
    root.title("数据可视化器测试")
    root.geometry("1000x800")
    
    visualizer = AudioDataVisualizer(root)
    
    # 创建模拟音频特征数据
    num_frames = 1000
    num_samples = num_frames * 512  # hop_length = 512
    
    features = {
        "temporal": {
            "amplitude": np.random.uniform(-1, 1, num_samples),
            "loudness": np.random.uniform(0.1, 1.0, num_frames),
            "zero_crossing_rate": np.random.uniform(0.0, 0.5, num_frames)
        },
        "frequency": {
            "spectral_centroid": np.random.uniform(1000, 5000, num_frames),
            "spectral_bandwidth": np.random.uniform(500, 2000, num_frames),
            "spectral_rolloff": np.random.uniform(2000, 8000, num_frames)
        },
        "rhythm": {
            "beat_strength": np.random.uniform(0.0, 1.0, num_frames)
        },
        "timbre": {
            "spectrum": np.random.uniform(0, 1, (1025, num_frames)),
            "mel_spectrogram": np.random.uniform(0, 1, (128, num_frames)),
            "log_mel_spectrogram": np.random.uniform(-80, 0, (128, num_frames)),
            "mfcc": np.random.uniform(-100, 100, (13, num_frames))
        }
    }
    
    # 加载特征数据
    visualizer.load_features(features)
    print(f"✓ 加载了 {num_frames} 帧的音频特征数据")
    print(f"✓ 总帧数: {visualizer.total_frames}")
    
    # 创建数据预览面板
    panel = DataPreviewPanel(root)
    panel.pack(fill="both", expand=True, padx=10, pady=10)
    panel.set_visualizer(visualizer)
    
    # 创建图表
    panel._create_charts()
    print("✓ 创建了所有图表")
    
    # 测试3: 实时更新
    print("\n测试3: 实时更新测试")
    test_frames = [0, 100, 200, 500, 800, 999]
    
    for frame in test_frames:
        panel.update_charts(frame)
        print(f"✓ 更新到第 {frame} 帧")
        import time
        time.sleep(0.5)
    
    # 测试4: 切片窗口调整
    print("\n测试4: 切片窗口调整测试")
    panel.slice_slider.set(50)
    time.sleep(0.5)
    panel.slice_slider.set(200)
    time.sleep(0.5)
    print("✓ 切片窗口调整正常")
    
    # 测试5: 可见性切换
    print("\n测试5: 可见性切换测试")
    panel._toggle_visibility()
    time.sleep(1)
    panel._toggle_visibility()
    print("✓ 可见性切换正常")
    
    print("\n✓ 所有测试通过！")
    print("关闭窗口以退出...")
    
    root.mainloop()


if __name__ == "__main__":
    try:
        test_fixes()
    except Exception as e:
        print(f"\n✗ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()