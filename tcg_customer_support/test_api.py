"""
测试 FastAPI 接口
"""
import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_health_check():
    """测试健康检查"""
    print(f"\n{'='*60}")
    print("测试: GET /health")
    print(f"{'='*60}")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保 api_server.py 正在运行")
        return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_get_scenarios():
    """测试获取场景列表"""
    print(f"\n{'='*60}")
    print("测试: GET /scenarios")
    print(f"{'='*60}")
    
    try:
        response = requests.get(f"{BASE_URL}/scenarios", timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 成功获取场景列表")
            print(f"   总大类数: {data.get('total_categories', 0)}")
            
            # 显示前几个大类
            categories = data.get('categories', {})
            for i, (cat, subcats) in enumerate(list(categories.items())[:3]):
                print(f"\n   大类 {i+1}: {cat}")
                print(f"     子类数: {len(subcats)}")
                if subcats:
                    print(f"     示例子类: {subcats[0].get('subcategory', 'N/A')}")
            
            return True
        else:
            print(f"❌ 请求失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_chat(user_query: str, thread_id: str = None) -> Dict[str, Any]:
    """测试聊天接口"""
    print(f"\n{'='*60}")
    print(f"测试: POST /chat")
    print(f"查询: {user_query}")
    print(f"{'='*60}")
    
    payload = {
        "user_query": user_query
    }
    
    if thread_id:
        payload["thread_id"] = thread_id
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json=payload,
            timeout=30
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 成功获取回复")
            print(f"   会话ID: {result.get('thread_id', 'N/A')}")
            print(f"   大类: {result.get('category', 'N/A')}")
            print(f"   子类: {result.get('subcategory', 'N/A')}")
            print(f"   置信度: {result.get('confidence', 'N/A')}")
            
            response_text = result.get('response', '')
            print(f"\n📝 回复内容:")
            print(f"   {response_text[:300]}..." if len(response_text) > 300 else f"   {response_text}")
            
            related = result.get('related_subcategories', [])
            if related:
                print(f"\n🔗 关联子类:")
                for item in related[:3]:
                    print(f"   - {item}")
            
            sop_refs = result.get('sop_references', [])
            if sop_refs:
                print(f"\n📚 SOP参考资料:")
                for ref in sop_refs[:3]:
                    print(f"   - {ref}")
            
            return result
        else:
            print(f"❌ 请求失败: {response.text}")
            return {}
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return {}

def test_chat_stream(user_query: str):
    """测试流式聊天接口"""
    print(f"\n{'='*60}")
    print(f"测试: POST /chat/stream")
    print(f"查询: {user_query}")
    print(f"{'='*60}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat/stream",
            json={"user_query": user_query},
            stream=True,
            timeout=30
        )
        
        print(f"状态码: {response.status_code}")
        print(f"流式响应:")
        print("-" * 60)
        
        if response.status_code == 200:
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]  # 去掉 'data: ' 前缀
                        try:
                            data = json.loads(data_str)
                            if data.get('done'):
                                print("\n✅ 流式响应完成")
                                break
                            elif data.get('response'):
                                print(data['response'], end='', flush=True)
                            elif data.get('category'):
                                print(f"\n分类: {data.get('category')} - {data.get('subcategory', '')}")
                        except json.JSONDecodeError:
                            continue
            return True
        else:
            print(f"❌ 请求失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_multi_turn_conversation():
    """测试多轮对话"""
    print(f"\n{'='*60}")
    print("测试: 多轮对话")
    print(f"{'='*60}")
    
    thread_id = None
    
    # 第一轮
    print("\n第一轮对话:")
    result1 = test_chat("我想提现", thread_id)
    if result1:
        thread_id = result1.get('thread_id')
    
    if thread_id:
        time.sleep(1)
        # 第二轮
        print("\n第二轮对话（使用相同 thread_id）:")
        result2 = test_chat("订单号是123456", thread_id)
    
    return thread_id is not None

def test_session_management():
    """测试会话管理"""
    print(f"\n{'='*60}")
    print("测试: 会话管理")
    print(f"{'='*60}")
    
    # 创建会话
    result = test_chat("测试查询")
    thread_id = result.get('thread_id') if result else None
    
    if thread_id:
        # 获取会话信息
        try:
            response = requests.get(f"{BASE_URL}/sessions/{thread_id}")
            if response.status_code == 200:
                print(f"\n✅ 成功获取会话信息:")
                print(json.dumps(response.json(), indent=2, ensure_ascii=False))
            else:
                print(f"❌ 获取会话失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 错误: {e}")
        
        # 删除会话
        try:
            response = requests.delete(f"{BASE_URL}/sessions/{thread_id}")
            if response.status_code == 200:
                print(f"\n✅ 成功删除会话")
            else:
                print(f"❌ 删除会话失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 错误: {e}")

def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("开始运行所有 API 测试")
    print("="*60)
    
    # 检查服务是否运行
    if not test_health_check():
        print("\n❌ 服务未运行，请先启动 api_server.py")
        return
    
    # 测试场景列表
    test_get_scenarios()
    
    # 测试各种查询
    test_queries = [
        "我想提现",
        "充值没到账",
        "忘记密码怎么办？",
        "返水怎么算？",
        "如何联系客服？",
    ]
    
    print(f"\n{'='*60}")
    print("测试各种查询场景")
    print(f"{'='*60}")
    
    for query in test_queries:
        test_chat(query)
        time.sleep(1)  # 避免请求过快
    
    # 测试流式响应
    test_chat_stream("我想查询提现状态")
    
    # 测试多轮对话
    test_multi_turn_conversation()
    
    # 测试会话管理
    test_session_management()
    
    print(f"\n{'='*60}")
    print("所有测试完成")
    print(f"{'='*60}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "health":
            test_health_check()
        elif sys.argv[1] == "scenarios":
            test_get_scenarios()
        elif sys.argv[1] == "chat":
            query = sys.argv[2] if len(sys.argv) > 2 else "我想提现"
            test_chat(query)
        elif sys.argv[1] == "stream":
            query = sys.argv[2] if len(sys.argv) > 2 else "我想提现"
            test_chat_stream(query)
        elif sys.argv[1] == "multi":
            test_multi_turn_conversation()
        elif sys.argv[1] == "session":
            test_session_management()
        else:
            print("使用方法:")
            print("  python test_api.py                    # 运行所有测试")
            print("  python test_api.py health             # 健康检查")
            print("  python test_api.py scenarios          # 获取场景列表")
            print("  python test_api.py chat '查询内容'    # 测试聊天接口")
            print("  python test_api.py stream '查询内容'  # 测试流式接口")
            print("  python test_api.py multi              # 测试多轮对话")
            print("  python test_api.py session             # 测试会话管理")
    else:
        run_all_tests()

