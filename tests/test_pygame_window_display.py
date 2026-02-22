import sys
import os
import time
import pygame

def test_pygame_window_display():
    """测试pygame窗口是否正常显示"""
    print("开始测试pygame窗口是否正常显示...")
    
    # 测试运行2次
    for i in range(2):
        print(f"\n=== 第 {i+1} 次运行 ===")
        
        # 初始化pygame
        if pygame.get_init():
            pygame.quit()
            time.sleep(0.1)
        
        pygame.init()
        
        # 创建窗口
        surface = pygame.display.set_mode((640, 480))
        pygame.display.set_caption(f"Test Window {i+1}")
        print("✓ 窗口创建成功")
        
        # 显示窗口几秒钟
        print("  显示窗口3秒...")
        start_time = time.time()
        
        frame_count = 0
        while time.time() - start_time < 3:
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit()
                    return
            
            # 渲染一些内容
            surface.fill((0, 0, 0))
            
            # 绘制一些内容
            color = (255, 255, 255)
            pygame.draw.circle(surface, color, (320, 240), 50)
            
            # 更新显示
            pygame.display.flip()
            
            frame_count += 1
            
            # 控制帧率
            time.sleep(0.033)  # 约30fps
        
        print(f"✓ 渲染了 {frame_count} 帧")
        
        # 清理资源
        pygame.quit()
        
        print(f"✓ 第 {i+1} 次运行完成")
        
        # 等待一段时间再进行下一次运行
        time.sleep(1)
    
    print("\n✓ 所有测试通过！")
    return True

if __name__ == "__main__":
    success = test_pygame_window_display()
    if not success:
        print("\n测试失败！")
        sys.exit(1)