import sys
import os
import time
import threading

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.gui.main_window import MainWindow
import customtkinter as ctk

def test_gui_multiple_runs():
    """测试GUI多次运行可视化"""
    print("开始测试GUI多次运行可视化...")
    
    # 创建主窗口
    app = MainWindow()
    
    # 测试音频文件
    test_audio = "test_audio.wav"
    
    # 检查是否有测试音频文件
    if not os.path.exists(test_audio):
        print(f"警告: 测试音频文件 {test_audio} 不存在")
        return False
    
    # 测试运行3次
    for i in range(3):
        print(f"\n=== 第 {i+1} 次运行 ===")
        
        # 模拟选择音频文件
        app.current_audio_path = test_audio
        
        # 模拟加载音频
        if not app.musicv.load_audio(test_audio):
            print(f"✗ 第 {i+1} 次加载音频失败")
            return False
        
        print(f"✓ 第 {i+1} 次加载音频成功")
        
        # 启动可视化（在新线程中）
        thread = threading.Thread(target=app.musicv.start_visualization, daemon=True)
        thread.start()
        
        # 等待一段时间（模拟用户观看）
        print("  等待3秒...")
        time.sleep(3)
        
        # 停止可视化
        print("  停止可视化...")
        app.musicv.stop_visualization()
        
        # 等待线程结束
        thread.join(timeout=2)
        
        if thread.is_alive():
            print(f"✗ 第 {i+1} 次线程未正常停止")
            return False
        
        print(f"✓ 第 {i+1} 次运行完成")
        
        # 等待一段时间再进行下一次运行
        time.sleep(1)
    
    print("\n✓ 所有测试通过！")
    return True

if __name__ == "__main__":
    success = test_gui_multiple_runs()
    if not success:
        print("\n测试失败！")
        sys.exit(1)