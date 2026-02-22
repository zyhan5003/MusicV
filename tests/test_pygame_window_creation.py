import sys
import os
import time
import threading
import pygame

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_pygame_window_creation():
    """测试pygame窗口创建的真实情况"""
    print("开始测试pygame窗口创建...")
    
    # 测试运行3次
    for i in range(3):
        print(f"\n=== 第 {i+1} 次运行 ===")
        
        # 检查pygame状态
        print(f"运行前 pygame.get_init(): {pygame.get_init()}")
        
        # 如果pygame已经初始化，先清理
        if pygame.get_init():
            print("  清理pygame...")
            pygame.quit()
            time.sleep(0.1)
        
        # 初始化pygame
        print("  初始化pygame...")
        pygame.init()
        
        # 创建窗口
        try:
            print("  创建窗口...")
            surface = pygame.display.set_mode((640, 480))
            pygame.display.set_caption(f"MusicV Test {i+1}")
            print("✓ 窗口创建成功")
        except Exception as e:
            print(f"✗ 窗口创建失败: {e}")
            return False
        
        # 显示窗口几秒钟
        print("  显示窗口2秒...")
        start_time = time.time()
        running = True
        
        while time.time() - start_time < 2 and running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    running = False
                    break
            
            # 渲染一些内容
            surface.fill((0, 0, 0))
            pygame.display.flip()
            time.sleep(0.01)
        
        # 清理资源
        print("  清理资源...")
        pygame.quit()
        
        print(f"✓ 第 {i+1} 次运行完成")
        
        # 等待一段时间再进行下一次运行
        time.sleep(1)
    
    print("\n✓ 所有测试通过！")
    return True

if __name__ == "__main__":
    success = test_pygame_window_creation()
    if not success:
        print("\n测试失败！")
        sys.exit(1)