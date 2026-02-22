import pygame
import numpy as np
from typing import Dict, Any, List, Optional
import math
import random
from .effect_base import EffectBase
from .beat_utils import OnsetIntensityTracker


class GlowingSquare:
    """闪光的方块粒子类"""

    def __init__(self, x: float, y: float, size: float, color: pygame.Color, 
                 velocity: np.ndarray, life: float, screen_width: int, screen_height: int,
                 frequency_band: int = 0):
        self.x = x
        self.y = y
        self.size = size
        self.base_size = size
        self.color = color
        self.base_color = color
        self.velocity = velocity
        self.life = life
        self.max_life = life
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.pulse_phase = random.uniform(0, math.pi * 2)
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-20, 20)
        self.frequency_band = frequency_band
        self.glow_intensity = 1.0
        self.target_size = size
        self.target_glow = 1.0
        self.current_shake = np.array([0.0, 0.0])

    def update(self, dt: float, audio_features: Dict[str, Any]) -> bool:
        loudness = 0.0
        beat_strength = 0.0
        onset_intensity = 0.0
        
        if "temporal" in audio_features and "loudness" in audio_features["temporal"]:
            loudness = float(np.mean(audio_features["temporal"]["loudness"]))
        
        if "rhythm" in audio_features and "beat_strength" in audio_features["rhythm"]:
            beat_strength = float(np.mean(audio_features["rhythm"]["beat_strength"]))
        
        if "rhythm" in audio_features and "onset_envelope" in audio_features["rhythm"]:
            onset_env = audio_features["rhythm"]["onset_envelope"]
            if isinstance(onset_env, np.ndarray) and len(onset_env) > 0:
                onset_intensity = float(np.mean(onset_env[-5:]))
        
        size_mod = 1.0 + loudness * 0.8 + beat_strength * 0.8
        self.target_size = self.base_size * size_mod
        
        pulse_speed = 3.0 + onset_intensity * 12.0 + beat_strength * 10.0
        self.pulse_phase += dt * pulse_speed
        
        pulse_amplitude = 0.3 + beat_strength * 0.9 + onset_intensity * 0.6
        _ = math.sin(self.pulse_phase) * pulse_amplitude + 1.0
        
        shake_intensity = beat_strength * 4.0 + onset_intensity * 3.0
        target_shake = np.array([
            math.sin(self.pulse_phase * 2) * shake_intensity,
            math.cos(self.pulse_phase * 2) * shake_intensity
        ])
        
        self.current_shake = self.current_shake * 0.85 + target_shake * 0.15
        
        rotation_mod = 1.0 + beat_strength * 1.5
        self.rotation += self.rotation_speed * rotation_mod * dt * 30
        
        osc_scale = 0.3 + beat_strength * 0.9 + onset_intensity * 0.6
        
        self.size = self.size * 0.85 + self.target_size * (1.0 + osc_scale * 0.5) * 0.15
        
        tiny_offset = np.array([
            math.sin(self.pulse_phase * 2) * (0.5 + beat_strength * 1.0 + onset_intensity * 0.5),
            math.cos(self.pulse_phase * 2) * (0.5 + beat_strength * 1.0 + onset_intensity * 0.5)
        ])
        
        self.x += self.velocity[0] * dt * 3 + tiny_offset[0]
        self.y += self.velocity[1] * dt * 3 + tiny_offset[1]
        
        if self.x < 0 or self.x > self.screen_width:
            self.velocity[0] *= -1
        if self.y < 0 or self.y > self.screen_height:
            self.velocity[1] *= -1
        
        self.x = max(0, min(self.screen_width, self.x))
        self.y = max(0, min(self.screen_height, self.y))
        
        self.glow_intensity = 1.0 + loudness * 0.5 + beat_strength * 0.5
        
        self.life -= dt
        
        return self.life > 0

    def update_color(self, audio_features: Dict[str, Any], base_hue: float):
        beat_strength = 0.0
        
        if "rhythm" in audio_features and "beat_strength" in audio_features["rhythm"]:
            beat_strength = float(np.mean(audio_features["rhythm"]["beat_strength"]))
        
        hue_shift = beat_strength * 30
        new_hue = (base_hue + hue_shift) % 360
        
        saturation = 70 + int(beat_strength * 20)
        value = 90 - int(beat_strength * 10)
        
        self.color = pygame.Color(255, 255, 255)
        self.color.hsva = (new_hue, saturation, value, 100)

    def render(self, surface: pygame.Surface):
        alpha = int(200 * min(1.0, self.life / 3.0))
        
        current_size = self.size * self.glow_intensity
        
        square_size = int(current_size * 1.8)
        square_surface = pygame.Surface((square_size, square_size), pygame.SRCALPHA)
        
        center = square_size // 2
        rect = pygame.Rect(center - current_size // 2, center - current_size // 2, current_size, current_size)
        
        glow_color = (*self.color[:3], alpha // 3)
        pygame.draw.rect(square_surface, glow_color, rect)
        
        main_color = (*self.color[:3], alpha)
        pygame.draw.rect(square_surface, main_color, rect, 2)
        
        rotated_surface = pygame.transform.rotate(square_surface, self.rotation)
        rect = rotated_surface.get_rect(center=(int(self.x), int(self.y)))
        
        surface.blit(rotated_surface, rect)


class GlowingSquaresEffect(EffectBase):
    """闪光的方块特效"""

    def __init__(self):
        super().__init__("glowing_squares")
        self.squares: List[GlowingSquare] = []
        self.onset_tracker = OnsetIntensityTracker(smoothing_factor=0.15)
        self.hue_offset = 0.0

    def initialize(self, surface: pygame.Surface, config: Dict[str, Any]) -> None:
        super().initialize(surface, config)
        self.width, self.height = surface.get_size()
        
        particles_count = config.get("particles", {}).get("count", 1000)
        scale_factor = particles_count / 1000.0
        
        self.base_square_count = int(config.get("base_square_count", 30) * scale_factor)
        self.max_square_count = int(config.get("max_square_count", 80) * scale_factor)
        self.base_square_count = max(self.base_square_count, 20)
        self.max_square_count = max(self.max_square_count, 60)
        
        self.square_size = config.get("square_size", 25.0)
        self.square_speed = config.get("square_speed", 1.5)
        self.square_life = config.get("square_life", 8.0)
        
        self.bg_color = pygame.Color(config.get("background_color", "#0a0a1a"))
        
        self.squares = []
        self.hue_offset = 0.0
        
        for i in range(self.base_square_count):
            freq_band = i % 4
            self.spawn_square(0.0, freq_band)

    def spawn_square(self, intensity: float = 0.0, frequency_band: int = 0):
        spacing = max(self.width, self.height) / (self.base_square_count ** 0.5 + 1)
        
        grid_cols = int(self.width / spacing)
        grid_rows = int(self.height / spacing)
        
        col = random.randint(0, max(1, grid_cols - 1))
        row = random.randint(0, max(1, grid_rows - 1))
        
        offset_x = random.uniform(-spacing * 0.3, spacing * 0.3)
        offset_y = random.uniform(-spacing * 0.3, spacing * 0.3)
        
        x = col * spacing + spacing + offset_x
        y = row * spacing + spacing + offset_y
        
        x = max(self.square_size, min(self.width - self.square_size, x))
        y = max(self.square_size, min(self.height - self.square_size, y))
        
        size = self.square_size * (1.0 + intensity * 0.3) * random.uniform(0.8, 1.1)
        
        base_hue = (self.hue_offset + frequency_band * 60) % 360
        color = pygame.Color(255, 255, 255)
        color.hsva = (base_hue, 70, 90, 100)
        
        angle = random.uniform(0, math.pi * 2)
        speed = self.square_speed * random.uniform(0.3, 0.8)
        velocity = np.array([
            math.cos(angle) * speed,
            math.sin(angle) * speed
        ])
        
        life = self.square_life * random.uniform(0.8, 1.5)
        
        self.squares.append(GlowingSquare(
            x, y, size, color, velocity, life, self.width, self.height, frequency_band
        ))

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
        
        self.hue_offset += (loudness * 10 + beat_strength * 15) * dt
        self.hue_offset = self.hue_offset % 360
        
        threshold = 0.25
        
        if onset_intensity > threshold:
            spawn_count = int(1 + (onset_intensity - threshold) * 2)
        else:
            spawn_count = 0
        
        if len(self.squares) < self.base_square_count:
            spawn_count += 1
        
        for _ in range(spawn_count):
            if len(self.squares) < self.max_square_count:
                freq_band = random.randint(0, 3)
                self.spawn_square(onset_intensity, freq_band)
        
        for square in self.squares:
            base_hue = (self.hue_offset + square.frequency_band * 60) % 360
            square.update_color(audio_features, base_hue)
        
        self.squares = [square for square in self.squares 
                       if square.update(dt, audio_features)]

    def _render_effect(self) -> None:
        if self.surface is None:
            return
        
        self.surface.fill(self.bg_color)
        
        self.squares.sort(key=lambda s: s.life)
        
        for square in self.squares:
            square.render(self.surface)

    def get_base_params(self) -> Dict[str, Any]:
        return {
            "square_size": self.square_size,
            "base_square_count": self.base_square_count,
            "max_square_count": self.max_square_count,
            "square_speed": self.square_speed,
            "square_life": self.square_life,
            "temporal_sensitivity": 0.5,
            "frequency_sensitivity": 0.5,
            "rhythm_sensitivity": 0.5,
            "dynamic_range": 0.5
        }

    def get_personalized_params(self) -> Dict[str, Any]:
        return {}
