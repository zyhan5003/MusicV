import customtkinter as ctk
from typing import Dict, Any, Optional
import numpy as np
from src.audio.data_visualizer import AudioDataVisualizer


class DataPreviewWindow(ctk.CTkToplevel):
    """独立的数据预览窗口 - 简洁风格"""

    def __init__(self, parent, **kwargs):
        """初始化数据预览窗口"""
        super().__init__(parent, **kwargs)
        
        self.title("音频数据预览")
        self.geometry("600x400")
        
        self.visualizer: Optional[AudioDataVisualizer] = None
        self.is_visible: bool = True
        
        # 数据显示控件
        self.data_labels: Dict[str, ctk.CTkLabel] = {}
        self.data_progress_bars: Dict[str, ctk.CTkProgressBar] = {}
        
        # 窗口关闭时通知父窗口
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        self._setup_ui()
        
    def _setup_ui(self):
        """设置用户界面 - 简洁风格"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # 标题栏
        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="音频数据预览",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=5)
        
        # 数据容器
        self.data_container = ctk.CTkScrollableFrame(self)
        self.data_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
    def set_visualizer(self, visualizer: AudioDataVisualizer) -> None:
        """设置可视化器"""
        self.visualizer = visualizer
        
    def _create_data_display(self) -> None:
        """创建数据显示 - 简洁风格"""
        if self.visualizer is None:
            return
            
        features = self.visualizer.features
        
        # 清除旧控件
        self._clear_old_widgets()
        
        # 创建分类框架
        categories = [
            ("时域特征", "temporal"),
            ("频域特征", "frequency"),
            ("节奏特征", "rhythm"),
            ("音色特征", "timbre")
        ]
        
        for category_name, category_key in categories:
            if category_key not in features:
                continue
            
            # 创建分类标题
            category_frame = ctk.CTkFrame(self.data_container)
            category_frame.pack(fill="x", padx=5, pady=5)
            
            category_label = ctk.CTkLabel(
                category_frame,
                text=category_name,
                font=ctk.CTkFont(size=12, weight="bold"),
                anchor="w"
            )
            category_label.pack(fill="x", padx=10, pady=5)
            
            # 创建数据项
            self._create_data_items(category_frame, category_key, features[category_key])
    
    def _create_data_items(self, parent_frame: ctk.CTkFrame, category_key: str, category_features: Dict[str, Any]) -> None:
        """创建数据项"""
        # 定义每个分类的数据项
        data_items = {
            "temporal": [
                ("音量", "loudness", 0.0, 1.0),
                ("过零率", "zero_crossing_rate", 0.0, 0.5)
            ],
            "frequency": [
                ("频谱能量", "spectrum", 0.0, 20.0),
                ("梅尔能量", "mel_spectrogram", 0.0, 30.0)
            ],
            "rhythm": [
                ("BPM", "bpm", 60.0, 200.0),
                ("节拍强度", "beat_strength", 0.0, 10.0),
                ("起音包络", "onset_envelope", 0.0, 10.0)
            ],
            "timbre": [
                ("谱质心", "spectral_centroid", 0.0, 5000.0),
                ("谱带宽", "spectral_bandwidth", 0.0, 3000.0)
            ]
        }
        
        if category_key not in data_items:
            return
        
        for label_text, feature_name, min_val, max_val in data_items[category_key]:
            if feature_name not in category_features:
                continue
            
            # 创建数据项框架
            item_frame = ctk.CTkFrame(parent_frame)
            item_frame.pack(fill="x", padx=10, pady=2)
            
            # 标签
            label = ctk.CTkLabel(
                item_frame,
                text=label_text + ":",
                width=80,
                anchor="e",
                font=ctk.CTkFont(size=10)
            )
            label.pack(side="left", padx=5)
            
            # 数值显示
            value_label = ctk.CTkLabel(
                item_frame,
                text="0.00",
                width=80,
                anchor="e",
                font=ctk.CTkFont(size=10, family="Courier")
            )
            value_label.pack(side="left", padx=5)
            
            # 进度条
            progress_bar = ctk.CTkProgressBar(
                item_frame,
                width=200,
                height=10
            )
            progress_bar.pack(side="left", padx=5)
            
            # 保存控件引用
            self.data_labels[feature_name] = value_label
            self.data_progress_bars[feature_name] = progress_bar
            
            # 保存特征数据
            setattr(self, f"{feature_name}_data", category_features[feature_name])
            setattr(self, f"{feature_name}_min", min_val)
            setattr(self, f"{feature_name}_max", max_val)
    
    def _clear_old_widgets(self) -> None:
        """清除旧控件"""
        for widget in self.data_container.winfo_children():
            widget.destroy()
        self.data_labels.clear()
        self.data_progress_bars.clear()
    
    def update_data_display(self, current_frame: int) -> None:
        """更新数据显示"""
        if self.visualizer is None or not self.is_visible:
            return
            
        features = self.visualizer.features
        
        # 更新每个数据项
        for feature_name in self.data_labels:
            if feature_name not in self.data_progress_bars:
                continue
            
            # 获取特征数据
            feature_data = self._get_feature_data(features, feature_name, current_frame)
            if feature_data is None:
                continue
            
            # 更新数值显示
            value_label = self.data_labels[feature_name]
            value_label.configure(text=f"{feature_data:.2f}")
            
            # 更新进度条
            progress_bar = self.data_progress_bars[feature_name]
            min_val = getattr(self, f"{feature_name}_min", 0.0)
            max_val = getattr(self, f"{feature_name}_max", 1.0)
            
            # 归一化到0-1范围
            normalized_value = (feature_data - min_val) / (max_val - min_val) if max_val > min_val else 0.0
            normalized_value = max(0.0, min(1.0, normalized_value))
            
            progress_bar.set(normalized_value)
    
    def _get_feature_data(self, features: Dict[str, Any], feature_name: str, current_frame: int) -> Optional[float]:
        """获取特征数据"""
        # 时域特征
        if "temporal" in features and feature_name in features["temporal"]:
            data = features["temporal"][feature_name]
            if isinstance(data, np.ndarray) and len(data) > 0:
                if current_frame < len(data):
                    return float(data[current_frame])
                else:
                    return float(np.mean(data))
        
        # 频域特征
        if "frequency" in features and feature_name in features["frequency"]:
            data = features["frequency"][feature_name]
            if isinstance(data, np.ndarray):
                if data.ndim == 1:
                    if current_frame < len(data):
                        return float(data[current_frame])
                    else:
                        return float(np.mean(data))
                elif data.ndim == 2:
                    if current_frame < data.shape[1]:
                        return float(np.mean(data[:, current_frame]))
                    else:
                        return float(np.mean(data))
        
        # 节奏特征
        if "rhythm" in features and feature_name in features["rhythm"]:
            data = features["rhythm"][feature_name]
            if isinstance(data, (int, float)):
                return float(data)
            elif isinstance(data, np.ndarray) and len(data) > 0:
                if current_frame < len(data):
                    return float(data[current_frame])
                else:
                    return float(np.mean(data))
        
        # 音色特征
        if "timbre" in features and feature_name in features["timbre"]:
            data = features["timbre"][feature_name]
            if isinstance(data, np.ndarray) and len(data) > 0:
                if current_frame < len(data):
                    return float(data[current_frame])
                else:
                    return float(np.mean(data))
        
        return None
    
    def show_window(self) -> None:
        """显示窗口"""
        self.is_visible = True
        self.deiconify()
        self.lift()
    
    def hide_window(self) -> None:
        """隐藏窗口"""
        self.is_visible = False
        self.withdraw()
    
    def _on_close(self) -> None:
        """窗口关闭处理"""
        self.is_visible = False
        self.withdraw()
    
    def _create_charts(self) -> None:
        """创建图表 - 重新实现为简洁风格"""
        if self.visualizer is None:
            return
            
        self._create_data_display()
    
    def update_charts(self, current_frame: int) -> None:
        """更新图表 - 重新实现为简洁风格"""
        self.update_data_display(current_frame)