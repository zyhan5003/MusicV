# Changelog

This document records all important changes to the MusicV project.

Format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and versioning follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Added microphone real-time input mode, supporting real-time audio visualization
- Added independent effect library architecture (effects_origin/)
- Added Rain Effect (RainEffect): Audio amplitude-driven rain drop effect
- Added Snow Effect (SnowEffect): Audio beat-driven snow falling effect
- Added Fire Effect (FireEffect): Audio intensity-driven flame effect
- Added Petal Effect (PetalEffect): Audio rhythm-driven petal falling effect
- Added Glowing Squares Effect (GlowingSquaresEffect): Audio feature-driven square animation effect
- Waveform visualization supports mirror display, symmetric rendering above and below center axis
- Audio feature extraction supports onset envelope (onset_envelope)
- Added data preview window, real-time display of audio features

### Optimized
- Optimized particle generation logic, dynamically adjusting based on audio intensity
- Improved microphone mode response speed (sample rate 16000Hz, update rate 60 FPS)
- Optimized square effect animation, reduced visual flickering
- Improved audio feature extraction performance

### Fixed
- Fixed window not displaying on multiple playbacks
- Fixed window residue issue when stopping visualization
- Fixed system crash when using ESC key
- Fixed visualization not responding in microphone mode
- Fixed system freeze when clicking window close button

### Documentation
- Added bilingual documentation (README.md and README_EN.md)
- Added contribution guides (CONTRIBUTING.md and CONTRIBUTING_EN.md)
- Added MIT license file (LICENSE)

## [0.1.0] - 2024-01-01

### Added
- Initial release
- Support for mainstream audio formats (MP3/WAV/FLAC) parsing
- Implemented multi-dimensional audio feature extraction (time domain, frequency domain, rhythm, timbre)
- Implemented 2D visualization (waveform, spectrum, equalizer)
- Implemented 3D visualization (spectrum cube, 3D model)
- Implemented particle system (basic particles, beat particles, jumping particles)
- Implemented GUI interface (file selection, visualization type switching, parameter configuration)
- Support for configuration file management (YAML)
- Support for data export functionality
