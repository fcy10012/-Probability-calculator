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
    """创建自定义配置"""
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
    
    # 获取问题描述
    description = input("请输入问题描述: ").strip()
    if not description:
        description = "自定义问题"
    
    # 获取袋子配置
    bags_config = {}
    print("\n开始配置袋子 (输入'q'完成配置):")
    while True:
        try:
            bag_input = input(f"袋子 {len(bags_config) + 1} (格式: 袋号:颜色:数量,颜色:数量 如 1:R:3,B:2): ").strip()
            
            if bag_input.lower() == 'q':
                if not bags_config:
                    print("至少需要一个袋子")
                    continue
                break
            
            # 解析输入：格式为 "袋号:颜色:数量,颜色:数量"
            parts = bag_input.split(':')
            if len(parts) < 2:
                print("格式错误，请按格式输入")
                continue
            
            # 第一部分是袋号
            bag_id = int(parts[0].strip())
            
            # 剩余部分是颜色配置
            colors_config = {}
            color_parts_str = ':'.join(parts[1:])  # 重新组合颜色部分
            
            # 解析颜色配置（用逗号分隔）
            for color_part in color_parts_str.split(','):
                color_part = color_part.strip()
                if not color_part:
                    continue
                    
                if ':' not in color_part:
                    print(f"颜色配置格式错误: {color_part} (应为 颜色:数量)")
                    continue
                    
                color_count_parts = color_part.split(':')
                if len(color_count_parts) != 2:
                    print(f"颜色配置格式错误: {color_part}")
                    continue
                    
                color = color_count_parts[0].strip()
                try:
                    count = int(color_count_parts[1].strip())
                    colors_config[color] = count
                except ValueError:
                    print(f"数量必须是整数: {color_count_parts[1]}")
                    continue
            
            if not colors_config:
                print("至少需要一个颜色")
                continue
            
            bags_config[bag_id] = colors_config
            print(f"✅ 袋子{bag_id}配置完成: {colors_config}")
            
        except ValueError as e:
            print(f"输入错误: {e}")
    
    # 获取操作序列
    operations = []
    print("\n开始配置操作序列 (输入'q'完成配置):")
    
    while True:
        try:
            if operations:
                print(f"已配置 {len(operations)} 个操作")
            
            op_input = input(f"操作 {len(operations) + 1} (格式: 袋号,数量,类型 如 1,2,draw): ").strip()
            
            if op_input.lower() == 'q':
                if not operations:
                    print("至少需要一个操作")
                    continue
                break
            
            parts = op_input.split(',')
            if len(parts) != 3:
                print("格式错误，需要3个参数: 袋号,数量,类型")
                continue
            
            bag_id = int(parts[0].strip())
            draw_count = int(parts[1].strip())
            operation_type = parts[2].strip().lower()
            
            if operation_type not in ['draw', 'discard', 'return']:
                print("操作类型必须是: draw, discard 或 return")
                continue
            
            if bag_id not in bags_config:
                print(f"错误: 袋子{bag_id}未定义")
                continue
            
            operations.append({
                "bag_id": bag_id,
                "draw_count": draw_count,
                "operation_type": operation_type
            })
            
            action = {"draw": "摸", "discard": "丢", "return": "还"}[operation_type]
            print(f"✅ 操作配置完成: {action}袋{bag_id} {draw_count}个球")
            
        except ValueError as e:
            print(f"输入错误: {e}")
    
    print(f"\n✅ 自定义配置创建完成!")
    print(f"描述: {description}")
    print(f"袋子数: {len(bags_config)}")
    print(f"操作数: {len(operations)}")
    
    return {
        "description": description,
        "bags_config": bags_config,
        "operations": operations
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