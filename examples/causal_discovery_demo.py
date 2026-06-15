"""
Demo: Causal Discovery on Industrial Process Data

Shows how to use the PC algorithm to discover causal relationships
from industrial process variables (temperature, pressure, flow rate).
"""

import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from causal_discovery import CausalDiscoverer


def demo():
    print("=== 工业场景因果发现 Demo ===\n")
    
    np.random.seed(42)
    n_samples = 1000
    
    print("场景: 注塑成型过程")
    print("变量: 熔体温度 -> 注射压力 -> 产品缺陷率\n")
    
    # 生成合成数据: 温度 -> 压力 -> 缺陷率
    temperature = np.random.randn(n_samples) * 10 + 200  # 均值200度
    pressure = 0.8 * temperature + np.random.randn(n_samples) * 5  # 温度影响压力
    defect_rate = 0.5 * pressure + 0.3 * temperature + np.random.randn(n_samples) * 2
    
    data = np.column_stack([temperature, pressure, defect_rate])
    
    discoverer = CausalDiscoverer(alpha=0.05)
    result = discoverer.discover(data, var_names=["熔体温度", "注射压力", "缺陷率"])
    
    print("发现结果:")
    print(f"  变量数: {result['n_variables']}")
    print(f"  边数: {result['n_edges']}")
    print(f"  邻接矩阵: (0=无连接, 1=无向, 2=有向)")
    for i, name in enumerate(result['var_names']):
        row = result['adjacency'][i].astype(int)
        print(f"    {name}: {row}")
    
    print("\n因果模式:")
    for p in result['patterns']:
        print(f"  {p['type']}: {p['structure']}")


if __name__ == "__main__":
    demo()
