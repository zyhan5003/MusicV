import customtkinter as ctk
from typing import Dict, Any, Optional
from src.audio.data_visualizer import AudioDataVisualizer
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class DataPreviewPanel(ctk.CTkFrame):
    """数据预览面板"""

    def __init__(self, parent, **kwargs):
        """初始化数据预览面板"""
        super().__init__(parent, **kwargs)
        
        self.visualizer: Optional[AudioDataVisualizer] = None
        self.is_visible: bool = False
        self.chart_widgets: Dict[str, ctk.CTkFrame] = {}
        self.canvas_widgets: Dict[str, FigureCanvasTkAgg] = {}
        
        self._setup_ui()
        
    def _setup_ui(self):
        """设置用户界面"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # 标题栏
        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        header_frame.grid_columnconfigure(1, weight=1)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="音频数据预览",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=5, pady=5)
        
        # 显示/隐藏开关
        self.toggle_button = ctk.CTkButton(
            header_frame,
            text="隐藏",
            width=80,
            command=self._toggle_visibility
        )
        self.toggle_button.grid(row=0, column=1, padx=5, pady=5)
        
        # 切片窗口大小控制
        slice_frame = ctk.CTkFrame(header_frame)
        slice_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        slice_frame.grid_columnconfigure(1, weight=1)
        
        slice_label = ctk.CTkLabel(slice_frame, text="切片窗口:")
        slice_label.grid(row=0, column=0, padx=5, pady=5)
        
        self.slice_slider = ctk.CTkSlider(
            slice_frame,
            from_=10,
            to=500,
            number_of_steps=49,
            command=self._on_slice_window_change
        )
        self.slice_slider.set(100)
        self.slice_slider.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        self.slice_value = ctk.CTkLabel(slice_frame, text="100")
        self.slice_value.grid(row=0, column=2, padx=5, pady=5)
        
        # 图表容器
        self.charts_container = ctk.CTkScrollableFrame(self)
        self.charts_container.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # 初始化图表框架
        self._init_chart_frames()
        
    def _init_chart_frames(self):
        """初始化图表框架"""
        chart_configs = [
            ("时域特征", "temporal"),
            ("频域特征", "frequency"),
            ("节奏特征", "rhythm"),
            ("音色特征", "timbre")
        ]
        
        for title, category in chart_configs:
            frame = ctk.CTkFrame(self.charts_container)
            frame.pack(fill="x", padx=5, pady=5)
            
            label = ctk.CTkLabel(
                frame,
                text=title,
                font=ctk.CTkFont(size=12, weight="bold")
            )
            label.pack(padx=5, pady=5)
            
            self.chart_widgets[category] = frame
            
    def set_visualizer(self, visualizer: AudioDataVisualizer) -> None:
        """设置可视化器"""
        self.visualizer = visualizer
        self._create_charts()
        
    def _create_charts(self) -> None:
        """创建图表"""
        if self.visualizer is None:
            return
            
        features = self.visualizer.features
        
        # 时域特征图表
        if "temporal" in features:
            self._create_temporal_charts(features["temporal"])
        
        # 频域特征图表
        if "frequency" in features:
            self._create_frequency_charts(features["frequency"])
        
        # 节奏特征图表
        if "rhythm" in features:
            self._create_rhythm_charts(features["rhythm"])
        
        # 音色特征图表
        if "timbre" in features:
            self._create_timbre_charts(features["timbre"])
            
    def _create_temporal_charts(self, features: Dict[str, Any]) -> None:
        """创建时域特征图表"""
        frame = self.chart_widgets.get("temporal")
        if frame is None:
            return
            
        # 振幅曲线图
        if "amplitude" in features:
            amplitude = features["amplitude"]
            # 降采样以避免显示过多数据点
            if len(amplitude) > 10000:
                step = len(amplitude) // 10000
                amplitude = amplitude[::step]
            self._add_chart_to_frame(
                frame,
                "amplitude",
                "振幅",
                amplitude,
                "line",
                "cyan"
            )
            
        # 音量曲线图
        if "loudness" in features:
            self._add_chart_to_frame(
                frame,
                "loudness",
                "音量",
                features["loudness"],
                "line",
                "blue"
            )
        
        # 过零率曲线图
        if "zero_crossing_rate" in features:
            self._add_chart_to_frame(
                frame,
                "zero_crossing_rate",
                "过零率",
                features["zero_crossing_rate"],
                "line",
                "green"
            )
            
    def _create_frequency_charts(self, features: Dict[str, Any]) -> None:
        """创建频域特征图表"""
        frame = self.chart_widgets.get("frequency")
        if frame is None:
            return
            
        # 频谱质心曲线图
        if "spectral_centroid" in features:
            self._add_chart_to_frame(
                frame,
                "spectral_centroid",
                "频谱质心",
                features["spectral_centroid"],
                "line",
                "purple"
            )
        
        # 频谱带宽曲线图
        if "spectral_bandwidth" in features:
            self._add_chart_to_frame(
                frame,
                "spectral_bandwidth",
                "频谱带宽",
                features["spectral_bandwidth"],
                "line",
                "orange"
            )
            
        # 频谱滚降曲线图
        if "spectral_rolloff" in features:
            self._add_chart_to_frame(
                frame,
                "spectral_rolloff",
                "频谱滚降",
                features["spectral_rolloff"],
                "line",
                "pink"
            )
            
    def _create_rhythm_charts(self, features: Dict[str, Any]) -> None:
        """创建节奏特征图表"""
        frame = self.chart_widgets.get("rhythm")
        if frame is None:
            return
            
        # 节拍强度柱状图
        if "beat_strength" in features:
            self._add_chart_to_frame(
                frame,
                "beat_strength",
                "节拍强度",
                features["beat_strength"],
                "bar",
                "red"
            )
        
        # onset_envelope曲线图
        if "onset_envelope" in features:
            self._add_chart_to_frame(
                frame,
                "onset_envelope",
                "起音包络",
                features["onset_envelope"],
                "line",
                "yellow"
            )
            
    def _create_timbre_charts(self, features: Dict[str, Any]) -> None:
        """创建音色特征图表"""
        frame = self.chart_widgets.get("timbre")
        if frame is None:
            return
            
        # 频谱图
        if "spectrum" in features:
            self._add_spectrum_chart(
                frame,
                "spectrum",
                "频谱",
                features["spectrum"]
            )
            
        # 梅尔频谱图
        if "mel_spectrogram" in features:
            self._add_spectrum_chart(
                frame,
                "mel_spectrogram",
                "梅尔频谱",
                features["mel_spectrogram"]
            )
            
        # 对数梅尔频谱图
        if "log_mel_spectrogram" in features:
            self._add_spectrum_chart(
                frame,
                "log_mel_spectrogram",
                "对数梅尔频谱",
                features["log_mel_spectrogram"]
            )
            
        # MFCC图
        if "mfcc" in features:
            self._add_spectrum_chart(
                frame,
                "mfcc",
                "MFCC",
                features["mfcc"]
            )
            
    def _add_chart_to_frame(self, frame: ctk.CTkFrame, name: str, title: str, 
                          data: Any, chart_type: str, color: str) -> None:
        """添加图表到框架"""
        if self.visualizer is None:
            return
            
        chart_frame = ctk.CTkFrame(frame)
        chart_frame.pack(fill="x", padx=5, pady=5)
        
        # 创建图表
        if chart_type == "line":
            fig = self.visualizer.create_line_plot(
                name,
                data,
                title,
                "值",
                color
            )
        elif chart_type == "bar":
            fig = self.visualizer.create_bar_plot(
                name,
                data,
                title,
                "值",
                color
            )
        else:
            return
            
        # 创建canvas
        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        self.canvas_widgets[name] = canvas
        self.visualizer.figures[name] = fig
        self.visualizer.canvases[name] = canvas
        
    def _add_spectrum_chart(self, frame: ctk.CTkFrame, name: str, 
                          title: str, data: Any) -> None:
        """添加频谱图到框架"""
        if self.visualizer is None:
            return
            
        chart_frame = ctk.CTkFrame(frame)
        chart_frame.pack(fill="x", padx=5, pady=5)
        
        fig = self.visualizer.create_spectrum_plot(name, data, title)
        
        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        self.canvas_widgets[name] = canvas
        self.visualizer.figures[name] = fig
        self.visualizer.canvases[name] = canvas
        
    def update_charts(self, current_frame: int) -> None:
        """更新图表"""
        if self.visualizer is None or not self.is_visible:
            return
            
        self.visualizer.set_current_frame(current_frame)
        features = self.visualizer.features
        
        # 更新时域特征图表
        if "temporal" in features:
            if "amplitude" in features["temporal"]:
                self.visualizer.update_line_plot("amplitude", features["temporal"]["amplitude"])
            if "loudness" in features["temporal"]:
                self.visualizer.update_line_plot("loudness", features["temporal"]["loudness"])
            if "zero_crossing_rate" in features["temporal"]:
                self.visualizer.update_line_plot("zero_crossing_rate", features["temporal"]["zero_crossing_rate"])
        
        # 更新频域特征图表
        if "frequency" in features:
            if "spectral_centroid" in features["frequency"]:
                self.visualizer.update_line_plot("spectral_centroid", features["frequency"]["spectral_centroid"])
            if "spectral_bandwidth" in features["frequency"]:
                self.visualizer.update_line_plot("spectral_bandwidth", features["frequency"]["spectral_bandwidth"])
            if "spectral_rolloff" in features["frequency"]:
                self.visualizer.update_line_plot("spectral_rolloff", features["frequency"]["spectral_rolloff"])
        
        # 更新节奏特征图表
        if "rhythm" in features:
            if "beat_strength" in features["rhythm"]:
                self.visualizer.update_bar_plot("beat_strength", features["rhythm"]["beat_strength"])
            if "onset_envelope" in features["rhythm"]:
                self.visualizer.update_line_plot("onset_envelope", features["rhythm"]["onset_envelope"])
        
        # 更新音色特征图表
        if "timbre" in features:
            if "spectrum" in features["timbre"]:
                self.visualizer.update_spectrum_plot("spectrum", features["timbre"]["spectrum"])
            if "mel_spectrogram" in features["timbre"]:
                self.visualizer.update_spectrum_plot("mel_spectrogram", features["timbre"]["mel_spectrogram"])
            if "log_mel_spectrogram" in features["timbre"]:
                self.visualizer.update_spectrum_plot("log_mel_spectrogram", features["timbre"]["log_mel_spectrogram"])
            if "mfcc" in features["timbre"]:
                self.visualizer.update_spectrum_plot("mfcc", features["timbre"]["mfcc"])
                
    def _toggle_visibility(self) -> None:
        """切换可见性"""
        self.is_visible = not self.is_visible
        
        if self.is_visible:
            self.charts_container.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
            self.toggle_button.configure(text="隐藏")
        else:
            self.charts_container.grid_forget()
            self.toggle_button.configure(text="显示")
            
    def _on_slice_window_change(self, value: float) -> None:
        """切片窗口大小变更处理"""
        window = int(value)
        self.slice_value.configure(text=str(window))
        if self.visualizer is not None:
            self.visualizer.set_slice_window(window)
            
    def clear_charts(self) -> None:
        """清除图表"""
        if self.visualizer is not None:
            self.visualizer.clear_all()
            
        for canvas in self.canvas_widgets.values():
            canvas.get_tk_widget().destroy()
            
        self.canvas_widgets.clear()
        
        # 重新初始化图表框架
        for frame in self.chart_widgets.values():
            for widget in frame.winfo_children():
                widget.destroy()