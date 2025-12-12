"""
测试各个场景分类和处理
"""
import uuid
from tcg_customer_support_graph import customer_support_graph, load_scenarios

def test_scenario(user_query: str, expected_category: str = None, expected_subcategory: str = None):
    """测试单个场景"""
    print(f"\n{'='*60}")
    print(f"测试查询: {user_query}")
    print(f"{'='*60}")
    
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    state = {
        "messages": [],
        "user_query": user_query,
        "category": "",
        "subcategory": "",
        "context": {},
        "response": "",
        "next_action": "",
        "history": []
    }
    
    try:
        result = customer_support_graph.invoke(state, config)
        
        print(f"✅ 分类结果:")
        print(f"   大类: {result.get('category', 'N/A')}")
        print(f"   子类: {result.get('subcategory', 'N/A')}")
        print(f"   置信度: {result.get('context', {}).get('confidence', 'N/A')}")
        
        if expected_category:
            if result.get('category') == expected_category:
                print(f"   ✅ 大类匹配预期: {expected_category}")
            else:
                print(f"   ❌ 大类不匹配! 预期: {expected_category}, 实际: {result.get('category')}")
        
        if expected_subcategory:
            if expected_subcategory in result.get('subcategory', ''):
                print(f"   ✅ 子类匹配预期: {expected_subcategory}")
            else:
                print(f"   ❌ 子类不匹配! 预期包含: {expected_subcategory}, 实际: {result.get('subcategory')}")
        
        print(f"\n📝 回复内容:")
        response = result.get('response', '')
        print(f"   {response[:200]}..." if len(response) > 200 else f"   {response}")
        
        # 显示关联子类
        flow_info = result.get("context", {}).get("flow_info", {})
        related = flow_info.get("related_subcategories", [])
        if related:
            print(f"\n🔗 关联子类:")
            for item in related[:5]:  # 只显示前5个
                print(f"   - {item}")
        
        return result
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_all_categories():
    """测试所有大类场景"""
    scenarios = load_scenarios()
    
    print(f"\n{'='*60}")
    print(f"开始测试所有 {len(scenarios)} 大类场景")
    print(f"{'='*60}")
    
    # 为每个大类准备测试用例
    test_cases = {
        "取款/提现": [
            "我想提现",
            "提现什么时候到账？",
            "提现失败怎么办？",
            "如何操作提现？",
            "提现需要验证吗？",
        ],
        "存款/充值": [
            "我想充值",
            "充值没到账",
            "充值失败原因",
            "充值限额是多少？",
            "充值需要什么材料？",
        ],
        "账号与安全": [
            "忘记密码怎么办？",
            "账号被锁了",
            "如何修改手机号？",
            "账号异常处理",
            "如何注销账号？",
        ],
        "红利 / 返水 / VIP 权益": [
            "返水怎么算？",
            "VIP每周返利是多少？",
            "积分怎么兑换？",
            "活动规则是什么？",
            "奖励什么时候发？",
        ],
        "身份验证与合规": [
            "需要身份验证吗？",
            "KYC审核要多久？",
            "地区限制说明",
            "验证码收不到",
            "违规处理流程",
        ],
        "游戏与投注规则": [
            "游戏结果查询",
            "投注规则说明",
            "游戏公平性",
            "投注异常处理",
        ],
        "支付方式与资金渠道": [
            "支持哪些支付方式？",
            "支付渠道维护",
            "虚拟钱包使用",
            "支付方式绑定",
        ],
        "沟通渠道与账户服务": [
            "如何联系客服？",
            "账户记录查询",
            "下载安装指南",
            "隐私安全说明",
        ],
        "活动与促销": [
            "如何参与活动？",
            "优惠码怎么用？",
            "推广奖励",
            "奖励领取",
        ],
        "投诉与争议解决": [
            "我要投诉",
            "账户争议",
            "资金争议",
            "申诉流程",
        ],
        "平台规则与通用信息": [
            "平台合法性",
            "违规行为处理",
            "账户限制",
            "推广代理佣金",
        ],
        "系统 / 技术问题": [
            "网站打不开",
            "APP下载问题",
            "登录失败",
            "余额显示异常",
        ],
        "负责任博彩与自我限制": [
            "如何设置自我限制？",
            "负责任博彩政策",
        ],
    }
    
    results = {}
    for category, queries in test_cases.items():
        print(f"\n\n{'#'*60}")
        print(f"测试大类: {category}")
        print(f"{'#'*60}")
        
        category_results = []
        for query in queries:
            result = test_scenario(query, expected_category=category)
            category_results.append(result)
        
        results[category] = category_results
    
    return results

def test_specific_scenarios():
    """测试特定场景"""
    print(f"\n{'='*60}")
    print("测试特定场景")
    print(f"{'='*60}")
    
    specific_tests = [
        {
            "query": "我想查询提现状态",
            "expected_category": "取款/提现",
            "expected_subcategory": "提现状态查询"
        },
        {
            "query": "充值没到账怎么办？",
            "expected_category": "存款/充值",
            "expected_subcategory": "存款到账状态查询"
        },
        {
            "query": "忘记密码了",
            "expected_category": "账号与安全",
            "expected_subcategory": "密码找回"
        },
        {
            "query": "返水怎么计算？",
            "expected_category": "红利 / 返水 / VIP 权益",
            "expected_subcategory": "返水规则"
        },
    ]
    
    for test in specific_tests:
        test_scenario(
            test["query"],
            test.get("expected_category"),
            test.get("expected_subcategory")
        )

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "all":
            # 测试所有场景
            test_all_categories()
        elif sys.argv[1] == "specific":
            # 测试特定场景
            test_specific_scenarios()
        else:
            # 测试单个查询
            test_scenario(sys.argv[1])
    else:
        # 默认运行特定场景测试
        print("使用方法:")
        print("  python test_scenarios.py                    # 运行特定场景测试")
        print("  python test_scenarios.py all                # 测试所有场景")
        print("  python test_scenarios.py specific            # 测试特定场景")
        print("  python test_scenarios.py '你的查询'         # 测试单个查询")
        print("\n开始运行默认测试...\n")
        test_specific_scenarios()

