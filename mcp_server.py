"""道冲模型 MCP 服务器——开发环境薄封装入口。

对外安装后请用 dao-chong-mcp 命令（见 README「一键安装」）；
仓库内开发可直接 `python mcp_server.py`（等价于 dao_chong.server:main）。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from dao_chong.server import (  # noqa: E402,F401
    dao_chong_get_concept,
    dao_chong_get_related,
    dao_chong_list_concepts,
    dao_chong_retrieve,
    main,
    mcp,
)

if __name__ == "__main__":
    main()
