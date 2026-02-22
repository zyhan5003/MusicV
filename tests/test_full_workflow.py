import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
import numpy as np
from src.core.main import MusicV
from src.gui.data_preview_window import DataPreviewWindow
from src.audio.data_visualizer import AudioDataVisualizer


def test_full_workflow():
    """测试完整工作流程"""
    print("=== 测试完整工作流程 ===")
    
    # 创建主窗口
    root = ctk.CTk()
    root.title("完整工作流程测试")
    root.geometry("600x400")
    
    # 创建MusicV实例
    musicv = MusicV()
    
    # 创建数据可视化器
    visualizer = AudioDataVisualizer(root)
    
    # 创建数据预览窗口
    preview_window = DataPreviewWindow(root)
    preview_window.set_visualizer(visualizer)
    preview_window.hide_window()
    
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
    path_entry.insert(0, "test_audio.wav")  # 默认路径
    
    # 加载音频并创建图表
    def load_and_create():
        file_path = path_entry.get()
        print(f"\n加载音频文件: {file_path}")
        
        # 加载音频
        success = musicv.load_audio(file_path)
        print(f"加载结果: {success}")
        
        if success and hasattr(musicv, 'audio_features') and musicv.audio_features:
            print(f"✓ 音频特征已加载")
            print(f"  特征类型: {list(musicv.audio_features.keys())}")
            
            # 加载到可视化器
            visualizer.load_features(musicv.audio_features)
            print("✓ 特征已加载到可视化器")
            
            # 创建图表
            preview_window._create_charts()
            print("✓ 图表已创建")
            
            # 显示预览窗口
            preview_window.show_window()
            print("✓ 预览窗口已显示")
        else:
            print("✗ 音频加载失败或特征为空")
    
    # 测试更新图表
    def test_update():
        print("\n测试更新图表...")
        current_frame = 50
        preview_window.update_charts(current_frame)
        print(f"✓ 图表已更新到帧 {current_frame}")
    
    # 创建按钮
    load_button = ctk.CTkButton(
        control_frame,
        text="加载音频并创建图表",
        command=load_and_create,
        height=40
    )
    load_button.pack(fill="x", padx=5, pady=5)
    
    update_button = ctk.CTkButton(
        control_frame,
        text="测试更新图表",
        command=test_update,
        height=40
    )
    update_button.pack(fill="x", padx=5, pady=5)
    
    print("✓ 测试界面已创建")
    print("使用说明:")
    print("1. 在输入框中输入音频文件路径")
    print("2. 点击'加载音频并创建图表'按钮")
    print("3. 点击'测试更新图表'按钮测试更新功能")
    
    root.mainloop()


if __name__ == "__main__":
    try:
        test_full_workflow()
        print("\n✓ 测试完成！")
    except Exception as e:
        print(f"\n✗ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()