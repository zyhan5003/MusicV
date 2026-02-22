import unittest
import os
import tempfile
import numpy as np
from src.audio.audio_parser import AudioParser, AudioData, AudioFeatures
from src.audio.feature_extractor import FeatureExtractorManager, FeatureConfig


class TestAudioParser(unittest.TestCase):
    """测试音频解析模块"""

    def setUp(self):
        """设置测试环境"""
        self.parser = AudioParser()
        # 创建一个简单的测试音频
        self.test_audio = np.sin(2 * np.pi * 440 * np.linspace(0, 1, 44100))
        self.test_sr = 44100

    def test_load_audio(self):
        """测试加载音频文件"""
        # 创建临时音频文件
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_file = f.name
        
        # 保存测试音频
        import soundfile as sf
        sf.write(temp_file, self.test_audio, self.test_sr)
        
        try:
            # 加载音频
            audio_data = self.parser.load_audio(temp_file)
            # 验证音频数据
            self.assertIsInstance(audio_data, AudioData)
            self.assertEqual(audio_data.sr, self.test_sr)
            self.assertAlmostEqual(audio_data.duration, 1.0, delta=0.1)
        finally:
            # 清理临时文件
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_extract_features(self):
        """测试提取音频特征"""
        # 创建音频数据
        audio_data = AudioData(
            y=self.test_audio,
            sr=self.test_sr,
            duration=1.0,
            channels=1
        )
        
        # 提取特征
        features = self.parser.extract_features(audio_data)
        
        # 验证特征数据
        self.assertIsInstance(features, AudioFeatures)
        self.assertIsInstance(features.amplitude, np.ndarray)
        self.assertIsInstance(features.loudness, np.ndarray)
        self.assertIsInstance(features.spectrum, np.ndarray)
        self.assertIsInstance(features.mel_spectrogram, np.ndarray)
        self.assertIsInstance(features.bpm, float)
        self.assertIsInstance(features.beat_frames, np.ndarray)
        self.assertIsInstance(features.mfcc, np.ndarray)
        self.assertIsInstance(features.spectral_centroid, np.ndarray)
        self.assertIsInstance(features.spectral_bandwidth, np.ndarray)

    def test_save_load_features(self):
        """测试保存和加载特征"""
        # 创建音频数据
        audio_data = AudioData(
            y=self.test_audio,
            sr=self.test_sr,
            duration=1.0,
            channels=1
        )
        
        # 提取特征
        features = self.parser.extract_features(audio_data)
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_file = f.name
        
        try:
            # 保存特征
            self.parser.save_features(temp_file)
            # 加载特征
            loaded_features = self.parser.load_features(temp_file)
            # 验证特征
            self.assertIsInstance(loaded_features, AudioFeatures)
            self.assertEqual(len(loaded_features.amplitude), len(features.amplitude))
            self.assertEqual(len(loaded_features.loudness), len(features.loudness))
        finally:
            # 清理临时文件
            if os.path.exists(temp_file):
                os.unlink(temp_file)


class TestFeatureExtractor(unittest.TestCase):
    """测试特征提取器"""

    def setUp(self):
        """设置测试环境"""
        self.extractor_manager = FeatureExtractorManager()
        self.feature_config = FeatureConfig()
        # 创建测试音频
        self.test_audio = np.sin(2 * np.pi * 440 * np.linspace(0, 1, 44100))
        self.test_sr = 44100

    def test_extract_all(self):
        """测试提取所有特征"""
        features = self.extractor_manager.extract_all(
            self.test_audio,
            self.test_sr,
            self.feature_config
        )
        
        # 验证特征
        self.assertIn("temporal", features)
        self.assertIn("frequency", features)
        self.assertIn("rhythm", features)
        self.assertIn("timbre", features)

        # 验证时域特征
        temporal_features = features["temporal"]
        self.assertIn("amplitude", temporal_features)
        self.assertIn("loudness", temporal_features)
        self.assertIn("zero_crossing_rate", temporal_features)

        # 验证频域特征
        frequency_features = features["frequency"]
        self.assertIn("spectrum", frequency_features)
        self.assertIn("mel_spectrogram", frequency_features)
        self.assertIn("log_mel_spectrogram", frequency_features)

        # 验证节奏特征
        rhythm_features = features["rhythm"]
        self.assertIn("bpm", rhythm_features)
        self.assertIn("beat_frames", rhythm_features)
        self.assertIn("beat_times", rhythm_features)
        self.assertIn("beat_strength", rhythm_features)

        # 验证音色特征
        timbre_features = features["timbre"]
        self.assertIn("mfcc", timbre_features)
        self.assertIn("spectral_centroid", timbre_features)
        self.assertIn("spectral_bandwidth", timbre_features)
        self.assertIn("spectral_rolloff", timbre_features)

    def test_extract_selected(self):
        """测试提取指定特征"""
        extractor_names = ["temporal", "rhythm"]
        features = self.extractor_manager.extract_selected(
            self.test_audio,
            self.test_sr,
            self.feature_config,
            extractor_names
        )
        
        # 验证特征
        self.assertIn("temporal", features)
        self.assertIn("rhythm", features)
        self.assertNotIn("frequency", features)
        self.assertNotIn("timbre", features)


if __name__ == "__main__":
    unittest.main()
