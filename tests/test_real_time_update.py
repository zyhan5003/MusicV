import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
import numpy as np
from src.core.main import MusicV
from src.gui.data_preview_window import DataPreviewWindow
from src.audio.data_visualizer import AudioDataVisualizer


def test_real_time_update():
    """测试实时更新功能"""
    print("=== 测试实时更新功能 ===")
    
    # 创建主窗口
    root = ctk.CTk()
    root.title("实时更新测试")
    root.geometry("600x400")
    
    # 创建MusicV实例
    musicv = MusicV()
    
    # 创建数据可视化器
    visualizer = AudioDataVisualizer(root)
    
    # 创建数据预览窗口
    preview_window = DataPreviewWindow(root)
    preview_window.set_visualizer(visualizer)
    preview_window.show_window()
    
    # 创建控制面板
    control_frame = ctk.CTkFrame(root)
    control_frame.pack(fill="x", padx=10, pady=10)
    
    # 文件路径输入
    path_frame = ctk.CTkFrame(control_frame)
    path_frame.pack(fill="x", padx=5, pady=5)
    
    path_label = ctk.CTkLabel(path_frame, text="音频文件路径:")
    path_label.pack(side="left", padx=5)
    
    path_entry = ctk.CTkEntry(path_frame)
    path_entry.pack(side="left", fill="x", expand=True, padx=5)
    path_entry.insert(0, "test_audio.wav")
    
    # 加载音频并创建图表
    def load_and_create():
        file_path = path_entry.get()
        print(f"\n加载音频文件: {file_path}")
        
        # 加载音频
        success = musicv.load_audio(file_path)
        print(f"加载结果: {success}")
        
        if success and hasattr(musicv, 'audio_features') and musicv.audio_features:
            print(f"✓ 音频特征已加载")
            print(f"  总帧数: {visualizer.total_frames}")
            print(f"  特征类型: {list(musicv.audio_features.keys())}")
            
            # 加载到可视化器
            visualizer.load_features(musicv.audio_features)
            print("✓ 特征已加载到可视化器")
            
            # 创建图表
            preview_window._create_charts()
            print("✓ 图表已创建")
            
            # 启用更新按钮
            update_button.configure(state="normal")
            auto_update_button.configure(state="normal")
        else:
            print("✗ 音频加载失败或特征为空")
    
    # 手动更新
    def manual_update():
        frame = int(frame_entry.get())
        print(f"\n手动更新到帧 {frame}")
        preview_window.update_charts(frame)
        print(f"✓ 图表已更新")
    
    # 自动更新
    def auto_update():
        print("\n开始自动更新...")
        start_frame = int(start_entry.get())
        end_frame = int(end_entry.get())
        step = int(step_entry.get())
        
        # 使用非阻塞方式更新
        current_frame = [start_frame]  # 使用列表以便在闭包中修改
        
        def update_step():
            if current_frame[0] >= end_frame:
                print("✓ 自动更新完成")
                return
            
            print(f"  更新到帧 {current_frame[0]}")
            preview_window.update_charts(current_frame[0])
            current_frame[0] += step
            
            # 100ms后继续下一次更新
            root.after(100, update_step)
        
        # 开始第一次更新
        update_step()
    
    # 创建按钮
    load_button = ctk.CTkButton(
        control_frame,
        text="加载音频并创建图表",
        command=load_and_create,
        height=40
    )
    load_button.pack(fill="x", padx=5, pady=5)
    
    # 手动更新控制
    update_frame = ctk.CTkFrame(control_frame)
    update_frame.pack(fill="x", padx=5, pady=5)
    
    frame_label = ctk.CTkLabel(update_frame, text="帧号:")
    frame_label.pack(side="left", padx=5)
    
    frame_entry = ctk.CTkEntry(update_frame, width=100)
    frame_entry.pack(side="left", padx=5)
    frame_entry.insert(0, "50")
    
    update_button = ctk.CTkButton(
        update_frame,
        text="更新",
        command=manual_update,
        height=40,
        state="disabled"
    )
    update_button.pack(side="left", padx=5)
    
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
    
    auto_update_button = ctk.CTkButton(
        auto_frame,
        text="自动更新",
        command=auto_update,
        height=40,
        state="disabled"
    )
    auto_update_button.pack(side="left", padx=5)
    
    print("✓ 测试界面已创建")
    print("使用说明:")
    print("1. 在输入框中输入音频文件路径")
    print("2. 点击'加载音频并创建图表'按钮")
    print("3. 使用手动更新或自动更新功能测试图表更新")
    
    root.mainloop()


if __name__ == "__main__":
    try:
        test_real_time_update()
        print("\n✓ 测试完成！")
    except Exception as e:
        print(f"\n✗ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()