"""
TCG 客服场景处理 LangGraph
为 14 大类场景的每个子类分别创建处理流程
"""
from typing import Annotated, TypedDict, Literal, List, Dict, Any
from pathlib import Path
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import AnyMessage, add_messages
from langgraph.checkpoint.memory import MemorySaver
import json
import os

# 导入配置（如果存在）
try:
    from config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL, SCENARIOS_FILE, SOP_BASE_DIR
except ImportError:
    # 默认配置
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-lcfvUUrmDih6qQWW5eC89504A869464d91E2AbFaBe087d43")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "http://one-api.internal-tools.com/v1")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    # 使用相对于当前文件的路径，自动查找配置文件
    _current_dir = Path(__file__).parent
    _root_dir = _current_dir.parent.parent  # 从 智能客服系统/tcg_customer_support 到根目录
    _default_scenarios_file = _root_dir / "TCG 客服场景flow_parsed.json"
    SCENARIOS_FILE = os.getenv("SCENARIOS_FILE", str(_default_scenarios_file))
    SOP_BASE_DIR = os.getenv("SOP_BASE_DIR", str(_current_dir.parent / "sop_data_global_en"))

# 定义状态
class CustomerSupportState(TypedDict):
    """客服场景处理状态"""
    messages: Annotated[List[AnyMessage], add_messages]
    user_query: str
    category: str  # 大类场景
    subcategory: str  # 子类场景
    context: Dict[str, Any]  # 上下文信息
    response: str  # 响应内容
    next_action: str  # 下一步动作
    history: List[Dict]  # 处理历史

# 初始化 LLM - 使用自定义 base_url 和 api_key
llm = ChatOpenAI(
    model=OPENAI_MODEL,
    temperature=0,
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL
)

# --- 场景配置加载 ---
def load_scenarios(file_path: str = None) -> Dict:
    """加载场景配置"""
    if file_path is None:
        file_path = SCENARIOS_FILE
    
    # 如果路径是相对路径，尝试多个可能的位置
    if not Path(file_path).is_absolute():
        possible_paths = [
            file_path,  # 当前目录
            Path(__file__).parent / file_path,  # 脚本所在目录
            Path(__file__).parent.parent.parent / file_path,  # 项目根目录
        ]
        for path in possible_paths:
            if Path(path).exists():
                file_path = str(path)
                break
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"场景配置文件 {file_path} 未找到，请先运行 parse_document.py")
        print(f"尝试的路径: {file_path}")
        return {}

# 场景配置（从文档解析或手动定义）
SCENARIOS = load_scenarios()

# --- SOP 映射与加载 ---
# 将中文大类映射到英文目录（智能客服系统/sop_data_global_en 下）
CATEGORY_MAP = {
    "取款/提现": "withdrawals",
    "存款/充值": "deposits_top_ups",
    "账号与安全": "account_security",
    "红利 / 返水 / VIP 权益": "bonuses_cashback_vip_benefits",
    "身份验证与合规": "identity_verification_compliance",
    "游戏与投注规则": "game_betting_rules",
    "支付方式与资金渠道": "payment_methods_funding_channels",
    "沟通渠道与账户服务": "communication_channels_account_services",
    "活动与促销": "promotions_campaigns",
    "投诉与争议解决": "platform_rules_general_information",
    "平台规则与通用信息": "platform_rules_general_information",
    "系统 / 技术问题": "system_technical_issues",
    "负责任博彩与自我限制": "platform_rules_general_information",  # 若无专门目录，映射到通用
}


def load_sops(base_dir: str = None) -> Dict[str, List[Dict[str, str]]]:
    """预加载 SOP 文件内容"""
    if base_dir is None:
        base_dir = SOP_BASE_DIR
    
    # 如果路径是相对路径，尝试多个可能的位置
    base = Path(base_dir)
    if not base.is_absolute():
        possible_paths = [
            base,  # 当前目录
            Path(__file__).parent / base,  # 脚本所在目录
            Path(__file__).parent.parent / base,  # learn 目录
        ]
        for path in possible_paths:
            if path.exists():
                base = path
                break
    data: Dict[str, List[Dict[str, str]]] = {}
    for cat_cn, folder in CATEGORY_MAP.items():
        cat_dir = base / folder
        if not cat_dir.exists():
            continue
        files = []
        for p in cat_dir.rglob("*.md"):
            try:
                text = p.read_text(encoding="utf-8")
            except Exception:
                continue
            files.append({"path": str(p), "name": p.stem, "text": text})
        data[cat_cn] = files
    return data


SOP_DATA = load_sops()


def retrieve_sop(category: str, subcategory: str, k: int = 2) -> List[Dict[str, str]]:
    """基于类别与子类名的简单检索"""
    files = SOP_DATA.get(category, [])
    if not files:
        return []
    key = (subcategory or "").replace(" ", "").lower()
    scored = []
    for f in files:
        name = f["name"].lower()
        score = 0
        if key and key in name:
            score += 2
        scored.append((score, f))
    scored.sort(key=lambda x: x[0], reverse=True)
    hits = [f for s, f in scored[:k] if s > 0]
    if not hits:
        hits = [f for s, f in scored[:k]]
    return hits


def classify_scenario(state: CustomerSupportState) -> Dict:
    """
    节点1: 分类场景
    识别用户查询属于哪个大类场景和子类场景
    """
    from langchain_core.prompts import ChatPromptTemplate
    # 尝试多种导入方式以兼容不同版本
    try:
        from pydantic import BaseModel, Field
    except ImportError:
        try:
            from langchain_core.pydantic_v1 import BaseModel, Field
        except ImportError:
            from pydantic.v1 import BaseModel, Field
    
    class ScenarioClassification(BaseModel):
        category: str = Field(description="大类场景名称")
        subcategory: str = Field(description="子类场景名称")
        confidence: float = Field(description="分类置信度")
    
    # 构建可用场景列表
    available_scenarios = []
    for cat, info in SCENARIOS.items():
        for subcat in info.get('subcategories', []):
            available_scenarios.append(f"{cat} - {subcat['name']}")
    
    # 添加特殊场景处理说明
    special_cases_note = """
特殊说明：
- 如果是问候、闲聊（如"你好"、"谢谢"、"再见"等），分类为：其他未分类问题（兜底）
- 如果是非业务相关的闲聊，分类为：其他未分类问题（兜底）
- 如果无法确定具体场景，分类为：其他未分类问题（兜底）
"""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""你是一个客服场景分类专家。根据用户查询，判断属于以下哪个场景：

可用场景：
{chr(10).join(f"- {s}" for s in available_scenarios)}
{special_cases_note}

请准确分类用户查询。如果是问候、闲聊或无法分类的查询，请分类为"其他未分类问题（兜底）"。"""),
        ("user", "用户查询：{query}")
    ])
    
    classifier = prompt | llm.with_structured_output(ScenarioClassification)
    result = classifier.invoke({"query": state["user_query"]})
    
    return {
        "category": result.category,
        "subcategory": result.subcategory,
        "context": {"confidence": result.confidence}
    }

def get_scenario_flow(state: CustomerSupportState) -> Dict:
    """
    节点2: 获取场景流程
    根据分类结果，获取对应的处理流程
    """
    category = state["category"]
    subcategory = state["subcategory"]
    
    # 查找对应的流程
    flow_info = None
    if category in SCENARIOS:
        for subcat in SCENARIOS[category].get('subcategories', []):
            if subcat['name'] == subcategory:
                flow_info = subcat
                break
    
    if not flow_info:
        return {
            "context": {
                **state.get("context", {}),
                "error": f"未找到场景流程: {category} - {subcategory}"
            },
            "next_action": "fallback"
        }
    
    return {
        "context": {
            **state.get("context", {}),
            "flow_info": flow_info,
            "category_description": SCENARIOS[category].get('description', '')
        },
        "next_action": "process"
    }

def process_scenario(state: CustomerSupportState) -> Dict:
    """
    节点3: 处理场景
    根据场景流程处理用户查询
    """
    from langchain_core.prompts import ChatPromptTemplate
    
    flow_info = state["context"].get("flow_info", {}) or {}
    category_desc = state["context"].get("category_description", "")
    subcategory_desc = flow_info.get("description", "")
    related = flow_info.get("related_subcategories", []) or []
    
    # 在系统提示中提供关联子类作为上下文参考，但不让 LLM 直接输出列表
    # 这样 LLM 可以参考这些信息生成更准确的回复，但不会重复列出
    related_context = ""
    if related:
        related_context = f"\n\n注意：以下是与当前场景相关的其他问题类型（供参考，无需在回复中列出）：\n" + "\n".join(f"- {item}" for item in related[:3])  # 只提供前3个作为上下文

    # 检索 SOP（按大类/子类），截取片段以控长度
    sop_hits = retrieve_sop(state["category"], state["subcategory"], k=2)
    sop_text = ""
    if sop_hits:
        snippets = []
        for h in sop_hits:
            snippet = h["text"][:800]
            snippets.append(f"【{h['name']}】\n{snippet}")
        sop_text = "\n\nSOP参考（节选）：\n" + "\n\n".join(snippets)

    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""你是一个专业的客服助手，专门处理以下场景：

大类场景：{state['category']}
{category_desc}

子类场景：{state['subcategory']}
{subcategory_desc}
{related_context}
{sop_text}

请根据场景流程和用户查询，提供专业、友好的回复。
重要：只需回答用户的具体问题，不要列出"关联子类"或"相关问题"等列表。"""),
        ("user", "用户查询：{query}\n\n请提供回复。")
    ])
    
    chain = prompt | llm
    response = chain.invoke({"query": state["user_query"]})

    # 清理回复内容，移除可能出现的关联子类列表
    response_text = response.content
    
    # 移除回复中可能出现的关联子类列表（如果 LLM 还是输出了）
    lines = response_text.split('\n')
    cleaned_lines = []
    skip_until_empty = False
    for i, line in enumerate(lines):
        # 检测是否开始出现关联子类列表
        if any(keyword in line for keyword in ["关联子类", "相关问题", "相关帮助", "💡 相关", "相关主题"]):
            skip_until_empty = True
            continue
        # 如果遇到空行，停止跳过
        if skip_until_empty and line.strip() == "":
            skip_until_empty = False
            continue
        # 如果正在跳过，检查是否是列表项
        if skip_until_empty:
            if line.strip().startswith("-") or line.strip().startswith("•") or line.strip().startswith("*"):
                continue
            else:
                skip_until_empty = False
        
        cleaned_lines.append(line)
    
    response_text = '\n'.join(cleaned_lines).strip()
    
    # 不再在回复中显示关联子类（用户要求）
    # 关联子类只在系统提示中作为上下文参考，帮助 LLM 生成更准确的回复
    
    # SOP 参考资料（可选：如果不需要也可以注释掉）
    # if sop_hits:
    #     refs = "\n".join(f"   • {h['name']}" for h in sop_hits)
    #     response_text = f"{response_text}\n\n📚 参考资料：\n{refs}"
    
    return {
        "response": response_text,
        "next_action": "complete"
    }

def fallback_handler(state: CustomerSupportState) -> Dict:
    """
    节点4: 降级处理
    当无法识别场景时的默认处理（包括闲聊、问候、其他未分类问题）
    """
    from langchain_core.prompts import ChatPromptTemplate
    
    query = state["user_query"].lower()
    
    # 检测是否是问候或闲聊
    greetings = ["你好", "hello", "hi", "早上好", "下午好", "晚上好", "您好"]
    farewells = ["再见", "bye", "拜拜", "谢谢", "thank", "感谢"]
    small_talk = ["在吗", "有人吗", "客服", "人工", "help"]
    
    is_greeting = any(g in query for g in greetings)
    is_farewell = any(f in query for f in farewells)
    is_small_talk = any(s in query for s in small_talk)
    
    # 根据查询类型选择不同的处理方式
    if is_greeting:
        system_prompt = """你是一个友好的客服助手。用户发送了问候，请礼貌地回应并询问如何帮助。
回复要求：
1. 友好地回应问候
2. 简要介绍你可以提供的帮助
3. 询问用户需要什么帮助
4. 保持简洁，不超过3句话"""
    elif is_farewell:
        system_prompt = """你是一个友好的客服助手。用户发送了告别或感谢，请礼貌地回应。
回复要求：
1. 友好地回应
2. 表达愿意继续提供帮助
3. 保持简洁，1-2句话即可"""
    elif is_small_talk:
        system_prompt = """你是一个友好的客服助手。用户可能在测试或寻找帮助，请友好地回应并引导。
回复要求：
1. 友好地确认在线
2. 说明可以提供帮助
3. 询问具体需求"""
    else:
        # 其他未分类问题
        system_prompt = """你是一个专业的客服助手。虽然无法准确识别用户的具体场景，但请尽力提供帮助。
回复要求：
1. 友好地回应
2. 尝试理解用户需求
3. 如果无法确定，可以询问更多信息或引导用户描述具体问题
4. 可以提及常见问题类型（如账户、充值、提现等）帮助用户明确需求"""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "用户查询：{query}\n\n请提供回复。")
    ])
    
    chain = prompt | llm
    response = chain.invoke({"query": state["user_query"]})
    
    return {
        "response": response.content,
        "next_action": "complete",
        "category": state.get("category", "其他未分类问题（兜底）"),
        "subcategory": "通用回复"
    }

def route_after_classification(state: CustomerSupportState) -> Literal["get_flow", "fallback"]:
    """路由：分类后决定下一步"""
    # 如果明确标记使用 fallback，或者分类为"其他未分类问题（兜底）"，直接走 fallback
    context = state.get("context", {})
    if context.get("use_fallback") or "其他未分类问题" in state.get("category", "") or "兜底" in state.get("category", ""):
        return "fallback"
    
    # 如果有有效的分类结果，走正常流程
    if state.get("category") and state.get("subcategory"):
        return "get_flow"
    
    # 默认走 fallback
    return "fallback"

def route_after_flow(state: CustomerSupportState) -> Literal["process", "fallback"]:
    """路由：获取流程后决定下一步"""
    if state.get("context", {}).get("flow_info"):
        return "process"
    return "fallback"

def route_after_process(state: CustomerSupportState) -> Literal["complete", "fallback"]:
    """路由：处理后决定下一步"""
    if state.get("response"):
        return "complete"
    return "fallback"

# 构建图
def build_customer_support_graph():
    """构建客服场景处理图"""
    builder = StateGraph(CustomerSupportState)
    
    # 添加节点
    builder.add_node("classify", classify_scenario)
    builder.add_node("get_flow", get_scenario_flow)
    builder.add_node("process", process_scenario)
    builder.add_node("fallback", fallback_handler)
    
    # 添加边
    builder.add_edge(START, "classify")
    
    # 条件路由
    builder.add_conditional_edges(
        "classify",
        route_after_classification,
        {
            "get_flow": "get_flow",
            "fallback": "fallback"
        }
    )
    
    builder.add_conditional_edges(
        "get_flow",
        route_after_flow,
        {
            "process": "process",
            "fallback": "fallback"
        }
    )
    
    builder.add_conditional_edges(
        "process",
        route_after_process,
        {
            "complete": END,
            "fallback": "fallback"
        }
    )
    
    builder.add_edge("fallback", END)
    
    # 编译图（添加持久化）
    memory = MemorySaver()
    graph = builder.compile(checkpointer=memory)
    
    return graph

# 创建图实例
customer_support_graph = build_customer_support_graph()

if __name__ == "__main__":
    import uuid
    
    # 测试运行
    graph = build_customer_support_graph()
    
    test_query = "我想查询订单状态"
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    result = graph.invoke(
        {
            "messages": [],
            "user_query": test_query,
            "category": "",
            "subcategory": "",
            "context": {},
            "response": "",
            "next_action": "",
            "history": []
        },
        config
    )
    
    print(f"用户查询: {test_query}")
    print(f"分类结果: {result['category']} - {result['subcategory']}")
    print(f"回复: {result['response']}")

