# TCG 智能客服系统

本文件夹包含基于 LangGraph 构建的 TCG 智能客服系统，支持 13 大类场景的智能处理和路由。

## 📚 目录结构

```
智能客服系统/
├── README.md                    # 本文件 - 系统说明
├── 01-基础概念.md               # LangGraph 基础概念
├── 02-示例组合指南.md            # 如何组合多个示例
├── 03-核心功能详解.md            # 核心功能详细说明
├── 04-最佳实践.md                # 开发最佳实践
├── examples/                    # 学习示例代码
│   └── combining_examples_demo.ipynb  # 示例组合演示
└── tcg_customer_support/       # TCG 智能客服系统核心代码
    ├── tcg_customer_support_graph.py  # LangGraph 主流程
    ├── api_server.py            # FastAPI 服务
    ├── parse_document.py        # 文档解析工具
    ├── config.py                # 配置文件
    ├── test_scenarios.py        # 场景测试
    ├── test_api.py              # API 测试
    └── sop_data_global_en/      # SOP 知识库
```

## 🚀 快速开始

### 1. TCG 智能客服系统

**启动 API 服务：**
```bash
cd tcg_customer_support
python api_server.py
```

**运行测试：**
```bash
# 测试场景分类
python test_scenarios.py

# 测试 API 接口
python test_api.py
```

**详细文档：**
- 系统说明: `tcg_customer_support/README.md`
- API 文档: `tcg_customer_support/README_API.md`
- 技术架构: `tcg_customer_support/技术架构说明.md`

### 2. LangGraph 学习资料

1. **了解基础概念** → 阅读 `01-基础概念.md`
2. **学习核心功能** → 阅读 `03-核心功能详解.md`
3. **查看示例组合** → 阅读 `02-示例组合指南.md` 和运行示例代码
4. **掌握最佳实践** → 阅读 `04-最佳实践.md`

## 📖 文档说明

### 01-基础概念.md
- LangGraph 是什么
- 核心概念：图、节点、边、状态
- 基本使用流程

### 02-示例组合指南.md
- 如何组合多个示例
- 四种组合模式详解
- 实际应用场景

### 03-核心功能详解.md
- 持久化（Persistence）
- 流式处理（Streaming）
- 记忆管理（Memory）
- 子图（Subgraphs）
- 条件路由（Branching）

### 04-最佳实践.md
- 代码组织建议
- 性能优化技巧
- 错误处理
- 测试策略

## 🎯 系统特性

### TCG 智能客服系统

- ✅ **智能场景分类**: 自动识别 13 大类、70+ 子类场景
- ✅ **多轮对话**: 支持上下文记忆和会话管理
- ✅ **知识检索**: 基于 SOP 文档的智能检索
- ✅ **流式处理**: 实时响应，提供更好的用户体验
- ✅ **RESTful API**: 完整的 FastAPI 服务接口
- ✅ **降级处理**: 智能处理闲聊、问候等场景

### 技术栈

- **LangGraph**: 图状态机框架
- **LangChain**: LLM 应用框架
- **FastAPI**: Web API 框架
- **OpenAI API**: 大语言模型

## 🔗 相关资源

- **TCG 客服系统**: `tcg_customer_support/` 目录
- **官方文档**: `../docs/docs/` 目录
- **示例代码**: `../examples/` 目录
- **源代码**: `../libs/langgraph/` 目录

## 💡 使用建议

### 对于 TCG 智能客服系统

1. **快速开始**: 查看 `tcg_customer_support/README.md`
2. **API 使用**: 查看 `tcg_customer_support/README_API.md`
3. **技术架构**: 查看 `tcg_customer_support/技术架构说明.md`
4. **运行测试**: 使用 `test_scenarios.py` 和 `test_api.py`

### 对于 LangGraph 学习

1. **循序渐进**: 先理解基础概念，再深入学习高级特性
2. **动手实践**: 运行示例代码，修改并观察结果
3. **组合创新**: 尝试将不同的示例组合起来
4. **查阅源码**: 遇到问题时查看源代码实现

## 📝 更新日志

- 2024-XX-XX: 重命名为"智能客服系统"，整合 TCG 客服系统
- 2024-XX-XX: 创建学习指南文档结构

