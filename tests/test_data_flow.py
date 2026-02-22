import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from src.core.main import MusicV
from src.gui.data_preview_window import DataPreviewWindow
from src.audio.data_visualizer import AudioDataVisualizer


def test_data_flow():
    """测试数据流"""
    print("=== 测试数据流 ===")
    
    # 创建主窗口
    root = ctk.CTk()
    root.title("数据流测试")
    root.geometry("400x300")
    
    # 创建MusicV实例
    musicv = MusicV()
    
    # 创建数据可视化器
    visualizer = AudioDataVisualizer(root)
    
    # 创建数据预览窗口
    preview_window = DataPreviewWindow(root)
    preview_window.set_visualizer(visualizer)
    
    # 测试加载音频
    def test_load_audio():
        print("\n测试1: 加载音频")
        test_file = "test_audio.mp3"  # 替换为实际文件
        
        # 检查加载前状态
        print(f"加载前 - hasattr(audio_features): {hasattr(musicv, 'audio_features')}")
        if hasattr(musicv, 'audio_features'):
            print(f"加载前 - audio_features: {musicv.audio_features}")
        
        # 尝试加载
        success = musicv.load_audio(test_file)
        print(f"加载结果: {success}")
        
        # 检查加载后状态
        print(f"加载后 - hasattr(audio_features): {hasattr(musicv, 'audio_features')}")
        if hasattr(musicv, 'audio_features'):
            print(f"加载后 - audio_features存在: {musicv.audio_features is not None}")
            if musicv.audio_features:
                print(f"加载后 - audio_features内容: {list(musicv.audio_features.keys())}")
            else:
                print("加载后 - audio_features为空")
        
        # 测试传递到可视化器
        print("\n测试2: 传递到可视化器")
        if hasattr(musicv, 'audio_features') and musicv.audio_features:
            visualizer.load_features(musicv.audio_features)
            print(f"可视化器features: {list(visualizer.features.keys())}")
            
            # 测试创建图表
            print("\n测试3: 创建图表")
            preview_window._create_charts()
            print("图表创建完成")
        else:
            print("audio_features不存在或为空，无法创建图表")
    
    # 创建测试按钮
    test_button = ctk.CTkButton(
        root,
        text="测试数据流",
        command=test_load_audio,
        height=50
    )
    test_button.pack(padx=20, pady=20)
    
    print("✓ 测试界面已创建")
    print("点击'测试数据流'按钮开始测试")
    
    root.mainloop()


if __name__ == "__main__":
    try:
        test_data_flow()
    except Exception as e:
        print(f"\n✗ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()