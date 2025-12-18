"""
多袋摸球概率计算器 - 交互式应用

提供命令行交互界面，让用户可以：
1. 查看示例问题
2. 自定义问题
3. 选择计算方法
4. 查看详细结果
"""

import sys
import json
import os
from typing import Dict, List
from probability_calculator import ProbabilityCalculator, BallDrawOperation
from example_config import load_problem_config, create_custom_config

class InteractiveProbabilityApp:
    """交互式应用"""
    
    def __init__(self):
        self.calculator = ProbabilityCalculator()
        self.current_config = None
        self.current_operations = None
        self.current_description = ""
        
    def run(self):
        """运行交互式应用"""
        print("🎲 多袋摸球概率计算器 - 交互式应用")
        print("=" * 60)
        
        while True:
            self.show_main_menu()
            choice = input("\n请选择操作 (1-6, q退出): ").strip().lower()
            
            if choice == 'q':
                print("\n👋 感谢使用，再见！")
                break
                
            self.handle_menu_choice(choice)
    
    def show_main_menu(self):
        """显示主菜单"""
        print("\n" + "=" * 60)
        print("📋 主菜单")
        print("=" * 60)
        print("1. 📊 查看示例问题")
        print("2. ✏️  自定义新问题")
        print("3. 🔢 精确计算当前问题")
        print("4. 🎲 蒙特卡洛模拟当前问题")
        print("5. 📁 保存当前配置")
        print("6. 📖 加载配置文件")
        print("Q. 🚪 退出")
        
        if self.current_config:
            print("\n📌 当前问题:")
            print(f"  描述: {self.current_description}")
            print(f"  袋子数: {len(self.current_config)}")
            print(f"  操作数: {len(self.current_operations)}")
    
    def handle_menu_choice(self, choice: str):
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
            else:
                print("❌ 无效选择，请重试。")
        except Exception as e:
            print(f"❌ 操作出错: {e}")
            import traceback
            traceback.print_exc()
    
    def view_example_problems(self):
        """查看示例问题"""
        print("\n📚 示例问题")
        print("=" * 60)
        
        from example_config import EXAMPLE_PROBLEMS
        
        for i, (name, problem) in enumerate(EXAMPLE_PROBLEMS.items(), 1):
            print(f"\n{i}. 📦 {name}")
            print(f"   📝 {problem['description']}")
            
            bags = problem["bags_config"]
            print(f"   📊 袋子: {len(bags)}个")
            for bag_id, colors in bags.items():
                total = sum(colors.values())
                color_str = ", ".join(f"{count}{color}" for color, count in colors.items())
                print(f"     袋子{bag_id}: {color_str} (共{total}个)")
        
        print("\n" + "=" * 60)
        
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
                
            except Exception as e:
                print(f"❌ 加载失败: {e}")
    
    def create_custom_problem(self):
        """创建自定义问题"""
        print("\n✏️ 创建自定义问题")
        print("=" * 60)
        
        create_custom_config()
        print("\n" + "=" * 60)
        
        print("\n🔄 现在开始创建自定义问题...")
        
        # 获取袋子配置
        bags_config = {}
        print("\n📦 配置袋子 (输入空行结束):")
        while True:
            bag_input = input("输入袋子ID和颜色数量 (格式: ID 颜色1:数量1 颜色2:数量2 ...): ").strip()
            if not bag_input:
                break
                
            parts = bag_input.split()
            if len(parts) < 2:
                print("❌ 格式错误，请重试")
                continue
                
            try:
                bag_id = int(parts[0])
                color_counts = {}
                
                for color_part in parts[1:]:
                    if ':' in color_part:
                        color, count = color_part.split(':')
                        color_counts[color.strip()] = int(count.strip())
                    else:
                        print(f"❌ 颜色格式错误: {color_part}")
                        continue
                
                bags_config[bag_id] = color_counts
                print(f"✅ 袋子{bag_id}配置成功: {color_counts}")
                
            except ValueError as e:
                print(f"❌ 输入格式错误: {e}")
        
        if not bags_config:
            print("⚠️  没有配置任何袋子，取消创建")
            return
        
        # 获取操作序列
        operations = []
        print("\n🔄 配置操作序列 (输入空行结束):")
        print("格式: 操作类型 袋子ID 数量 (操作类型: draw=摸, discard=丢, return=还)")
        
        op_types = {"draw": "摸", "discard": "丢", "return": "还"}
        
        while True:
            op_input = input("输入操作 (或按回车结束): ").strip()
            if not op_input:
                break
                
            parts = op_input.split()
            if len(parts) != 3:
                print("❌ 需要3个参数: 操作类型 袋子ID 数量")
                continue
                
            op_type, bag_id_str, count_str = parts
            
            if op_type not in op_types:
                print(f"❌ 无效操作类型，可用: {', '.join(op_types.keys())}")
                continue
                
            try:
                bag_id = int(bag_id_str)
                draw_count = int(count_str)
                
                if bag_id not in bags_config:
                    print(f"⚠️  袋子{bag_id}在配置中不存在")
                    continue
                    
                operations.append(
                    BallDrawOperation(
                        bag_id=bag_id,
                        draw_count=draw_count,
                        operation_type=op_type
                    )
                )
                
                print(f"✅ 添加操作: {op_types[op_type]}袋{bag_id}{draw_count}球")
                
            except ValueError as e:
                print(f"❌ 参数错误: {e}")
        
        if not operations:
            print("⚠️  没有配置任何操作，取消创建")
            return
        
        # 验证配置
        errors = self.calculator.validate_configuration(bags_config, operations)
        if errors:
            print("\n❌ 配置验证失败:")
            for error in errors:
                print(f"  - {error}")
            print("请修正配置后重试")
            return
        
        # 保存配置
        self.current_config = bags_config
        self.current_operations = operations
        self.current_description = input("\n输入问题描述 (可选): ").strip() or "自定义问题"
        
        print(f"\n✅ 自定义问题创建成功!")
        self._display_current_problem_summary()
    
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
            results = self.calculator.calculate_exact(self.current_config, self.current_operations)
            self.display_results(results, is_monte_carlo=False)
            self.save_results_to_file(results)
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
            results = self.calculator.monte_carlo_simulation(
                self.current_config, 
                self.current_operations, 
                num_simulations
            )
            
            self.display_results(results, is_monte_carlo=True)
            self.save_results_to_file(results)
            
        except ValueError as e:
            print(f"❌ 输入错误: {e}")
        except Exception as e:
            print(f"❌ 模拟失败: {e}")
    
    def display_results(self, results: Dict, is_monte_carlo: bool = False):
        """显示计算结果"""
        print("\n" + "=" * 60)
        print("📈 计算结果")
        print("=" * 60)
        
        total_states = results.get('total_states', 0)
        total_prob = results.get('total_probability', 0)
        
        print(f"📊 总状态数: {total_states:,}")
        print(f"✅ 总概率: {total_prob:.8f}")
        
        if is_monte_carlo:
            print(f"🎲 模拟方法: Monte Carlo ({results.get('simulations', 0):,}次)")
        else:
            print(f"🧮 计算方法: 精确计算")
        
        print("\n🏆 手上球的最终分布:")
        print("-" * 60)
        
        distribution = results.get('hand_distribution', {})
        sorted_items = sorted(distribution.items(), key=lambda x: x[1], reverse=True)
        
        # 显示前15种情况
        for i, (hand_desc, prob) in enumerate(sorted_items[:15]):
            percentage = prob * 100
            print(f"{i+1:2d}. {hand_desc:20s}: {prob:.6f} ({percentage:.2f}%)")
        
        print("-" * 60)
        
        # 显示统计信息
        total_results = len(distribution)
        print(f"\n📋 总共的不同结果: {total_results}种手上球的组合")
        
        if total_results > 15:
            print(f"  （显示前15种最可能的情况）")
            print(f"  最小概率: {sorted_items[-1][1]:.8f} ({sorted_items[-1][1]*100:.4f}%)")
        
        # 计算一些统计指标
        if sorted_items:
            most_likely = sorted_items[0]
            least_likely = sorted_items[-1]
            
            print(f"\n📊 统计指标:")
            print(f"  最可能结果: {most_likely[0]} ({most_likely[1]*100:.2f}%)")
            print(f"  最不可能结果: {least_likely[0]} ({least_likely[1]*100:.4f}%)")
            
            # 计算不同颜色球的期望数量
            if not is_monte_carlo:
                color_expectations = self._calculate_color_expectations(distribution)
                if color_expectations:
                    print(f"\n🎯 期望球数:")
                    for color, expectation in sorted(color_expectations.items()):
                        print(f"  {color}: {expectation:.4f}个")
    
    def _calculate_color_expectations(self, distribution: Dict[str, float]) -> Dict[str, float]:
        """计算各颜色球的期望数量"""
        color_expectations = {}
        
        for hand_desc, prob in distribution.items():
            # 解析手描述，如 "2Y+3W+1B"
            if hand_desc == "空手":
                continue
                
            parts = hand_desc.split('+')
            for part in parts:
                # 提取颜色和数量
                for i, char in enumerate(part):
                    if not char.isdigit():
                        count = int(part[:i]) if i > 0 else 1
                        color = part[i:]
                        color_expectations[color] = color_expectations.get(color, 0) + count * prob
                        break
        
        return color_expectations
    
    def save_results_to_file(self, results: Dict):
        """保存结果到文件"""
        import time
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"results_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    "problem_description": self.current_description,
                    "config": self.current_config,
                    "operations": [
                        {
                            "bag_id": op.bag_id,
                            "draw_count": op.draw_count,
                            "operation_type": op.operation_type
                        }
                        for op in self.current_operations
                    ],
                    "results": results,
                    "timestamp": timestamp
                }, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 结果已保存到文件: {filename}")
            
        except Exception as e:
            print(f"❌ 保存结果失败: {e}")
    
    def save_configuration(self):
        """保存当前配置到文件"""
        if not self.current_config:
            print("❌ 没有可保存的配置")
            return
            
        filename = input("输入保存的文件名 (默认: config.json): ").strip() or "config.json"
        
        try:
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

def main():
    """主函数"""
    app = InteractiveProbabilityApp()
    
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n\n👋 程序被用户中断")
    except Exception as e:
        print(f"\n❌ 程序出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()