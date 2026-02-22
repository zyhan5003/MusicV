import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.gui.main_window import MainWindow


def test_main_window_effects_controls():
    """测试main_window中的特效控件"""
    print("=== 测试main_window中的特效控件 ===")
    
    try:
        # 创建主窗口
        main_window = MainWindow()
        
        # 检查可视化类型分类
        print("\n可视化类型分类:")
        for category, types in main_window.visual_categories.items():
            print(f"  {category}: {', '.join(types)}")
        
        # 检查特效系统分类是否存在
        if "特效系统" in main_window.visual_categories:
            print("\n✓ 特效系统分类已添加")
            effects = main_window.visual_categories["特效系统"]
            print(f"  特效列表: {', '.join(effects)}")
            
            # 检查是否包含新的特效
            if "rain" in effects:
                print("  ✓ 下雨特效已添加")
            else:
                print("  ✗ 下雨特效未添加")
            
            if "fire" in effects:
                print("  ✓ 火焰特效已添加")
            else:
                print("  ✗ 火焰特效未添加")
            
            if "snow" in effects:
                print("  ✓ 下雪特效已添加")
            else:
                print("  ✗ 下雪特效未添加")
        else:
            print("\n✗ 特效系统分类未添加")
        
        # 检查可视化类型菜单
        print("\n可视化类型菜单选项:")
        visual_options = main_window.visual_type_menu.cget("values")
        print(f"  总选项数: {len(visual_options)}")
        
        # 检查特效系统相关选项
        effect_options = [opt for opt in visual_options if opt.startswith("特效系统")]
        print(f"  特效系统选项数: {len(effect_options)}")
        for opt in effect_options:
            print(f"    - {opt}")
        
        # 检查模式选项
        print("\n模式选项:")
        pattern_options = main_window.pattern_options
        print(f"  总模式数: {len(pattern_options)}")
        for name, code in pattern_options.items():
            print(f"    - {name}: {code}")
        
        # 测试可视化类型变更
        print("\n测试可视化类型变更:")
        test_visual_types = ["特效系统 - rain", "特效系统 - fire", "特效系统 - snow"]
        for visual_type in test_visual_types:
            try:
                main_window._on_visual_type_change(visual_type)
                print(f"  ✓ 成功切换到: {visual_type}")
                
                # 检查模式选项是否更新
                current_patterns = main_window.pattern_menu.cget("values")
                print(f"    当前可用模式数: {len(current_patterns)}")
                
            except Exception as e:
                print(f"  ✗ 切换失败: {visual_type}, 错误: {e}")
        
        print("\n✓ main_window控件测试完成")
        return True
        
    except Exception as e:
        print(f"\n✗ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_main_window_effects_controls()
    if success:
        print("\n✓ 所有控件测试通过！")
    else:
        print("\n✗ 部分控件测试失败！")