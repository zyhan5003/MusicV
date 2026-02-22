import pygame
import numpy as np
from typing import Dict, Any, List
from .effect_base import EffectBase
from .beat_utils import OnsetIntensityTracker, calculate_particle_count


class RainDrop:
    """雨滴类"""

    def __init__(self, x: float, y: float, speed: float, length: float, color: pygame.Color, screen_height: int):
        """初始化雨滴"""
        self.x = x
        self.y = y
        self.speed = speed
        self.length = length
        self.base_color = color
        self.current_color = color
        self.shake_offset = np.array([0.0, 0.0])
        self.trail_points = []
        self.max_trail_length = 8
        self.screen_height = screen_height
        # 计算雨滴的生命周期，确保能够完整穿过屏幕
        # 大幅增加生命周期，让雨滴能够存活更长时间
        self.max_life = (screen_height - y) / (speed * 60) * 5.0  # 增加400%的缓冲
        self.life = self.max_life

    def update(self, dt: float, height: int, audio_features: Dict[str, Any]) -> bool:
        """更新雨滴"""
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
        
        # 过零率 - 控制水平风力
        if "temporal" in audio_features and "zero_crossing_rate" in audio_features["temporal"]:
            zero_crossing_rate = float(np.mean(audio_features["temporal"]["zero_crossing_rate"]))
        
        # 频谱带宽 - 控制粒子大小
        if "frequency" in audio_features and "spectral_bandwidth" in audio_features["frequency"]:
            spectral_bandwidth = float(np.mean(audio_features["frequency"]["spectral_bandwidth"]))
        
        # 【维度3】响度控制抖动强度（增强幅度）
        shake_intensity = loudness * 8.0
        
        # 【维度4】节拍强度控制轨迹震颤（增强幅度）
        tremor_intensity = beat_strength * 6.0
        
        # 【维度5】过零率控制水平风力
        wind_intensity = (zero_crossing_rate - 0.05) * 10  # 归一化过零率
        wind_intensity = max(0, min(wind_intensity, 3.0))  # 限制范围
        
        # 应用抖动
        self.shake_offset = np.array([
            np.random.uniform(-shake_intensity, shake_intensity),
            np.random.uniform(-shake_intensity, shake_intensity)
        ])
        
        # 更新位置（加入风力影响）
        self.y += self.speed * dt * 60
        self.x += np.random.uniform(-tremor_intensity, tremor_intensity) + wind_intensity * np.sin(self.y * 0.01)
        
        # 更新轨迹
        self.trail_points.append((self.x, self.y))
        if len(self.trail_points) > self.max_trail_length:
            self.trail_points.pop(0)
        
        # 【维度6】频谱质心控制颜色
        brightness_factor = 0.5 + (spectral_centroid / 5000.0) * 0.5
        r = min(255, int(self.base_color.r * brightness_factor))
        g = min(255, int(self.base_color.g * brightness_factor))
        b = min(255, int(self.base_color.b * brightness_factor))
        self.current_color = pygame.Color(r, g, b)
        
        # 【维度7】频谱带宽微调颜色
        bandwidth_factor = 0.8 + (spectral_bandwidth / 2000.0) * 0.4
        self.current_color = pygame.Color(
            min(255, int(self.current_color.r * bandwidth_factor)),
            min(255, int(self.current_color.g * bandwidth_factor)),
            min(255, int(self.current_color.b * bandwidth_factor))
        )
        
        # 减少生命值
        self.life -= dt
        
        # 性能优化：雨滴超出屏幕底部立即消亡
        if self.y > self.screen_height + self.length:
            return False
        
        return self.life > 0

    def render(self, surface: pygame.Surface) -> None:
        """渲染雨滴"""
        # 渲染轨迹
        if len(self.trail_points) > 1:
            for i in range(len(self.trail_points) - 1):
                alpha = int(255 * (i / len(self.trail_points)) * 0.3)
                trail_color = pygame.Color(
                    self.current_color.r,
                    self.current_color.g,
                    self.current_color.b,
                    alpha
                )
                start_pos = (int(self.trail_points[i][0]), int(self.trail_points[i][1]))
                end_pos = (int(self.trail_points[i + 1][0]), int(self.trail_points[i + 1][1]))
                pygame.draw.line(surface, trail_color, start_pos, end_pos, 2)
        
        # 渲染雨滴主体（使用更大的宽度和长度）
        start_pos = (int(self.x + self.shake_offset[0]), int(self.y + self.shake_offset[1]))
        end_pos = (int(self.x + self.shake_offset[0]), int(self.y + self.length + self.shake_offset[1]))
        pygame.draw.line(surface, self.current_color, start_pos, end_pos, 6)  # 进一步增加线宽


class RainEffect(EffectBase):
    """下雨特效"""

    def __init__(self):
        """初始化下雨特效"""
        super().__init__("rain")

    def initialize(self, surface: pygame.Surface, config: Dict[str, Any]) -> None:
        """初始化下雨特效"""
        super().initialize(surface, config)
        self.width, self.height = surface.get_size()
        
        # 从配置中获取粒子数量（与GUI控件联动）
        particles_count = config.get("particles", {}).get("count", 1000)
        
        # 根据GUI粒子数量计算雨滴数量（按比例缩放）
        # GUI范围100-5000，映射到雨滴数量
        scale_factor = particles_count / 1000.0
        self.base_rain_count = int(config.get("base_rain_count", 120) * scale_factor)
        self.max_rain_count = int(config.get("max_rain_count", 600) * scale_factor)
        
        # 确保最小值
        self.base_rain_count = max(self.base_rain_count, 120)
        self.max_rain_count = max(self.max_rain_count, 600)
        
        self.rain_speed = config.get("rain_speed", 5.0)
        self.rain_length = config.get("rain_length", 30.0)  # 进一步增大雨滴长度
        self.rain_width = config.get("rain_width", 3.0)  # 新增雨滴宽度
        self.rain_color = pygame.Color(config.get("rain_color", "#3498db"))
        self.smoothing_factor = config.get("smoothing_factor", 0.3)
        
        # 节拍变化检测
        self.last_onset_intensity = 0.0
        
        # onset强度跟踪器
        self.onset_tracker = OnsetIntensityTracker(smoothing_factor=0.1)  # 使用onset强度，响应更灵敏
        
        # 创建雨滴（初始化时不创建粒子，避免突兀）
        self.rain_drops: List[RainDrop] = []

    def _update_effect(self, audio_features: Dict[str, Any]) -> None:
        """更新下雨特效"""
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
        
        # 2. 响度 - 控制雨滴速度和长度
        if "temporal" in audio_features and "loudness" in audio_features["temporal"]:
            loudness = float(np.mean(audio_features["temporal"]["loudness"]))
        
        # 3. 节拍强度 - 控制轨迹震颤
        if "rhythm" in audio_features and "beat_strength" in audio_features["rhythm"]:
            beat_strength = float(np.mean(audio_features["rhythm"]["beat_strength"]))
        
        # 4. 频谱质心 - 控制颜色变化
        if "frequency" in audio_features and "spectral_centroid" in audio_features["frequency"]:
            spectral_centroid = float(np.mean(audio_features["frequency"]["spectral_centroid"]))
        
        # 5. 过零率 - 控制风力效果
        if "temporal" in audio_features and "zero_crossing_rate" in audio_features["temporal"]:
            zero_crossing_rate = float(np.mean(audio_features["temporal"]["zero_crossing_rate"]))
        
        # 6. 频谱带宽 - 控制粒子大小变化
        if "frequency" in audio_features and "spectral_bandwidth" in audio_features["frequency"]:
            spectral_bandwidth = float(np.mean(audio_features["frequency"]["spectral_bandwidth"]))
        
        # 阈值：降低以确保有粒子产生
        threshold = 0.08
        
        # 【维度1】onset强度控制粒子生成数量
        if onset_intensity > threshold:
            burst_rate = (onset_intensity - threshold) * 8
            
            if not hasattr(self, 'burst_counter'):
                self.burst_counter = 0.0
            
            self.burst_counter += burst_rate
            
            while self.burst_counter >= 1.0:
                self.burst_counter -= 1.0
                x = np.random.uniform(0, self.width)
                y = np.random.uniform(-50, 0)
                
                # 【维度2】响度控制雨滴速度和长度
                speed_mod = 1.0 + loudness * 1.5  # 响度越大，速度越快
                length_mod = 1.0 + loudness * 0.8  # 响度越大，雨滴越长
                
                speed = (self.rain_speed + np.random.uniform(-1, 1)) * speed_mod
                length = (self.rain_length + np.random.uniform(-2, 2)) * length_mod
                
                self.rain_drops.append(RainDrop(x, y, speed, length, self.rain_color, self.height))
        else:
            if hasattr(self, 'burst_counter'):
                self.burst_counter = 0.0
        
        # 目标数量计算
        target_count = calculate_particle_count(
            onset_intensity, 
            self.base_rain_count, 
            self.max_rain_count,
            self.smoothing_factor
        )
        
        # 持续生成：降低速率
        if onset_intensity > 0.02:
            spawn_rate = 0.008 + 0.03 * onset_intensity
        else:
            spawn_rate = 0.008
        
        if not hasattr(self, 'spawn_counter'):
            self.spawn_counter = 0.0
        
        self.spawn_counter += spawn_rate
        
        while self.spawn_counter >= 1.0 and len(self.rain_drops) < target_count:
            self.spawn_counter -= 1.0
            x = np.random.uniform(0, self.width)
            y = np.random.uniform(-50, 0)
            speed = self.rain_speed + np.random.uniform(-1, 1)
            length = self.rain_length + np.random.uniform(-2, 2)
            self.rain_drops.append(RainDrop(x, y, speed, length, self.rain_color, self.height))
        
        # 更新所有雨滴，传入多种音频特征
        self.rain_drops = [drop for drop in self.rain_drops 
                         if drop.update(dt, self.height, audio_features)]

    def _render_effect(self) -> None:
        """渲染下雨特效"""
        for drop in self.rain_drops:
            drop.render(self.surface)

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
            "base_rain_count": {
                "type": "int",
                "min": 10,
                "max": 100,
                "default": 10,
                "description": "基准雨滴数量"
            },
            "max_rain_count": {
                "type": "int",
                "min": 25,
                "max": 250,
                "default": 25,
                "description": "最大雨滴数量"
            },
            "rain_speed": {
                "type": "float",
                "min": 1.0,
                "max": 20.0,
                "default": 5.0,
                "description": "雨滴下落速度"
            },
            "rain_length": {
                "type": "float",
                "min": 10.0,
                "max": 50.0,
                "default": 30.0,
                "description": "雨滴长度"
            },
            "rain_color": {
                "type": "color",
                "default": "#3498db",
                "description": "雨滴颜色"
            },
            "smoothing_factor": {
                "type": "float",
                "min": 0.0,
                "max": 1.0,
                "default": 0.3,
                "description": "平滑因子（0-1），用于平滑节拍强度变化"
            }
        }