"""
配置向导程序
让用户轻松配置复杂的摸球问题
"""

import json
import os
from typing import Dict, List, Any
from datetime import datetime

class ConfigWizard:
    """配置向导类"""
    
    def __init__(self):
        self.config = {
            "description": "",
            "bags_config": {},
            "operations": [],
            "created_at": datetime.now().isoformat()
        }
    
    def run(self):
        """运行配置向导"""
        print("🎯 摸球问题配置向导")
        print("=" * 60)
        print("欢迎使用摸球问题配置向导！")
        print("我们将分步引导您配置一个完整的摸球问题。")
        print()
        
        # 1. 问题描述
        self.configure_description()
        
        # 2. 袋子配置
        self.configure_bags()
        
        # 3. 操作配置
        self.configure_operations()
        
        # 4. 验证配置
        self.validate_configuration()
        
        # 5. 保存配置
        filename = self.save_configuration()
        
        # 6. 选择是否立即计算
        self.ask_calculation(filename)
    
    def configure_description(self):
        """配置问题描述"""
        print("\n📝 步骤1: 问题描述")
        print("-" * 40)
        print("请为这个摸球问题提供一个描述：")
        print("例如：'复杂4袋摸球问题' 或 '概率学习测试'")
        
        description = input("\n输入问题描述: ").strip()
        if not description:
            description = "自定义摸球问题"
        
        self.config["description"] = description
        print(f"✅ 已设置问题描述: {description}")
    
    def configure_bags(self):
        """配置袋子"""
        print("\n📦 步骤2: 配置袋子")
        print("-" * 40)
        print("现在配置袋子。每个袋子可以包含不同颜色的球。")
        print("颜色可以是任意字符串，如 '红', '蓝', '黄', 'W', 'B' 等。")
        print()
        
        while True:
            try:
                num_bags = int(input("请输入袋子数量 (1-10): ").strip())
                if 1 <= num_bags <= 10:
                    break
                else:
                    print("❌ 请输入1到10之间的数字")
            except ValueError:
                print("❌ 请输入有效的数字")
        
        for bag_id in range(1, num_bags + 1):
            self.configure_single_bag(bag_id)
        
        print(f"\n✅ 已配置 {num_bags} 个袋子")
    
    def configure_single_bag(self, bag_id: int):
        """配置单个袋子"""
        print(f"\n  📍 配置袋子 {bag_id}")
        print("  " + "-" * 30)
        
        color_counts = {}
        
        while True:
            color = input(f"  输入颜色名称 (输入空行结束颜色添加): ").strip()
            if not color:
                if color_counts:
                    break
                else:
                    print("  至少需要一种颜色！")
                    continue
            
            while True:
                try:
                    count = int(input(f"  输入颜色 '{color}' 的数量: ").strip())
                    if count <= 0:
                        print("  数量必须为正数！")
                        continue
                    color_counts[color] = count
                    print(f"  ✅ 已添加: {count}个{color}球")
                    break
                except ValueError:
                    print("  ❌ 请输入有效的数字")
        
        self.config["bags_config"][bag_id] = color_counts
        
        # 显示袋子摘要
        total = sum(color_counts.values())
        colors_str = ", ".join(f"{count}{color}" for color, count in color_counts.items())
        print(f"  📊 袋子{bag_id}摘要: {colors_str} (共{total}个球)")
    
    def configure_operations(self):
        """配置操作序列"""
        print("\n🔄 步骤3: 配置操作序列")
        print("-" * 40)
        print("现在配置每一步操作。最多支持10步操作。")
        print("可用操作类型:")
        print("  1. 摸球 (draw) - 从指定袋子随机摸球")
        print("  2. 丢袋球 (discard_bag) - 从指定袋子随机丢球")
        print("  3. 丢手球 (discard_hand) - 从手中随机丢球")
        print("  4. 放回球 (return) - 从手中随机放回球到指定袋子")
        print()
        
        max_steps = 10
        step_count = 0
        
        while step_count < max_steps:
            print(f"\n  步骤 {step_count + 1}/{max_steps}")
            print("  输入 'done' 结束配置，'back' 返回上一步")
            
            operation = self.configure_single_operation()
            
            if operation is None:  # 用户输入 'back'
                if step_count > 0:
                    # 删除上一步操作
                    self.config["operations"].pop()
                    step_count -= 1
                    print("  ↩️ 已删除上一步操作")
                else:
                    print("  ℹ️ 没有上一步可返回")
                continue
            
            if operation == "done":
                print("  ✅ 操作配置完成")
                break
            
            self.config["operations"].append(operation)
            step_count += 1
        
        if step_count >= max_steps:
            print(f"\n⚠️  已达到最大步骤数 ({max_steps})")
        
        print(f"\n✅ 已配置 {len(self.config['operations'])} 个操作")
    
    def configure_single_operation(self) -> Dict[str, Any]:
        """配置单个操作"""
        while True:
            print("\n    选择操作类型:")
            print("      1. 摸球 (从袋子中随机摸球)")
            print("      2. 丢袋球 (从袋子中随机丢球)")
            print("      3. 丢手球 (从手中随机丢球)")
            print("      4. 放回球 (从手中放回球到袋子)")
            print("      输入 'done' 完成, 'back' 返回上一步")
            
            choice = input("\n    输入选择 (1-4): ").strip().lower()
            
            if choice == 'done':
                return "done"
            elif choice == 'back':
                return None
            
            if choice not in ['1', '2', '3', '4']:
                print("    ❌ 无效选择，请重试")
                continue
            
            # 获取操作类型
            op_types = {
                '1': {"type": "draw", "name": "摸球"},
                '2': {"type": "discard_bag", "name": "丢袋球"},
                '3': {"type": "discard_hand", "name": "丢手球"},
                '4': {"type": "return", "name": "放回球"}
            }
            
            op_info = op_types[choice]
            
            # 获取袋子ID（如果需要）
            bag_id = None
            if op_info["type"] in ["draw", "discard_bag", "return"]:
                bag_id = self.get_bag_id()
                if bag_id is None:
                    continue
            
            # 获取数量
            count = self.get_ball_count(op_info["name"])
            if count is None:
                continue
            
            operation = {
                "operation_type": op_info["type"],
                "bag_id": bag_id,
                "draw_count": count
            }
            
            # 显示操作摘要
            self.display_operation_summary(operation)
            
            confirm = input("\n    确认添加此操作？ (y/N): ").strip().lower()
            if confirm == 'y':
                return operation
            else:
                print("    ⏪ 取消，重新选择")
    
    def get_bag_id(self) -> int:
        """获取袋子ID"""
        available_bags = list(self.config["bags_config"].keys())
        
        print(f"\n    可用的袋子: {available_bags}")
        
        while True:
            try:
                bag_id = int(input("    输入袋子ID: ").strip())
                if bag_id in available_bags:
                    return bag_id
                else:
                    print(f"    ❌ 袋子{bag_id}不存在")
            except ValueError:
                print("    ❌ 请输入有效的数字")
    
    def get_ball_count(self, operation_name: str) -> int:
        """获取球的数量"""
        while True:
            try:
                count = int(input(f"    {operation_name}数量: ").strip())
                if count > 0:
                    return count
                else:
                    print("    ❌ 数量必须为正数")
            except ValueError:
                print("    ❌ 请输入有效的数字")
    
    def display_operation_summary(self, operation: Dict[str, Any]):
        """显示操作摘要"""
        op_type = operation["operation_type"]
        count = operation["draw_count"]
        bag_id = operation.get("bag_id")
        
        descriptions = {
            "draw": f"从袋子{bag_id}随机摸{count}个球",
            "discard_bag": f"从袋子{bag_id}随机丢{count}个球",
            "discard_hand": f"从手中随机丢{count}个球",
            "return": f"从手中随机放回{count}个球到袋子{bag_id}"
        }
        
        print(f"\n    📋 操作摘要: {descriptions.get(op_type, '未知操作')}")
    
    def validate_configuration(self):
        """验证配置"""
        print("\n🔍 步骤4: 验证配置")
        print("-" * 40)
        
        errors = []
        
        # 检查袋子配置
        if not self.config["bags_config"]:
            errors.append("没有配置任何袋子")
        
        # 检查操作序列
        if not self.config["operations"]:
            errors.append("没有配置任何操作")
        
        # 检查操作引用的袋子是否存在
        for i, op in enumerate(self.config["operations"]):
            if "bag_id" in op and op["bag_id"] not in self.config["bags_config"]:
                errors.append(f"操作{i+1}引用不存在的袋子{op['bag_id']}")
        
        if errors:
            print("❌ 配置验证失败:")
            for error in errors:
                print(f"  - {error}")
            print("\n请修正配置后重试")
            return False
        else:
            print("✅ 配置验证通过")
            return True
    
    def save_configuration(self) -> str:
        """保存配置到文件"""
        print("\n💾 步骤5: 保存配置")
        print("-" * 40)
        
        default_filename = "user_problem.json"
        filename = input(f"输入保存的文件名 (默认: {default_filename}): ").strip()
        if not filename:
            filename = default_filename
        
        # 确保文件名以.json结尾
        if not filename.endswith('.json'):
            filename += '.json'
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 配置已保存到: {filename}")
            
            # 显示配置摘要
            self.display_config_summary()
            
            return filename
            
        except Exception as e:
            print(f"❌ 保存失败: {e}")
            return ""
    
    def display_config_summary(self):
        """显示配置摘要"""
        print("\n📊 配置摘要:")
        print("=" * 60)
        print(f"问题描述: {self.config['description']}")
        
        print(f"\n袋子配置 ({len(self.config['bags_config'])}个袋子):")
        for bag_id, colors in self.config["bags_config"].items():
            total = sum(colors.values())
            colors_str = ", ".join(f"{count}{color}" for color, count in colors.items())
            print(f"  袋子{bag_id}: {colors_str} (共{total}个球)")
        
        print(f"\n操作序列 ({len(self.config['operations'])}个操作):")
        for i, op in enumerate(self.config["operations"], 1):
            op_type = op["operation_type"]
            count = op["draw_count"]
            bag_id = op.get("bag_id", "N/A")
            
            descriptions = {
                "draw": f"从袋子{bag_id}随机摸{count}个球",
                "discard_bag": f"从袋子{bag_id}随机丢{count}个球",
                "discard_hand": f"从手中随机丢{count}个球",
                "return": f"从手中随机放回{count}个球到袋子{bag_id}"
            }
            
            print(f"  {i}. {descriptions.get(op_type, '未知操作')}")
        
        print("\n" + "=" * 60)
    
    def ask_calculation(self, config_filename: str = ""):
        """询问是否立即计算"""
        if not config_filename:
            return
        
        print("\n🧮 步骤6: 立即计算")
        print("-" * 40)
        print("是否立即使用此配置进行计算？")
        print("请选择计算方法：")
        print("  1. 精确计算（组合数学）")
        print("  2. 蒙特卡洛模拟")
        print("  3. 稍后手动计算")
        print("  4. 重新配置")
        
        while True:
            choice = input("\n输入选择 (1-4): ").strip()
            
            if choice == '1':
                self.run_exact_calculation(config_filename)
                break
            elif choice == '2':
                self.run_monte_carlo(config_filename)
                break
            elif choice == '3':
                print("您可以在稍后使用以下命令进行计算：")
                print(f"  python calculate_from_file.py {config_filename}")
                print("或者使用交互式应用程序加载此配置文件。")
                break
            elif choice == '4':
                print("请重新运行配置向导。")
                break
            else:
                print("❌ 无效选择，请重试")
    
    def run_exact_calculation(self, config_filename: str):
        """运行精确计算"""
        print(f"\n🔢 开始精确计算...")
        print("正在加载配置...")
        
        try:
            from probability_calculator import ProbabilityCalculator, BallDrawOperation
            
            # 加载配置
            with open(config_filename, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            bags_config = config["bags_config"]
            operations_data = config["operations"]
            
            # 转换为操作对象
            operations = []
            for op_data in operations_data:
                # 转换操作类型到兼容格式
                op_type = op_data["operation_type"]
                if op_type == "discard_bag":
                    # discard_bag 转换为特殊的操作类型
                    operations.append(BallDrawOperation(
                        bag_id=op_data["bag_id"],
                        draw_count=op_data["draw_count"],
                        operation_type="discard"  # 使用现有的discard类型
                    ))
                elif op_type == "discard_hand":
                    # discard_hand 需要特殊处理，暂时不支持
                    print(f"⚠️  暂不支持 'discard_hand' 操作，跳过操作: {op_data}")
                    continue
                else:
                    operations.append(BallDrawOperation(
                        bag_id=op_data.get("bag_id", 1),
                        draw_count=op_data["draw_count"],
                        operation_type=op_type
                    ))
            
            if not operations:
                print("❌ 没有有效的操作，无法计算")
                return
            
            # 创建计算器
            calculator = ProbabilityCalculator()
            
            print("开始计算...（可能需要一些时间）")
            results = calculator.calculate_exact(bags_config, operations)
            
            # 显示结果
            self.display_calculation_results(results, "精确计算")
            
            # 保存结果
            self.save_calculation_results(results, config, "exact")
            
        except Exception as e:
            print(f"❌ 计算失败: {e}")
            import traceback
            traceback.print_exc()
    
    def run_monte_carlo(self, config_filename: str):
        """运行蒙特卡洛模拟"""
        print(f"\n🎲 开始蒙特卡洛模拟...")
        print("正在加载配置...")
        
        try:
            # 获取模拟次数
            while True:
                try:
                    num_sim = input("输入模拟次数 (默认100000): ").strip()
                    num_simulations = int(num_sim) if num_sim else 100000
                    if num_simulations > 0:
                        break
                    else:
                        print("❌ 模拟次数必须为正数")
                except ValueError:
                    print("❌ 请输入有效的数字")
            
            from probability_calculator import ProbabilityCalculator, BallDrawOperation
            
            # 加载配置
            with open(config_filename, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            bags_config = config["bags_config"]
            operations_data = config["operations"]
            
            # 转换为操作对象（简化处理，主要支持draw/discard/return）
            operations = []
            for op_data in operations_data:
                op_type = op_data["operation_type"]
                if op_type == "discard_bag":
                    operations.append(BallDrawOperation(
                        bag_id=op_data["bag_id"],
                        draw_count=op_data["draw_count"],
                        operation_type="discard"
                    ))
                elif op_type in ["draw", "return"]:
                    operations.append(BallDrawOperation(
                        bag_id=op_data.get("bag_id", 1),
                        draw_count=op_data["draw_count"],
                        operation_type=op_type
                    ))
                else:
                    print(f"⚠️  蒙特卡洛模拟暂不支持 '{op_type}' 操作，跳过")
            
            if not operations:
                print("❌ 没有有效的操作，无法计算")
                return
            
            # 创建计算器
            calculator = ProbabilityCalculator()
            
            print(f"开始 {num_simulations:,} 次模拟...")
            results = calculator.monte_carlo_simulation(bags_config, operations, num_simulations)
            
            # 显示结果
            self.display_calculation_results(results, "蒙特卡洛模拟")
            
            # 保存结果
            self.save_calculation_results(results, config, "monte_carlo", num_simulations)
            
        except Exception as e:
            print(f"❌ 模拟失败: {e}")
            import traceback
            traceback.print_exc()
    
    def display_calculation_results(self, results: Dict[str, Any], method_name: str):
        """显示计算结果"""
        print("\n" + "=" * 70)
        print(f"📈 {method_name} 结果")
        print("=" * 70)
        
        total_states = results.get('total_states', 0)
        total_prob = results.get('total_probability', 0)
        
        print(f"📊 总状态数: {total_states:,}")
        print(f"✅ 总概率: {total_prob:.8f}")
        
        if 'simulations' in results:
            print(f"🎲 模拟次数: {results['simulations']:,}")
        
        print("\n🏆 手上球的最终分布 (按概率排序):")
        print("-" * 70)
        
        distribution = results.get('hand_distribution', {})
        sorted_items = sorted(distribution.items(), key=lambda x: x[1], reverse=True)
        
        for i, (hand_desc, prob) in enumerate(sorted_items[:20], 1):
            percentage = prob * 100
            print(f"{i:2d}. {hand_desc:25s}: {prob:.6f} ({percentage:.2f}%)")
        
        if len(sorted_items) > 20:
            print(f"  ... 还有 {len(sorted_items) - 20} 种结果")
        
        print("-" * 70)
        print(f"📋 总共的不同结果: {len(distribution)}种手上球的组合")
    
    def save_calculation_results(self, results: Dict[str, Any], config: Dict[str, Any], 
                                method: str, simulations: int = 0):
        """保存计算结果"""
        import time
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"results_{method}_{timestamp}.json"
        
        try:
            results_data = {
                "problem_description": config.get("description", ""),
                "config": config,
                "results": results,
                "calculation_method": method,
                "simulations": simulations,
                "calculated_at": timestamp
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results_data, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 计算结果已保存到: {filename}")
            
        except Exception as e:
            print(f"❌ 保存结果失败: {e}")

def main():
    """主函数"""
    wizard = ConfigWizard()
    
    try:
        wizard.run()
    except KeyboardInterrupt:
        print("\n\n👋 配置被用户中断")
    except Exception as e:
        print(f"\n❌ 配置向导出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()