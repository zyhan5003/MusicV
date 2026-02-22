import pygame
import numpy as np
from typing import Dict, Any, List
from .effect_base import EffectBase
from .beat_utils import OnsetIntensityTracker, calculate_particle_count


class FireParticle:
    """火焰粒子类"""

    def __init__(self, x: float, y: float, size: float, color: pygame.Color, 
                 velocity: np.ndarray, life: float, max_life: float, screen_height: int = 0):
        """初始化火焰粒子"""
        self.x = x
        self.y = y
        self.base_size = size
        self.size = size
        self.base_color = color
        self.current_color = color
        self.velocity = velocity
        self.life = life
        self.max_life = max_life
        self.screen_height = screen_height  # 添加屏幕高度参数
        self.shake_offset = np.array([0.0, 0.0])
        self.trail_points = []
        self.max_trail_length = 10
        self.pulse_phase = np.random.uniform(0, 2 * np.pi)
        self.rotation = np.random.uniform(0, 360)
        self.rotation_speed = np.random.uniform(-5, 5)

    def update(self, dt: float, audio_features: Dict[str, Any]) -> bool:
        """更新火焰粒子"""
        # 提取多种音频特征用于控制不同维度
        loudness = 0.0
        beat_strength = 0.0
        spectral_centroid = 0.0
        zero_crossing_rate = 0.0
        spectral_bandwidth = 0.0
        
        # 响度 - 控制抖动强度
        if "temporal" in audio_features and "loudness" in audio_features["temporal"]:
            loudness = float(np.mean(audio_features["temporal"]["loudness"]))
        
        # 节拍强度 - 控制轨迹震颤
        if "rhythm" in audio_features and "beat_strength" in audio_features["rhythm"]:
            beat_strength = float(np.mean(audio_features["rhythm"]["beat_strength"]))
        
        # 频谱质心 - 控制颜色
        if "frequency" in audio_features and "spectral_centroid" in audio_features["frequency"]:
            spectral_centroid = float(np.mean(audio_features["frequency"]["spectral_centroid"]))
        
        # 过零率 - 控制水平扩散
        if "temporal" in audio_features and "zero_crossing_rate" in audio_features["temporal"]:
            zero_crossing_rate = float(np.mean(audio_features["temporal"]["zero_crossing_rate"]))
        
        # 频谱带宽 - 控制脉冲强度
        if "frequency" in audio_features and "spectral_bandwidth" in audio_features["frequency"]:
            spectral_bandwidth = float(np.mean(audio_features["frequency"]["spectral_bandwidth"]))
        
        # 【维度3】响度控制抖动强度（增强幅度）
        shake_intensity = loudness * 12.0
        
        # 【维度4】节拍强度控制轨迹震颤（增强幅度）
        tremor_intensity = beat_strength * 10.0
        
        # 【维度5】过零率控制水平扩散速度
        spread_mod = 1.0 + zero_crossing_rate * 3.0
        
        # 应用抖动
        self.shake_offset = np.array([
            np.random.uniform(-shake_intensity, shake_intensity),
            np.random.uniform(-shake_intensity, shake_intensity)
        ])
        
        # 更新位置（加入扩散效果）
        self.x += self.velocity[0] * dt * 60 * spread_mod
        self.y += self.velocity[1] * dt * 60
        self.x += np.random.uniform(-tremor_intensity, tremor_intensity)
        
        # 更新旋转
        self.rotation += self.rotation_speed * dt * 60
        
        # 更新脉冲相位
        self.pulse_phase += dt * 15
        
        # 【维度6】响度+频谱带宽控制脉冲大小
        pulse_factor = 1.0 + np.sin(self.pulse_phase) * 0.5 * loudness * (1 + spectral_bandwidth / 1500)
        self.size = self.base_size * pulse_factor
        
        # 【维度7】频谱质心控制颜色
        hue_shift = (spectral_centroid / 5000.0) * 40
        h, s, v, a = self.base_color.hsva
        h = (h + hue_shift) % 360
        self.current_color.hsva = (h, s, v, a)
        
        # 粒子向上移动
        self.velocity[1] -= 0.3 * dt * 60
        
        # 更新轨迹
        self.trail_points.append((self.x, self.y))
        if len(self.trail_points) > self.max_trail_length:
            self.trail_points.pop(0)
        
        # 减少生命值（但不要太快）
        # 大幅降低生命值减少速度，让粒子存活更长时间
        self.life -= dt * 0.02  # 从0.1降低到0.02，减少80%
        
        # 性能优化：火粒子超出屏幕顶部立即消亡
        # 不再依赖生命周期，而是直接根据位置判断
        if self.screen_height > 0 and self.y < -self.size:
            return False
        
        return self.life > 0

    def render(self, surface: pygame.Surface) -> None:
        """渲染火焰粒子"""
        if self.size > 0:
            # 渲染轨迹
            if len(self.trail_points) > 1:
                for i in range(len(self.trail_points) - 1):
                    alpha = int(255 * (i / len(self.trail_points)) * 0.4 * (self.life / self.max_life))
                    trail_color = pygame.Color(
                        self.current_color.r,
                        self.current_color.g,
                        self.current_color.b,
                        alpha
                    )
                    start_pos = (int(self.trail_points[i][0]), int(self.trail_points[i][1]))
                    end_pos = (int(self.trail_points[i + 1][0]), int(self.trail_points[i + 1][1]))
                    pygame.draw.line(surface, trail_color, start_pos, end_pos, 2)
            
            # 渲染粒子主体
            center_x = int(self.x + self.shake_offset[0])
            center_y = int(self.y + self.shake_offset[1])
            radius = int(self.size)
            
            # 绘制多层火焰效果
            alpha = int(255 * (self.life / self.max_life))
            
            # 外层（较亮）
            outer_color = pygame.Color(
                min(255, self.current_color.r + 50),
                min(255, self.current_color.g + 50),
                min(255, self.current_color.b + 50),
                alpha // 2
            )
            pygame.draw.circle(surface, outer_color, (center_x, center_y), radius + 2)
            
            # 中层
            mid_color = pygame.Color(
                self.current_color.r,
                self.current_color.g,
                self.current_color.b,
                int(alpha * 0.7)
            )
            pygame.draw.circle(surface, mid_color, (center_x, center_y), radius)
            
            # 内层（较暗）
            inner_color = pygame.Color(
                max(0, self.current_color.r - 50),
                max(0, self.current_color.g - 50),
                max(0, self.current_color.b - 50),
                alpha
            )
            pygame.draw.circle(surface, inner_color, (center_x, center_y), radius - 1)


class FireEffect(EffectBase):
    """火焰特效"""

    def __init__(self):
        """初始化火焰特效"""
        super().__init__("fire")

    def initialize(self, surface: pygame.Surface, config: Dict[str, Any]) -> None:
        """初始化火焰特效"""
        super().initialize(surface, config)
        self.width, self.height = surface.get_size()
        
        # 从配置中获取粒子数量（与GUI控件联动）
        particles_count = config.get("particles", {}).get("count", 1000)
        
        # 根据GUI粒子数量计算火焰粒子数量（按比例缩放）
        # GUI范围100-5000，映射到火焰粒子数量
        scale_factor = particles_count / 1000.0
        self.base_particle_count = int(config.get("base_particle_count", 150) * scale_factor)
        self.max_particle_count = int(config.get("max_particle_count", 700) * scale_factor)
        
        # 确保最小值
        self.base_particle_count = max(self.base_particle_count, 150)
        self.max_particle_count = max(self.max_particle_count, 700)
        
        self.base_spawn_rate = config.get("base_spawn_rate", 0.05)
        self.max_spawn_rate = config.get("max_spawn_rate", 0.15)
        self.base_size = config.get("base_size", 6.0)
        self.base_speed = config.get("base_speed", 3.0)
        self.fire_color = pygame.Color(config.get("fire_color", "#ff4500"))
        self.base_x = config.get("base_x", self.width // 2)
        self.base_y = config.get("base_y", self.height - 50)
        self.smoothing_factor = config.get("smoothing_factor", 0.3)
        self.fire_width = config.get("fire_width", 60)  # 火焰宽度
        self.fire_height = config.get("fire_height", 100)  # 火焰高度
        
        # 节拍变化检测
        self.last_onset_intensity = 0.0
        
        # onset强度跟踪器（更灵敏的平滑因子）
        self.onset_tracker = OnsetIntensityTracker(smoothing_factor=0.05)
        
        # 火焰粒子
        self.particles: List[FireParticle] = []
        self.spawn_timer = 0.0

    def _update_effect(self, audio_features: Dict[str, Any]) -> None:
        """更新火焰特效"""
        dt = 0.016  # 约60fps
        
        # 提取多种音频特征用于控制不同维度
        onset_intensity = 0.0
        loudness = 0.0
        beat_strength = 0.0
        spectral_centroid = 0.0
        zero_crossing_rate = 0.0
        spectral_bandwidth = 0.0
        
        # 1. onset强度 - 控制粒子生成数量
        onset_intensity = self.onset_tracker.update(audio_features)
        
        # 2. 响度 - 控制火焰高度和速度
        if "temporal" in audio_features and "loudness" in audio_features["temporal"]:
            loudness = float(np.mean(audio_features["temporal"]["loudness"]))
        
        # 3. 节拍强度 - 控制火焰宽度
        if "rhythm" in audio_features and "beat_strength" in audio_features["rhythm"]:
            beat_strength = float(np.mean(audio_features["rhythm"]["beat_strength"]))
        
        # 4. 频谱质心 - 控制颜色
        if "frequency" in audio_features and "spectral_centroid" in audio_features["frequency"]:
            spectral_centroid = float(np.mean(audio_features["frequency"]["spectral_centroid"]))
        
        # 5. 过零率 - 控制粒子密度
        if "temporal" in audio_features and "zero_crossing_rate" in audio_features["temporal"]:
            zero_crossing_rate = float(np.mean(audio_features["temporal"]["zero_crossing_rate"]))
        
        # 6. 频谱带宽 - 控制火焰活跃度
        if "frequency" in audio_features and "spectral_bandwidth" in audio_features["frequency"]:
            spectral_bandwidth = float(np.mean(audio_features["frequency"]["spectral_bandwidth"]))
        
        # 阈值：只有当onset强度超过阈值时才生成粒子（降低阈值以确保有粒子）
        threshold = 0.08
        
        # 【维度1】onset强度控制粒子生成数量
        if onset_intensity > threshold:
            burst_rate = (onset_intensity - threshold) * 10
            
            if not hasattr(self, 'burst_counter'):
                self.burst_counter = 0.0
            
            self.burst_counter += burst_rate
            
            while self.burst_counter >= 1.0:
                self.burst_counter -= 1.0
                spawn_y_ratio = np.random.uniform(0, 1) ** 2
                
                # 【维度2】响度控制火焰高度
                height_mod = 1.0 + loudness * 1.5  # 响度越大，火焰越高
                fire_height_mod = self.fire_height * height_mod
                
                x = self.base_x + np.random.uniform(-self.fire_width / 2, self.fire_width / 2)
                y = self.base_y - spawn_y_ratio * fire_height_mod
                
                # 【维度3】节拍强度控制火焰宽度
                width_mod = 1.0 + beat_strength * 0.8
                x = self.base_x + (x - self.base_x) * width_mod
                
                size_factor = 1.0 - spawn_y_ratio * 0.5
                size = (self.base_size + np.random.uniform(-2, 2)) * size_factor
                
                # 【维度4】频谱带宽控制速度
                speed_mod = 1.0 + spectral_bandwidth / 1500
                speed_factor = (1.0 + spawn_y_ratio * 0.5) * speed_mod
                velocity = np.array([
                    np.random.uniform(-1, 1) * speed_factor,
                    -self.base_speed * speed_factor + np.random.uniform(-0.5, 0.5)
                ])
                
                life_factor = 1.0 - spawn_y_ratio * 0.3
                life = (2.0 + np.random.uniform(0, 1.0)) * life_factor
                self.particles.append(FireParticle(x, y, size, self.fire_color, velocity, life, life, self.height))
        else:
            if hasattr(self, 'burst_counter'):
                self.burst_counter = 0.0
        
        # 根据onset强度计算目标粒子数量（仅用于参考，不强制限制）
        target_count = calculate_particle_count(
            onset_intensity,
            self.base_particle_count,
            self.max_particle_count,
            self.smoothing_factor
        )
        
        # 持续生成：降低速率
        if onset_intensity > 0.02:
            target_spawn_rate = 0.01 + 0.03 * onset_intensity
        else:
            target_spawn_rate = 0.01
        
        # 生成新粒子（使用恒定速率，不强制限制粒子数量）
        self.spawn_timer += dt
        while self.spawn_timer >= target_spawn_rate:
            self.spawn_timer = 0
            
            # 使用更合理的生成位置分布（底部密集，顶部稀疏）
            spawn_y_ratio = np.random.uniform(0, 1) ** 2  # 使用平方函数使底部更密集
            x = self.base_x + np.random.uniform(-self.fire_width / 2, self.fire_width / 2)
            y = self.base_y - spawn_y_ratio * self.fire_height
            
            # 根据高度调整粒子大小（底部大，顶部小）
            size_factor = 1.0 - spawn_y_ratio * 0.5
            size = (self.base_size + np.random.uniform(-2, 2)) * size_factor
            
            # 根据高度调整速度（底部慢，顶部快）
            speed_factor = 1.0 + spawn_y_ratio * 0.5
            velocity = np.array([
                np.random.uniform(-1, 1) * speed_factor,
                -self.base_speed * speed_factor + np.random.uniform(-0.5, 0.5)
            ])
            
            # 根据高度调整生命周期（底部长，顶部短）
            life_factor = 1.0 - spawn_y_ratio * 0.3
            life = (8.0 + np.random.uniform(0, 2.0)) * life_factor
            self.particles.append(FireParticle(x, y, size, self.fire_color, velocity, life, life, self.height))
        
        # 更新所有粒子（自然消亡）
        self.particles = [particle for particle in self.particles if particle.update(dt, audio_features)]

    def _render_effect(self) -> None:
        """渲染火焰特效"""
        for particle in self.particles:
            particle.render(self.surface)

    def get_base_params(self) -> Dict[str, Any]:
        """获取基础参数（用于与音频模块联动）"""
        return {
            "temporal_sensitivity": 1.0,
            "frequency_sensitivity": 1.0,
            "rhythm_sensitivity": 1.0,
            "dynamic_range": 1.0
        }

    def get_personalized_params(self) -> Dict[str, Any]:
        """获取个性化参数"""
        return {
            "base_particle_count": {
                "type": "int",
                "min": 50,
                "max": 400,
                "default": 50,
                "description": "基准火焰粒子数量"
            },
            "max_particle_count": {
                "type": "int",
                "min": 120,
                "max": 1000,
                "default": 120,
                "description": "最大火焰粒子数量"
            },
            "base_spawn_rate": {
                "type": "float",
                "min": 0.02,
                "max": 0.1,
                "default": 0.05,
                "description": "基准粒子生成速率"
            },
            "max_spawn_rate": {
                "type": "float",
                "min": 0.1,
                "max": 0.3,
                "default": 0.15,
                "description": "最大粒子生成速率"
            },
            "base_size": {
                "type": "float",
                "min": 3.0,
                "max": 15.0,
                "default": 6.0,
                "description": "粒子基础大小"
            },
            "base_speed": {
                "type": "float",
                "min": 1.0,
                "max": 8.0,
                "default": 3.0,
                "description": "粒子基础速度"
            },
            "fire_color": {
                "type": "color",
                "default": "#ff4500",
                "description": "火焰颜色"
            },
            "base_x": {
                "type": "int",
                "min": 0,
                "max": 1920,
                "default": 960,
                "description": "火焰中心X坐标"
            },
            "base_y": {
                "type": "int",
                "min": 0,
                "max": 1080,
                "default": 1030,
                "description": "火焰中心Y坐标"
            },
            "fire_width": {
                "type": "int",
                "min": 20,
                "max": 200,
                "default": 60,
                "description": "火焰宽度"
            },
            "fire_height": {
                "type": "int",
                "min": 50,
                "max": 300,
                "default": 100,
                "description": "火焰高度"
            },
            "smoothing_factor": {
                "type": "float",
                "min": 0.0,
                "max": 1.0,
                "default": 0.3,
                "description": "平滑因子（0-1），用于平滑节拍强度变化"
            }
        }