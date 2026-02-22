import sys
import os
import time
import threading
import pygame

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.main import MusicV

def test_window_visibility():
    """测试窗口是否真正显示"""
    print("开始测试窗口可见性...")
    
    # 创建MusicV实例
    musicv = MusicV()
    
    # 测试音频文件
    test_audio = "test_audio.wav"
    
    # 检查是否有测试音频文件
    if not os.path.exists(test_audio):
        print(f"警告: 测试音频文件 {test_audio} 不存在")
        # 创建一个简单的测试音频
        import numpy as np
        from scipy.io import wavfile
        
        # 生成1秒的测试音频
        sample_rate = 44100
        duration = 1.0
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio_data = 0.5 * np.sin(2 * np.pi * 440 * t)  # 440Hz正弦波
        
        # 保存为WAV文件
        wavfile.write(test_audio, sample_rate, audio_data.astype(np.float32))
        print(f"✓ 创建测试音频文件: {test_audio}")
    
    # 测试运行3次
    for i in range(3):
        print(f"\n=== 第 {i+1} 次运行 ===")
        
        # 加载音频
        if not musicv.load_audio(test_audio):
            print(f"✗ 第 {i+1} 次加载音频失败")
            return False
        
        print(f"✓ 第 {i+1} 次加载音频成功")
        
        # 设置可视化类型
        musicv.set_visual_type("waveform")
        
        # 启动可视化（在新线程中）
        thread = threading.Thread(target=musicv.start_visualization, daemon=True)
        thread.start()
        
        # 等待一段时间让窗口显示
        print("  等待2秒让窗口显示...")
        time.sleep(2)
        
        # 检查窗口是否真的显示
        # 通过检查pygame的显示状态来判断
        if hasattr(musicv, 'visual_renderer') and musicv.visual_renderer.surface:
            print("✓ 窗口已创建")
        else:
            print("✗ 窗口未创建")
            return False
        
        # 检查线程状态
        if not thread.is_alive():
            print("✗ 线程提前退出")
            return False
        
        # 停止可视化
        print("  停止可视化...")
        musicv.stop_visualization()
        
        # 等待线程结束
        thread.join(timeout=3)
        
        if thread.is_alive():
            print("✗ 线程未正常停止")
            return False
        
        print(f"✓ 第 {i+1} 次运行完成")
        
        # 等待一段时间再进行下一次运行
        time.sleep(1)
    
    print("\n✓ 所有测试通过！")
    return True

if __name__ == "__main__":
    success = test_window_visibility()
    if not success:
        print("\n测试失败！")
        sys.exit(1)