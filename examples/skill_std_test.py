# -*- coding: utf-8 -*-
"""
Agent技能标准化框架 · 验证测试

测试：
1. 技能注册与搜索
2. 五维评分
3. 质量门禁
4. 6个标准技能预加载
"""

import sys
import os

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, ".."))

from skill_std import SkillRegistry, SkillEvaluator
from skill_std.skill_registry import SkillRecord, STANDARD_SKILLS


def test_registry():
    """测试技能注册表"""
    reg = SkillRegistry()
    passed = 0

    # 预加载标准技能
    for s in STANDARD_SKILLS:
        reg.register(s)
        passed += 1

    # 搜索测试
    coding_skills = reg.search("代码开发")
    assert len(coding_skills) > 0, "应找到代码开发技能"
    print("  [OK] 技能注册: %d个" % len(STANDARD_SKILLS))

    # 分类测试
    analysis_skills = reg.list_by_category("analysis")
    assert len(analysis_skills) > 0, "应有分析类技能"
    print("  [OK] 分类搜索: analysis=%d" % len(analysis_skills))

    # 统计测试
    stats = reg.stats()
    assert stats["total"] == 6, "应有6个标准技能"
    print("  [OK] 统计: total=%d, active=%d" % (stats["total"], stats["active"]))

    return reg


def test_evaluation():
    """测试技能评估"""
    evaluator = SkillEvaluator()
    coding_skill = STANDARD_SKILLS[0]  # 代码开发

    # 场景1：正常执行
    result = evaluator.evaluate(
        skill=coding_skill,
        task_keywords=["代码", "编程", "debug"],
        execution_time=30.0,
        output_length=200,
        has_errors=False,
        is_reusable=True,
        stability_runs=5,
    )
    assert result.passed, "正常场景应通过"
    print("  [OK] 评估通过: %.1f分 (门禁%d分)" % (result.total_score, coding_skill.quality_gate))

    # 场景2：有错误
    result2 = evaluator.evaluate(
        skill=coding_skill,
        task_keywords=["代码"],
        execution_time=30.0,
        output_length=200,
        has_errors=True,
        is_reusable=True,
        stability_runs=5,
    )
    assert not result2.passed, "有错误应不通过"
    print("  [OK] 有错误拦截: %.1f分 (未通过)" % result2.total_score)

    # 场景3：超时
    result3 = evaluator.evaluate(
        skill=coding_skill,
        task_keywords=["代码"],
        execution_time=200.0,  # 超时
        output_length=200,
        has_errors=False,
        is_reusable=True,
        stability_runs=5,
    )
    print("  [OK] 超时评估: %.1f分" % result3.total_score)


def test_batch():
    """批量评估"""
    evaluator = SkillEvaluator()
    results = evaluator.batch_evaluate(STANDARD_SKILLS, ["代码", "开发"])
    passed = sum(1 for r in results if r.passed)
    print("  [OK] 批量评估: %d/%d通过" % (passed, len(results)))


if __name__ == "__main__":
    print("=" * 60)
    print("NEW-SKILL-STD Agent技能标准化框架")
    print("=" * 60)

    print("\n1. 技能注册表测试:")
    reg = test_registry()

    print("\n2. 技能评估测试:")
    test_evaluation()

    print("\n3. 批量评估测试:")
    test_batch()

    print("\n" + "=" * 60)
    print("全部测试通过")
    print("=" * 60)
