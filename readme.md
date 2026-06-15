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

### 4. 交付方案包 (delivery_package) [NEW]
- 三模块打包为可销售的工业AI交付方案
- 一键生成交付报告（合规+调参+因果）
- 支持压缩机站/注塑成型/流程化工等标准场景

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

# 许可
MIT

## 交付方案

交付方案包把三个模块打包为可销售的工业AI交付方案：

```python
from delivery_package import IndustrialDeliveryPackage

pkg = IndustrialDeliveryPackage()
plan = pkg.generate_delivery_plan({
    "project_name": "压缩机站MIMO控制优化",
    "actions": ["read sensor temperature"],
    "plant_params": {"K": 1.0, "tau": 1.0, "theta": 0.1},
    "variables": ["进气压力", "排气温度", "流量"],
    "data_sample": [[3.2,85,120],[3.4,87,125],[3.1,83,118]],
})
print(pkg.generate_report(plan))
```

完整文档: `DELIVERY.md`
演示脚本: `examples/delivery_demo.py`
