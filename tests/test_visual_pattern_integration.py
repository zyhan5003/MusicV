import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.gui.main_window import MainWindow
import customtkinter as ctk

def test_visual_pattern_integration():
    """测试特效与模式的联动"""
    print("开始测试特效与模式的联动...")
    
    # 创建主窗口
    app = MainWindow()
    
    # 测试所有特效类型
    test_cases = [
        ("2D可视化 - waveform", "waveform"),
        ("2D可视化 - spectrum", "spectrum"),
        ("2D可视化 - equalizer", "equalizer"),
        ("3D可视化 - spectrum_cube", "spectrum_cube"),
        ("3D可视化 - 3d_model", "3d_model"),
        ("粒子系统 - particles", "particles"),
        ("粒子系统 - beat_particles", "beat_particles"),
        ("粒子系统 - jumping_particles", "jumping_particles"),
        ("粒子系统 - style_aware_particles", "style_aware_particles"),
        ("信息显示 - info_display", "info_display"),
        ("综合可视化 - comprehensive", "comprehensive")
    ]
    
    all_passed = True
    
    for visual_option, visual_type in test_cases:
        print(f"\n测试特效: {visual_type}")
        
        # 切换特效
        app._on_visual_type_change(visual_option)
        
        # 检查模式选项是否更新
        pattern_values = list(app.pattern_options.keys())
        print(f"  可用模式: {pattern_values}")
        
        # 验证至少有默认模式
        if "默认模式" not in pattern_values:
            print(f"  ✗ 缺少默认模式")
            all_passed = False
            continue
        
        # 测试每个模式
        for pattern_name in pattern_values:
            pattern_code = app.pattern_options[pattern_name]
            print(f"    测试模式: {pattern_name} ({pattern_code})")
            
            # 切换模式
            app._on_pattern_change(pattern_name)
            
            # 检查MusicV中的模式是否更新
            if app.musicv.current_pattern == pattern_code:
                print(f"      ✓ 模式已更新")
            else:
                print(f"      ✗ 模式更新失败")
                all_passed = False
    
    if all_passed:
        print("\n✓ 所有测试通过！")
        return True
    else:
        print("\n✗ 部分测试失败！")
        return False

if __name__ == "__main__":
    success = test_visual_pattern_integration()
    if not success:
        sys.exit(1)
