import threading
import time
import numpy as np
from typing import Dict, Any, Optional, Callable
from collections import deque


class AudioFeatureBuffer:
    """音频特征缓冲区，用于线程安全的数据共享"""
    
    def __init__(self, max_size: int = 10):
        """
        初始化音频特征缓冲区
        
        Args:
            max_size: 缓冲区最大大小
        """
        self.max_size = max_size
        self.buffer: deque = deque(maxlen=max_size)
        self.lock = threading.Lock()
        self.current_features: Optional[Dict[str, Any]] = None
        self.latest_timestamp: float = 0.0
    
    def put(self, features: Dict[str, Any], timestamp: float) -> None:
        """
        添加音频特征到缓冲区
        
        Args:
            features: 音频特征字典
            timestamp: 时间戳
        """
        with self.lock:
            self.buffer.append((features, timestamp))
            self.current_features = features
            self.latest_timestamp = timestamp
    
    def get_latest(self) -> Optional[Dict[str, Any]]:
        """
        获取最新的音频特征
        
        Returns:
            最新的音频特征字典，如果没有则返回None
        """
        with self.lock:
            return self.current_features
    
    def get_latest_with_timestamp(self) -> tuple[Optional[Dict[str, Any]], float]:
        """
        获取最新的音频特征和时间戳
        
        Returns:
            (最新的音频特征字典, 时间戳)
        """
        with self.lock:
            return self.current_features, self.latest_timestamp
    
    def get_features_at_time(self, timestamp: float, tolerance: float = 0.05) -> Optional[Dict[str, Any]]:
        """
        获取指定时间附近的音频特征
        
        Args:
            timestamp: 目标时间戳
            tolerance: 时间容差（秒）
        
        Returns:
            最接近的音频特征字典，如果没有则返回None
        """
        with self.lock:
            if not self.buffer:
                return None
            
            # 查找最接近的时间戳
            best_features = None
            best_diff = float('inf')
            
            for features, ts in self.buffer:
                diff = abs(ts - timestamp)
                if diff < tolerance and diff < best_diff:
                    best_features = features
                    best_diff = diff
            
            return best_features
    
    def clear(self) -> None:
        """清空缓冲区"""
        with self.lock:
            self.buffer.clear()
            self.current_features = None
            self.latest_timestamp = 0.0


class AudioFeatureGenerator:
    """音频特征生成器，在独立线程中运行"""
    
    def __init__(
        self,
        audio_path: str,
        full_features: Dict[str, Any],
        audio_data,
        sample_rate: int,
        hop_length: int = 512,
        update_rate: float = 120.0
    ):
        """
        初始化音频特征生成器
        
        Args:
            audio_path: 音频文件路径
            full_features: 完整的音频特征
            audio_data: 音频数据
            sample_rate: 采样率
            hop_length: 跳跃长度
            update_rate: 数据更新率（FPS）
        """
        self.audio_path = audio_path
        self.full_features = full_features
        self.audio_data = audio_data
        self.sample_rate = sample_rate
        self.hop_length = hop_length
        self.update_rate = update_rate
        self.update_interval = 1.0 / update_rate
        
        # 音频播放相关
        self.sound = None
        self.start_time = 0.0
        self.total_duration = audio_data.duration
        self.is_playing = False
        
        # 特征缓冲区
        self.buffer = AudioFeatureBuffer(max_size=10)
        
        # 线程控制
        self.thread: Optional[threading.Thread] = None
        self.running = False
        self.lock = threading.Lock()
        
        # 回调函数
        self.on_frame_update: Optional[Callable[[int], None]] = None
    
    def set_frame_update_callback(self, callback: Callable[[int], None]) -> None:
        """
        设置帧更新回调函数
        
        Args:
            callback: 回调函数，接收当前帧索引
        """
        self.on_frame_update = callback
    
    def _generate_real_time_features(self, elapsed_time: float) -> Dict[str, Any]:
        """
        生成实时特征
        
        Args:
            elapsed_time: 已播放时间（秒）
        
        Returns:
            实时特征字典
        """
        # 计算当前帧索引
        current_frame = int(elapsed_time * self.sample_rate / self.hop_length)
        
        # 创建实时特征字典
        real_time_features = {}
        
        # 时域特征
        if "temporal" in self.full_features:
            temporal_features = self.full_features["temporal"]
            real_time_temporal = {}
            
            # 提取当前帧附近的响度
            if "loudness" in temporal_features:
                loudness = temporal_features["loudness"]
                frame_idx = min(current_frame, len(loudness) - 1)
                real_time_temporal["loudness"] = np.array([loudness[frame_idx]])
            
            # 提取当前帧附近的振幅
            if "amplitude" in temporal_features:
                amplitude = temporal_features["amplitude"]
                window_size = 1000
                sample_idx = int(elapsed_time * self.sample_rate)
                sample_idx = min(sample_idx, len(amplitude) - 1)
                
                start_idx = max(0, sample_idx - window_size // 2)
                end_idx = min(len(amplitude), start_idx + window_size)
                
                if end_idx - start_idx < window_size:
                    if start_idx == 0:
                        pad_size = window_size - (end_idx - start_idx)
                        padded_amplitude = np.pad(
                            amplitude[:end_idx], 
                            (0, pad_size), 
                            mode='constant'
                        )
                    else:
                        pad_size = window_size - (end_idx - start_idx)
                        padded_amplitude = np.pad(
                            amplitude[start_idx:], 
                            (pad_size, 0), 
                            mode='constant'
                        )
                else:
                    padded_amplitude = amplitude[start_idx:end_idx]
                
                real_time_temporal["amplitude"] = padded_amplitude
            
            real_time_features["temporal"] = real_time_temporal
        
        # 频域特征
        if "frequency" in self.full_features:
            frequency_features = self.full_features["frequency"]
            real_time_frequency = {}
            
            # 提取当前帧附近的梅尔频谱
            if "mel_spectrogram" in frequency_features:
                mel_spec = frequency_features["mel_spectrogram"]
                frame_idx = min(current_frame, mel_spec.shape[1] - 1)
                real_time_frequency["mel_spectrogram"] = mel_spec[:, frame_idx:frame_idx+1]
            
            # 提取当前帧附近的频谱
            if "spectrum" in frequency_features:
                spectrum = frequency_features["spectrum"]
                frame_idx = min(current_frame, spectrum.shape[1] - 1)
                real_time_frequency["spectrum"] = spectrum[:, frame_idx:frame_idx+1]
            
            # 提取当前帧附近的对数梅尔频谱
            if "log_mel_spectrogram" in frequency_features:
                log_mel_spec = frequency_features["log_mel_spectrogram"]
                frame_idx = min(current_frame, log_mel_spec.shape[1] - 1)
                real_time_frequency["log_mel_spectrogram"] = log_mel_spec[:, frame_idx:frame_idx+1]
            
            real_time_features["frequency"] = real_time_frequency
        
        # 节奏特征
        if "rhythm" in self.full_features:
            rhythm_features = self.full_features["rhythm"]
            real_time_rhythm = {}
            
            # 复制节奏特征（这些是全局特征）
            real_time_rhythm["bpm"] = rhythm_features.get("bpm", 0)
            real_time_rhythm["beat_frames"] = rhythm_features.get("beat_frames", np.array([]))
            real_time_rhythm["beat_times"] = rhythm_features.get("beat_times", np.array([]))
            
            # 提取onset_envelope
            if "onset_envelope" in rhythm_features:
                onset_env = rhythm_features["onset_envelope"]
                frame_idx = min(current_frame, len(onset_env) - 1)
                # 提取当前帧附近的onset_envelope
                window_size = min(20, len(onset_env))
                start_idx = max(0, frame_idx - window_size // 2)
                end_idx = min(len(onset_env), frame_idx + window_size // 2 + 1)
                real_time_rhythm["onset_envelope"] = onset_env[start_idx:end_idx]
            
            # 检查当前是否有节拍
            if "beat_times" in rhythm_features:
                beat_times = rhythm_features["beat_times"]
                for beat_time in beat_times:
                    if abs(beat_time - elapsed_time) < 0.1:
                        real_time_rhythm["is_beat"] = True
                        break
                else:
                    real_time_rhythm["is_beat"] = False
            
            real_time_features["rhythm"] = real_time_rhythm
        
        # 音色特征
        if "timbre" in self.full_features:
            timbre_features = self.full_features["timbre"]
            real_time_timbre = {}
            
            # 提取当前帧附近的谱质心
            if "spectral_centroid" in timbre_features:
                spectral_centroid = timbre_features["spectral_centroid"]
                frame_idx = min(current_frame, len(spectral_centroid) - 1)
                real_time_timbre["spectral_centroid"] = np.array([spectral_centroid[frame_idx]])
            
            real_time_features["timbre"] = real_time_timbre
        
        return real_time_features
    
    def _update_loop(self) -> None:
        """数据更新循环"""
        import pygame.mixer
        
        while self.running:
            # 检查是否在播放
            if not self.is_playing:
                time.sleep(0.01)
                continue
            
            # 计算当前播放位置
            current_time = pygame.time.get_ticks() / 1000.0
            elapsed_time = current_time - self.start_time
            elapsed_time = min(elapsed_time, self.total_duration)
            
            # 检查音频是否在播放
            if not pygame.mixer.get_busy():
                if elapsed_time >= self.total_duration:
                    break
                time.sleep(0.01)
                continue
            
            # 计算当前帧索引
            current_frame = int(elapsed_time * self.sample_rate / self.hop_length)
            
            # 调用帧更新回调
            if self.on_frame_update:
                self.on_frame_update(current_frame)
            
            # 生成实时特征
            real_time_features = self._generate_real_time_features(elapsed_time)
            
            # 添加到缓冲区
            self.buffer.put(real_time_features, elapsed_time)
            
            # 控制更新率
            time.sleep(self.update_interval)
    
    def start(self) -> None:
        """启动音频特征生成器"""
        import pygame.mixer
        
        with self.lock:
            if self.running:
                return
            
            # 确保mixer模块已初始化
            if not pygame.mixer.get_init():
                try:
                    pygame.mixer.init(frequency=self.sample_rate)
                except Exception as e:
                    print(f"pygame.mixer初始化失败: {e}")
                    return
            else:
                # 如果mixer已初始化，检查采样率是否匹配
                current_freq = pygame.mixer.get_init()[0]
                if current_freq != self.sample_rate:
                    # 采样率不匹配，需要重新初始化
                    try:
                        pygame.mixer.quit()
                        pygame.mixer.init(frequency=self.sample_rate)
                    except Exception as e:
                        print(f"pygame.mixer重新初始化失败: {e}")
                        return
            
            # 加载音频
            try:
                self.sound = pygame.mixer.Sound(self.audio_path)
                self.sound.set_volume(1.0)
            except Exception as e:
                print(f"加载音频文件失败: {e}")
                return
            
            # 开始播放
            try:
                self.sound.play()
                self.is_playing = True
            except Exception as e:
                print(f"播放音频失败: {e}")
                return
            
            # 记录开始时间
            self.start_time = pygame.time.get_ticks() / 1000.0
            
            # 启动线程
            self.running = True
            self.thread = threading.Thread(target=self._update_loop, daemon=True)
            self.thread.start()
    
    def stop(self) -> None:
        """停止音频特征生成器"""
        import pygame.mixer
        
        with self.lock:
            if not self.running:
                return
            
            self.running = False
            self.is_playing = False
        
        # 等待线程结束
        if self.thread:
            self.thread.join(timeout=1.0)
            self.thread = None
        
        # 停止音频播放
        if self.sound:
            self.sound.stop()
            self.sound = None
        
        # 停止mixer（但不退出mixer模块）
        if pygame.mixer.get_busy():
            pygame.mixer.stop()
        
        # 清空缓冲区
        self.buffer.clear()
    
    def get_latest_features(self) -> Optional[Dict[str, Any]]:
        """
        获取最新的音频特征
        
        Returns:
            最新的音频特征字典，如果没有则返回None
        """
        return self.buffer.get_latest()
    
    def is_running(self) -> bool:
        """检查是否正在运行"""
        with self.lock:
            return self.running
    
    def get_elapsed_time(self) -> float:
        """
        获取已播放时间
        
        Returns:
            已播放时间（秒）
        """
        import pygame.mixer
        if not self.is_playing:
            return 0.0
        
        current_time = pygame.time.get_ticks() / 1000.0
        elapsed_time = current_time - self.start_time
        return min(elapsed_time, self.total_duration)
