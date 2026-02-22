import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
import numpy as np
from src.audio.data_visualizer import AudioDataVisualizer
from src.gui.data_preview_window import DataPreviewWindow


def test_simple():
    """简单测试"""
    print("=== 简单测试 ===")
    
    # 创建主窗口
    root = ctk.CTk()
    root.title("简单测试")
    root.geometry("400x300")
    
    # 创建数据可视化器
    visualizer = AudioDataVisualizer(root)
    
    # 创建模拟数据
    num_frames = 100
    features = {
        "temporal": {
            "loudness": np.random.uniform(0.1, 1.0, num_frames),
            "zero_crossing_rate": np.random.uniform(0.0, 0.5, num_frames)
        },
        "frequency": {
            "spectral_centroid": np.random.uniform(1000, 5000, num_frames)
        },
        "rhythm": {
            "beat_strength": np.random.uniform(0.0, 1.0, num_frames)
        },
        "timbre": {
            "spectrum": np.random.uniform(0, 1, (1025, num_frames))
        }
    }
    
    print("加载特征数据...")
    visualizer.load_features(features)
    print(f"✓ 加载了 {num_frames} 帧的特征")
    print(f"✓ features内容: {list(visualizer.features.keys())}")
    
    # 创建数据预览窗口
    print("\n创建数据预览窗口...")
    preview_window = DataPreviewWindow(root)
    preview_window.set_visualizer(visualizer)
    print("✓ 数据预览窗口已创建（初始隐藏）")
    
    # 测试创建图表
    def test_create():
        print("\n开始创建图表...")
        preview_window._create_charts()
        print("✓ 图表创建完成")
    
    # 测试显示窗口
    def test_show():
        print("\n显示预览窗口...")
        preview_window.show_window()
        print("✓ 预览窗口已显示")
    
    # 创建测试按钮
    create_button = ctk.CTkButton(
        root,
        text="创建图表",
        command=test_create,
        height=50
    )
    create_button.pack(padx=20, pady=10)
    
    show_button = ctk.CTkButton(
        root,
        text="显示预览窗口",
        command=test_show,
        height=50
    )
    show_button.pack(padx=20, pady=10)
    
    print("✓ 测试界面已创建")
    print("点击'创建图表'按钮开始测试")
    
    root.mainloop()


if __name__ == "__main__":
    try:
        test_simple()
        print("\n✓ 测试完成！")
    except Exception as e:
        print(f"\n✗ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()