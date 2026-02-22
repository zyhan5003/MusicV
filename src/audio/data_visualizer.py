from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import customtkinter as ctk

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题


class AudioDataVisualizer:
    """音频数据可视化器"""

    def __init__(self, parent: ctk.CTk):
        """初始化音频数据可视化器"""
        self.parent = parent
        self.features: Dict[str, Any] = {}
        self.current_frame: int = 0
        self.total_frames: int = 0
        self.slice_window: int = 100
        self.figures: Dict[str, Figure] = {}
        self.canvases: Dict[str, FigureCanvasTkAgg] = {}
        self.lines: Dict[str, List] = {}
        self.bars: Dict[str, List] = {}
        
        # 性能优化：更新频率控制
        self.last_update_time = 0
        self.update_interval = 0.2  # 更新间隔（秒），即每秒5次（降低更新频率）
        
        # 图表显示控制
        self.enabled_charts: Dict[str, bool] = {
            "loudness": True,
            "zero_crossing_rate": True,
            "spectrum": True,
            "beat_strength": True,
            "onset_envelope": True,
            "spectral_centroid": True,
            "spectral_bandwidth": True
        }
        
    def load_features(self, features: Dict[str, Any]) -> None:
        """加载音频特征数据"""
        self.features = features
        
        # 计算总帧数 - 遍历所有特征，找到最长的特征长度
        # 优先使用时域特征（loudness, zero_crossing_rate）作为总帧数
        self.total_frames = 0
        
        # 优先检查时域特征
        if "temporal" in features:
            for feature_name in ["loudness", "zero_crossing_rate"]:
                if feature_name in features["temporal"]:
                    feature_data = features["temporal"][feature_name]
                    if isinstance(feature_data, np.ndarray) and feature_data.ndim == 1:
                        self.total_frames = max(self.total_frames, len(feature_data))
        
        # 如果没有找到时域特征，检查其他特征
        if self.total_frames == 0:
            for category in features.values():
                if isinstance(category, dict):
                    for feature_name, feature_data in category.items():
                        if isinstance(feature_data, np.ndarray):
                            if feature_data.ndim == 1:
                                # 一维数组（可能是特征帧）
                                self.total_frames = max(self.total_frames, len(feature_data))
                            elif feature_data.ndim == 2:
                                # 二维数组，使用第二个维度（时间维度）
                                self.total_frames = max(self.total_frames, feature_data.shape[1])
        
        if self.total_frames == 0:
            print("警告: 无法确定总帧数")
        
        self.current_frame = 0
        
    def set_current_frame(self, frame: int) -> None:
        """设置当前播放帧"""
        self.current_frame = max(0, min(frame, self.total_frames - 1))
        
    def set_slice_window(self, window: int) -> None:
        """设置切片窗口大小"""
        self.slice_window = max(10, window)
        
    def get_slice_range(self) -> Tuple[int, int]:
        """获取当前切片范围"""
        start = max(0, self.current_frame - self.slice_window)
        end = min(self.total_frames, self.current_frame + self.slice_window)
        return start, end
        
    def create_line_plot(self, name: str, data: np.ndarray, title: str, ylabel: str, color: str = 'blue') -> Figure:
        """创建曲线图"""
        fig = Figure(figsize=(5, 2), dpi=100)
        ax = fig.add_subplot(111)
        
        # 对于amplitude数据，使用不同的处理方式
        if name == "amplitude":
            # amplitude数据通常很长，我们只显示初始窗口的数据
            window_size = 1000
            if len(data) > window_size:
                x = np.arange(window_size)
                y = data[:window_size]
            else:
                x = np.arange(len(data))
                y = data
        else:
            # 对于其他特征数据，使用切片窗口
            start, end = self.get_slice_range()
            x = np.arange(start, end)
            # 确保不超出数据范围
            end = min(end, len(data))
            y = data[start:end]
            # 调整x的长度以匹配y
            x = x[:len(y)]
        
        line, = ax.plot(x, y, color=color, linewidth=1)
        ax.set_title(title, fontsize=8)
        ax.set_ylabel(ylabel, fontsize=7)
        ax.set_xlabel('帧', fontsize=7)
        ax.tick_params(axis='both', which='major', labelsize=6)
        ax.grid(True, alpha=0.3)
        
        # 保存line对象以便后续更新
        self.lines[name] = [line]
        
        # 添加当前帧指示线
        if name == "amplitude":
            # 对于amplitude，指示线显示在初始位置
            ax.axvline(x=0, color='red', linestyle='--', linewidth=1, alpha=0.8)
        else:
            if start <= self.current_frame < end:
                ax.axvline(x=self.current_frame, color='red', linestyle='--', linewidth=1, alpha=0.8)
        
        fig.tight_layout()
        return fig
        
    def create_bar_plot(self, name: str, data: np.ndarray, title: str, ylabel: str, color: str = 'blue') -> Figure:
        """创建柱状图"""
        fig = Figure(figsize=(5, 2), dpi=100)
        ax = fig.add_subplot(111)
        
        start, end = self.get_slice_range()
        x = np.arange(start, end)
        y = data[start:end]
        
        # 确保x和y长度一致
        min_len = min(len(x), len(y))
        x = x[:min_len]
        y = y[:min_len]
        
        # 限制显示的柱子数量
        max_bars = 50
        if len(x) > max_bars:
            step = len(x) // max_bars
            x = x[::step]
            y = y[::step]
        
        # 动态计算柱状图宽度
        if len(x) > 1:
            bar_width = max(1.0, (x[1] - x[0]) * 0.8)
        else:
            bar_width = 1.0
        
        # 确保bar_width是标量
        if isinstance(bar_width, np.ndarray):
            bar_width = float(bar_width.item())
        
        bars = ax.bar(x, y, color=color, alpha=0.7, width=bar_width)
        ax.set_title(title, fontsize=8)
        ax.set_ylabel(ylabel, fontsize=7)
        ax.set_xlabel('帧', fontsize=7)
        ax.tick_params(axis='both', which='major', labelsize=6)
        ax.grid(True, alpha=0.3)
        
        # 保存bars对象以便后续更新
        self.bars[name] = bars
        
        # 添加当前帧指示线
        if start <= self.current_frame < end:
            ax.axvline(x=self.current_frame, color='red', linestyle='--', linewidth=1, alpha=0.8)
        
        fig.tight_layout()
        return fig
        
    def create_spectrum_plot(self, name: str, data: np.ndarray, title: str) -> Figure:
        """创建频谱图"""
        fig = Figure(figsize=(5, 2), dpi=100)
        ax = fig.add_subplot(111)
        
        # 获取当前帧的频谱
        if self.current_frame < data.shape[1]:
            spectrum = data[:, self.current_frame]
            x = np.arange(len(spectrum))
            
            line, = ax.plot(x, spectrum, color='purple', linewidth=1)
            ax.set_title(title, fontsize=8)
            ax.set_ylabel('幅度', fontsize=7)
            ax.set_xlabel('频率', fontsize=7)
            ax.tick_params(axis='both', which='major', labelsize=6)
            ax.grid(True, alpha=0.3)
            ax.fill_between(x, spectrum, alpha=0.3, color='purple')
            
            # 保存line对象以便后续更新
            self.lines[name] = [line]
        
        fig.tight_layout()
        return fig
        
    def update_line_plot(self, name: str, data: np.ndarray) -> None:
        """更新曲线图"""
        if name not in self.figures:
            return
            
        fig = self.figures[name]
        ax = fig.axes[0]
        
        # 对于amplitude数据，使用不同的处理方式
        if name == "amplitude":
            # amplitude数据通常很长，我们只显示当前帧附近的数据
            window_size = 1000
            if len(data) > window_size:
                # 计算当前帧对应的样本位置
                current_sample = self.current_frame * 512  # hop_length
                start = max(0, current_sample - window_size // 2)
                end = min(len(data), start + window_size)
                x = np.arange(start, end)
                y = data[start:end]
            else:
                x = np.arange(len(data))
                y = data
        else:
            # 对于其他特征数据，使用切片窗口
            start, end = self.get_slice_range()
            x = np.arange(start, end)
            # 确保不超出数据范围
            end = min(end, len(data))
            y = data[start:end]
            # 调整x的长度以匹配y
            x = x[:len(y)]
        
        if name in self.lines and len(self.lines[name]) > 0:
            line = self.lines[name][0]
            line.set_data(x, y)
            
            # 更新坐标轴范围
            if name == "amplitude":
                ax.set_xlim(x[0], x[-1])
            else:
                ax.set_xlim(start, end)
            
            # 动态调整y轴范围
            if len(y) > 0:
                y_min, y_max = np.min(y), np.max(y)
                if y_max > y_min:
                    margin = (y_max - y_min) * 0.1
                    ax.set_ylim(y_min - margin, y_max + margin)
                else:
                    ax.set_ylim(y_min - 1, y_max + 1)
        
        # 更新当前帧指示线
        for line in ax.lines:
            if line.get_linestyle() == '--':
                if name == "amplitude":
                    # 对于amplitude，指示线显示在当前样本位置
                    current_sample = self.current_frame * 512
                    line.set_xdata([current_sample, current_sample])
                else:
                    line.set_xdata([self.current_frame, self.current_frame])
        
        # 强制重绘 - 使用更高效的方式
        self.canvases[name].draw_idle()
        # 不再强制更新GUI，让Tkinter自动处理
        
    def update_bar_plot(self, name: str, data: np.ndarray) -> None:
        """更新柱状图"""
        if name not in self.figures:
            return
            
        fig = self.figures[name]
        ax = fig.axes[0]
        
        start, end = self.get_slice_range()
        x = np.arange(start, end)
        y = data[start:end]
        
        # 确保x和y长度一致
        min_len = min(len(x), len(y))
        x = x[:min_len]
        y = y[:min_len]
        
        # 限制显示的柱子数量
        max_bars = 50
        if len(x) > max_bars:
            step = len(x) // max_bars
            x = x[::step]
            y = y[::step]
        
        # 动态计算柱状图宽度
        if len(x) > 1:
            bar_width = max(1.0, (x[1] - x[0]) * 0.8)
        else:
            bar_width = 1.0
        
        # 确保bar_width是标量
        if isinstance(bar_width, np.ndarray):
            bar_width = float(bar_width.item())
        
        if name in self.bars and len(self.bars[name]) > 0:
            for bar in self.bars[name]:
                bar.remove()
            
            bars = ax.bar(x, y, color='blue', alpha=0.7, width=bar_width)
            self.bars[name] = bars
            ax.set_xlim(start, end)
            
            # 动态调整y轴范围
            if len(y) > 0:
                y_min, y_max = np.min(y), np.max(y)
                if y_max > y_min:
                    margin = (y_max - y_min) * 0.1
                    ax.set_ylim(y_min - margin, y_max + margin)
                else:
                    ax.set_ylim(y_min - 1, y_max + 1)
        
        # 更新当前帧指示线
        for line in ax.lines:
            if line.get_linestyle() == '--':
                line.set_xdata([self.current_frame, self.current_frame])
        
        # 强制重绘 - 使用更高效的方式
        self.canvases[name].draw_idle()
        # 不再强制更新GUI，让Tkinter自动处理
        
    def update_spectrum_plot(self, name: str, data: np.ndarray) -> None:
        """更新频谱图"""
        if name not in self.figures:
            return
            
        fig = self.figures[name]
        ax = fig.axes[0]
        
        # 检查数据维度
        if data.ndim == 1:
            # 一维数据，直接显示
            x = np.arange(len(data))
            spectrum = data
        elif data.ndim == 2:
            # 二维数据，显示当前帧
            if self.current_frame < data.shape[1]:
                spectrum = data[:, self.current_frame]
                x = np.arange(len(spectrum))
            else:
                return
        else:
            return
        
        if name in self.lines and len(self.lines[name]) > 0:
            line = self.lines[name][0]
            line.set_data(x, spectrum)
            
            # 动态调整y轴范围
            if len(spectrum) > 0:
                y_min, y_max = np.min(spectrum), np.max(spectrum)
                if y_max > y_min:
                    margin = (y_max - y_min) * 0.1
                    ax.set_ylim(y_min - margin, y_max + margin)
                else:
                    ax.set_ylim(y_min - 1, y_max + 1)
            
            # 更新填充区域
            for collection in ax.collections:
                collection.remove()
            ax.fill_between(x, spectrum, alpha=0.3, color='purple')
        
        # 强制重绘 - 使用更高效的方式
        self.canvases[name].draw_idle()
        # 不再强制更新GUI，让Tkinter自动处理
        
    def clear_all(self) -> None:
        """清除所有图表"""
        for canvas in self.canvases.values():
            canvas.get_tk_widget().destroy()
        self.figures.clear()
        self.canvases.clear()
        self.lines.clear()
        self.bars.clear()