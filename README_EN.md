# MusicV - Music Audio Analysis and Visualization Project

## Project Overview

MusicV is a highly extensible, modular music audio analysis and visualization project built with Python. The core objective is to achieve multi-dimensional audio analysis + dynamic visual display, while meeting engineering design requirements for long-term iterative expansion.

## Video Demo

[![Bilibili Video Demo](https://img.shields.io/badge/Bilibili-Video%20Demo-blue?logo=bilibili)](https://www.bilibili.com/video/BV1ndZZBVEuU/?spm_id_from=333.1387.homepage.video_card.click&vd_source=1ff83d420d632f519258dfadd458d056)

Watch the full demo video: [我用AI完成了一款音频可视化软件\_哔哩哔哩\_bilibili](https://www.bilibili.com/video/BV1ahZZB8EWy/?spm_id_from=333.1387.list.card_archive.click&vd_source=1ff83d420d632f519258dfadd458d056)

## Features

### Audio Analysis Module

- Supports reading and parsing mainstream audio formats (MP3/WAV/FLAC, etc.)
- Extracts multi-dimensional audio features:
  - Time-domain features (waveform, amplitude, loudness)
  - Frequency-domain features (spectrum, mel spectrogram, fundamental frequency/pitch)
  - Rhythm features (BPM, beat points, measure division, onset envelope)
  - Timbre features (MFCC, spectral centroid, spectral bandwidth, spectral rolloff)
- Encapsulates analysis results in standardized data structures, supports feature data export/import
- Supports microphone real-time input, real-time audio feature analysis

### Visual Display Module

- Implements real-time dynamic visual effects based on audio feature data
- Supports multiple visual rendering types:
  - 2D visualization (waveform with mirror display, spectrum waterfall, dynamic equalizer)
  - 3D visualization (3D spectrum cube, audio feature-driven 3D model animation)
  - Particle system (audio amplitude/frequency-driven particle emission/movement/dissipation)
  - Effect system (rain, snow, fire, petals, glowing squares and other dynamic effects)
  - Animation system (beat-triggered frame animations, easing animations)
- Visual effects support custom configuration (color schemes, particle count, 3D perspective, animation speed, etc.)

### Engineering Design

- Strictly separates **audio analysis layer** and **visual rendering layer**, with standardized interface communication between layers
- Adopts "core rendering engine + plugin-style visual components" architecture
- Event-driven architecture, reducing coupling between modules
- Layered architecture: data layer, analysis layer, interface layer, rendering layer, control layer
- Configuration management: Uses YAML configuration files for global parameter management
- Supports Python 3.10+, cross-platform (Windows/macOS/Linux) operation

## Environment Setup

### Dependency Installation

1. Clone the project to local:

   ```bash
   git clone <repository_url>
   cd MusicV
   ```
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

### Main Dependencies

- **Audio Processing**: librosa, soundfile, numpy, scipy
- **Visualization**: matplotlib, plotly, pyvista, pygame, pyglet
- **GUI**: customtkinter, tkinter
- **Configuration Management**: pyyaml
- **Data Processing**: pandas
- **Utility Libraries**: tqdm

## Usage

### Command Line Usage

```bash
# Basic usage
python -m src.core.main <audio_file_path>

# Example
python -m src.core.main examples/audio/sample.mp3
```

### GUI Usage

```bash
python -m src.gui.main_window
```

### Microphone Real-time Mode

The GUI interface supports microphone real-time input mode, enabling real-time visualization without loading audio files:

1. Start the program: `python -m src.gui.main_window`
2. Check the "🎤 Enable Microphone Real-time Mode" box in the interface
3. Click the "Start Visualization" button
4. Speak to the microphone or play music to see real-time visualization effects

Note: Requires the `sounddevice` library: `pip install sounddevice`

### Example Code

```bash
python examples/example_usage.py
```

## Project Structure

```
MusicV/
├── src/
│   ├── audio/            # Audio analysis module
│   │   ├── audio_parser.py      # Audio parser
│   │   ├── feature_extractor.py  # Feature extractor
│   │   ├── audio_feature_generator.py  # Audio feature generator
│   │   ├── microphone_input.py  # Microphone real-time input
│   │   ├── audio_category.py   # Audio category
│   │   ├── audio_categories.py # Audio category implementations
│   │   ├── music_style_analyzer.py  # Music style analyzer
│   │   └── beat_utils.py      # Beat utilities
│   ├── visual/           # Visual display module
│   │   ├── renderer/visual_renderer.py    # Core rendering engine
│   │   ├── components/visual_2d.py         # 2D visual components
│   │   ├── components/visual_3d.py         # 3D visual components
│   │   ├── particle_system.py    # Particle system
│   │   └── effects/          # Visual effects (rain, snow, fire, petals, squares)
│   ├── core/             # Core modules
│   │   ├── interfaces.py         # Standardized interfaces
│   │   ├── event_system.py       # Event system
│   │   ├── main.py               # Main entry
│   │   └── config_manager.py     # Configuration manager
│   └── gui/              # GUI interface
│       └── main_window.py        # Main window
├── effects_origin/     # Independent effect library
│   ├── rain_effect.py
│   ├── snow_effect.py
│   ├── fire_effect.py
│   ├── petal_effect.py
│   └── glowing_squares_effect.py
├── examples/             # Examples
│   ├── audio/            # Example audio
│   └── example_usage.py  # Usage examples
├── tests/                # Tests
│   └── test_audio_parser.py  # Audio analysis tests
├── docs/                 # Documentation
├── config.yaml           # Global configuration file
├── requirements.txt      # Dependency management
├── setup.py              # Project configuration
├── README.md             # Project description (Chinese)
└── README_EN.md         # Project description (English)
```

## Configuration

Configuration file is located at `config.yaml`, containing the following main configuration items:

- **audio**: Audio analysis configuration
- **visual**: Visual display configuration
- **color_schemes**: Color schemes
- **gui**: GUI configuration
- **export**: Export configuration

## Extension Development

### Adding New Audio Feature Analysis

1. Create a new feature extractor class in `src/audio/feature_extractor.py`, inheriting from `FeatureExtractor`
2. Implement the `extract` method and `name` property
3. Register the new extractor in `FeatureExtractorManager`

### Adding New Visual Components

1. Create a new visual component file in `src/visual/` directory
2. Create a new component class inheriting from `VisualComponent`
3. Implement `initialize`, `update`, `render` methods and `name` property
4. Register the new component in `VisualRenderer`

### Adding New Visualization Types

1. Add new visualization type in the `visual_types` list in `src/gui/main_window.py`
2. Ensure the corresponding visual component is registered

## Performance Optimization

- Visual rendering uses Pygame, ensuring smooth operation on consumer-grade computers (frame rate ≥30 at 1080P resolution)
- Audio feature extraction uses librosa's optimized algorithms
- Supports frame rate adaptation, adjusting rendering frame rate based on hardware performance

## Testing

Run tests:

```bash
python -m pytest tests/
```

## License

MIT License

## Contributing

Issues and Pull Requests are welcome!

## Support the Project

If this project helps you, your support is appreciated:

![Support the Project](./ysiyisi.png)

## Contact

- Author: zy.h
- Email: 1104460281@qq.com
