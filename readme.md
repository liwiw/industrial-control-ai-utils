# Industrial Control AI Utils

工业控制场景AI辅助工具集。将公开控制理论与现代AI方法结合，服务于PLC/SCADA/MES等工业自动化场景。

## 模块

### 1. 因果发现 (causal_discovery)
- PC算法：从观测数据中发现变量间因果图
- 因果模式分类：识别链式/叉式/对撞等因果结构
- 反事实推理：线性/非线性SEM

### 2. MIMO调参 (mimo_tuning)  
- SISO PID整定：Ziegler-Nichols / Cohen-Coon / Lambda
- MIMO RGA分析：相对增益阵列计算与配对建议
- 解耦器设计：静态/动态解耦

### 3. 工业合规 (compliance)
- IEC 61508 功能安全等级检查
- ISO 13849 控制系统安全评估
- 通用安全红线验证

## 安装

```bash
pip install numpy
```

## 示例

```python
# 因果发现
from causal_discovery import CausalDiscoverer
discoverer = CausalDiscoverer(alpha=0.05)
graph = discoverer.discover(data)

# MIMO调参
from mimo_tuning import MIMOTuner
tuner = MIMOTuner()
result = tuner.tune_mimo(inputs, outputs, gain_matrix)

# 合规检查
from compliance import ComplianceChecker
checker = ComplianceChecker()
result = checker.check("修改安全回路配置")
```

## 许可
MIT
