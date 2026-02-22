"""
测试节拍强度变化
"""
import pygame
import numpy as np
from src.audio.audio_parser import AudioParser
from src.audio.feature_extractor import FeatureExtractor
from src.visual.effects.beat_utils import BeatStrengthTracker


def test_beat_strength():
    """测试节拍强度变化"""
    print("=== 节拍强度测试 ===\n")
    
    # 初始化pygame
    pygame.init()
    
    # 创建测试窗口
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("节拍强度测试")
    
    # 加载音频文件
    audio_file = "test_audio.mp3"
    print(f"加载音频文件: {audio_file}")
    
    try:
        audio_parser = AudioParser(audio_file)
        audio_data, sample_rate = audio_parser.parse()
        print(f"音频数据形状: {audio_data.shape}, 采样率: {sample_rate}")
    except Exception as e:
        print(f"加载音频失败: {e}")
        print("请确保test_audio.mp3文件存在")
        return
    
    # 提取特征
    print("提取音频特征...")
    feature_extractor = FeatureExtractor()
    features = feature_extractor.extract(audio_data, sample_rate)
    print(f"特征提取完成")
    
    # 创建节拍强度跟踪器
    beat_tracker = BeatStrengthTracker(smoothing_factor=0.1)
    
    # 模拟播放
    clock = pygame.time.Clock()
    frame_count = 0
    running = True
    
    print("\n开始模拟播放...")
    print("按ESC键退出\n")
    
    # 节拍强度历史
    beat_strengths = []
    
    while running and frame_count < len(features.get("temporal", {}).get("loudness", [])):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # 获取当前帧的特征
        current_frame = frame_count
        
        # 构建音频特征字典
        audio_features = {
            "temporal": {
                "loudness": features["temporal"]["loudness"][current_frame:current_frame+1] if current_frame < len(features["temporal"]["loudness"]) else np.array([0.0])
            },
            "frequency": {
                "spectral_centroid": features["frequency"]["spectral_centroid"][current_frame:current_frame+1] if current_frame < len(features["frequency"]["spectral_centroid"]) else np.array([0.0])
            },
            "rhythm": {
                "beat_strength": features["rhythm"]["beat_strength"][current_frame:current_frame+1] if current_frame < len(features["rhythm"]["beat_strength"]) else np.array([0.0])
            }
        }
        
        # 更新节拍强度
        beat_strength = beat_tracker.update(audio_features)
        beat_strengths.append(beat_strength)
        
        # 每60帧打印一次
        if frame_count % 60 == 0:
            print(f"帧 {frame_count}: 节拍强度 = {beat_strength:.4f}, 原始值 = {audio_features['rhythm']['beat_strength'][0] if len(audio_features['rhythm']['beat_strength']) > 0 else 0.0:.4f}")
        
        # 绘制
        screen.fill((0, 0, 0))
        
        # 绘制节拍强度曲线
        if len(beat_strengths) > 1:
            points = []
            for i, bs in enumerate(beat_strengths[-300:]):  # 只显示最近300帧
                x = int(i * (width / 300))
                y = int(height - bs * height)
                points.append((x, y))
            
            if len(points) > 1:
                pygame.draw.lines(screen, (0, 255, 0), False, points, 2)
        
        # 显示当前节拍强度
        font = pygame.font.Font(None, 36)
        text = font.render(f"节拍强度: {beat_strength:.4f}", True, (255, 255, 255))
        screen.blit(text, (10, 10))
        
        pygame.display.flip()
        clock.tick(60)
        frame_count += 1
    
    # 打印统计信息
    print(f"\n=== 统计信息 ===")
    print(f"总帧数: {len(beat_strengths)}")
    print(f"节拍强度范围: [{min(beat_strengths):.4f}, {max(beat_strengths):.4f}]")
    print(f"平均节拍强度: {np.mean(beat_strengths):.4f}")
    print(f"前100帧平均: {np.mean(beat_strengths[:100]):.4f}")
    print(f"后100帧平均: {np.mean(beat_strengths[-100:]):.4f}")
    
    pygame.quit()


if __name__ == "__main__":
    test_beat_strength()
