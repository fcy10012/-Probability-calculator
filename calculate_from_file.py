"""
从配置文件计算摸球问题的概率
"""

import json
import sys
import os
from typing import Dict, List
from probability_calculator import ProbabilityCalculator, BallDrawOperation

def load_configuration(filename: str) -> Dict:
    """加载配置文件"""
    if not os.path.exists(filename):
        print(f"❌ 文件不存在: {filename}")
        return None
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print(f"✅ 配置文件加载成功: {filename}")
        print(f"📝 问题描述: {config.get('description', '无描述')}")
        return config
    
    except Exception as e:
        print(f"❌ 加载配置文件失败: {e}")
        return None

def validate_configuration(config: Dict) -> bool:
    """验证配置"""
    errors = []
    
    # 检查必需字段
    if "bags_config" not in config:
        errors.append("缺少 'bags_config' 字段")
    
    if "operations" not in config:
        errors.append("缺少 'operations' 字段")
    
    if errors:
        print("❌ 配置验证失败:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    # 检查袋子配置
    bags_config = config["bags_config"]
    if not isinstance(bags_config, dict) or not bags_config:
        errors.append("'bags_config' 必须是非空字典")
    
    # 检查操作序列
    operations = config["operations"]
    if not isinstance(operations, list):
        errors.append("'operations' 必须是列表")
    
    if errors:
        print("❌ 配置验证失败:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    return True

def convert_operations(operations_data: List[Dict]) -> List[BallDrawOperation]:
    """转换操作数据到操作对象"""
    operations = []
    
    for i, op_data in enumerate(operations_data, 1):
        try:
            op_type = op_data.get("operation_type", "")
            draw_count = op_data.get("draw_count", 0)
            bag_id = op_data.get("bag_id", 1)
            
            if not op_type:
                print(f"⚠️  操作{i}缺少 'operation_type'，跳过")
                continue
            
            if draw_count <= 0:
                print(f"⚠️  操作{i}的 'draw_count' 必须为正数，跳过")
                continue
            
            # 处理不同类型的操作
            if op_type == "discard_bag":
                # discard_bag 转换为 discard
                operations.append(BallDrawOperation(
                    bag_id=bag_id,
                    draw_count=draw_count,
                    operation_type="discard"
                ))
            elif op_type in ["draw", "return"]:
                operations.append(BallDrawOperation(
                    bag_id=bag_id,
                    draw_count=draw_count,
                    operation_type=op_type
                ))
            elif op_type == "discard_hand":
                print(f"⚠️  操作{i}: 暂不支持 'discard_hand' 操作类型，跳过")
                continue
            else:
                print(f"⚠️  操作{i}: 未知的操作类型 '{op_type}'，跳过")
                continue
            
        except Exception as e:
            print(f"⚠️  操作{i}转换失败: {e}，跳过")
    
    return operations

def run_exact_calculation(bags_config: Dict, operations: List[BallDrawOperation]) -> Dict:
    """运行精确计算"""
    print("\n🔢 开始精确计算...")
    print("这可能需要一些时间，具体取决于问题的复杂性。")
    
    calculator = ProbabilityCalculator()
    results = calculator.calculate_exact(bags_config, operations)
    
    return results

def run_monte_carlo(bags_config: Dict, operations: List[BallDrawOperation], 
                   num_simulations: int = 100000) -> Dict:
    """运行蒙特卡洛模拟"""
    print(f"\n🎲 开始蒙特卡洛模拟...")
    print(f"模拟次数: {num_simulations:,}")
    
    calculator = ProbabilityCalculator()
    results = calculator.monte_carlo_simulation(bags_config, operations, num_simulations)
    
    return results

def display_results(results: Dict, method_name: str, config_description: str = ""):
    """显示计算结果"""
    print("\n" + "=" * 70)
    print(f"📈 计算结果 - {method_name}")
    if config_description:
        print(f"📝 问题: {config_description}")
    print("=" * 70)
    
    total_states = results.get('total_states', 0)
    total_prob = results.get('total_probability', 0)
    
    print(f"📊 总状态数: {total_states:,}")
    print(f"✅ 总概率: {total_prob:.8f}")
    
    if 'simulations' in results:
        print(f"🎲 模拟次数: {results['simulations']:,}")
    
    print("\n🏆 手上球的最终分布 (前20种最可能的情况):")
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
    
    # 显示最可能和最小可能的结果
    if sorted_items:
        most_likely = sorted_items[0]
        least_likely = sorted_items[-1]
        
        print(f"\n📊 统计指标:")
        print(f"  最可能结果: {most_likely[0]} ({most_likely[1]*100:.2f}%)")
        print(f"  最不可能结果: {least_likely[0]} ({least_likely[1]*100:.4f}%)")

def save_results(results: Dict, config: Dict, method: str, simulations: int = 0):
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
    print("🎲 从文件计算摸球问题的概率")
    print("=" * 60)
    
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python calculate_from_file.py <配置文件.json> [计算方法] [模拟次数]")
        print()
        print("参数说明:")
        print("  <配置文件.json> - 配置文件路径（必需）")
        print("  [计算方法]      - 'exact'（精确计算）或 'monte'（蒙特卡洛模拟），默认为'monte'")
        print("  [模拟次数]      - 蒙特卡洛模拟的次数，默认为100000")
        print()
        print("示例:")
        print("  python calculate_from_file.py user_problem.json exact")
        print("  python calculate_from_file.py user_problem.json monte 500000")
        print()
        print("要创建配置文件，请运行:")
        print("  python config_wizard.py")
        return
    
    # 获取参数
    config_file = sys.argv[1]
    calculation_method = sys.argv[2] if len(sys.argv) > 2 else "monte"
    
    if calculation_method not in ["exact", "monte"]:
        print(f"❌ 未知的计算方法: {calculation_method}")
        print("可用方法: 'exact' (精确计算) 或 'monte' (蒙特卡洛模拟)")
        return
    
    # 加载配置文件
    config = load_configuration(config_file)
    if config is None:
        return
    
    # 验证配置
    if not validate_configuration(config):
        return
    
    # 转换操作
    operations_data = config["operations"]
    operations = convert_operations(operations_data)
    
    if not operations:
        print("❌ 没有有效的操作，无法计算")
        return
    
    print(f"\n📊 配置摘要:")
    print(f"  袋子数量: {len(config['bags_config'])}")
    print(f"  操作数量: {len(operations)}")
    
    # 运行计算
    if calculation_method == "exact":
        results = run_exact_calculation(config["bags_config"], operations)
        method_name = "精确计算"
    else:  # monte
        # 获取模拟次数
        num_simulations = 100000
        if len(sys.argv) > 3:
            try:
                num_simulations = int(sys.argv[3])
            except ValueError:
                print(f"⚠️  无效的模拟次数，使用默认值: {num_simulations}")
        
        results = run_monte_carlo(config["bags_config"], operations, num_simulations)
        method_name = f"蒙特卡洛模拟 ({num_simulations:,}次)"
    
    # 显示结果
    description = config.get("description", "")
    display_results(results, method_name, description)
    
    # 保存结果
    save_results(results, config, calculation_method, 
                num_simulations if calculation_method == "monte" else 0)
    
    print(f"\n🎉 计算完成！")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 程序被用户中断")
    except Exception as e:
        print(f"\n❌ 程序出错: {e}")
        import traceback
        traceback.print_exc()