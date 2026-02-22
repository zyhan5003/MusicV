import pygame
import numpy as np
import time
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.visual.renderer import VisualRenderer, VisualConfig
from src.visual.effects import RainEffect, SnowEffect, FireEffect


def test_all_weather_effects():
    """测试所有天气特效与音频系统的协调"""
    print("=== 测试所有天气特效与音频系统的协调 ===")
    
    # 初始化pygame
    pygame.init()
    
    # 创建窗口
    width, height = 640, 480
    surface = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Weather Effects Test")
    
    # 创建渲染器
    renderer = VisualRenderer()
    renderer.visual_config = VisualConfig(width=width, height=height, fps=30)
    renderer.surface = surface
    
    # 创建特效
    effects = [
        ("下雨特效", RainEffect(), {"rain_count": 100, "rain_speed": 5.0, "rain_length": 10.0, "rain_color": "#3498db"}),
        ("下雪特效", SnowEffect(), {"snow_count": 100, "snow_speed": 2.0, "snow_size": 3.0, "snow_drift": 0.5, "snow_color": "#FFFFFF"}),
        ("火焰特效", FireEffect(), {"particle_count": 50, "spawn_rate": 0.1, "base_size": 5.0, "base_speed": 2.0, "fire_color": "#ff4500"})
    ]
    
    # 初始化所有特效
    for name, effect, config in effects:
        effect.initialize(surface, config)
    
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
    current_effect_index = 0
    frames_per_effect = 180  # 每个特效运行约3秒
    max_frames = len(effects) * frames_per_effect
    
    print("开始测试天气特效...")
    print("按ESC键或等待9秒自动退出")
    
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
        
        # 切换特效
        if frame_count % frames_per_effect == 0:
            current_effect_index = frame_count // frames_per_effect
            if current_effect_index < len(effects):
                print(f"\n切换到: {effects[current_effect_index][0]}")
        
        # 更新当前特效
        if current_effect_index < len(effects):
            effect_name, effect, config = effects[current_effect_index]
            effect._update_effect(audio_features)
            
            # 渲染
            surface.fill((26, 26, 26))
            effect._render_effect()
            
            # 显示特效名称
            font = pygame.font.Font(None, 36)
            text = font.render(effect_name, True, (255, 255, 255))
            surface.blit(text, (10, 10))
            
            # 显示音频特征
            font_small = pygame.font.Font(None, 24)
            loudness = np.mean(audio_features["temporal"]["loudness"])
            beat_strength = np.mean(audio_features["rhythm"]["beat_strength"])
            spectral_centroid = np.mean(audio_features["frequency"]["spectral_centroid"])
            
            info_text = f"音量: {loudness:.2f} | 节奏: {beat_strength:.2f} | 频谱: {spectral_centroid:.0f}"
            info_surface = font_small.render(info_text, True, (200, 200, 200))
            surface.blit(info_surface, (10, 50))
            
            pygame.display.flip()
        
        # 控制帧率
        clock.tick(30)
        frame_count += 1
        
        # 每60帧打印一次状态
        if frame_count % 60 == 0:
            loudness = np.mean(audio_features["temporal"]["loudness"])
            beat_strength = np.mean(audio_features["rhythm"]["beat_strength"])
            spectral_centroid = np.mean(audio_features["frequency"]["spectral_centroid"])
            print(f"帧数: {frame_count}, 音量: {loudness:.2f}, 节奏: {beat_strength:.2f}, 频谱: {spectral_centroid:.0f}")
    
    print(f"\n✓ 天气特效测试完成，共运行 {frame_count} 帧")
    
    # 清理
    pygame.quit()
    return True


if __name__ == "__main__":
    try:
        success = test_all_weather_effects()
        if success:
            print("\n✓ 所有天气特效测试通过！")
        else:
            print("\n✗ 天气特效测试失败！")
    except Exception as e:
        print(f"\n✗ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()