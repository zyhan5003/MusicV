import sys
import os
import time
import threading

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.main import MusicV

def test_esc_exit():
    """测试ESC退出时音频是否停止"""
    print("开始测试ESC退出时音频停止...")
    
    # 创建MusicV实例
    musicv = MusicV()
    
    # 测试音频文件
    test_audio = "test_audio.wav"
    
    # 检查是否有测试音频文件
    if not os.path.exists(test_audio):
        print(f"警告: 测试音频文件 {test_audio} 不存在")
        return False
    
    # 加载音频
    if not musicv.load_audio(test_audio):
        print("✗ 加载音频失败")
        return False
    
    print("✓ 加载音频成功")
    
    # 启动可视化（在新线程中）
    def run_visualization():
        try:
            musicv.start_visualization()
        except Exception as e:
            print(f"✗ 可视化运行出错: {e}")
    
    thread = threading.Thread(target=run_visualization, daemon=True)
    thread.start()
    
    # 等待窗口初始化
    time.sleep(2)
    
    # 检查音频是否在播放
    import pygame.mixer
    if pygame.mixer.get_busy():
        print("✓ 音频正在播放")
    else:
        print("✗ 音频未在播放")
        return False
    
    # 模拟按ESC键（通过停止可视化）
    print("  模拟按ESC键退出...")
    musicv.stop_visualization()
    
    # 等待线程结束
    thread.join(timeout=2)
    
    # 检查音频是否停止
    if pygame.mixer.get_busy():
        print("✗ ESC退出后音频仍在播放")
        return False
    else:
        print("✓ ESC退出后音频已停止")
    
    # 检查声音对象是否已释放
    if musicv.current_sound is None:
        print("✓ 声音对象已释放")
    else:
        print("✗ 声音对象未释放")
        return False
    
    # 检查运行标志是否已重置
    if not musicv.is_visualization_running:
        print("✓ 运行标志已重置")
    else:
        print("✗ 运行标志未重置")
        return False
    
    print("\n✓ 所有测试通过！")
    return True

if __name__ == "__main__":
    success = test_esc_exit()
    if not success:
        print("\n测试失败！")
        sys.exit(1)
