import sys
import os
import time
import yaml
import numpy as np
from typing import Dict, Any, Optional
from src.audio.audio_parser import AudioParser
from src.audio.feature_extractor import FeatureExtractorManager, FeatureConfig
from src.audio.audio_feature_generator import AudioFeatureGenerator
from src.audio.microphone_input import MicrophoneFeatureGenerator
from src.visual.renderer import VisualRenderer
from src.visual.components import (
    WaveformVisualizer,
    SpectrumVisualizer,
    EqualizerVisualizer,
    SpectrumCubeVisualizer,
    Audio3DModelVisualizer,
    InfoDisplayVisualizer,
    ComprehensiveVisualizer
)
from src.visual.particles import (
    ParticleSystem,
    BeatParticleSystem,
    JumpingParticleSystem,
    StyleAwareParticleSystem
)
from src.visual.effects import (
    RainEffect,
    FireEffect,
    SnowEffect,
    PetalEffect,
    GlowingSquaresEffect
)
from src.core.interfaces import AudioVisualizerInterface
from src.core.event_system import get_event_system, EventType


class MusicV(AudioVisualizerInterface):
    """MusicV 主类"""

    def __init__(self, config_path: str = "config.yaml"):
        """初始化 MusicV"""
        # 加载配置
        self.config = self._load_config(config_path)
        # 初始化事件系统
        self.event_system = get_event_system()
        self.event_system.start()
        # 初始化音频解析器
        self.audio_parser = AudioParser()
        self.feature_extractor = FeatureExtractorManager()
        # 提取FeatureConfig需要的参数
        feature_extraction_config = self.config.get("audio", {}).get("feature_extraction", {})
        # 构建FeatureConfig参数
        feature_config_params = {
            "window_size": feature_extraction_config.get("temporal", {}).get("window_size", 2048),
            "hop_size": feature_extraction_config.get("temporal", {}).get("hop_size", 512),
            "n_fft": feature_extraction_config.get("frequency", {}).get("n_fft", 2048),
            "n_mels": feature_extraction_config.get("frequency", {}).get("n_mels", 128),
            "n_mfcc": feature_extraction_config.get("timbre", {}).get("n_mfcc", 13),
            "bpm_range": feature_extraction_config.get("rhythm", {}).get("bpm_range", [60, 200])
        }
        self.feature_config = FeatureConfig(**feature_config_params)
        # 初始化视觉渲染器
        self.visual_renderer = VisualRenderer(self.config.get("visual", {}))
        # 注册视觉组件
        self._register_visual_components()
        # 当前音频路径
        self.current_audio_path = None
        # 当前音频特征
        self.current_features = None
        # 音频特征数据（用于数据预览）
        self.audio_features = None
        # 当前可视化类型
        self.current_visual_type = "waveform"
        # 当前运动模式
        self.current_pattern = "default"
        # 当前音频特征生成器
        self.current_feature_generator = None
        # 麦克风特征生成器
        self.microphone_generator = None
        # 当前输入模式: "file" 或 "microphone"
        self.input_mode = "file"
        # 可视化运行标志
        self.is_visualization_running = False

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}

    def _register_visual_components(self):
        """注册视觉组件"""
        # 2D 可视化组件
        self.visual_renderer.register_component(WaveformVisualizer())
        self.visual_renderer.register_component(SpectrumVisualizer())
        self.visual_renderer.register_component(EqualizerVisualizer())
        # 3D 可视化组件
        self.visual_renderer.register_component(SpectrumCubeVisualizer())
        self.visual_renderer.register_component(Audio3DModelVisualizer())
        # 粒子系统组件
        self.visual_renderer.register_component(ParticleSystem())
        self.visual_renderer.register_component(BeatParticleSystem())
        self.visual_renderer.register_component(JumpingParticleSystem())
        self.visual_renderer.register_component(StyleAwareParticleSystem())
        # 特效系统组件
        self.visual_renderer.register_component(RainEffect())
        self.visual_renderer.register_component(FireEffect())
        self.visual_renderer.register_component(SnowEffect())
        self.visual_renderer.register_component(PetalEffect())
        self.visual_renderer.register_component(GlowingSquaresEffect())
        # 信息显示组件
        self.visual_renderer.register_component(InfoDisplayVisualizer())
        # 综合可视化组件
        self.visual_renderer.register_component(ComprehensiveVisualizer())

    def load_audio(self, file_path: str) -> bool:
        """加载音频文件"""
        try:
            # 加载音频
            audio_data = self.audio_parser.load_audio(file_path)
            # 提取特征
            features = self.feature_extractor.extract_all(audio_data.y, audio_data.sr, self.feature_config)
            self.current_features = features
            self.audio_features = features
            self.current_audio_path = file_path
            # 发送音频加载完成事件
            self.event_system.emit(EventType.AUDIO_LOADED, {
                "file_path": file_path,
                "duration": audio_data.duration,
                "sr": audio_data.sr
            })
            return True
        except Exception as e:
            print(f"Error loading audio: {e}")
            self.event_system.emit(EventType.ERROR_OCCURRED, {"message": str(e)})
            return False

    def start_visualization(self):
        """开始可视化（文件模式）"""
        if self.input_mode == "microphone":
            self._start_microphone_visualization()
            return
        
        if not self.current_features:
            return

        # 检查是否已经在运行
        if self.is_visualization_running:
            return

        # 设置运行标志
        self.is_visualization_running = True

        # 激活当前可视化类型
        self._activate_visual_component(self.current_visual_type)

        # 获取音频数据和特征
        audio_data = self.audio_parser.audio_data
        full_features = self.current_features
        
        # 创建音频特征生成器（数据刷新率：120 FPS）
        feature_generator = AudioFeatureGenerator(
            audio_path=self.current_audio_path,
            full_features=full_features,
            audio_data=audio_data,
            sample_rate=audio_data.sr,
            hop_length=512,
            update_rate=120.0  # 数据刷新率：120 FPS（比窗体刷新率快2倍）
        )
        
        # 设置帧更新回调（用于数据预览窗口）
        def frame_update_callback(frame_idx):
            if hasattr(self, 'data_preview_window') and self.data_preview_window:
                try:
                    self.data_preview_window.update_charts(frame_idx)
                except Exception as e:
                    print(f"更新数据预览窗口失败: {e}")
        
        feature_generator.set_frame_update_callback(frame_update_callback)
        
        # 保存音频特征生成器对象，以便在stop_visualization中停止音频播放
        self.current_feature_generator = feature_generator
        
        # 设置窗口关闭回调
        self.visual_renderer.on_close_callback = self.stop_visualization
        
        try:
            # 启动音频特征生成器（独立线程，120 FPS）
            feature_generator.start()
            
            # 运行视觉渲染器（主线程，60 FPS）
            self.visual_renderer.run(feature_generator)
        finally:
            # 确保停止可视化和音频播放
            self.stop_visualization()
            # 停止音频特征生成器
            feature_generator.stop()
    
    def _start_microphone_visualization(self):
        """开始麦克风实时可视化"""
        if self.is_visualization_running:
            return
        
        self.is_visualization_running = True
        
        self._activate_visual_component(self.current_visual_type)
        
        # 使用配置文件中的参数
        feature_extraction_config = self.config.get("audio", {}).get("feature_extraction", {})
        mic_config = {
            'window_size': feature_extraction_config.get("temporal", {}).get("window_size", 2048),
            'hop_size': feature_extraction_config.get("temporal", {}).get("hop_size", 512),
            'n_fft': feature_extraction_config.get("frequency", {}).get("n_fft", 2048),
            'n_mels': feature_extraction_config.get("frequency", {}).get("n_mels", 128),
            'n_mfcc': feature_extraction_config.get("timbre", {}).get("n_mfcc", 13),
            'chunk_size': 1024
        }
        
        self.microphone_generator = MicrophoneFeatureGenerator(
            sample_rate=16000,
            update_rate=30.0,
            config=mic_config
        )
        
        if not self.microphone_generator.start():
            self.is_visualization_running = False
            self.microphone_generator = None
            return
        
        self.visual_renderer.on_close_callback = self.stop_visualization
        
        try:
            self.visual_renderer.run(self.microphone_generator)
        finally:
            self.stop_visualization()
    
    def set_input_mode(self, mode: str) -> bool:
        """
        设置输入模式
        
        Args:
            mode: "file" 或 "microphone"
            
        Returns:
            是否设置成功
        """
        if mode not in ["file", "microphone"]:
            return False
        
        if mode == "microphone":
            mic = MicrophoneFeatureGenerator(
                sample_rate=16000,
                update_rate=30.0
            )
            if not mic.microphone.is_available():
                return False
            if mic.start():
                mic.stop()
                del mic
        
        self.input_mode = mode
        return True
    
    def is_microphone_available(self) -> bool:
        """
        检查麦克风是否可用
        
        Returns:
            麦克风是否可用
        """
        mic = MicrophoneFeatureGenerator(sample_rate=16000, update_rate=30.0)
        return mic.microphone.is_available()

    def stop_visualization(self) -> None:
        """停止可视化"""
        # 检查是否已经在停止状态
        if not self.is_visualization_running:
            return

        # 设置运行标志为False
        self.is_visualization_running = False
        
        # 设置视觉渲染器的运行标志为False，确保渲染循环退出
        if hasattr(self.visual_renderer, 'running'):
            self.visual_renderer.running = False
        
        # 停止音频播放
        if self.current_feature_generator:
            self.current_feature_generator.stop()
            self.current_feature_generator = None
        
        # 停止麦克风输入
        if self.microphone_generator:
            self.microphone_generator.stop()
            self.microphone_generator = None
        
        # 等待渲染循环退出
        import time
        time.sleep(0.3)
        
        # 在主线程中清理窗口
        self.visual_renderer.cleanup_window()

    def set_visual_type(self, visual_type: str) -> None:
        """设置可视化类型"""
        self.current_visual_type = visual_type
        # 发送可视化类型变更事件
        self.event_system.emit(EventType.VISUAL_TYPE_CHANGED, {"visual_type": visual_type})

    def set_pattern(self, pattern_code: str) -> None:
        """设置运动模式"""
        self.current_pattern = pattern_code
        # 发送模式变更事件
        self.event_system.emit(EventType.PATTERN_CHANGED, {"pattern": pattern_code})
        
        # 应用模式到当前激活的视觉组件
        if self.visual_renderer.active_components:
            for component_name in self.visual_renderer.active_components:
                component = self.visual_renderer.components.get(component_name)
                if component and hasattr(component, 'update_pattern_params'):
                    # 从pattern_library获取模式配置
                    from src.pattern.pattern_library import PatternLibrary
                    from src.pattern.pattern_matcher import PatternMatcher
                    pattern_matcher = PatternMatcher()
                    pattern_library = PatternLibrary(pattern_matcher)
                    
                    # 获取模式名称
                    pattern_name = f"{pattern_code}_{component_name}"
                    pattern_config = pattern_matcher.get_pattern_config(pattern_name)
                    
                    if pattern_config:
                        # 应用模式参数
                        component.update_pattern_params(pattern_config)
                        print(f"应用模式: {pattern_name}")
                    else:
                        print(f"未找到模式: {pattern_name}")

    def set_config(self, config: Dict[str, Any]) -> None:
        """设置配置"""
        self.config.update(config)
        self.visual_renderer.set_config(config.get("visual", {}))
        # 发送配置更新事件
        self.event_system.emit(EventType.CONFIG_UPDATED, {"config": config})

    def _activate_visual_component(self, component_name: str):
        """激活视觉组件"""
        # 停用所有组件
        for component in self.visual_renderer.components:
            self.visual_renderer.deactivate_component(component)
        # 激活指定组件
        self.visual_renderer.activate_component(component_name)

    def cleanup(self):
        """清理资源"""
        # 停止可视化（包括音频播放）
        if self.is_visualization_running:
            self.stop_visualization()
        
        # 清理视觉渲染器
        self.visual_renderer.cleanup()
        
        # 停止事件系统
        self.event_system.stop()
        
        # 完全退出pygame系统
        import pygame
        if pygame.get_init():
            pygame.quit()


def main():
    """主函数"""
    # 创建 MusicV 实例
    musicv = MusicV()

    # 检查命令行参数
    if len(sys.argv) > 1:
        audio_path = sys.argv[1]
        if os.path.exists(audio_path):
            musicv.load_audio(audio_path)
            musicv.start_visualization()
        else:
            print(f"Audio file not found: {audio_path}")
    else:
        print("Usage: musicv <audio_file_path>")

    # 清理资源
    musicv.cleanup()


if __name__ == "__main__":
    main()
