'''
接口文件
启动命令：uvicorn main:app --reload
'''

from fastapi import FastAPI, Body,WebSocket,WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.websockets import WebSocket

from backend.workflow.graph_engine import WorkFlow

app = FastAPI()

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，可以根据需要指定特定的origin
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有HTTP头部
)

@app.get("/")
async def read_root():
    return {"Hello": "World"}

class Message(BaseModel):
    mes: str

@app.post("/chat")
async def chat(message: Message = Body(...)):
    work_flow = WorkFlow()
    input_data = {'messages': message.mes}
    # 频谱划分规定
    response = work_flow.run(input_data)
    return {"response": response['judgement_chat']['messages']}


@app.websocket("/chat")
async def chat(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # 等待接收客户端消息
            data = await websocket.receive_text()

            # 假设传入的消息可以直接作为Message模型解析
            message = Message(mes=data)

            work_flow = WorkFlow()
            input_data = {'messages': message.mes}
            response = work_flow.run(input_data)

            # 发送响应给客户端
            await websocket.send_json({"response": response['judgement_chat']['messages']})
    except WebSocketDisconnect:
        print("Client disconnected")



if __name__ == '__main__':
    import uvicorn
    # 注意：在生产环境中不要使用reload=True选项
    uvicorn.run(app, host="0.0.0.0", port=8000,  workers=1)