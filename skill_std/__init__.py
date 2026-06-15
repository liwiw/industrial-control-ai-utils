# -*- coding: utf-8 -*-
"""
Agent技能标准化框架 v1.0

参考：GitHub 60K星 agent-skills 框架
核心：
1. 技能定义模板（SKILL.md 标准格式）
2. 技能评估标准（五维评分）
3. Skill Registry（技能注册与检索）
"""

from .skill_registry import SkillRegistry, SkillRecord
from .skill_evaluator import SkillEvaluator
