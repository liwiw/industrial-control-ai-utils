# -*- coding: utf-8 -*-
"""
工业AI交付方案包 · 客户演示Demo
模拟：压缩机站MIMO控制器交付项目
"""
import sys
import os

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, ".."))

from delivery_package import IndustrialDeliveryPackage


def demo_compressor_station():
    """压缩机站交付方案Demo"""
    pkg = IndustrialDeliveryPackage()
    
    project = {
        "project_name": "压缩机站MIMO控制优化",
        "industry": "流程化工",
        "control_loops": 2,
        "variables": ["进气压力", "排气温度", "流量"],
        "data_sample": [
            [3.2, 85, 120],
            [3.4, 87, 125],
            [3.1, 83, 118],
            [3.5, 89, 128],
            [3.3, 86, 122],
            [3.6, 90, 130],
            [3.0, 82, 115],
            [3.4, 88, 126],
            [3.2, 84, 120],
            [3.5, 91, 132],
        ],
        "plant_params": {
            "Ku": 2.0,
            "Tu": 1.0,
            "Kp": 1.0,
            "tau": 1.0,
            "theta": 0.1,
            "gain_matrix": [[1.0, 0.5], [0.3, 1.0]],
        },
        "compliance_standards": ["IEC 61508", "ISO 13849"],
    }
    
    plan = pkg.generate_delivery_plan(project)
    report = pkg.generate_report(plan)
    
    print(report)
    
    # 验证
    s = plan["summary"]
    assert s["overall_status"] in ("PASS", "REVIEW"), "交付状态异常"
    assert s["compliance_rate"] > 0, "合规率不应为0"
    assert "mimo_tuning" in plan["modules"], "缺少MIMO模块"
    assert "compliance_audit" in plan["modules"], "缺少合规模块"
    print("\n[OK] 交付方案生成成功")
    return plan


def demo_injection_molding():
    """注塑成型交付方案Demo"""
    pkg = IndustrialDeliveryPackage()
    
    project = {
        "project_name": "注塑成型过程优化",
        "industry": "离散制造",
        "control_loops": 2,
        "variables": ["熔体温度", "注射压力", "产品缺陷率"],
        "data_sample": [
            [220, 80, 2.1],
            [225, 85, 1.8],
            [215, 75, 2.5],
            [230, 90, 1.5],
            [218, 78, 2.3],
            [228, 88, 1.6],
            [222, 82, 2.0],
            [235, 92, 1.3],
            [212, 72, 2.8],
            [226, 86, 1.7],
        ],
        "plant_params": {
            "Ku": 1.5,
            "Tu": 0.8,
            "Kp": 0.8,
            "tau": 0.5,
            "theta": 0.05,
            "gain_matrix": [[0.8, 0.3], [0.2, 0.9]],
        },
        "compliance_standards": ["ISO 13849"],
    }
    
    plan = pkg.generate_delivery_plan(project)
    report = pkg.generate_report(plan)
    
    print(report)
    
    s = plan["summary"]
    assert s["overall_status"] in ("PASS", "REVIEW"), "交付状态异常"
    print("\n[OK] 注塑成型交付方案生成成功")
    return plan


if __name__ == "__main__":
    print("=" * 60)
    print("工业AI交付方案包 v1.0 - 客户演示")
    print("=" * 60)
    
    demo_compressor_station()
    
    print("\n" + "=" * 60)
    print("演示二: 注塑成型")
    print("=" * 60)
    
    demo_injection_molding()
    
    print("\n" + "=" * 60)
    print("交付方案包验证完成")
    print("=" * 60)
