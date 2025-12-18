"""
多袋摸球概率问题配置文件示例

此文件展示如何配置不同的问题场景
"""

EXAMPLE_PROBLEMS = {
    "original_problem": {
        "description": "原始问题 - 4个袋子，复杂操作",
        "bags_config": {
            1: {"Y": 3, "W": 5},  # 袋子1: 3黄球, 5白球
            2: {"B": 1, "P": 1},  # 袋子2: 1蓝球, 1紫球
            3: {"B": 2, "Y": 1},  # 袋子3: 2蓝球, 1黄球
            4: {"Y": 1, "B": 5},  # 袋子4: 1黄球, 5蓝球
        },
        "operations": [
            {"bag_id": 1, "draw_count": 2, "operation_type": "draw"},     # 从袋子1摸两个球
            {"bag_id": 1, "draw_count": 2, "operation_type": "discard"},  # 从袋子1丢掉两个球
            {"bag_id": 1, "draw_count": 1, "operation_type": "draw"},     # 再从袋子1摸一个球
            {"bag_id": 2, "draw_count": 1, "operation_type": "draw"},     # 从袋子2摸一个球
            {"bag_id": 3, "draw_count": 1, "operation_type": "draw"},     # 从袋子3摸一个球
            {"bag_id": 3, "draw_count": 1, "operation_type": "return"},   # 放回一个球到袋子3
            {"bag_id": 4, "draw_count": 2, "operation_type": "draw"},     # 从袋子4摸两个球
            {"bag_id": 1, "draw_count": 1, "operation_type": "return"},   # 放回一个球到袋子1
            {"bag_id": 1, "draw_count": 1, "operation_type": "draw"},     # 再从袋子1摸一个球
        ]
    },
    
    "simple_two_bag": {
        "description": "简单两袋问题",
        "bags_config": {
            1: {"R": 3, "B": 2},  # 袋子1: 3红球, 2蓝球
            2: {"G": 4, "Y": 1},  # 袋子2: 4绿球, 1黄球
        },
        "operations": [
            {"bag_id": 1, "draw_count": 2, "operation_type": "draw"},
            {"bag_id": 2, "draw_count": 1, "operation_type": "draw"},
            {"bag_id": 1, "draw_count": 1, "operation_type": "return"},
        ]
    },
    
    "three_bag_sequence": {
        "description": "三袋顺序摸球",
        "bags_config": {
            1: {"A": 2, "B": 3, "C": 1},
            2: {"X": 4, "Y": 2},
            3: {"P": 1, "Q": 1, "R": 1},
        },
        "operations": [
            {"bag_id": 1, "draw_count": 1, "operation_type": "draw"},
            {"bag_id": 2, "draw_count": 2, "operation_type": "draw"},
            {"bag_id": 3, "draw_count": 1, "operation_type": "draw"},
            {"bag_id": 1, "draw_count": 1, "operation_type": "return"},
        ]
    },
    
    "discard_only": {
        "description": "仅丢球操作",
        "bags_config": {
            1: {"R": 5, "B": 5},
            2: {"G": 3, "Y": 7},
        },
        "operations": [
            {"bag_id": 1, "draw_count": 3, "operation_type": "draw"},
            {"bag_id": 1, "draw_count": 2, "operation_type": "discard"},
            {"bag_id": 2, "draw_count": 2, "operation_type": "discard"},
        ]
    }
}

def load_problem_config(problem_name="original_problem"):
    """
    加载问题配置
    
    参数:
        problem_name: 问题名称，默认为原始问题
        
    返回:
        (bags_config, operations)
    """
    if problem_name not in EXAMPLE_PROBLEMS:
        available = list(EXAMPLE_PROBLEMS.keys())
        raise ValueError(f"未知问题名称 '{problem_name}'。可用问题: {available}")
    
    problem = EXAMPLE_PROBLEMS[problem_name]
    
    # 转换为操作对象
    from probability_calculator import BallDrawOperation
    
    operations_objs = []
    for op in problem["operations"]:
        operations_objs.append(
            BallDrawOperation(
                bag_id=op["bag_id"],
                draw_count=op["draw_count"],
                operation_type=op["operation_type"]
            )
        )
    
    return problem["bags_config"], operations_objs, problem["description"]

def create_custom_config():
    """创建自定义配置的指南"""
    print("=" * 60)
    print("创建自定义配置指南")
    print("=" * 60)
    print()
    print("1. 袋子配置格式:")
    print("   bags_config = {")
    print('     1: {"红": 3, "蓝": 5},  # 袋子1: 3红球, 5蓝球')
    print('     2: {"绿": 2, "黄": 4},  # 袋子2: 2绿球, 4黄球')
    print("   }")
    print()
    print("2. 操作序列格式:")
    print("   operations = [")
    print('      {"bag_id": 1, "draw_count": 2, "operation_type": "draw"},')
    print('      {"bag_id": 1, "draw_count": 1, "operation_type": "discard"},')
    print('      {"bag_id": 2, "draw_count": 1, "operation_type": "draw"},')
    print('      {"bag_id": 1, "draw_count": 1, "operation_type": "return"},')
    print("   ]")
    print()
    print("3. 操作类型说明:")
    print("   - 'draw': 从指定袋子摸球")
    print("   - 'discard': 从指定袋子丢球（随机丢）") 
    print("   - 'return': 从手中随机放回一个球到指定袋子")
    print()
    
    return {
        "bags_config_example": {
            1: {"R": 3, "B": 5},
            2: {"G": 2, "Y": 4},
        },
        "operations_example": [
            {"bag_id": 1, "draw_count": 2, "operation_type": "draw"},
            {"bag_id": 1, "draw_count": 1, "operation_type": "discard"},
            {"bag_id": 2, "draw_count": 1, "operation_type": "draw"},
            {"bag_id": 1, "draw_count": 1, "operation_type": "return"},
        ]
    }

if __name__ == "__main__":
    print("示例配置文件")
    print("=" * 60)
    
    for name, problem in EXAMPLE_PROBLEMS.items():
        print(f"\n📦 问题: {name}")
        print(f"📝 描述: {problem['description']}")
        
        bags = problem["bags_config"]
        print(f"📊 袋子配置: {len(bags)}个袋子")
        for bag_id, colors in bags.items():
            total = sum(colors.values())
            print(f"  袋子{bag_id}: {colors} (共{total}个球)")
        
        ops = problem["operations"]
        print(f"🔄 操作序列: {len(ops)}个操作")
        for i, op in enumerate(ops, 1):
            action = {"draw": "摸", "discard": "丢", "return": "还"}[op["operation_type"]]
            print(f"  {i}. {action}袋{op['bag_id']} {op['draw_count']}个球")
    
    print("\n" + "=" * 60)
    create_custom_config()