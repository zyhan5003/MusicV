import librosa
import soundfile as sf
import numpy as np
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, List
import json


@dataclass
class AudioData:
    """音频数据类"""
    y: np.ndarray  # 音频波形数据
    sr: int        # 采样率
    duration: float  # 音频时长（秒）
    channels: int  # 声道数


@dataclass
class AudioFeatures:
    """音频特征数据类"""
    # 时域特征
    amplitude: np.ndarray  # 振幅
    loudness: np.ndarray   # 响度
    # 频域特征
    spectrum: np.ndarray    # 频谱
    mel_spectrogram: np.ndarray  # 梅尔频谱
    # 节奏特征
    bpm: float              # 每分钟节拍数
    beat_frames: np.ndarray  # 节拍帧位置
    # 音色特征
    mfcc: np.ndarray        # 梅尔频率倒谱系数
    spectral_centroid: np.ndarray  # 谱质心
    spectral_bandwidth: np.ndarray  # 谱带宽

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "amplitude": self.amplitude.tolist(),
            "loudness": self.loudness.tolist(),
            "spectrum": self.spectrum.tolist(),
            "mel_spectrogram": self.mel_spectrogram.tolist(),
            "bpm": self.bpm,
            "beat_frames": self.beat_frames.tolist(),
            "mfcc": self.mfcc.tolist(),
            "spectral_centroid": self.spectral_centroid.tolist(),
            "spectral_bandwidth": self.spectral_bandwidth.tolist()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AudioFeatures':
        """从字典创建"""
        return cls(
            amplitude=np.array(data["amplitude"]),
            loudness=np.array(data["loudness"]),
            spectrum=np.array(data["spectrum"]),
            mel_spectrogram=np.array(data["mel_spectrogram"]),
            bpm=data["bpm"],
            beat_frames=np.array(data["beat_frames"]),
            mfcc=np.array(data["mfcc"]),
            spectral_centroid=np.array(data["spectral_centroid"]),
            spectral_bandwidth=np.array(data["spectral_bandwidth"])
        )


class AudioParser:
    """音频解析器"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化音频解析器"""
        self.config = config or {
            "sr": 22050,  # 统一采样率
            "mono": True,  # 转换为单声道
            "n_fft": 2048,
            "hop_length": 512,
            "n_mels": 128,
            "n_mfcc": 13,
            "bpm_range": [60, 200]
        }
        self.audio_data: Optional[AudioData] = None
        self.features: Optional[AudioFeatures] = None

    def load_audio(self, file_path: str) -> AudioData:
        """加载音频文件"""
        # 使用配置中的采样率和声道设置
        sr = self.config.get("sr", 22050)
        mono = self.config.get("mono", True)
        
        # 使用librosa加载音频
        y, sr = librosa.load(file_path, sr=sr, mono=mono)
        duration = librosa.get_duration(y=y, sr=sr)
        channels = 1 if y.ndim == 1 else y.shape[1]
        
        self.audio_data = AudioData(y=y, sr=sr, duration=duration, channels=channels)
        return self.audio_data

    def extract_features(self, audio_data: Optional[AudioData] = None) -> AudioFeatures:
        """提取音频特征"""
        if audio_data is None:
            if self.audio_data is None:
                raise ValueError("No audio data loaded")
            audio_data = self.audio_data

        y = audio_data.y
        sr = audio_data.sr

        # 从配置中获取参数
        n_fft = self.config.get("n_fft", 2048)
        hop_length = self.config.get("hop_length", 512)
        n_mels = self.config.get("n_mels", 128)
        n_mfcc = self.config.get("n_mfcc", 13)
        bpm_range = self.config.get("bpm_range", [60, 200])

        # 提取时域特征
        amplitude = np.abs(y)
        loudness = librosa.feature.rms(y=y, frame_length=n_fft, hop_length=hop_length)[0]

        # 提取频域特征
        spectrum = np.abs(librosa.stft(y, n_fft=n_fft, hop_length=hop_length))
        mel_spectrogram = librosa.feature.melspectrogram(
            y=y, sr=sr, n_fft=n_fft, hop_length=hop_length, n_mels=n_mels
        )

        # 提取节奏特征 - 使用配置中的bpm_range
        tempo, beat_frames = librosa.beat.beat_track(
            y=y, sr=sr, start_bpm=bpm_range[0], tightness=100
        )

        # 提取音色特征
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc, n_fft=n_fft, hop_length=hop_length)
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr, n_fft=n_fft, hop_length=hop_length)[0]
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr, n_fft=n_fft, hop_length=hop_length)[0]

        # 确保所有特征长度一致
        max_len = max(len(loudness), len(spectral_centroid), len(spectral_bandwidth))
        loudness = self._pad_feature(loudness, max_len)
        spectral_centroid = self._pad_feature(spectral_centroid, max_len)
        spectral_bandwidth = self._pad_feature(spectral_bandwidth, max_len)

        self.features = AudioFeatures(
            amplitude=amplitude,
            loudness=loudness,
            spectrum=spectrum,
            mel_spectrogram=mel_spectrogram,
            bpm=tempo,
            beat_frames=beat_frames,
            mfcc=mfcc,
            spectral_centroid=spectral_centroid,
            spectral_bandwidth=spectral_bandwidth
        )

        return self.features

    def _pad_feature(self, feature: np.ndarray, target_len: int) -> np.ndarray:
        """填充特征到目标长度"""
        if len(feature) >= target_len:
            return feature[:target_len]
        else:
            return np.pad(feature, (0, target_len - len(feature)), mode='constant')

    def save_features(self, file_path: str) -> None:
        """保存特征到文件"""
        if self.features is None:
            raise ValueError("No features extracted")
        
        with open(file_path, 'w') as f:
            json.dump(self.features.to_dict(), f)

    def load_features(self, file_path: str) -> AudioFeatures:
        """从文件加载特征"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        self.features = AudioFeatures.from_dict(data)
        return self.features
