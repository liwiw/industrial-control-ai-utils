"""
Industrial Control AI Utils - Compliance Checker

Industrial safety standards encoded as code rules:
- IEC 61508: Functional safety
- ISO 13849: Safety of machinery
- General safety red lines for industrial automation

This module provides automated compliance checking for industrial AI-assisted operations.
"""

from enum import Enum
from typing import List
from dataclasses import dataclass


class ComplianceLevel(Enum):
    """Compliance check result levels."""
    SAFE = "safe"
    WARNING = "warning"
    VIOLATION = "violation"


@dataclass
class ComplianceResult:
    """Result of a compliance check."""
    action: str
    level: ComplianceLevel
    violated_rules: List[str]
    suggestion: str


# Safety rules database (based on public industrial standards)
SAFETY_RULES = [
    {
        "id": "SR001",
        "name": "急停优先原则",
        "standard": "IEC 61508",
        "keywords": ["急停", "紧急停止", "emergency stop", "e-stop"],
        "violation_keywords": ["短接", "跳过", "绕过", "禁用", "bypass", "disable"],
        "description": "急停信号必须优先于所有其他控制逻辑，不得短接或绕过"
    },
    {
        "id": "SR002",
        "name": "安全回路完整性",
        "standard": "ISO 13849",
        "keywords": ["安全回路", "safety circuit", "安全链", "safety chain"],
        "violation_keywords": ["短接", "跳过", "旁路", "bypass", "disable"],
        "description": "安全回路必须保持完整，不得短接或旁路"
    },
    {
        "id": "SR003",
        "name": "防护装置不可禁用",
        "standard": "ISO 13849",
        "keywords": ["防护罩", "安全门", "光栅", "guard", "safety door", "light curtain"],
        "violation_keywords": ["禁用", "拆除", "disable", "remove"],
        "description": "安全防护装置在任何情况下不得被禁用或拆除"
    },
    {
        "id": "SR004",
        "name": "安全文档完整性",
        "standard": "IEC 61508",
        "keywords": ["安全验证", "安全报告", "SIL评估", "safety validation", "SIL"],
        "violation_keywords": ["删除", "不写", "跳过", "delete", "skip"],
        "description": "安全验证报告和相关文档必须保留，不得删除"
    },
    {
        "id": "SR005",
        "name": "联锁逻辑不可旁路",
        "standard": "通用安全红线",
        "keywords": ["联锁", "interlock", "安全联锁", "safety interlock"],
        "violation_keywords": ["旁路", "跳过", "强制", "bypass", "force", "override"],
        "description": "安全联锁逻辑不得被旁路或强制"
    },
    {
        "id": "SR006",
        "name": "报警不可永久屏蔽",
        "standard": "通用安全红线",
        "keywords": ["报警", "alarm", "告警", "警报"],
        "violation_keywords": ["永久屏蔽", "永久禁用", "disable permanently"],
        "description": "安全相关报警不得被永久屏蔽"
    },
    {
        "id": "SR007",
        "name": "故障安全默认状态",
        "standard": "IEC 61508",
        "keywords": ["故障安全", "fail-safe", "安全状态", "safe state"],
        "violation_keywords": ["取消", "移除", "disable", "remove"],
        "description": "系统故障时必须进入预定义的安全状态"
    },
    {
        "id": "SR008",
        "name": "权限分级控制",
        "standard": "通用安全红线",
        "keywords": ["权限", "操作员", "工程师", "维护", "operator", "engineer"],
        "violation_keywords": ["越权", "提权", "绕过权限", "escalate", "bypass auth"],
        "description": "不同安全级别的操作必须有相应权限控制"
    },
]


class ComplianceChecker:
    """
    Industrial compliance checker.
    
    Checks actions against encoded safety standards and flags violations.
    
    Usage:
        checker = ComplianceChecker()
        result = checker.check("短接安全回路进行调试")
        if result.level == ComplianceLevel.VIOLATION:
            print("操作被拒绝:", result.violated_rules)
    """
    
    def __init__(self):
        self.rules = SAFETY_RULES
    
    def check(self, action: str) -> ComplianceResult:
        """
        Check if an action violates any safety rules.
        
        Args:
            action: Description of the planned action
        
        Returns:
            ComplianceResult with level and violated rules
        """
        action_lower = action.lower()
        violated = []
        
        for rule in self.rules:
            matches_keyword = any(kw.lower() in action_lower for kw in rule["keywords"])
            
            if matches_keyword:
                matches_violation = any(vw.lower() in action_lower for vw in rule["violation_keywords"])
                if matches_violation:
                    violated.append(rule)
        
        if violated:
            rule_ids = [r["id"] + " " + r["name"] for r in violated]
            return ComplianceResult(
                action=action,
                level=ComplianceLevel.VIOLATION,
                violated_rules=rule_ids,
                suggestion="操作违反安全标准，必须重新设计。违反规则: " + "; ".join(rule_ids)
            )
        else:
            return ComplianceResult(
                action=action,
                level=ComplianceLevel.SAFE,
                violated_rules=[],
                suggestion="未发现安全违规"
            )
    
    def list_rules(self) -> List[dict]:
        """List all safety rules."""
        return [
            {"id": r["id"], "name": r["name"], "standard": r["standard"], "description": r["description"]}
            for r in self.rules
        ]


def demo():
    """Demo compliance checker."""
    print("=== Industrial Compliance Checker ===\n")
    
    checker = ComplianceChecker()
    
    test_actions = [
        ("短接安全回路进行调试", "VIOLATION"),
        ("编写PLC温度控制程序", "SAFE"),
        ("禁用防护罩以提高效率", "VIOLATION"),
        ("修改机器人速度上限", "SAFE"),
        ("部署SCADA监控系统", "SAFE"),
        ("删除安全验证报告", "VIOLATION"),
        ("配置Modbus通信参数", "SAFE"),
    ]
    
    passed = 0
    for action, expected in test_actions:
        result = checker.check(action)
        status = "PASS" if result.level.value == expected.lower() else "FAIL"
        if status == "PASS":
            passed += 1
        print(f"  [{status}] {action}")
        print(f"        -> {result.level.value}")
        if result.violated_rules:
            print(f"        违反: {', '.join(result.violated_rules)}")
    
    print(f"\n通过率: {passed}/{len(test_actions)} = {round(passed/len(test_actions)*100, 1)}%")


if __name__ == "__main__":
    demo()
