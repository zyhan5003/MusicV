import pygame
import numpy as np
from typing import Dict, Any
from ..renderer.visual_renderer import VisualComponent


class InfoDisplayVisualizer(VisualComponent):
    """音频信息显示可视化组件"""

    @property
    def name(self) -> str:
        return "info_display"

    def initialize(self, surface: pygame.Surface, config: Dict[str, Any]) -> None:
        """初始化信息显示组件"""
        self.surface = surface
        self.config = config.get("info", {}).get("display", {})
        self.width, self.height = surface.get_size()
        self.font = pygame.font.Font(None, 24)
        self.text_color = pygame.Color(255, 255, 255)
        self.bar_color = pygame.Color(0, 255, 255)
        self.bar_bg_color = pygame.Color(50, 50, 50)
        self.padding = 20
        self.line_height = 30
        self.bar_width = 200
        self.bar_height = 20

    def update(self, audio_features: Dict[str, Any], dt: float) -> None:
        """更新信息显示"""
        self.audio_features = audio_features

    def render(self, surface: pygame.Surface) -> None:
        """渲染信息显示"""
        if not hasattr(self, "audio_features"):
            return

        # 显示音频信息
        y_offset = self.padding
        
        # 1. 时域特征
        if "temporal" in self.audio_features:
            temporal_features = self.audio_features["temporal"]
            
            # 响度
            if "loudness" in temporal_features:
                loudness = temporal_features["loudness"]
                loudness_value = np.mean(loudness) if len(loudness) > 0 else 0
                self._draw_info_item(surface, "Loudness:", loudness_value, y_offset)
                y_offset += self.line_height
            
            # 振幅
            if "amplitude" in temporal_features:
                amplitude = temporal_features["amplitude"]
                amplitude_value = np.mean(amplitude) if len(amplitude) > 0 else 0
                self._draw_info_item(surface, "Amplitude:", amplitude_value, y_offset)
                y_offset += self.line_height
        
        # 2. 频域特征
            if "frequency" in self.audio_features:
                frequency_features = self.audio_features["frequency"]
                
                # 频谱能量
                if "spectrum" in frequency_features:
                    spectrum = frequency_features["spectrum"]
                    spectrum_value = np.mean(spectrum) if spectrum.size > 0 else 0
                    # 归一化频谱能量
                    spectrum_normalized = min(1.0, spectrum_value / 100)  # 根据实际情况调整阈值
                    self._draw_info_item(surface, "Spectrum Energy:", spectrum_normalized, y_offset)
                    y_offset += self.line_height
                
                # 梅尔频谱能量
                if "mel_spectrogram" in frequency_features:
                    mel_spec = frequency_features["mel_spectrogram"]
                    mel_value = np.mean(mel_spec) if mel_spec.size > 0 else 0
                    # 归一化梅尔频谱能量
                    mel_normalized = min(1.0, mel_value / 100)  # 根据实际情况调整阈值
                    self._draw_info_item(surface, "Mel Energy:", mel_normalized, y_offset)
                    y_offset += self.line_height
        
        # 3. 节奏特征
        if "rhythm" in self.audio_features:
            rhythm_features = self.audio_features["rhythm"]
            
            # BPM
            if "bpm" in rhythm_features:
                bpm_value = rhythm_features["bpm"]
                self._draw_info_item(surface, "BPM:", bpm_value, y_offset)
                y_offset += self.line_height
            
            # 节拍状态
            if "is_beat" in rhythm_features:
                is_beat = rhythm_features["is_beat"]
                beat_status = 1.0 if is_beat else 0.0
                self._draw_info_item(surface, "Beat:", beat_status, y_offset)
                y_offset += self.line_height
        
        # 4. 音色特征
        if "timbre" in self.audio_features:
            timbre_features = self.audio_features["timbre"]
            
            # 谱质心
            if "spectral_centroid" in timbre_features:
                spectral_centroid = timbre_features["spectral_centroid"]
                centroid_value = np.mean(spectral_centroid) if len(spectral_centroid) > 0 else 0
                # 归一化谱质心值
                centroid_normalized = min(1.0, centroid_value / 10000)
                self._draw_info_item(surface, "Spectral Centroid:", centroid_normalized, y_offset)
                y_offset += self.line_height

    def _draw_info_item(self, surface: pygame.Surface, label: str, value: float, y: int) -> None:
        """绘制单个信息项"""
        # 绘制标签
        label_text = self.font.render(label, True, self.text_color)
        surface.blit(label_text, (self.padding, y))
        
        # 绘制数值
        value_text = self.font.render(f"{value:.2f}", True, self.text_color)
        surface.blit(value_text, (self.padding + 120, y))
        
        # 绘制进度条
        bar_x = self.padding + 200
        bar_y = y + 5
        
        # 绘制背景
        pygame.draw.rect(surface, self.bar_bg_color, (bar_x, bar_y, self.bar_width, self.bar_height))
        
        # 绘制进度
        progress_width = int(min(1.0, value) * self.bar_width)
        pygame.draw.rect(surface, self.bar_color, (bar_x, bar_y, progress_width, self.bar_height))
