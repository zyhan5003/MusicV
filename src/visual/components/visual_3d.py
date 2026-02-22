import pygame
import numpy as np
from typing import Dict, Any, Optional
from ..renderer.visual_renderer import VisualComponent


class SpectrumCubeVisualizer(VisualComponent):
    """3D 频谱立方体可视化组件"""

    @property
    def name(self) -> str:
        return "spectrum_cube"

    def initialize(self, surface: pygame.Surface, config: Dict[str, Any]) -> None:
        """初始化 3D 频谱立方体组件"""
        self.surface = surface
        self.config = config.get("3d", {}).get("spectrum_cube", {})
        self.size = self.config.get("size", 10)
        self.color_map = self.config.get("color_map", "plasma")
        self.rotation_speed = self.config.get("rotation_speed", 0.01)
        self.width, self.height = surface.get_size()
        self.center_x, self.center_y = self.width // 2, self.height // 2
        self.cube_size = min(self.width, self.height) // 2
        self.rotation_x, self.rotation_y = 0, 0
        self.bands = 16  # 减少频谱带数以提高性能

    def update(self, audio_features: Dict[str, Any], dt: float) -> None:
        """更新 3D 频谱立方体"""
        # 更新旋转
        self.rotation_x += self.rotation_speed * dt * 60
        self.rotation_y += self.rotation_speed * dt * 60

        # 获取频谱数据
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
        """渲染 3D 频谱立方体"""
        if not hasattr(self, "band_energy"):
            return

        # 归一化能量
        if np.max(self.band_energy) > 0:
            band_energy = self.band_energy / np.max(self.band_energy)
        else:
            band_energy = self.band_energy

        # 绘制 3D 效果的频谱立方体
        self._draw_cube(surface, band_energy)

    def _draw_cube(self, surface: pygame.Surface, band_energy: np.ndarray) -> None:
        """绘制 3D 立方体（优化性能）"""
        cube_size = self.cube_size
        half_size = cube_size // 2

        # 预计算旋转矩阵
        rad_x = np.radians(self.rotation_x)
        rad_y = np.radians(self.rotation_y)
        cos_x, sin_x = np.cos(rad_x), np.sin(rad_x)
        cos_y, sin_y = np.cos(rad_y), np.sin(rad_y)

        # 存储所有点以便后续绘制连接线
        points = []

        # 生成立方体顶点
        for i in range(self.bands):
            # 计算每个频段的高度
            height = band_energy[i] * cube_size
            # 计算位置
            angle = (i / self.bands) * 2 * np.pi
            x = np.cos(angle) * half_size
            z = np.sin(angle) * half_size
            y = -half_size

            # 应用旋转
            x_rot = x * cos_x - y * sin_x
            y_rot = x * sin_x + y * cos_x
            z_rot = z * cos_y - y_rot * sin_y
            y_rot = z * sin_y + y_rot * cos_y

            # 透视投影
            scale = 200 / (200 + y_rot)
            screen_x = int(self.center_x + x_rot * scale)
            screen_y = int(self.center_y + z_rot * scale)
            screen_size = int(10 * scale)

            # 计算颜色
            intensity = band_energy[i]
            color = self._get_color(intensity)

            # 绘制立方体
            pygame.draw.rect(
                surface, 
                color, 
                (screen_x - screen_size // 2, screen_y - screen_size // 2, screen_size, screen_size)
            )

            points.append((screen_x, screen_y, color))

        # 绘制连接线
        for i in range(1, len(points)):
            pygame.draw.line(
                surface, 
                points[i][2], 
                (points[i][0], points[i][1]), 
                (points[i-1][0], points[i-1][1]), 
                2
            )

    def _get_color(self, intensity: float) -> pygame.Color:
        """根据强度获取颜色"""
        # 简单的颜色映射
        r = int(intensity * 255)
        g = int((1 - intensity) * 255)
        b = int(intensity * 128 + 127)
        return pygame.Color(r, g, b)


class Audio3DModelVisualizer(VisualComponent):
    """音频特征驱动的 3D 模型动效组件"""

    @property
    def name(self) -> str:
        return "3d_model"

    def initialize(self, surface: pygame.Surface, config: Dict[str, Any]) -> None:
        """初始化 3D 模型组件"""
        self.surface = surface
        self.config = config.get("3d", {}).get("model", {})
        self.enable = self.config.get("enable", True)
        self.width, self.height = surface.get_size()
        self.center_x, self.center_y = self.width // 2, self.height // 2
        self.scale = 1.0
        self.rotation_x = 0
        self.rotation_y = 0
        self.rotation_z = 0
        
        # 3D球体参数
        self.sphere_radius = 150
        self.sphere_points = self._generate_sphere_points(16, 16)
        
        # 颜色配置
        self.base_color = pygame.Color(100, 200, 255)
        self.accent_color = pygame.Color(255, 100, 150)

    def _generate_sphere_points(self, lat_lines: int, lon_lines: int) -> np.ndarray:
        """生成球体点"""
        points = []
        for i in range(lat_lines + 1):
            lat = np.pi * i / lat_lines
            for j in range(lon_lines):
                lon = 2 * np.pi * j / lon_lines
                x = self.sphere_radius * np.sin(lat) * np.cos(lon)
                y = self.sphere_radius * np.sin(lat) * np.sin(lon)
                z = self.sphere_radius * np.cos(lat)
                points.append([x, y, z])
        return np.array(points)

    def update(self, audio_features: Dict[str, Any], dt: float) -> None:
        """更新 3D 模型"""
        self.audio_features = audio_features
        if not self.enable:
            return

        # 根据音频特征更新模型参数
        loudness = 0.5
        if "temporal" in audio_features and "loudness" in audio_features["temporal"]:
            loudness = np.mean(audio_features["temporal"]["loudness"])
        
        # 更新缩放
        self.scale = 0.8 + loudness * 0.5
        
        # 更新旋转速度（响度越大，旋转越快）
        rotation_speed = 0.5 + loudness * 2.0
        self.rotation_x += rotation_speed * dt
        self.rotation_y += rotation_speed * dt * 0.7
        self.rotation_z += rotation_speed * dt * 0.3

    def render(self, surface: pygame.Surface) -> None:
        """渲染 3D 模型"""
        if not self.enable:
            return

        # 获取音频特征用于动态效果
        loudness = 0.5
        if hasattr(self, 'audio_features'):
            if "temporal" in self.audio_features and "loudness" in self.audio_features["temporal"]:
                loudness = np.mean(self.audio_features["temporal"]["loudness"])
        
        # 绘制3D球体
        self._draw_3d_sphere(surface, loudness)
        
        # 绘制音频波形环
        self._draw_audio_ring(surface, loudness)

    def _draw_3d_sphere(self, surface: pygame.Surface, loudness: float) -> None:
        """绘制3D球体"""
        # 预计算旋转矩阵
        rad_x = np.radians(self.rotation_x)
        rad_y = np.radians(self.rotation_y)
        rad_z = np.radians(self.rotation_z)
        
        cos_x, sin_x = np.cos(rad_x), np.sin(rad_x)
        cos_y, sin_y = np.cos(rad_y), np.sin(rad_y)
        cos_z, sin_z = np.cos(rad_z), np.sin(rad_z)
        
        # 投影并绘制每个点
        for point in self.sphere_points:
            x, y, z = point
            
            # 应用旋转
            x, y = x * cos_x - y * sin_x, x * sin_x + y * cos_x
            x, z = x * cos_y - z * sin_y, x * sin_y + z * cos_y
            y, z = y * cos_z - z * sin_z, y * sin_z + z * cos_z
            
            # 根据响度调整球体大小
            x *= self.scale
            y *= self.scale
            z *= self.scale
            
            # 透视投影
            fov = 500
            distance = 400
            scale = fov / (distance + z)
            screen_x = int(self.center_x + x * scale)
            screen_y = int(self.center_y + y * scale)
            
            # 根据深度调整颜色和大小
            depth_factor = (z + self.sphere_radius) / (2 * self.sphere_radius)
            point_size = max(1, int(3 * scale * (1 - depth_factor * 0.5)))
            
            # 混合颜色
            color_r = int(self.base_color.r * (1 - depth_factor) + self.accent_color.r * depth_factor)
            color_g = int(self.base_color.g * (1 - depth_factor) + self.accent_color.g * depth_factor)
            color_b = int(self.base_color.b * (1 - depth_factor) + self.accent_color.b * depth_factor)
            
            # 根据响度增加亮度
            brightness = 1 + loudness * 0.5
            color_r = min(255, int(color_r * brightness))
            color_g = min(255, int(color_g * brightness))
            color_b = min(255, int(color_b * brightness))
            
            color = pygame.Color(color_r, color_g, color_b)
            
            # 绘制点
            if 0 <= screen_x < self.width and 0 <= screen_y < self.height:
                pygame.draw.circle(surface, color, (screen_x, screen_y), point_size)

    def _draw_audio_ring(self, surface: pygame.Surface, loudness: float) -> None:
        """绘制音频波形环"""
        ring_radius = int(200 * self.scale)
        num_points = 64
        
        # 获取频谱数据
        spectrum_data = np.ones(num_points) * 0.5
        if hasattr(self, 'audio_features') and "frequency" in self.audio_features:
            if "spectrum" in self.audio_features["frequency"]:
                spectrum = self.audio_features["frequency"]["spectrum"]
                if spectrum.size > 0:
                    # 降采样到num_points
                    spectrum_data = np.interp(
                        np.linspace(0, spectrum.size - 1, num_points),
                        np.arange(spectrum.size),
                        spectrum.flatten()
                    )
                    # 归一化
                    spectrum_data = spectrum_data / (np.max(spectrum_data) + 0.001)
        
        # 绘制波形环
        points = []
        for i in range(num_points):
            angle = (i / num_points) * 2 * np.pi
            # 根据频谱数据调整半径
            radius = ring_radius * (1 + spectrum_data[i] * 0.5 * loudness)
            x = self.center_x + np.cos(angle) * radius
            y = self.center_y + np.sin(angle) * radius
            points.append((x, y))
        
        # 绘制多边形
        if len(points) > 2:
            # 填充
            fill_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            fill_color = pygame.Color(
                self.accent_color.r,
                self.accent_color.g,
                self.accent_color.b,
                50
            )
            pygame.draw.polygon(fill_surface, fill_color, points)
            surface.blit(fill_surface, (0, 0))
            
            # 边框
            pygame.draw.lines(surface, self.accent_color, True, points, 2)
