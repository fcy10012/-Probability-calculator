#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多袋摸球概率计算器 - 主菜单界面

这是一个简洁的前端界面，所有功能都在其他模块中实现
"""

import sys
import os

# 添加modules目录到路径，以便导入模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

def show_main_menu():
    """显示主菜单"""
    print("\n" + "=" * 60)
    print("🎲 多袋摸球概率计算器 - 主菜单")
    print("=" * 60)
    print("1. 📊 查看示例问题")
    print("2. ✏️  自定义新问题")
    print("3. 🔢 精确计算当前问题")
    print("4. 🎲 蒙特卡洛模拟当前问题")
    print("5. 📁 保存当前配置")
    print("6. 📖 加载配置文件")
    print("7. 🗑️  清理结果文件")
    print("Q. 🚪 退出")
    print("=" * 60)

def main():
    """主函数 - 前端界面"""
    print("🎲 多袋摸球概率计算器")
    print("📁 模块化架构版本")
    print("🔧 主界面只负责菜单显示和功能调用")
    
    # 导入必要的模块
    try:
        from ui.menu import MenuController
    except ImportError as e:
        print(f"❌ 模块导入错误: {e}")
        print("请确保所有模块已正确创建")
        return
    
    # 创建菜单控制器
    controller = MenuController()
    
    while True:
        show_main_menu()
        choice = input("\n请选择操作 (1-7, q退出): ").strip().lower()
        
        if choice == 'q':
            print("\n👋 感谢使用，再见！")
            break
            
        controller.handle_choice(choice)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 程序被用户中断")
    except Exception as e:
        print(f"\n❌ 程序出错: {e}")
        import traceback
        traceback.print_exc()