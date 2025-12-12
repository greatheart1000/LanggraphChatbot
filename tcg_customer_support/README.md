# TCG 客服场景处理系统

基于 LangGraph 的 TCG 客服场景处理系统，支持 14 大类场景及其子类的智能处理和路由。

## 文件说明

- `parse_document.py` - 解析 Word 文档，提取场景结构
- `tcg_customer_support_graph.py` - LangGraph 主流程实现
- `requirements.txt` - 依赖包列表
- `README.md` - 本文件

## 快速开始

### 1. 安装依赖

```bash
pip install python-docx langchain langchain-openai langgraph
```

### 2. 解析文档

```bash
python parse_document.py "../TCG 客服场景flow.docx"
```

这将生成 `TCG_客服场景flow_parsed.json` 文件，包含所有场景结构。

### 3. 运行客服系统

```python
from tcg_customer_support_graph import customer_support_graph
import uuid

# 创建会话
thread_id = str(uuid.uuid4())
config = {"configurable": {"thread_id": thread_id}}

# 处理用户查询
result = customer_support_graph.invoke(
    {
        "messages": [],
        "user_query": "我想查询订单状态",
        "category": "",
        "subcategory": "",
        "context": {},
        "response": "",
        "next_action": "",
        "history": []
    },
    config
)

print(result["response"])

```

## 系统架构

### 处理流程

```
用户查询
  ↓
[分类场景] → 识别大类场景和子类场景
  ↓
[获取流程] → 加载对应的处理流程
  ↓
[处理场景] → 根据流程生成回复
  ↓
返回结果
```

### 节点说明

1. **classify_scenario**: 场景分类节点
   - 使用 LLM 识别用户查询属于哪个场景
   - 输出：category, subcategory, confidence

2. **get_scenario_flow**: 获取流程节点
   - 根据分类结果加载对应的处理流程
   - 输出：flow_info, category_description

3. **process_scenario**: 处理场景节点
   - 根据场景流程和用户查询生成回复
   - 输出：response

4. **fallback_handler**: 降级处理节点
   - 当无法识别场景时的默认处理
   - 输出：通用回复

## 扩展功能

### 添加新场景

1. 在 Word 文档中添加新场景
2. 运行 `parse_document.py` 重新解析
3. 系统会自动识别新场景

### 自定义处理逻辑

修改 `process_scenario` 函数，添加特定场景的处理逻辑：

```python
def process_scenario(state: CustomerSupportState) -> Dict:
    # 根据特定场景添加自定义逻辑
    if state["category"] == "订单查询":
        # 订单查询的特殊处理
        pass
    
    # 通用处理
    ...
```

### 添加工具

可以为特定场景添加工具，例如：

```python
from langchain_core.tools import tool

@tool
def query_order(order_id: str) -> str:
    """查询订单信息"""
    # 调用订单查询 API
    return order_info

# 在 process_scenario 中使用工具
```

## 流式处理

支持流式输出，提供更好的用户体验：

```python
events = customer_support_graph.stream(
    {
        "messages": [],
        "user_query": "我想查询订单状态",
        ...
    },
    config,
    stream_mode="values"
)

for event in events:
    if "response" in event:
        print(event["response"])
```

## 持久化

系统使用 MemorySaver 进行持久化，支持多轮对话：

```python
# 使用相同的 thread_id 可以继续对话
config = {"configurable": {"thread_id": "your-thread-id"}}

# 第二次调用会自动包含历史记录
result = customer_support_graph.invoke(state, config)
```

## 注意事项

1. 确保已设置 `OPENAI_API_KEY` 环境变量
2. Word 文档格式需要规范（使用标题样式）
3. 场景配置文件路径需要正确
4. 建议在生产环境使用数据库检查点替代 MemorySaver

## 下一步

- 添加更多场景处理逻辑
- 集成外部 API（订单查询、支付等）
- 添加人机交互（Human-in-the-Loop）
- 优化分类准确性
- 添加场景处理效果评估

