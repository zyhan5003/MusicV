from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import numpy as np
import pygame
from dataclasses import dataclass


@dataclass
class VisualConfig:
    """视觉配置"""
    width: int = 1920
    height: int = 1080
    fps: int = 30
    background_color: str = "#1a1a1a"


class VisualComponent(ABC):
    """视觉组件基类"""

    @abstractmethod
    def initialize(self, surface: pygame.Surface, config: Dict[str, Any]) -> None:
        """初始化组件"""
        pass

    @abstractmethod
    def update(self, audio_features: Dict[str, Any], dt: float) -> None:
        """更新组件"""
        pass

    @abstractmethod
    def render(self, surface: pygame.Surface) -> None:
        """渲染组件"""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """组件名称"""
        pass

    def update_pattern_params(self, params: Dict[str, Any]) -> None:
        """更新模式参数（可选实现）"""
        pass


class VisualRenderer:
    """视觉渲染器"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化视觉渲染器"""
        self.config = config or {}
        self.visual_config = VisualConfig(
            width=self.config.get("width", 640),
            height=self.config.get("height", 480),
            fps=self.config.get("fps", 30),
            background_color=self.config.get("background_color", "#1a1a1a")
        )
        self.components: Dict[str, VisualComponent] = {}
        self.active_components: List[str] = []
        self.surface: Optional[pygame.Surface] = None
        self.clock = pygame.time.Clock()
        self.running = False
        self.is_fullscreen = False
        # 标记pygame是否已初始化
        self.pygame_initialized = False
        # 标记是否需要强制重新初始化
        self.force_reinit = False
        # 窗口关闭回调
        self.on_close_callback = None

    def initialize(self) -> None:
        """初始化渲染器"""
        # 如果pygame已经初始化，不需要重新初始化
        if not pygame.get_init() or self.force_reinit:
            pygame.init()
            self.pygame_initialized = True
            self.force_reinit = False
        
        # 设置显示模式（无标题栏窗口）
        try:
            # 创建无标题栏窗口
            self.surface = pygame.display.set_mode(
                (self.visual_config.width, self.visual_config.height),
                pygame.NOFRAME
            )
            pygame.display.set_caption("MusicV Visualizer")
            
            # 强制刷新显示，确保窗口可见
            pygame.display.flip()
            
            # 处理所有待处理的事件
            pygame.event.pump()
            
            # 等待更长时间，确保窗口完全显示
            import time
            time.sleep(0.2)
            
            # 再次刷新显示，确保窗口可见
            pygame.display.flip()
            pygame.event.pump()
            time.sleep(0.1)
            
            self.running = True
            
            # 立即渲染第一帧，确保窗口有内容显示
            # 创建默认的音频特征数据
            default_features = {
                "beat_strength": 0.0,
                "onset_envelope": 0.0,
                "mel_coeffs": [0.0] * 128,
                "tempo": 120.0,
                "rms": 0.0,
                "spectral_centroid": 0.0,
                "spectral_bandwidth": 0.0,
                "zero_crossing_rate": 0.0,
                "mfcc": [0.0] * 13
            }
            self.update(default_features)
            self.render()
        except pygame.error:
            self.running = False
            return
        
        # 重新初始化所有已注册的组件（确保状态正确）
        if self.surface:
            for component in self.components.values():
                try:
                    component.initialize(self.surface, self.config)
                except Exception:
                    pass

    def register_component(self, component: VisualComponent) -> None:
        """注册视觉组件"""
        self.components[component.name] = component
        if self.surface:
            component.initialize(self.surface, self.config)

    def activate_component(self, component_name: str) -> None:
        """激活视觉组件"""
        if component_name in self.components and component_name not in self.active_components:
            self.active_components.append(component_name)

    def deactivate_component(self, component_name: str) -> None:
        """停用视觉组件"""
        if component_name in self.active_components:
            self.active_components.remove(component_name)

    def set_config(self, config: Dict[str, Any]) -> None:
        """设置配置"""
        self.config.update(config)
        # 更新视觉配置
        self.visual_config = VisualConfig(
            width=self.config.get("width", 640),
            height=self.config.get("height", 480),
            fps=self.config.get("fps", 30),
            background_color=self.config.get("background_color", "#1a1a1a")
        )
        # 重新初始化所有组件
        if self.surface:
            for component in self.components.values():
                component.initialize(self.surface, self.config)

    def update(self, audio_features: Dict[str, Any]) -> None:
        """更新所有激活的组件"""
        # 更新组件
        for component_name in self.active_components:
            if component_name in self.components:
                try:
                    self.components[component_name].update(audio_features, 0.0)
                except Exception:
                    pass

    def render(self) -> None:
        """渲染所有激活的组件"""
        if not self.surface:
            return

        # 清屏
        bg_color = pygame.Color(self.visual_config.background_color)
        self.surface.fill(bg_color)

        # 渲染组件
        for component_name in self.active_components:
            if component_name in self.components:
                try:
                    self.components[component_name].render(self.surface)
                except Exception:
                    pass

        # 更新显示
        try:
            pygame.display.flip()
        except Exception:
            pass

    def run(self, audio_feature_generator) -> None:
        """运行渲染循环
        
        Args:
            audio_feature_generator: 音频特征生成器对象（AudioFeatureGenerator）
        """
        # 不再调用initialize()，因为窗口已经在主线程中初始化了
        # 只需要确保running标志为True
        self.running = True
        
        # 设置时钟控制帧率
        clock = pygame.time.Clock()
        
        try:
            while self.running:
                # 处理事件 - 添加超时机制，避免阻塞
                try:
                    # 使用peek检查是否有事件，避免阻塞
                    if pygame.event.peek():
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                self.running = False
                                # 触发窗口关闭回调（如果存在）
                                if hasattr(self, 'on_close_callback') and self.on_close_callback:
                                    try:
                                        self.on_close_callback()
                                    except Exception:
                                        pass
                                break
                except Exception:
                    pass
                
                # 如果已经停止，立即退出
                if not self.running:
                    break
                
                # 处理额外的事件，确保GUI响应
                try:
                    pygame.event.pump()
                except Exception:
                    pass
                
                # 获取最新的音频特征（从缓冲区，不阻塞渲染）
                try:
                    audio_features = audio_feature_generator.get_latest_features()
                except Exception:
                    audio_features = None
                
                # 如果没有特征，跳过这一帧，但仍然渲染（保持窗口显示）
                if audio_features is None:
                    try:
                        self.render()
                    except Exception:
                        pass
                    clock.tick(self.visual_config.fps)
                    continue
                
                # 更新和渲染
                self.update(audio_features)
                self.render()
                
                # 控制帧率（窗体刷新率）
                clock.tick(self.visual_config.fps)
        except Exception:
            pass
        finally:
            # 渲染循环结束时的清理
            try:
                self.surface = None
            except Exception:
                pass

    def cleanup(self) -> None:
        """清理资源"""
        # 设置running为False，停止渲染循环
        self.running = False
        
        # 检查是否已经清理过
        if self.surface is None:
            return
        
        # 清理surface引用，不尝试关闭pygame窗口（避免阻塞）
        self.surface = None
    
    def cleanup_window(self) -> None:
        """在主线程中清理pygame窗口"""
        # 设置running为False，停止渲染循环
        self.running = False
        
        # 等待一小段时间让渲染循环退出
        import time
        time.sleep(0.2)
        
        # 完全重置pygame显示系统（避免窗体残留）
        try:
            pygame.quit()
        except Exception:
            pass
        
        self.surface = None
        # 设置标志，强制下次重新初始化
        self.force_reinit = True

    def set_background_color(self, color: str) -> None:
        """设置背景颜色"""
        self.visual_config.background_color = color

    def set_resolution(self, width: int, height: int) -> None:
        """设置分辨率"""
        self.visual_config.width = width
        self.visual_config.height = height

    def toggle_fullscreen(self) -> None:
        """切换全屏模式"""
        # 切换全屏标志
        self.is_fullscreen = not self.is_fullscreen
        
        # 保存当前窗口尺寸
        if not self.is_fullscreen:
            # 恢复到原始尺寸（无标题栏窗口）
            width, height = self.visual_config.width, self.visual_config.height
            self.surface = pygame.display.set_mode((width, height), pygame.NOFRAME)
        else:
            # 切换到全屏
            self.surface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            # 更新配置为全屏尺寸
            width, height = self.surface.get_size()
            self.visual_config.width = width
            self.visual_config.height = height
        
        # 强制刷新显示
        pygame.display.flip()
        
        # 处理所有待处理的事件
        pygame.event.pump()
        
        # 重新初始化所有组件，更新它们的表面引用
        for component in self.components.values():
            component.initialize(self.surface, self.config)

    def set_fps(self, fps: int) -> None:
        """设置帧率"""
        self.visual_config.fps = fps
