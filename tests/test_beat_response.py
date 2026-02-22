import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
import numpy as np
import librosa
from typing import Dict, Any
from src.visual.effects.rain_effect import RainEffect
from src.visual.effects.fire_effect import FireEffect
from src.visual.effects.snow_effect import SnowEffect


def create_mock_audio_features(beat_strength: float) -> Dict[str, Any]:
    """创建模拟的音频特征"""
    # 创建模拟的onset_envelope数据
    onset_envelope = np.random.uniform(0, 1, 100)
    # 根据节拍强度调整onset_envelope的强度
    onset_envelope = onset_envelope * (0.1 + beat_strength * 0.9)
    
    return {
        "temporal": {
            "loudness": np.array([0.5 + beat_strength * 0.5]),
            "amplitude": np.random.uniform(-1, 1, 512)
        },
        "frequency": {
            "spectrum": np.random.uniform(0, 1, (1025, 100)),
            "spectral_centroid": np.array([2500.0])
        },
        "rhythm": {
            "bpm": 120.0,
            "beat_frames": np.array([10, 20, 30]),
            "beat_times": np.array([0.1, 0.2, 0.3]),
            "beat_strength": np.array([beat_strength]),
            "onset_envelope": onset_envelope  # 添加onset_envelope
        },
        "timbre": {
            "mfcc": np.random.uniform(-10, 10, (20, 100)),
            "spectral_centroid": np.array([2500.0])
        }
    }


def test_rain_effect():
    """测试雨特效的节拍响应"""
    print("=== 测试雨特效的节拍响应 ===")
    
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("雨特效节拍响应测试")
    clock = pygame.time.Clock()
    
    # 创建雨特效
    rain_effect = RainEffect()
    config = {
        "base_rain_count": 8,
        "max_rain_count": 20,
        "rain_speed": 5.0,
        "rain_length": 10.0,
        "rain_color": "#3498db",
        "smoothing_factor": 0.3
    }
    rain_effect.initialize(screen, config)
    
    # 测试不同的节拍强度
    beat_strengths = [0.2, 0.5, 0.9]
    current_beat_index = 0
    frame_count = 0
    frames_per_beat = 120  # 每2秒切换一次节拍强度
    
    print("测试不同的节拍强度：")
    for i, beat_strength in enumerate(beat_strengths):
        print(f"  {i+1}. 节拍强度: {beat_strength:.1f}")
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # 切换节拍强度
        if frame_count % frames_per_beat == 0:
            current_beat_index = (current_beat_index + 1) % len(beat_strengths)
            current_beat = beat_strengths[current_beat_index]
            print(f"\n切换到节拍强度: {current_beat:.1f}")
        
        # 获取当前节拍强度
        current_beat = beat_strengths[current_beat_index]
        
        # 创建音频特征
        audio_features = create_mock_audio_features(current_beat)
        
        # 更新和渲染特效
        screen.fill((20, 20, 30))
        rain_effect.update(audio_features, 0.016)
        rain_effect.render(screen)
        
        # 显示信息
        font = pygame.font.Font(None, 36)
        info_text = f"节拍强度: {current_beat:.2f}"
        text_surface = font.render(info_text, True, (255, 255, 255))
        screen.blit(text_surface, (10, 10))
        
        # 显示雨滴数量
        rain_count_text = f"雨滴数量: {len(rain_effect.rain_drops)}"
        rain_count_surface = font.render(rain_count_text, True, (255, 255, 255))
        screen.blit(rain_count_surface, (10, 50))
        
        pygame.display.flip()
        clock.tick(60)
        frame_count += 1
    
    pygame.quit()
    print("\n✓ 雨特效测试完成")


def test_fire_effect():
    """测试火特效的节拍响应"""
    print("=== 测试火特效的节拍响应 ===")
    
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("火特效节拍响应测试")
    clock = pygame.time.Clock()
    
    # 创建火特效
    fire_effect = FireEffect()
    config = {
        "base_particle_count": 10,
        "max_particle_count": 25,
        "base_spawn_rate": 0.1,
        "max_spawn_rate": 0.3,
        "base_size": 5.0,
        "base_speed": 2.0,
        "fire_color": "#ff4500",
        "base_x": 400,
        "base_y": 550,
        "smoothing_factor": 0.3
    }
    fire_effect.initialize(screen, config)
    
    # 测试不同的节拍强度
    beat_strengths = [0.2, 0.5, 0.9]
    current_beat_index = 0
    frame_count = 0
    frames_per_beat = 120  # 每2秒切换一次节拍强度
    
    print("测试不同的节拍强度：")
    for i, beat_strength in enumerate(beat_strengths):
        print(f"  {i+1}. 节拍强度: {beat_strength:.1f}")
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # 切换节拍强度
        if frame_count % frames_per_beat == 0:
            current_beat_index = (current_beat_index + 1) % len(beat_strengths)
            current_beat = beat_strengths[current_beat_index]
            print(f"\n切换到节拍强度: {current_beat:.1f}")
        
        # 获取当前节拍强度
        current_beat = beat_strengths[current_beat_index]
        
        # 创建音频特征
        audio_features = create_mock_audio_features(current_beat)
        
        # 更新和渲染特效
        screen.fill((20, 20, 30))
        fire_effect.update(audio_features, 0.016)
        fire_effect.render(screen)
        
        # 显示信息
        font = pygame.font.Font(None, 36)
        info_text = f"节拍强度: {current_beat:.2f}"
        text_surface = font.render(info_text, True, (255, 255, 255))
        screen.blit(text_surface, (10, 10))
        
        # 显示粒子数量
        particle_count_text = f"粒子数量: {len(fire_effect.particles)}"
        particle_count_surface = font.render(particle_count_text, True, (255, 255, 255))
        screen.blit(particle_count_surface, (10, 50))
        
        pygame.display.flip()
        clock.tick(60)
        frame_count += 1
    
    pygame.quit()
    print("\n✓ 火特效测试完成")


def test_snow_effect():
    """测试雪特效的节拍响应"""
    print("=== 测试雪特效的节拍响应 ===")
    
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("雪特效节拍响应测试")
    clock = pygame.time.Clock()
    
    # 创建雪特效
    snow_effect = SnowEffect()
    config = {
        "base_snow_count": 4,
        "max_snow_count": 12,
        "snow_speed": 2.0,
        "snow_size": 3.0,
        "snow_drift": 0.5,
        "snow_color": "#FFFFFF",
        "smoothing_factor": 0.3
    }
    snow_effect.initialize(screen, config)
    
    # 测试不同的节拍强度
    beat_strengths = [0.2, 0.5, 0.9]
    current_beat_index = 0
    frame_count = 0
    frames_per_beat = 120  # 每2秒切换一次节拍强度
    
    print("测试不同的节拍强度：")
    for i, beat_strength in enumerate(beat_strengths):
        print(f"  {i+1}. 节拍强度: {beat_strength:.1f}")
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # 切换节拍强度
        if frame_count % frames_per_beat == 0:
            current_beat_index = (current_beat_index + 1) % len(beat_strengths)
            current_beat = beat_strengths[current_beat_index]
            print(f"\n切换到节拍强度: {current_beat:.1f}")
        
        # 获取当前节拍强度
        current_beat = beat_strengths[current_beat_index]
        
        # 创建音频特征
        audio_features = create_mock_audio_features(current_beat)
        
        # 更新和渲染特效
        screen.fill((20, 20, 30))
        snow_effect.update(audio_features, 0.016)
        snow_effect.render(screen)
        
        # 显示信息
        font = pygame.font.Font(None, 36)
        info_text = f"节拍强度: {current_beat:.2f}"
        text_surface = font.render(info_text, True, (255, 255, 255))
        screen.blit(text_surface, (10, 10))
        
        # 显示雪花数量
        snow_count_text = f"雪花数量: {len(snow_effect.snowflakes)}"
        snow_count_surface = font.render(snow_count_text, True, (255, 255, 255))
        screen.blit(snow_count_surface, (10, 50))
        
        pygame.display.flip()
        clock.tick(60)
        frame_count += 1
    
    pygame.quit()
    print("\n✓ 雪特效测试完成")


def main():
    """主测试函数"""
    print("=== 粒子特效节拍响应测试 ===")
    print("\n请选择要测试的特效：")
    print("1. 雨特效")
    print("2. 火特效")
    print("3. 雪特效")
    print("4. 全部测试")
    
    choice = input("\n请输入选项 (1-4): ").strip()
    
    if choice == "1":
        test_rain_effect()
    elif choice == "2":
        test_fire_effect()
    elif choice == "3":
        test_snow_effect()
    elif choice == "4":
        test_rain_effect()
        test_fire_effect()
        test_snow_effect()
    else:
        print("无效的选项")
    
    print("\n✓ 所有测试完成！")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n✗ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()