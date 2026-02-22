import sys
import os
import time
import threading
import pygame

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_pygame_multiple_initializations():
    """测试pygame多次初始化的真实情况"""
    print("开始测试pygame多次初始化...")
    
    for i in range(3):
        print(f"\n=== 第 {i+1} 次初始化 ===")
        
        # 检查当前状态
        print(f"pygame.get_init(): {pygame.get_init()}")
        print(f"pygame.mixer.get_init(): {pygame.mixer.get_init()}")
        
        # 初始化pygame
        pygame.init()
        pygame.mixer.init()
        
        print(f"初始化后 pygame.get_init(): {pygame.get_init()}")
        print(f"初始化后 pygame.mixer.get_init(): {pygame.mixer.get_init()}")
        
        # 创建窗口
        try:
            surface = pygame.display.set_mode((640, 480))
            pygame.display.set_caption(f"Test Window {i+1}")
            print("✓ 窗口创建成功")
        except Exception as e:
            print(f"✗ 窗口创建失败: {e}")
            return False
        
        # 显示窗口几秒钟
        print("  显示窗口3秒...")
        start_time = time.time()
        while time.time() - start_time < 3:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    print("  用户退出")
                    pygame.quit()
                    return True
            
            surface.fill((0, 0, 0))
            pygame.display.flip()
            time.sleep(0.01)
        
        # 清理资源
        print("  清理资源...")
        pygame.quit()
        
        print(f"✓ 第 {i+1} 次完成")
        
        # 等待一下再进行下一次
        time.sleep(1)
    
    print("\n✓ 所有测试通过！")
    return True

if __name__ == "__main__":
    success = test_pygame_multiple_initializations()
    if not success:
        print("\n测试失败！")
        sys.exit(1)