import numpy as np
from typing import Dict, Any


def calculate_mel_intensity(audio_features: Dict[str, Any], previous_intensity: float = 0.0, 
                        smoothing_factor: float = 0.3) -> float:
    """
    从梅尔频谱中提取强度值
    
    Args:
        audio_features: 音频特征字典
        previous_intensity: 上一帧的强度（用于平滑）
        smoothing_factor: 平滑因子
    
    Returns:
        梅尔强度 (0.0 - 1.0)
    """
    # 从频域特征中提取梅尔频谱
    current_intensity = 0.0
    
    if "frequency" in audio_features:
        # 优先使用对数梅尔频谱
        if "log_mel_spectrogram" in audio_features["frequency"]:
            mel_data = audio_features["frequency"]["log_mel_spectrogram"]
            
            if isinstance(mel_data, np.ndarray):
                if mel_data.ndim == 2 and mel_data.size > 0:
                    # 计算当前帧的平均强度
                    current_intensity = float(np.mean(np.abs(mel_data[:, -1])))
                    # 归一化到0-1范围（假设对数梅尔频谱的范围是-80到0）
                    current_intensity = (current_intensity + 80) / 80.0
                    current_intensity = max(0.0, min(1.0, current_intensity))
    
    # 应用平滑
    smoothing_factor = max(0.0, min(1.0, smoothing_factor))
    smoothed_intensity = previous_intensity + smoothing_factor * (current_intensity - previous_intensity)
    
    return smoothed_intensity


class MelIntensityTracker:
    """梅尔强度跟踪器，用于平滑梅尔强度变化"""
    
    def __init__(self, smoothing_factor: float = 0.3):
        """
        初始化梅尔强度跟踪器
        
        Args:
            smoothing_factor: 平滑因子 (0.0 - 1.0)
        """
        self.smoothing_factor = smoothing_factor
        self.current_intensity = 0.0
        self.intensity_history = []
        self.max_history_length = 10
    
    def update(self, audio_features: Dict[str, Any]) -> float:
        """
        更新梅尔强度
        
        Args:
            audio_features: 音频特征字典
        
        Returns:
            当前梅尔强度 (0.0 - 1.0)
        """
        # 从音频特征中提取梅尔强度
        self.current_intensity = calculate_mel_intensity(
            audio_features, 
            self.current_intensity, 
            self.smoothing_factor
        )
        
        # 记录历史
        self.intensity_history.append(self.current_intensity)
        if len(self.intensity_history) > self.max_history_length:
            self.intensity_history.pop(0)
        
        return self.current_intensity
    
    def get_current_intensity(self) -> float:
        """获取当前梅尔强度"""
        return self.current_intensity
    
    def get_average_intensity(self, window_size: int = 5) -> float:
        """
        获取平均梅尔强度
        
        Args:
            window_size: 计算平均值的窗口大小
        
        Returns:
            平均梅尔强度
        """
        if len(self.intensity_history) == 0:
            return 0.0
        
        window = self.intensity_history[-window_size:]
        return sum(window) / len(window)
    
    def reset(self) -> None:
        """重置跟踪器"""
        self.current_intensity = 0.0
        self.intensity_history.clear()


def calculate_particle_count(beat_strength: float, base_count: int, max_count: int, smoothing_factor: float = 0.3) -> int:
    """
    根据节拍强度计算粒子生成数量
    
    Args:
        beat_strength: 节拍强度 (0.0 - 1.0)
        base_count: 基准粒子数量
        max_count: 最大粒子数量
        smoothing_factor: 平滑因子 (0.0 - 1.0)，用于平滑节拍强度变化
    
    Returns:
        粒子生成数量
    """
    # 确保节拍强度在有效范围内
    beat_strength = max(0.0, min(1.0, beat_strength))
    
    # 线性映射：base_count + (max_count - base_count) * beat_strength
    target_count = base_count + (max_count - base_count) * beat_strength
    
    # 添加随机性，使粒子数量更自然
    random_variation = np.random.uniform(-0.1, 0.1)
    target_count = target_count * (1 + random_variation)
    
    return int(target_count)


def smooth_beat_strength(current_beat: float, previous_beat: float, smoothing_factor: float = 0.3) -> float:
    """
    平滑节拍强度变化，避免粒子数量突变
    
    Args:
        current_beat: 当前节拍强度
        previous_beat: 上一帧的节拍强度
        smoothing_factor: 平滑因子 (0.0 - 1.0)
                          0.0 = 不平滑，直接使用当前值
                          1.0 = 完全平滑，不更新
    
    Returns:
        平滑后的节拍强度
    """
    # 确保平滑因子在有效范围内
    smoothing_factor = max(0.0, min(1.0, smoothing_factor))
    
    # 指数移动平均
    return previous_beat + smoothing_factor * (current_beat - previous_beat)


def get_beat_strength_from_features(audio_features: Dict[str, Any], previous_beat: float = 0.0, 
                                   smoothing_factor: float = 0.3) -> float:
    """
    从音频特征中提取节拍强度
    
    Args:
        audio_features: 音频特征字典
        previous_beat: 上一帧的节拍强度（用于平滑）
        smoothing_factor: 平滑因子
    
    Returns:
        节拍强度 (0.0 - 1.0)
    """
    # 从节奏特征中提取节拍强度
    current_beat = 0.0
    
    if "rhythm" in audio_features and "beat_strength" in audio_features["rhythm"]:
        beat_data = audio_features["rhythm"]["beat_strength"]
        
        if isinstance(beat_data, (int, float)):
            current_beat = float(beat_data)
        elif isinstance(beat_data, np.ndarray):
            if beat_data.ndim == 1 and len(beat_data) > 0:
                # 取当前帧的节拍强度
                current_beat = float(beat_data[-1])
            elif beat_data.ndim == 2 and beat_data.size > 0:
                # 取最后一帧的节拍强度
                current_beat = float(np.mean(beat_data[:, -1]))
    
    # 归一化到0-1范围
    # 假设节拍强度的正常范围是0-1，如果超出则进行归一化
    if current_beat > 1.0:
        current_beat = min(1.0, current_beat / 2.0)
    
    # 应用平滑
    return smooth_beat_strength(current_beat, previous_beat, smoothing_factor)


class BeatStrengthTracker:
    """节拍强度跟踪器，用于平滑节拍强度变化"""
    
    def __init__(self, smoothing_factor: float = 0.3):
        """
        初始化节拍强度跟踪器
        
        Args:
            smoothing_factor: 平滑因子 (0.0 - 1.0)
        """
        self.smoothing_factor = smoothing_factor
        self.current_beat = 0.0
        self.beat_history = []
        self.max_history_length = 10
    
    def update(self, audio_features: Dict[str, Any]) -> float:
        """
        更新节拍强度
        
        Args:
            audio_features: 音频特征字典
        
        Returns:
            当前节拍强度 (0.0 - 1.0)
        """
        # 从音频特征中提取节拍强度
        raw_beat = 0.0
        
        if "rhythm" in audio_features and "beat_strength" in audio_features["rhythm"]:
            beat_data = audio_features["rhythm"]["beat_strength"]
            
            if isinstance(beat_data, (int, float)):
                raw_beat = float(beat_data)
            elif isinstance(beat_data, np.ndarray):
                if beat_data.ndim == 1 and len(beat_data) > 0:
                    raw_beat = float(beat_data[-1])
                elif beat_data.ndim == 2 and beat_data.size > 0:
                    raw_beat = float(np.mean(beat_data[:, -1]))
        
        # 归一化到0-1范围
        if raw_beat > 1.0:
            raw_beat = min(1.0, raw_beat / 2.0)
        
        # 应用平滑 - 使用更小的平滑因子，使节拍强度变化更灵敏
        self.current_beat = smooth_beat_strength(raw_beat, self.current_beat, self.smoothing_factor)
        
        # 记录历史
        self.beat_history.append(self.current_beat)
        if len(self.beat_history) > self.max_history_length:
            self.beat_history.pop(0)
        
        return self.current_beat
    
    def get_current_beat(self) -> float:
        """获取当前节拍强度"""
        return self.current_beat
    
    def get_average_beat(self, window_size: int = 5) -> float:
        """
        获取平均节拍强度
        
        Args:
            window_size: 计算平均值的窗口大小
        
        Returns:
            平均节拍强度
        """
        if len(self.beat_history) == 0:
            return 0.0
        
        window = self.beat_history[-window_size:]
        return sum(window) / len(window)
    
    def reset(self) -> None:
        """重置跟踪器"""
        self.current_beat = 0.0
        self.beat_history.clear()


def calculate_onset_intensity(audio_features: Dict[str, Any], previous_intensity: float = 0.0, 
                          smoothing_factor: float = 0.3) -> float:
    """
    从onset_envelope中提取强度值
    
    Args:
        audio_features: 音频特征字典
        previous_intensity: 上一帧的强度（用于平滑）
        smoothing_factor: 平滑因子
    
    Returns:
        onset强度 (0.0 - 1.0)
    """
    # 从节拍特征中提取onset_envelope
    current_intensity = 0.0
    
    if "rhythm" in audio_features and "onset_envelope" in audio_features["rhythm"]:
        onset_env = audio_features["rhythm"]["onset_envelope"]
        
        if isinstance(onset_env, np.ndarray) and onset_env.size > 0:
            # 获取最新一帧的onset强度
            current_intensity = float(onset_env[-1])
            
            # 使用滑动窗口计算局部最大值，使强度更敏感
            window_size = min(20, len(onset_env))
            start_idx = max(0, len(onset_env) - window_size)
            local_max = np.max(onset_env[start_idx:])
            
            # 归一化到0-1范围（使用局部最大值）
            if local_max > 0:
                current_intensity = current_intensity / local_max
            current_intensity = max(0.0, min(1.0, current_intensity))
            
            # 添加基准值，确保最低强度不会太低
            # 使用局部均值作为基准
            local_mean = np.mean(onset_env[start_idx:])
            base_intensity = local_mean / local_max if local_max > 0 else 0
            current_intensity = max(current_intensity, base_intensity * 0.5)
            
    elif "rhythm" in audio_features and "beat_strength" in audio_features["rhythm"]:
        # 如果没有onset_envelope，使用beat_strength作为后备
        beat_strength = audio_features["rhythm"]["beat_strength"]
        
        if isinstance(beat_strength, np.ndarray) and beat_strength.size > 0:
            # 获取最新一帧的节拍强度
            current_intensity = float(beat_strength[-1])
            current_intensity = max(0.0, min(1.0, current_intensity))
    
    # 应用平滑
    smoothing_factor = max(0.0, min(1.0, smoothing_factor))
    smoothed_intensity = previous_intensity + smoothing_factor * (current_intensity - previous_intensity)
    
    return smoothed_intensity


class OnsetIntensityTracker:
    """onset强度跟踪器，用于平滑onset强度变化"""
    
    def __init__(self, smoothing_factor: float = 0.3):
        """
        初始化onset强度跟踪器
        
        Args:
            smoothing_factor: 平滑因子 (0.0 - 1.0)
        """
        self.smoothing_factor = smoothing_factor
        self.current_intensity = 0.0
        self.intensity_history = []
        self.max_history_length = 10
    
    def update(self, audio_features: Dict[str, Any]) -> float:
        """
        更新onset强度
        
        Args:
            audio_features: 音频特征字典
        
        Returns:
            当前的onset强度 (0.0 - 1.0)
        """
        self.current_intensity = calculate_onset_intensity(
            audio_features, 
            self.current_intensity, 
            self.smoothing_factor
        )
        
        # 记录历史
        self.intensity_history.append(self.current_intensity)
        if len(self.intensity_history) > self.max_history_length:
            self.intensity_history.pop(0)
        
        return self.current_intensity
    
    def get_current_intensity(self) -> float:
        """获取当前onset强度"""
        return self.current_intensity
    
    def get_average_intensity(self, window_size: int = 5) -> float:
        """
        获取平均onset强度
        
        Args:
            window_size: 计算平均值的窗口大小
        
        Returns:
            平均onset强度
        """
        if len(self.intensity_history) == 0:
            return 0.0
        
        window = self.intensity_history[-window_size:]
        return sum(window) / len(window)
    
    def reset(self) -> None:
        """重置跟踪器"""
        self.current_intensity = 0.0
        self.intensity_history.clear()