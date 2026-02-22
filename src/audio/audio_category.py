from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import numpy as np


class AudioCategory(ABC):
    """音频类别基类"""

    @property
    @abstractmethod
    def name(self) -> str:
        """类别名称"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """类别描述"""
        pass

    @abstractmethod
    def get_base_attributes(self) -> Dict[str, Any]:
        """获取统一的基础属性"""
        pass

    @abstractmethod
    def get_personalized_attributes(self) -> Dict[str, Any]:
        """获取个性化属性"""
        pass

    @abstractmethod
    def parse_audio(self, audio_data: Any) -> Dict[str, Any]:
        """解析音频，提取属性"""
        pass


class AudioAttributes:
    """音频统一属性"""

    def __init__(self):
        """初始化音频属性"""
        # 时域特征
        self.amplitude: Optional[np.ndarray] = None
        self.loudness: Optional[np.ndarray] = None
        
        # 频域特征
        self.spectrum: Optional[np.ndarray] = None
        self.mel_spectrogram: Optional[np.ndarray] = None
        self.spectral_centroid: Optional[np.ndarray] = None
        self.spectral_bandwidth: Optional[np.ndarray] = None
        
        # 节奏特征
        self.bpm: float = 0.0
        self.beat_frames: np.ndarray = np.array([])
        self.beat_times: np.ndarray = np.array([])
        self.is_beat: bool = False
        
        # 音色特征
        self.mfcc: Optional[np.ndarray] = None
        
        # 元数据
        self.duration: float = 0.0
        self.sample_rate: int = 0
        self.channels: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "temporal": {
                "amplitude": self.amplitude,
                "loudness": self.loudness
            },
            "frequency": {
                "spectrum": self.spectrum,
                "mel_spectrogram": self.mel_spectrogram,
                "spectral_centroid": self.spectral_centroid,
                "spectral_bandwidth": self.spectral_bandwidth
            },
            "rhythm": {
                "bpm": self.bpm,
                "beat_frames": self.beat_frames,
                "beat_times": self.beat_times,
                "is_beat": self.is_beat
            },
            "timbre": {
                "mfcc": self.mfcc
            },
            "metadata": {
                "duration": self.duration,
                "sample_rate": self.sample_rate,
                "channels": self.channels
            }
        }
