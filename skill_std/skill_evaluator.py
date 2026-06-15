# -*- coding: utf-8 -*-
"""
技能评估标准 · 五维评分

借鉴：EpiBench (2606.13602) 短程可验证基准
五维：
1. 能力匹配度（30%）- 技能与任务画像的匹配程度
2. 输出质量（25%）- 产出物的完整性和正确性
3. 执行效率（20%）- 是否在超时内完成
4. 可复用性（15%）- 技能是否可被其他任务复用
5. 稳定性（10%）- 多次执行结果的一致性
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from .skill_registry import SkillRecord


@dataclass
class SkillEvalResult:
    """技能评估结果"""
    skill_id: str
    skill_name: str
    capability_match: float  # 0-100
    output_quality: float    # 0-100
    execution_efficiency: float  # 0-100
    reusability: float       # 0-100
    stability: float         # 0-100
    total_score: float       # 加权总分
    passed: bool             # 是否通过质量门禁
    details: str = ""


class SkillEvaluator:
    """技能评估器"""

    # 五维权重
    WEIGHTS = {
        "capability_match": 0.30,
        "output_quality": 0.25,
        "execution_efficiency": 0.20,
        "reusability": 0.15,
        "stability": 0.10,
    }

    def evaluate(
        self,
        skill: SkillRecord,
        task_keywords: List[str],
        execution_time: float,
        output_length: int = 0,
        has_errors: bool = False,
        is_reusable: bool = True,
        stability_runs: int = 1,
    ) -> SkillEvalResult:
        """
        评估技能表现

        Args:
            skill: 被评估的技能
            task_keywords: 任务关键词
            execution_time: 实际执行时间（秒）
            output_length: 输出长度（字符数）
            has_errors: 是否有错误
            is_reusable: 是否可复用
            stability_runs: 稳定执行次数
        """
        # 1. 能力匹配度
        match_count = sum(
            1 for kw in task_keywords
            if any(tk.lower() in kw.lower() for tk in skill.trigger_keywords)
        )
        capability_match = min(100, match_count / max(len(task_keywords), 1) * 100 + 30)

        # 2. 输出质量
        if has_errors:
            output_quality = 20
        elif output_length > 50:
            output_quality = 80
        else:
            output_quality = 40

        # 3. 执行效率
        if execution_time <= skill.timeout_seconds:
            efficiency_ratio = 1.0 - (execution_time / skill.timeout_seconds) * 0.5
            execution_efficiency = efficiency_ratio * 100
        else:
            execution_efficiency = max(0, 50 - (execution_time - skill.timeout_seconds) * 5)

        # 4. 可复用性
        reusability = 80 if is_reusable else 30
        if skill.dependencies:
            reusability = min(reusability, 60)  # 有依赖会降低可复用性

        # 5. 稳定性
        stability = min(100, stability_runs * 20)

        # 加权总分
        total = (
            capability_match * self.WEIGHTS["capability_match"]
            + output_quality * self.WEIGHTS["output_quality"]
            + execution_efficiency * self.WEIGHTS["execution_efficiency"]
            + reusability * self.WEIGHTS["reusability"]
            + stability * self.WEIGHTS["stability"]
        )

        passed = total >= skill.quality_gate

        return SkillEvalResult(
            skill_id=skill.skill_id,
            skill_name=skill.name,
            capability_match=round(capability_match, 1),
            output_quality=round(output_quality, 1),
            execution_efficiency=round(execution_efficiency, 1),
            reusability=round(reusability, 1),
            stability=round(stability, 1),
            total_score=round(total, 1),
            passed=passed,
            details=f"质量门禁: {skill.quality_gate}分, 实际: {round(total, 1)}分",
        )

    def batch_evaluate(
        self, skills: List[SkillRecord], task_keywords: List[str]
    ) -> List[SkillEvalResult]:
        """批量评估多个技能"""
        return [self.evaluate(s, task_keywords, s.timeout_seconds * 0.5) for s in skills]
