"""
TCG 客服场景处理 FastAPI 服务
提供 RESTful API 接口调用 LangGraph 客服处理流程
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uuid
import json
import asyncio
from tcg_customer_support_graph import customer_support_graph, load_scenarios

# 创建 FastAPI 应用
app = FastAPI(
    title="TCG 客服场景处理 API",
    description="基于 LangGraph 的智能客服场景处理服务",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求模型
class ChatRequest(BaseModel):
    """聊天请求模型"""
    user_query: str = Field(..., description="用户查询")
    thread_id: Optional[str] = Field(None, description="会话ID，不提供则自动生成")
    category: Optional[str] = Field("", description="预设的大类场景")
    subcategory: Optional[str] = Field("", description="预设的子类场景")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="上下文信息")

class ChatResponse(BaseModel):
    """聊天响应模型"""
    response: str = Field(..., description="客服回复")
    category: str = Field(..., description="识别的大类场景")
    subcategory: str = Field(..., description="识别的子类场景")
    thread_id: str = Field(..., description="会话ID")
    confidence: Optional[float] = Field(None, description="分类置信度")
    related_subcategories: Optional[List[str]] = Field(None, description="关联子类")
    sop_references: Optional[List[str]] = Field(None, description="SOP参考资料")

class ScenarioInfo(BaseModel):
    """场景信息模型"""
    category: str
    subcategory: str
    description: str
    related_subcategories: List[str]

class ScenariosListResponse(BaseModel):
    """场景列表响应"""
    total_categories: int
    categories: Dict[str, List[ScenarioInfo]]

# 会话管理（生产环境建议使用 Redis 或数据库）
sessions: Dict[str, Dict] = {}

def create_initial_state(user_query: str, thread_id: str, category: str = "", 
                        subcategory: str = "", context: Dict = None) -> Dict:
    """创建初始状态"""
    return {
        "messages": [],
        "user_query": user_query,
        "category": category,
        "subcategory": subcategory,
        "context": context or {},
        "response": "",
        "next_action": "",
        "history": []
    }

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "TCG 客服场景处理 API",
        "version": "1.0.0",
        "endpoints": {
            "/chat": "POST - 发送客服查询",
            "/chat/stream": "POST - 流式客服查询",
            "/scenarios": "GET - 获取所有场景列表",
            "/health": "GET - 健康检查"
        }
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    try:
        scenarios = load_scenarios()
        return {
            "status": "healthy",
            "scenarios_loaded": len(scenarios) > 0,
            "total_categories": len(scenarios)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@app.get("/scenarios", response_model=ScenariosListResponse)
async def get_scenarios():
    """获取所有场景列表"""
    try:
        scenarios = load_scenarios()
        categories_info = {}
        
        for category, info in scenarios.items():
            subcategories = []
            for subcat in info.get('subcategories', []):
                subcategories.append(ScenarioInfo(
                    category=category,
                    subcategory=subcat.get('name', ''),
                    description=subcat.get('description', ''),
                    related_subcategories=subcat.get('related_subcategories', [])
                ))
            categories_info[category] = subcategories
        
        return ScenariosListResponse(
            total_categories=len(categories_info),
            categories=categories_info
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"加载场景失败: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    发送客服查询（同步）
    
    - **user_query**: 用户查询内容
    - **thread_id**: 会话ID（可选，不提供则自动生成）
    - **category**: 预设的大类场景（可选）
    - **subcategory**: 预设的子类场景（可选）
    """
    try:
        # 生成或使用 thread_id
        thread_id = request.thread_id or str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}
        
        # 创建初始状态
        state = create_initial_state(
            user_query=request.user_query,
            thread_id=thread_id,
            category=request.category or "",
            subcategory=request.subcategory or "",
            context=request.context or {}
        )
        
        # 调用 LangGraph
        result = customer_support_graph.invoke(state, config)
        
        # 提取相关信息
        flow_info = result.get("context", {}).get("flow_info", {})
        related_subcategories = flow_info.get("related_subcategories", [])
        
        # 提取 SOP 参考资料（如果有）
        sop_references = []
        if "sop_references" in result.get("context", {}):
            sop_references = result["context"]["sop_references"]
        
        # 保存会话
        sessions[thread_id] = {
            "last_query": request.user_query,
            "category": result.get("category", ""),
            "subcategory": result.get("subcategory", ""),
            "timestamp": str(uuid.uuid4())  # 简化时间戳
        }
        
        return ChatResponse(
            response=result.get("response", ""),
            category=result.get("category", ""),
            subcategory=result.get("subcategory", ""),
            thread_id=thread_id,
            confidence=result.get("context", {}).get("confidence"),
            related_subcategories=related_subcategories,
            sop_references=sop_references
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理请求失败: {str(e)}")

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    流式客服查询
    
    返回 Server-Sent Events (SSE) 流式响应
    """
    async def generate():
        try:
            thread_id = request.thread_id or str(uuid.uuid4())
            config = {"configurable": {"thread_id": thread_id}}
            
            state = create_initial_state(
                user_query=request.user_query,
                thread_id=thread_id,
                category=request.category or "",
                subcategory=request.subcategory or "",
                context=request.context or {}
            )
            
            # 流式调用
            events = customer_support_graph.stream(state, config, stream_mode="values")
            
            for event in events:
                # 格式化 SSE 数据
                data = {
                    "category": event.get("category", ""),
                    "subcategory": event.get("subcategory", ""),
                    "response": event.get("response", ""),
                    "thread_id": thread_id
                }
                
                # 如果有消息，也包含
                if "messages" in event and event["messages"]:
                    last_msg = event["messages"][-1]
                    if hasattr(last_msg, 'content'):
                        data["response"] = last_msg.content
                
                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
            
            # 发送结束标记
            yield f"data: {json.dumps({'done': True, 'thread_id': thread_id}, ensure_ascii=False)}\n\n"
            
        except Exception as e:
            error_data = {"error": str(e), "done": True}
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@app.get("/sessions/{thread_id}")
async def get_session(thread_id: str):
    """获取会话信息"""
    if thread_id not in sessions:
        raise HTTPException(status_code=404, detail="会话不存在")
    return sessions[thread_id]

@app.delete("/sessions/{thread_id}")
async def delete_session(thread_id: str):
    """删除会话"""
    if thread_id in sessions:
        del sessions[thread_id]
        return {"message": "会话已删除"}
    raise HTTPException(status_code=404, detail="会话不存在")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

