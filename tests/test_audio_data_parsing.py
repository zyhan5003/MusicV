"""
音频数据解析测试用例
评估音频数据的实时性、同步性、准确度等维度
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import time
from typing import Dict, Any, List, Tuple
from src.audio.audio_parser import AudioParser
from src.audio.feature_extractor import FeatureExtractorManager, FeatureConfig
from src.audio.data_visualizer import AudioDataVisualizer
from src.visual.effects.beat_utils import OnsetIntensityTracker


class AudioDataParsingTest:
    """音频数据解析测试类"""
    
    def __init__(self, audio_path: str):
        """初始化测试"""
        self.audio_path = audio_path
        self.audio_parser = AudioParser()
        self.feature_extractor_manager = FeatureExtractorManager()
        self.feature_config = FeatureConfig()
        self.test_results: Dict[str, Any] = {}
        
        # 性能指标
        self.load_time = 0.0
        self.feature_extraction_time = 0.0
        self.frame_processing_times: List[float] = []
        
        # 同步性指标
        self.audio_video_sync_offset: List[float] = []
        
        # 准确度指标
        self.feature_accuracy: Dict[str, float] = {}
        
    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试"""
        print("=" * 60)
        print("音频数据解析测试")
        print("=" * 60)
        print(f"测试音频: {self.audio_path}")
        print()
        
        # 1. 测试音频加载
        self.test_audio_loading()
        
        # 2. 测试特征提取
        self.test_feature_extraction()
        
        # 3. 测试实时性
        self.test_realtime_performance()
        
        # 4. 测试同步性
        self.test_synchronization()
        
        # 5. 测试准确度
        self.test_accuracy()
        
        # 6. 分析视觉效果与音乐关联度
        self.test_visual_music_correlation()
        
        # 7. 生成测试报告
        self.generate_report()
        
        return self.test_results
    
    def test_audio_loading(self) -> None:
        """测试音频加载"""
        print("1. 测试音频加载...")
        
        start_time = time.time()
        audio_data = self.audio_parser.load_audio(self.audio_path)
        self.load_time = time.time() - start_time
        
        print(f"   ✓ 音频加载时间: {self.load_time:.3f}秒")
        print(f"   ✓ 采样率: {audio_data.sr} Hz")
        print(f"   ✓ 时长: {audio_data.duration:.2f}秒")
        print(f"   ✓ 采样点数: {len(audio_data.y)}")
        print()
        
        self.test_results['audio_loading'] = {
            'load_time': self.load_time,
            'sample_rate': audio_data.sr,
            'duration': audio_data.duration,
            'sample_count': len(audio_data.y)
        }
        
        self.audio_data = audio_data
    
    def test_feature_extraction(self) -> None:
        """测试特征提取"""
        print("2. 测试特征提取...")
        
        start_time = time.time()
        features = self.feature_extractor_manager.extract_all(
            self.audio_data.y, 
            self.audio_data.sr, 
            self.feature_config
        )
        self.feature_extraction_time = time.time() - start_time
        
        print(f"   ✓ 特征提取时间: {self.feature_extraction_time:.3f}秒")
        print(f"   ✓ 特征类别数: {len(features)}")
        
        # 打印各类特征
        for category, category_features in features.items():
            print(f"   ✓ {category}: {list(category_features.keys())}")
        
        print()
        
        self.test_results['feature_extraction'] = {
            'extraction_time': self.feature_extraction_time,
            'feature_categories': len(features),
            'features': features
        }
        
        self.features = features
    
    def test_realtime_performance(self) -> None:
        """测试实时性能"""
        print("3. 测试实时性能...")
        
        # 模拟实时处理
        frame_count = 0
        total_frames = 1000  # 测试1000帧
        
        onset_tracker = OnsetIntensityTracker(smoothing_factor=0.1)
        
        for frame in range(total_frames):
            start_time = time.time()
            
            # 模拟特征更新
            if "rhythm" in self.features and "onset_envelope" in self.features["rhythm"]:
                onset_env = self.features["rhythm"]["onset_envelope"]
                if frame < len(onset_env):
                    onset_intensity = onset_tracker.update({
                        "rhythm": {
                            "onset_envelope": onset_env[:frame+1]
                        }
                    })
            
            processing_time = time.time() - start_time
            self.frame_processing_times.append(processing_time)
            frame_count += 1
        
        # 计算性能指标
        avg_processing_time = np.mean(self.frame_processing_times)
        max_processing_time = np.max(self.frame_processing_times)
        min_processing_time = np.min(self.frame_processing_times)
        std_processing_time = np.std(self.frame_processing_times)
        
        # 计算帧率
        if avg_processing_time > 0:
            avg_fps = 1.0 / avg_processing_time
            min_fps = 1.0 / max_processing_time
        else:
            avg_fps = 0
            min_fps = 0
        
        print(f"   ✓ 平均处理时间: {avg_processing_time*1000:.3f}毫秒")
        print(f"   ✓ 最大处理时间: {max_processing_time*1000:.3f}毫秒")
        print(f"   ✓ 最小处理时间: {min_processing_time*1000:.3f}毫秒")
        print(f"   ✓ 处理时间标准差: {std_processing_time*1000:.3f}毫秒")
        print(f"   ✓ 平均帧率: {avg_fps:.1f} FPS")
        print(f"   ✓ 最低帧率: {min_fps:.1f} FPS")
        
        # 评估实时性
        realtime_score = self._evaluate_realtime(avg_fps, std_processing_time)
        print(f"   ✓ 实时性评分: {realtime_score:.1f}/100")
        print()
        
        self.test_results['realtime_performance'] = {
            'avg_processing_time': avg_processing_time,
            'max_processing_time': max_processing_time,
            'min_processing_time': min_processing_time,
            'std_processing_time': std_processing_time,
            'avg_fps': avg_fps,
            'min_fps': min_fps,
            'realtime_score': realtime_score
        }
    
    def test_synchronization(self) -> None:
        """测试同步性"""
        print("4. 测试同步性...")
        
        # 检查特征帧与音频帧的对应关系
        if "rhythm" in self.features and "onset_envelope" in self.features["rhythm"]:
            onset_env = self.features["rhythm"]["onset_envelope"]
            onset_frames = len(onset_env)
            
            # 计算音频帧数
            audio_frames = len(self.audio_data.y)
            
            # 计算hop_length（特征提取的步长）
            hop_length = self.feature_config.hop_size
            
            # 计算理论上的特征帧数
            expected_frames = (audio_frames // hop_length) + 1
            
            # 计算同步偏移
            sync_offset = abs(onset_frames - expected_frames)
            sync_ratio = onset_frames / expected_frames if expected_frames > 0 else 0
            
            print(f"   ✓ 音频帧数: {audio_frames}")
            print(f"   ✓ 特征帧数: {onset_frames}")
            print(f"   ✓ 理论特征帧数: {expected_frames}")
            print(f"   ✓ 同步偏移: {sync_offset}帧")
            print(f"   ✓ 同步比率: {sync_ratio:.3f}")
            
            # 评估同步性
            sync_score = self._evaluate_synchronization(sync_offset, expected_frames)
            print(f"   ✓ 同步性评分: {sync_score:.1f}/100")
            print()
            
            self.test_results['synchronization'] = {
                'audio_frames': audio_frames,
                'feature_frames': onset_frames,
                'expected_frames': expected_frames,
                'sync_offset': sync_offset,
                'sync_ratio': sync_ratio,
                'sync_score': sync_score
            }
        else:
            print("   ✗ 缺少onset_envelope数据")
            print()
            
            self.test_results['synchronization'] = {
                'sync_score': 0
            }
    
    def test_accuracy(self) -> None:
        """测试准确度"""
        print("5. 测试准确度...")
        
        accuracy_scores = {}
        
        # 1. 测试onset_envelope的准确性
        if "rhythm" in self.features and "onset_envelope" in self.features["rhythm"]:
            onset_env = self.features["rhythm"]["onset_envelope"]
            
            # 检查数据范围
            onset_min = np.min(onset_env)
            onset_max = np.max(onset_env)
            onset_mean = np.mean(onset_env)
            onset_std = np.std(onset_env)
            
            print(f"   ✓ onset_envelope范围: [{onset_min:.3f}, {onset_max:.3f}]")
            print(f"   ✓ onset_envelope均值: {onset_mean:.3f}")
            print(f"   ✓ onset_envelope标准差: {onset_std:.3f}")
            
            # 评估onset_envelope的准确性
            onset_accuracy = self._evaluate_onset_accuracy(onset_env)
            accuracy_scores['onset_envelope'] = onset_accuracy
            print(f"   ✓ onset_envelope准确性: {onset_accuracy:.1f}/100")
        
        # 2. 测试beat_strength的准确性
        if "rhythm" in self.features and "beat_strength" in self.features["rhythm"]:
            beat_strength = self.features["rhythm"]["beat_strength"]
            
            # 检查数据范围
            beat_min = np.min(beat_strength)
            beat_max = np.max(beat_strength)
            beat_mean = np.mean(beat_strength)
            beat_std = np.std(beat_strength)
            
            print(f"   ✓ beat_strength范围: [{beat_min:.3f}, {beat_max:.3f}]")
            print(f"   ✓ beat_strength均值: {beat_mean:.3f}")
            print(f"   ✓ beat_strength标准差: {beat_std:.3f}")
            
            # 评估beat_strength的准确性
            beat_accuracy = self._evaluate_beat_accuracy(beat_strength)
            accuracy_scores['beat_strength'] = beat_accuracy
            print(f"   ✓ beat_strength准确性: {beat_accuracy:.1f}/100")
        
        print()
        
        # 计算总体准确度
        overall_accuracy = np.mean(list(accuracy_scores.values())) if accuracy_scores else 0
        print(f"   ✓ 总体准确度: {overall_accuracy:.1f}/100")
        print()
        
        self.test_results['accuracy'] = {
            'accuracy_scores': accuracy_scores,
            'overall_accuracy': overall_accuracy
        }
    
    def test_visual_music_correlation(self) -> None:
        """测试视觉效果与音乐关联度"""
        print("6. 测试视觉效果与音乐关联度...")
        
        correlation_scores = {}
        
        # 1. 分析onset_envelope与音乐节奏的关联
        if "rhythm" in self.features and "onset_envelope" in self.features["rhythm"]:
            onset_env = self.features["rhythm"]["onset_envelope"]
            
            # 计算onset_envelope的变化率
            onset_diff = np.diff(onset_env)
            onset_change_rate = np.abs(onset_diff)
            
            # 计算峰值检测
            from scipy.signal import find_peaks
            peaks, _ = find_peaks(onset_env, height=np.mean(onset_env) + np.std(onset_env))
            
            print(f"   ✓ onset_envelope峰值数: {len(peaks)}")
            print(f"   ✓ 平均峰值间隔: {len(onset_env)/len(peaks):.1f}帧" if len(peaks) > 0 else "   ✓ 无峰值")
            
            # 评估关联度
            onset_correlation = self._evaluate_visual_music_correlation(onset_env, peaks)
            correlation_scores['onset_envelope'] = onset_correlation
            print(f"   ✓ onset_envelope关联度: {onset_correlation:.1f}/100")
        
        # 2. 分析beat_strength与音乐节奏的关联
        if "rhythm" in self.features and "beat_strength" in self.features["rhythm"]:
            beat_strength = self.features["rhythm"]["beat_strength"]
            
            # 计算beat_strength的变化率
            beat_diff = np.diff(beat_strength)
            beat_change_rate = np.abs(beat_diff)
            
            # 计算峰值检测
            from scipy.signal import find_peaks
            peaks, _ = find_peaks(beat_strength, height=np.mean(beat_strength) + np.std(beat_strength))
            
            print(f"   ✓ beat_strength峰值数: {len(peaks)}")
            print(f"   ✓ 平均峰值间隔: {len(beat_strength)/len(peaks):.1f}帧" if len(peaks) > 0 else "   ✓ 无峰值")
            
            # 评估关联度
            beat_correlation = self._evaluate_visual_music_correlation(beat_strength, peaks)
            correlation_scores['beat_strength'] = beat_correlation
            print(f"   ✓ beat_strength关联度: {beat_correlation:.1f}/100")
        
        print()
        
        # 计算总体关联度
        overall_correlation = np.mean(list(correlation_scores.values())) if correlation_scores else 0
        print(f"   ✓ 总体关联度: {overall_correlation:.1f}/100")
        print()
        
        self.test_results['visual_music_correlation'] = {
            'correlation_scores': correlation_scores,
            'overall_correlation': overall_correlation
        }
    
    def _evaluate_realtime(self, avg_fps: float, std_processing_time: float) -> float:
        """评估实时性"""
        # 目标帧率是60 FPS
        target_fps = 60.0
        
        # 帧率得分 (0-50分)
        fps_score = min(50, (avg_fps / target_fps) * 50)
        
        # 稳定性得分 (0-50分)
        # 标准差越小，稳定性越好
        stability_score = max(0, 50 - (std_processing_time * 100000))
        
        return fps_score + stability_score
    
    def _evaluate_synchronization(self, sync_offset: int, expected_frames: int) -> float:
        """评估同步性"""
        # 偏移越小，同步性越好
        if expected_frames == 0:
            return 0
        
        offset_ratio = sync_offset / expected_frames
        sync_score = max(0, 100 - (offset_ratio * 1000))
        
        return sync_score
    
    def _evaluate_onset_accuracy(self, onset_env: np.ndarray) -> float:
        """评估onset_envelope的准确性"""
        # 1. 数据范围得分 (0-30分)
        onset_min = np.min(onset_env)
        onset_max = np.max(onset_env)
        range_score = 0
        if onset_max > 0 and onset_min >= 0:
            range_score = 30
        
        # 2. 变化性得分 (0-40分)
        onset_std = np.std(onset_env)
        variation_score = min(40, (onset_std / np.mean(onset_env)) * 100) if np.mean(onset_env) > 0 else 0
        
        # 3. 峰值检测得分 (0-30分)
        from scipy.signal import find_peaks
        peaks, _ = find_peaks(onset_env, height=np.mean(onset_env) + np.std(onset_env))
        peak_score = min(30, (len(peaks) / len(onset_env)) * 1000)
        
        return range_score + variation_score + peak_score
    
    def _evaluate_beat_accuracy(self, beat_strength: np.ndarray) -> float:
        """评估beat_strength的准确性"""
        # 1. 数据范围得分 (0-30分)
        beat_min = np.min(beat_strength)
        beat_max = np.max(beat_strength)
        range_score = 0
        if beat_max > 0 and beat_min >= 0:
            range_score = 30
        
        # 2. 变化性得分 (0-40分)
        beat_std = np.std(beat_strength)
        variation_score = min(40, (beat_std / np.mean(beat_strength)) * 100) if np.mean(beat_strength) > 0 else 0
        
        # 3. 峰值检测得分 (0-30分)
        from scipy.signal import find_peaks
        peaks, _ = find_peaks(beat_strength, height=np.mean(beat_strength) + np.std(beat_strength))
        peak_score = min(30, (len(peaks) / len(beat_strength)) * 1000)
        
        return range_score + variation_score + peak_score
    
    def _evaluate_visual_music_correlation(self, data: np.ndarray, peaks: np.ndarray) -> float:
        """评估视觉效果与音乐关联度"""
        # 1. 峰值数量得分 (0-40分)
        # 峰值数量适中，说明有明显的节奏
        peak_ratio = len(peaks) / len(data)
        peak_score = 0
        if 0.01 <= peak_ratio <= 0.1:
            peak_score = 40
        elif 0.001 <= peak_ratio < 0.01:
            peak_score = 30
        elif peak_ratio > 0.1:
            peak_score = 20
        
        # 2. 变化性得分 (0-30分)
        data_std = np.std(data)
        variation_score = min(30, (data_std / np.mean(data)) * 100) if np.mean(data) > 0 else 0
        
        # 3. 动态范围得分 (0-30分)
        data_range = np.max(data) - np.min(data)
        dynamic_score = min(30, data_range * 10)
        
        return peak_score + variation_score + dynamic_score
    
    def generate_report(self) -> None:
        """生成测试报告"""
        print("=" * 60)
        print("测试报告")
        print("=" * 60)
        print()
        
        # 1. 实时性评估
        realtime_score = self.test_results.get('realtime_performance', {}).get('realtime_score', 0)
        print(f"1. 实时性评估: {realtime_score:.1f}/100")
        if realtime_score >= 80:
            print("   ✓ 优秀：系统实时性能很好")
        elif realtime_score >= 60:
            print("   △ 良好：系统实时性能尚可")
        else:
            print("   ✗ 较差：系统实时性能需要优化")
        print()
        
        # 2. 同步性评估
        sync_score = self.test_results.get('synchronization', {}).get('sync_score', 0)
        print(f"2. 同步性评估: {sync_score:.1f}/100")
        if sync_score >= 80:
            print("   ✓ 优秀：音频与视觉同步性很好")
        elif sync_score >= 60:
            print("   △ 良好：音频与视觉同步性尚可")
        else:
            print("   ✗ 较差：音频与视觉同步性需要优化")
        print()
        
        # 3. 准确度评估
        accuracy_score = self.test_results.get('accuracy', {}).get('overall_accuracy', 0)
        print(f"3. 准确度评估: {accuracy_score:.1f}/100")
        if accuracy_score >= 80:
            print("   ✓ 优秀：特征提取准确性很高")
        elif accuracy_score >= 60:
            print("   △ 良好：特征提取准确性尚可")
        else:
            print("   ✗ 较差：特征提取准确性需要优化")
        print()
        
        # 4. 关联度评估
        correlation_score = self.test_results.get('visual_music_correlation', {}).get('overall_correlation', 0)
        print(f"4. 关联度评估: {correlation_score:.1f}/100")
        if correlation_score >= 80:
            print("   ✓ 优秀：视觉效果与音乐关联度很高")
        elif correlation_score >= 60:
            print("   △ 良好：视觉效果与音乐关联度尚可")
        else:
            print("   ✗ 较差：视觉效果与音乐关联度需要优化")
        print()
        
        # 5. 总体评估
        overall_score = (realtime_score + sync_score + accuracy_score + correlation_score) / 4
        print(f"5. 总体评估: {overall_score:.1f}/100")
        if overall_score >= 80:
            print("   ✓ 优秀：系统整体表现很好")
        elif overall_score >= 60:
            print("   △ 良好：系统整体表现尚可")
        else:
            print("   ✗ 较差：系统整体表现需要优化")
        print()
        
        # 6. 优化建议
        print("6. 优化建议:")
        self._generate_optimization_suggestions()
        print()
        
        self.test_results['overall_score'] = overall_score
    
    def _generate_optimization_suggestions(self) -> None:
        """生成优化建议"""
        suggestions = []
        
        # 实时性优化建议
        realtime_score = self.test_results.get('realtime_performance', {}).get('realtime_score', 0)
        if realtime_score < 60:
            suggestions.append("- 优化特征提取算法，减少计算时间")
            suggestions.append("- 使用多线程或GPU加速")
            suggestions.append("- 减少不必要的特征计算")
        
        # 同步性优化建议
        sync_score = self.test_results.get('synchronization', {}).get('sync_score', 0)
        if sync_score < 60:
            suggestions.append("- 检查特征提取的hop_length设置")
            suggestions.append("- 优化音频帧与特征帧的对应关系")
            suggestions.append("- 添加时间戳同步机制")
        
        # 准确度优化建议
        accuracy_score = self.test_results.get('accuracy', {}).get('overall_accuracy', 0)
        if accuracy_score < 60:
            suggestions.append("- 调整特征提取参数")
            suggestions.append("- 使用更先进的特征提取算法")
            suggestions.append("- 添加特征后处理和滤波")
        
        # 关联度优化建议
        correlation_score = self.test_results.get('visual_music_correlation', {}).get('overall_correlation', 0)
        if correlation_score < 60:
            suggestions.append("- 优化onset_envelope的计算方法")
            suggestions.append("- 调整粒子生成的关联因子")
            suggestions.append("- 增加粒子生成的响应速度")
            suggestions.append("- 使用更灵敏的平滑因子")
        
        if not suggestions:
            print("   ✓ 系统表现良好，暂无优化建议")
        else:
            for suggestion in suggestions:
                print(f"   {suggestion}")


def main():
    """主函数"""
    # 测试音频文件
    audio_path = "test_audio.wav"
    
    # 检查文件是否存在
    if not os.path.exists(audio_path):
        print(f"错误：找不到测试音频文件 {audio_path}")
        return
    
    # 创建测试实例
    test = AudioDataParsingTest(audio_path)
    
    # 运行所有测试
    results = test.run_all_tests()
    
    # 保存结果
    import json
    with open("test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    
    print("测试结果已保存到 test_results.json")


if __name__ == "__main__":
    main()
