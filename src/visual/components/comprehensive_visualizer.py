import pygame
import numpy as np
from typing import Dict, Any
from ..renderer.visual_renderer import VisualComponent
from ..particles.particle_system import ParticleSystem


class ComprehensiveVisualizer(VisualComponent):
    """综合可视化组件，整合多种视觉元素"""

    @property
    def name(self) -> str:
        return "comprehensive"

    def initialize(self, surface: pygame.Surface, config: Dict[str, Any]) -> None:
        """初始化综合可视化组件"""
        self.surface = surface
        self.config = config.get("comprehensive", {})
        self.width, self.height = surface.get_size()
        self.center_x, self.center_y = self.width // 2, self.height // 2
        self.font = pygame.font.Font(None, 24)
        self.text_color = pygame.Color(255, 255, 255)
        self.padding = 20
        
        # 初始化粒子系统
        self.particle_system = ParticleSystem()
        self.particle_system.initialize(surface, config)
        
        # 自定义粒子系统参数
        self.particle_system.emit_rate = 100
        self.particle_system.count = 3000
        self.particle_system.frequency_based_color = True
        
        # 初始化视觉元素参数
        self.waveform_color = pygame.Color(0, 255, 255)
        self.spectrum_color = pygame.Color(255, 0, 255)
        self.equalizer_color = pygame.Color(0, 255, 0)
        # 背景震动效果参数
        self.shake_intensity = 0
        self.shake_decay = 0.95
        self.max_shake = 10
        
        # 初始化数据缓存
        self.amplitude_history = np.zeros(500)
        self.spectrum_history = np.zeros((100, 500))

    def update(self, audio_features: Dict[str, Any], dt: float) -> None:
        """更新综合可视化"""
        self.audio_features = audio_features
        
        # 更新粒子系统
        self.particle_system.update(audio_features, dt)
        
        # 更新波形历史
        if "temporal" in audio_features and "amplitude" in audio_features["temporal"]:
            amplitude = audio_features["temporal"]["amplitude"]
            if len(amplitude) > 0:
                self.amplitude_history = np.roll(self.amplitude_history, -1)
                self.amplitude_history[-1] = np.mean(amplitude)
        
        # 更新频谱历史
        if "frequency" in audio_features and "spectrum" in audio_features["frequency"]:
            spectrum = audio_features["frequency"]["spectrum"]
            if spectrum.size > 0:
                spectrum_mean = np.mean(spectrum, axis=1)
                # 降采样到100个频段
                if len(spectrum_mean) != 100:
                    # 使用插值方法，更安全可靠
                    spectrum_mean = np.interp(
                        np.linspace(0, len(spectrum_mean)-1, 100),
                        np.arange(len(spectrum_mean)),
                        spectrum_mean
                    )
                self.spectrum_history = np.roll(self.spectrum_history, -1, axis=1)
                self.spectrum_history[:, -1] = spectrum_mean
        
        # 更新背景震动效果
        if "rhythm" in audio_features and "is_beat" in audio_features["rhythm"]:
            if audio_features["rhythm"]["is_beat"]:
                # 节拍时增加震动强度
                self.shake_intensity = self.max_shake
            else:
                # 非节拍时衰减震动强度
                self.shake_intensity = max(0, self.shake_intensity * self.shake_decay)

    def render(self, surface: pygame.Surface) -> None:
        """渲染综合可视化"""
        if not hasattr(self, "audio_features"):
            return

        # 应用背景震动效果
        if self.shake_intensity > 0:
            # 创建一个临时表面来绘制震动效果
            temp_surface = pygame.Surface((self.width, self.height))
            # 绘制所有内容到临时表面
            self._draw_background(temp_surface)
            self._draw_waveform(temp_surface)
            self._draw_spectrum_waterfall(temp_surface)
            self._draw_equalizer(temp_surface)
            self._draw_spectrum_cube(temp_surface)
            self.particle_system.render(temp_surface)
            self._draw_audio_info(temp_surface)
            
            # 计算震动偏移
            shake_x = int(np.sin(pygame.time.get_ticks() * 0.01) * self.shake_intensity)
            shake_y = int(np.cos(pygame.time.get_ticks() * 0.01) * self.shake_intensity)
            
            # 将临时表面绘制到主表面，应用震动偏移
            surface.blit(temp_surface, (shake_x, shake_y))
        else:
            # 正常绘制
            self._draw_background(surface)
            self._draw_waveform(surface)
            self._draw_spectrum_waterfall(surface)
            self._draw_equalizer(surface)
            self._draw_spectrum_cube(surface)
            self.particle_system.render(surface)
            self._draw_audio_info(surface)

    def _draw_background(self, surface: pygame.Surface) -> None:
        """绘制背景"""
        # 绘制渐变背景
        for y in range(self.height):
            alpha = int((y / self.height) * 100 + 50)
            color = pygame.Color(20, 20, 40, alpha)
            pygame.draw.line(surface, color, (0, y), (self.width, y))

    def _draw_waveform(self, surface: pygame.Surface) -> None:
        """绘制波形图"""
        # 绘制波形图（底部）
        waveform_height = 150
        waveform_y = self.height - waveform_height - self.padding
        
        # 绘制波形路径
        points = []
        for i, amp in enumerate(self.amplitude_history):
            x = int((i / len(self.amplitude_history)) * self.width)
            y = waveform_y + int((1 - amp) * waveform_height / 2)
            points.append((x, y))
        
        # 绘制波形线
        pygame.draw.lines(surface, self.waveform_color, False, points, 2)
        
        # 填充波形下方
        filled_points = points + [(self.width, waveform_y + waveform_height // 2), (0, waveform_y + waveform_height // 2)]
        waveform_surface = pygame.Surface((self.width, waveform_height), pygame.SRCALPHA)
        waveform_surface.fill((0, 0, 0, 0))
        pygame.draw.polygon(waveform_surface, (0, 255, 255, 50), filled_points)
        surface.blit(waveform_surface, (0, waveform_y))

    def _draw_spectrum_waterfall(self, surface: pygame.Surface) -> None:
        """绘制频谱瀑布图"""
        waterfall_width = 200
        waterfall_height = self.height - 300
        waterfall_x = self.padding
        waterfall_y = self.padding
        
        # 创建临时表面用于绘制瀑布图
        waterfall_surface = pygame.Surface((waterfall_width, waterfall_height))
        waterfall_surface.fill((0, 0, 0))
        
        # 绘制频谱瀑布图（优化性能）
        for i in range(min(waterfall_width, self.spectrum_history.shape[1])):
            for j in range(min(waterfall_height, self.spectrum_history.shape[0])):
                value = self.spectrum_history[j, i]
                if value > 0:
                    intensity = int(min(255, value * 10))
                    color = pygame.Color(intensity, 0, 255 - intensity)
                    y = waterfall_height - j - 1
                    waterfall_surface.set_at((i, y), color)
        
        # 将瀑布图绘制到主表面
        surface.blit(waterfall_surface, (waterfall_x, waterfall_y))

    def _draw_equalizer(self, surface: pygame.Surface) -> None:
        """绘制动态均衡器"""
        equalizer_width = 200
        equalizer_height = self.height - 300
        equalizer_x = self.width - equalizer_width - self.padding
        equalizer_y = self.padding
        bands = 32
        
        # 获取频谱数据
        if "frequency" in self.audio_features and "mel_spectrogram" in self.audio_features["frequency"]:
            mel_spec = self.audio_features["frequency"]["mel_spectrogram"]
            if mel_spec.size > 0:
                # 计算每个频段的能量
                band_energy = []
                band_size = mel_spec.shape[0] // bands
                for i in range(bands):
                    start = i * band_size
                    end = (i + 1) * band_size
                    if end <= mel_spec.shape[0]:
                        energy = np.mean(mel_spec[start:end])
                        band_energy.append(energy)
                
                # 归一化能量
                if len(band_energy) > 0 and np.max(band_energy) > 0:
                    band_energy = band_energy / np.max(band_energy)
                    
                    # 绘制均衡器条（优化性能，不使用渐变）
                    bar_width = (equalizer_width - (bands - 1) * 2) // bands
                    for i, energy in enumerate(band_energy):
                        bar_height = int(energy * equalizer_height)
                        x = equalizer_x + i * (bar_width + 2)
                        y = equalizer_y + equalizer_height - bar_height
                        
                        # 简单绘制矩形，不使用渐变效果以提高性能
                        if bar_height > 0:
                            pygame.draw.rect(surface, pygame.Color(0, 255, 255), (x, y, bar_width, bar_height))

    def _draw_spectrum_cube(self, surface: pygame.Surface) -> None:
        """绘制3D频谱立方体"""
        cube_size = min(self.width, self.height) // 3
        cube_x = self.center_x - cube_size // 2
        cube_y = self.center_y - cube_size // 2
        
        # 获取频谱数据
        if "frequency" in self.audio_features and "mel_spectrogram" in self.audio_features["frequency"]:
            mel_spec = self.audio_features["frequency"]["mel_spectrogram"]
            if mel_spec.size > 0:
                # 计算每个频段的能量
                bands = 8
                band_energy = []
                band_size = mel_spec.shape[0] // bands
                for i in range(bands):
                    start = i * band_size
                    end = (i + 1) * band_size
                    if end <= mel_spec.shape[0]:
                        energy = np.mean(mel_spec[start:end])
                        band_energy.append(energy)
                
                # 归一化能量
                if len(band_energy) > 0 and np.max(band_energy) > 0:
                    band_energy = band_energy / np.max(band_energy)
                    
                    # 绘制3D立方体
                    for i, energy in enumerate(band_energy):
                        # 计算立方体位置
                        x = cube_x + (i % 4) * (cube_size // 4)
                        y = cube_y + (i // 4) * (cube_size // 2)
                        size = int((energy + 0.1) * cube_size // 5)
                        
                        # 绘制立方体
                        if size > 0:
                            # 绘制立方体边框
                            pygame.draw.rect(surface, (255, 255, 255), (x, y, size, size), 1)
                            # 绘制立方体填充
                            color = pygame.Color(int(energy * 255), 0, int((1 - energy) * 255))
                            pygame.draw.rect(surface, color, (x + 1, y + 1, size - 2, size - 2))

    def _draw_beat_flash(self, surface: pygame.Surface) -> None:
        """绘制节拍闪光效果"""
        if self.beat_flash_alpha > 0:
            # 创建闪光表面
            flash_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            color = pygame.Color(255, 255, 255, self.beat_flash_alpha)
            flash_surface.fill(color)
            
            # 绘制闪光
            surface.blit(flash_surface, (0, 0))
            
            # 衰减闪光
            self.beat_flash_alpha = max(0, self.beat_flash_alpha - 5)

    def _draw_audio_info(self, surface: pygame.Surface) -> None:
        """绘制音频信息"""
        # 绘制音频信息（顶部）
        y_offset = self.padding
        
        # 绘制BPM
        if "rhythm" in self.audio_features and "bpm" in self.audio_features["rhythm"]:
            bpm = self.audio_features["rhythm"]["bpm"]
            text = self.font.render(f"BPM: {bpm:.1f}", True, self.text_color)
            surface.blit(text, (self.padding, y_offset))
            y_offset += 30
        
        # 绘制响度
        if "temporal" in self.audio_features and "loudness" in self.audio_features["temporal"]:
            loudness = self.audio_features["temporal"]["loudness"]
            if len(loudness) > 0:
                loudness_value = np.mean(loudness)
                text = self.font.render(f"Loudness: {loudness_value:.2f}", True, self.text_color)
                surface.blit(text, (self.padding, y_offset))
                y_offset += 30
        
        # 绘制节拍状态
        if "rhythm" in self.audio_features and "is_beat" in self.audio_features["rhythm"]:
            is_beat = self.audio_features["rhythm"]["is_beat"]
            beat_status = "Beat!" if is_beat else ""
            text = self.font.render(beat_status, True, self.text_color)
            surface.blit(text, (self.width - 100, self.padding))
