import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
import numpy as np
import time
from src.audio.data_visualizer import AudioDataVisualizer
from src.gui.data_preview_window import DataPreviewWindow


def test_performance():
    """测试性能优化效果"""
    print("=== 性能优化测试 ===")
    
    # 创建主窗口
    root = ctk.CTk()
    root.title("性能测试")
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
    print(f"✓ 更新间隔: {visualizer.update_interval}秒（每秒{1/visualizer.update_interval:.0f}次）")
    
    # 创建数据预览窗口
    preview_window = DataPreviewWindow(root)
    preview_window.set_visualizer(visualizer)
    preview_window.show_window()
    
    # 创建图表
    print("\n创建图表...")
    start_time = time.time()
    preview_window._create_charts()
    end_time = time.time()
    print(f"✓ 图表创建完成，耗时: {end_time - start_time:.2f}秒")
    print(f"✓ 创建的图表: {list(visualizer.figures.keys())}")
    
    # 测试更新性能
    def test_update_performance():
        print("\n开始性能测试...")
        
        # 测试100次更新
        num_updates = 100
        start_time = time.time()
        
        for frame in range(0, num_frames * 10, 10):
            preview_window.update_charts(frame)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"✓ 完成{num_updates}次更新")
        print(f"✓ 总耗时: {total_time:.2f}秒")
        print(f"✓ 平均每次更新: {total_time/num_updates*1000:.2f}毫秒")
        print(f"✓ 实际更新频率: {num_updates/total_time:.1f}次/秒")
        
        # 检查是否达到目标频率
        target_fps = 1 / visualizer.update_interval
        actual_fps = num_updates / total_time
        if actual_fps >= target_fps * 0.8:  # 允许20%的误差
            print(f"✓ 性能良好，达到目标频率的{actual_fps/target_fps*100:.1f}%")
        else:
            print(f"⚠ 性能不足，只达到目标频率的{actual_fps/target_fps*100:.1f}%")
    
    # 测试禁用部分图表的性能
    def test_with_disabled_charts():
        print("\n测试禁用部分图表的性能...")
        
        # 禁用一半的图表
        charts_to_disable = ["zero_crossing_rate", "beat_strength", "spectral_bandwidth"]
        for chart_name in charts_to_disable:
            if chart_name in visualizer.enabled_charts:
                visualizer.enabled_charts[chart_name] = False
                print(f"  禁用: {chart_name}")
        
        # 测试100次更新
        num_updates = 100
        start_time = time.time()
        
        for frame in range(0, num_updates * 10, 10):
            preview_window.update_charts(frame)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        if total_time == 0:
            total_time = 0.001  # 避免除零错误
        
        print(f"✓ 完成{num_updates}次更新（仅{len(visualizer.figures) - len(charts_to_disable)}个图表）")
        print(f"✓ 总耗时: {total_time:.2f}秒")
        print(f"✓ 平均每次更新: {total_time/num_updates*1000:.2f}毫秒")
        print(f"✓ 实际更新频率: {num_updates/total_time:.1f}次/秒")
    
    # 创建控制面板
    control_frame = ctk.CTkFrame(root)
    control_frame.pack(fill="x", padx=10, pady=10)
    
    test_button = ctk.CTkButton(
        control_frame,
        text="测试完整性能",
        command=test_update_performance,
        height=40
    )
    test_button.pack(fill="x", padx=5, pady=5)
    
    test_button2 = ctk.CTkButton(
        control_frame,
        text="测试禁用部分图表",
        command=test_with_disabled_charts,
        height=40
    )
    test_button2.pack(fill="x", padx=5, pady=5)
    
    print("\n✓ 测试界面已创建")
    print("使用说明:")
    print("1. 点击'测试完整性能'按钮测试所有图表的性能")
    print("2. 点击'测试禁用部分图表'按钮测试禁用部分图表后的性能")
    print("3. 使用图表显示复选框来控制显示哪些图表")
    print("4. 禁用不需要的图表可以显著提升性能")
    
    root.mainloop()


if __name__ == "__main__":
    try:
        test_performance()
        print("\n✓ 测试完成！")
    except Exception as e:
        print(f"\n✗ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()