import sys
import os
import time
import threading
import pygame

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.main import MusicV

def test_debug_multiple_runs():
    """调试多次运行的问题"""
    print("开始调试多次运行问题...")
    
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
        
        # 检查pygame状态
        print(f"运行前 pygame.get_init(): {pygame.get_init()}")
        print(f"运行前 pygame.mixer.get_init(): {pygame.mixer.get_init()}")
        
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
        
        # 等待一段时间
        print("  等待2秒...")
        time.sleep(2)
        
        # 检查线程状态
        if not thread.is_alive():
            print(f"✗ 第 {i+1} 次线程提前退出")
            print(f"线程退出时 pygame.get_init(): {pygame.get_init()}")
            return False
        
        # 停止可视化
        print("  停止可视化...")
        musicv.stop_visualization()
        
        # 等待线程结束
        thread.join(timeout=3)
        
        if thread.is_alive():
            print(f"✗ 第 {i+1} 次线程未正常停止")
            print(f"线程未停止时 pygame.get_init(): {pygame.get_init()}")
            return False
        
        # 检查pygame状态
        print(f"运行后 pygame.get_init(): {pygame.get_init()}")
        print(f"运行后 pygame.mixer.get_init(): {pygame.mixer.get_init()}")
        
        print(f"✓ 第 {i+1} 次运行完成")
        
        # 等待一段时间再进行下一次运行
        time.sleep(1)
    
    print("\n✓ 所有测试通过！")
    return True

if __name__ == "__main__":
    success = test_debug_multiple_runs()
    if not success:
        print("\n测试失败！")
        sys.exit(1)