"""
菜单控制器模块

负责控制菜单选择和调用其他模块
"""

import sys
import os
from typing import Dict, List, Optional
# 导入其他模块
FileManager = None  # 默认值，以防导入失败
try:
    from calculation.core import ProbabilityCalculator, BallDrawOperation
    from config.examples import load_problem_config, EXAMPLE_PROBLEMS, create_custom_config
    from utils.file_manager import FileManager
except ImportError as e:
    print(f"警告: 模块导入错误: {e}")
    print("部分功能可能不可用")
    # 设置默认值
    FileManager = type('FileManager', (), {
        'save_results': lambda *args, **kwargs: print("文件管理器不可用"),
        'clean_old_results': lambda *args, **kwargs: 0
    })

class MenuController:
    """菜单控制器"""
    
    def __init__(self):
        self.calculator = ProbabilityCalculator()
        self.file_manager = FileManager()
        self.current_config = None
        self.current_operations = None
        self.current_description = ""
        
    def handle_choice(self, choice: str):
        """处理菜单选择"""
        try:
            if choice == '1':
                self.view_example_problems()
            elif choice == '2':
                self.create_custom_problem()
            elif choice == '3':
                self.run_exact_calculation()
            elif choice == '4':
                self.run_monte_carlo()
            elif choice == '5':
                self.save_configuration()
            elif choice == '6':
                self.load_configuration()
            elif choice == '7':
                self.clean_results_files()
            else:
                print("❌ 无效选择，请重试。")
        except Exception as e:
            print(f"❌ 操作出错: {e}")
            import traceback
            traceback.print_exc()
    
    def view_example_problems(self):
        """查看示例问题 - 调用示例模块"""
        print("\n📚 示例问题")
        print("=" * 60)
        
        try:
            from ui.display import display_example_problems
            display_example_problems()
            
            # 询问是否加载示例
            load_example = input("是否加载示例问题？ (输入编号或名称，按回车跳过): ").strip()
            
            if load_example:
                try:
                    # 尝试按编号加载
                    if load_example.isdigit():
                        index = int(load_example) - 1
                        example_names = list(EXAMPLE_PROBLEMS.keys())
                        if 0 <= index < len(example_names):
                            example_name = example_names[index]
                        else:
                            print("❌ 编号超出范围")
                            return
                    else:
                        example_name = load_example
                    
                    # 加载配置
                    self.current_config, self.current_operations, self.current_description = load_problem_config(example_name)
                    print(f"✅ 已加载示例问题: {example_name}")
                    self._display_current_problem_summary()
                    
                except Exception as e:
                    print(f"❌ 加载失败: {e}")
        except ImportError:
            print("❌ 显示模块未找到")
    def create_custom_problem(self):
        """创建自定义问题 - 调用配置向导"""
        print("\n✏️ 创建自定义问题")
        print("=" * 60)
        
        try:
            # 使用配置向导创建问题
            config_data = create_custom_config()
            
            if config_data:
                self.current_config = config_data["bags_config"]
                self.current_description = config_data["description"]
                
                # 将字典列表转换为BallDrawOperation对象列表
                from calculation.core import BallDrawOperation
                operations_list = []
                for op_dict in config_data["operations"]:
                    operations_list.append(
                        BallDrawOperation(
                            bag_id=op_dict["bag_id"],
                            draw_count=op_dict["draw_count"],
                            operation_type=op_dict["operation_type"]
                        )
                    )
                
                self.current_operations = operations_list
                print(f"\n✅ 自定义问题创建成功!")
                self._display_current_problem_summary()
        except Exception as e:
            print(f"❌ 创建失败: {e}")
    
    def run_exact_calculation(self):
        """运行精确计算"""
        if not self.current_config:
            print("❌ 请先创建或加载一个问题")
            return
            
        print("\n🔢 开始精确计算...")
        self._display_current_problem_summary()
        
        confirm = input("\n确定开始精确计算？这可能消耗大量计算资源 (y/N): ").strip().lower()
        if confirm != 'y':
            print("取消计算")
            return
        
        try:
            from ui.display import display_calculation_progress
            results = self.calculator.calculate_exact(
                self.current_config, 
                self.current_operations,
                progress_callback=display_calculation_progress
            )
            from ui.display import display_results
            display_results(results, is_monte_carlo=False)
            
            # 保存结果
            self.file_manager.save_results(results)
            
        except Exception as e:
            print(f"❌ 计算失败: {e}")
            print("建议尝试蒙特卡洛模拟")
    
    def run_monte_carlo(self):
        """运行蒙特卡洛模拟"""
        if not self.current_config:
            print("❌ 请先创建或加载一个问题")
            return
            
        print("\n🎲 开始蒙特卡洛模拟...")
        self._display_current_problem_summary()
        
        try:
            num_simulations = input("输入模拟次数 (默认100000): ").strip()
            num_simulations = int(num_simulations) if num_simulations else 100000
            
            if num_simulations <= 0:
                print("❌ 模拟次数必须为正数")
                return
                
            print(f"开始 {num_simulations:,} 次模拟...")
            
            from ui.display import display_simulation_progress
            results = self.calculator.monte_carlo_simulation(
                self.current_config, 
                self.current_operations, 
                num_simulations,
                progress_callback=display_simulation_progress
            )
            from ui.display import display_results
            display_results(results, is_monte_carlo=True)
            
            # 保存结果
            self.file_manager.save_results(results)
            
        except ValueError as e:
            print(f"❌ 输入错误: {e}")
        except Exception as e:
            print(f"❌ 模拟失败: {e}")
    
    def save_configuration(self):
        """保存当前配置到文件"""
        if not self.current_config:
            print("❌ 没有可保存的配置")
            return
            
        try:
            filename = input("输入保存的文件名 (默认: config.json): ").strip() or "config.json"
            config_data = {
                "description": self.current_description,
                "bags_config": self.current_config,
                "operations": [
                    {
                        "bag_id": op.bag_id,
                        "draw_count": op.draw_count,
                        "operation_type": op.operation_type
                    }
                    for op in self.current_operations
                ]
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                import json
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 配置已保存到: {filename}")
            
        except Exception as e:
            print(f"❌ 保存失败: {e}")
    
    def load_configuration(self):
        """从文件加载配置"""
        filename = input("输入要加载的文件名 (默认: config.json): ").strip() or "config.json"
        
        if not os.path.exists(filename):
            print(f"❌ 文件不存在: {filename}")
            return
            
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                import json
                config_data = json.load(f)
            
            # 解析配置
            self.current_description = config_data.get("description", "从文件加载的问题")
            self.current_config = config_data["bags_config"]
            
            operations_data = config_data["operations"]
            self.current_operations = [
                BallDrawOperation(
                    bag_id=op["bag_id"],
                    draw_count=op["draw_count"],
                    operation_type=op["operation_type"]
                )
                for op in operations_data
            ]
            
            # 验证配置
            errors = self.calculator.validate_configuration(self.current_config, self.current_operations)
            if errors:
                print("⚠️  配置验证警告:")
                for error in errors:
                    print(f"  - {error}")
                fix = input("是否继续使用此配置？ (y/N): ").strip().lower()
                if fix != 'y':
                    self.current_config = None
                    self.current_operations = None
                    return
            
            print(f"✅ 配置已从 {filename} 加载")
            self._display_current_problem_summary()
            
        except Exception as e:
            print(f"❌ 加载失败: {e}")
    
    def clean_results_files(self):
        """清理结果文件"""
        print("\n🗑️  清理结果文件")
        print("=" * 60)
        
        try:
            # 使用文件管理器清理
            cleaned = self.file_manager.clean_old_results()
            print(f"✅ 已清理 {cleaned} 个旧结果文件")
        except Exception as e:
            print(f"❌ 清理失败: {e}")
    
    def _display_current_problem_summary(self):
        """显示当前问题摘要"""
        if not self.current_config:
            return
            
        print("\n📋 当前问题摘要:")
        print("=" * 60)
        print(f"描述: {self.current_description}")
        print(f"袋子数: {len(self.current_config)}")
        
        for bag_id, colors in self.current_config.items():
            total = sum(colors.values())
            color_str = ", ".join(f"{count}{color}" for color, count in colors.items())
            print(f"  袋子{bag_id}: {color_str} (共{total}个球)")
        
        print(f"\n操作序列 ({len(self.current_operations)}个操作):")
        for i, op in enumerate(self.current_operations, 1):
            action = {"draw": "摸", "discard": "丢", "return": "还"}[op.operation_type]
            print(f"  {i}. {action}袋{op.bag_id} {op.draw_count}个球")
            
    def get_current_problem(self):
        """获取当前问题"""
        return {
            "config": self.current_config,
            "operations": self.current_operations,
            "description": self.current_description
        }
        
    def set_current_problem(self, config, operations, description):
        """设置当前问题"""
        self.current_config = config
        self.current_operations = operations
        self.current_description = description