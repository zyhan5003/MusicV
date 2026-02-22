from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import pygame
from ..renderer import VisualComponent


class EffectBase(VisualComponent):
    """特效基类，所有特效都应该继承这个基类"""

    def __init__(self, name: str):
        """初始化特效"""
        self._name = name
        self.surface: Optional[pygame.Surface] = None
        self.config: Dict[str, Any] = {}

    @property
    def name(self) -> str:
        """组件名称"""
        return self._name

    def initialize(self, surface: pygame.Surface, config: Dict[str, Any]) -> None:
        """初始化特效"""
        self.surface = surface
        self.config = config

    def update(self, audio_features: Dict[str, Any], dt: float) -> None:
        """更新特效状态"""
        self._update_effect(audio_features)

    def render(self, surface: pygame.Surface) -> None:
        """渲染特效"""
        if self.surface:
            self._render_effect()

    @abstractmethod
    def _update_effect(self, audio_features: Dict[str, Any]) -> None:
        """更新特效状态（子类实现）"""
        pass

    @abstractmethod
    def _render_effect(self) -> None:
        """渲染特效（子类实现）"""
        pass

    @abstractmethod
    def get_base_params(self) -> Dict[str, Any]:
        """获取基础参数（用于与音频模块联动）"""
        return {
            "temporal_sensitivity": 1.0,
            "frequency_sensitivity": 1.0,
            "rhythm_sensitivity": 1.0,
            "dynamic_range": 1.0
        }

    @abstractmethod
    def get_personalized_params(self) -> Dict[str, Any]:
        """获取个性化参数"""
        return {}

    def set_config(self, config: Dict[str, Any]) -> None:
        """设置配置"""
        self.config.update(config)