from typing import Dict, Any
from .pattern_matcher import PatternMatcher


class PatternLibrary:
    """模式实例库，包含预定义的音频-视觉组合"""

    def __init__(self, pattern_matcher: PatternMatcher):
        """初始化模式实例库"""
        self.pattern_matcher = pattern_matcher
        self._register_default_patterns()

    def _register_default_patterns(self) -> None:
        """注册默认模式"""
        
        # 默认风格 + 波形图
        self.pattern_matcher.create_pattern(
            "default_waveform",
            "default",
            "waveform",
            {
                "color": "#FFFFFF",
                "line_width": 2,
                "smoothness": 0.8
            }
        )
        
        # 默认风格 + 频谱图
        self.pattern_matcher.create_pattern(
            "default_spectrum",
            "default",
            "spectrum",
            {
                "color": "#FFFFFF",
                "bar_width": 6,
                "intensity": 1.0
            }
        )
        
        # 默认风格 + 均衡器
        self.pattern_matcher.create_pattern(
            "default_equalizer",
            "default",
            "equalizer",
            {
                "color": "#FFFFFF",
                "bar_width": 6,
                "smoothness": 0.8
            }
        )
        
        # 默认风格 + 3D频谱立方体
        self.pattern_matcher.create_pattern(
            "default_spectrum_cube",
            "default",
            "spectrum_cube",
            {
                "color": "#FFFFFF",
                "cube_size": 15,
                "rotation_speed": 0.5
            }
        )
        
        # 默认风格 + 3D模型
        self.pattern_matcher.create_pattern(
            "default_3d_model",
            "default",
            "3d_model",
            {
                "color": "#FFFFFF",
                "model_scale": 1.0,
                "rotation_speed": 0.3
            }
        )
        
        # 默认风格 + 粒子系统
        self.pattern_matcher.create_pattern(
            "default_particles",
            "default",
            "particles",
            {
                "particle_count": 300,
                "min_size": 3,
                "max_size": 8,
                "color_palette": "default",
                "movement_pattern": "default"
            }
        )
        
        # 默认风格 + 节拍粒子
        self.pattern_matcher.create_pattern(
            "default_beat_particles",
            "default",
            "beat_particles",
            {
                "particle_count": 250,
                "min_size": 3,
                "max_size": 8,
                "color_palette": "default",
                "beat_sensitivity": 0.8
            }
        )
        
        # 默认风格 + 跳动粒子
        self.pattern_matcher.create_pattern(
            "default_jumping_particles",
            "default",
            "jumping_particles",
            {
                "particle_count": 250,
                "min_size": 3,
                "max_size": 8,
                "min_jump_height": 15,
                "max_jump_height": 80,
                "min_jump_speed": 0.06,
                "max_jump_speed": 0.15,
                "trail_length": 4,
                "color_palette": "default"
            }
        )
        
        # 默认风格 + 风格感知粒子
        self.pattern_matcher.create_pattern(
            "default_style_aware_particles",
            "default",
            "style_aware_particles",
            {
                "particle_count": 250,
                "min_size": 3,
                "max_size": 8,
                "color_palette": "default",
                "style_sensitivity": 0.8
            }
        )
        
        # 默认风格 + 综合可视化
        self.pattern_matcher.create_pattern(
            "default_comprehensive",
            "default",
            "comprehensive",
            {
                "show_waveform": True,
                "show_spectrum": True,
                "show_particles": True,
                "show_3d": False
            }
        )
        
        # 钢琴曲 + 波形图
        self.pattern_matcher.create_pattern(
            "piano_waveform",
            "piano",
            "waveform",
            {
                "color": "#FFD700",
                "line_width": 2,
                "smoothness": 0.8
            }
        )
        
        # 钢琴曲 + 粒子系统
        self.pattern_matcher.create_pattern(
            "piano_particles",
            "piano",
            "particles",
            {
                "particle_count": 300,
                "min_size": 2,
                "max_size": 6,
                "color_palette": "pastel",
                "movement_pattern": "smooth_flow"
            }
        )
        
        # 摇滚乐 + 频谱图
        self.pattern_matcher.create_pattern(
            "rock_spectrum",
            "rock",
            "spectrum",
            {
                "color": "#FF4500",
                "bar_width": 8,
                "intensity": 1.5
            }
        )
        
        # 摇滚乐 + 粒子系统
        self.pattern_matcher.create_pattern(
            "rock_particles",
            "rock",
            "particles",
            {
                "particle_count": 400,
                "min_size": 3,
                "max_size": 10,
                "color_palette": "vibrant",
                "movement_pattern": "intense_jump"
            }
        )
        
        # DJ音乐 + 频谱图
        self.pattern_matcher.create_pattern(
            "dj_spectrum",
            "dj",
            "spectrum",
            {
                "color": "#00FFFF",
                "bar_width": 6,
                "intensity": 1.8,
                "neon_glow": True
            }
        )
        
        # DJ音乐 + 粒子系统
        self.pattern_matcher.create_pattern(
            "dj_particles",
            "dj",
            "particles",
            {
                "particle_count": 350,
                "min_size": 2,
                "max_size": 8,
                "min_jump_height": 20,
                "max_jump_height": 120,
                "min_jump_speed": 0.08,
                "max_jump_speed": 0.18,
                "trail_length": 5,
                "color_palette": "neon_glow",
                "movement_pattern": "geometric_sync"
            }
        )
        
        # 轻音乐 + 波形图
        self.pattern_matcher.create_pattern(
            "light_waveform",
            "light",
            "waveform",
            {
                "color": "#87CEEB",
                "line_width": 2,
                "smoothness": 0.9
            }
        )
        
        # 轻音乐 + 频谱图
        self.pattern_matcher.create_pattern(
            "light_spectrum",
            "light",
            "spectrum",
            {
                "color": "#87CEEB",
                "bar_width": 4,
                "intensity": 0.7
            }
        )
        
        # 轻音乐 + 粒子系统
        self.pattern_matcher.create_pattern(
            "light_particles",
            "light",
            "particles",
            {
                "particle_count": 200,
                "min_size": 2,
                "max_size": 5,
                "color_palette": "soft_blue",
                "movement_pattern": "gentle_float"
            }
        )
        
        # 钢琴曲 + 均衡器
        self.pattern_matcher.create_pattern(
            "piano_equalizer",
            "piano",
            "equalizer",
            {
                "color": "#FFD700",
                "bar_width": 6,
                "smoothness": 0.9
            }
        )
        
        # 摇滚乐 + 均衡器
        self.pattern_matcher.create_pattern(
            "rock_equalizer",
            "rock",
            "equalizer",
            {
                "color": "#FF4500",
                "bar_width": 10,
                "smoothness": 0.5
            }
        )
        
        # DJ音乐 + 均衡器
        self.pattern_matcher.create_pattern(
            "dj_equalizer",
            "dj",
            "equalizer",
            {
                "color": "#00FFFF",
                "bar_width": 8,
                "smoothness": 0.7,
                "neon_glow": True
            }
        )
        
        # 轻音乐 + 均衡器
        self.pattern_matcher.create_pattern(
            "light_equalizer",
            "light",
            "equalizer",
            {
                "color": "#87CEEB",
                "bar_width": 4,
                "smoothness": 0.95
            }
        )
        
        # 钢琴曲 + 3D频谱立方体
        self.pattern_matcher.create_pattern(
            "piano_spectrum_cube",
            "piano",
            "spectrum_cube",
            {
                "color": "#FFD700",
                "cube_size": 15,
                "rotation_speed": 0.5
            }
        )
        
        # 摇滚乐 + 3D频谱立方体
        self.pattern_matcher.create_pattern(
            "rock_spectrum_cube",
            "rock",
            "spectrum_cube",
            {
                "color": "#FF4500",
                "cube_size": 20,
                "rotation_speed": 1.0
            }
        )
        
        # DJ音乐 + 3D频谱立方体
        self.pattern_matcher.create_pattern(
            "dj_spectrum_cube",
            "dj",
            "spectrum_cube",
            {
                "color": "#00FFFF",
                "cube_size": 18,
                "rotation_speed": 0.8,
                "neon_glow": True
            }
        )
        
        # 轻音乐 + 3D频谱立方体
        self.pattern_matcher.create_pattern(
            "light_spectrum_cube",
            "light",
            "spectrum_cube",
            {
                "color": "#87CEEB",
                "cube_size": 12,
                "rotation_speed": 0.3
            }
        )
        
        # 钢琴曲 + 3D模型
        self.pattern_matcher.create_pattern(
            "piano_3d_model",
            "piano",
            "3d_model",
            {
                "color": "#FFD700",
                "model_scale": 1.0,
                "rotation_speed": 0.3
            }
        )
        
        # 摇滚乐 + 3D模型
        self.pattern_matcher.create_pattern(
            "rock_3d_model",
            "rock",
            "3d_model",
            {
                "color": "#FF4500",
                "model_scale": 1.2,
                "rotation_speed": 0.8
            }
        )
        
        # DJ音乐 + 3D模型
        self.pattern_matcher.create_pattern(
            "dj_3d_model",
            "dj",
            "3d_model",
            {
                "color": "#00FFFF",
                "model_scale": 1.1,
                "rotation_speed": 0.6,
                "neon_glow": True
            }
        )
        
        # 轻音乐 + 3D模型
        self.pattern_matcher.create_pattern(
            "light_3d_model",
            "light",
            "3d_model",
            {
                "color": "#87CEEB",
                "model_scale": 0.9,
                "rotation_speed": 0.2
            }
        )
        
        # 钢琴曲 + 节拍粒子
        self.pattern_matcher.create_pattern(
            "piano_beat_particles",
            "piano",
            "beat_particles",
            {
                "particle_count": 250,
                "min_size": 3,
                "max_size": 8,
                "color_palette": "pastel",
                "beat_sensitivity": 0.6
            }
        )
        
        # 摇滚乐 + 节拍粒子
        self.pattern_matcher.create_pattern(
            "rock_beat_particles",
            "rock",
            "beat_particles",
            {
                "particle_count": 350,
                "min_size": 4,
                "max_size": 12,
                "color_palette": "vibrant",
                "beat_sensitivity": 1.2
            }
        )
        
        # DJ音乐 + 节拍粒子
        self.pattern_matcher.create_pattern(
            "dj_beat_particles",
            "dj",
            "beat_particles",
            {
                "particle_count": 300,
                "min_size": 3,
                "max_size": 10,
                "color_palette": "neon_glow",
                "beat_sensitivity": 1.0,
                "neon_glow": True
            }
        )
        
        # 轻音乐 + 节拍粒子
        self.pattern_matcher.create_pattern(
            "light_beat_particles",
            "light",
            "beat_particles",
            {
                "particle_count": 200,
                "min_size": 2,
                "max_size": 6,
                "color_palette": "soft_blue",
                "beat_sensitivity": 0.5
            }
        )
        
        # 钢琴曲 + 跳动粒子
        self.pattern_matcher.create_pattern(
            "piano_jumping_particles",
            "piano",
            "jumping_particles",
            {
                "particle_count": 250,
                "min_size": 3,
                "max_size": 8,
                "min_jump_height": 10,
                "max_jump_height": 60,
                "min_jump_speed": 0.05,
                "max_jump_speed": 0.12,
                "trail_length": 3,
                "color_palette": "pastel"
            }
        )
        
        # 摇滚乐 + 跳动粒子
        self.pattern_matcher.create_pattern(
            "rock_jumping_particles",
            "rock",
            "jumping_particles",
            {
                "particle_count": 350,
                "min_size": 4,
                "max_size": 12,
                "min_jump_height": 30,
                "max_jump_height": 150,
                "min_jump_speed": 0.08,
                "max_jump_speed": 0.20,
                "trail_length": 7,
                "color_palette": "vibrant"
            }
        )
        
        # DJ音乐 + 跳动粒子
        self.pattern_matcher.create_pattern(
            "dj_jumping_particles",
            "dj",
            "jumping_particles",
            {
                "particle_count": 300,
                "min_size": 3,
                "max_size": 10,
                "min_jump_height": 20,
                "max_jump_height": 120,
                "min_jump_speed": 0.06,
                "max_jump_speed": 0.18,
                "trail_length": 5,
                "color_palette": "neon_glow",
                "neon_glow": True
            }
        )
        
        # 轻音乐 + 跳动粒子
        self.pattern_matcher.create_pattern(
            "light_jumping_particles",
            "light",
            "jumping_particles",
            {
                "particle_count": 200,
                "min_size": 2,
                "max_size": 6,
                "min_jump_height": 5,
                "max_jump_height": 40,
                "min_jump_speed": 0.03,
                "max_jump_speed": 0.10,
                "trail_length": 2,
                "color_palette": "soft_blue"
            }
        )
        
        # 钢琴曲 + 风格感知粒子
        self.pattern_matcher.create_pattern(
            "piano_style_aware_particles",
            "piano",
            "style_aware_particles",
            {
                "particle_count": 250,
                "min_size": 3,
                "max_size": 8,
                "color_palette": "pastel",
                "style_sensitivity": 0.7
            }
        )
        
        # 摇滚乐 + 风格感知粒子
        self.pattern_matcher.create_pattern(
            "rock_style_aware_particles",
            "rock",
            "style_aware_particles",
            {
                "particle_count": 350,
                "min_size": 4,
                "max_size": 12,
                "color_palette": "vibrant",
                "style_sensitivity": 1.3
            }
        )
        
        # DJ音乐 + 风格感知粒子
        self.pattern_matcher.create_pattern(
            "dj_style_aware_particles",
            "dj",
            "style_aware_particles",
            {
                "particle_count": 300,
                "min_size": 3,
                "max_size": 10,
                "color_palette": "neon_glow",
                "style_sensitivity": 1.1,
                "neon_glow": True
            }
        )
        
        # 轻音乐 + 风格感知粒子
        self.pattern_matcher.create_pattern(
            "light_style_aware_particles",
            "light",
            "style_aware_particles",
            {
                "particle_count": 200,
                "min_size": 2,
                "max_size": 6,
                "color_palette": "soft_blue",
                "style_sensitivity": 0.6
            }
        )
        
        # 综合可视化（所有风格）
        for style in ["piano", "rock", "dj", "light"]:
            self.pattern_matcher.create_pattern(
                f"{style}_comprehensive",
                style,
                "comprehensive",
                {
                    "show_waveform": True,
                    "show_spectrum": True,
                    "show_particles": True,
                    "show_3d": False
                }
            )
        
        # 下雨特效（所有风格）
        for style in ["default", "piano", "rock", "dj", "light"]:
            self.pattern_matcher.create_pattern(
                f"{style}_rain",
                style,
                "rain",
                {
                    "rain_count": 100 if style == "default" else 150,
                    "rain_speed": 5.0 if style == "default" else 6.0,
                    "rain_length": 10.0 if style == "default" else 12.0,
                    "rain_color": "#3498db" if style == "default" else "#87CEEB" if style == "light" else "#00FFFF" if style == "dj" else "#FFD700" if style == "piano" else "#FF4500"
                }
            )
        
        # 火焰特效（所有风格）
        for style in ["default", "piano", "rock", "dj", "light"]:
            self.pattern_matcher.create_pattern(
                f"{style}_fire",
                style,
                "fire",
                {
                    "particle_count": 50 if style == "default" else 80,
                    "spawn_rate": 0.1 if style == "default" else 0.15,
                    "base_size": 5.0 if style == "default" else 6.0,
                    "base_speed": 2.0 if style == "default" else 3.0,
                    "fire_color": "#ff4500" if style == "default" else "#FFD700" if style == "piano" else "#FF0000" if style == "rock" else "#00FFFF" if style == "dj" else "#FFA500"
                }
            )
        
        # 下雪特效（所有风格）
        for style in ["default", "piano", "rock", "dj", "light"]:
            self.pattern_matcher.create_pattern(
                f"{style}_snow",
                style,
                "snow",
                {
                    "snow_count": 100 if style == "default" else 150,
                    "snow_speed": 2.0 if style == "default" else 2.5,
                    "snow_size": 3.0 if style == "default" else 4.0,
                    "snow_drift": 0.5 if style == "default" else 0.8,
                    "snow_color": "#FFFFFF" if style == "default" else "#E0FFFF" if style == "light" else "#87CEEB" if style == "dj" else "#FFD700" if style == "piano" else "#FF6347"
                }
            )

    def get_pattern_names(self) -> list:
        """获取所有模式名称"""
        return list(self.pattern_matcher.patterns.keys())

    def get_pattern_by_style(self, style: str, effect_type: str) -> str:
        """根据风格和特效类型获取模式名称"""
        return f"{style}_{effect_type}"

    def add_custom_pattern(self, pattern_name: str, audio_category: str,
                          visual_effect: str, custom_config: Dict[str, Any]) -> None:
        """添加自定义模式"""
        self.pattern_matcher.create_pattern(
            pattern_name,
            audio_category,
            visual_effect,
            custom_config
        )
