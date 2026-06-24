"""agent_core.server - 快速启动入口"""
import sys
from pathlib import Path

# 确保项目根目录在 sys.path 中
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "agent_core.server.server:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info",
    )
