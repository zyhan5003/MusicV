import pygame
import numpy as np
from typing import Dict, Any, List
from ..renderer.visual_renderer import VisualComponent
from src.audio.music_style_analyzer import MusicStyleAnalyzer


class StyleAwareParticleSystem(VisualComponent):
    """风格感知粒子系统组件"""

    @property
    def name(self) -> str:
        return "style_aware_particles"

    def initialize(self, surface: pygame.Surface, config: Dict[str, Any]) -> None:
        """初始化风格感知粒子系统"""
        self.surface = surface
        self.config = config.get("style_aware_particles", {})
        self.width, self.height = surface.get_size()
        self.center_x, self.center_y = self.width // 2, self.height // 2
        
        # 初始化音乐风格分析器
        self.style_analyzer = MusicStyleAnalyzer()
        self.current_style = self.config.get("manual_style", None)  # 手动设置的风格
        self.style_config = None
        
        # 粒子系统默认参数
        self.default_config = {
            "particle_count": 300,
            "min_size": 3,
            "max_size": 8,
            "min_jump_height": 50,
            "max_jump_height": 150,
            "min_jump_speed": 0.1,
            "max_jump_speed": 0.2,
            "trail_length": 8,
            "color_palette": "default",
            "movement_pattern": "default",
            "beat_response": 1.5
        }
        
        # 应用默认配置
        self._apply_config(self.default_config)
        
        # 背景震动效果参数
        self.shake_intensity = 0
        self.shake_decay = 0.95
        self.max_shake = 8
        
        # 初始化粒子
        self.particles = []
        self._initialize_particles()
        
        # 性能优化：缓存时间
        self._current_time = 0

    def _apply_config(self, config: Dict[str, Any]) -> None:
        """应用配置"""
        self.particle_count = config.get("particle_count", 300)
        self.min_size = config.get("min_size", 3)
        self.max_size = config.get("max_size", 8)
        self.min_jump_height = config.get("min_jump_height", 50)
        self.max_jump_height = config.get("max_jump_height", 150)
        self.min_jump_speed = config.get("min_jump_speed", 0.1)
        self.max_jump_speed = config.get("max_jump_speed", 0.2)
        self.trail_length = config.get("trail_length", 8)
        self.color_palette = config.get("color_palette", "default")
        self.movement_pattern = config.get("movement_pattern", "default")
        self.beat_response = config.get("beat_response", 1.5)

    def _initialize_particles(self) -> None:
        """初始化粒子"""
        self.particles = []
        for _ in range(self.particle_count):
            # 粒子位置围绕中心分布
            angle = np.random.uniform(0, 2 * np.pi)
            radius = np.random.uniform(0, min(self.width, self.height) // 3)
            x = self.center_x + np.cos(angle) * radius
            y = self.center_y + np.sin(angle) * radius
            
            particle = {
                "x": x,
                "y": y,
                "base_x": x,
                "base_y": y,
                "size": np.random.uniform(self.min_size, self.max_size),
                "color": self._get_particle_color(np.random.uniform(0, 1)),
                "jump_height": np.random.uniform(self.min_jump_height, self.max_jump_height),
                "jump_speed": np.random.uniform(self.min_jump_speed, self.max_jump_speed),
                "jump_phase": np.random.uniform(0, 2 * np.pi),
                "trail": [],
                "frequency_band": np.random.randint(0, 10),
                "amplitude_factor": np.random.uniform(0.8, 1.2),
                "beat_response": np.random.uniform(0.8, 1.5) * self.beat_response
            }
            self.particles.append(particle)

    def update(self, audio_features: Dict[str, Any], dt: float) -> None:
        """更新风格感知粒子系统"""
        self.audio_features = audio_features
        
        # 使用手动设置的风格
        if self.current_style and not self.style_config:
            self.style_config = self.style_analyzer.get_style_config(self.current_style)
            if self.style_config:
                self._apply_config(self.style_config)
                # 重新初始化粒子以应用新配置
                self._initialize_particles()
        
        # 获取音频特征
        amplitude = 0
        if "temporal" in audio_features and "amplitude" in audio_features["temporal"]:
            amp_data = audio_features["temporal"]["amplitude"]
            if len(amp_data) > 0:
                amplitude = np.mean(amp_data)
        
        spectrum = None
        if "frequency" in audio_features and "spectrum" in audio_features["frequency"]:
            spectrum = audio_features["frequency"]["spectrum"]
        
        is_beat = False
        if "rhythm" in audio_features and "is_beat" in audio_features["rhythm"]:
            is_beat = audio_features["rhythm"]["is_beat"]
        
        # 更新背景震动效果
        if is_beat:
            self.shake_intensity = self.max_shake
        else:
            self.shake_intensity = max(0, self.shake_intensity * self.shake_decay)
        
        # 性能优化：只调用一次pygame.time.get_ticks()
        self._current_time = pygame.time.get_ticks() * 0.001
        
        # 更新每个粒子
        for particle in self.particles:
            # 基于振幅调整跳动强度
            amplitude_influence = amplitude * 3 + 0.5
            
            # 更新跳动相位
            particle["jump_phase"] += particle["jump_speed"] * amplitude_influence
            
            # 计算核心主运动路径（基于时间的周期性运动）
            base_angle = np.pi * 2 * (particle["frequency_band"] / 10.0) + self._current_time * 0.5
            
            # 核心圆形运动路径
            radius = min(self.width, self.height) // 4
            core_x = self.center_x + np.cos(base_angle) * radius
            core_y = self.center_y + np.sin(base_angle) * radius
            
            # 计算跳动位置（始终有基础跳动，即使音频数据较小）
            jump_offset = 0
            if self.movement_pattern == "fluid_curve":
                # 流畅曲线运动（钢琴曲）
                jump_offset = np.sin(particle["jump_phase"]) * particle["jump_height"] * (amplitude_influence * 0.8 + 0.2)
            elif self.movement_pattern == "intense_jump":
                # 强烈跳跃运动（摇滚乐）
                jump_offset = np.sin(particle["jump_phase"]) * particle["jump_height"] * (amplitude_influence * 1.2 + 0.3)
            elif self.movement_pattern == "geometric_sync":
                # 几何同步运动（DJ音乐）
                jump_offset = np.sin(particle["jump_phase"] * 2) * particle["jump_height"] * (amplitude_influence * 1.0 + 0.2)
            elif self.movement_pattern == "slow_float":
                # 缓慢漂浮运动（轻音乐）
                jump_offset = np.sin(particle["jump_phase"] * 0.5) * particle["jump_height"] * (amplitude_influence * 0.6 + 0.4)
            else:
                # 默认运动
                jump_offset = np.sin(particle["jump_phase"]) * particle["jump_height"] * (amplitude_influence * 0.8 + 0.2)
            
            # 基于频率调整水平偏移
            horizontal_offset = 0
            if spectrum is not None and spectrum.size > 0:
                band_index = min(particle["frequency_band"], spectrum.shape[0] - 1)
                band_energy = np.mean(spectrum[band_index]) if spectrum.shape[1] > 0 else 0
                horizontal_offset = np.cos(particle["jump_phase"] * 0.3) * (band_energy * 2 + 5)
            else:
                # 即使没有频谱数据，也添加一些基础水平运动
                horizontal_offset = np.cos(particle["jump_phase"] * 0.3) * 5
            
            # 更新粒子位置（结合核心路径和跳动）
            particle["x"] = core_x + horizontal_offset
            particle["y"] = core_y - jump_offset
            
            # 更新粒子的基础位置，使其跟随核心路径
            particle["base_x"] = core_x
            particle["base_y"] = core_y
            
            # 边界检查
            if particle["x"] < 0:
                particle["x"] = 0
                particle["base_x"] = 0
            elif particle["x"] > self.width:
                particle["x"] = self.width
                particle["base_x"] = self.width
            if particle["y"] < 0:
                particle["y"] = 0
            elif particle["y"] > self.height:
                particle["y"] = self.height
                particle["base_y"] = self.height
            
            # 更新轨迹
            particle["trail"].append((particle["x"], particle["y"]))
            if len(particle["trail"]) > self.trail_length:
                particle["trail"].pop(0)
            
            # 基于频谱更新颜色
            if spectrum is not None and spectrum.size > 0:
                band_index = min(particle["frequency_band"], spectrum.shape[0] - 1)
                band_energy = np.mean(spectrum[band_index]) if spectrum.shape[1] > 0 else 0
                particle["color"] = self._get_particle_color(band_energy)
            
            # 基于节拍调整粒子属性
            if is_beat:
                # 节拍处增加跳跃高度
                particle["jump_height"] *= particle["beat_response"]
                if particle["jump_height"] > self.max_jump_height:
                    particle["jump_height"] = self.max_jump_height
            else:
                # 非节拍时恢复跳跃高度
                particle["jump_height"] *= 0.98
                if particle["jump_height"] < self.min_jump_height:
                    particle["jump_height"] = self.min_jump_height

    def render(self, surface: pygame.Surface) -> None:
        """渲染风格感知粒子系统"""
        if not hasattr(self, "audio_features"):
            return
        
        # 应用背景震动效果
        if self.shake_intensity > 0:
            # 创建一个临时表面来绘制震动效果
            temp_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            # 绘制所有内容到临时表面
            self._draw_particles(temp_surface)
            self._draw_style_info(temp_surface)
            
            # 计算震动偏移
            shake_x = int(np.sin(pygame.time.get_ticks() * 0.01) * self.shake_intensity)
            shake_y = int(np.cos(pygame.time.get_ticks() * 0.01) * self.shake_intensity)
            
            # 将临时表面绘制到主表面，应用震动偏移
            surface.blit(temp_surface, (shake_x, shake_y))
        else:
            # 正常绘制
            self._draw_particles(surface)
            self._draw_style_info(surface)

    def _draw_particles(self, surface: pygame.Surface) -> None:
        """绘制粒子"""
        # 绘制粒子轨迹
        for particle in self.particles:
            if len(particle["trail"]) > 1:
                # 绘制轨迹
                for i in range(len(particle["trail"]) - 1):
                    alpha = int((i / len(particle["trail"])) * 80)
                    trail_color = pygame.Color(
                        particle["color"].r,
                        particle["color"].g,
                        particle["color"].b,
                        alpha
                    )
                    start_pos = particle["trail"][i]
                    end_pos = particle["trail"][i + 1]
                    pygame.draw.line(surface, trail_color, start_pos, end_pos, 1)
        
        # 绘制粒子
        for particle in self.particles:
            # 性能优化：简化光晕效果，只绘制1层
            glow_radius = int(particle["size"]) * 1.5
            glow_color = pygame.Color(
                particle["color"].r,
                particle["color"].g,
                particle["color"].b,
                30
            )
            pygame.draw.circle(
                surface,
                glow_color,
                (int(particle["x"]), int(particle["y"])),
                glow_radius
            )
            
            # 绘制粒子
            pygame.draw.circle(
                surface,
                particle["color"],
                (int(particle["x"]), int(particle["y"])),
                int(particle["size"])
            )

    def _draw_style_info(self, surface: pygame.Surface) -> None:
        """绘制风格信息"""
        if self.current_style:
            # 使用系统默认字体，支持中文
            font = pygame.font.SysFont("SimHei", 24)
            style_info = self.style_analyzer.get_style_info(self.current_style)
            if style_info:
                text = font.render(f"风格: {style_info['name']}", True, pygame.Color(255, 255, 255))
                surface.blit(text, (20, 20))
                # 绘制风格描述
                desc_font = pygame.font.SysFont("SimHei", 16)
                desc_text = desc_font.render(f"描述: {style_info['description']}", True, pygame.Color(200, 200, 200))
                surface.blit(desc_text, (20, 50))

    def _get_particle_color(self, frequency_value: float) -> pygame.Color:
        """根据频率值和颜色 palette 获取粒子颜色"""
        if self.color_palette == "soft_pastel":
            # 柔和的 pastel 颜色（钢琴曲）
            hue = int(frequency_value * 360)
            r = int(200 + 55 * np.sin(0.0174 * (hue + 0)) ** 2)
            g = int(200 + 55 * np.sin(0.0174 * (hue + 120)) ** 2)
            b = int(200 + 55 * np.sin(0.0174 * (hue + 240)) ** 2)
            return pygame.Color(r, g, b)
        elif self.color_palette == "vibrant_contrast":
            # 鲜艳的对比色（摇滚乐）
            hue = int(frequency_value * 360)
            r = int(255 * np.sin(0.0174 * (hue + 0)) ** 2)
            g = int(255 * np.sin(0.0174 * (hue + 180)) ** 2)
            b = int(255 * np.sin(0.0174 * (hue + 90)) ** 2)
            return pygame.Color(r, g, b)
        elif self.color_palette == "neon_glow":
            # 霓虹发光色（DJ音乐）
            hue = int(frequency_value * 360)
            r = int(255 * np.sin(0.0174 * (hue + 0)) ** 2)
            g = int(255 * np.sin(0.0174 * (hue + 150)) ** 2)
            b = int(255 * np.sin(0.0174 * (hue + 300)) ** 2)
            return pygame.Color(r, g, b)
        elif self.color_palette == "soft_blue":
            # 柔和的蓝色调（轻音乐）
            hue = int(frequency_value * 60) + 180  # 限定在蓝色范围内
            r = int(150 + 100 * np.sin(0.0174 * (hue + 0)) ** 2)
            g = int(150 + 100 * np.sin(0.0174 * (hue + 60)) ** 2)
            b = int(150 + 100 * np.sin(0.0174 * (hue + 120)) ** 2)
            return pygame.Color(r, g, b)
        else:
            # 默认彩虹色
            hue = int(frequency_value * 360)
            r = int(255 * np.sin(0.0174 * (hue + 0)) ** 2)
            g = int(255 * np.sin(0.0174 * (hue + 120)) ** 2)
            b = int(255 * np.sin(0.0174 * (hue + 240)) ** 2)
            return pygame.Color(r, g, b)
