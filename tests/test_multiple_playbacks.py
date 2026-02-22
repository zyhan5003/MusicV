import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from src.audio.audio_parser import AudioParser
from src.audio.feature_extractor import FeatureExtractorManager, FeatureConfig
from src.audio.audio_feature_generator import AudioFeatureGenerator


def test_multiple_playbacks():
    """测试多次播放"""
    
    print("=" * 60)
    print("多次播放测试")
    print("=" * 60)
    
    # 测试音频文件
    audio_path = "test_audio.wav"
    
    if not os.path.exists(audio_path):
        print(f"错误：找不到测试音频文件 {audio_path}")
        return
    
    # 加载音频
    print("\n1. 加载音频...")
    audio_parser = AudioParser()
    audio_data = audio_parser.load_audio(audio_path)
    print(f"   ✓ 音频加载成功")
    print(f"   - 采样率: {audio_data.sr} Hz")
    print(f"   - 时长: {audio_data.duration:.2f} 秒")
    
    # 提取特征
    print("\n2. 提取音频特征...")
    feature_extractor = FeatureExtractorManager()
    feature_config = FeatureConfig()
    features = feature_extractor.extract_all(audio_data.y, audio_data.sr, feature_config)
    print(f"   ✓ 特征提取成功")
    
    # 测试多次播放
    for play_count in range(1, 4):
        print(f"\n{'=' * 60}")
        print(f"第 {play_count} 次播放")
        print(f"{'=' * 60}")
        
        # 创建音频特征生成器
        print(f"\n{play_count}.1 创建音频特征生成器...")
        feature_generator = AudioFeatureGenerator(
            audio_path=audio_path,
            full_features=features,
            audio_data=audio_data,
            sample_rate=audio_data.sr,
            hop_length=512,
            update_rate=120.0
        )
        print(f"   ✓ 音频特征生成器创建成功")
        
        # 设置帧更新回调
        frame_updates = []
        def on_frame_update(frame_idx):
            frame_updates.append((time.time(), frame_idx))
        feature_generator.set_frame_update_callback(on_frame_update)
        
        # 启动生成器
        print(f"\n{play_count}.2 启动音频特征生成器...")
        feature_generator.start()
        print(f"   ✓ 音频特征生成器已启动")
        
        # 模拟播放3秒
        print(f"\n{play_count}.3 模拟播放3秒...")
        start_time = time.time()
        render_count = 0
        
        while time.time() - start_time < 3.0:
            audio_features = feature_generator.get_latest_features()
            
            if audio_features is not None:
                render_count += 1
                
                # 检查是否有onset_envelope
                if "rhythm" in audio_features and "onset_envelope" in audio_features["rhythm"]:
                    onset_env = audio_features["rhythm"]["onset_envelope"]
                    if isinstance(onset_env, np.ndarray) and onset_env.size > 0:
                        current_intensity = float(onset_env[-1])
                        if render_count % 30 == 0:  # 每0.5秒打印一次
                            print(f"   - 渲染 #{render_count}, onset_intensity: {current_intensity:.4f}")
            
            time.sleep(0.016)  # 模拟60 FPS
        
        # 停止生成器
        print(f"\n{play_count}.4 停止音频特征生成器...")
        feature_generator.stop()
        print(f"   ✓ 音频特征生成器已停止")
        
        # 统计结果
        print(f"\n{play_count}.5 统计结果:")
        print(f"   - 渲染次数: {render_count}")
        print(f"   - 帧更新次数: {len(frame_updates)}")
        
        if render_count > 0:
            print(f"   ✓ 第 {play_count} 次播放成功")
        else:
            print(f"   ✗ 第 {play_count} 次播放失败（没有渲染）")
        
        # 等待一下，确保资源释放
        time.sleep(0.5)
    
    print(f"\n{'=' * 60}")
    print("测试完成")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    import numpy as np
    test_multiple_playbacks()
