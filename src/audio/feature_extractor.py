from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import numpy as np
import librosa
from dataclasses import dataclass


@dataclass
class FeatureConfig:
    """特征提取配置"""
    window_size: int = 2048
    hop_size: int = 512
    n_fft: int = 2048
    n_mels: int = 128
    n_mfcc: int = 13
    bpm_range: List[int] = None

    def __post_init__(self):
        if self.bpm_range is None:
            self.bpm_range = [60, 200]


class FeatureExtractor(ABC):
    """特征提取器基类"""

    @abstractmethod
    def extract(self, y: np.ndarray, sr: int, config: FeatureConfig) -> Dict[str, Any]:
        """提取特征"""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """特征提取器名称"""
        pass


class TemporalFeatureExtractor(FeatureExtractor):
    """时域特征提取器"""

    @property
    def name(self) -> str:
        return "temporal"

    def extract(self, y: np.ndarray, sr: int, config: FeatureConfig) -> Dict[str, Any]:
        """提取时域特征"""
        # 振幅
        amplitude = np.abs(y)
        # 响度（RMS）
        loudness = librosa.feature.rms(
            y=y, 
            frame_length=config.window_size, 
            hop_length=config.hop_size
        )[0]
        # 零交叉率
        zero_crossing_rate = librosa.feature.zero_crossing_rate(
            y=y, 
            frame_length=config.window_size, 
            hop_length=config.hop_size
        )[0]

        return {
            "amplitude": amplitude,
            "loudness": loudness,
            "zero_crossing_rate": zero_crossing_rate
        }


class FrequencyFeatureExtractor(FeatureExtractor):
    """频域特征提取器"""

    @property
    def name(self) -> str:
        return "frequency"

    def extract(self, y: np.ndarray, sr: int, config: FeatureConfig) -> Dict[str, Any]:
        """提取频域特征"""
        # 频谱
        spectrum = np.abs(librosa.stft(
            y=y, 
            n_fft=config.n_fft, 
            hop_length=config.hop_size
        ))
        # 梅尔频谱
        mel_spectrogram = librosa.feature.melspectrogram(
            y=y, 
            sr=sr, 
            n_fft=config.n_fft, 
            hop_length=config.hop_size, 
            n_mels=config.n_mels
        )
        # 对数梅尔频谱
        log_mel_spectrogram = librosa.power_to_db(mel_spectrogram, ref=np.max)

        return {
            "spectrum": spectrum,
            "mel_spectrogram": mel_spectrogram,
            "log_mel_spectrogram": log_mel_spectrogram
        }


class RhythmFeatureExtractor(FeatureExtractor):
    """节奏特征提取器"""

    @property
    def name(self) -> str:
        return "rhythm"

    def extract(self, y: np.ndarray, sr: int, config: FeatureConfig) -> Dict[str, Any]:
        """提取节奏特征"""
        # BPM和节拍点
        tempo, beat_frames = librosa.beat.beat_track(
            y=y, 
            sr=sr, 
            start_bpm=config.bpm_range[0],
            tightness=100
        )
        # 节拍时间
        beat_times = librosa.frames_to_time(beat_frames, sr=sr, hop_length=config.hop_size)
        # 节拍强度 - 使用完整的onset_envelope，而不是只在节拍点提取
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        
        # 对onset_envelope进行归一化和平滑处理
        # 使用滑动窗口计算局部最大值，使节拍强度更加平滑和持续
        window_size = 20  # 增加滑动窗口大小
        beat_strength_smoothed = np.zeros_like(onset_env)
        for i in range(len(onset_env)):
            start_idx = max(0, i - window_size // 2)
            end_idx = min(len(onset_env), i + window_size // 2 + 1)
            beat_strength_smoothed[i] = np.max(onset_env[start_idx:end_idx])
        
        # 归一化到0-1范围
        if np.max(beat_strength_smoothed) > 0:
            beat_strength = beat_strength_smoothed / np.max(beat_strength_smoothed)
        else:
            beat_strength = beat_strength_smoothed
        
        # 添加基准值，确保节拍强度不会太低
        # 使用中位数作为基准，确保大部分时间都有一定的节拍强度
        base_strength = np.percentile(beat_strength, 30)  # 使用30分位数作为基准
        beat_strength = np.maximum(beat_strength, base_strength)
        
        # 再次归一化到0-1范围
        if np.max(beat_strength) > 0:
            beat_strength = beat_strength / np.max(beat_strength)
        
        return {
            "bpm": float(tempo),
            "beat_frames": beat_frames,
            "beat_times": beat_times,
            "beat_strength": beat_strength,
            "onset_envelope": onset_env  # 添加原始onset_envelope
        }


class TimbreFeatureExtractor(FeatureExtractor):
    """音色特征提取器"""

    @property
    def name(self) -> str:
        return "timbre"

    def extract(self, y: np.ndarray, sr: int, config: FeatureConfig) -> Dict[str, Any]:
        """提取音色特征"""
        # MFCC
        mfcc = librosa.feature.mfcc(
            y=y, 
            sr=sr, 
            n_mfcc=config.n_mfcc,
            n_fft=config.n_fft,
            hop_length=config.hop_size
        )
        # 谱质心
        spectral_centroid = librosa.feature.spectral_centroid(
            y=y, 
            sr=sr, 
            n_fft=config.n_fft, 
            hop_length=config.hop_size
        )[0]
        # 谱带宽
        spectral_bandwidth = librosa.feature.spectral_bandwidth(
            y=y, 
            sr=sr, 
            n_fft=config.n_fft, 
            hop_length=config.hop_size
        )[0]
        # 谱滚降
        spectral_rolloff = librosa.feature.spectral_rolloff(
            y=y, 
            sr=sr, 
            n_fft=config.n_fft, 
            hop_length=config.hop_size
        )[0]

        return {
            "mfcc": mfcc,
            "spectral_centroid": spectral_centroid,
            "spectral_bandwidth": spectral_bandwidth,
            "spectral_rolloff": spectral_rolloff
        }


class FeatureExtractorManager:
    """特征提取器管理器"""

    def __init__(self):
        """初始化特征提取器管理器"""
        self.extractors: Dict[str, FeatureExtractor] = {}
        self._register_default_extractors()

    def _register_default_extractors(self) -> None:
        """注册默认提取器"""
        self.register_extractor(TemporalFeatureExtractor())
        self.register_extractor(FrequencyFeatureExtractor())
        self.register_extractor(RhythmFeatureExtractor())
        self.register_extractor(TimbreFeatureExtractor())

    def register_extractor(self, extractor: FeatureExtractor) -> None:
        """注册特征提取器"""
        self.extractors[extractor.name] = extractor

    def extract_all(self, y: np.ndarray, sr: int, config: FeatureConfig) -> Dict[str, Any]:
        """提取所有特征"""
        features = {}
        for name, extractor in self.extractors.items():
            features[name] = extractor.extract(y, sr, config)
        return features

    def extract_selected(self, y: np.ndarray, sr: int, config: FeatureConfig, extractor_names: List[str]) -> Dict[str, Any]:
        """提取指定的特征"""
        features = {}
        for name in extractor_names:
            if name in self.extractors:
                features[name] = self.extractors[name].extract(y, sr, config)
        return features
