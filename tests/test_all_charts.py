import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
import numpy as np
from src.audio.data_visualizer import AudioDataVisualizer
from src.gui.data_preview_window import DataPreviewWindow


def test_all_charts():
    """测试所有图表的更新"""
    print("=== 测试所有图表更新 ===")
    
    # 创建主窗口
    root = ctk.CTk()
    root.title("所有图表测试")
    root.geometry("800x600")
    
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
    
    # 创建数据预览窗口
    preview_window = DataPreviewWindow(root)
    preview_window.set_visualizer(visualizer)
    preview_window.show_window()
    
    # 创建图表
    print("\n创建图表...")
    preview_window._create_charts()
    print("✓ 图表创建完成")
    print(f"✓ 创建的图表: {list(visualizer.figures.keys())}")
    
    # 测试更新
    def test_update():
        frame = int(frame_entry.get())
        print(f"\n更新到帧 {frame}")
        
        # 更新前检查
        print(f"  更新前当前帧: {visualizer.current_frame}")
        
        # 更新图表
        preview_window.update_charts(frame)
        
        # 更新后检查
        print(f"  更新后当前帧: {visualizer.current_frame}")
        print(f"✓ 图表已更新")
    
    # 自动更新测试
    def auto_update():
        print("\n开始自动更新测试...")
        start_frame = int(start_entry.get())
        end_frame = int(end_entry.get())
        step = int(step_entry.get())
        
        # 使用非阻塞方式更新
        current_frame = [start_frame]  # 使用列表以便在闭包中修改
        
        def update_step():
            if current_frame[0] >= end_frame:
                print("✓ 自动更新测试完成")
                return
            
            print(f"  更新到帧 {current_frame[0]}")
            preview_window.update_charts(current_frame[0])
            current_frame[0] += step
            
            # 100ms后继续下一次更新
            root.after(100, update_step)
        
        # 开始第一次更新
        update_step()
    
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
    
    # 自动更新控制
    auto_frame = ctk.CTkFrame(control_frame)
    auto_frame.pack(fill="x", padx=5, pady=5)
    
    start_label = ctk.CTkLabel(auto_frame, text="起始帧:")
    start_label.pack(side="left", padx=5)
    
    start_entry = ctk.CTkEntry(auto_frame, width=60)
    start_entry.pack(side="left", padx=5)
    start_entry.insert(0, "0")
    
    end_label = ctk.CTkLabel(auto_frame, text="结束帧:")
    end_label.pack(side="left", padx=5)
    
    end_entry = ctk.CTkEntry(auto_frame, width=60)
    end_entry.pack(side="left", padx=5)
    end_entry.insert(0, "500")
    
    step_label = ctk.CTkLabel(auto_frame, text="步长:")
    step_label.pack(side="left", padx=5)
    
    step_entry = ctk.CTkEntry(auto_frame, width=60)
    step_entry.pack(side="left", padx=5)
    step_entry.insert(0, "10")
    
    auto_button = ctk.CTkButton(
        auto_frame,
        text="自动更新",
        command=auto_update,
        height=40
    )
    auto_button.pack(side="left", padx=5)
    
    print("\n✓ 测试界面已创建")
    print("使用说明:")
    print("1. 输入帧号并点击'更新到指定帧'按钮")
    print("2. 或点击'自动更新'按钮进行连续更新")
    print("3. 观察所有4个分类的图表是否都能正常更新")
    
    root.mainloop()


if __name__ == "__main__":
    try:
        test_all_charts()
        print("\n✓ 测试完成！")
    except Exception as e:
        print(f"\n✗ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()