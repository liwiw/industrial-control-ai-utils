# -*- coding: utf-8 -*-
"""
Agent技能标准化框架 v1.0

参考：GitHub 60K星 agent-skills 框架 + 郡城36智能体经验
核心交付物：技能定义模板 + 评估标准 + Skill Registry

技能定义标准格式（借鉴agent-skills的SKILL.md模式）：
- 技能ID（唯一）
- 技能名称
- 技能描述（160字节内）
- 触发条件（关键词/场景）
- 执行流程（步骤列表）
- 质量门禁（评分>=60才通过）
- 依赖技能
"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class SkillRecord:
    """技能记录"""
    skill_id: str
    name: str
    description: str  # <= 160 bytes
    category: str     # coding/analysis/creative/vision/quick/reasoning
    trigger_keywords: List[str]
    execution_steps: List[str]
    quality_gate: int = 60  # 最低通过分数
    dependencies: List[str] = field(default_factory=list)
    timeout_seconds: int = 60
    version: str = "1.0.0"
    created_at: str = ""
    updated_at: str = ""
    status: str = "active"  # active/deprecated/experimental

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()
        # 描述截断到160字节
        if len(self.description.encode("utf-8")) > 160:
            self.description = self.description[:50] + "..."


class SkillRegistry:
    """技能注册表"""

    def __init__(self, storage_path: str = None):
        self.skills: Dict[str, SkillRecord] = {}
        self.storage_path = storage_path
        if storage_path and os.path.exists(storage_path):
            self.load(storage_path)

    def register(self, skill: SkillRecord) -> str:
        """注册技能"""
        if skill.skill_id in self.skills:
            # 更新
            self.skills[skill.skill_id] = skill
        else:
            self.skills[skill.skill_id] = skill
        if self.storage_path:
            self.save(self.storage_path)
        return skill.skill_id

    def get(self, skill_id: str) -> Optional[SkillRecord]:
        return self.skills.get(skill_id)

    def search(self, keyword: str) -> List[SkillRecord]:
        """按关键词搜索"""
        results = []
        for s in self.skills.values():
            if any(kw.lower() in keyword.lower() for kw in s.trigger_keywords):
                results.append(s)
        return results

    def list_by_category(self, category: str) -> List[SkillRecord]:
        return [s for s in self.skills.values() if s.category == category]

    def list_all(self) -> List[SkillRecord]:
        return list(self.skills.values())

    def save(self, path: str):
        data = {sid: asdict(s) for sid, s in self.skills.items()}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self, path: str):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for sid, d in data.items():
            self.skills[sid] = SkillRecord(**d)

    def stats(self) -> Dict:
        by_cat = {}
        for s in self.skills.values():
            by_cat[s.category] = by_cat.get(s.category, 0) + 1
        return {
            "total": len(self.skills),
            "by_category": by_cat,
            "active": sum(1 for s in self.skills.values() if s.status == "active"),
        }


# 预定义的标准技能模板
STANDARD_SKILLS = [
    SkillRecord(
        skill_id="SKILL-001",
        name="代码开发",
        description="代码编写、调试、架构设计、单元测试",
        category="coding",
        trigger_keywords=["代码", "编程", "debug", "test", "修复", "开发", "脚本"],
        execution_steps=[
            "1. 理解需求，明确输入输出",
            "2. 设计架构，划分模块",
            "3. 编写代码，遵循PEP8/ESLint",
            "4. 单元测试，覆盖率>80%",
            "5. 代码审查，至少一人通过",
        ],
        quality_gate=80,
        timeout_seconds=120,
    ),
    SkillRecord(
        skill_id="SKILL-002",
        name="数据分析",
        description="数据清洗、统计分析、可视化、报告生成",
        category="analysis",
        trigger_keywords=["分析", "数据", "report", "统计", "表格", "计算"],
        execution_steps=[
            "1. 理解数据源和字段含义",
            "2. 数据清洗，处理缺失值/异常值",
            "3. 探索性分析，发现模式",
            "4. 可视化呈现关键发现",
            "5. 输出结构化报告",
        ],
        quality_gate=75,
        timeout_seconds=90,
    ),
    SkillRecord(
        skill_id="SKILL-003",
        name="文案创作",
        description="营销文案、脚本写作、标题优化、SEO",
        category="creative",
        trigger_keywords=["文案", "创作", "writing", "营销", "脚本", "标题"],
        execution_steps=[
            "1. 明确目标受众和平台",
            "2. 确定核心卖点和hook",
            "3. 撰写初稿",
            "4. A/B测试标题/开头",
            "5. SEO关键词优化",
        ],
        quality_gate=70,
        timeout_seconds=60,
    ),
    SkillRecord(
        skill_id="SKILL-004",
        name="视觉设计",
        description="LOGO/海报/UI/排版/配色方案",
        category="vision",
        trigger_keywords=["图片", "视觉", "设计", "image", "logo", "排版"],
        execution_steps=[
            "1. 理解品牌调性和目标",
            "2. 调研竞品和趋势",
            "3. 生成3个方案",
            "4. 选择最佳方案细化",
            "5. 输出多尺寸适配版本",
        ],
        quality_gate=75,
        timeout_seconds=120,
    ),
    SkillRecord(
        skill_id="SKILL-005",
        name="快速查询",
        description="时间、日期、状态、简单事实查询",
        category="quick",
        trigger_keywords=["简单", "快速", "查询", "时间", "日期", "状态"],
        execution_steps=[
            "1. 直接回答，不展开",
            "2. 给出准确数据",
            "3. 不添加多余信息",
        ],
        quality_gate=60,
        timeout_seconds=10,
    ),
    SkillRecord(
        skill_id="SKILL-006",
        name="推理规划",
        description="复杂推理、策略规划、架构设计、方案评估",
        category="reasoning",
        trigger_keywords=["推理", "策略", "规划", "架构", "复杂", "方案"],
        execution_steps=[
            "1. 拆解问题，明确约束",
            "2. 列出可行方案",
            "3. 评估各方案优劣",
            "4. 选择最优并给出理由",
            "5. 制定执行计划",
        ],
        quality_gate=85,
        timeout_seconds=180,
    ),
]
