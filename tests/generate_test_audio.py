import numpy as np
import soundfile as sf
import os

def generate_test_audio(filename="test_audio.wav", duration=5, sample_rate=44100):
    """生成测试音频文件"""
    print(f"生成测试音频文件: {filename}")
    
    # 生成时间轴
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    
    # 生成一个简单的音频信号（包含多个频率）
    audio = (np.sin(2 * np.pi * 440 * t) * 0.3 +  # A4音符
             np.sin(2 * np.pi * 880 * t) * 0.2 +  # A5音符
             np.sin(2 * np.pi * 1320 * t) * 0.1)  # E6音符
    
    # 添加一些节奏（通过振幅调制）
    beat_freq = 2  # 每秒2拍
    envelope = 0.5 + 0.5 * np.sin(2 * np.pi * beat_freq * t)
    audio = audio * envelope
    
    # 归一化到[-1, 1]范围
    audio = audio / np.max(np.abs(audio))
    
    # 转换为立体声
    audio_stereo = np.column_stack((audio, audio))
    
    # 保存音频文件
    sf.write(filename, audio_stereo, sample_rate)
    
    print(f"✓ 测试音频文件已生成: {filename}")
    print(f"  时长: {duration}秒")
    print(f"  采样率: {sample_rate}Hz")
    print(f"  声道: 立体声")

if __name__ == "__main__":
    # 生成测试音频
    generate_test_audio()
