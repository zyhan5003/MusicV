import pygame
import numpy as np
from typing import Dict, Any, List, Optional
from ..renderer.visual_renderer import VisualComponent


class Particle:
    """粒子类"""

    def __init__(self, x: float, y: float, size: float, color: pygame.Color, velocity: np.ndarray, life: float):
        """初始化粒子"""
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.velocity = velocity
        self.life = life
        self.max_life = life
        self.original_size = size

    def update(self, dt: float) -> bool:
        """更新粒子状态"""
        # 更新位置
        self.x += self.velocity[0] * dt
        self.y += self.velocity[1] * dt
        # 更新生命周期
        self.life -= dt
        # 更新大小（随生命周期减小）
        self.size = self.original_size * (self.life / self.max_life)
        # 返回是否存活
        return self.life > 0

    def render(self, surface: pygame.Surface) -> None:
        """渲染粒子"""
        if self.size > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size))


class ParticleSystem(VisualComponent):
    """粒子系统组件 - 创建流动的音频粒子效果"""

    @property
    def name(self) -> str:
        return "particles"

    def initialize(self, surface: pygame.Surface, config: Dict[str, Any]) -> None:
        """初始化粒子系统"""
        self.surface = surface
        self.config = config.get("particles", {})
        self.count = self.config.get("count", 500)
        self.size_range = self.config.get("size_range", {"min": 2, "max": 6})
        self.speed_range = self.config.get("speed_range", {"min": 20, "max": 80})
        self.color_config = self.config.get("color", {"base": "#ffffff", "frequency_based": True})
        self.base_color = pygame.Color(self.color_config["base"])
        self.frequency_based_color = self.color_config["frequency_based"]
        self.width, self.height = surface.get_size()
        self.center_x, self.center_y = self.width // 2, self.height // 2
        self.particles: List[Particle] = []
        self.emit_rate = 100  # 每秒发射粒子数
        self.last_emit_time = 0
        
        # 粒子运动模式
        self.movement_mode = "spiral"  # spiral, radial, wave
        
        # 性能优化：限制最大粒子数量
        self.max_particles = min(self.count, 800)

    def update(self, audio_features: Dict[str, Any], dt: float) -> None:
        """更新粒子系统"""
        self.audio_features = audio_features
        
        # 更新现有粒子
        self.particles = [p for p in self.particles if p.update(dt)]

        # 根据音频特征调整发射率
        emit_rate = self.emit_rate
        loudness = 0.5
        if "temporal" in audio_features and "loudness" in audio_features["temporal"]:
            loudness = np.mean(audio_features["temporal"]["loudness"])
            # 响度越大，发射率越高
            emit_rate = self.emit_rate * (1 + loudness * 3)

        # 发射新粒子（使用累积时间）
        self.last_emit_time += dt
        if self.last_emit_time >= 1.0 / emit_rate:
            emit_count = int(self.last_emit_time * emit_rate)
            if emit_count > 0:
                self._emit_particles(emit_count, audio_features)
            self.last_emit_time = 0

    def render(self, surface: pygame.Surface) -> None:
        """渲染粒子系统"""
        # 绘制粒子
        for particle in self.particles:
            particle.render(surface)

    def _emit_particles(self, count: int, audio_features: Dict[str, Any]) -> None:
        """发射粒子"""
        # 根据音频特征调整发射参数
        amplitude = 0.5
        frequency = 0.5
        loudness = 0.5

        if "temporal" in audio_features and "amplitude" in audio_features["temporal"]:
            amplitude = np.mean(audio_features["temporal"]["amplitude"])
        if "temporal" in audio_features and "loudness" in audio_features["temporal"]:
            loudness = np.mean(audio_features["temporal"]["loudness"])
        if "frequency" in audio_features and "spectrum" in audio_features["frequency"]:
            spectrum = audio_features["frequency"]["spectrum"]
            frequency = np.mean(spectrum) if spectrum.size > 0 else 0.5
        elif "frequency" in audio_features and "mel_spectrogram" in audio_features["frequency"]:
            mel_spec = audio_features["frequency"]["mel_spectrogram"]
            frequency = np.mean(mel_spec) if mel_spec.size > 0 else 0.5

        # 限制粒子数量
        if len(self.particles) >= self.max_particles:
            return

        # 发射粒子
        for _ in range(count):
            # 限制粒子数量
            if len(self.particles) >= self.max_particles:
                break
            # 根据运动模式计算发射位置和速度
            if self.movement_mode == "spiral":
                x, y, velocity = self._emit_spiral_particle(loudness, amplitude)
            elif self.movement_mode == "radial":
                x, y, velocity = self._emit_radial_particle(loudness, amplitude)
            else:  # wave
                x, y, velocity = self._emit_wave_particle(loudness, amplitude, frequency)

            # 计算大小
            base_size = np.random.uniform(self.size_range["min"], self.size_range["max"])
            size = base_size * (1 + loudness * 1.5)

            # 计算颜色
            if self.frequency_based_color:
                hue = (frequency % 1.0) * 360
                saturation = 80
                lightness = 50 + loudness * 20
                color = self._hsl_to_rgb(hue, saturation, lightness)
            else:
                brightness = 1 + loudness * 1.5
                r = max(0, min(255, int(self.base_color.r * brightness)))
                g = max(0, min(255, int(self.base_color.g * brightness)))
                b = max(0, min(255, int(self.base_color.b * brightness)))
                color = pygame.Color(r, g, b)

            # 计算生命周期
            life = np.random.uniform(2, 4) * (1 + loudness * 0.5)

            # 创建粒子
            particle = Particle(x, y, size, color, velocity, life)
            self.particles.append(particle)

    def _emit_spiral_particle(self, loudness: float, amplitude: float):
        """发射螺旋运动的粒子"""
        angle = np.random.uniform(0, 2 * np.pi)
        distance = np.random.uniform(0, 30)
        x = self.center_x + np.cos(angle) * distance
        y = self.center_y + np.sin(angle) * distance
        
        # 螺旋速度
        base_speed = np.random.uniform(self.speed_range["min"], self.speed_range["max"])
        speed = base_speed * (1 + loudness * 2)
        velocity_angle = angle + np.pi / 2 + np.random.uniform(-0.3, 0.3)
        velocity = np.array([
            np.cos(velocity_angle) * speed,
            np.sin(velocity_angle) * speed
        ])
        
        return x, y, velocity

    def _emit_radial_particle(self, loudness: float, amplitude: float):
        """发射径向运动的粒子"""
        angle = np.random.uniform(0, 2 * np.pi)
        distance = np.random.uniform(0, 20)
        x = self.center_x + np.cos(angle) * distance
        y = self.center_y + np.sin(angle) * distance
        
        # 径向速度
        base_speed = np.random.uniform(self.speed_range["min"], self.speed_range["max"])
        speed = base_speed * (1 + loudness * 2)
        velocity = np.array([
            np.cos(angle) * speed,
            np.sin(angle) * speed
        ])
        
        return x, y, velocity

    def _emit_wave_particle(self, loudness: float, amplitude: float, frequency: float):
        """发射波浪运动的粒子"""
        x = np.random.uniform(0, self.width)
        y = np.random.uniform(0, self.height)
        
        # 波浪速度
        base_speed = np.random.uniform(self.speed_range["min"], self.speed_range["max"])
        speed = base_speed * (1 + loudness * 2)
        velocity_angle = np.random.uniform(0, 2 * np.pi)
        velocity = np.array([
            np.cos(velocity_angle) * speed,
            np.sin(velocity_angle) * speed
        ])
        
        return x, y, velocity

    def _hsl_to_rgb(self, h: float, s: float, l: float) -> pygame.Color:
        """HSL 转 RGB"""
        h /= 360
        s /= 100
        l /= 100

        if s == 0:
            r = g = b = l
        else:
            def hue2rgb(p, q, t):
                if t < 0:
                    t += 1
                if t > 1:
                    t -= 1
                if t < 1/6:
                    return p + (q - p) * 6 * t
                if t < 1/2:
                    return q
                if t < 2/3:
                    return p + (q - p) * (2/3 - t) * 6
                return p

            q = l * (1 + s) if l < 0.5 else l + s - l * s
            p = 2 * l - q
            r = hue2rgb(p, q, h + 1/3)
            g = hue2rgb(p, q, h)
            b = hue2rgb(p, q, h - 1/3)

        return pygame.Color(int(r * 255), int(g * 255), int(b * 255))


class BeatParticleSystem(ParticleSystem):
    """节拍粒子系统 - 在节拍时爆发粒子"""

    @property
    def name(self) -> str:
        return "beat_particles"

    def update(self, audio_features: Dict[str, Any], dt: float) -> None:
        """更新节拍粒子系统"""
        # 基础粒子更新
        super().update(audio_features, dt)

        # 检测节拍
        if "rhythm" in audio_features and "is_beat" in audio_features["rhythm"]:
            if audio_features["rhythm"]["is_beat"]:
                # 节拍触发，发射额外粒子
                self._emit_beat_particles(int(self.count * 0.2), audio_features)
        elif "rhythm" in audio_features and "beat_strength" in audio_features["rhythm"]:
            # 兼容旧的节拍检测方法
            beat_strength = audio_features["rhythm"]["beat_strength"]
            if len(beat_strength) > 0 and np.max(beat_strength) > 0.8:
                # 节拍触发，发射额外粒子
                self._emit_beat_particles(int(self.count * 0.2), audio_features)

    def _emit_beat_particles(self, count: int, audio_features: Dict[str, Any]) -> None:
        """发射节拍粒子"""
        # 限制粒子数量
        if len(self.particles) >= self.max_particles:
            return

        # 根据音频特征调整发射参数
        amplitude = 1.0
        loudness = 1.0
        if "temporal" in audio_features and "amplitude" in audio_features["temporal"]:
            amplitude = np.mean(audio_features["temporal"]["amplitude"])
        if "temporal" in audio_features and "loudness" in audio_features["temporal"]:
            loudness = np.mean(audio_features["temporal"]["loudness"])

        # 增加发射数量，增强视觉效果
        count = int(count * 2)

        # 发射节拍粒子
        for _ in range(count):
            # 限制粒子数量
            if len(self.particles) >= self.max_particles:
                break
            # 计算发射位置（从中心向外）
            angle = np.random.uniform(0, 2 * np.pi)
            distance = np.random.uniform(0, 50)
            x = self.center_x + np.cos(angle) * distance
            y = self.center_y + np.sin(angle) * distance

            # 计算速度（节拍粒子速度更快）
            base_speed = np.random.uniform(self.speed_range["max"], self.speed_range["max"] * 3)
            speed = base_speed * (1 + loudness * 3)
            velocity_angle = angle + np.random.uniform(-0.2, 0.2)
            velocity = np.array([
                np.cos(velocity_angle) * speed,
                np.sin(velocity_angle) * speed
            ])

            # 计算大小（节拍粒子更大）
            base_size = np.random.uniform(self.size_range["max"], self.size_range["max"] * 2)
            size = base_size * (1 + loudness * 2)

            # 计算颜色（更亮的颜色）
            brightness = 1 + loudness * 2
            if np.random.random() < 0.3:
                # 金色粒子
                color = pygame.Color(
                    min(255, int(255 * brightness)),
                    min(255, int(215 * brightness)),
                    min(255, int(0 * brightness))
                )
            elif np.random.random() < 0.5:
                # 蓝色粒子
                color = pygame.Color(
                    min(255, int(0 * brightness)),
                    min(255, int(191 * brightness)),
                    min(255, int(255 * brightness))
                )
            else:
                # 红色粒子
                color = pygame.Color(
                    min(255, int(255 * brightness)),
                    min(255, int(0 * brightness)),
                    min(255, int(0 * brightness))
                )

            # 计算生命周期
            life = np.random.uniform(0.8, 1.5) * (1 + loudness * 0.5)

            # 创建粒子
            particle = Particle(x, y, size, color, velocity, life)
            self.particles.append(particle)
