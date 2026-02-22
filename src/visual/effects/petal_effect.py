import pygame
import numpy as np
from typing import Dict, Any, List, Optional
import math
import random
from .effect_base import EffectBase
from .beat_utils import OnsetIntensityTracker


class Petal:
    """花瓣粒子类"""

    def __init__(self, x: float, y: float, size: float, color: pygame.Color, 
                 velocity: np.ndarray, rotation: float, rotation_speed: float,
                 screen_height: int):
        self.x = x
        self.y = y
        self.size = size
        self.base_size = size
        self.color = color
        self.base_color = color
        self.velocity = velocity
        self.rotation = rotation
        self.rotation_speed = rotation_speed
        self.screen_height = screen_height
        self.life = 8.0
        self.max_life = 8.0
        self.shake_offset = np.array([0.0, 0.0])
        
    def update(self, dt: float, audio_features: Dict[str, Any]) -> bool:
        loudness = 0.0
        beat_strength = 0.0
        
        if "temporal" in audio_features and "loudness" in audio_features["temporal"]:
            loudness = float(np.mean(audio_features["temporal"]["loudness"]))
        
        if "rhythm" in audio_features and "beat_strength" in audio_features["rhythm"]:
            beat_strength = float(np.mean(audio_features["rhythm"]["beat_strength"]))
        
        shake_intensity = loudness * 15.0 + beat_strength * 12.0
        self.shake_offset = np.array([
            random.uniform(-shake_intensity, shake_intensity),
            random.uniform(-shake_intensity, shake_intensity)
        ])
        
        speed_mod = 1.0 + beat_strength * 2.0
        
        self.x += (self.velocity[0] + self.shake_offset[0]) * dt * 60 * speed_mod
        self.y += (self.velocity[1] + self.shake_offset[1]) * dt * 60 * speed_mod
        
        self.rotation += (self.rotation_speed + beat_strength * 120) * dt * 60
        
        self.life -= dt
        
        if self.y > self.screen_height + self.size * 2:
            return False
        
        return self.life > 0

    def render(self, surface: pygame.Surface):
        alpha = int(255 * min(1.0, self.life / 2.0))
        
        petal_surface = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
        
        color_with_alpha = (*self.color[:3], alpha)
        pygame.draw.ellipse(petal_surface, self.color, 
                           (0, 0, self.size * 2, self.size))
        
        rotated_surface = pygame.transform.rotate(petal_surface, self.rotation)
        rect = rotated_surface.get_rect(center=(int(self.x), int(self.y)))
        
        surface.blit(rotated_surface, rect)


class PetalEffect(EffectBase):
    """花瓣特效"""

    def __init__(self):
        super().__init__("petal")
        self.petals: List[Petal] = []
        self.onset_tracker = OnsetIntensityTracker(smoothing_factor=0.1)
        self.spawn_timer = 0.0

    def initialize(self, surface: pygame.Surface, config: Dict[str, Any]) -> None:
        super().initialize(surface, config)
        self.width, self.height = surface.get_size()
        
        particles_count = config.get("particles", {}).get("count", 1000)
        scale_factor = particles_count / 1000.0
        
        self.base_petal_count = int(config.get("base_petal_count", 80) * scale_factor)
        self.max_petal_count = int(config.get("max_petal_count", 400) * scale_factor)
        self.base_petal_count = max(self.base_petal_count, 80)
        self.max_petal_count = max(self.max_petal_count, 400)
        
        self.petal_size = config.get("petal_size", 8.0)
        self.petal_speed = config.get("petal_speed", 1.5)
        self.petal_color = pygame.Color(config.get("petal_color", "#FF69B4"))
        self.spawn_rate = config.get("spawn_rate", 0.03)
        
        self.bg_color = pygame.Color(config.get("background_color", "#1a1a2e"))
        
        self.petals = []
        self.spawn_timer = 0.0

    def _update_effect(self, audio_features: Dict[str, Any]) -> None:
        dt = 0.016
        
        onset_intensity = 0.0
        loudness = 0.0
        beat_strength = 0.0
        
        onset_intensity = self.onset_tracker.update(audio_features)
        
        if "temporal" in audio_features and "loudness" in audio_features["temporal"]:
            loudness = float(np.mean(audio_features["temporal"]["loudness"]))
        
        if "rhythm" in audio_features and "beat_strength" in audio_features["rhythm"]:
            beat_strength = float(np.mean(audio_features["rhythm"]["beat_strength"]))
        
        threshold = 0.15
        
        if onset_intensity > threshold:
            spawn_count = int(1 + (onset_intensity - threshold) * 5)
        else:
            spawn_count = 0
        
        spawn_rate = self.spawn_rate * (1.0 + (onset_intensity + beat_strength) * 3.0)
        
        self.spawn_timer += dt
        
        if self.spawn_timer >= spawn_rate or spawn_count > 0:
            self.spawn_timer = 0.0
            
            total_spawn = spawn_count if spawn_count > 0 else 1
            for _ in range(total_spawn):
                x = random.uniform(0, self.width)
                y = random.uniform(-50, 0)
                
                size = self.petal_size * random.uniform(0.8, 1.2)
                
                color_brightness = 1.0 + loudness * 0.5
                color = pygame.Color(
                    min(255, int(self.petal_color.r * color_brightness)),
                    min(255, int(self.petal_color.g * color_brightness)),
                    min(255, int(self.petal_color.b * color_brightness))
                )
                
                velocity = np.array([
                    random.uniform(-1, 1),
                    self.petal_speed + random.uniform(-0.5, 0.5)
                ])
                
                rotation = random.uniform(0, 360)
                rotation_speed = random.uniform(-60, 60)
                
                self.petals.append(Petal(
                    x, y, size, color, velocity, rotation, rotation_speed, self.height
                ))
        
        self.petals = [petal for petal in self.petals 
                      if petal.update(dt, audio_features)]

    def _render_effect(self) -> None:
        if self.surface is None:
            return
        
        self.surface.fill(self.bg_color)
        
        for petal in self.petals:
            petal.render(self.surface)

    def get_base_params(self) -> Dict[str, Any]:
        return {
            "petal_size": self.petal_size,
            "petal_speed": self.petal_speed,
            "petal_color": "#FF69B4",
            "spawn_rate": self.spawn_rate,
            "base_petal_count": self.base_petal_count,
            "max_petal_count": self.max_petal_count,
            "temporal_sensitivity": 1.0,
            "frequency_sensitivity": 0.5,
            "rhythm_sensitivity": 1.0,
            "dynamic_range": 1.0
        }

    def get_personalized_params(self) -> Dict[str, Any]:
        return {}
