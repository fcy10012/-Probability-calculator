#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件管理工具模块
处理结果保存、文件组织等功能
"""

import os
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime

class FileManager:
    """文件管理器"""
    
    def __init__(self, base_dir: str = None):
        """
        初始化文件管理器
        
        Args:
            base_dir: 基础目录，默认为当前目录
        """
        self.base_dir = base_dir or os.getcwd()
        self.results_dir = os.path.join(self.base_dir, "results")
        
        # 确保results目录存在
        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)
    
    def save_results(self, 
                    results: Dict[str, Any], 
                    prefix: str = "results") -> str:
        """
        保存结果到文件
        
        Args:
            results: 结果数据
            prefix: 文件前缀
            
        Returns:
            保存的文件路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.json"
        filepath = os.path.join(self.results_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            return filepath
            
        except Exception as e:
            raise Exception(f"保存结果失败: {e}")
    
    def save_config(self, 
                   config: Dict[str, Any], 
                   filename: str = "config.json") -> str:
        """
        保存配置文件
        
        Args:
            config: 配置数据
            filename: 文件名
            
        Returns:
            保存的文件路径
        """
        filepath = os.path.join(self.base_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            return filepath
            
        except Exception as e:
            raise Exception(f"保存配置失败: {e}")
    
    def load_config(self, filename: str = "config.json") -> Dict[str, Any]:
        """
        加载配置文件
        
        Args:
            filename: 文件名
            
        Returns:
            配置数据
        """
        filepath = os.path.join(self.base_dir, filename)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"配置文件不存在: {filepath}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            raise Exception(f"加载配置失败: {e}")
    
    def list_results(self) -> list:
        """
        列出所有结果文件
        
        Returns:
            结果文件列表
        """
        if not os.path.exists(self.results_dir):
            return []
        
        results = []
        for filename in os.listdir(self.results_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.results_dir, filename)
                stat = os.stat(filepath)
                results.append({
                    'filename': filename,
                    'filepath': filepath,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime)
                })
        
        # 按修改时间排序（最新的在前）
        results.sort(key=lambda x: x['modified'], reverse=True)
        return results
    
    def clean_old_results(self, keep_last: int = 10) -> int:
        """
        清理旧的结果文件
        
        Args:
            keep_last: 保留最新的几个文件
            
        Returns:
            删除的文件数量
        """
        results = self.list_results()
        
        if len(results) <= keep_last:
            return 0
        
        deleted = 0
        for result in results[keep_last:]:
            try:
                os.remove(result['filepath'])
                deleted += 1
            except Exception:
                pass
        
        return deleted
    
    def export_results_text(self, 
                           results: Dict[str, Any], 
                           filename: str = None) -> str:
        """
        导出结果为文本格式
        
        Args:
            results: 结果数据
            filename: 输出文件名（可选）
            
        Returns:
            保存的文件路径
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"results_summary_{timestamp}.txt"
        
        filepath = os.path.join(self.results_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                # 写入标题
                f.write("多袋摸球概率计算结果汇总\n")
                f.write("=" * 50 + "\n\n")
                
                # 写入基本信息
                if 'problem_description' in results:
                    f.write(f"问题描述: {results['problem_description']}\n")
                
                if 'timestamp' in results:
                    f.write(f"计算时间: {results['timestamp']}\n")
                
                # 写入统计信息
                if 'results' in results:
                    res = results['results']
                    f.write(f"\n总状态数: {res.get('total_states', 0):,}\n")
                    f.write(f"总概率: {res.get('total_probability', 0):.10f}\n\n")
                    
                    # 写入分布
                    f.write("手上球的最终分布:\n")
                    f.write("-" * 50 + "\n")
                    
                    distribution = res.get('hand_distribution', {})
                    sorted_items = sorted(distribution.items(), 
                                         key=lambda x: x[1], 
                                         reverse=True)
                    
                    for hand_desc, prob in sorted_items:
                        percentage = prob * 100
                        f.write(f"{hand_desc:20s}: {prob:.10f} ({percentage:.6f}%)\n")
                
                f.write("\n" + "=" * 50 + "\n")
                f.write(f"计算完成于: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            return filepath
            
        except Exception as e:
            raise Exception(f"导出文本结果失败: {e}")