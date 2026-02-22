import numpy as np
from typing import Dict, Any, Optional


class MusicStyleAnalyzer:
    """音乐风格分析器"""

    def __init__(self):
        """初始化音乐风格分析器"""
        # 音乐风格定义
        self.styles = {
            "piano": {
                "name": "钢琴曲",
                "description": "优雅、流畅、旋律性强",
                "visual_config": {
                    "particle_count": 200,
                    "min_size": 4,
                    "max_size": 8,
                    "min_jump_height": 20,
                    "max_jump_height": 100,
                    "min_jump_speed": 0.08,
                    "max_jump_speed": 0.15,
                    "trail_length": 12,
                    "color_palette": "soft_pastel",
                    "movement_pattern": "fluid_curve",
                    "beat_response": 1.2
                }
            },
            "rock": {
                "name": "摇滚乐",
                "description": "强烈、有力、节奏感强",
                "visual_config": {
                    "particle_count": 400,
                    "min_size": 3,
                    "max_size": 10,
                    "min_jump_height": 80,
                    "max_jump_height": 250,
                    "min_jump_speed": 0.15,
                    "max_jump_speed": 0.3,
                    "trail_length": 6,
                    "color_palette": "vibrant_contrast",
                    "movement_pattern": "intense_jump",
                    "beat_response": 1.8
                }
            },
            "dj": {
                "name": "DJ音乐",
                "description": "电子感强、节拍明确、低音重",
                "visual_config": {
                    "particle_count": 350,
                    "min_size": 2,
                    "max_size": 8,
                    "min_jump_height": 20,
                    "max_jump_height": 120,
                    "min_jump_speed": 0.08,
                    "max_jump_speed": 0.18,
                    "trail_length": 5,
                    "color_palette": "neon_glow",
                    "movement_pattern": "geometric_sync",
                    "beat_response": 1.6
                }
            },
            "light": {
                "name": "轻音乐",
                "description": "舒缓、放松、低强度",
                "visual_config": {
                    "particle_count": 150,
                    "min_size": 5,
                    "max_size": 10,
                    "min_jump_height": 10,
                    "max_jump_height": 60,
                    "min_jump_speed": 0.05,
                    "max_jump_speed": 0.1,
                    "trail_length": 15,
                    "color_palette": "soft_blue",
                    "movement_pattern": "slow_float",
                    "beat_response": 1.0
                }
            }
        }

    def analyze(self, audio_features: Dict[str, Any]) -> Optional[str]:
        """分析音频特征，识别音乐风格"""
        if not audio_features:
            return None

        # 提取特征
        amplitude = 0
        if "temporal" in audio_features and "amplitude" in audio_features["temporal"]:
            amp_data = audio_features["temporal"]["amplitude"]
            if len(amp_data) > 0:
                amplitude = np.mean(amp_data)

        loudness = 0
        if "temporal" in audio_features and "loudness" in audio_features["temporal"]:
            loud_data = audio_features["temporal"]["loudness"]
            if len(loud_data) > 0:
                loudness = np.mean(loud_data)

        spectrum = None
        if "frequency" in audio_features and "spectrum" in audio_features["frequency"]:
            spectrum = audio_features["frequency"]["spectrum"]

        mel_spectrogram = None
        if "frequency" in audio_features and "mel_spectrogram" in audio_features["frequency"]:
            mel_spectrogram = audio_features["frequency"]["mel_spectrogram"]

        bpm = 0
        if "rhythm" in audio_features and "bpm" in audio_features["rhythm"]:
            bpm = audio_features["rhythm"]["bpm"]

        # 计算特征值
        features = {
            "amplitude": amplitude,
            "loudness": loudness,
            "bpm": bpm,
            "spectral_centroid": 0,
            "spectral_bandwidth": 0,
            "low_freq_energy": 0,
            "high_freq_energy": 0
        }

        # 计算频谱特征
        if spectrum is not None and spectrum.size > 0:
            freq_bins = spectrum.shape[0]
            freqs = np.linspace(0, 1, freq_bins)
            spectrum_mean = np.mean(spectrum, axis=1)
            
            # 谱质心
            if np.sum(spectrum_mean) > 0:
                features["spectral_centroid"] = np.sum(freqs * spectrum_mean) / np.sum(spectrum_mean)
            
            # 谱带宽
            if np.sum(spectrum_mean) > 0:
                centroid = features["spectral_centroid"]
                features["spectral_bandwidth"] = np.sqrt(np.sum(spectrum_mean * (freqs - centroid) ** 2) / np.sum(spectrum_mean))
            
            # 低频能量
            low_freq_bins = int(freq_bins * 0.2)
            features["low_freq_energy"] = np.mean(spectrum_mean[:low_freq_bins])
            
            # 高频能量
            high_freq_bins = int(freq_bins * 0.8)
            features["high_freq_energy"] = np.mean(spectrum_mean[high_freq_bins:])

        # 基于特征识别音乐风格
        style_scores = {
            "piano": self._score_piano(features),
            "rock": self._score_rock(features),
            "dj": self._score_dj(features),
            "light": self._score_light(features)
        }

        # 返回得分最高的风格
        if style_scores:
            return max(style_scores, key=style_scores.get)
        else:
            return None

    def _score_piano(self, features: Dict[str, float]) -> float:
        """计算钢琴曲得分"""
        score = 0
        
        # 钢琴曲通常有中等的振幅和响度
        if 0.2 < features["amplitude"] < 0.6:
            score += 2
        
        # 钢琴曲通常有中等的BPM
        if 60 < features["bpm"] < 120:
            score += 2
        
        # 钢琴曲通常有较高的谱质心（旋律性）
        if features["spectral_centroid"] > 0.4:
            score += 3
        
        # 钢琴曲通常有较窄的谱带宽
        if features["spectral_bandwidth"] < 0.2:
            score += 2
        
        return score

    def _score_rock(self, features: Dict[str, float]) -> float:
        """计算摇滚乐得分"""
        score = 0
        
        # 摇滚乐通常有较高的振幅和响度
        if features["amplitude"] > 0.5:
            score += 3
        
        # 摇滚乐通常有较高的BPM
        if 100 < features["bpm"] < 160:
            score += 2
        
        # 摇滚乐通常有丰富的高频能量
        if features["high_freq_energy"] > 0.3:
            score += 3
        
        # 摇滚乐通常有较宽的谱带宽
        if features["spectral_bandwidth"] > 0.25:
            score += 2
        
        return score

    def _score_dj(self, features: Dict[str, float]) -> float:
        """计算DJ音乐得分"""
        score = 0
        
        # DJ音乐通常有较高的振幅
        if features["amplitude"] > 0.4:
            score += 2
        
        # DJ音乐通常有明确的BPM
        if 120 < features["bpm"] < 180:
            score += 3
        
        # DJ音乐通常有丰富的低频能量
        if features["low_freq_energy"] > 0.4:
            score += 3
        
        # DJ音乐通常有中等的谱质心
        if 0.3 < features["spectral_centroid"] < 0.6:
            score += 2
        
        return score

    def _score_light(self, features: Dict[str, float]) -> float:
        """计算轻音乐得分"""
        score = 0
        
        # 轻音乐通常有较低的振幅和响度
        if features["amplitude"] < 0.3:
            score += 3
        
        # 轻音乐通常有较低的BPM
        if features["bpm"] < 100:
            score += 2
        
        # 轻音乐通常有较低的高频能量
        if features["high_freq_energy"] < 0.2:
            score += 2
        
        # 轻音乐通常有较窄的谱带宽
        if features["spectral_bandwidth"] < 0.2:
            score += 2
        
        return score

    def get_style_config(self, style: str) -> Optional[Dict[str, Any]]:
        """获取音乐风格的视觉配置"""
        if style in self.styles:
            return self.styles[style]["visual_config"]
        else:
            return None

    def get_style_info(self, style: str) -> Optional[Dict[str, Any]]:
        """获取音乐风格信息"""
        if style in self.styles:
            return {
                "name": self.styles[style]["name"],
                "description": self.styles[style]["description"]
            }
        else:
            return None
