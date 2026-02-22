from typing import Dict, Any, List, Optional
import pygame
from .effect_base import EffectBase


class EffectLibrary:
    """特效库，管理所有视觉特效"""

    def __init__(self):
        """初始化特效库"""
        self.effects: Dict[str, EffectBase] = {}
        self.registered_effects: List[str] = []

    def register_effect(self, effect: EffectBase) -> None:
        """注册特效"""
        self.effects[effect.name] = effect
        self.registered_effects.append(effect.name)

    def unregister_effect(self, effect_name: str) -> None:
        """注销特效"""
        if effect_name in self.effects:
            del self.effects[effect_name]
            self.registered_effects.remove(effect_name)

    def get_effect(self, effect_name: str) -> Optional[EffectBase]:
        """获取特效"""
        return self.effects.get(effect_name)

    def list_effects(self) -> List[str]:
        """列出所有特效"""
        return self.registered_effects.copy()

    def initialize_all(self, surface: pygame.Surface, config: Dict[str, Any]) -> None:
        """初始化所有特效"""
        for effect in self.effects.values():
            effect.initialize(surface, config)

    def update_all(self, audio_features: Dict[str, Any]) -> None:
        """更新所有特效"""
        for effect in self.effects.values():
            effect.update(audio_features)

    def render_all(self) -> None:
        """渲染所有特效"""
        for effect in self.effects.values():
            effect.render()

    def get_effect_base_params(self, effect_name: str) -> Optional[Dict[str, Any]]:
        """获取特效的基础参数"""
        effect = self.get_effect(effect_name)
        if effect:
            return effect.get_base_params()
        return None

    def get_effect_personalized_params(self, effect_name: str) -> Optional[Dict[str, Any]]:
        """获取特效的个性化参数"""
        effect = self.get_effect(effect_name)
        if effect:
            return effect.get_personalized_params()
        return None
