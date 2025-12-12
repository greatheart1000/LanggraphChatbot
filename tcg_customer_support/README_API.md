# TCG 客服场景处理 FastAPI 服务

基于 FastAPI 的 RESTful API 服务，提供 TCG 客服场景处理的 HTTP 接口。

## 安装依赖

```bash
pip install -r requirements_api.txt
```

## 启动服务

### 方式1: 直接运行

```bash
python api_server.py
```

### 方式2: 使用 uvicorn

```bash
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

服务启动后访问：
- API 文档: http://localhost:8000/docs
- 交互式文档: http://localhost:8000/redoc
- 健康检查: http://localhost:8000/health

## API 端点

### 1. 根路径

```
GET /
```

返回 API 基本信息。

### 2. 健康检查

```
GET /health
```

检查服务状态和场景配置加载情况。

### 3. 获取场景列表

```
GET /scenarios
```

返回所有可用的场景类别和子类。

**响应示例：**
```json
{
  "total_categories": 13,
  "categories": {
    "取款/提现": [
      {
        "category": "取款/提现",
        "subcategory": "1 提现状态查询 Flow",
        "description": "...",
        "related_subcategories": [...]
      }
    ]
  }
}
```

### 4. 发送客服查询（同步）

```
POST /chat
```

**请求体：**
```json
{
  "user_query": "我想查询订单状态",
  "thread_id": "optional-session-id",
  "category": "",
  "subcategory": "",
  "context": {}
}
```

**响应示例：**
```json
{
  "response": "您好，我来帮您查询订单状态...",
  "category": "订单查询",
  "subcategory": "订单状态查询",
  "thread_id": "uuid-here",
  "confidence": 0.95,
  "related_subcategories": ["订单详情", "订单历史"],
  "sop_references": ["order_query_guide.md"]
}
```

### 5. 流式客服查询

```
POST /chat/stream
```

返回 Server-Sent Events (SSE) 流式响应。

**请求体：** 同 `/chat`

**响应格式：** SSE 流
```
data: {"category": "...", "subcategory": "...", "response": "...", "thread_id": "..."}

data: {"done": true, "thread_id": "..."}
```

### 6. 获取会话信息

```
GET /sessions/{thread_id}
```

获取指定会话的最近信息。

### 7. 删除会话

```
DELETE /sessions/{thread_id}
```

删除指定会话。

## 使用示例

### Python 客户端

```python
import requests

# 发送查询
response = requests.post(
    "http://localhost:8000/chat",
    json={
        "user_query": "我想查询提现状态",
        "thread_id": "my-session-123"
    }
)

result = response.json()
print(result["response"])
print(f"分类: {result['category']} - {result['subcategory']}")
```

### 流式查询

```python
import requests
import json

response = requests.post(
    "http://localhost:8000/chat/stream",
    json={"user_query": "如何提现？"},
    stream=True
)

for line in response.iter_lines():
    if line:
        data = json.loads(line.decode('utf-8').replace('data: ', ''))
        if 'done' in data:
            break
        print(data.get('response', ''), end='', flush=True)
```

### JavaScript/TypeScript 客户端

```javascript
// 普通查询
const response = await fetch('http://localhost:8000/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_query: '我想查询订单状态'
  })
});

const result = await response.json();
console.log(result.response);

// 流式查询
const eventSource = new EventSource(
  'http://localhost:8000/chat/stream?' + 
  new URLSearchParams({
    user_query: '如何提现？'
  })
);

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.done) {
    eventSource.close();
  } else {
    console.log(data.response);
  }
};
```

## 环境变量

- `OPENAI_API_KEY`: OpenAI API 密钥（必需）

## 部署建议

### 生产环境

1. **使用进程管理器**
   ```bash
   # 使用 gunicorn + uvicorn workers
   gunicorn api_server:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

2. **使用 Docker**
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements*.txt ./
   RUN pip install --no-cache-dir -r requirements.txt -r requirements_api.txt
   COPY . .
   CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

3. **会话存储**
   - 当前使用内存存储会话（仅用于演示）
   - 生产环境建议使用 Redis 或数据库

4. **添加认证**
   - 使用 FastAPI 的 `HTTPBearer` 或 OAuth2
   - 添加 API Key 验证

## 性能优化

1. **异步处理**: 已使用 FastAPI 的异步特性
2. **连接池**: 配置数据库/Redis 连接池
3. **缓存**: 对场景配置进行缓存
4. **限流**: 使用 `slowapi` 或 `ratelimit` 添加限流

## 监控和日志

建议添加：
- 日志记录（使用 `logging`）
- 指标收集（Prometheus）
- 错误追踪（Sentry）

## 故障排查

1. **场景配置未加载**
   - 检查 `TCG 客服场景flow_parsed.json` 是否存在
   - 检查文件路径是否正确

2. **API 调用失败**
   - 检查 `OPENAI_API_KEY` 是否设置
   - 检查网络连接

3. **流式响应中断**
   - 检查客户端是否支持 SSE
   - 检查代理/负载均衡器配置

