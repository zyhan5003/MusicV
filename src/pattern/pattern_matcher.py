from typing import Dict, Any, Optional, Callable
import numpy as np


class PatternMatcher:
    """模式匹配器，负责将音频参数映射到视觉参数"""

    def __init__(self):
        """初始化模式匹配器"""
        self.audio_categories: Dict[str, Dict[str, Any]] = {}
        self.visual_effects: Dict[str, Dict[str, Any]] = {}
        self.patterns: Dict[str, Dict[str, Any]] = {}
        self.mapping_rules: Dict[str, Callable] = {}

    def register_audio_category(self, category_name: str, category_config: Dict[str, Any]) -> None:
        """注册音频类别"""
        self.audio_categories[category_name] = category_config

    def register_visual_effect(self, effect_name: str, effect_config: Dict[str, Any]) -> None:
        """注册视觉特效"""
        self.visual_effects[effect_name] = effect_config

    def register_pattern(self, pattern_name: str, pattern_config: Dict[str, Any]) -> None:
        """注册模式"""
        self.patterns[pattern_name] = pattern_config

    def register_mapping_rule(self, rule_name: str, mapping_func: Callable) -> None:
        """注册映射规则"""
        self.mapping_rules[rule_name] = mapping_func

    def match_audio_to_visual(self, audio_category: str, audio_features: Dict[str, Any], 
                             visual_effect: str) -> Dict[str, Any]:
        """将音频特征映射到视觉参数"""
        # 获取音频类别配置
        audio_config = self.audio_categories.get(audio_category, {})
        
        # 获取视觉特效配置
        visual_config = self.visual_effects.get(visual_effect, {})
        
        # 获取基础参数
        base_params = audio_config.get("base_attributes", {})
        
        # 应用映射规则
        visual_params = self._apply_mapping_rules(
            audio_features,
            base_params,
            visual_config
        )
        
        return visual_params

    def _apply_mapping_rules(self, audio_features: Dict[str, Any], 
                            base_params: Dict[str, Any],
                            visual_config: Dict[str, Any]) -> Dict[str, Any]:
        """应用映射规则"""
        visual_params = visual_config.copy()
        
        # 时域敏感度映射
        if "temporal_sensitivity" in base_params:
            temporal_sens = base_params["temporal_sensitivity"]
            visual_params["temporal_sensitivity"] = temporal_sens
            
            # 根据时域敏感度调整振幅响应
            if "amplitude" in audio_features:
                amplitude = np.mean(audio_features["amplitude"])
                visual_params["amplitude_response"] = amplitude * temporal_sens
        
        # 频域敏感度映射
        if "frequency_sensitivity" in base_params:
            frequency_sens = base_params["frequency_sensitivity"]
            visual_params["frequency_sensitivity"] = frequency_sens
            
            # 根据频域敏感度调整频谱响应
            if "spectrum" in audio_features:
                spectrum = audio_features["spectrum"]
                spectrum_energy = np.mean(np.abs(spectrum))
                visual_params["spectrum_response"] = spectrum_energy * frequency_sens
        
        # 节奏敏感度映射
        if "rhythm_sensitivity" in base_params:
            rhythm_sens = base_params["rhythm_sensitivity"]
            visual_params["rhythm_sensitivity"] = rhythm_sens
            
            # 根据节奏敏感度调整节拍响应
            if "is_beat" in audio_features:
                is_beat = audio_features["is_beat"]
                visual_params["beat_response"] = rhythm_sens if is_beat else 0.5
        
        # 动态范围映射
        if "dynamic_range" in base_params:
            dynamic_range = base_params["dynamic_range"]
            visual_params["dynamic_range"] = dynamic_range
        
        return visual_params

    def get_pattern_config(self, pattern_name: str) -> Optional[Dict[str, Any]]:
        """获取模式配置"""
        return self.patterns.get(pattern_name)

    def create_pattern(self, pattern_name: str, audio_category: str, 
                     visual_effect: str, custom_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """创建模式"""
        pattern_config = {
            "audio_category": audio_category,
            "visual_effect": visual_effect,
            "custom_config": custom_config or {}
        }
        
        self.register_pattern(pattern_name, pattern_config)
        return pattern_config

    def apply_pattern(self, pattern_name: str, audio_features: Dict[str, Any]) -> Dict[str, Any]:
        """应用模式"""
        pattern_config = self.get_pattern_config(pattern_name)
        if not pattern_config:
            return {}
        
        audio_category = pattern_config["audio_category"]
        visual_effect = pattern_config["visual_effect"]
        custom_config = pattern_config["custom_config"]
        
        # 匹配音频到视觉
        visual_params = self.match_audio_to_visual(
            audio_category,
            audio_features,
            visual_effect
        )
        
        # 应用自定义配置
        visual_params.update(custom_config)
        
        return visual_params
