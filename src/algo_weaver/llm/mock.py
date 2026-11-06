"""Deterministic model adapter for local development and tests."""

import json
import re


class MockChatModel:
    """Return a deterministic capability draft without external API calls."""

    def complete_json(self, *, system_prompt: str, user_prompt: str) -> str:
        del system_prompt
        source_match = re.search(r"SOURCE_TEXT_JSON:\s*(.+)$", user_prompt, re.S)
        source_text = json.loads(source_match.group(1)) if source_match else user_prompt

        name = "未命名算法"
        for line in source_text.splitlines():
            candidate = line.strip().lstrip("# ").strip()
            if candidate:
                name = candidate[:80]
                break
        if "移动平均" in source_text or "moving average" in source_text.lower():
            name = "移动平均算法"

        payload = {
            "name": name,
            "problem_definition": "从输入资料中识别算法要解决的问题；Mock 模式不进行真实语义推断。",
            "algorithm_family": "time_series" if "时间序列" in source_text else "unknown",
            "inputs": ["待从原始资料中确认"],
            "outputs": ["待从原始资料中确认"],
            "preprocessing": [],
            "algorithm_steps": ["Mock 模式占位步骤：请切换真实模型完成抽取。"],
            "parameters": [],
            "constraints": [],
            "metrics": [],
            "failure_cases": [],
            "implementation_notes": ["该结果由 MockChatModel 生成，仅用于验证工程链路。"],
            "missing_information": ["当前为 Mock 模式，算法细节尚未经过真实模型抽取和人工核验。"],
        }
        return json.dumps(payload, ensure_ascii=False)
