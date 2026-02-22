import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.gui.main_window import MainWindow
import customtkinter as ctk

def test_pattern_selection():
    """测试模式选择功能"""
    print("开始测试模式选择功能...")
    
    # 创建主窗口
    app = MainWindow()
    
    # 检查模式选择控件是否存在
    if hasattr(app, 'pattern_menu'):
        print("✓ 模式选择控件已创建")
        
        # 检查模式选项
        if hasattr(app, 'pattern_options'):
            print(f"✓ 模式选项已定义: {list(app.pattern_options.keys())}")
        else:
            print("✗ 模式选项未定义")
            return False
        
        # 检查当前模式显示
        if hasattr(app, 'current_pattern_label'):
            print("✓ 当前模式显示标签已创建")
        else:
            print("✗ 当前模式显示标签未创建")
            return False
        
        # 测试模式切换
        print("\n测试模式切换...")
        for pattern_name in app.pattern_options.keys():
            print(f"  切换到: {pattern_name}")
            app._on_pattern_change(pattern_name)
            
            # 检查MusicV中的模式是否更新
            if app.musicv.current_pattern == app.pattern_options[pattern_name]:
                print(f"  ✓ 模式已更新为: {app.musicv.current_pattern}")
            else:
                print(f"  ✗ 模式更新失败")
                return False
        
        print("\n✓ 模式选择功能测试通过")
        return True
    else:
        print("✗ 模式选择控件未创建")
        return False

if __name__ == "__main__":
    success = test_pattern_selection()
    if success:
        print("\n所有测试通过！")
    else:
        print("\n测试失败！")
        sys.exit(1)
