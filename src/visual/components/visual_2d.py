import pygame
import numpy as np
from typing import Dict, Any, Optional
from ..renderer.visual_renderer import VisualComponent


class WaveformVisualizer(VisualComponent):
    """波形图可视化组件"""

    @property
    def name(self) -> str:
        return "waveform"

    def initialize(self, surface: pygame.Surface, config: Dict[str, Any]) -> None:
        """初始化波形图组件"""
        self.surface = surface
        self.config = config.get("2d", {}).get("waveform", {})
        self.color = pygame.Color(self.config.get("color", "#3498db"))
        self.line_width = self.config.get("line_width", 2)
        self.width, self.height = surface.get_size()
        self.center_y = self.height // 2

    def update(self, audio_features: Dict[str, Any], dt: float) -> None:
        """更新波形图"""
        self.audio_features = audio_features

    def render(self, surface: pygame.Surface) -> None:
        """渲染波形图"""
        if not hasattr(self, "audio_features"):
            return
        if "temporal" not in self.audio_features or "amplitude" not in self.audio_features["temporal"]:
            return

        amplitude = self.audio_features["temporal"]["amplitude"]
        if len(amplitude) == 0:
            return

        # 绘制波形（下方）
        points_bottom = []
        for i, amp in enumerate(amplitude):
            x = int((i / len(amplitude)) * self.width)
            y = self.center_y + int(amp * self.center_y)
            points_bottom.append((x, y))

        # 绘制波形（上方镜像）
        points_top = []
        for i, amp in enumerate(amplitude):
            x = int((i / len(amplitude)) * self.width)
            y = self.center_y - int(amp * self.center_y)
            points_top.append((x, y))

        if len(points_bottom) > 1:
            pygame.draw.lines(surface, self.color, False, points_bottom, self.line_width)
        
        if len(points_top) > 1:
            pygame.draw.lines(surface, self.color, False, points_top, self.line_width)


class SpectrumVisualizer(VisualComponent):
    """频谱瀑布图可视化组件"""

    @property
    def name(self) -> str:
        return "spectrum"

    def initialize(self, surface: pygame.Surface, config: Dict[str, Any]) -> None:
        """初始化频谱组件"""
        self.surface = surface
        self.config = config.get("2d", {}).get("spectrum", {})
        self.color_map = self.config.get("color_map", "viridis")
        self.width, self.height = surface.get_size()
        self.spectrum_history = []
        self.max_history = self.height

    def update(self, audio_features: Dict[str, Any], dt: float) -> None:
        """更新频谱"""
        if "frequency" in audio_features and "spectrum" in audio_features["frequency"]:
            spectrum = audio_features["frequency"]["spectrum"]
            if spectrum.size > 0:
                spectrum_mean = np.mean(spectrum, axis=1)
                self.spectrum_history.append(spectrum_mean)
                if len(self.spectrum_history) > self.max_history:
                    self.spectrum_history.pop(0)

    def render(self, surface: pygame.Surface) -> None:
        """渲染频谱"""
        if len(self.spectrum_history) == 0:
            return

        # 创建临时表面用于绘制频谱瀑布图
        temp_surface = pygame.Surface((self.width, self.height))
        temp_surface.fill((0, 0, 0))
        
        # 绘制频谱瀑布图（优化性能）
        for i, spectrum in enumerate(self.spectrum_history):
            y = i * (self.height // len(self.spectrum_history))
            for j, value in enumerate(spectrum):
                x = int((j / len(spectrum)) * self.width)
                intensity = int((value / np.max(spectrum)) * 255)
                color = pygame.Color(intensity, intensity, intensity)
                temp_surface.set_at((x, y), color)
        
        # 将临时表面绘制到主表面
        surface.blit(temp_surface, (0, 0))


class EqualizerVisualizer(VisualComponent):
    """动态均衡器可视化组件"""

    @property
    def name(self) -> str:
        return "equalizer"

    def initialize(self, surface: pygame.Surface, config: Dict[str, Any]) -> None:
        """初始化均衡器组件"""
        self.surface = surface
        self.config = config.get("2d", {}).get("equalizer", {})
        self.bands = self.config.get("bands", 32)
        self.color = pygame.Color(self.config.get("color", "#e74c3c"))
        self.width, self.height = surface.get_size()
        self.bar_width = (self.width // self.bands) - 2
        self.bar_spacing = 2

    def update(self, audio_features: Dict[str, Any], dt: float) -> None:
        """更新均衡器"""
        if "frequency" in audio_features and "mel_spectrogram" in audio_features["frequency"]:
            mel_spec = audio_features["frequency"]["mel_spectrogram"]
            # 计算每个频段的能量
            band_energy = []
            band_size = mel_spec.shape[0] // self.bands
            for i in range(self.bands):
                start = i * band_size
                end = (i + 1) * band_size
                if end <= mel_spec.shape[0]:
                    energy = np.mean(mel_spec[start:end])
                    band_energy.append(energy)
            self.band_energy = np.array(band_energy)
        else:
            self.band_energy = np.zeros(self.bands)

    def render(self, surface: pygame.Surface) -> None:
        """渲染均衡器"""
        if not hasattr(self, "band_energy"):
            return

        # 归一化能量
        if np.max(self.band_energy) > 0:
            band_energy = self.band_energy / np.max(self.band_energy) * self.height
        else:
            band_energy = self.band_energy

        # 绘制均衡器条
        for i, energy in enumerate(band_energy):
            x = i * (self.bar_width + self.bar_spacing)
            bar_height = int(energy)
            y = self.height - bar_height
            
            # 简单绘制矩形，不使用渐变效果以提高性能
            pygame.draw.rect(
                surface, 
                self.color, 
                (x, y, self.bar_width, bar_height)
            )
