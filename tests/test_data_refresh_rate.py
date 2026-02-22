import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import numpy as np
from typing import Dict, Any
from src.audio.audio_parser import AudioParser
from src.audio.feature_extractor import FeatureExtractorManager, FeatureConfig
from src.audio.audio_feature_generator import AudioFeatureGenerator


def test_data_refresh_rate():
    """测试数据刷新率和窗体刷新率分离的效果"""
    
    print("=" * 60)
    print("数据刷新率与窗体刷新率分离测试")
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
    print(f"   - 特征类别: {list(features.keys())}")
    
    # 创建音频特征生成器
    print("\n3. 创建音频特征生成器...")
    feature_generator = AudioFeatureGenerator(
        audio_path=audio_path,
        full_features=features,
        audio_data=audio_data,
        sample_rate=audio_data.sr,
        hop_length=512,
        update_rate=120.0  # 数据刷新率：120 FPS
    )
    print(f"   ✓ 音频特征生成器创建成功")
    print(f"   - 数据刷新率: {feature_generator.update_rate} FPS")
    print(f"   - 更新间隔: {feature_generator.update_interval * 1000:.2f} ms")
    
    # 设置帧更新回调
    frame_updates = []
    def on_frame_update(frame_idx):
        frame_updates.append((time.time(), frame_idx))
    feature_generator.set_frame_update_callback(on_frame_update)
    
    # 启动生成器
    print("\n4. 启动音频特征生成器...")
    feature_generator.start()
    print(f"   ✓ 音频特征生成器已启动")
    
    # 模拟窗体刷新（60 FPS）
    print("\n5. 模拟窗体刷新（60 FPS）...")
    window_fps = 60.0
    window_interval = 1.0 / window_fps
    
    window_updates = []
    render_count = 0
    start_time = time.time()
    
    # 运行5秒
    duration = 5.0
    while time.time() - start_time < duration:
        # 获取最新的音频特征（模拟窗体刷新）
        audio_features = feature_generator.get_latest_features()
        
        if audio_features is not None:
            window_updates.append((time.time(), audio_features))
            render_count += 1
            
            # 检查是否有onset_envelope
            if "rhythm" in audio_features and "onset_envelope" in audio_features["rhythm"]:
                onset_env = audio_features["rhythm"]["onset_envelope"]
                if isinstance(onset_env, np.ndarray) and onset_env.size > 0:
                    current_intensity = float(onset_env[-1])
                    if render_count % 30 == 0:  # 每0.5秒打印一次
                        print(f"   - 窗体刷新 #{render_count}, onset_intensity: {current_intensity:.4f}")
        
        # 控制窗体刷新率
        time.sleep(window_interval)
    
    # 停止生成器
    print("\n6. 停止音频特征生成器...")
    feature_generator.stop()
    print(f"   ✓ 音频特征生成器已停止")
    
    # 统计结果
    print("\n" + "=" * 60)
    print("测试结果")
    print("=" * 60)
    
    # 数据刷新统计
    if frame_updates:
        data_update_times = [t[0] for t in frame_updates]
        data_update_count = len(frame_updates)
        data_update_rate = data_update_count / duration
        
        print(f"\n1. 数据刷新统计:")
        print(f"   - 数据更新次数: {data_update_count}")
        print(f"   - 实际数据刷新率: {data_update_rate:.2f} FPS")
        print(f"   - 目标数据刷新率: {feature_generator.update_rate:.2f} FPS")
        print(f"   - 刷新率差异: {abs(data_update_rate - feature_generator.update_rate):.2f} FPS")
        
        if abs(data_update_rate - feature_generator.update_rate) < 10:
            print(f"   ✓ 数据刷新率符合预期")
        else:
            print(f"   ✗ 数据刷新率偏差较大")
    else:
        print(f"\n1. 数据刷新统计:")
        print(f"   ✗ 没有数据更新记录")
    
    # 窗体刷新统计
    if window_updates:
        window_update_times = [t[0] for t in window_updates]
        window_update_count = len(window_updates)
        window_update_rate = window_update_count / duration
        
        print(f"\n2. 窗体刷新统计:")
        print(f"   - 窗体刷新次数: {window_update_count}")
        print(f"   - 实际窗体刷新率: {window_update_rate:.2f} FPS")
        print(f"   - 目标窗体刷新率: {window_fps:.2f} FPS")
        print(f"   - 刷新率差异: {abs(window_update_rate - window_fps):.2f} FPS")
        
        if abs(window_update_rate - window_fps) < 5:
            print(f"   ✓ 窗体刷新率符合预期")
        else:
            print(f"   ✗ 窗体刷新率偏差较大")
    else:
        print(f"\n2. 窗体刷新统计:")
        print(f"   ✗ 没有窗体更新记录")
    
    # 刷新率对比
    if frame_updates and window_updates:
        print(f"\n3. 刷新率对比:")
        print(f"   - 数据刷新率: {data_update_rate:.2f} FPS")
        print(f"   - 窗体刷新率: {window_update_rate:.2f} FPS")
        print(f"   - 比例: {data_update_rate / window_update_rate:.2f}x")
        
        if data_update_rate > window_update_rate:
            print(f"   ✓ 数据刷新率快于窗体刷新率，符合预期")
        else:
            print(f"   ✗ 数据刷新率不应慢于窗体刷新率")
    
    # 数据新鲜度统计
    if frame_updates and window_updates:
        print(f"\n4. 数据新鲜度统计:")
        
        # 计算每次窗体刷新时，数据更新的时间差
        data_freshness = []
        for window_time, _ in window_updates:
            # 找到最近的数据更新时间
            latest_data_time = max([t[0] for t in frame_updates if t[0] <= window_time])
            time_diff = window_time - latest_data_time
            data_freshness.append(time_diff)
        
        avg_freshness = np.mean(data_freshness) * 1000  # 转换为毫秒
        max_freshness = np.max(data_freshness) * 1000
        min_freshness = np.min(data_freshness) * 1000
        
        print(f"   - 平均数据新鲜度: {avg_freshness:.2f} ms")
        print(f"   - 最大数据新鲜度: {max_freshness:.2f} ms")
        print(f"   - 最小数据新鲜度: {min_freshness:.2f} ms")
        
        if avg_freshness < 10:
            print(f"   ✓ 数据新鲜度很好（< 10ms）")
        elif avg_freshness < 20:
            print(f"   △ 数据新鲜度良好（< 20ms）")
        else:
            print(f"   ✗ 数据新鲜度较差（> 20ms）")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    test_data_refresh_rate()
