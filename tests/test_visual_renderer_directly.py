import sys
import os
import time
import threading
import pygame

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.main import MusicV

def test_visual_renderer_directly():
    """直接测试VisualRenderer的多次初始化"""
    print("开始直接测试VisualRenderer...")
    
    from src.visual.visual_renderer import VisualRenderer
    from src.config.config_manager import ConfigManager
    
    # 创建配置管理器
    config_manager = ConfigManager()
    
    # 测试运行3次
    for i in range(3):
        print(f"\n=== 第 {i+1} 次运行 ===")
        
        # 检查pygame状态
        print(f"运行前 pygame.get_init(): {pygame.get_init()}")
        
        # 创建VisualRenderer实例
        renderer = VisualRenderer(config_manager)
        
        # 模拟音频特征生成器
        def mock_features_generator():
            for j in range(100):  # 模拟100帧
                yield {"temporal": {"loudness": [0.5]}}
                time.sleep(0.01)  # 模拟10fps
        
        # 启动渲染器
        thread = threading.Thread(target=renderer.run, args=(mock_features_generator(),), daemon=True)
        thread.start()
        
        # 等待一段时间
        print("  等待2秒...")
        time.sleep(2)
        
        # 检查渲染器状态
        if renderer.running and renderer.surface:
            print("✓ 渲染器正在运行，窗口已创建")
        else:
            print("✗ 渲染器没有正常运行")
            return False
        
        # 停止渲染器
        print("  停止渲染器...")
        renderer.running = False
        
        # 等待线程结束
        thread.join(timeout=3)
        
        if thread.is_alive():
            print("✗ 线程未正常停止")
            return False
        
        # 清理资源
        renderer.cleanup()
        
        print(f"✓ 第 {i+1} 次运行完成")
        
        # 等待一段时间再进行下一次运行
        time.sleep(1)
    
    print("\n✓ 所有测试通过！")
    return True

if __name__ == "__main__":
    success = test_visual_renderer_directly()
    if not success:
        print("\n测试失败！")
        sys.exit(1)