# MusicV - 音乐音频解析与可视化工程

## 项目简介

MusicV是一个基于Python语言的高扩展性、模块化音乐音频解析与可视化工程，核心目标是完成音频多维度解析+动态视觉化展示，同时满足长期迭代扩展的工程化设计要求。

## 视频演示

[![B站视频演示](https://img.shields.io/badge/B站-视频演示-blue?logo=bilibili)](https://www.bilibili.com/video/BV1ndZZBVEuU/?spm_id_from=333.1387.homepage.video_card.click&vd_source=1ff83d420d632f519258dfadd458d056)

观看完整演示视频：[我用AI完成了一款音频可视化软件\_哔哩哔哩\_bilibili](https://www.bilibili.com/video/BV1ahZZB8EWy/?spm_id_from=333.1387.list.card_archive.click&vd_source=1ff83d420d632f519258dfadd458d056)

## 功能特点

### 音频解析模块

- 支持主流音频格式（MP3/WAV/FLAC等）的读取与解析
- 提取音频多维度特征：
  - 时域特征（波形、振幅、响度）
  - 频域特征（频谱、梅尔频谱、基频/音高）
  - 节奏特征（BPM、节拍点、小节划分、起音包络）
  - 音色特征（MFCC、谱质心、谱带宽、谱滚降）
- 解析结果封装为标准化数据结构，支持特征数据的导出/导入
- 支持麦克风实时输入，实时解析音频特征

### 视觉展示模块

- 基于音频特征数据实现实时随动的视觉效果
- 支持多类型视觉渲染：
  - 2D可视化（波形图-支持镜像显示、频谱瀑布图、动态均衡器）
  - 3D可视化（3D频谱立方体、音频特征驱动的3D模型动效）
  - 粒子系统（音频振幅/频率驱动的粒子发射/运动/消散）
  - 特效系统（雨、雪、火、花瓣、闪光方块等动态特效）
  - 动画系统（节拍触发的帧动画、缓动动画）
- 视觉效果支持自定义配置（色彩方案、粒子数量、3D视角、动画速度等）

### 工程设计

- 严格拆分**音频解析层**与**视觉渲染层**，两层之间通过标准化接口通信
- 采用“核心渲染引擎+插件式视觉组件”架构
- 事件驱动架构，降低模块间耦合
- 分层架构：数据层、解析层、接口层、渲染层、控制层
- 配置管理：采用YAML配置文件管理全局参数
- 支持Python 3.10+版本，跨平台（Windows/macOS/Linux）运行

## 环境搭建

### 依赖安装

1. 克隆项目到本地：

   ```bash
   git clone <repository_url>
   cd MusicV
   ```
2. 安装依赖：

   ```bash
   pip install -r requirements.txt
   ```

### 主要依赖

- **音频处理**：librosa, soundfile, numpy, scipy
- **可视化**：matplotlib, plotly, pyvista, pygame, pyglet
- **GUI**：customtkinter, tkinter
- **配置管理**：pyyaml
- **数据处理**：pandas
- **工具库**：tqdm

## 使用方法

### 命令行使用

```bash
# 基本使用
python -m src.core.main <audio_file_path>

# 示例
python -m src.core.main examples/audio/sample.mp3
```

### GUI使用

```bash
python -m src.gui.main_window
```

### 麦克风实时模式

GUI界面支持麦克风实时输入模式，无需加载音频文件即可实现实时可视化：

1. 启动程序：`python -m src.gui.main_window`
2. 在界面中勾选"🎤 启用麦克风实时模式"
3. 点击"开始可视化"按钮
4. 对着麦克风说话或播放音乐，即可看到实时可视化效果

注意：需要安装 `sounddevice` 库：`pip install sounddevice`

### 示例代码

```bash
python examples/example_usage.py
```

## 项目结构

```
MusicV/
├── src/
│   ├── audio/            # 音频解析模块
│   │   ├── audio_parser.py      # 音频解析器
│   │   ├── feature_extractor.py  # 特征提取器
│   │   ├── audio_feature_generator.py  # 音频特征生成器
│   │   ├── microphone_input.py  # 麦克风实时输入
│   │   ├── audio_category.py   # 音频类别
│   │   ├── audio_categories.py # 音频类别实现
│   │   ├── music_style_analyzer.py  # 音乐风格分析
│   │   └── beat_utils.py      # 节拍工具
│   ├── visual/           # 视觉展示模块
│   │   ├── renderer/visual_renderer.py    # 核心渲染引擎
│   │   ├── components/visual_2d.py         # 2D可视化组件
│   │   ├── components/visual_3d.py         # 3D可视化组件
│   │   ├── particle_system.py    # 粒子系统
│   │   └── effects/          # 视觉特效（雨、雪、火、花瓣、方块）
│   ├── core/             # 核心模块
│   │   ├── interfaces.py         # 标准化接口
│   │   ├── event_system.py       # 事件系统
│   │   ├── main.py               # 主入口
│   │   └── config_manager.py     # 配置管理器
│   └── gui/              # GUI界面
│       └── main_window.py        # 主窗口
├── effects_origin/     # 独立特效库
│   ├── rain_effect.py
│   ├── snow_effect.py
│   ├── fire_effect.py
│   ├── petal_effect.py
│   └── glowing_squares_effect.py
├── examples/             # 示例
│   ├── audio/            # 示例音频
│   └── example_usage.py  # 使用示例
├── tests/                # 测试
│   └── test_audio_parser.py  # 音频解析测试
├── docs/                 # 文档
├── config.yaml           # 全局配置文件
├── requirements.txt      # 依赖管理
├── setup.py              # 项目配置
├── README.md             # 项目说明（中文）
└── README_EN.md         # 项目说明（英文）
```

## 配置说明

配置文件位于 `config.yaml`，包含以下主要配置项：

- **audio**：音频解析配置
- **visual**：视觉展示配置
- **color_schemes**：色彩方案
- **gui**：GUI配置
- **export**：导出配置

## 扩展开发

### 新增音频特征解析

1. 在 `src/audio/feature_extractor.py` 中创建新的特征提取器类，继承自 `FeatureExtractor`
2. 实现 `extract` 方法和 `name` 属性
3. 在 `FeatureExtractorManager` 中注册新的提取器

### 新增视觉组件

1. 在 `src/visual/` 目录下创建新的视觉组件文件
2. 创建新的组件类，继承自 `VisualComponent`
3. 实现 `initialize`、`update`、`render` 方法和 `name` 属性
4. 在 `VisualRenderer` 中注册新的组件

### 新增可视化类型

1. 在 `src/gui/main_window.py` 中的 `visual_types` 列表中添加新的可视化类型
2. 确保对应的视觉组件已注册

## 性能优化

- 视觉渲染采用Pygame，确保在普通消费级电脑上流畅运行（1080P分辨率下帧率≥30）
- 音频特征提取采用librosa的优化算法
- 支持帧率自适应，根据硬件性能调整渲染帧率

## 测试

运行测试：

```bash
python -m pytest tests/
```

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 支持项目

如果这个项目对你有帮助，欢迎支持：

![支持项目](./ysiyisi.png)

## 联系方式

- 作者：zy.h
- 邮箱：1104460281@qq.com
