"""
测试降级处理（闲聊、问候、其他未分类问题）
"""
import uuid
from tcg_customer_support_graph import customer_support_graph

def test_fallback(query: str, expected_type: str = None):
    """测试降级处理"""
    print(f"\n{'='*60}")
    print(f"测试查询: {query}")
    print(f"{'='*60}")
    
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
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
        
        category = result.get('category', 'N/A')
        subcategory = result.get('subcategory', 'N/A')
        response = result.get('response', '')
        
        print(f"✅ 分类结果:")
        print(f"   大类: {category}")
        print(f"   子类: {subcategory}")
        
        if expected_type:
            if expected_type in category or category in expected_type:
                print(f"   ✅ 符合预期: {expected_type}")
            else:
                print(f"   ⚠️  预期: {expected_type}, 实际: {category}")
        
        print(f"\n📝 回复内容:")
        print(f"   {response}")
        
        return result
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_all_fallback_cases():
    """测试所有降级场景"""
    print(f"\n{'='*60}")
    print("测试降级处理场景")
    print(f"{'='*60}")
    
    # 问候类
    print("\n【问候类测试】")
    greetings = [
        "你好",
        "Hello",
        "Hi",
        "早上好",
        "下午好",
        "晚上好",
        "您好",
    ]
    
    for query in greetings:
        test_fallback(query, expected_type="其他未分类问题")
    
    # 告别/感谢类
    print("\n【告别/感谢类测试】")
    farewells = [
        "谢谢",
        "Thank you",
        "再见",
        "Bye",
        "拜拜",
        "感谢",
    ]
    
    for query in farewells:
        test_fallback(query, expected_type="其他未分类问题")
    
    # 闲聊类
    print("\n【闲聊类测试】")
    small_talk = [
        "在吗",
        "有人吗",
        "客服",
        "人工客服",
        "help",
        "需要帮助",
    ]
    
    for query in small_talk:
        test_fallback(query, expected_type="其他未分类问题")
    
    # 其他未分类问题
    print("\n【其他未分类问题测试】")
    other_queries = [
        "今天天气怎么样？",
        "你们公司在哪里？",
        "我想了解一下",
        "随便问问",
        "这是什么？",
    ]
    
    for query in other_queries:
        test_fallback(query, expected_type="其他未分类问题")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        test_fallback(sys.argv[1])
    else:
        test_all_fallback_cases()

