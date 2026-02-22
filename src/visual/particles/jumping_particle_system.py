import pygame
import numpy as np
from typing import Dict, Any, List
from ..renderer.visual_renderer import VisualComponent


class JumpingParticleSystem(VisualComponent):
    """跳动粒子系统组件"""

    @property
    def name(self) -> str:
        return "jumping_particles"

    def initialize(self, surface: pygame.Surface, config: Dict[str, Any]) -> None:
        """初始化跳动粒子系统"""
        self.surface = surface
        self.config = config.get("jumping_particles", {})
        self.width, self.height = surface.get_size()
        self.center_x, self.center_y = self.width // 2, self.height // 2
        
        # 粒子系统参数
        self.count = 300  # 固定粒子数量（减少数量，提高艺术感）
        self.min_size = 3
        self.max_size = 8
        self.min_jump_height = 30
        self.max_jump_height = 150
        self.min_jump_speed = 0.1
        self.max_jump_speed = 0.2
        self.trail_length = 8  # 减少轨迹长度，避免混乱
        
        # 粒子颜色
        self.base_color = pygame.Color(255, 255, 255)
        self.frequency_based_color = True
        
        # 背景震动效果参数
        self.shake_intensity = 0
        self.shake_decay = 0.95
        self.max_shake = 8
        
        # 初始化粒子
        self.particles = []
        for _ in range(self.count):
            # 粒子位置围绕中心分布，更有整体感
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
                "beat_response": np.random.uniform(0.8, 1.5)  # 粒子对节拍的响应程度
            }
            self.particles.append(particle)

    def update(self, audio_features: Dict[str, Any], dt: float) -> None:
        """更新跳动粒子系统"""
        self.audio_features = audio_features
        
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
        
        # 更新每个粒子
        for particle in self.particles:
            # 基于振幅调整跳动强度
            amplitude_influence = amplitude * 3 + 0.5
            
            # 更新跳动相位
            particle["jump_phase"] += particle["jump_speed"] * amplitude_influence
            
            # 计算跳动位置（使用正弦函数产生平滑的跳跃）
            jump_offset = np.sin(particle["jump_phase"]) * particle["jump_height"] * amplitude_influence
            
            # 基于频率调整水平偏移
            horizontal_offset = 0
            if spectrum is not None and spectrum.size > 0:
                band_index = min(particle["frequency_band"], spectrum.shape[0] - 1)
                band_energy = np.mean(spectrum[band_index]) if spectrum.shape[1] > 0 else 0
                horizontal_offset = np.cos(particle["jump_phase"] * 0.3) * band_energy * 2
            
            # 更新粒子位置
            particle["x"] = particle["base_x"] + horizontal_offset
            particle["y"] = particle["base_y"] - jump_offset
            
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
            if self.frequency_based_color and spectrum is not None and spectrum.size > 0:
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
        """渲染跳动粒子系统"""
        if not hasattr(self, "audio_features"):
            return
        
        # 应用背景震动效果
        if self.shake_intensity > 0:
            # 创建一个临时表面来绘制震动效果
            temp_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            # 绘制所有内容到临时表面
            self._draw_particles(temp_surface)
            
            # 计算震动偏移
            shake_x = int(np.sin(pygame.time.get_ticks() * 0.01) * self.shake_intensity)
            shake_y = int(np.cos(pygame.time.get_ticks() * 0.01) * self.shake_intensity)
            
            # 将临时表面绘制到主表面，应用震动偏移
            surface.blit(temp_surface, (shake_x, shake_y))
        else:
            # 正常绘制
            self._draw_particles(surface)

    def _draw_particles(self, surface: pygame.Surface) -> None:
        """绘制粒子"""
        # 绘制粒子轨迹
        for particle in self.particles:
            if len(particle["trail"]) > 1:
                # 绘制轨迹
                for i in range(len(particle["trail"]) - 1):
                    alpha = int((i / len(particle["trail"])) * 80)  # 减少轨迹透明度，避免混乱
                    trail_color = pygame.Color(
                        particle["color"].r,
                        particle["color"].g,
                        particle["color"].b,
                        alpha
                    )
                    start_pos = particle["trail"][i]
                    end_pos = particle["trail"][i + 1]
                    # 轨迹线宽设为1，避免线条过粗
                    pygame.draw.line(surface, trail_color, start_pos, end_pos, 1)
        
        # 绘制粒子
        for particle in self.particles:
            # 绘制粒子光晕（优化性能，只绘制2层）
            glow_radius = int(particle["size"]) * 2
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            # 简化光晕效果，只绘制2层
            for r in range(glow_radius, glow_radius // 2, -1):
                alpha = int(20)
                glow_color = pygame.Color(
                    particle["color"].r,
                    particle["color"].g,
                    particle["color"].b,
                    alpha
                )
                pygame.draw.circle(
                    glow_surface,
                    glow_color,
                    (glow_radius, glow_radius),
                    r
                )
            surface.blit(
                glow_surface,
                (
                    int(particle["x"]) - glow_radius,
                    int(particle["y"]) - glow_radius
                )
            )
            
            # 绘制粒子（后绘制，作为前景）
            pygame.draw.circle(
                surface,
                particle["color"],
                (int(particle["x"]), int(particle["y"])),
                int(particle["size"])
            )

    def _get_particle_color(self, frequency_value: float) -> pygame.Color:
        """根据频率值获取粒子颜色"""
        if self.frequency_based_color:
            # 基于频率的彩虹色，更有艺术感
            hue = int(frequency_value * 360)
            # 更柔和的颜色过渡
            r = int(255 * np.sin(0.0174 * (hue + 0)) ** 2)
            g = int(255 * np.sin(0.0174 * (hue + 120)) ** 2)
            b = int(255 * np.sin(0.0174 * (hue + 240)) ** 2)
            return pygame.Color(r, g, b)
        else:
            return self.base_color
