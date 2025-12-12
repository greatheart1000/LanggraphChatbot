"""
配置文件
支持从环境变量或直接配置 OpenAI 参数
"""
import os

# OpenAI 配置
# 优先级：环境变量 > 默认值
OPENAI_API_KEY = os.getenv(
    "OPENAI_API_KEY", 
    "sk-lcfvUUrmDih6qQWW5eC89504A869464d91E2AbFaBe087d43"
)

OPENAI_BASE_URL = os.getenv(
    "OPENAI_BASE_URL",
    "http://one-api.internal-tools.com/v1"
)

OPENAI_MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-4.1-mini"
)

# 其他配置
# 使用相对于配置文件的路径
from pathlib import Path
_config_dir = Path(__file__).parent
_root_dir = _config_dir.parent.parent  # 从 智能客服系统/tcg_customer_support 到根目录

SCENARIOS_FILE = os.getenv(
    "SCENARIOS_FILE",
    str(_root_dir / "TCG 客服场景flow_parsed.json")
)

SOP_BASE_DIR = os.getenv(
    "SOP_BASE_DIR",
    str(_config_dir.parent / "sop_data_global_en")
)

