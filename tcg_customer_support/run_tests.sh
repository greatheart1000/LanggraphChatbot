#!/bin/bash
# 运行所有测试的脚本

echo "=========================================="
echo "TCG 客服场景处理系统 - 测试套件"
echo "=========================================="

# 检查服务是否运行
echo ""
echo "1. 检查 API 服务状态..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "   ✅ API 服务正在运行"
    RUN_API_TESTS=true
else
    echo "   ⚠️  API 服务未运行（将跳过 API 测试）"
    echo "   提示: 在另一个终端运行 'python api_server.py'"
    RUN_API_TESTS=false
fi

# 运行场景测试
echo ""
echo "2. 运行场景分类测试..."
python test_scenarios.py specific

# 运行 API 测试（如果服务运行）
if [ "$RUN_API_TESTS" = true ]; then
    echo ""
    echo "3. 运行 API 接口测试..."
    python test_api.py health
    python test_api.py scenarios
    python test_api.py chat "我想提现"
else
    echo ""
    echo "3. 跳过 API 测试（服务未运行）"
fi

# 运行集成测试
echo ""
echo "4. 运行集成测试..."
python test_integration.py

echo ""
echo "=========================================="
echo "测试完成"
echo "=========================================="

