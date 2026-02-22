import customtkinter as ctk
import threading
import pygame
import time
from typing import Dict, Any
from src.core.main import MusicV
from src.core.config_manager import ConfigManager
from src.gui.data_preview_window import DataPreviewWindow
from src.audio.data_visualizer import AudioDataVisualizer
from src.utils.file_history_manager import FileHistoryManager


class MainWindow(ctk.CTk):
    """主窗口类"""

    def __init__(self):
        """初始化主窗口"""
        super().__init__()

        self.title("MusicV - 音乐可视化")
        self.geometry("800x600")
        
        # pygame事件处理定时器
        self.pygame_event_timer = None

        self.config_manager = ConfigManager()
        self.musicv = MusicV()
        self.musicv.set_config(self.config_manager.config)
        
        # 初始化文件历史记录管理器
        self.file_history_manager = FileHistoryManager()
        
        # 初始化数据可视化器
        self.data_visualizer = AudioDataVisualizer(self)
        # 初始化独立的数据预览窗口
        self.data_preview_window = DataPreviewWindow(self)
        self.data_preview_window.set_visualizer(self.data_visualizer)
        self.data_preview_window.hide_window()  # 初始隐藏

        self._setup_ui()

    def _setup_ui(self):
        """设置用户界面"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 创建主框架
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        # 标题
        title_label = ctk.CTkLabel(
            main_frame,
            text="MusicV - 音乐可视化系统",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 20))

        # 控制面板
        control_frame = ctk.CTkFrame(main_frame)
        control_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        control_frame.grid_columnconfigure(0, weight=1)

        # 音频文件选择
        file_frame = ctk.CTkFrame(control_frame)
        file_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        file_frame.grid_columnconfigure(0, weight=1)

        # 第一行：文件标签和输入框
        file_label = ctk.CTkLabel(file_frame, text="音频文件:")
        file_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.file_entry = ctk.CTkEntry(file_frame, placeholder_text="选择音频文件...")
        self.file_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        browse_button = ctk.CTkButton(
            file_frame,
            text="浏览",
            command=self._browse_file,
            width=80
        )
        browse_button.grid(row=0, column=2, padx=5, pady=5)

        # 第二行：历史记录
        history_label = ctk.CTkLabel(file_frame, text="历史记录:")
        history_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.history_menu = ctk.CTkOptionMenu(
            file_frame,
            values=[],
            command=self._on_history_select
        )
        self.history_menu.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        
        # 更新历史记录列表
        self._update_history_menu()

        # 可视化类型选择（分类展示）
        visual_frame = ctk.CTkFrame(control_frame)
        visual_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        visual_frame.grid_columnconfigure(1, weight=1)

        visual_label = ctk.CTkLabel(visual_frame, text="可视化类型:")
        visual_label.grid(row=0, column=0, padx=5, pady=5)

        # 分类展示的可视化类型
        self.visual_categories = {
            "2D可视化": ["waveform", "spectrum", "equalizer"],
            "3D可视化": ["spectrum_cube", "3d_model"],
            "粒子系统": ["particles", "beat_particles", "jumping_particles", "style_aware_particles"],
            "特效系统": ["rain", "fire", "snow", "petal", "glowing_squares"],
            "信息显示": ["info_display"],
            "综合可视化": ["comprehensive"]
        }

        # 创建扁平化的选项列表，格式为"分类 - 名称"
        visual_options = []
        for category, types in self.visual_categories.items():
            for visual_type in types:
                visual_options.append(f"{category} - {visual_type}")

        self.visual_type_menu = ctk.CTkOptionMenu(
            visual_frame,
            values=visual_options,
            command=self._on_visual_type_change
        )
        self.visual_type_menu.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # 模式选择
        pattern_frame = ctk.CTkFrame(control_frame)
        pattern_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        pattern_frame.grid_columnconfigure(1, weight=1)

        pattern_label = ctk.CTkLabel(pattern_frame, text="运动模式:")
        pattern_label.grid(row=0, column=0, padx=5, pady=5)

        # 模式选项（将根据当前特效类型动态更新）
        self.pattern_options = {
            "默认模式": "default"
        }

        pattern_values = list(self.pattern_options.keys())
        self.pattern_menu = ctk.CTkOptionMenu(
            pattern_frame,
            values=pattern_values,
            command=self._on_pattern_change
        )
        self.pattern_menu.set("默认模式")
        self.pattern_menu.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # 当前模式显示
        self.current_pattern_label = ctk.CTkLabel(
            pattern_frame,
            text="当前模式: 默认",
            font=ctk.CTkFont(size=12)
        )
        self.current_pattern_label.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        # 粒子数量控制
        particle_frame = ctk.CTkFrame(control_frame)
        particle_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        particle_frame.grid_columnconfigure(1, weight=1)

        particle_label = ctk.CTkLabel(particle_frame, text="粒子数量:")
        particle_label.grid(row=0, column=0, padx=5, pady=5)

        self.particle_slider = ctk.CTkSlider(
            particle_frame,
            from_=100,
            to=5000,
            number_of_steps=49,
            command=self._on_particle_count_change
        )
        self.particle_slider.set(1000)
        self.particle_slider.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.particle_count_value = ctk.CTkLabel(particle_frame, text="1000")
        self.particle_count_value.grid(row=0, column=2, padx=5, pady=5)

        # 帧率控制
        fps_frame = ctk.CTkFrame(control_frame)
        fps_frame.grid(row=4, column=0, sticky="ew", padx=5, pady=5)
        fps_frame.grid_columnconfigure(1, weight=1)

        fps_label = ctk.CTkLabel(fps_frame, text="帧率:")
        fps_label.grid(row=0, column=0, padx=5, pady=5)

        self.fps_slider = ctk.CTkSlider(
            fps_frame,
            from_=15,
            to=60,
            number_of_steps=45,
            command=self._on_fps_change
        )
        self.fps_slider.set(30)
        self.fps_slider.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.fps_value = ctk.CTkLabel(fps_frame, text="30")
        self.fps_value.grid(row=0, column=2, padx=5, pady=5)

        # 按钮面板
        button_frame = ctk.CTkFrame(control_frame)
        button_frame.grid(row=5, column=0, sticky="ew", padx=5, pady=5)

        self.start_button = ctk.CTkButton(
            button_frame,
            text="开始可视化",
            command=self._start_visualization,
            fg_color="green"
        )
        self.start_button.grid(row=0, column=0, padx=5, pady=5)

        self.stop_button = ctk.CTkButton(
            button_frame,
            text="停止可视化",
            command=self._stop_visualization,
            fg_color="red"
        )
        self.stop_button.grid(row=0, column=1, padx=5, pady=5)
        
        # 输入模式选择 - 麦克风开关
        mic_toggle_frame = ctk.CTkFrame(control_frame)
        mic_toggle_frame.grid(row=6, column=0, sticky="ew", padx=5, pady=5)
        
        self.mic_enabled_var = ctk.BooleanVar(value=False)
        
        self.mic_checkbox = ctk.CTkCheckBox(
            mic_toggle_frame,
            text="🎤 启用麦克风实时模式",
            variable=self.mic_enabled_var,
            command=self._on_mic_toggle,
            font=("Arial", 12, "bold")
        )
        self.mic_checkbox.pack(padx=5, pady=5)
        
        self.mic_status_label = ctk.CTkLabel(
            mic_toggle_frame,
            text="[麦克风未启用]",
            text_color="gray"
        )
        self.mic_status_label.pack(padx=5, pady=2)
        
        # 检查麦克风可用性
        self._check_microphone_available()
        
        # 数据预览窗口控制
        preview_frame = ctk.CTkFrame(control_frame)
        preview_frame.grid(row=7, column=0, sticky="ew", padx=5, pady=5)
        
        self.preview_check_var = ctk.BooleanVar(value=False)
        preview_check = ctk.CTkCheckBox(
            preview_frame,
            text="显示数据预览窗口",
            variable=self.preview_check_var,
            command=self._toggle_preview_window
        )
        preview_check.pack(padx=5, pady=5)

    def _browse_file(self):
        """浏览文件"""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="选择音频文件",
            filetypes=[
                ("音频文件", "*.mp3 *.wav *.ogg *.flac"),
                ("所有文件", "*.*")
            ]
        )
        if file_path:
            self.file_entry.delete(0, "end")
            self.file_entry.insert(0, file_path)
            # 添加到历史记录
            self.file_history_manager.add_file(file_path)
            self._update_history_menu()

    def _update_history_menu(self):
        """更新历史记录菜单"""
        display_names = self.file_history_manager.get_display_names()
        if display_names:
            self.history_menu.configure(values=display_names)
        else:
            self.history_menu.configure(values=["无历史记录"])

    def _on_history_select(self, value: str):
        """历史记录选择处理"""
        if value == "无历史记录":
            return
        
        file_path = self.file_history_manager.get_file_by_display_name(value)
        if file_path:
            self.file_entry.delete(0, "end")
            self.file_entry.insert(0, file_path)

    def _on_visual_type_change(self, value: str):
        """可视化类型变更处理"""
        # 从分类格式中提取可视化类型名称
        # 格式: "分类 - 名称"
        if " - " in value:
            visual_type = value.split(" - ")[1]
        else:
            visual_type = value
        self.musicv.set_visual_type(visual_type)
        
        # 根据当前特效类型更新模式列表
        self._update_pattern_options(visual_type)

    def _update_pattern_options(self, visual_type: str):
        """根据特效类型更新模式选项"""
        # 获取pattern_library中可用的模式
        from src.pattern.pattern_library import PatternLibrary
        from src.pattern.pattern_matcher import PatternMatcher
        
        pattern_matcher = PatternMatcher()
        pattern_library = PatternLibrary(pattern_matcher)
        
        # 获取所有pattern配置
        all_patterns = pattern_matcher.patterns
        
        # 筛选出当前特效类型的模式
        available_patterns = {}
        available_patterns["默认模式"] = "default"
        
        for pattern_name, pattern_config in all_patterns.items():
            # 检查pattern的visual_effect是否匹配当前特效类型
            if pattern_config.get("visual_effect") == visual_type:
                # 提取风格名称
                audio_category = pattern_config.get("audio_category", "")
                
                # 跳过default风格，因为已经添加了"默认模式"
                if audio_category == "default":
                    continue
                
                # 根据风格名称生成显示名称
                style_display_names = {
                    "piano": "钢琴曲模式",
                    "rock": "摇滚乐模式",
                    "dj": "DJ音乐模式",
                    "light": "轻音乐模式"
                }
                
                display_name = style_display_names.get(audio_category, f"{audio_category}模式")
                available_patterns[display_name] = audio_category
        
        # 更新模式选项
        self.pattern_options = available_patterns
        
        # 更新模式菜单的选项
        pattern_values = list(self.pattern_options.keys())
        self.pattern_menu.configure(values=pattern_values)
        
        # 重置为默认模式
        self.pattern_menu.set("默认模式")
        self.current_pattern_label.configure(text="当前模式: 默认")

    def _on_pattern_change(self, value: str):
        """模式变更处理"""
        # 获取模式代码
        pattern_code = self.pattern_options.get(value, "default")
        
        # 更新当前模式显示
        self.current_pattern_label.configure(text=f"当前模式: {value}")
        
        # 应用模式到MusicV
        self.musicv.set_pattern(pattern_code)

    def _start_visualization(self):
        """开始可视化"""
        # 如果正在运行，先停止并等待完全停止
        if self.musicv.is_visualization_running:
            self._stop_visualization()
            # 等待可视化完全停止
            import time
            for i in range(20):
                if not self.musicv.is_visualization_running:
                    break
                time.sleep(0.1)
        
        is_mic_mode = self.mic_enabled_var.get()
        
        if not is_mic_mode:
            file_path = self.file_entry.get()
            if not file_path:
                print("请选择音频文件")
                return

            if not self.musicv.load_audio(file_path):
                print("加载音频文件失败")
                return

            # 加载音频特征数据到数据可视化器
            if hasattr(self, 'data_visualizer') and hasattr(self.musicv, 'audio_features') and self.musicv.audio_features:
                self.data_visualizer.load_features(self.musicv.audio_features)
                self.data_preview_window._create_charts()
                
                # 如果预览窗口被勾选，显示窗口
                if self.preview_check_var.get():
                    self.data_preview_window.show_window()
        
        # 应用当前选择的模式
        pattern_value = self.pattern_menu.get()
        pattern_code = self.pattern_options.get(pattern_value, "default")
        self.musicv.set_pattern(pattern_code)
        
        # 将数据预览窗口传递给musicv
        self.musicv.data_preview_window = self.data_preview_window

        # 在主线程中初始化pygame窗口
        self.musicv.visual_renderer.initialize()
        
        # 启动pygame事件处理定时器
        self._start_pygame_event_timer()

        # 在新线程中启动可视化，避免阻塞GUI
        thread = threading.Thread(target=self.musicv.start_visualization, daemon=True)
        thread.start()
    
    def _start_pygame_event_timer(self):
        """启动pygame事件处理定时器"""
        if self.pygame_event_timer is None:
            self.pygame_event_timer = self.after(10, self._process_pygame_events)
    
    def _process_pygame_events(self):
        """处理pygame事件"""
        try:
            if pygame.get_init():
                # 检查ESC键
                for event in pygame.event.get([pygame.KEYDOWN]):
                    if event.key == pygame.K_ESCAPE:
                        self._stop_visualization()
                        return
                pygame.event.pump()
        except Exception:
            pass
        
        # 继续定时器
        if self.pygame_event_timer is not None:
            self.pygame_event_timer = self.after(10, self._process_pygame_events)
    
    def _stop_pygame_event_timer(self):
        """停止pygame事件处理定时器"""
        if self.pygame_event_timer is not None:
            self.after_cancel(self.pygame_event_timer)
            self.pygame_event_timer = None

    def _stop_visualization(self):
        """停止可视化"""
        self.musicv.stop_visualization()
        
        # 停止pygame事件处理定时器
        self._stop_pygame_event_timer()
        
        if self.mic_enabled_var.get():
            self.mic_enabled_var.set(False)
            self.musicv.set_input_mode("file")
            self.mic_status_label.configure(text="[麦克风未启用]", text_color="gray")
        
    def _on_mic_toggle(self):
        """麦克风开关处理"""
        if self.mic_enabled_var.get():
            if not self.musicv.is_microphone_available():
                self.mic_enabled_var.set(False)
                return
            
            if not self.musicv.set_input_mode("microphone"):
                self.mic_enabled_var.set(False)
                self.mic_status_label.configure(text="[麦克风启用失败]", text_color="red")
                return
            
            self.mic_status_label.configure(text="[麦克风模式已开启]", text_color="green")
            
            if not self.musicv.is_visualization_running:
                self._start_visualization()
        else:
            if self.musicv.is_visualization_running:
                self._stop_visualization()
            
            self.musicv.set_input_mode("file")
            self.mic_status_label.configure(text="[麦克风未启用]", text_color="gray")
    
    def _check_microphone_available(self):
        """检查麦克风可用性"""
        if self.musicv.is_microphone_available():
            self.mic_checkbox.configure(state="normal")
            self.mic_status_label.configure(text="[麦克风未启用 - 可开启]", text_color="orange")
        else:
            self.mic_checkbox.configure(state="disabled")
            self.mic_status_label.configure(text="[未检测到麦克风]", text_color="red")
    
    def _toggle_preview_window(self):
        """切换数据预览窗口显示"""
        if self.preview_check_var.get():
            self.data_preview_window.show_window()
        else:
            self.data_preview_window.hide_window()

    def _on_particle_count_change(self, value: float):
        """粒子数量变更处理"""
        count = int(value)
        self.particle_count_value.configure(text=str(count))
        # 更新配置
        self.config_manager.set("particles.count", count)

    def _on_fps_change(self, value: float):
        """帧率变更处理"""
        fps = int(value)
        self.fps_value.configure(text=str(fps))
        # 更新配置
        self.config_manager.set("visual.rendering.fps", fps)

    def run(self):
        """运行窗口"""
        self.mainloop()

    def cleanup(self):
        """清理资源"""
        self.musicv.cleanup()


def main():
    """GUI主函数"""
    window = MainWindow()
    try:
        window.run()
    except KeyboardInterrupt:
        print("程序被中断")
    finally:
        window.cleanup()


if __name__ == "__main__":
    main()
