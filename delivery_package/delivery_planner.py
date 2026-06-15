# -*- coding: utf-8 -*-
"""
Industrial AI Delivery Package v1.0

Bundles three open-source modules into a sellable delivery solution:
1. Compliance Checker (IEC 61508 / ISO 13849)
2. MIMO Tuning (ZN / Cohen-Coon / RGA)
3. Causal Discovery (PC Algorithm)
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Optional
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)
sys.path.insert(0, PARENT_DIR)

from causal_discovery import CausalDiscoverer
from compliance import ComplianceChecker, ComplianceLevel
from mimo_tuning import (
    ziegler_nichols_open_loop,
    cohen_coon,
    calculate_rga,
    suggest_pairings,
    tune_mimo,
    PIDParams,
)


class IndustrialDeliveryPackage:
    """Bundles compliance + MIMO tuning + causal discovery for industrial delivery."""

    VERSION = "1.0.0"

    def __init__(self):
        self.compliance = ComplianceChecker()
        self.causal = CausalDiscoverer(alpha=0.05)
        self.delivery_log = []

    # ------------------------------------------------------------------
    # Module 1: Compliance Audit
    # ------------------------------------------------------------------
    def run_compliance_audit(self, actions: List[str]) -> Dict:
        """Check a list of industrial actions against safety rules."""
        results = []
        for action_text in actions:
            r = self.compliance.check(action_text)
            results.append({
                "action": r.action,
                "level": r.level.value,
                "violated": r.violated_rules,
                "suggestion": r.suggestion,
            })
        passed = sum(1 for r in results if r["level"] == "safe")
        warnings = sum(1 for r in results if r["level"] == "warning")
        violations = sum(1 for r in results if r["level"] == "violation")
        return {
            "module": "compliance_audit",
            "total_checks": len(results),
            "passed": passed,
            "warnings": warnings,
            "violations": violations,
            "details": results,
        }

    # ------------------------------------------------------------------
    # Module 2: MIMO Tuning
    # ------------------------------------------------------------------
    def run_mimo_tuning(
        self,
        K: float = 1.0,
        tau: float = 1.0,
        theta: float = 0.1,
        Ku: float = 2.0,
        Tu: float = 1.0,
        gain_matrix: Optional[List[List[float]]] = None,
        inputs: Optional[List[str]] = None,
        outputs: Optional[List[str]] = None,
    ) -> Dict:
        """Run ZN, Cohen-Coon, and RGA pairing analysis."""
        # ZN open-loop
        zn = ziegler_nichols_open_loop(K, tau, theta)
        # Cohen-Coon
        cc = cohen_coon(K, tau, theta)
        # RGA
        if gain_matrix is None:
            gain_matrix = [[1.0, 0.5], [0.3, 1.0]]
        gm = np.array(gain_matrix, dtype=float)
        rga = calculate_rga(gm)
        pairings = suggest_pairings(rga)

        result = {
            "module": "mimo_tuning",
            "ziegler_nichols": {"Kc": zn.Kc, "Ti": zn.Ti, "Td": zn.Td},
            "cohen_coon": {"Kc": cc.Kc, "Ti": cc.Ti, "Td": cc.Td},
            "rga_matrix": rga.tolist(),
            "pairings": pairings,
        }

        # Full MIMO tune if inputs/outputs provided
        if inputs and outputs:
            full = tune_mimo(inputs, outputs, gain_matrix, K, tau, theta)
            result["full_mimo"] = {
                "pairings": full.pairings,
                "loop_params": {
                    k: {"Kc": v.Kc, "Ti": v.Ti, "Td": v.Td}
                    for k, v in full.loop_params.items()
                },
            }
        return result

    # ------------------------------------------------------------------
    # Module 3: Causal Discovery
    # ------------------------------------------------------------------
    def run_causal_discovery(
        self, data: List[List[float]], var_names: List[str]
    ) -> Dict:
        """Run PC algorithm on observational data."""
        arr = np.array(data, dtype=float)
        result = self.causal.discover(arr, var_names)
        return {
            "module": "causal_discovery",
            "variables": result["var_names"],
            "n_edges": result["n_edges"],
            "adjacency_matrix": result["adjacency"].tolist(),
            "patterns": result.get("patterns", []),
        }

    # ------------------------------------------------------------------
    # Full Delivery Plan
    # ------------------------------------------------------------------
    def generate_delivery_plan(self, project_info: Dict) -> Dict:
        """Generate a complete delivery plan from project info."""
        plan = {
            "project_name": project_info.get("project_name", "未命名"),
            "delivery_version": self.VERSION,
            "timestamp": datetime.now().isoformat(),
            "modules": {},
        }

        # 1. Compliance
        actions = project_info.get("actions", ["read sensor temperature"])
        plan["modules"]["compliance_audit"] = self.run_compliance_audit(actions)

        # 2. MIMO Tuning
        pp = project_info.get("plant_params", {})
        plan["modules"]["mimo_tuning"] = self.run_mimo_tuning(
            K=pp.get("K", 1.0),
            tau=pp.get("tau", 1.0),
            theta=pp.get("theta", 0.1),
            Ku=pp.get("Ku", 2.0),
            Tu=pp.get("Tu", 1.0),
            gain_matrix=pp.get("gain_matrix"),
            inputs=project_info.get("inputs"),
            outputs=project_info.get("outputs"),
        )

        # 3. Causal Discovery
        data = project_info.get("data_sample")
        var_names = project_info.get("variables")
        if data and var_names:
            plan["modules"]["causal_discovery"] = self.run_causal_discovery(
                data, var_names
            )

        # Summary
        ca = plan["modules"]["compliance_audit"]
        plan["summary"] = {
            "compliance_rate": round(
                ca["passed"] / max(ca["total_checks"], 1) * 100, 1
            ),
            "mimo_methods": ["ZN", "Cohen-Coon", "RGA"],
            "causal_variables": len(var_names) if var_names else 0,
            "overall_status": "PASS" if ca["violations"] == 0 else "REVIEW",
        }

        self.delivery_log.append(
            {
                "project": project_info.get("project_name"),
                "timestamp": plan["timestamp"],
                "status": plan["summary"]["overall_status"],
            }
        )
        return plan

    def generate_report(self, plan: Dict) -> str:
        """Generate a human-readable delivery report."""
        lines = [
            "=" * 60,
            "Industrial AI Delivery Report",
            "=" * 60,
            "",
            f"Project: {plan['project_name']}",
            f"Version: {plan['delivery_version']}",
            f"Time:    {plan['timestamp']}",
            "",
            "--- Module 1: Compliance Audit ---",
        ]
        ca = plan["modules"]["compliance_audit"]
        lines.append(f"  Checks:   {ca['total_checks']}")
        lines.append(f"  Passed:   {ca['passed']}")
        lines.append(f"  Warnings: {ca['warnings']}")
        lines.append(f"  Violated: {ca['violations']}")
        for d in ca["details"]:
            tag = "PASS" if d["level"] == "safe" else d["level"].upper()
            lines.append(f"    [{tag}] {d['action']}")

        lines.append("")
        lines.append("--- Module 2: MIMO Tuning ---")
        mt = plan["modules"]["mimo_tuning"]
        zn = mt["ziegler_nichols"]
        lines.append(f"  ZN:          Kc={zn['Kc']:.3f} Ti={zn['Ti']:.3f} Td={zn['Td']:.3f}")
        cc = mt["cohen_coon"]
        lines.append(f"  Cohen-Coon:  Kc={cc['Kc']:.3f} Ti={cc['Ti']:.3f} Td={cc['Td']:.3f}")
        lines.append(f"  RGA pairing: {mt['pairings']}")

        lines.append("")
        lines.append("--- Module 3: Causal Discovery ---")
        if "causal_discovery" in plan["modules"]:
            cd = plan["modules"]["causal_discovery"]
            lines.append(f"  Variables: {cd['variables']}")
            lines.append(f"  Edges:     {cd['n_edges']}")
            for p in cd.get("patterns", []):
                lines.append(f"    {p['type']}: {p['structure']}")
        else:
            lines.append("  (skipped, no data)")

        lines.append("")
        lines.append("--- Summary ---")
        s = plan["summary"]
        lines.append(f"  Compliance: {s['compliance_rate']}%")
        lines.append(f"  Causal vars:{s['causal_variables']}")
        lines.append(f"  Status:     {s['overall_status']}")
        lines.append("=" * 60)
        return "\n".join(lines)
