"""
显示模块

负责所有显示相关的功能，包括结果显示、进度显示等
"""

import sys
import time
from typing import Dict, List, Optional, Callable

def display_example_problems():
    """显示示例问题列表"""
    try:
        from config.examples import EXAMPLE_PROBLEMS
        
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
        
    except ImportError:
        print("❌ 示例模块未找到")

def display_calculation_progress(current: int, total: int, message: str = ""):
    """显示精确计算进度"""
    if total > 0:
        percentage = (current / total) * 100
        bar_length = 40
        filled_length = int(bar_length * current // total)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        sys.stdout.write(f'\r🔢 计算进度: |{bar}| {percentage:.1f}% ({current}/{total}) {message}')
        sys.stdout.flush()
        
        if current == total:
            print()  # 换行

def display_simulation_progress(current: int, total: int):
    """显示蒙特卡洛模拟进度"""
    if total > 0:
        percentage = (current / total) * 100
        bar_length = 40
        filled_length = int(bar_length * current // total)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        sys.stdout.write(f'\r🎲 模拟进度: |{bar}| {percentage:.1f}% ({current:,}/{total:,})')
        sys.stdout.flush()
        
        if current == total:
            print()  # 换行
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
            color_expectations = _calculate_color_expectations(distribution)
            if color_expectations:
                print(f"\n🎯 期望球数:")
                for color, expectation in sorted(color_expectations.items()):
                    print(f"  {color}: {expectation:.4f}个")
    
    # 显示袋子状态分布（新功能）
    bag_distributions = results.get('bag_distributions', {})
    if bag_distributions:
        print(f"\n📦 袋子最终状态分布:")
        print("=" * 60)
        
        for bag_id, bag_dist in sorted(bag_distributions.items()):
            print(f"\n袋子{bag_id}状态分布:")
            print("-" * 40)
            
            # 按概率排序
            sorted_bag_states = sorted(bag_dist.items(), key=lambda x: x[1], reverse=True)
            
            # 显示前10种最可能的状态
            for i, (bag_state_str, prob) in enumerate(sorted_bag_states[:10]):
                percentage = prob * 100
                print(f"  {i+1:2d}. {bag_state_str:30s}: {prob:.6f} ({percentage:.2f}%)")
            
            if len(sorted_bag_states) > 10:
                print(f"  ... 和其他 {len(sorted_bag_states) - 10} 种状态")
            
            # 显示袋子状态的统计信息
            if sorted_bag_states:
                total_bag_prob = sum(prob for _, prob in sorted_bag_states)
                print(f"  袋子{bag_id}总概率: {total_bag_prob:.8f}")
                print(f"  不同状态数: {len(sorted_bag_states)}")

def _calculate_color_expectations(distribution: Dict[str, float]) -> Dict[str, float]:
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

def display_problem_summary(description: str, config: Dict, operations: List):
    """显示问题摘要"""
    print("\n📋 问题摘要:")
    print("=" * 60)
    print(f"描述: {description}")
    print(f"袋子数: {len(config)}")
    
    for bag_id, colors in config.items():
        total = sum(colors.values())
        color_str = ", ".join(f"{count}{color}" for color, count in colors.items())
        print(f"  袋子{bag_id}: {color_str} (共{total}个球)")
    
    print(f"\n操作序列 ({len(operations)}个操作):")
    for i, op in enumerate(operations, 1):
        action = {"draw": "摸", "discard": "丢", "return": "还"}[op.operation_type]
        print(f"  {i}. {action}袋{op.bag_id} {op.draw_count}个球")

def display_error(message: str, details: str = ""):
    """显示错误信息"""
    print(f"\n❌ 错误: {message}")
    if details:
        print(f"   详情: {details}")

def display_success(message: str):
    """显示成功信息"""
    print(f"\n✅ {message}")

def display_warning(message: str):
    """显示警告信息"""
    print(f"\n⚠️  警告: {message}")

def display_info(message: str):
    """显示一般信息"""
    print(f"\nℹ️  {message}")

def display_file_list(files: List[str], title: str = "文件列表"):
    """显示文件列表"""
    print(f"\n📁 {title}:")
    print("-" * 60)
    
    if not files:
        print("  没有文件")
        return
    
    for i, file in enumerate(files, 1):
        print(f"  {i:2d}. {file}")