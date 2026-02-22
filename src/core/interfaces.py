from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import numpy as np


class AudioFeatureProvider(ABC):
    """音频特征提供者接口"""

    @abstractmethod
    def get_features(self) -> Dict[str, Any]:
        """获取音频特征"""
        pass

    @abstractmethod
    def is_playing(self) -> bool:
        """是否正在播放"""
        pass

    @abstractmethod
    def get_current_time(self) -> float:
        """获取当前播放时间"""
        pass


class VisualRendererInterface(ABC):
    """视觉渲染器接口"""

    @abstractmethod
    def initialize(self) -> None:
        """初始化渲染器"""
        pass

    @abstractmethod
    def update(self, audio_features: Dict[str, Any]) -> None:
        """更新渲染器"""
        pass

    @abstractmethod
    def render(self) -> None:
        """渲染画面"""
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """清理资源"""
        pass

    @abstractmethod
    def set_config(self, config: Dict[str, Any]) -> None:
        """设置配置"""
        pass


class AudioVisualizerInterface(ABC):
    """音频可视化主接口"""

    @abstractmethod
    def load_audio(self, file_path: str) -> bool:
        """加载音频文件"""
        pass

    @abstractmethod
    def start_visualization(self) -> None:
        """开始可视化"""
        pass

    @abstractmethod
    def stop_visualization(self) -> None:
        """停止可视化"""
        pass

    @abstractmethod
    def set_visual_type(self, visual_type: str) -> None:
        """设置可视化类型"""
        pass

    @abstractmethod
    def set_config(self, config: Dict[str, Any]) -> None:
        """设置配置"""
        pass


class DataAdapter(ABC):
    """数据适配器接口"""

    @abstractmethod
    def adapt(self, data: Any) -> Any:
        """适配数据"""
        pass


class AudioFeatureAdapter(DataAdapter):
    """音频特征适配器"""

    def adapt(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """适配音频特征数据"""
        # 确保数据格式一致
        adapted_data = {
            "temporal": {
                "amplitude": np.array(data.get("temporal", {}).get("amplitude", [0])),
                "loudness": np.array(data.get("temporal", {}).get("loudness", [0])),
                "zero_crossing_rate": np.array(data.get("temporal", {}).get("zero_crossing_rate", [0]))
            },
            "frequency": {
                "spectrum": np.array(data.get("frequency", {}).get("spectrum", [[0]])),
                "mel_spectrogram": np.array(data.get("frequency", {}).get("mel_spectrogram", [[0]])),
                "log_mel_spectrogram": np.array(data.get("frequency", {}).get("log_mel_spectrogram", [[0]]))
            },
            "rhythm": {
                "bpm": data.get("rhythm", {}).get("bpm", 0),
                "beat_frames": np.array(data.get("rhythm", {}).get("beat_frames", [])),
                "beat_times": np.array(data.get("rhythm", {}).get("beat_times", [])),
                "beat_strength": np.array(data.get("rhythm", {}).get("beat_strength", []))
            },
            "timbre": {
                "mfcc": np.array(data.get("timbre", {}).get("mfcc", [[0]])),
                "spectral_centroid": np.array(data.get("timbre", {}).get("spectral_centroid", [0])),
                "spectral_bandwidth": np.array(data.get("timbre", {}).get("spectral_bandwidth", [0])),
                "spectral_rolloff": np.array(data.get("timbre", {}).get("spectral_rolloff", [0]))
            }
        }
        return adapted_data


class ConfigManagerInterface(ABC):
    """配置管理器接口"""

    @abstractmethod
    def load_config(self, file_path: str) -> Dict[str, Any]:
        """加载配置"""
        pass

    @abstractmethod
    def save_config(self, config: Dict[str, Any], file_path: str) -> None:
        """保存配置"""
        pass

    @abstractmethod
    def get_config(self, section: Optional[str] = None) -> Dict[str, Any]:
        """获取配置"""
        pass

    @abstractmethod
    def set_config(self, section: str, key: str, value: Any) -> None:
        """设置配置"""
        pass
