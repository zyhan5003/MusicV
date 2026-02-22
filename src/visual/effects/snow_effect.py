import pygame
import numpy as np
from typing import Dict, Any, List
from .effect_base import EffectBase
from .beat_utils import OnsetIntensityTracker, calculate_particle_count


class Snowflake:
    """雪花类"""

    def __init__(self, x: float, y: float, size: float, speed: float, drift: float, color: pygame.Color, screen_height: int):
        """初始化雪花"""
        self.x = x
        self.y = y
        self.size = size
        self.base_size = size
        self.speed = speed
        self.base_speed = speed
        self.drift = drift
        self.base_drift = drift
        self.base_color = color
        self.current_color = color
        self.rotation = np.random.uniform(0, 360)
        self.rotation_speed = np.random.uniform(-2, 2)
        self.shake_offset = np.array([0.0, 0.0])
        self.trail_points = []
        self.max_trail_length = 8
        self.pulse_phase = np.random.uniform(0, 2 * np.pi)
        self.screen_height = screen_height
        # 计算雪花的生命周期，确保能够完整穿过屏幕
        # 大幅增加生命周期，让雪花能够存活更长时间
        self.max_life = (screen_height - y) / (speed * 60) * 5.0  # 增加400%的缓冲
        self.life = self.max_life

    def update(self, dt: float, width: int, height: int, audio_features: Dict[str, Any]) -> bool:
        """更新雪花"""
        # 提取多种音频特征用于控制不同维度
        loudness = 0.0
        beat_strength = 0.0
        spectral_centroid = 0.0
        zero_crossing_rate = 0.0
        spectral_bandwidth = 0.0
        
        # 响度 - 控制抖动强度
        if "temporal" in audio_features and "loudness" in audio_features["temporal"]:
            loudness = float(np.mean(audio_features["temporal"]["loudness"]))
        
        # 节拍强度 - 控制横向摆动
        if "rhythm" in audio_features and "beat_strength" in audio_features["rhythm"]:
            beat_strength = float(np.mean(audio_features["rhythm"]["beat_strength"]))
        
        # 频谱质心 - 控制颜色
        if "frequency" in audio_features and "spectral_centroid" in audio_features["frequency"]:
            spectral_centroid = float(np.mean(audio_features["frequency"]["spectral_centroid"]))
        
        # 过零率 - 控制旋转速度
        if "temporal" in audio_features and "zero_crossing_rate" in audio_features["temporal"]:
            zero_crossing_rate = float(np.mean(audio_features["temporal"]["zero_crossing_rate"]))
        
        # 频谱带宽 - 控制脉冲强度
        if "frequency" in audio_features and "spectral_bandwidth" in audio_features["frequency"]:
            spectral_bandwidth = float(np.mean(audio_features["frequency"]["spectral_bandwidth"]))
        
        # 【维度3】响度控制抖动强度（增强幅度）
        shake_intensity = loudness * 10.0
        
        # 【维度4】节拍强度控制横向摆动（增强幅度）
        tremor_intensity = beat_strength * 8.0
        
        # 【维度5】过零率控制旋转速度
        rotation_speed_mod = 1.0 + zero_crossing_rate * 5.0
        
        # 应用抖动
        self.shake_offset = np.array([
            np.random.uniform(-shake_intensity, shake_intensity),
            np.random.uniform(-shake_intensity, shake_intensity)
        ])
        
        # 更新位置（加入摆动效果）
        self.y += self.speed * dt * 60
        self.x += np.sin(self.rotation * np.pi / 180) * self.drift * dt * 60
        self.x += np.random.uniform(-tremor_intensity, tremor_intensity)
        
        # 更新旋转（加入过零率影响）
        self.rotation += self.rotation_speed * rotation_speed_mod * dt * 60
        
        # 更新脉冲相位
        self.pulse_phase += dt * 10
        
        # 【维度6】响度+频谱带宽控制脉冲大小
        pulse_factor = 1.0 + np.sin(self.pulse_phase) * 0.3 * loudness * (1 + spectral_bandwidth / 2000)
        self.size = self.base_size * pulse_factor
        
        # 【维度7】频谱质心控制颜色
        hue_shift = (spectral_centroid / 5000.0) * 30
        h, s, v, a = self.base_color.hsva
        h = (h + hue_shift) % 360
        self.current_color.hsva = (h, s, v, a)
        
        # 更新轨迹
        self.trail_points.append((self.x, self.y))
        if len(self.trail_points) > self.max_trail_length:
            self.trail_points.pop(0)
        
        # 减少生命值
        self.life -= dt
        
        # 性能优化：雪花超出屏幕底部立即消亡
        if self.y > self.screen_height + self.size:
            return False
        
        return self.life > 0

    def render(self, surface: pygame.Surface) -> None:
        """渲染雪花"""
        # 渲染轨迹
        if len(self.trail_points) > 1:
            for i in range(len(self.trail_points) - 1):
                alpha = int(255 * (i / len(self.trail_points)) * 0.2)
                trail_color = pygame.Color(
                    self.current_color.r,
                    self.current_color.g,
                    self.current_color.b,
                    alpha
                )
                start_pos = (int(self.trail_points[i][0]), int(self.trail_points[i][1]))
                end_pos = (int(self.trail_points[i + 1][0]), int(self.trail_points[i + 1][1]))
                pygame.draw.line(surface, trail_color, start_pos, end_pos, 1)
        
        # 渲染雪花主体
        center_x = int(self.x + self.shake_offset[0])
        center_y = int(self.y + self.shake_offset[1])
        radius = int(self.size)
        
        # 绘制六角雪花
        for i in range(6):
            angle = self.rotation + i * 60
            end_x = center_x + int(radius * np.cos(angle * np.pi / 180))
            end_y = center_y + int(radius * np.sin(angle * np.pi / 180))
            pygame.draw.line(surface, self.current_color, (center_x, center_y), (end_x, end_y), 1)
            
            # 绘制分支
            mid_x = (center_x + end_x) // 2
            mid_y = (center_y + end_y) // 2
            branch_angle = angle + 30
            branch_end_x = mid_x + int(radius * 0.3 * np.cos(branch_angle * np.pi / 180))
            branch_end_y = mid_y + int(radius * 0.3 * np.sin(branch_angle * np.pi / 180))
            pygame.draw.line(surface, self.current_color, (mid_x, mid_y), (branch_end_x, branch_end_y), 1)


class SnowEffect(EffectBase):
    """下雪特效"""

    def __init__(self):
        """初始化下雪特效"""
        super().__init__("snow")

    def initialize(self, surface: pygame.Surface, config: Dict[str, Any]) -> None:
        """初始化下雪特效"""
        super().initialize(surface, config)
        self.width, self.height = surface.get_size()
        
        # 从配置中获取粒子数量（与GUI控件联动）
        particles_count = config.get("particles", {}).get("count", 1000)
        
        # 根据GUI粒子数量计算雪花数量（按比例缩放）
        # GUI范围100-5000，映射到雪花数量
        scale_factor = particles_count / 1000.0
        self.base_snow_count = int(config.get("base_snow_count", 80) * scale_factor)
        self.max_snow_count = int(config.get("max_snow_count", 400) * scale_factor)
        
        # 确保最小值
        self.base_snow_count = max(self.base_snow_count, 80)
        self.max_snow_count = max(self.max_snow_count, 400)
        
        self.snow_speed = config.get("snow_speed", 2.0)
        self.snow_size = config.get("snow_size", 10.0)  # 进一步增大雪花尺寸
        self.snow_drift = config.get("snow_drift", 0.5)
        self.snow_color = pygame.Color(config.get("snow_color", "#FFFFFF"))
        self.smoothing_factor = config.get("smoothing_factor", 0.3)
        
        # 节拍变化检测
        self.last_onset_intensity = 0.0
        
        # onset强度跟踪器
        self.onset_tracker = OnsetIntensityTracker(smoothing_factor=0.1)  # 使用onset强度，响应更灵敏
        
        # 创建雪花（初始化时不创建粒子，避免突兀）
        self.snowflakes: List[Snowflake] = []

    def _update_effect(self, audio_features: Dict[str, Any]) -> None:
        """更新下雪特效"""
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
        
        # 2. 响度 - 控制雪花速度和下落速度
        if "temporal" in audio_features and "loudness" in audio_features["temporal"]:
            loudness = float(np.mean(audio_features["temporal"]["loudness"]))
        
        # 3. 节拍强度 - 控制横向摆动
        if "rhythm" in audio_features and "beat_strength" in audio_features["rhythm"]:
            beat_strength = float(np.mean(audio_features["rhythm"]["beat_strength"]))
        
        # 4. 频谱质心 - 控制颜色
        if "frequency" in audio_features and "spectral_centroid" in audio_features["frequency"]:
            spectral_centroid = float(np.mean(audio_features["frequency"]["spectral_centroid"]))
        
        # 5. 过零率 - 控制旋转速度
        if "temporal" in audio_features and "zero_crossing_rate" in audio_features["temporal"]:
            zero_crossing_rate = float(np.mean(audio_features["temporal"]["zero_crossing_rate"]))
        
        # 6. 频谱带宽 - 控制粒子大小
        if "frequency" in audio_features and "spectral_bandwidth" in audio_features["frequency"]:
            spectral_bandwidth = float(np.mean(audio_features["frequency"]["spectral_bandwidth"]))
        
        # 阈值：降低以确保有粒子产生
        threshold = 0.08
        
        # 【维度1】onset强度控制粒子生成数量
        if onset_intensity > threshold:
            burst_rate = (onset_intensity - threshold) * 6
            
            if not hasattr(self, 'burst_counter'):
                self.burst_counter = 0.0
            
            self.burst_counter += burst_rate
            
            while self.burst_counter >= 1.0:
                self.burst_counter -= 1.0
                x = np.random.uniform(0, self.width)
                y = np.random.uniform(-50, 0)
                
                # 【维度2】响度控制雪花大小
                size_mod = 1.0 + loudness * 1.0
                size = (self.snow_size + np.random.uniform(-1, 1)) * size_mod
                
                self.snowflakes.append(Snowflake(x, y, size, self.snow_speed, self.snow_drift, self.snow_color, self.height))
        else:
            if hasattr(self, 'burst_counter'):
                self.burst_counter = 0.0
        
        # 目标数量计算
        target_count = calculate_particle_count(
            onset_intensity,
            self.base_snow_count,
            self.max_snow_count,
            self.smoothing_factor
        )
        
        # 持续生成：降低速率
        if onset_intensity > 0.02:
            spawn_rate = 0.008 + 0.02 * onset_intensity
        else:
            spawn_rate = 0.008
        
        if not hasattr(self, 'spawn_counter'):
            self.spawn_counter = 0.0
        
        self.spawn_counter += spawn_rate
        
        while self.spawn_counter >= 1.0 and len(self.snowflakes) < target_count:
            self.spawn_counter -= 1.0
            x = np.random.uniform(0, self.width)
            y = np.random.uniform(-50, 0)
            size = self.snow_size + np.random.uniform(-1, 1)
            speed = self.snow_speed + np.random.uniform(-0.5, 0.5)
            drift = self.snow_drift + np.random.uniform(-0.2, 0.2)
            self.snowflakes.append(Snowflake(x, y, size, speed, drift, self.snow_color, self.height))
        
        # 更新所有雪花，传入多种音频特征
        self.snowflakes = [flake for flake in self.snowflakes 
                          if flake.update(dt, self.width, self.height, audio_features)]

    def _render_effect(self) -> None:
        """渲染下雪特效"""
        for flake in self.snowflakes:
            flake.render(self.surface)

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
            "base_snow_count": {
                "type": "int",
                "min": 5,
                "max": 50,
                "default": 5,
                "description": "基准雪花数量"
            },
            "max_snow_count": {
                "type": "int",
                "min": 15,
                "max": 150,
                "default": 15,
                "description": "最大雪花数量"
            },
            "snow_speed": {
                "type": "float",
                "min": 0.5,
                "max": 10.0,
                "default": 2.0,
                "description": "雪花下落速度"
            },
            "snow_size": {
                "type": "float",
                "min": 5.0,
                "max": 20.0,
                "default": 10.0,
                "description": "雪花大小"
            },
            "snow_drift": {
                "type": "float",
                "min": 0.0,
                "max": 2.0,
                "default": 0.5,
                "description": "雪花飘移速度"
            },
            "snow_color": {
                "type": "color",
                "default": "#FFFFFF",
                "description": "雪花颜色"
            },
            "smoothing_factor": {
                "type": "float",
                "min": 0.0,
                "max": 1.0,
                "default": 0.3,
                "description": "平滑因子（0-1），用于平滑节拍强度变化"
            }
        }