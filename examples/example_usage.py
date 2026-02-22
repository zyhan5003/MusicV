#!/usr/bin/env python3
"""
MusicV 使用示例
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.main import MusicV


def basic_usage():
    """基本使用示例"""
    print("=== MusicV 基本使用示例 ===")
    
    # 创建 MusicV 实例
    musicv = MusicV()
    
    # 加载音频文件
    audio_path = input("请输入音频文件路径: ")
    if not os.path.exists(audio_path):
        print("错误: 音频文件不存在")
        return
    
    print(f"加载音频文件: {audio_path}")
    success = musicv.load_audio(audio_path)
    if not success:
        print("错误: 加载音频失败")
        return
    
    # 选择可视化类型
    print("\n可选的可视化类型:")
    print("1. waveform - 波形图")
    print("2. spectrum - 频谱瀑布图")
    print("3. equalizer - 动态均衡器")
    print("4. spectrum_cube - 3D频谱立方体")
    print("5. particles - 粒子系统")
    print("6. beat_particles - 节拍粒子系统")
    print("7. jumping_particles - 跳动粒子系统")
    print("8. style_aware_particles - 风格感知粒子系统")
    print("9. comprehensive - 综合可视化")
    
    choice = input("请选择可视化类型 (1-9): ")
    visual_types = [
        "waveform", "spectrum", "equalizer",
        "spectrum_cube", "particles", "beat_particles",
        "jumping_particles", "style_aware_particles", "comprehensive"
    ]
    
    if choice.isdigit() and 1 <= int(choice) <= 9:
        visual_type = visual_types[int(choice) - 1]
        print(f"选择的可视化类型: {visual_type}")
        
        # 如果选择风格感知粒子系统，让用户手动选择音乐类型
        if visual_type == "style_aware_particles":
            print("\n请选择音乐风格:")
            print("1. piano - 钢琴曲（优雅、流畅）")
            print("2. rock - 摇滚乐（强烈、有力）")
            print("3. dj - DJ音乐（电子感强、节拍明确）")
            print("4. light - 轻音乐（舒缓、放松）")
            
            style_choice = input("请选择音乐风格 (1-4): ")
            style_map = {
                "1": "piano",
                "2": "rock",
                "3": "dj",
                "4": "light"
            }
            
            if style_choice in style_map:
                manual_style = style_map[style_choice]
                print(f"选择的音乐风格: {manual_style}")
                # 设置手动风格配置
                musicv.set_config({"visual": {"style_aware_particles": {"manual_style": manual_style}}})
            else:
                print("无效选择，使用默认音乐风格: light")
                manual_style = "light"
                musicv.set_config({"visual": {"style_aware_particles": {"manual_style": manual_style}}})
        
        musicv.set_visual_type(visual_type)
    else:
        print("无效选择，使用默认可视化类型: waveform")
        visual_type = "waveform"
        musicv.set_visual_type(visual_type)
    
    # 开始可视化
    print("\n开始可视化...")
    print("按 ESC 键退出")
    try:
        musicv.start_visualization()
    except KeyboardInterrupt:
        print("\n可视化已停止")
    finally:
        musicv.cleanup()


def batch_visualization():
    """批量可视化示例"""
    print("\n=== MusicV 批量可视化示例 ===")
    
    # 创建 MusicV 实例
    musicv = MusicV()
    
    # 音频文件目录
    audio_dir = input("请输入音频文件目录: ")
    if not os.path.isdir(audio_dir):
        print("错误: 目录不存在")
        return
    
    # 获取目录中的音频文件
    audio_files = []
    for file in os.listdir(audio_dir):
        if file.endswith((".mp3", ".wav", ".flac", ".ogg")):
            audio_files.append(os.path.join(audio_dir, file))
    
    if not audio_files:
        print("错误: 目录中没有音频文件")
        return
    
    print(f"找到 {len(audio_files)} 个音频文件")
    
    # 对每个音频文件进行可视化
    for audio_path in audio_files:
        print(f"\n处理文件: {os.path.basename(audio_path)}")
        
        # 加载音频
        success = musicv.load_audio(audio_path)
        if not success:
            print(f"错误: 加载音频失败 - {audio_path}")
            continue
        
        # 依次使用不同的可视化类型
        for visual_type in ["waveform", "spectrum", "particles"]:
            print(f"使用可视化类型: {visual_type}")
            musicv.set_visual_type(visual_type)
            
            # 开始可视化
            print("按 ESC 键切换到下一个可视化类型")
            try:
                musicv.start_visualization()
            except KeyboardInterrupt:
                print("切换到下一个可视化类型...")
            finally:
                musicv.stop_visualization()
    
    musicv.cleanup()


def info_display_usage():
    """音频信息显示示例"""
    print("\n=== MusicV 音频信息显示示例 ===")
    
    # 创建 MusicV 实例
    musicv = MusicV()
    
    # 加载音频文件
    audio_path = input("请输入音频文件路径: ")
    if not os.path.exists(audio_path):
        print("错误: 音频文件不存在")
        return
    
    print(f"加载音频文件: {audio_path}")
    success = musicv.load_audio(audio_path)
    if not success:
        print("错误: 加载音频失败")
        return
    
    # 设置为信息显示可视化类型
    visual_type = "info_display"
    print(f"选择的可视化类型: {visual_type}")
    musicv.set_visual_type(visual_type)
    
    # 开始可视化
    print("\n开始可视化...")
    print("显示音频各维度特征及其对应的视觉元素")
    print("按 ESC 键退出")
    try:
        musicv.start_visualization()
    except KeyboardInterrupt:
        print("\n可视化已停止")
    finally:
        musicv.cleanup()


if __name__ == "__main__":
    print("Welcome to MusicV Example!")
    print("==========================")
    
    print("1. 基本使用示例")
    print("2. 批量可视化示例")
    print("3. 音频信息显示示例")
    
    choice = input("请选择示例类型 (1-3): ")
    
    if choice == "1":
        basic_usage()
    elif choice == "2":
        batch_visualization()
    elif choice == "3":
        info_display_usage()
    else:
        print("无效选择")
