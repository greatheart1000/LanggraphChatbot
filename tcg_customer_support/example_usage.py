"""
TCG 客服场景处理系统使用示例
"""
import uuid
import os
from tcg_customer_support_graph import customer_support_graph, load_scenarios

def example_basic_usage():
    """基础使用示例"""
    print("=" * 50)
    print("示例 1: 基础使用")
    print("=" * 50)
    
    # 创建会话
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    # 用户查询
    user_query = "我想查询订单状态"
    
    # 调用图
    result = customer_support_graph.invoke(
        {
            "messages": [],
            "user_query": user_query,
            "category": "",
            "subcategory": "",
            "context": {},
            "response": "",
            "next_action": "",
            "history": []
        },
        config
    )
    
    print(f"用户查询: {user_query}")
    print(f"分类结果: {result['category']} - {result['subcategory']}")
    print(f"回复: {result['response']}")
    print()

def example_streaming():
    """流式处理示例"""
    print("=" * 50)
    print("示例 2: 流式处理")
    print("=" * 50)
    
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    user_query = "我的订单什么时候能到？"
    
    print(f"用户查询: {user_query}")
    print("流式输出:")
    print("-" * 50)
    
    events = customer_support_graph.stream(
        {
            "messages": [],
            "user_query": user_query,
            "category": "",
            "subcategory": "",
            "context": {},
            "response": "",
            "next_action": "",
            "history": []
        },
        config,
        stream_mode="values"
    )
    
    for event in events:
        if "category" in event and event["category"]:
            print(f"分类: {event['category']} - {event.get('subcategory', '')}")
        if "response" in event and event["response"]:
            print(f"回复: {event['response']}")
    print()

def example_multi_turn():
    """多轮对话示例"""
    print("=" * 50)
    print("示例 3: 多轮对话")
    print("=" * 50)
    
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    # 第一轮
    query1 = "我想退货"
    result1 = customer_support_graph.invoke(
        {
            "messages": [],
            "user_query": query1,
            "category": "",
            "subcategory": "",
            "context": {},
            "response": "",
            "next_action": "",
            "history": []
        },
        config
    )
    
    print(f"用户: {query1}")
    print(f"客服: {result1['response']}")
    print()
    
    # 第二轮（使用相同的 thread_id，会自动包含历史）
    query2 = "订单号是123456"
    result2 = customer_support_graph.invoke(
        {
            "messages": result1.get("messages", []),
            "user_query": query2,
            "category": result1.get("category", ""),
            "subcategory": result1.get("subcategory", ""),
            "context": result1.get("context", {}),
            "response": "",
            "next_action": "",
            "history": result1.get("history", [])
        },
        config
    )
    
    print(f"用户: {query2}")
    print(f"客服: {result2['response']}")
    print()

def example_batch_processing():
    """批量处理示例"""
    print("=" * 50)
    print("示例 4: 批量处理不同场景")
    print("=" * 50)
    
    queries = [
        "我想查询订单状态",
        "如何申请退款",
        "商品质量问题",
        "物流信息查询",
        "账户登录问题"
    ]
    
    for query in queries:
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}
        
        result = customer_support_graph.invoke(
            {
                "messages": [],
                "user_query": query,
                "category": "",
                "subcategory": "",
                "context": {},
                "response": "",
                "next_action": "",
                "history": []
            },
            config
        )
        
        print(f"查询: {query}")
        print(f"分类: {result.get('category', 'N/A')} - {result.get('subcategory', 'N/A')}")
        print(f"回复: {result.get('response', '')[:100]}...")
        print("-" * 50)

def check_scenarios():
    """检查场景配置"""
    print("=" * 50)
    print("场景配置检查")
    print("=" * 50)
    
    scenarios = load_scenarios()
    
    if not scenarios:
        print("⚠️  未找到场景配置文件！")
        print("请先运行: python parse_document.py '../TCG 客服场景flow.docx'")
        return
    
    print(f"✅ 找到 {len(scenarios)} 大类场景:")
    print()
    
    for category, info in scenarios.items():
        subcategories = info.get('subcategories', [])
        print(f"📁 {category}")
        print(f"   子类数量: {len(subcategories)}")
        for subcat in subcategories[:3]:  # 只显示前3个
            print(f"   - {subcat['name']}")
        if len(subcategories) > 3:
            print(f"   ... 还有 {len(subcategories) - 3} 个子类")
        print()

if __name__ == "__main__":
    # 检查环境变量
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  警告: 未设置 OPENAI_API_KEY 环境变量")
        print("请设置: export OPENAI_API_KEY='your-api-key'")
        print()
    
    # 检查场景配置
    check_scenarios()
    print()
    
    # 运行示例
    try:
        example_basic_usage()
        example_streaming()
        example_multi_turn()
        example_batch_processing()
    except Exception as e:
        print(f"❌ 运行出错: {e}")
        print("\n提示:")
        print("1. 确保已安装依赖: pip install -r requirements.txt")
        print("2. 确保已设置 OPENAI_API_KEY")
        print("3. 确保已解析文档生成场景配置文件")

