"""
多袋摸球概率计算器核心模块
提供精确计算和蒙特卡洛模拟两种方法
"""
import math
import random
import itertools
from typing import Dict, List, Tuple, Set, Optional, Any
from dataclasses import dataclass
from collections import defaultdict, Counter

# numpy是可选的，只用于某些高级功能
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    # 创建一个简单的替代
    class np:
        @staticmethod
        def random():
            return random

@dataclass
class BallDrawOperation:
    """摸球操作定义"""
    bag_id: int  # 袋子编号
    draw_count: int  # 摸球数量
    operation_type: str  # "draw": 摸球, "discard": 丢球, "return": 放回
    
    def __repr__(self):
        action_map = {
            "draw": "摸",
            "discard": "丢", 
            "return": "还"
        }
        return f"{action_map.get(self.operation_type, self.operation_type)}袋{self.bag_id}{self.draw_count}球"

class BagState:
    """袋子状态类"""
    def __init__(self, color_counts: Dict[str, int]):
        self.color_counts = color_counts.copy()
        self.total_balls = sum(color_counts.values())
        
    def copy(self):
        """创建副本"""
        return BagState(self.color_counts)
    
    def has_enough_balls(self, count: int) -> bool:
        """检查是否有足够数量的球"""
        return self.total_balls >= count
    
    def draw_balls(self, count: int) -> List[Tuple[List[str], float]]:
        """
        从袋子中摸count个球的所有可能结果及概率
        
        返回: [(球的颜色列表, 概率), ...]
        """
        if count > self.total_balls:
            return [([], 1.0)]  # 无法摸球
            
        results = []
        
        # 生成所有可能的颜色组合
        colors = list(self.color_counts.keys())
        
        def generate_combinations(remaining_colors_idx, remaining_count, current_combination, current_counts):
            if remaining_count == 0:
                # 计算这种组合的概率
                prob = 1.0
                total_choose = self.total_balls
                remaining_choose = count
                
                # 计算多项组合概率：∏ C(n_i, k_i) / C(N, K)
                numerator = 1
                for color_idx, take in enumerate(current_counts):
                    if take > 0:
                        color = colors[color_idx]
                        numerator *= math.comb(self.color_counts[color], take)
                
                denominator = math.comb(self.total_balls, count)
                prob = numerator / denominator if denominator > 0 else 0
                
                if prob > 0:
                    # 生成球的颜色列表
                    balls = []
                    for color_idx, take in enumerate(current_counts):
                        balls.extend([colors[color_idx]] * take)
                    results.append((balls, prob))
                return
            
            if remaining_colors_idx >= len(colors):
                return
                
            color = colors[remaining_colors_idx]
            max_take = min(self.color_counts[color], remaining_count)
            
            for take in range(max_take + 1):
                new_counts = current_counts[:]
                new_counts.append(take)
                generate_combinations(
                    remaining_colors_idx + 1, 
                    remaining_count - take, 
                    current_combination, 
                    new_counts
                )
        
        generate_combinations(0, count, [], [])
        return results
    
    def remove_balls(self, colors: List[str]):
        """从袋子中移除指定颜色的球"""
        for color in colors:
            if color in self.color_counts and self.color_counts[color] > 0:
                self.color_counts[color] -= 1
                self.total_balls -= 1
    
    def add_ball(self, color: str):
        """向袋子中添加一个球"""
        if color not in self.color_counts:
            self.color_counts[color] = 0
        self.color_counts[color] += 1
        self.total_balls += 1
    
    def __repr__(self):
        return f"BagState({self.color_counts})"

class ProbabilityCalculator:
    """概率计算器主类"""
    
    def __init__(self):
        self.states_cache = {}  # 状态缓存，避免重复计算
        
    def calculate_exact(self, bags_config: Dict[int, Dict[str, int]], 
                       operations: List[BallDrawOperation]) -> Dict[str, Any]:
        """
        精确计算（状态空间遍历）
        
        参数:
            bags_config: 袋子配置 {袋子ID: {颜色: 数量}}
            operations: 操作序列
            
        返回:
            结果字典
        """
        print("开始精确计算...")
        
        # 初始化袋子状态
        bags = {bag_id: BagState(color_counts) for bag_id, color_counts in bags_config.items()}
        
        # 初始状态：空手，概率1.0
        initial_state = {
            "hand": Counter(),  # 手中的球 Counter对象
            "bags": bags,      # 袋子状态字典
            "prob": 1.0,       # 当前状态概率
            "path": []         # 路径记录（用于调试）
        }
        
        # 状态列表，每个元素是(hand_counter, bags_dict, probability)
        states = [initial_state]
        
        total_states_processed = 0
        
        for op_idx, operation in enumerate(operations):
            print(f"  处理操作 {op_idx+1}/{len(operations)}: {operation}")
            new_states = []
            
            for state in states:
                bags = {bag_id: bag.copy() for bag_id, bag in state["bags"].items()}
                hand_counter = Counter(state["hand"])
                current_prob = state["prob"]
                
                if operation.operation_type == "draw":
                    # 摸球操作
                    bag = bags[operation.bag_id]
                    possible_draws = bag.draw_balls(operation.draw_count)
                    
                    for balls_drawn, draw_prob in possible_draws:
                        if draw_prob <= 0:
                            continue
                            
                        new_bags = {bag_id: bag.copy() for bag_id, bag in bags.items()}
                        new_hand = Counter(hand_counter)
                        
                        # 从袋子中移除摸到的球
                        new_bags[operation.bag_id].remove_balls(balls_drawn)
                        
                        # 将球加入手中
                        for ball in balls_drawn:
                            new_hand[ball] += 1
                        
                        new_prob = current_prob * draw_prob
                        
                        new_states.append({
                            "hand": new_hand,
                            "bags": new_bags,
                            "prob": new_prob,
                            "path": state["path"] + [f"draw{operation.bag_id}:{balls_drawn}"]
                        })
                        
                elif operation.operation_type == "discard":
                    # 丢球操作（从袋子中丢）
                    bag = bags[operation.bag_id]
                    possible_discards = bag.draw_balls(operation.draw_count)
                    
                    for balls_discarded, discard_prob in possible_discards:
                        if discard_prob <= 0:
                            continue
                            
                        new_bags = {bag_id: bag.copy() for bag_id, bag in bags.items()}
                        
                        # 从袋子中移除丢弃的球
                        new_bags[operation.bag_id].remove_balls(balls_discarded)
                        
                        new_prob = current_prob * discard_prob
                        
                        new_states.append({
                            "hand": Counter(hand_counter),  # 手不变
                            "bags": new_bags,
                            "prob": new_prob,
                            "path": state["path"] + [f"discard{operation.bag_id}:{balls_discarded}"]
                        })
                        
                elif operation.operation_type == "return":
                    # 放回操作（从手中放回到袋子）
                    if not hand_counter:
                        # 手中没球，直接传递状态
                        new_states.append(state.copy())
                        continue
                    
                    # 手中球的颜色列表
                    hand_colors = list(hand_counter.elements())
                    
                    for color_to_return in set(hand_colors):
                        # 计算选择这个颜色球的概率
                        return_prob = hand_counter[color_to_return] / len(hand_colors)
                        
                        new_hand = Counter(hand_counter)
                        new_hand[color_to_return] -= 1
                        if new_hand[color_to_return] == 0:
                            del new_hand[color_to_return]
                        
                        new_bags = {bag_id: bag.copy() for bag_id, bag in bags.items()}
                        new_bags[operation.bag_id].add_ball(color_to_return)
                        
                        new_prob = current_prob * return_prob
                        
                        new_states.append({
                            "hand": new_hand,
                            "bags": new_bags,
                            "prob": new_prob,
                            "path": state["path"] + [f"return{operation.bag_id}:{color_to_return}"]
                        })
            
            # 合并相同手状态（优化状态空间）
            merged_states = self._merge_states(new_states)
            states = merged_states
            
            total_states_processed += len(states)
            print(f"    生成状态: {len(states)}个, 累计状态: {total_states_processed}")
            
            # 防止状态爆炸，进行剪枝
            if len(states) > 100000:
                print(f"⚠️  状态过多 ({len(states)})，进行剪枝...")
                states = self._prune_states(states, max_states=50000)
        
        print(f"计算完成，最终状态数: {len(states)}")
        
        # 汇总结果
        return self._aggregate_results(states)
    
    def _merge_states(self, states: List[Dict]) -> List[Dict]:
        """合并相同手状态的状态"""
        merged_dict = {}
        
        for state in states:
            # 以手状态和袋子状态的字符串表示为键
            hand_key = tuple(sorted(state["hand"].items()))
            
            # 袋子状态键（简化，只考虑球总数）
            bag_summaries = []
            for bag_id, bag in sorted(state["bags"].items()):
                bag_summaries.append((bag_id, sum(bag.color_counts.values())))
            bag_key = tuple(bag_summaries)
            
            full_key = (hand_key, bag_key)
            
            if full_key in merged_dict:
                # 合并概率
                merged_dict[full_key]["prob"] += state["prob"]
            else:
                merged_dict[full_key] = state.copy()
        
        return list(merged_dict.values())
    
    def _prune_states(self, states: List[Dict], max_states: int = 50000) -> List[Dict]:
        """剪枝：保留概率最高的状态"""
        if len(states) <= max_states:
            return states
            
        # 按概率排序，保留概率最高的状态
        sorted_states = sorted(states, key=lambda x: x["prob"], reverse=True)
        pruned_states = sorted_states[:max_states]
        
        # 重新归一化概率
        total_prob = sum(s["prob"] for s in pruned_states)
        if total_prob > 0:
            for state in pruned_states:
                state["prob"] /= total_prob
        
        print(f"  剪枝后保留 {len(pruned_states)} 个状态 (原 {len(states)} 个)")
        return pruned_states
    
    def _aggregate_results(self, states: List[Dict]) -> Dict[str, Any]:
        """汇总计算结果"""
        hand_distribution = defaultdict(float)
        
        for state in states:
            # 将手状态转换为字符串表示
            hand_desc_parts = []
            for color, count in sorted(state["hand"].items()):
                if count > 0:
                    hand_desc_parts.append(f"{count}{color}")
            
            hand_desc = "+".join(hand_desc_parts) if hand_desc_parts else "空手"
            hand_distribution[hand_desc] += state["prob"]
        
        # 计算总概率
        total_prob = sum(hand_distribution.values())
        
        return {
            "total_states": len(states),
            "total_probability": total_prob,
            "hand_distribution": dict(hand_distribution),
            "calculation_method": "exact"
        }
    
    def monte_carlo_simulation(self, bags_config: Dict[int, Dict[str, int]], 
                              operations: List[BallDrawOperation], 
                              num_simulations: int = 100000) -> Dict[str, Any]:
        """
        蒙特卡洛模拟
        
        参数:
            bags_config: 袋子配置
            operations: 操作序列
            num_simulations: 模拟次数
            
        返回:
            结果字典
        """
        print(f"开始蒙特卡洛模拟，次数: {num_simulations:,}")
        
        results = defaultdict(int)
        
        # 进度显示
        progress_step = max(1, num_simulations // 20)
        
        for sim in range(num_simulations):
            # 进度显示
            if sim % progress_step == 0:
                progress = (sim / num_simulations) * 100
                print(f"  进度: {progress:.1f}%", end='\r')
            
            # 初始化模拟
            bags = {bag_id: BagState(color_counts) for bag_id, color_counts in bags_config.items()}
            hand_counter = Counter()
            
            # 执行所有操作
            for operation in operations:
                if operation.operation_type == "draw":
                    # 摸球
                    bag = bags[operation.bag_id]
                    
                    # 从袋子中所有球中随机摸
                    all_balls = []
                    for color, count in bag.color_counts.items():
                        all_balls.extend([color] * count)
                    
                    if len(all_balls) < operation.draw_count:
                        # 球不够，跳过
                        continue
                    
                    # 随机摸球
                    drawn_balls = random.sample(all_balls, operation.draw_count)
                    
                    # 从袋子中移除
                    for ball in drawn_balls:
                        bag.color_counts[ball] -= 1
                        bag.total_balls -= 1
                        if bag.color_counts[ball] == 0:
                            del bag.color_counts[ball]
                    
                    # 加入手中
                    for ball in drawn_balls:
                        hand_counter[ball] += 1
                        
                elif operation.operation_type == "discard":
                    # 丢球
                    bag = bags[operation.bag_id]
                    
                    all_balls = []
                    for color, count in bag.color_counts.items():
                        all_balls.extend([color] * count)
                    
                    if len(all_balls) < operation.draw_count:
                        # 球不够，跳过
                        continue
                    
                    # 随机丢球
                    discarded_balls = random.sample(all_balls, operation.draw_count)
                    
                    # 从袋子中移除
                    for ball in discarded_balls:
                        bag.color_counts[ball] -= 1
                        bag.total_balls -= 1
                        if bag.color_counts[ball] == 0:
                            del bag.color_counts[ball]
                            
                elif operation.operation_type == "return":
                    # 放回球
                    if not hand_counter:
                        continue
                    
                    # 从手中随机选择一个球
                    hand_balls = []
                    for color, count in hand_counter.items():
                        hand_balls.extend([color] * count)
                    
                    if not hand_balls:
                        continue
                    
                    ball_to_return = random.choice(hand_balls)
                    
                    # 从手中移除
                    hand_counter[ball_to_return] -= 1
                    if hand_counter[ball_to_return] == 0:
                        del hand_counter[ball_to_return]
                    
                    # 放回袋子
                    bags[operation.bag_id].add_ball(ball_to_return)
            
            # 记录结果
            hand_desc_parts = []
            for color, count in sorted(hand_counter.items()):
                if count > 0:
                    hand_desc_parts.append(f"{count}{color}")
            
            hand_desc = "+".join(hand_desc_parts) if hand_desc_parts else "空手"
            results[hand_desc] += 1
        
        print(f"模拟完成，生成 {len(results)} 种不同结果")
        
        # 转换为概率
        total_simulations = sum(results.values())
        hand_distribution = {}
        
        for hand_desc, count in results.items():
            hand_distribution[hand_desc] = count / total_simulations
        
        return {
            "total_states": len(hand_distribution),
            "total_probability": sum(hand_distribution.values()),
            "hand_distribution": hand_distribution,
            "simulations": num_simulations,
            "calculation_method": "monte_carlo"
        }
    
    def validate_configuration(self, bags_config: Dict[int, Dict[str, int]], 
                              operations: List[BallDrawOperation]) -> List[str]:
        """
        验证配置的有效性
        
        返回: 错误信息列表，空列表表示配置有效
        """
        errors = []
        
        # 检查袋子配置
        for bag_id, color_counts in bags_config.items():
            if not isinstance(bag_id, int) or bag_id <= 0:
                errors.append(f"袋子ID必须是正整数: {bag_id}")
            
            total_balls = sum(color_counts.values())
            if total_balls <= 0:
                errors.append(f"袋子{bag_id}必须至少有一个球")
            
            for color, count in color_counts.items():
                if count < 0:
                    errors.append(f"袋子{bag_id}中颜色{color}的数量不能为负数: {count}")
        
        # 检查操作序列
        for i, op in enumerate(operations):
            if op.bag_id not in bags_config:
                errors.append(f"操作{i+1}引用不存在的袋子: {op.bag_id}")
            
            if op.draw_count <= 0:
                errors.append(f"操作{i+1}的摸球数量必须为正数: {op.draw_count}")
            
            if op.operation_type not in ["draw", "discard", "return"]:
                errors.append(f"操作{i+1}的类型无效: {op.operation_type}")
        
        return errors