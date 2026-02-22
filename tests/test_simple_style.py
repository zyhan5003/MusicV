import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
import numpy as np
from src.audio.data_visualizer import AudioDataVisualizer
from src.gui.data_preview_window import DataPreviewWindow


def test_simple_style():
    """测试简洁风格的数据预览窗口"""
    print("=== 简洁风格数据预览窗口测试 ===")
    
    # 创建主窗口
    root = ctk.CTk()
    root.title("简洁风格测试")
    root.geometry("800x600")
    
    # 创建数据可视化器
    visualizer = AudioDataVisualizer(root)
    
    # 创建模拟数据
    num_frames = 1000
    
    features = {
        "temporal": {
            "amplitude": np.random.uniform(-1, 1, num_frames * 512),
            "loudness": np.random.uniform(0.1, 1.0, num_frames),
            "zero_crossing_rate": np.random.uniform(0.0, 0.5, num_frames)
        },
        "frequency": {
            "spectrum": np.random.uniform(0, 1, (1025, num_frames)),
            "mel_spectrogram": np.random.uniform(0, 1, (128, num_frames)),
            "log_mel_spectrogram": np.random.uniform(-80, 0, (128, num_frames))
        },
        "rhythm": {
            "bpm": 120.0,
            "beat_frames": np.array([10, 20, 30, 40, 50]),
            "beat_times": np.array([0.1, 0.2, 0.3, 0.4, 0.5]),
            "beat_strength": np.random.uniform(0.5, 1.0, num_frames)
        },
        "timbre": {
            "mfcc": np.random.uniform(-10, 10, (20, num_frames)),
            "spectral_centroid": np.random.uniform(1000, 5000, num_frames),
            "spectral_bandwidth": np.random.uniform(1000, 3000, num_frames),
            "spectral_rolloff": np.random.uniform(2000, 6000, num_frames)
        }
    }
    
    print(f"加载 {num_frames} 帧的特征数据...")
    visualizer.load_features(features)
    print(f"✓ 总帧数: {visualizer.total_frames}")
    
    # 创建数据预览窗口
    preview_window = DataPreviewWindow(root)
    preview_window.set_visualizer(visualizer)
    preview_window.show_window()
    
    # 创建数据显示
    print("\n创建简洁风格的数据显示...")
    preview_window._create_charts()
    print(f"✓ 数据显示创建完成")
    
    # 创建控制面板
    control_frame = ctk.CTkFrame(root)
    control_frame.pack(fill="x", padx=10, pady=10)
    
    # 测试更新
    def test_update():
        """测试更新功能"""
        print("\n开始测试更新功能...")
        
        # 模拟100帧的更新
        for frame in range(0, 1000, 10):
            preview_window.update_charts(frame)
            root.update()
        
        print("✓ 更新测试完成")
    
    # 创建测试按钮
    test_button = ctk.CTkButton(
        control_frame,
        text="测试更新",
        command=test_update,
        height=40
    )
    test_button.pack(fill="x", padx=5, pady=5)
    
    print("\n✓ 测试界面已创建")
    print("使用说明:")
    print("1. 数据预览窗口会显示简洁风格的数据展示")
    print("2. 每个数据项包含：标签、数值、进度条")
    print("3. 点击'测试更新'按钮测试更新功能")
    print("4. 数据会实时更新，进度条会反映当前值")
    
    root.mainloop()


if __name__ == "__main__":
    try:
        test_simple_style()
        print("\n✓ 测试完成！")
    except Exception as e:
        print(f"\n✗ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()