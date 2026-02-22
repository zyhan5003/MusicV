import customtkinter as ctk
import threading
import numpy as np
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.audio.data_visualizer import AudioDataVisualizer
from src.gui.data_preview_panel import DataPreviewPanel


def test_data_preview_panel():
    """测试数据预览面板功能"""
    print("=== 测试数据预览面板功能 ===")
    
    # 创建主窗口
    root = ctk.CTk()
    root.title("数据预览面板测试")
    root.geometry("1000x800")
    
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
            "spectral_centroid": np.random.uniform(1000, 5000, num_frames),
            "spectral_bandwidth": np.random.uniform(500, 2000, num_frames)
        },
        "rhythm": {
            "beat_strength": np.random.uniform(0.0, 1.0, num_frames)
        },
        "timbre": {
            "spectrum": np.random.uniform(0, 1, (128, num_frames))
        }
    }
    
    # 加载特征数据
    visualizer.load_features(features)
    print(f"✓ 加载了 {num_frames} 帧的音频特征数据")
    
    # 创建数据预览面板
    panel = DataPreviewPanel(root)
    panel.pack(fill="both", expand=True, padx=10, pady=10)
    panel.set_visualizer(visualizer)
    
    # 创建控制按钮
    control_frame = ctk.CTkFrame(root)
    control_frame.pack(fill="x", padx=10, pady=5)
    
    # 播放/暂停按钮
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
        control_frame,
        text="播放",
        command=toggle_play,
        width=100
    )
    play_button.pack(side="left", padx=5, pady=5)
    
    # 重置按钮
    def reset_simulation():
        visualizer.set_current_frame(0)
        panel.update_charts(0)
        print("✓ 重置到第0帧")
    
    reset_button = ctk.CTkButton(
        control_frame,
        text="重置",
        command=reset_simulation,
        width=100
    )
    reset_button.pack(side="left", padx=5, pady=5)
    
    # 帧进度条
    progress_frame = ctk.CTkFrame(control_frame)
    progress_frame.pack(side="left", padx=5, pady=5, fill="x", expand=True)
    
    progress_label = ctk.CTkLabel(progress_frame, text="帧进度:")
    progress_label.pack(side="left", padx=5)
    
    progress_slider = ctk.CTkSlider(
        progress_frame,
        from_=0,
        to=num_frames - 1,
        number_of_steps=num_frames - 1,
        command=lambda v: update_frame(int(v))
    )
    progress_slider.pack(side="left", padx=5, fill="x", expand=True)
    
    frame_label = ctk.CTkLabel(progress_frame, text="0")
    frame_label.pack(side="left", padx=5)
    
    # 模拟播放线程
    simulation_thread = None
    stop_event = threading.Event()
    
    def update_frame(frame):
        """更新帧"""
        visualizer.set_current_frame(frame)
        panel.update_charts(frame)
        progress_slider.set(frame)
        frame_label.configure(text=str(frame))
    
    def start_simulation():
        """开始模拟播放"""
        nonlocal simulation_thread
        stop_event.clear()
        
        def simulation_loop():
            current_frame = visualizer.current_frame
            while not stop_event.is_set() and current_frame < num_frames:
                update_frame(current_frame)
                current_frame += 1
                import time
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
        
        # 测试1: 切换可见性
        print("测试1: 切换可见性")
        panel._toggle_visibility()
        import time
        time.sleep(1)
        panel._toggle_visibility()
        print("✓ 可见性切换正常")
        
        # 测试2: 调整切片窗口
        print("\n测试2: 调整切片窗口")
        panel.slice_slider.set(50)
        time.sleep(0.5)
        panel.slice_slider.set(200)
        time.sleep(0.5)
        print("✓ 切片窗口调整正常")
        
        # 测试3: 更新图表
        print("\n测试3: 更新图表")
        for frame in [0, 100, 200, 500, 800]:
            update_frame(frame)
            time.sleep(0.5)
        print("✓ 图表更新正常")
        
        # 测试4: 自动播放
        print("\n测试4: 自动播放")
        toggle_play()
        time.sleep(3)
        toggle_play()
        print("✓ 自动播放正常")
        
        print("\n✓ 所有功能测试完成！")
    
    # 添加测试按钮
    test_button = ctk.CTkButton(
        control_frame,
        text="运行测试",
        command=test_functions,
        width=100
    )
    test_button.pack(side="left", padx=5, pady=5)
    
    print("✓ 数据预览面板测试界面已创建")
    print("点击'运行测试'按钮开始测试，或手动操作控制面板")
    
    # 运行窗口
    root.mainloop()


if __name__ == "__main__":
    try:
        test_data_preview_panel()
        print("\n✓ 数据预览面板测试通过！")
    except Exception as e:
        print(f"\n✗ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()