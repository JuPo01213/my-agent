"""
智能体模型配置文件。

说明：
- 本文件存放默认模型与 API 配置。
- 敏感信息（API Key）优先读取环境变量，避免提交到版本库。
- 如需覆盖，直接设置环境变量即可：STEPFUN_API_KEY / STEPFUN_BASE_URL / STEPFUN_MODEL
"""

from __future__ import annotations

import os
from typing import Optional


# ---------------------------------------------------------------------------
# StepFun 默认配置（用户提供的模型信息已写入默认值）
# ---------------------------------------------------------------------------

STEPFUN_BASE_URL: str = os.getenv("STEPFUN_BASE_URL", "https://api.stepfun.com/step_plan/v1")
STEPFUN_MODEL: str = os.getenv("STEPFUN_MODEL", "step-3.7-flash")
STEPFUN_API_KEY: Optional[str] = os.getenv("STEPFUN_API_KEY", "3tZqqWODY5avioff3DF5JrnRtzK5cwYh5AW9N2DAnXA5gP1AR38rzDADkQugvHJgO")

# ---------------------------------------------------------------------------
# OpenAI 兼容配置（可选 fallback）
# ---------------------------------------------------------------------------

OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "")
OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "")
OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")

# ---------------------------------------------------------------------------
# Ark / Doubao 配置（第二模型）
# ---------------------------------------------------------------------------

ARK_BASE_URL: str = os.getenv("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
ARK_MODEL: str = os.getenv("ARK_MODEL", "doubao-seed-evolving")
ARK_API_KEY: Optional[str] = os.getenv("ARK_API_KEY", "ark-105fe362-e7e2-454c-a88b-cc049f1e72fb-ffe98")

# ---------------------------------------------------------------------------
# 运行时解析
# ---------------------------------------------------------------------------


def get_provider() -> tuple[str, str, str]:
    """
    返回当前生效的 (api_key, base_url, model)。
    优先级：StepFun > OpenAI。
    """
    if STEPFUN_API_KEY:
        return STEPFUN_API_KEY, STEPFUN_BASE_URL, STEPFUN_MODEL
    if OPENAI_API_KEY:
        return OPENAI_API_KEY, OPENAI_BASE_URL or "https://api.openai.com/v1", OPENAI_MODEL
    raise RuntimeError(
        "未检测到 API Key。请设置环境变量 STEPFUN_API_KEY 或 OPENAI_API_KEY。"
    )


def get_provider_config(name: str) -> tuple[str, str, str]:
    """
    按 provider 名称返回 (api_key, base_url, model)。
    支持：stepfun / ark / openai。
    """
    normalized = (name or "").strip().lower()
    if normalized in {"", "stepfun", "step"}:
        if not STEPFUN_API_KEY:
            raise RuntimeError("未配置 STEPFUN_API_KEY")
        return STEPFUN_API_KEY, STEPFUN_BASE_URL, STEPFUN_MODEL
    if normalized in {"ark", "doubao"}:
        if not ARK_API_KEY:
            raise RuntimeError("未配置 ARK_API_KEY")
        return ARK_API_KEY, ARK_BASE_URL, ARK_MODEL
    if normalized == "openai":
        if not OPENAI_API_KEY:
            raise RuntimeError("未配置 OPENAI_API_KEY")
        return OPENAI_API_KEY, OPENAI_BASE_URL or "https://api.openai.com/v1", OPENAI_MODEL
    raise RuntimeError(f"不支持的 provider：{name}")
