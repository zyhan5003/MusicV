import threading
import numpy as np
import time
from typing import Dict, Any, Optional, Callable
from collections import deque


class MicrophoneInput:
    """麦克风实时输入捕获器"""
    
    def __init__(
        self,
        sample_rate: int = 16000,
        chunk_size: int = 1024,
        channels: int = 1
    ):
        """
        初始化麦克风输入
        
        Args:
            sample_rate: 采样率
            chunk_size: 每次读取的音频块大小
            channels: 声道数
        """
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.channels = channels
        
        self.stream = None
        self.is_recording = False
        self.audio_buffer = deque(maxlen=100)
        self.lock = threading.Lock()
        
        self._audio_module = None
        self._init_audio()
    
    def _init_audio(self):
        """初始化音频模块"""
        try:
            import sounddevice as sd
            self._audio_module = sd
            self._use_sounddevice = True
        except ImportError:
            try:
                import pyaudio
                self._audio_module = pyaudio
                self._use_pyaudio = True
            except ImportError:
                self._use_sounddevice = False
                self._use_pyaudio = False
    
    def start(self) -> bool:
        """
        开始录音
        
        Returns:
            是否成功开始录音
        """
        if self.is_recording:
            return True
        
        try:
            if self._use_sounddevice:
                return self._start_sounddevice()
            elif self._use_pyaudio:
                return self._start_pyaudio()
            else:
                return False
        except Exception as e:
            return False
    
    def _start_sounddevice(self) -> bool:
        """使用sounddevice开始录音"""
        import sounddevice as sd
        
        def callback(indata, frames, time_info, status):
            if status:
                pass
            with self.lock:
                self.audio_buffer.append(indata.flatten())
        
        try:
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                blocksize=self.chunk_size,
                callback=callback
            )
            self.stream.start()
            self.is_recording = True
            return True
        except Exception as e:
            return False
    
    def _start_pyaudio(self) -> bool:
        """使用pyaudio开始录音"""
        import pyaudio
        
        def callback(in_data, frame_count, time_info, status):
            if in_data:
                audio_data = np.frombuffer(in_data, dtype=np.float32)
                with self.lock:
                    self.audio_buffer.append(audio_data)
            return (in_data, pyaudio.paContinue)
        
        try:
            self._pyaudio = pyaudio.PyAudio()
            self.stream = self._pyaudio.open(
                format=pyaudio.paFloat32,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=callback
            )
            self.stream.start_stream()
            self.is_recording = True
            return True
        except Exception:
            return False
    
    def stop(self):
        """停止录音"""
        if not self.is_recording:
            return
        
        try:
            if self._use_sounddevice and self.stream:
                self.stream.stop()
                self.stream.close()
                self.stream = None
            elif self._use_pyaudio and self.stream:
                self.stream.stop_stream()
                self.stream.close()
                if hasattr(self, '_pyaudio'):
                    self._pyaudio.terminate()
                self.stream = None
        except Exception:
            pass
        
        self.is_recording = False
    
    def get_audio_chunk(self) -> Optional[np.ndarray]:
        """
        获取最近的音频数据
        
        Returns:
            音频数据，如果缓冲区为空则返回None
        """
        with self.lock:
            if len(self.audio_buffer) == 0:
                return None
            
            chunks = list(self.audio_buffer)
            return np.concatenate(chunks)
    
    def get_latest_chunk(self) -> Optional[np.ndarray]:
        """
        获取最新的单个音频块
        
        Returns:
            最新的音频数据块
        """
        with self.lock:
            if len(self.audio_buffer) == 0:
                return None
            return self.audio_buffer[-1].copy()
    
    def is_available(self) -> bool:
        """
        检查麦克风是否可用
        
        Returns:
            麦克风是否可用
        """
        if self._use_sounddevice:
            import sounddevice as sd
            try:
                return len(sd.query_devices()) > 0
            except Exception:
                return False
        elif self._use_pyaudio:
            import pyaudio
            try:
                p = pyaudio.PyAudio()
                count = p.get_device_count()
                p.terminate()
                return count > 0
            except Exception:
                return False
        return False
    
    def list_devices(self) -> list:
        """
        列出可用的音频输入设备
        
        Returns:
            设备列表
        """
        devices = []
        if self._use_sounddevice:
            import sounddevice as sd
            try:
                for dev in sd.query_devices():
                    if dev['max_input_channels'] > 0:
                        devices.append({
                            'name': dev['name'],
                            'channels': dev['max_input_channels'],
                            'sample_rate': dev['default_samplerate']
                        })
            except Exception:
                pass
        elif self._use_pyaudio:
            import pyaudio
            try:
                p = pyaudio.PyAudio()
                for i in range(p.get_device_count()):
                    info = p.get_device_info_by_index(i)
                    if info['maxInputChannels'] > 0:
                        devices.append({
                            'name': info['name'],
                            'channels': info['maxInputChannels'],
                            'sample_rate': int(info['defaultSampleRate'])
                        })
                p.terminate()
            except Exception:
                pass
        return devices


class MicrophoneFeatureGenerator:
    """麦克风实时特征生成器"""
    
    def __init__(
        self,
        sample_rate: int = 16000,
        update_rate: float = 60.0,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        初始化麦克风特征生成器
        
        Args:
            sample_rate: 采样率
            update_rate: 更新率（FPS）
            config: 特征提取配置
        """
        self.sample_rate = sample_rate
        self.update_rate = update_rate
        self.update_interval = 1.0 / update_rate
        
        self.config = config or {
            'window_size': 2048,
            'hop_size': 512,
            'n_fft': 2048,
            'n_mels': 128,
            'n_mfcc': 13
        }
        
        self.microphone = MicrophoneInput(
            sample_rate=sample_rate,
            chunk_size=self.config.get('chunk_size', 1024)
        )
        
        self.current_features: Optional[Dict[str, Any]] = None
        self.lock = threading.Lock()
        
        self.thread: Optional[threading.Thread] = None
        self.running = False
        
        self.on_update: Optional[Callable[[Dict[str, Any]], None]] = None
    
    def start(self) -> bool:
        """
        开始生成特征
        
        Returns:
            是否成功开始
        """
        if self.running:
            return True
        
        if not self.microphone.start():
            return False
        
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        return True
    
    def stop(self):
        """停止生成特征"""
        self.running = False
        self.microphone.stop()
        
        if self.thread:
            self.thread.join(timeout=1.0)
            self.thread = None
    
    def _run(self):
        """运行特征生成循环"""
        import librosa
        
        window_size = self.config.get('window_size', 2048)
        hop_size = self.config.get('hop_size', 512)
        n_fft = self.config.get('n_fft', 2048)
        n_mels = self.config.get('n_mels', 128)
        n_mfcc = self.config.get('n_mfcc', 13)
        
        audio_buffer = []
        buffer_duration = 0.5
        
        while self.running:
            chunk = self.microphone.get_latest_chunk()
            
            if chunk is not None:
                audio_buffer.append(chunk)
                
                total_samples = int(buffer_duration * self.sample_rate)
                
                if sum(len(c) for c in audio_buffer) >= window_size // 2:
                    y = np.concatenate(audio_buffer)
                    
                    if len(y) > total_samples:
                        y = y[-total_samples:]
                        audio_buffer = [y]
                    elif len(y) < window_size // 2:
                        continue
                    
                    try:
                        features = self._extract_features(
                            y, self.sample_rate,
                            window_size, hop_size, n_fft, n_mels, n_mfcc
                        )
                        
                        with self.lock:
                            self.current_features = features
                        
                        if self.on_update:
                            self.on_update(features)
                    except Exception:
                        pass
            
            time.sleep(self.update_interval)
    
    def _extract_features(
        self,
        y: np.ndarray,
        sr: int,
        window_size: int,
        hop_size: int,
        n_fft: int,
        n_mels: int,
        n_mfcc: int
    ) -> Dict[str, Any]:
        """提取音频特征"""
        import librosa
        
        features = {}
        
        y = y * 3.0
        
        loudness = librosa.feature.rms(
            y=y,
            frame_length=window_size,
            hop_length=hop_size
        )[0]
        features['temporal'] = {
            'loudness': loudness,
            'amplitude': np.abs(y)
        }
        
        mel_spec = librosa.feature.melspectrogram(
            y=y, sr=sr, n_fft=n_fft, hop_length=hop_size, n_mels=n_mels
        )
        log_mel_spec = librosa.power_to_db(mel_spec, ref=np.max)
        
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        window = 10
        beat_strength = np.zeros_like(onset_env)
        for i in range(len(onset_env)):
            start = max(0, i - window // 2)
            end = min(len(onset_env), i + window // 2 + 1)
            beat_strength[i] = np.max(onset_env[start:end])
        
        if np.max(beat_strength) > 0:
            beat_strength = beat_strength / np.max(beat_strength)
        
        features['frequency'] = {
            'mel_spectrogram': mel_spec,
            'log_mel_spectrogram': log_mel_spec,
            'spectrum': np.abs(librosa.stft(y, n_fft=n_fft, hop_length=hop_size))
        }
        
        features['rhythm'] = {
            'onset_envelope': onset_env,
            'beat_strength': beat_strength,
            'bpm': 0.0,
            'beat_frames': np.array([]),
            'beat_times': np.array([])
        }
        
        mfcc = librosa.feature.mfcc(
            y=y, sr=sr, n_mfcc=n_mfcc, n_fft=n_fft, hop_length=hop_size
        )
        spectral_centroid = librosa.feature.spectral_centroid(
            y=y, sr=sr, n_fft=n_fft, hop_length=hop_size
        )[0]
        
        features['timbre'] = {
            'mfcc': mfcc,
            'spectral_centroid': spectral_centroid,
            'spectral_bandwidth': librosa.feature.spectral_bandwidth(
                y=y, sr=sr, n_fft=n_fft, hop_length=hop_size
            )[0],
            'spectral_rolloff': librosa.feature.spectral_rolloff(
                y=y, sr=sr, n_fft=n_fft, hop_length=hop_size
            )[0]
        }
        
        return features
    
    def get_features(self) -> Optional[Dict[str, Any]]:
        """
        获取当前特征
        
        Returns:
            当前音频特征
        """
        with self.lock:
            return self.current_features.copy() if self.current_features else None
    
    def get_latest_features(self) -> Optional[Dict[str, Any]]:
        """
        获取最新的音频特征（与AudioFeatureGenerator兼容）
        
        Returns:
            最新的音频特征
        """
        return self.get_features()
