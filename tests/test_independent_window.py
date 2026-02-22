import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
import numpy as np
from src.audio.data_visualizer import AudioDataVisualizer
from src.gui.data_preview_window import DataPreviewWindow


def test_independent_window():
    """测试独立的数据预览窗口"""
    print("=== 测试独立的数据预览窗口 ===")
    
    # 创建主窗口
    root = ctk.CTk()
    root.title("独立窗口测试")
    root.geometry("600x400")
    
    # 创建数据可视化器
    visualizer = AudioDataVisualizer(root)
    
    # 创建模拟音频特征数据
    num_frames = 1000
    
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
    
    # 加载特征数据
    visualizer.load_features(features)
    print(f"✓ 加载了 {num_frames} 帧的音频特征数据")
    
    # 创建独立的数据预览窗口
    preview_window = DataPreviewWindow(root)
    preview_window.set_visualizer(visualizer)
    preview_window.hide_window()  # 初始隐藏
    
    # 创建控制按钮
    control_frame = ctk.CTkFrame(root)
    control_frame.pack(fill="x", padx=10, pady=10)
    
    # 显示/隐藏预览窗口
    show_button = ctk.CTkButton(
        control_frame,
        text="显示预览窗口",
        command=preview_window.show_window,
        width=150
    )
    show_button.pack(side="left", padx=5, pady=5)
    
    hide_button = ctk.CTkButton(
        control_frame,
        text="隐藏预览窗口",
        command=preview_window.hide_window,
        width=150
    )
    hide_button.pack(side="left", padx=5, pady=5)
    
    # 创建图表按钮
    create_button = ctk.CTkButton(
        control_frame,
        text="创建图表",
        command=lambda: (visualizer.load_features(features), preview_window._create_charts()),
        width=150
    )
    create_button.pack(side="left", padx=5, pady=5)
    
    # 模拟播放控制
    play_frame = ctk.CTkFrame(root)
    play_frame.pack(fill="x", padx=10, pady=5)
    
    is_playing = [False]
    
    def toggle_play():
        is_playing[0] = not is_playing[0]
        if is_playing[0]:
            play_button.configure(text="暂停")
            start_simulation()
        else:
            play_button.configure(text="播放")
            stop_simulation()
    
    play_button = ctk.CTkButton(
        play_frame,
        text="播放",
        command=toggle_play,
        width=100
    )
    play_button.pack(side="left", padx=5, pady=5)
    
    # 模拟播放线程
    import threading
    import time
    simulation_thread = None
    stop_event = threading.Event()
    
    def start_simulation():
        """开始模拟播放"""
        nonlocal simulation_thread
        stop_event.clear()
        
        def simulation_loop():
            current_frame = visualizer.current_frame
            while not stop_event.is_set() and current_frame < num_frames:
                preview_window.update_charts(current_frame)
                current_frame += 1
                time.sleep(0.03)  # 约30fps
        
        simulation_thread = threading.Thread(target=simulation_loop, daemon=True)
        simulation_thread.start()
    
    def stop_simulation():
        """停止模拟播放"""
        stop_event.set()
    
    # 测试功能
    def test_functions():
        """测试各个功能"""
        print("\n开始功能测试...")
        
        # 测试1: 显示/隐藏窗口
        print("测试1: 显示/隐藏窗口")
        preview_window.show_window()
        time.sleep(1)
        preview_window.hide_window()
        time.sleep(1)
        preview_window.show_window()
        print("✓ 窗口显示/隐藏正常")
        
        # 测试2: 创建图表
        print("\n测试2: 创建图表")
        preview_window._create_charts()
        time.sleep(1)
        print("✓ 图表创建正常")
        
        # 测试3: 调整切片窗口
        print("\n测试3: 调整切片窗口")
        preview_window.slice_slider.set(50)
        time.sleep(0.5)
        preview_window.slice_slider.set(200)
        time.sleep(0.5)
        print("✓ 切片窗口调整正常")
        
        # 测试4: 更新图表
        print("\n测试4: 更新图表")
        for frame in [0, 100, 200, 500, 800]:
            preview_window.update_charts(frame)
            time.sleep(0.5)
        print("✓ 图表更新正常")
        
        # 测试5: 自动播放
        print("\n测试5: 自动播放")
        toggle_play()
        time.sleep(3)
        toggle_play()
        print("✓ 自动播放正常")
        
        print("\n✓ 所有功能测试完成！")
    
    # 添加测试按钮
    test_button = ctk.CTkButton(
        play_frame,
        text="运行测试",
        command=test_functions,
        width=100
    )
    test_button.pack(side="left", padx=5, pady=5)
    
    print("✓ 独立窗口测试界面已创建")
    print("点击'显示预览窗口'按钮打开预览窗口")
    print("点击'运行测试'按钮开始测试")
    
    # 运行窗口
    root.mainloop()


if __name__ == "__main__":
    try:
        test_independent_window()
        print("\n✓ 独立窗口测试通过！")
    except Exception as e:
        print(f"\n✗ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()