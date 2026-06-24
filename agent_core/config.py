"""
智能体模型配置文件。

说明
====

本文件存放默认模型与 API 配置。

**安全声明**（依据 ADR-003）：
  本项目**不需要任何安全护栏和权限限制**（用户明确要求）。
  出于本地开发便利，文件中硬编码了 API Key 作为默认值。
  这意味着：
    - 任何 clone 本仓库的人都能直接使用默认 Key 跑通
    - 这些 Key 仅用于本地测试，**不要用于生产环境**
    - 敏感信息（API Key）优先通过环境变量覆盖（见下方"环境变量覆盖"）

**环境变量覆盖**（推荐生产用法）：

  - StepFun：STEPFUN_API_KEY / STEPFUN_BASE_URL / STEPFUN_MODEL
  - OpenAI：OPENAI_API_KEY / OPENAI_BASE_URL / OPENAI_MODEL
  - Ark / 豆包：ARK_API_KEY / ARK_BASE_URL / ARK_MODEL

环境变量优先级 > 文件默认值。设置环境变量后，文件中的硬编码 Key 不会生效。
"""
from __future__ import annotations

import os
from typing import Optional


# ---------------------------------------------------------------------------
# StepFun 默认配置（用户提供的模型信息已写入默认值）
# ---------------------------------------------------------------------------
# ⚠️ 本节 Key 仅为本地开发默认值，**禁止用于生产**。
# 部署时请通过环境变量 STEPFUN_API_KEY 覆盖。

STEPFUN_BASE_URL: str = os.getenv("STEPFUN_BASE_URL", "https://api.stepfun.com/step_plan/v1")
STEPFUN_MODEL: str = os.getenv("STEPFUN_MODEL", "step-3.7-flash")
# ↓ 本地开发默认值，生产环境必须用环境变量覆盖
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
# ⚠️ 本节 Key 仅为本地开发默认值，**禁止用于生产**。
# 部署时请通过环境变量 ARK_API_KEY 覆盖。

ARK_BASE_URL: str = os.getenv("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
ARK_MODEL: str = os.getenv("ARK_MODEL", "doubao-seed-evolving")
# ↓ 本地开发默认值，生产环境必须用环境变量覆盖
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
