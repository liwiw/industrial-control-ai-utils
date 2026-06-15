# 工业AI交付方案包 v1.0

## 方案概述

**定位**: 面向工业客户的标准化AI交付方案，零代码基础也可交付。

**核心卖点**: 合规审查 + 控制器调参 + 因果分析，三件套一站式交付。

## 三模块

### 模块一: 工业AI合规审查
- 基于 IEC 61508 / ISO 13849 标准
- 8条硬编码安全规则
- 自动检测违规操作并给出建议

### 模块二: MIMO控制器调参
- Ziegler-Nichols 整定（开环法）
- Cohen-Coon 整定
- Lambda 整定
- RGA 配对分析
- 静态解耦器设计

### 模块三: 因果发现
- PC 算法（学术标准实现）
- Fisher Z 检验条件独立性
- v-结构自动识别
- 因果模式分类（chain/fork/collider）

## 交付物
- 交付方案文档（本文件）
- Demo 脚本（examples/delivery_demo.py）
- 合规审查报告模板
- MIMO调参结果模板

## 适用场景
- 压缩机站控制优化
- 注塑成型过程优化
- 流程化工PID整定
- 工业巡检合规审查

## 安装
```bash
pip install numpy
git clone https://github.com/liwiw/industrial-control-ai-utils
cd industrial-control-ai-utils
python examples/delivery_demo.py
```

## 版本
v1.0.0 · 2026-06-15
