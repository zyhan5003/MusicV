import pygame
import numpy as np
import time
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.visual.renderer import VisualRenderer, VisualConfig
from src.visual.effects import RainEffect, FireEffect
from src.audio.feature_extractor import FeatureExtractorManager, FeatureConfig


def test_rain_effect_with_audio():
    """测试下雨特效与音频系统的协调"""
    print("=== 测试下雨特效与音频系统的协调 ===")
    
    # 初始化pygame
    pygame.init()
    
    # 创建窗口
    width, height = 640, 480
    surface = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Rain Effect Test")
    
    # 创建渲染器
    renderer = VisualRenderer()
    renderer.visual_config = VisualConfig(width=width, height=height, fps=30)
    renderer.surface = surface
    
    # 创建下雨特效
    rain_effect = RainEffect()
    rain_effect.initialize(surface, {"rain_count": 100, "rain_speed": 5.0, "rain_length": 10.0, "rain_color": "#3498db"})
    
    # 模拟音频特征
    def generate_audio_features():
        """生成模拟音频特征"""
        while True:
            # 模拟时域特征
            loudness = np.random.uniform(0.1, 1.0)
            zero_crossing_rate = np.random.uniform(0.0, 0.5)
            
            # 模拟频域特征
            spectrum = np.random.uniform(0, 1, (128, 1))
            spectral_centroid = np.random.uniform(1000, 5000)
            spectral_bandwidth = np.random.uniform(500, 2000)
            
            # 模拟节奏特征
            tempo = np.random.uniform(60, 180)
            beat_strength = np.random.uniform(0.0, 1.0)
            
            audio_features = {
                "temporal": {
                    "loudness": np.array([loudness]),
                    "zero_crossing_rate": np.array([zero_crossing_rate])
                },
                "frequency": {
                    "spectrum": spectrum,
                    "spectral_centroid": np.array([spectral_centroid]),
                    "spectral_bandwidth": np.array([spectral_bandwidth])
                },
                "rhythm": {
                    "tempo": np.array([tempo]),
                    "beat_strength": np.array([beat_strength])
                }
            }
            yield audio_features
            time.sleep(0.016)  # 约60fps
    
    # 运行测试
    features_generator = generate_audio_features()
    clock = pygame.time.Clock()
    running = True
    frame_count = 0
    max_frames = 180  # 运行约3秒
    
    print("开始测试下雨特效...")
    print("按ESC键或等待3秒自动退出")
    
    while running and frame_count < max_frames:
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # 获取音频特征
        try:
            audio_features = next(features_generator)
        except StopIteration:
            break
        
        # 更新特效
        rain_effect.update(audio_features)
        
        # 渲染
        surface.fill((26, 26, 26))
        rain_effect.render()
        pygame.display.flip()
        
        # 控制帧率
        clock.tick(30)
        frame_count += 1
        
        # 每60帧打印一次状态
        if frame_count % 60 == 0:
            loudness = np.mean(audio_features["temporal"]["loudness"])
            print(f"帧数: {frame_count}, 音量: {loudness:.2f}")
    
    print(f"✓ 下雨特效测试完成，共运行 {frame_count} 帧")
    
    # 清理
    pygame.quit()
    return True


def test_fire_effect_with_audio():
    """测试火焰特效与音频系统的协调"""
    print("\n=== 测试火焰特效与音频系统的协调 ===")
    
    # 初始化pygame
    pygame.init()
    
    # 创建窗口
    width, height = 640, 480
    surface = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Fire Effect Test")
    
    # 创建火焰特效
    fire_effect = FireEffect()
    fire_effect.initialize(surface, {"particle_count": 50, "spawn_rate": 0.1, "base_size": 5.0, "base_speed": 2.0, "fire_color": "#ff4500"})
    
    # 模拟音频特征
    def generate_audio_features():
        """生成模拟音频特征"""
        while True:
            # 模拟时域特征
            loudness = np.random.uniform(0.1, 1.0)
            zero_crossing_rate = np.random.uniform(0.0, 0.5)
            
            # 模拟频域特征
            spectrum = np.random.uniform(0, 1, (128, 1))
            spectral_centroid = np.random.uniform(1000, 5000)
            spectral_bandwidth = np.random.uniform(500, 2000)
            
            # 模拟节奏特征
            tempo = np.random.uniform(60, 180)
            beat_strength = np.random.uniform(0.0, 1.0)
            
            audio_features = {
                "temporal": {
                    "loudness": np.array([loudness]),
                    "zero_crossing_rate": np.array([zero_crossing_rate])
                },
                "frequency": {
                    "spectrum": spectrum,
                    "spectral_centroid": np.array([spectral_centroid]),
                    "spectral_bandwidth": np.array([spectral_bandwidth])
                },
                "rhythm": {
                    "tempo": np.array([tempo]),
                    "beat_strength": np.array([beat_strength])
                }
            }
            yield audio_features
            time.sleep(0.016)  # 约60fps
    
    # 运行测试
    features_generator = generate_audio_features()
    clock = pygame.time.Clock()
    running = True
    frame_count = 0
    max_frames = 180  # 运行约3秒
    
    print("开始测试火焰特效...")
    print("按ESC键或等待3秒自动退出")
    
    while running and frame_count < max_frames:
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # 获取音频特征
        try:
            audio_features = next(features_generator)
        except StopIteration:
            break
        
        # 更新特效
        fire_effect.update(audio_features)
        
        # 渲染
        surface.fill((26, 26, 26))
        fire_effect.render()
        pygame.display.flip()
        
        # 控制帧率
        clock.tick(30)
        frame_count += 1
        
        # 每60帧打印一次状态
        if frame_count % 60 == 0:
            loudness = np.mean(audio_features["temporal"]["loudness"])
            print(f"帧数: {frame_count}, 音量: {loudness:.2f}")
    
    print(f"✓ 火焰特效测试完成，共运行 {frame_count} 帧")
    
    # 清理
    pygame.quit()
    return True


if __name__ == "__main__":
    try:
        # 测试下雨特效
        rain_success = test_rain_effect_with_audio()
        
        # 等待一下
        time.sleep(1)
        
        # 测试火焰特效
        fire_success = test_fire_effect_with_audio()
        
        if rain_success and fire_success:
            print("\n✓ 所有特效测试通过！")
        else:
            print("\n✗ 部分特效测试失败！")
    except Exception as e:
        print(f"\n✗ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()