# 测试指南

本目录包含完整的测试套件，用于测试 TCG 客服场景处理系统的各个功能。

## 测试文件说明

### 1. `test_scenarios.py` - 场景分类测试

测试各个场景的分类准确性。

**使用方法：**
```bash
# 运行默认测试（特定场景）
python test_scenarios.py

# 测试所有场景（耗时较长）
python test_scenarios.py all

# 测试特定场景
python test_scenarios.py specific

# 测试单个查询
python test_scenarios.py "我想提现"
```

**测试内容：**
- 场景分类准确性
- 子类识别
- 回复生成质量
- 关联子类提取

### 2. `test_api.py` - API 接口测试

测试 FastAPI 服务的各个端点。

**前置条件：**
需要先启动 API 服务：
```bash
python api_server.py
```

**使用方法：**
```bash
# 运行所有测试
python test_api.py

# 健康检查
python test_api.py health

# 获取场景列表
python test_api.py scenarios

# 测试聊天接口
python test_api.py chat "我想提现"

# 测试流式接口
python test_api.py stream "我想提现"

# 测试多轮对话
python test_api.py multi

# 测试会话管理
python test_api.py session
```

**测试内容：**
- `/health` - 健康检查
- `/scenarios` - 场景列表
- `/chat` - 同步聊天
- `/chat/stream` - 流式聊天
- `/sessions/{thread_id}` - 会话管理

### 3. `test_integration.py` - 集成测试

测试完整的端到端流程。

**使用方法：**
```bash
# 测试 LangGraph 流程
python test_integration.py

# 测试 API 集成
python test_integration.py api
```

**测试内容：**
- 场景配置加载
- 场景分类流程
- 多轮对话
- API 集成

### 4. `run_tests.sh` - 一键运行所有测试

```bash
chmod +x run_tests.sh
./run_tests.sh
```

## 测试场景覆盖

### 大类场景测试

系统会测试以下 13 个大类场景：

1. **取款/提现**
   - 提现状态查询
   - 提现失败原因
   - 提现操作指导
   - 提现验证
   - 提现限额/规则

2. **存款/充值**
   - 存款到账状态查询
   - 存款失败原因分析
   - 存款验证材料提交
   - 存款规则/限额
   - 存款异常处理

3. **账号与安全**
   - 账号登录/密码找回
   - 身份验证/实名认证
   - 账号异常/风控处理
   - 账户信息变更
   - 账户注销/停用

4. **红利/返水/VIP 权益**
   - 奖励领取与发放状态查询
   - 优惠资格与规则判断
   - 返水规则/红利政策说明
   - 推广/代理/佣金体系
   - 异常奖励处理

5. **身份验证与合规**
   - 身份验证（KYC）提交与审核
   - 支付相关身份验证
   - 平台牌照/监管/合规说明
   - 地区/IP 限制
   - 验证码/手机号验证

6. **游戏与投注规则**
   - 游戏结果/开奖/结算状态
   - 投注异常/风控监控
   - 投注规则/游戏规则说明
   - 游戏公平性/RNG/合规认证

7. **支付方式与资金渠道**
   - 支付方式绑定/解绑
   - 支付渠道可用性与维护状态
   - 支付方式支持范围/规则说明
   - 虚拟钱包/数字资产支付流程

8. **沟通渠道与账户服务**
   - 客服沟通规范/官方渠道
   - 推广/代理/佣金相关服务
   - 账号管理/绑定/解绑定
   - 账户记录/交易记录查询

9. **活动与促销**
   - 活动参与与规则说明
   - 奖励领取与发放
   - 促销代码/红包码/优惠码
   - 推广与推荐奖励

10. **投诉与争议解决**
    - 账户与行为违规争议
    - 投注/游戏争议处理
    - 资金相关争议
    - 投诉与申诉流程

11. **平台规则与通用信息**
    - 违规行为/风控/惩戒政策
    - 促销活动/优惠规则说明
    - 平台合法性/监管/官方信息
    - 账户与访问限制

12. **系统/技术问题**
    - 系统维护与服务中断
    - 网站/链接/访问问题
    - APP/软件/下载与安装
    - 账户登录/系统登录问题

13. **负责任博彩与自我限制**
    - 负责任博彩与自我限制

## 测试最佳实践

### 1. 运行顺序

建议按以下顺序运行测试：

1. 先运行 `test_scenarios.py` 确保场景分类正常
2. 启动 API 服务：`python api_server.py`
3. 运行 `test_api.py` 测试 API 接口
4. 运行 `test_integration.py` 进行集成测试

### 2. 调试技巧

如果测试失败：

1. **检查配置文件**
   ```bash
   ls -la TCG\ 客服场景flow_parsed.json
   ```

2. **检查环境变量**
   ```bash
   echo $OPENAI_API_KEY
   ```

3. **查看详细错误**
   - 测试脚本会打印详细的错误信息
   - 检查 API 服务的日志输出

4. **单独测试**
   ```bash
   # 测试单个查询
   python test_scenarios.py "你的查询"
   
   # 测试单个 API 端点
   python test_api.py chat "你的查询"
   ```

### 3. 性能测试

对于性能测试，可以：

1. **批量测试**
   ```python
   # 在 test_scenarios.py 中使用 test_all_categories()
   ```

2. **并发测试**
   ```python
   import concurrent.futures
   # 使用线程池并发测试多个查询
   ```

3. **压力测试**
   ```bash
   # 使用 Apache Bench 或 wrk
   ab -n 100 -c 10 http://localhost:8000/chat
   ```

## 测试报告

运行测试后，会输出：
- ✅ 成功测试
- ❌ 失败测试
- ⚠️  警告（部分匹配）

可以根据输出结果调整：
- 场景分类逻辑
- 提示词优化
- SOP 文档完善

## 持续集成

可以将测试集成到 CI/CD 流程：

```yaml
# .github/workflows/test.yml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: python test_scenarios.py specific
```

## 问题反馈

如果测试发现问题，请：
1. 记录测试用例
2. 记录实际输出
3. 记录预期输出
4. 提交 Issue 或 PR

