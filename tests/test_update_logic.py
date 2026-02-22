import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
import numpy as np
from src.audio.data_visualizer import AudioDataVisualizer
from src.gui.data_preview_window import DataPreviewWindow


def test_update_logic():
    """测试更新逻辑"""
    print("=== 测试更新逻辑 ===")
    
    # 创建主窗口
    root = ctk.CTk()
    root.title("更新逻辑测试")
    root.geometry("600x400")
    
    # 创建数据可视化器
    visualizer = AudioDataVisualizer(root)
    
    # 创建模拟数据
    num_frames = 500
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
    
    print(f"加载 {num_frames} 帧的特征数据...")
    visualizer.load_features(features)
    print(f"✓ 总帧数: {visualizer.total_frames}")
    print(f"✓ 切片窗口: {visualizer.slice_window}")
    print(f"✓ 更新间隔: {visualizer.update_interval}秒")
    
    # 创建数据预览窗口
    preview_window = DataPreviewWindow(root)
    preview_window.set_visualizer(visualizer)
    preview_window.show_window()
    
    # 创建图表
    print("\n创建图表...")
    preview_window._create_charts()
    print("✓ 图表创建完成")
    
    # 测试更新
    def test_update():
        frame = int(frame_entry.get())
        print(f"\n更新到帧 {frame}")
        
        # 检查切片范围
        start, end = visualizer.get_slice_range()
        print(f"  切片范围: {start} - {end}")
        
        # 更新图表
        preview_window.update_charts(frame)
        print(f"✓ 图表已更新")
        
        # 检查更新后的切片范围
        start, end = visualizer.get_slice_range()
        print(f"  更新后切片范围: {start} - {end}")
    
    # 自动更新测试
    def auto_update():
        import time
        print("\n开始自动更新测试...")
        for i in range(0, 500, 50):
            print(f"  更新到帧 {i}")
            preview_window.update_charts(i)
            time.sleep(0.2)  # 等待200ms
        print("✓ 自动更新测试完成")
    
    # 创建控制面板
    control_frame = ctk.CTkFrame(root)
    control_frame.pack(fill="x", padx=10, pady=10)
    
    # 帧号输入
    frame_frame = ctk.CTkFrame(control_frame)
    frame_frame.pack(fill="x", padx=5, pady=5)
    
    frame_label = ctk.CTkLabel(frame_frame, text="帧号:")
    frame_label.pack(side="left", padx=5)
    
    frame_entry = ctk.CTkEntry(frame_frame)
    frame_entry.pack(side="left", fill="x", expand=True, padx=5)
    frame_entry.insert(0, "50")
    
    # 按钮
    update_button = ctk.CTkButton(
        control_frame,
        text="更新到指定帧",
        command=test_update,
        height=40
    )
    update_button.pack(fill="x", padx=5, pady=5)
    
    auto_button = ctk.CTkButton(
        control_frame,
        text="自动更新测试",
        command=auto_update,
        height=40
    )
    auto_button.pack(fill="x", padx=5, pady=5)
    
    print("\n✓ 测试界面已创建")
    print("使用说明:")
    print("1. 输入帧号并点击'更新到指定帧'按钮")
    print("2. 或点击'自动更新测试'按钮进行连续更新")
    
    root.mainloop()


if __name__ == "__main__":
    try:
        test_update_logic()
        print("\n✓ 测试完成！")
    except Exception as e:
        print(f"\n✗ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()