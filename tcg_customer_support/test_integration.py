"""
集成测试：测试完整流程
"""
import uuid
import requests
from tcg_customer_support_graph import customer_support_graph, load_scenarios

def test_end_to_end():
    """端到端测试"""
    print(f"\n{'='*60}")
    print("端到端集成测试")
    print(f"{'='*60}")
    
    # 1. 加载场景配置
    print("\n1. 加载场景配置...")
    scenarios = load_scenarios()
    if scenarios:
        print(f"   ✅ 成功加载 {len(scenarios)} 个大类场景")
    else:
        print("   ❌ 场景配置加载失败")
        return False
    
    # 2. 测试场景分类
    print("\n2. 测试场景分类...")
    test_queries = [
        ("我想提现", "取款/提现"),
        ("充值没到账", "存款/充值"),
        ("忘记密码", "账号与安全"),
    ]
    
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    for query, expected_category in test_queries:
        state = {
            "messages": [],
            "user_query": query,
            "category": "",
            "subcategory": "",
            "context": {},
            "response": "",
            "next_action": "",
            "history": []
        }
        
        try:
            result = customer_support_graph.invoke(state, config)
            category = result.get('category', '')
            
            if expected_category in category or category in expected_category:
                print(f"   ✅ '{query}' -> {category}")
            else:
                print(f"   ⚠️  '{query}' -> {category} (预期: {expected_category})")
        except Exception as e:
            print(f"   ❌ '{query}' 失败: {e}")
    
    # 3. 测试多轮对话
    print("\n3. 测试多轮对话...")
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    queries = [
        "我想提现",
        "订单号是123456",
        "什么时候能到账？"
    ]
    
    for i, query in enumerate(queries, 1):
        state = {
            "messages": [],
            "user_query": query,
            "category": "",
            "subcategory": "",
            "context": {},
            "response": "",
            "next_action": "",
            "history": []
        }
        
        try:
            result = customer_support_graph.invoke(state, config)
            print(f"   第{i}轮: {query}")
            print(f"   回复: {result.get('response', '')[:100]}...")
        except Exception as e:
            print(f"   ❌ 第{i}轮失败: {e}")
    
    print("\n✅ 端到端测试完成")
    return True

def test_api_integration():
    """测试 API 集成"""
    print(f"\n{'='*60}")
    print("API 集成测试")
    print(f"{'='*60}")
    
    BASE_URL = "http://localhost:8000"
    
    # 检查服务是否运行
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ API 服务未运行")
            return False
    except:
        print("❌ 无法连接到 API 服务，请先启动 api_server.py")
        return False
    
    # 测试完整流程
    print("\n1. 发送查询...")
    result = requests.post(
        f"{BASE_URL}/chat",
        json={"user_query": "我想提现"},
        timeout=30
    )
    
    if result.status_code == 200:
        data = result.json()
        print(f"   ✅ 成功获取回复")
        print(f"   分类: {data.get('category')} - {data.get('subcategory')}")
        
        # 使用返回的 thread_id 继续对话
        thread_id = data.get('thread_id')
        if thread_id:
            print(f"\n2. 继续对话 (thread_id: {thread_id})...")
            result2 = requests.post(
                f"{BASE_URL}/chat",
                json={
                    "user_query": "订单号是123456",
                    "thread_id": thread_id
                },
                timeout=30
            )
            
            if result2.status_code == 200:
                print(f"   ✅ 多轮对话成功")
            
    print("\n✅ API 集成测试完成")
    return True

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "api":
        test_api_integration()
    else:
        test_end_to_end()
        print("\n提示: 运行 'python test_integration.py api' 测试 API 集成")

