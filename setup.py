from setuptools import setup, find_packages

setup(
    name="MusicV",
    version="0.1.0",
    description="音乐音频解析与可视化工程",
    long_description="基于Python的高扩展性、模块化音乐音频解析与可视化系统，支持多维度音频特征提取和实时视觉效果展示。",
    author="Your Name",
    author_email="your.email@example.com",
    url="",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "librosa==0.10.1",
        "soundfile==0.12.1",
        "numpy==1.26.4",
        "scipy==1.12.0",
        "matplotlib==3.8.3",
        "plotly==5.18.0",
        "pyvista==0.43.2",
        "pygame==2.6.1",
        "pyglet==2.0.9",
        "customtkinter==5.2.2",
        "pyyaml==6.0.1",
        "pandas==2.2.1",
        "tqdm==4.66.1",
    ],
    extras_require={
        "dev": [
            "mypy==1.8.0",
            "pytest==7.4.0",
            "black==23.3.0",
            "flake8==6.0.0",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Topic :: Multimedia :: Sound/Audio :: Visualization",
    ],
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "musicv=core.main:main",
        ],
    },
)
