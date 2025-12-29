#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多袋摸球概率计算器
一个用于计算复杂摸球问题概率的通用工具
"""

import sys
import json
from typing import List, Dict, Tuple, Optional
from probability_calculator import ProbabilityCalculator, BallDrawOperation

def main():
    print("🎯 多袋摸球概率计算器")
    print("=" * 60)
    
    # 示例配置 - 用户的问题
    print("\n📊 问题描述:")
    print("  袋子1: 3个黄球，5个白球")
    print("  袋子2: 1个蓝球，1个紫球") 
    print("  袋子3: 2个蓝球，1个黄球")
    print("  袋子4: 1个黄球，5个蓝球")
    
    print("\n🔄 操作步骤:")
    print("  1. 从袋子1摸两个球")
    print("  2. 从袋子1丢掉两个球")
    print("  3. 再从袋子1摸一个球")
    print("  4. 从袋子2摸一个球")
    print("  5. 从袋子3摸一个球")
    print("  6. 将自己手中的球放回袋子3一个")
    print("  7. 从袋子4摸两个球")
    print("  8. 放回一个球到袋子1")
    print("  9. 再从袋子1摸一个球")
    
    # 创建计算器实例
    calculator = ProbabilityCalculator()
    
    # 定义袋子初始状态
    bags_config = {
        1: {"Y": 3, "W": 5},  # 黄球3个，白球5个
        2: {"B": 1, "P": 1},  # 蓝球1个，紫球1个
        3: {"B": 2, "Y": 1},  # 蓝球2个，黄球1个
        4: {"Y": 1, "B": 5},  # 黄球1个，蓝球5个
    }
    
    # 定义操作序列
    operations = [
        BallDrawOperation(bag_id=1, draw_count=2, operation_type="draw"),
        BallDrawOperation(bag_id=1, draw_count=2, operation_type="discard"),
        BallDrawOperation(bag_id=1, draw_count=1, operation_type="draw"),
        BallDrawOperation(bag_id=2, draw_count=1, operation_type="draw"),
        BallDrawOperation(bag_id=3, draw_count=1, operation_type="draw"),
        BallDrawOperation(bag_id=3, draw_count=1, operation_type="return"),
        BallDrawOperation(bag_id=4, draw_count=2, operation_type="draw"),
        BallDrawOperation(bag_id=1, draw_count=1, operation_type="return"),
        BallDrawOperation(bag_id=1, draw_count=1, operation_type="draw"),
    ]
    
    print("\n🧮 正在计算概率...")
    
    # 计算方法选择
    print("\n请选择计算方法:")
    print("  1. 精确计算（组合数学）")
    print("  2. 蒙特卡洛模拟（快速近似）")
    choice = input("请输入选择 (1或2): ").strip()
    
    if choice == "1":
        # 精确计算
        print("\n🔢 使用精确组合数学方法计算...")
        try:
            results = calculator.calculate_exact(bags_config, operations)
            display_results(results)
        except Exception as e:
            print(f"\n❌ 精确计算失败: {e}")
            print("  尝试使用蒙特卡洛模拟...")
            results = calculator.monte_carlo_simulation(bags_config, operations, num_simulations=100000)
            display_results(results, is_monte_carlo=True)
    else:
        # 蒙特卡洛模拟
        num_simulations = input("请输入模拟次数（默认100000）: ").strip()
        num_simulations = int(num_simulations) if num_simulations else 100000
        
        print(f"\n🎲 使用蒙特卡洛模拟方法，模拟次数: {num_simulations}")
        results = calculator.monte_carlo_simulation(bags_config, operations, num_simulations)
        display_results(results, is_monte_carlo=True)
    
    print("\n📁 结果已保存到文件:")
    print("  - results.json (JSON格式)")
    print("  - results_summary.txt (文本摘要)")
    
    # 保存结果到文件
    save_results(results)

def display_results(results: Dict, is_monte_carlo: bool = False):
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
    
    print("\n🏆 手上球的最终分布 (前10种最可能的情况):")
    print("-" * 60)
    
    distribution = results.get('hand_distribution', {})
    sorted_items = sorted(distribution.items(), key=lambda x: x[1], reverse=True)
    
    # 显示前10种情况
    for i, (hand_desc, prob) in enumerate(sorted_items[:10]):
        percentage = prob * 100
        print(f"{i+1:2d}. {hand_desc:20s}: {prob:.8f} ({percentage:.4f}%)")
    
    print("-" * 60)
    
    # 显示所有可能的结果数量
    print(f"\n📋 总共的不同结果: {len(distribution)}种手上球的组合")
    
    # 如果结果太多，显示更多统计信息
    if len(distribution) > 10:
        print(f"  显示前10种最可能的情况")
        print(f"  最小概率: {sorted_items[-1][1]:.10f} ({sorted_items[-1][1]*100:.6f}%)")
    
    # 验证总概率
    total_calculated = sum(distribution.values())
    if abs(total_calculated - 1.0) > 0.0001:
        print(f"\n⚠️  注意：总概率不等于1 ({total_calculated:.8f})")
        print(f"  可能原因：舍入误差或计算近似")

def save_results(results: Dict):
    """保存结果到文件"""
    # 保存为JSON
    with open('results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 保存文本摘要
    with open('results_summary.txt', 'w', encoding='utf-8') as f:
        f.write("多袋摸球概率计算结果汇总\n")
        f.write("=" * 50 + "\n\n")
        
        f.write(f"总状态数: {results.get('total_states', 0):,}\n")
        f.write(f"总概率: {results.get('total_probability', 0):.10f}\n\n")
        
        f.write("手上球的最终分布:\n")
        f.write("-" * 50 + "\n")
        
        distribution = results.get('hand_distribution', {})
        sorted_items = sorted(distribution.items(), key=lambda x: x[1], reverse=True)
        
        for hand_desc, prob in sorted_items:
            percentage = prob * 100
            f.write(f"{hand_desc:20s}: {prob:.10f} ({percentage:.6f}%)\n")
        
        f.write("\n" + "=" * 50 + "\n")
        f.write(f"总共的不同结果: {len(distribution)}种手上球的组合\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 程序被用户中断")
    except Exception as e:
        print(f"\n❌ 程序出错: {e}")
        import traceback
        traceback.print_exc()
